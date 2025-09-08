from django.urls import path
from goodBuy_order.views import *


urlpatterns = [
    path('<int:user_id>/feedback/', view_user_feedback_page, name='view_user_feedback_page'),
    path('timeline/', payment_timeline, name='payment_timeline'),
]