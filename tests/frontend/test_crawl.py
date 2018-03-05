import pytest

pytestmark = pytest.mark.django_db


def test_initial_setup(django_app, application1):
    "home is always accessible"
    organization = application1.organization
    # owner = organization.owner

    res = django_app.get('/')
    res = res.click("Login")
    res.form["username"] = application1.owner.email
    res.form["password"] = '123'
    res = res.form.submit()
    # FIXME: remove this line (pdb)
    import pdb; pdb.set_trace()
    assert res.status_code == 302, res.showbrowser()
    res = res.follow()
    # configure organization
    #   general
    res = res.click(organization.name)
    res.form["slug"] = organization.name.lower()
    res.form["billing_email"] = "billing@noreply.org"
    res = res.form.submit().follow()
    #   channels
    res = res.click("Channels")

    #   channels
    res = res.click("Members")

    #   applications
    res = res.click("Applications")
    res = res.click("Create new application")
    res.form["name"] = "Application1"
    res = res.form.submit().follow()
    # now we are in Application screen
    # go beck to Organization
    res = res.click(organization.name)
