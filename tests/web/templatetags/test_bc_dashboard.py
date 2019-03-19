from bitcaster.web.templatetags.bc_dashboard import metric


def test_metric():
    return metric('label', 'value')
