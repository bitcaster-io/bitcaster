from bitcaster.models import Address, Channel


def test_manager_valid(address: "Address", channel: "Channel"):
    assert not Address.objects.valid()
    address.validate_channel(channel)
    assert Address.objects.valid()


def test_address(db):
    from testutils.factories import AddressFactory, ChannelFactory

    addr: "Address" = AddressFactory()
    ch: "Channel" = ChannelFactory()
    addr.validate_channel(ch)

    assert list(addr.channels.all()) == [ch]
