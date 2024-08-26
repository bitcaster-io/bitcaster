import os
from unittest import mock

import pytest

from bitcaster.config import SmartEnv


@pytest.fixture()
def env() -> SmartEnv:
    return SmartEnv(STORAGE_DEFAULT=(str, ""))


@pytest.mark.parametrize(
    "storage",
    [
        "storage.SampleStorage?bucket=container&option=value&connection_string=Defaul",
        "storage.SampleStorage?bucket=container&option=value&connection_string=DefaultEndpointsProtocol=http;Account"
        "Name=devstoreaccount1;AccountKey=ke1==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;",
    ],
)
def test_storage_options(storage: str, env: SmartEnv) -> None:
    with mock.patch.dict(os.environ, {"STORAGE_DEFAULT": storage}, clear=True):
        ret = env.storage("STORAGE_DEFAULT")

    assert ret["BACKEND"] == "storage.SampleStorage"  # type: ignore[index]
    assert sorted(ret["OPTIONS"].keys()) == ["bucket", "connection_string", "option"]  # type: ignore[union-attr,index]


@pytest.mark.parametrize("storage", ["storage.SampleStorage"])
def test_storage(storage: str, env: SmartEnv) -> None:
    with mock.patch.dict(os.environ, {"STORAGE_DEFAULT": storage}, clear=True):
        ret = env.storage("STORAGE_DEFAULT")

    assert ret["BACKEND"] == "storage.SampleStorage"  # type: ignore[index]


def test_storage_empty(env: SmartEnv) -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        assert not env.storage("STORAGE_DEFAULT")


def test_env() -> None:
    e = SmartEnv(
        **{
            "T1": (str, "a@b.com"),  # type: ignore
            "T2": (str, "a@b.com", "help"),
            "T3": (str, "a@b.com", "help", "dev@b.com"),
            "T4": (int, None),
        }
    )

    assert e("T1") == "a@b.com"
    assert e.get_help("T1") == ""
    assert e.for_develop("T1") == "a@b.com"
    assert e.get_default("T1") == "a@b.com"

    assert e("T2") == "a@b.com"
    assert e.get_help("T2") == "help"
    assert e.for_develop("T2") == "a@b.com"
    assert e.get_default("T2") == "a@b.com"

    assert e("T3") == "a@b.com"
    assert e.get_help("T3") == "help"
    assert e.for_develop("T3") == "dev@b.com"
    assert e.get_default("T3") == "a@b.com"

    assert e.get_default("cc") == ""

    with pytest.raises(TypeError):
        assert e.get_default("T4")
