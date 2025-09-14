from django.urls import path
from goodBuy_web.views import *

urlpatterns = [
    path('', homePage, name='home'),
    path('login/', logins, name='login'),
    path('register/', register, name='register'),
    path('logout/', logouts, name='logout'),
]