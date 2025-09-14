from django.urls import path
from goodBuy_web.views import *
from goodBuy_order.views.comment import view_user_feedback_page

urlpatterns = [
    path('editprofile/', editProfile, name='editprofile'),
    path('payment_accounts/', payment_accounts, name='payment_accounts'),
]