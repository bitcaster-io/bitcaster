from io import BytesIO

import requests
from rest_framework import serializers

from .base import Attachment, BaseRetriever, RetrieverOptions
from .registry import registry


class HttpOptions(RetrieverOptions):
    username = serializers.CharField(allow_blank=True, required=False)
    password = serializers.CharField(allow_blank=True, required=False)

    url_pattern = serializers.CharField()
    name_pattern = serializers.CharField()


@registry.register
class HttpRetriever(BaseRetriever):
    options_class = HttpOptions

    def get(self, subscription) -> Attachment:
        name = self.parse_name(subscription=subscription)
        url = self.parse_template(subscription=subscription)
        r = requests.get(url, stream=True)
        content_type = r.headers['content-type']

        return Attachment(name, BytesIO(r.content), content_type)
