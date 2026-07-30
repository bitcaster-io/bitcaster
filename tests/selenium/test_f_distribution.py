from typing import TYPE_CHECKING

import pytest
from testutils.selenium import TestBrowser

if TYPE_CHECKING:
    from bitcaster.models import DistributionList

pytestmark = pytest.mark.selenium


@pytest.mark.flaky(max_runs=2)
def test_distribution_list_autocomplete_chain(browser: TestBrowser, db) -> None:
    from testutils.factories.org import ApplicationFactory, OrganizationFactory, ProjectFactory

    from bitcaster.models import DistributionList

    org = OrganizationFactory()
    project1 = ProjectFactory(organization=org, name="Project Alpha")
    project2 = ProjectFactory(organization=org, name="Project Beta")
    app1 = ApplicationFactory(project=project1, name="App One")
    app2 = ApplicationFactory(project=project2, name="App Two")

    browser.login()
    browser.open("/admin/bitcaster/distributionlist/add/")
    browser.wait_for_ready_state_complete()
    current_url = browser.get_current_url()
    assert "distributionlist/add" in current_url, f"Expected add form URL, got: {current_url}"
    browser.wait_for_element_visible("#id_project", timeout=10)

    browser.select2_select("id_project", project1.name)

    browser.slow_click("span[aria-labelledby='select2-id_application-container']")
    browser.wait_for_element_visible("input.select2-search__field")
    browser.wait_for_element(f"li.select2-results__option:contains('{app1.name}')", timeout=10)
    apps = browser.execute_script(
        "return Array.from(document.querySelectorAll('#select2-id_application-results "
        "li.select2-results__option[role=option]')).map(function(el){return el.textContent.trim();});"
    )
    assert apps == [app1.name]

    browser.click("li.select2-results__option:contains('App One')")
    browser.wait_for_element_absent("input.select2-search__field")

    browser.select2_select("id_project", project2.name)

    app_val = browser.execute_script("return document.getElementById('id_application').value;")
    assert app_val == ""

    browser.select2_select("id_application", app2.name)
    browser.type("input[name=name]", "Test DL")
    browser.click("button[name='_continue']")
    browser.wait_for_ready_state_complete()
    messages = browser.get_admin_messages()
    assert any("added successfully" in m.lower() for m in messages), f"No success message found: {messages}"

    dl: "DistributionList | None" = DistributionList.objects.get(name="Test DL")
    assert dl.project == project2
    assert dl.application == app2
