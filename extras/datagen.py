import factory

USERS = 1000
GROUPS = 5
EVENTS = 5
NOTIFICATIONS = 5000
OCCURENCES = 2000
AUDITLOGS = 1000

if __name__ == '__main__':  # noqa: C901
    import os
    import random
    from django.core.wsgi import get_wsgi_application

    os.environ['DJANGO_SETTINGS_MODULE'] = 'bitcaster.config.settings'
    application = get_wsgi_application()

    from bitcaster.models import Organization, Subscription, Notification, Event
    from bitcaster.utils.tests import factories

    org = Organization.objects.first()
    app = factories.ApplicationFactory(organization=org, name='Dummy1')
    users = []

    for i in range(0, USERS):
        print('.', end='')
        user = factories.UserFactory(email='user%s@example.com' % i)
        org_member = factories.OrganizationMemberFactory(organization=org, user=user)
        users.append(org_member)
        factories.ApplicationMemberFactory(application=app, org_member=org_member)
        assert Organization.objects.count() == 1

    if not users:
        users = list(org.memberships.all())

    channels = list(org.channels.all())

    for i in range(0, GROUPS):
        group = factories.OrganizationGroupFactory(organization=org, name='Group-%s' % i)
        assert Organization.objects.count() == 1
        if not group.members.exists():
            members = random.sample(users, random.randint(5, 15))
            for m in members:
                group.members.add(m)

    for i in range(0, EVENTS):
        event = factories.EventFactory(application=app, enabled=True, name='Event-%s' % i)
        assert Organization.objects.count() == 1
        chs = random.sample(channels, random.randint(1, 5))
        for ch in chs:
            event.channels.add(ch)
            factories.MessageFactory(event=event,
                                     channel=ch, body='test')

        members = random.sample(users, random.randint(5, 300))
        for m in members:
            ch = random.choice(chs)
            factories.AddressFactory(user=m.user, address='123')
            assert Organization.objects.count() == 1
            factories.SubscriptionFactory(subscriber=m.user,
                                          trigger_by=m.user,
                                          channel=ch,
                                          event=event)
            assert Organization.objects.count() == 1

    fld = Notification._meta.get_field('timestamp')
    fld.auto_now_add = False
    Notification.timestamp.auto_now_add = False

    events = list(app.events.all())
    subscriptions = list(Subscription.objects.filter(event__application=app))
    # Notification Log
    for i in range(NOTIFICATIONS):
        subscription = random.choice(subscriptions)
        factories.NotificationFactory(id=i,
                                      application=app,
                                      event=subscription.event,
                                      subscription=subscription,
                                      channel=subscription.channel)
        assert Organization.objects.count() == 1

    # Notification Log
    for i in range(OCCURENCES):
        factories.OccurenceFactory(id=i,
                                   organization=org,
                                   application=app,
                                   event=factory.LazyAttribute(lambda a: Event.objects.order_by('?').first()))

    # Audit Log
    for i in range(AUDITLOGS):
        e = factories.AuditLogEntryFactory(id=i,
                                           organization=org,
                                           )
