from __future__ import annotations

import re
from typing import Any


_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_\.\-]+)\s*\}\}")


def _lookup(context: dict[str, Any], path: str) -> Any:
    current: Any = context
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def interpolate(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        matches = list(_PATTERN.finditer(value))
        if len(matches) == 1 and matches[0].group(0) == value.strip():
            looked = _lookup(context, matches[0].group(1))
            return looked
        return _PATTERN.sub(lambda m: str(_lookup(context, m.group(1)) or ""), value)
    if isinstance(value, dict):
        return {k: interpolate(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [interpolate(v, context) for v in value]
    return value


def apply_mapping(mapping: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if not mapping:
        return {}
    return interpolate(mapping, context)
