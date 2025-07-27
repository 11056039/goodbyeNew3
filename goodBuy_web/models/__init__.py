from .user import User
from .blacklist import Blacklist
from .profile import Profile
from .payment import Payment
from .payment_account import PaymentAccount
from .user_address import UserAddress
from .search_history import SearchHistory

# 讓 User 物件擁有 .profile 屬性
def get_profile(self):
    return Profile.objects.filter(user=self).first()

User.add_to_class('profile', property(get_profile))