from bitcaster.config import SmartEnv


def test_env():
    e = SmartEnv(
        **{
            "T1": (str, "a@b.com"),
            "T2": (str, "a@b.com", "help"),
            "T3": (str, "a@b.com", "help", "dev@b.com"),
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
