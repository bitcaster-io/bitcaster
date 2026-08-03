from typing import TYPE_CHECKING

from allauth.account.authentication import get_authentication_records
from allauth.socialaccount.models import SocialAccount

if TYPE_CHECKING:
    from django.http import HttpRequest

    from bitcaster.social.models import SocialProvider


def is_own_login_provider(request: "HttpRequest", provider: "SocialProvider") -> bool:
    """Check if `provider` authenticated the current session or is linked to the requesting user.

    SocialApp instances are built with ``provider_id=str(SocialProvider.pk)`` (see
    ``BitcasterSocialAccountAdapter._build_social_app``), so both the allauth session
    authentication records and ``SocialAccount.provider`` store the SocialProvider pk.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return False
    for record in get_authentication_records(request):
        if record.get("method") == "socialaccount" and str(record.get("provider")) == str(provider.pk):
            return True
    return SocialAccount.objects.filter(user=user.pk, provider=str(provider.pk)).exists()
