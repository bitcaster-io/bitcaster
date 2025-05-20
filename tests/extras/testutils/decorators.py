import os

import pytest
from _pytest.mark.structures import MarkDecorator


def requires_env(*envs: str) -> MarkDecorator:
    missing = [env for env in envs if os.environ.get(env, None) is None]

    return pytest.mark.skipif(len(missing) > 0, reason=f"Not suitable environment {missing} for current test")
