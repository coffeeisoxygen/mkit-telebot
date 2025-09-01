import re
from typing import Any


def mask_message(msg: str, mask_regex: dict[str, str], mask_value: str) -> str:
    """Mask sensitive patterns in log message."""
    for pattern in mask_regex.values():
        msg = re.sub(pattern, mask_value, msg)
    return msg


def mask_extra(
    extra: dict[str, Any],
    mask_fields: list,
    mask_regex: dict[str, str],
    mask_value: str,
) -> dict[str, Any]:
    """Mask sensitive fields and patterns in extra dict, including nested dicts."""
    for field in mask_fields:
        if field in extra:
            extra[field] = mask_value
    for key, value in extra.items():
        if key not in mask_fields:
            if isinstance(value, dict):
                extra[key] = mask_extra(value, mask_fields, mask_regex, mask_value)
            elif isinstance(value, str):
                for pattern in mask_regex.values():
                    extra[key] = re.sub(pattern, mask_value, value)
    return extra


def masking_patcher(record: Any, masking: dict[str, Any]) -> None:
    """Apply masking to log record based on config."""
    if masking.get("enabled"):
        mask_value = masking.get("default_mask", "***")
        mask_fields = masking.get("mask_fields", [])
        mask_regex = masking.get("mask_regex", {})
        if masking.get("mask_message", True):
            record["message"] = mask_message(record["message"], mask_regex, mask_value)
        if masking.get("mask_extra", True):
            record["extra"] = mask_extra(
                record["extra"], mask_fields, mask_regex, mask_value
            )


def extra_patcher(record: dict, default_extra: dict) -> None:
    """Override extra: tampilkan default jika tidak ada bind, hapus default jika ada bind."""
    extra = record["extra"]
    # Jika log pakai bind (ada extra selain default), hapus default
    if extra and any(k not in default_extra for k in extra):
        for k in list(default_extra.keys()):
            extra.pop(k, None)
    # Jika tidak ada extra dari bind, pastikan default tetap ada
    else:
        for k, v in default_extra.items():
            extra.setdefault(k, v)
