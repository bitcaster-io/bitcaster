from django_webtest import DjangoWebtestResponse


def assert_form_error(response: DjangoWebtestResponse, field: str, error: str) -> None:
    target = response.context["adminform"].form
    assert field in target.errors, f"No errors found for field {field}"
    assert error in target.errors[field], f"Error message '{error} not found for field '{field}'"
