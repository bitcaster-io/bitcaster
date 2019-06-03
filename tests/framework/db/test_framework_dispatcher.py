from bitcaster.dispatchers import Email, Gmail, dispatcher_registry
from bitcaster.framework.forms.fields import DispatcherFormField
from bitcaster.utils.reflect import fqn


def test_DispatcherFormField():
    dispatcher1 = Email
    dispatcher2 = Gmail
    f = DispatcherFormField(registry=dispatcher_registry)

    assert f.has_changed(dispatcher1, fqn(dispatcher2))
    assert not f.has_changed(dispatcher1, fqn(dispatcher1))
    assert f.has_changed(dispatcher1, None)
