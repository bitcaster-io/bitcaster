from unittest.mock import Mock

from bitcaster.middleware.state import StateMiddleware
from bitcaster.state import state


def test_state_middleware():
    def get_response(request):
        assert state.request == request
        return Mock()

    middleware = StateMiddleware(get_response)
    request = Mock()
    response = middleware(request)

    assert state.request is None
    assert response is not None
