# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


# @pytest.mark.django_db
# def test_create_member(django_app, organization1):
#     owner = organization1.owner
#     pwd = uuid4()
#
#     url = reverse('org-member-register', args=[organization1.slug])
#     res = django_app.get(url, user=owner.email)
#     res.form['email'] = 'test@noreply.org'
#     res.form['password1'] = str(pwd)
#     res.form['password2'] = str(pwd)
#     res = res.form.submit()
#     res = res.follow()
#     assert User.objects.get(email='test@noreply.org')
#
#
# @pytest.mark.django_db
# def test_create_member_fail(django_app, organization1):
#     owner = organization1.owner
#     pwd = uuid4()
#
#     url = reverse('org-member-register', args=[organization1.slug])
#     res = django_app.get(url, user=owner.email)
#     res.form['email'] = 'test@noreply.org'
#     res.form['password1'] = str(pwd)
#     res.form['password2'] = '--'
#     assert res.status_code == 200
