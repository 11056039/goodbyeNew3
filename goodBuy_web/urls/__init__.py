from .web import urlpatterns as web_urlpatterns
from .user import urlpatterns as user_urlpatterns
from .blacklist import urlpatterns as blacklist_urlpatterns
from .profile import urlpatterns as profile_urlpatterns

urlpatterns = web_urlpatterns + user_urlpatterns + blacklist_urlpatterns + profile_urlpatterns
