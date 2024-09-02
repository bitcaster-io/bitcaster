# Run tests

Bitcaster uses [pytest](https://pypi.org/project/pytest/) as testing framework.
Please refers to its [official documentation](https://docs.pytest.org/en/stable/) for more detailed information.

!!! warning

    Test suite requires DIANGO_SETTINGS_MODULE is not set in the enviroment during the tests.
    Uses 

         `DJANGO_SETTINGS_MODULE='' pytest tests/` # (or any other test command)
    
    if you have it set 

## Run full test suite

    pytest tests

## Run coverage and inspect results

[pytest-cov](https://pypi.org/project/pytest-cov/) configuration is `tests/.coveragerc`

    pytest tests/ --create-db -vv --cov
    open ./~build/coverage/index.html

## Using multiple CPUs

[pytest-xdist](https://pypi.org/project/pytest-xdist/) plugin is available for distributed tests

    pytest tests/ tests/ -n auto
