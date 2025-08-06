# core/decorators_shortcuts.py
from .decorators_base import *
from django.contrib.auth import get_user_model
from goodBuy_shop.models import Shop, Product, ShopAnnouncement
from goodBuy_tag.models import Tag
from goodBuy_order.models import *
from goodBuy_want.models import Want


User = get_user_model()

# --- 基礎存在驗證 ---
# -------------------------
# 商店存在檢查
# -------------------------
shop_exists_required = object_exists_required(
    model=Shop,
    arg_name='shop_id',
    context_name='shop',
    deleted_check='auto',
    deleted_msg='這個商店已被刪除'
)
# -------------------------
# 商品存在檢查
# -------------------------
product_exists_required = object_exists_required(
    model=Product,
    arg_name='product_id',
    context_name='product',
    deleted_check='auto',
    deleted_msg='這個商品或商店已被刪除'
)
# -------------------------
# 訂單存在檢查
# -------------------------
order_exists_required = object_exists_required(
    model=Order,
    arg_name='order_id',
    context_name='order',
    not_found_msg='找不到這個訂單'
)
# -------------------------
# 標籤存在檢查
# -------------------------
tag_exists_required = object_exists_required(
    model=Tag,
    arg_name='tag_id',
    context_name='tag',
    not_found_msg='找不到這個Tag'
)
# -------------------------
# 使用者存在檢查
# -------------------------
user_exists_required = object_exists_required(
    model=User,
    arg_name='user_id',
    context_name='user',
    not_found_msg='找不到使用者'
)
# -------------------------
# 收物帖存在檢查
# -------------------------
want_exists_required = object_exists_required(
    model=Want,
    arg_name='want_id',
    context_name='want',
    not_found_msg='找不到這個收物帖'
)
# -------------------------
# 付款記錄存在檢查
# -------------------------
payment_exists_required = object_exists_required(
    model=OrderPayment,
    arg_name='payment_id',
    context_name='payment',
    not_found_msg='找不到這個支付記錄'
)

# --- 擁有者驗證 ---
# -------------------------
# 商店擁有者檢查
# -------------------------
shop_owner_required = object_owner_required(
    model=Shop,
    arg_name='shop_id',
    owner_field='owner',
    context_name='shop',
    not_found_msg='找不到商店',
    owner_error_msg='這不是您的商店哦',
    deleted_check='auto',
    deleted_msg='這個商店已被刪除'
)
# -------------------------
# 產品擁有者檢查
# -------------------------
product_owner_required = object_owner_required(
    model=Product,
    arg_name='product_id',
    owner_field='shop.owner',
    context_name='product',
    not_found_msg='找不到商品',
    owner_error_msg='這不是您的商品哦',
    deleted_check='auto',
    deleted_msg='這個商品或商店已被刪除'
)
# -------------------------
# 收物帖擁有者檢查
# -------------------------
want_owner_required = object_owner_required(
    model=Want,
    arg_name='want_id',
    owner_field='user',
    context_name='want',
    not_found_msg='找不到這篇收物帖',
    owner_error_msg='這不是您的收物帖喔',
    deleted_check='auto',
    deleted_msg='這篇收物帖已被刪除'
)
# -------------------------
# 公告擁有者檢查
# -------------------------
announcement_owner_required = object_owner_required(
    model=ShopAnnouncement,
    arg_name='announcement_id',
    owner_field='shop.owner',
    context_name='announcement',
    not_found_msg='找不到這則公告',
    owner_error_msg='這不是您商店的公告喔',
    deleted_check=lambda a: a.shop.permission_id == 3,
    deleted_msg='此公告所屬商店已被刪除'
)
# -------------------------
# 訂單支付記錄擁有者檢查
# -------------------------
order_payment_owner_required = object_owner_required(
    model=OrderPayment,
    arg_name='payment_id',
    owner_field='order.shop.owner',
    context_name='payment',
    not_found_msg='找不到這筆付款紀錄',
    owner_error_msg='您無權審核此筆付款',
    deleted_check=lambda p: p.order.shop.permission_id == 3,
    deleted_msg='此付款所屬商店已被刪除'
)

# --- 訂單買家和賣家檢查 ---
# -------------------------
# 訂單為購買者擁有檢查
# -------------------------
def order_buyer_required(redirect_to='home'):
    return lambda view_func: \
        order_exists_required(check_order_buyer(redirect_to=redirect_to)(view_func))
# -------------------------
# 訂單為賣家擁有檢查
# -------------------------
def order_seller_required(redirect_to='home'):
    return lambda view_func: \
        order_exists_required(check_order_seller(redirect_to=redirect_to)(view_func))
