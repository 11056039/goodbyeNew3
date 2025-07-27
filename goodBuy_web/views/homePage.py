from django.shortcuts import render

from goodBuy_shop.shop_utils import *
from goodBuy_shop.weighting import *
from goodBuy_shop.hot_rank import *

from goodBuy_want.want_utils import *
from goodBuy_want.weighting import *
from goodBuy_want.hot_rank import *

from goodBuy_tag.models import *

from itertools import chain
from operator import attrgetter

def homePage(request):
    #篩選
    post_type = request.GET.get('type')  # sell / want 
    tag = request.GET.get('tag')         # 標籤名稱 

    if request.user.is_authenticated:
        # 個人化推薦（最多 10 筆）
        personalized = personalized_shop_recommendation(request.user, limit=10)
        exclude_ids = [s.id for s in personalized]

        # 熱門商店：先排除個人化中出現過的，再取前 10 筆
        hot_shop = get_hot_shops().exclude(id__in=exclude_ids)[:10]

        shop_ids = list(personalized.values_list('id', flat=True)) + list(hot_shop.values_list('id', flat=True))
        shops = Shop.objects.filter(id__in=shop_ids)

        # 個人化 want 推薦（最多 10 筆）
        personalized = personalized_want_recommendation(request.user, limit=10)
        exclude_ids = [w.id for w in personalized]

        # 熱門 want：先排除個人化中出現過的，再取前 10 筆
        hot_want = get_hot_wants().exclude(id__in=exclude_ids)[:10]
        want_ids = list(personalized.values_list('id', flat=True)) + list(hot_want.values_list('id', flat=True))
        wants = Want.objects.filter(id__in=want_ids)

    else:
        # 未登入使用者直接看熱門
        shops = get_hot_shops(limit=20)
        wants = get_hot_wants(limit=20)
    
    # 篩選條件：只顯示特定 type（sell / want）
    if post_type == 'sell':
        wants = Want.objects.none()
    elif post_type == 'want':
        shops = Shop.objects.none()

    # 整理資訊
    shops = shopInformation_many(shops)
    wants = wantInformation_many(wants)

    for s in shops:
        s.post_type = 'shop'

    for w in wants:
        w.post_type = 'want'

    # 商店混和排序
    items = sorted(
        chain(shops, wants), 
        key=attrgetter('update'), 
        reverse=True
    )

    return render(request, 'home.html', locals())
