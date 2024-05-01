from bitcaster.models import ApiKey, Application, User


def test_manager_get_or_create(application: "Application", user: "User"):
    assert ApiKey.objects.get_or_create(user=user, application=application)
    assert ApiKey.objects.get_or_create(user=user, project=application.project)
    assert ApiKey.objects.get_or_create(user=user, organization=application.project.organization)

    assert ApiKey.objects.get_or_create(user=user, defaults={"application": application})
    assert ApiKey.objects.get_or_create(user=user, defaults={"project": application.project})
    assert ApiKey.objects.get_or_create(user=user, defaults={"organization": application.project.organization})


def test_manager_update_or_create(application: "Application", user: "User"):
    assert ApiKey.objects.update_or_create(user=user, application=application)
    assert ApiKey.objects.update_or_create(user=user, project=application.project)
    assert ApiKey.objects.update_or_create(user=user, organization=application.project.organization)

    assert ApiKey.objects.update_or_create(user=user, defaults={"application": application})
    assert ApiKey.objects.update_or_create(user=user, defaults={"project": application.project})
    assert ApiKey.objects.update_or_create(user=user, defaults={"organization": application.project.organization})
