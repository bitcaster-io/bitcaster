from uuid import UUID, uuid4, uuid5

NAMESPACE_API = UUID('b9209163-3a51-4cdc-a534-34422fed7be9')
NAMESPACE_SUBSCRIPTION = UUID('d617f4ed-bb71-46ea-97ac-c3d2f403f8c5')


def generate_subscription_token(subscription):
    return uuid5(NAMESPACE_SUBSCRIPTION, str(subscription.pk)).hex + uuid4().hex


def generate_api_token():
    return uuid5(NAMESPACE_API, 'api').hex + uuid4().hex


def generate_token():
    return uuid4().hex + uuid4().hex
