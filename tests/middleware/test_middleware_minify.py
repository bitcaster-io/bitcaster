# mypy: disable-error-code="union-attr"
from unittest.mock import Mock

import pytest
from constance.test import override_config
from django.http import HttpResponse
from django.test.client import RequestFactory

from bitcaster.middleware.minify import MinifyFlag

page = """
<h1>aaaa</h1>
 <div>
    <span>aaaa</span>
 </div>
<table>
    <tr>
        <th>h11               </th>
        <td>a11               </td>
        <td>a12               </td>
    </tr>
    <tr>
        <th>h21               </th>
        <td>a21               </td>
        <td>a22               </td>
    </tr>
    <tr>
        <th>h31               </th>
        <td>a31               </td>
        <td>a32               </td>
    </tr>
</table>
   """


@override_config(MINIFY_RESPONSE=MinifyFlag.HTML + MinifyFlag.NEWLINE + MinifyFlag.SPACES)  # type: ignore[misc]
def test_minify_base_handling(rf: RequestFactory) -> None:
    from bitcaster.middleware.minify import HtmlMinMiddleware

    request = rf.get("/", headers={"HTT_Content_Type": "text/html"})
    m = HtmlMinMiddleware(lambda x: HttpResponse(page))
    res = m(request)
    assert res.content.decode() == (
        "<h1>aaaa</h1><div><span>aaaa</span></div><table><tr><th>h11 "
        "</th><td>a11 </td><td>a12 </td></tr><tr><th>h21 </th><td>a21 "
        "</td><td>a22 </td></tr><tr><th>h31 </th><td>a31 </td><td>a32 </td></tr></table>"
    )


@pytest.mark.parametrize("opt", [MinifyFlag.HTML, MinifyFlag.NEWLINE, MinifyFlag.SPACES])
def test_minify_base_handling_option(rf: RequestFactory, opt: MinifyFlag) -> None:
    from bitcaster.middleware.minify import HtmlMinMiddleware

    override_config(MINIFY_RESPONSE=opt).enable()
    request = rf.get("/", headers={"HTT_Content_Type": "text/html"})
    m = HtmlMinMiddleware(lambda x: HttpResponse(page))
    res = m(request)
    assert res.content.decode()


@override_config(
    MINIFY_RESPONSE=MinifyFlag.HTML + MinifyFlag.NEWLINE + MinifyFlag.SPACES, MINIFY_IGNORE_PATH="aa.*"
)  # type: ignore[misc]
def test_minify_base_handling_option_path(rf: RequestFactory) -> None:
    from bitcaster.middleware.minify import HtmlMinMiddleware

    request = rf.get("/", headers={"HTT_Content_Type": "text/html"})
    m = HtmlMinMiddleware(lambda x: HttpResponse(page))
    res = m(request)
    assert res.content.decode() == (
        "<h1>aaaa</h1><div><span>aaaa</span></div><table><tr><th>h11 "
        "</th><td>a11 </td><td>a12 </td></tr><tr><th>h21 </th><td>a21 "
        "</td><td>a22 </td></tr><tr><th>h31 </th><td>a31 </td><td>a32 </td></tr></table>"
    )


@override_config(
    MINIFY_RESPONSE=MinifyFlag.HTML + MinifyFlag.NEWLINE + MinifyFlag.SPACES, MINIFY_IGNORE_PATH="aa.*"
)  # type: ignore[misc]
def test_minify_skip(rf: RequestFactory) -> None:
    from bitcaster.middleware.minify import HtmlMinMiddleware

    request = rf.get("/", headers={"HTT_Content_Type": "text/html"})
    m = HtmlMinMiddleware(lambda x: HttpResponse("<a  ></a>"))
    res = m(request)
    assert res.content.decode() == "<a  ></a>"


@override_config(MINIFY_RESPONSE=MinifyFlag.HTML)  # type: ignore[misc]
def test_minify_update_config() -> None:
    from bitcaster.middleware.minify import HtmlMinMiddleware

    m = HtmlMinMiddleware(lambda x: HttpResponse("<a  ></a>"))
    m.update_config(Mock(), "aa", 22, 33)
