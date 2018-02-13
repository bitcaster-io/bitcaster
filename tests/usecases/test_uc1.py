# -*- coding: utf-8 -*-
import tempfile
import webbrowser

import pytest
from rest_framework.reverse import reverse
import requests

#
# @pytest.fixture(scope="module")
# def browser():
#     selenium = WebDriver()
#     selenium.implicitly_wait(10)
#     yield selenium
#     selenium.quit()


# MacOS
chrome_path = 'open -a /Applications/Google\ Chrome.app %s'


# Windows
# chrome_path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s'

# Linux
# chrome_path = '/usr/bin/google-chrome %s'

class Client:
    def __init__(self, user, server):
        self.server = server
        self.user = user
        self.headers = {}

    def login(self):
        self.headers[b'AUTHORIZATION'] = "Token {}".format(self.user.tokens.first().token)

    def logout(self):
        self.headers[b'AUTHORIZATION'] = ""

    def get(self, url):
        return requests.get(self.server.url + url,
                            headers=self.headers)

    def post(self, url, data=None):
        return requests.get(self.server.url + url,
                            data=data,
                            headers=self.headers)

    def showbrowser(self, res):
        t = tempfile.NamedTemporaryFile()
        with open(t.name, "w") as f:
            f.write(str(res.content))
        webbrowser.get().open(t.name)


@pytest.fixture()
def demo(message1, message2):
    return message1, message2


def test_access_owned_objects(live_server, demo):
    message1, message2 = demo
    event1 = message1.event
    event2 = message2.event
    application1 = event1.application
    application2 = event2.application
    channel1 = message1.channels.first()
    channel2 = message2.channels.first()

    client = Client(application1.owner, live_server)

    # Anonmymous cannot access applications list
    url = reverse('api:application-list')
    res = client.get(url)
    assert res.status_code == 403

    client.login()
    # Auth cannot access applications list but it will be filtered
    res = client.get(url)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Owner can access owned application
    url = reverse('api:application-detail', args=[application1.pk])
    res = client.get(url)
    assert res.status_code == 200, url

    # Owner canNOT access alien application
    url = reverse('api:application-detail', args=[application2.pk])
    res = client.get(url)
    assert res.status_code == 404, url

    res = client.post(url, {})
    assert res.status_code == 404, url

    # Owner can access application related components
    url = reverse('api:application-channel-list', args=[application1.pk])
    res = client.get(url)
    assert res.status_code == 200, url
    assert len(res.json()) == application1.channels.count()

    url = reverse('api:application-event-list', args=[application1.pk])
    res = client.get(url)
    assert res.status_code == 200, url
    assert len(res.json()) == application1.events.count()

    # Owner can access application related components
    url = reverse('api:application-channel-detail', args=[application1.pk,
                                                          channel1.pk])
    res = client.get(url)
    assert res.json()['name'] == channel1.name

    url = reverse('api:application-event-detail', args=[application1.pk,
                                                        event1.pk])
    res = client.get(url)
    assert res.json()['name'] == event1.name

    url = reverse('api:application-message-detail', args=[application1.pk,
                                                          message1.pk])
    res = client.get(url)
    assert res.json()['name'] == message1.name

    # Owner canNOT access other tapplication related components
    url = reverse('api:application-channel-detail', args=[application2.pk,
                                                          channel2.pk])
    res = client.get(url)
    assert res.status_code == 403, url

    url = reverse('api:application-channel-detail', args=[application1.pk,
                                                          channel2.pk])
    res = client.get(url)
    assert res.status_code == 404, url

    url = reverse('api:application-event-detail', args=[application2.pk,
                                                        event2.pk])
    res = client.get(url)
    assert res.status_code == 403, url

    url = reverse('api:application-event-detail', args=[application1.pk,
                                                        event2.pk])
    res = client.get(url)
    assert res.status_code == 404, url

    url = reverse('api:application-message-detail', args=[application2.pk,
                                                          message2.pk])
    res = client.get(url)
    assert res.status_code == 403, url

    url = reverse('api:application-message-detail', args=[application1.pk,
                                                          message2.pk])
    res = client.get(url)
    assert res.status_code == 404, url
