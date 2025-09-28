from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.db.models import *
from django.shortcuts import *

from .models import *

def get_blocked_user_ids(user):
    if not user or not user.is_authenticated:
        return []

    # 自己封鎖別人的
    blocked_by_me = Blacklist.objects.filter(user=user).values_list('black_user_id', flat=True)
    # 被對方封鎖
    blocked_me = Blacklist.objects.filter(black_user=user).values_list('user_id', flat=True)

    # 合併成一個 set
    return set(blocked_by_me).union(set(blocked_me))