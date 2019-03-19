def test_wsgi():
    from bitcaster.config.wsgi import application
    assert application
