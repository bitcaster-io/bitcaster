from django.utils.translation import gettext as _

FILTERING_NONE = 1
FILTERING_EXTERNAL = 3
FILTERING_DYNAMIC = 4
FILTERING = (
    (FILTERING_NONE, _("No Filters. Forward to distribution list")),
    (FILTERING_EXTERNAL, _("API filters. Do not use DistributionList, filter users by API rules")),
    (FILTERING_DYNAMIC, _("Filter users using provided rules.")),
)
