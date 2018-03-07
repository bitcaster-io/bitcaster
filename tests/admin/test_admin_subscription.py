# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse


def test_subscriptions_list(django_app, admin):
    url = reverse("admin:mercury_subscription_changelist")
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200


# def test_subscriptions_add(django_app, admin, event1, channel1, user1):
#     url = reverse("admin:mercury_subscription_add")
#     res = django_app.get(url, user=admin.email)
#     res.form['subscriber'] = user1
#     res.form['channel'] = channel1
#     res.form['event'] = event1
#     res = res.submit().follow()
#     assert res.status_code == 200
#
#
# @pytest.mark.parametrize("action", ["activate", "deactivate"])
# def test_channel_adminaction_bulk(action, django_app: django_webtest.DjangoTestApp,
#                                   admin, subscription1: Subscription):
#     url = reverse("admin:mercury_subscription_changelist")
#     res = django_app.get(url, user=admin.email)
#     res.form['action'] = action
#     res.form['_selected_action'] = [subscription1.pk]
#     res = res.form.submit()
#     assert res.status_code == 302
#     assert subscription1.active
