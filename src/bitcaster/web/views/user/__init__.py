from .address import (UserAddressesAssignmentView, UserAddressesInfoView,
                      UserAddressesVerifyView, UserAddressesView,)
from .application import UserApplicationListView
from .base import UserHome, UserProfileView
from .events import UserEventListView, UserEventSubcribe
from .social import UserSocialAuthDisconnectView, UserSocialAuthView
from .subscriptions import (UserSubscriptionEdit, UserSubscriptionListView,
                            UserSubscriptionRemove, UserSubscriptionToggle,)
