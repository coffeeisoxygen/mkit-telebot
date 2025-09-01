from app.custom.exception.base_exc import AppExceptionError


def test_default_initialization():
    exc = AppExceptionError()
    assert exc.message == exc.default_message
    assert exc.name == "ApplicationError"
    assert exc.status_code is None
    assert exc.context == {}
    assert exc.__cause__ is None
    assert str(exc) == exc.default_message


def test_custom_message_and_name():
    exc = AppExceptionError(message="Custom error", name="CustomError")
    assert exc.message == "Custom error"
    assert exc.name == "CustomError"
    assert str(exc) == "Custom error"


def test_context_and_cause():
    cause = ValueError("bad value")
    context = {"foo": "bar"}
    exc = AppExceptionError(message="Has cause", context=context, cause=cause)
    assert exc.context == context
    assert exc.__cause__ == cause
    assert "caused by ValueError: bad value" in str(exc)


def test_to_dict_with_cause():
    cause = RuntimeError("fail")
    exc = AppExceptionError(message="With cause", cause=cause)
    d = exc.to_dict()
    assert d["name"] == "ApplicationError"
    assert d["message"] == "With cause"
    assert d["status_code"] is None
    assert d["cause"] == "fail"


def test_repr():
    exc = AppExceptionError(message="Repr test")
    r = repr(exc)
    assert "<AppExceptionError" in r
    assert "message='Repr test'" in r
    assert "Repr test" in r
