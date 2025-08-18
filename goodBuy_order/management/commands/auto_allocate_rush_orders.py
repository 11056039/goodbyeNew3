from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from collections import defaultdict

from goodBuy_shop.models import Shop, Product
from goodBuy_order.models import Order, ProductOrder
from ...rush_utils import get_rush_summaries  # 你的既有邏輯

ORDER_STATE_INIT = 1
PAY_STATE_UNPAID = 1

'''
dry run test
python manage.py allocate_rush_orders --dry-run

只看特定商店
python manage.py allocate_rush_orders --dry-run --shop 123

'''

class Command(BaseCommand):
    help = "自動分配搶購商店的訂單（截團）"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只預覽分配結果，不寫入資料庫'
        )
        parser.add_argument(
            '--shop',
            type=int,
            help='只處理特定 shop_id'
        )

    def handle(self, *args, **options):
        now = timezone.now()
        dry_run = options.get('dry_run', False)
        only_shop = options.get('shop')

        shops = Shop.objects.filter(
            purchase_priority_id__in=[2, 3],  # 金額/數量優先
            end_time__lt=now,                 # 已截止
            is_rush_settled=False             # 尚未結算
        ).order_by('id')

        if only_shop:
            shops = shops.filter(id=only_shop)

        if not shops.exists():
            self.stdout.write(self.style.WARNING('沒有需要處理的商店。'))
            return

        mode = 'DRY-RUN（不寫入）' if dry_run else '正式結算'
        self.stdout.write(self.style.NOTICE(f'開始執行：{mode}，共 {shops.count()} 間商店\n'))

        for shop in shops:
            try:
                self.stdout.write(self.style.SUCCESS(f'==> 處理商店：{shop.id} - {shop.name}'))
                if dry_run:
                    self.dry_run_shop(shop)
                else:
                    self.allocate_shop(shop)
                self.stdout.write(self.style.SUCCESS(f'完成：{shop.id} - {shop.name}\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'處理商店 {shop.id} 失敗：{e}\n'))
                # 不中斷後續商店

    # -------------------------
    # Dry-run：只計算與列印，不寫入
    # -------------------------
    def dry_run_shop(self, shop):
        intent_summaries = get_rush_summaries(shop)  # 建議內部 select_related('product')
        product_claimed = defaultdict(int)

        # 收集所有 product 初始庫存（僅顯示用）
        product_stock = {}
        # 嘗試從 summaries 拿到所有 product
        for s in intent_summaries:
            for ip in s['products']:
                p = ip.product
                product_stock[p.id] = getattr(p, 'stock', 0)

        total_orders = 0
        total_items = 0
        total_amount = 0

        self.stdout.write(self.style.NOTICE('分配預覽：'))
        for summary in intent_summaries:
            user = summary['user']
            user_total = 0
            lines = []

            for ip in summary['products']:
                p = ip.product
                want_qty = ip.quantity
                available = max(0, product_stock[p.id] - product_claimed[p.id])
                claim_qty = min(want_qty, available)

                if claim_qty > 0:
                    lines.append(f'  - 商品#{p.id} {p.name} x {claim_qty} @ {p.price} = {p.price * claim_qty}')
                    product_claimed[p.id] += claim_qty
                    user_total += p.price * claim_qty
                    total_items += claim_qty

            if user_total > 0:
                total_orders += 1
                total_amount += user_total
                self.stdout.write(f'  使用者 {getattr(user, "username", user.id)}：總額 {user_total}')
                for ln in lines:
                    self.stdout.write(ln)

        # 剩餘庫存概覽
        self.stdout.write(self.style.NOTICE('\n商品剩餘庫存：'))
        for pid, stk in product_stock.items():
            remain = stk - product_claimed[pid]
            self.stdout.write(f'  商品#{pid} 已分配 {product_claimed[pid]}，剩餘 {remain}')

        self.stdout.write(self.style.WARNING(
            f'\n[DRY-RUN 統計] 建立訂單數：{total_orders}，分配件數：{total_items}，總金額：{total_amount}\n'
        ))

    # -------------------------
    # 正式結算：寫入資料庫（含鎖定與防重複）
    # -------------------------
    def allocate_shop(self, shop):
        intent_summaries = get_rush_summaries(shop)

        with transaction.atomic():
            # 鎖住該商店，避免多 worker 併發
            locked_shop = Shop.objects.select_for_update().get(pk=shop.pk)
            if locked_shop.is_rush_settled:
                # 已被其他程序處理
                return

            product_claimed = defaultdict(int)
            product_orders_bulk = []

            for summary in intent_summaries:
                user = summary['user']
                # 建立空訂單
                order = Order.objects.create(
                    user=user,
                    shop=locked_shop,
                    total=0,
                    payment_mode='full',
                    pay_state_id=PAY_STATE_UNPAID,
                    order_state_id=ORDER_STATE_INIT,
                )

                total_price = 0
                for ip in summary['products']:
                    p = ip.product
                    want_qty = ip.quantity
                    available = max(0, p.stock - product_claimed[p.id])
                    claim_qty = min(want_qty, available)

                    if claim_qty <= 0:
                        continue

                    product_orders_bulk.append(ProductOrder(
                        order=order,
                        product=p,
                        amount=claim_qty,
                        product_name=p.name,
                        product_price=p.price,
                        product_img=(p.img.name if getattr(p, 'img', None) else ''),
                    ))
                    product_claimed[p.id] += claim_qty
                    total_price += p.price * claim_qty

                if total_price == 0:
                    order.delete()
                else:
                    order.total = total_price
                    order.save(update_fields=['total'])

            if product_orders_bulk:
                ProductOrder.objects.bulk_create(product_orders_bulk, batch_size=1000)

            # 切回時間序 + 標記已結算
            locked_shop.purchase_priority_id = 1
            locked_shop.is_rush_settled = True
            locked_shop.save(update_fields=['purchase_priority_id', 'is_rush_settled'])
