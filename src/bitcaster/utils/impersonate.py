from bitcaster.models import User


def queryset(request):
    return User.objects.exclude(id=request.user.id).exclude(is_superuser=True).order_by('email')
