from django.urls import path
from goodBuy_web.views import *

urlpatterns = [
    path('<int:user_id>/', view_profile, name='view_profile'),
    path('<int:user_id>/more/<str:tab>/', user_more, name='user_more'),
]