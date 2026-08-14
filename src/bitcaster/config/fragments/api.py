from bitcaster.config import env

# Lifetime (seconds) of client tokens minted via the token exchange endpoint.
CLIENT_TOKEN_TTL = env.int("CLIENT_TOKEN_TTL")
# Maximum size in bytes of the serialized `context` payload accepted from web credentials.
TRIGGER_CONTEXT_MAX_SIZE = env.int("TRIGGER_CONTEXT_MAX_SIZE")
