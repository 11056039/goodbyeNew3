from goodBuy_web.models import Blacklist
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
import re
from django.contrib import messages
from goodBuy_web.models import User

@login_required
def view_blacklist(request):
    blacklist = Blacklist.objects.filter(user=request.user)
    return render(request, 'blacklist/add_blacklist.html', {'blacklist': blacklist})

@login_required
def add_to_blacklist(request):
    if request.method == 'POST':
        black_user_id = request.POST.get('black_user_id')
        if not black_user_id:
            messages.error(request, '封鎖對象未提供')
            return redirect('blacklist')

        try:
            black_user = User.objects.get(id=black_user_id)
        except User.DoesNotExist:
            messages.error(request, '該用戶不存在')
            return redirect('blacklist')

        if Blacklist.objects.filter(user=request.user, black_user=black_user).exists():
            messages.error(request, '該用戶已存在於您的黑名單中')
        else:
            Blacklist.objects.create(user=request.user, black_user=black_user)
            messages.success(request, '成功加入黑名單')

        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)

@login_required
def remove_from_blacklist(request):
    if request.method == 'POST':
        black_user_id = request.POST.get('black_user_id')
        Blacklist.objects.filter(user=request.user, black_user_id=black_user_id).delete()
        messages.success(request, '已從黑名單中移除')

        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)