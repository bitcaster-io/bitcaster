from .address import (UserAddressCreate, UserAddressDelete,
                      UserAddressesAssignmentView, UserAddressesInfoView,
                      UserAddressesVerifyView, UserAddressesView,
                      UserAddressUpdate,)
from .application import UserApplicationListView
from .base import UserHome, UserProfileView
from .events import UserEventListView
from .log import UserNotificationLogView
from .social import UserSocialAuthDisconnectView, UserSocialAuthView
from .subscriptions import (UserSubscriptionCreate, UserSubscriptionEdit,
                            UserSubscriptionListView, UserSubscriptionRemove,
                            UserSubscriptionToggle,)
