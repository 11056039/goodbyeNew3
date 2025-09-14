from django.urls import path
from goodBuy_web.views import *

urlpatterns = [
    path('', view_blacklist, name='blacklist'),
    path('add/', add_to_blacklist, name='blacklist_add'),
    path('remove/', remove_from_blacklist, name='blacklist_remove'),
    ]