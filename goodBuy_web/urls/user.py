from django.urls import path
from goodBuy_web.views import *

urlpatterns = [
    path('payment_accounts/', payment_accounts, name='payment_accounts'),
]