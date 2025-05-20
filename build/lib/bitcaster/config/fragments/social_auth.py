from ..settings import env

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "email",
]
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_URL_NAMESPACE = "social"
# SOCIAL_AUTH_REQUIRE_POST = True
SOCIAL_AUTH_STRATEGY = "bitcaster.social.strategy.BitcasterStrategy"

# SOCIAL_AUTH_PIPELINE = (
#     "social_core.pipeline.social_auth.social_uid",
#     "social_core.pipeline.social_auth.auth_allowed",
#     "social_core.pipeline.social_auth.social_user",
#     "social_core.pipeline.user.get_username",
#     "social_core.pipeline.social_auth.associate_by_email",
#     "social_core.pipeline.social_auth.associate_user",
#     "social_core.pipeline.social_auth.load_extra_data",
#     "social_core.pipeline.user.user_details",
# )
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "bitcaster.social.pipeline.save_to_group",
)

SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_REDIRECT_IS_HTTPS = env.bool("SOCIAL_AUTH_REDIRECT_IS_HTTPS")
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_RAISE_EXCEPTIONS = env("SOCIAL_AUTH_RAISE_EXCEPTIONS")

SOCIAL_LOGIN_URL = env("SOCIAL_AUTH_LOGIN_URL")

USER_FIELDS = ["username", "email", "first_name", "last_name"]
