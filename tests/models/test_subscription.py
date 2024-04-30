# from contextlib import nullcontext as does_not_raise
#
# import pytest
# from jmespath.exceptions import EmptyExpressionError, ParseError
#
#
# @pytest.mark.parametrize(
#     "filter, expectation",
#     [
#         pytest.param(
#             "", pytest.raises(EmptyExpressionError, match="Invalid JMESPath expression: cannot be empty"), id="empty"
#         ),
#         pytest.param(
#             None, pytest.raises(EmptyExpressionError, match="Invalid JMESPath expression: cannot be empty"), id="none"
#         ),
#         pytest.param(
#             "1", pytest.raises(ParseError, match='invalid token: Parse error at column 0, token "1"'), id="none"
#         ),
#         pytest.param('"JA"', does_not_raise(), id="ok"),
#     ],
# )
# def test_check_filter(filter, expectation):
#     from bitcaster.models import Subscription
#
#     with expectation:
#         Subscription.check_filter(filter)
#     assert True
