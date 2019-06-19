from bitcaster.models import Application


def check_application_subscriptions(app_id):
    app = Application.objects.get(pk=app_id)
    invalid = 0
    for event in app.events.filter(enabled=True):
        for subscription in event.subscriptions.filter(enabled=True):
            if not subscription.recipient:
                subscription.enabled = False
                subscription.save()
                invalid += 1
    return invalid
