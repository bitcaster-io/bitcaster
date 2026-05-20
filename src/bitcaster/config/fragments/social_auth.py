ACCOUNT_ADAPTER = "bitcaster.social.adapter.BitcasterAccountAdapter"
SOCIALACCOUNT_ADAPTER = "bitcaster.social.adapter.BitcasterSocialAccountAdapter"

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# Passkey / MFA settings
MFA_PASSKEY_LOGIN_ENABLED = False
MFA_PASSKEY_SIGNUP_ENABLED = False
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes", "webauthn"]
