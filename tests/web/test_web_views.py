from django.urls import reverse


def test_home(db, client):
    assert client.get("/").status_code == 200


def test_login(db, client):
    assert client.get(reverse("login")).status_code == 200
