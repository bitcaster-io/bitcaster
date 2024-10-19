from bitcaster.models import Assignment


class Browser(Assignment):
    class Meta:
        proxy = True
