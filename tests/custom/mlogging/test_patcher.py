from app.custom.mlogging.patcher import (
    extra_patcher,
    mask_extra,
    mask_message,
    masking_patcher,
)


def test_mask_message_basic():
    msg = "password=1234; token=abcd"
    mask_regex = {"pw": r"password=\w+", "tk": r"token=\w+"}
    masked = mask_message(msg, mask_regex, "[MASKED]")
    assert "password=" not in masked
    assert "token=" not in masked
    assert "[MASKED]" in masked


def test_mask_message_no_match():
    msg = "no sensitive info"
    mask_regex = {"pw": r"password=\w+"}
    masked = mask_message(msg, mask_regex, "XXX")
    assert masked == msg


def test_mask_extra_flat():
    extra = {"password": "1234", "token": "abcd", "user": "alice"}
    mask_fields = ["password"]
    mask_regex = {"tk": r"abcd"}
    masked = mask_extra(extra.copy(), mask_fields, mask_regex, "XXX")
    assert masked["password"] == "XXX"
    assert masked["token"] == "XXX"
    assert masked["user"] == "alice"


def test_mask_extra_nested():
    extra = {
        "user": "bob",
        "details": {"token": "abcd", "password": "1234"},
        "info": "secret=xyz",
    }
    mask_fields = ["password"]
    mask_regex = {"secret": r"secret=\w+"}
    masked = mask_extra(extra.copy(), mask_fields, mask_regex, "MASK")
    assert masked["details"]["password"] == "MASK"
    assert masked["details"]["token"] == "abcd"
    assert masked["info"] == "MASK"


def test_masking_patcher_message_and_extra():
    record = {
        "message": "api_key=12345",
        "extra": {"api_key": "12345", "other": "data"},
    }
    masking = {
        "enabled": True,
        "default_mask": "XXX",
        "mask_fields": ["api_key"],
        "mask_regex": {"key": r"api_key=\w+"},
        "mask_message": True,
        "mask_extra": True,
    }
    masking_patcher(record, masking)
    assert record["message"] == "XXX"
    assert record["extra"]["api_key"] == "XXX"


def test_masking_patcher_disabled():
    record = {"message": "api_key=12345", "extra": {"api_key": "12345"}}
    masking = {"enabled": False}
    masking_patcher(record, masking)
    assert record["message"] == "api_key=12345"
    assert record["extra"]["api_key"] == "12345"


def test_extra_patcher_with_bind():
    record = {"extra": {"foo": "bar", "default1": "val1"}}
    default_extra = {"default1": "val1", "default2": "val2"}
    extra_patcher(record, default_extra)
    assert "default1" not in record["extra"]
    assert "default2" not in record["extra"]
    assert "foo" in record["extra"]


def test_extra_patcher_without_bind():
    record = {"extra": {}}
    default_extra = {"default1": "val1", "default2": "val2"}
    extra_patcher(record, default_extra)
    assert record["extra"]["default1"] == "val1"
    assert record["extra"]["default2"] == "val2"
