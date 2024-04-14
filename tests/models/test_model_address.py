from bitcaster.models import Address, Channel


def test_manager_valid(address: "Address", channel: "Channel"):
    assert not Address.objects.valid()
    address.validate_channel(channel)
    assert Address.objects.valid()
