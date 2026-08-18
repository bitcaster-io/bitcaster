from typing import TYPE_CHECKING, Any

from anymail.backends.amazon_ses import EmailBackend as AmazonSESBackend

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import DispatcherConfig

from .base import AnyMailDispatcher

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import DispatcherHandler


class AmazonSESConfig(DispatcherConfig):
    aws_access_key_id = forms.CharField(label=_("AWS Access Key ID"))
    aws_secret_access_key = forms.CharField(label=_("AWS Secret Access Key"), widget=forms.PasswordInput)
    aws_region = forms.CharField(label=_("AWS Region"), initial="us-east-1", required=False)

    help_text = "Create an IAM user with ses:SendEmail permission in your AWS account."


class AmazonSESDispatcher(AnyMailDispatcher):
    slug = "ses"
    verbose_name = "Amazon SES Email"
    config_class = AmazonSESConfig
    backend = AmazonSESBackend

    def get_connection(self) -> "DispatcherHandler":
        kwargs: dict[str, Any] = {
            "session_params": {
                "aws_access_key_id": self.config["aws_access_key_id"],
                "aws_secret_access_key": self.config["aws_secret_access_key"],
            }
        }
        if region := self.config.get("aws_region"):
            kwargs["client_params"] = {"region_name": region}
        return self.backend(fail_silently=False, **kwargs)
