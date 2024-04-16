from bitcaster.utils.constance import EmailChannel


def test_emailchannel(db, channel):
    fld = EmailChannel()
    assert fld.choices == [("", "None"), (channel.pk, channel.name)]
