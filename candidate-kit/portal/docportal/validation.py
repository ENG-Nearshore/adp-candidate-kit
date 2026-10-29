"""Validates engine output against the JSON schemas in contract/.

Supports the subset of JSON Schema the contract uses: type, const, enum,
required, properties, additionalProperties (false), items, minItems,
minLength, minimum.
"""

import json
from pathlib import Path

CONTRACT_DIR = Path(__file__).resolve().parent.parent / "contract"

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
}


def load_schema(name: str) -> dict:
    return json.loads((CONTRACT_DIR / name).read_text(encoding="utf-8"))


def validate(value, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        python_type = _TYPES[expected]
        is_bool = isinstance(value, bool)
        if not isinstance(value, python_type) or (is_bool and expected in ("number", "integer")):
            return [f"{path}: expected {expected}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{path}: must not be empty")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema:
        if value < schema["minimum"]:
            errors.append(f"{path}: must be >= {schema['minimum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing '{key}'")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors.extend(validate(item, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property '{key}'")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate(item, schema["items"], f"{path}[{index}]"))
    return errors
