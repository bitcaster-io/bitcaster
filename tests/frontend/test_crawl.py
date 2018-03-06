import pytest

pytestmark = pytest.mark.django_db


def test_initial_setup(django_app, application1):
    "home is always accessible"
    organization = application1.organization
    owner = organization.owner

    res = django_app.get('/', user=owner.email)
    # res = res.click("Login")
    # res.form["username"] = owner.email
    # res.form["password"] = owner._password
    # res = res.form.submit().follow()
    #
    res = res.click(organization.name)
    res = res.click("Configuration")
    res.form["slug"] = "org_slug"
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
    res = res.click(organization.name, index=1)
