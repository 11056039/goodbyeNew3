# core/decorators_base.py
from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from goodBuy_shop.models import Shop
from goodBuy_want.models import Want
from django.db.models import Q

# -------------------------
# 物件存在檢查
# -------------------------
def object_exists_required(
    model,
    arg_name,
    context_name=None,
    not_found_msg='找不到資料',
    redirect_to='home',
    deleted_check=None,  # 可為 'auto', callable, 或 None
    deleted_msg='資料已被刪除'
):
    """
    檢查物件是否存在，若有提供 deleted_check，則額外判斷資料是否為已刪除狀態。
    deleted_check 可為：
        - None：不檢查是否被刪除
        - 'auto'：自動判斷常見刪除欄位（is_delete, permission）
        - callable：自定義 lambda obj -> bool
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj_id = kwargs.get(arg_name)
            try:
                obj = model.objects.get(id=obj_id)
            except model.DoesNotExist:
                messages.error(request, not_found_msg)
                return redirect(redirect_to)

            # 自動判斷是否為已刪除
            if deleted_check == 'auto':
                is_deleted = False
                if hasattr(obj, 'is_delete') and obj.is_delete:
                    is_deleted = True
                elif hasattr(obj, 'permission_id') and getattr(obj, 'permission_id') == 3:
                    is_deleted = True
                elif hasattr(obj, 'permission') and getattr(obj, 'permission') == 3:
                    is_deleted = True
                if is_deleted:
                    messages.error(request, deleted_msg)
                    return redirect(redirect_to)

            elif callable(deleted_check):
                try:
                    if deleted_check(obj):
                        messages.error(request, deleted_msg)
                        return redirect(redirect_to)
                except Exception:
                    messages.error(request, '資料狀態檢查失敗')
                    return redirect(redirect_to)

            kwargs[context_name or model.__name__.lower()] = obj 
            kwargs.pop(arg_name, None)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# -------------------------
# 物件擁有者檢查
# -------------------------
def object_owner_required(
    model,
    arg_name,
    owner_field,
    context_name=None,
    not_found_msg='找不到資料',
    owner_error_msg='您不是擁有者',
    redirect_to='home',
    deleted_check=None,
    deleted_msg='資料已被刪除'
):
    """
    檢查物件是否存在且為使用者擁有者，並可選擇性檢查是否被刪除
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj_id = kwargs.get(arg_name)
            obj = get_object_or_404(model, id=obj_id)

            if deleted_check:
                try:
                    if deleted_check == 'auto':
                        is_deleted = False
                        if hasattr(obj, 'is_delete') and obj.is_delete:
                            is_deleted = True
                        elif hasattr(obj, 'permission_id') and obj.permission_id == 3:
                            is_deleted = True
                        elif hasattr(obj, 'permission') and obj.permission == 3:
                            is_deleted = True
                        if is_deleted:
                            messages.error(request, deleted_msg)
                            return redirect(redirect_to)
                    elif callable(deleted_check) and deleted_check(obj):
                        messages.error(request, deleted_msg)
                        return redirect(redirect_to)
                except Exception:
                    messages.error(request, '資料狀態檢查失敗')
                    return redirect(redirect_to)

            if not request.user.is_authenticated:
                messages.error(request, '需要登入才可操作')
                return redirect('home')

            # 支援巢狀 owner 欄位
            owner = obj
            for attr in owner_field.split('.'):
                owner = getattr(owner, attr)

            if owner != request.user:
                messages.error(request, owner_error_msg)
                return redirect(redirect_to)

            kwargs[context_name or model.__name__.lower()] = obj
            kwargs.pop(arg_name, None) #移除多餘的 shop_id 傳入
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# -------------------------
# 黑名單檢查
# -------------------------
# def blacklist_check(owner_getter, redirect_to='home', msg='你已被此使用者封鎖，無法查看。'):
#     """
#     檢查 request.user 是否被 owner 封鎖
#     owner_getter: lambda obj: obj.owner or obj.shop.owner
#     """
# def blacklist_check(owner_getter, redirect_to='home', msg='你已被此使用者封鎖。', context_name='obj'):
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, obj, *args, **kwargs):
#             if request.user.is_authenticated:
#         def _wrapped_view(request, *args, **kwargs):
#             obj = kwargs.get(context_name)
#             if obj and request.user.is_authenticated:
#                 owner = owner_getter(obj)
#                 from goodBuy_web.models import Blacklist
#                 if Blacklist.objects.filter(user=owner, black_user=request.user).exists():
#                     messages.error(request, msg)
#                     return redirect(redirect_to)
#             return view_func(request, obj, *args, **kwargs)
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

def blacklist_check(owner_getter, redirect_to='home', msg='你與此使用者有封鎖關係，無法查看。', context_name='obj'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj = kwargs.get(context_name)
            if obj and request.user.is_authenticated:
                owner = owner_getter(obj)
                from goodBuy_web.models import Blacklist

                # 雙向封鎖檢查
                blocked = Blacklist.objects.filter(
                    Q(user=owner, black_user=request.user) |
                    Q(user=request.user, black_user=owner)
                ).exists()

                if blocked:
                    print(f"[封鎖觸發] {owner} ⛔ {request.user}（雙向擋）")
                    messages.error(request, msg)
                    return redirect(redirect_to)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# -------------------------
# 訂單是否屬於買家檢查
# -------------------------
def check_order_buyer(redirect_to='home'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, order, *args, **kwargs):
            if getattr(order, 'user_id', None) != getattr(request.user, 'id', None):
                messages.error(request, '您無權操作此訂單')
                return redirect(redirect_to)
            return view_func(request, order, *args, **kwargs)
        return _wrapped_view
    return decorator

# -------------------------
# 訂單是否為賣家商店的檢查
# -------------------------
def check_order_seller(redirect_to='home'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, order, *args, **kwargs):
            if order.shop.owner != request.user:
                messages.error(request, '您無權操作此訂單')
                return redirect(redirect_to)
            return view_func(request, order, *args, **kwargs)
        return _wrapped_view
    return decorator