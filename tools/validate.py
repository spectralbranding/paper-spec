"""
validate.py — paper-spec YAML validator

Usage:
    python tools/validate.py examples/zharnikov-2026a-sbt.yaml
    python tools/validate.py examples/ more-papers/

Checks each file against schema/paper-spec.schema.json (required fields, types, enums,
patterns, unknown fields), then adds checks a schema cannot express: claim ids are unique,
acceptance and result entries name a known claim, and required strings are not blank.
Needs only PyYAML: the schema is read with the standard library, so the validator also runs
in environments that do not install jsonschema.

Exit code 0 if all files valid, 1 if any errors found.
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: uv add pyyaml")
    sys.exit(1)


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "paper-spec.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

# The JSON Schema keywords this validator implements. tests/test_validation.py fails if
# the schema starts using one that is not listed here.
IMPLEMENTED_KEYWORDS = {
    "additionalProperties",
    "anyOf",
    "enum",
    "items",
    "minItems",
    "pattern",
    "properties",
    "required",
    "type",
    "uniqueItems",
}
ANNOTATIONS = {"$id", "$schema", "deprecated", "description", "title"}

TYPE_NAMES = {
    "string": "a string",
    "integer": "an integer",
    "number": "a number",
    "boolean": "a boolean",
    "array": "a list",
    "object": "a mapping",
}


def _is_type(value: object, name: str) -> bool:
    """JSON Schema type test; booleans are not integers or numbers."""
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    expected = {"string": str, "boolean": bool, "array": list, "object": dict}
    return isinstance(value, expected[name])


class ValidationError:
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message

    def __str__(self) -> str:
        return f"  [{self.path}] {self.message}"


class Validator:
    def __init__(self, data: dict, source: str):
        self.data = data
        self.source = source
        self.errors: list[ValidationError] = []

    def err(self, path: str, message: str) -> None:
        self.errors.append(ValidationError(path or "(root)", message))

    # ------------------------------------------------------------------
    # Structure: the schema keywords in IMPLEMENTED_KEYWORDS
    # ------------------------------------------------------------------

    def _passes(self, node: dict, value: object) -> bool:
        probe = Validator(self.data, self.source)
        probe.check(node, value, "")
        return not probe.errors

    def check(self, node: dict, value: object, path: str) -> None:
        """Check value against one schema node and recurse into its children."""
        if "anyOf" in node and not any(self._passes(b, value) for b in node["anyOf"]):
            keys = [k for b in node["anyOf"] for k in b.get("required", [])]
            if keys and all(set(b) == {"required"} for b in node["anyOf"]):
                self.err(path, f"needs at least one of {', '.join(map(repr, keys))}")
            else:
                self.err(path, "does not match any allowed form")
        if "type" in node:
            names = node["type"] if isinstance(node["type"], list) else [node["type"]]
            if not any(_is_type(value, n) for n in names):
                wanted = " or ".join(TYPE_NAMES[n] for n in names)
                self.err(path, f"must be {wanted}, got {type(value).__name__}")
                return
        if "enum" in node and value not in node["enum"]:
            self.err(path, f"must be one of {sorted(node['enum'])}, got {value!r}")
        if "pattern" in node and isinstance(value, str):
            if not re.search(node["pattern"], value):
                self.err(
                    path, f"{value!r} does not match the pattern {node['pattern']}"
                )
        if isinstance(value, dict):
            self._check_mapping(node, value, path)
        if isinstance(value, list) and "items" in node:
            if len(value) < node.get("minItems", 0):
                self.err(path, f"must have at least {node['minItems']} item(s)")
            if node.get("uniqueItems"):
                seen = [json.dumps(v, sort_keys=True, default=str) for v in value]
                if len(set(seen)) != len(seen):
                    self.err(path, "must not repeat a value")
            for i, item in enumerate(value):
                self.check(node["items"], item, f"{path}[{i}]")

    def _check_mapping(self, node: dict, value: dict, path: str) -> None:
        props = node.get("properties", {})
        for key in node.get("required", []):
            if key not in value or value[key] is None:
                self.err(path, f"required field '{key}' is missing")
            elif isinstance(value[key], str) and not value[key].strip():
                self.err(path, f"'{key}' must not be empty")
        for key, item in value.items():
            if key in props:
                if item is None and key in node.get("required", []):
                    continue  # reported as missing above
                self.check(props[key], item, f"{path}.{key}" if path else key)
            elif node.get("additionalProperties") is False:
                self.err(path, f"unknown field '{key}'")

    # ------------------------------------------------------------------
    # Meaning: what the schema cannot express
    # ------------------------------------------------------------------

    def check_claim_references(self) -> None:
        """Claim ids are unique; acceptance and results entries name a known claim."""
        claims = self.data.get("claims")
        ids: set[str] = set()
        for i, claim in enumerate(claims if isinstance(claims, list) else []):
            cid = claim.get("id") if isinstance(claim, dict) else None
            if isinstance(cid, str):
                if cid in ids:
                    self.err(f"claims[{i}]", f"duplicate claim id '{cid}'")
                ids.add(cid)
        if not ids:
            return
        for section in ("acceptance", "results"):
            entries = self.data.get(section)
            for i, entry in enumerate(entries if isinstance(entries, list) else []):
                cid = entry.get("claim_id") if isinstance(entry, dict) else None
                if isinstance(cid, str) and cid not in ids:
                    self.err(
                        f"{section}[{i}]",
                        f"'claim_id' '{cid}' does not reference a known claim id",
                    )

    def validate(self) -> bool:
        self.check(SCHEMA, self.data, "")
        self.check_claim_references()
        return len(self.errors) == 0


# ---------------------------------------------------------------------------
# File-level runner
# ---------------------------------------------------------------------------


def validate_file(path: Path) -> bool:
    print(f"Validating: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  ERROR: Cannot read file — {exc}")
        return False

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        print(f"  ERROR: YAML parse error — {exc}")
        return False

    if not isinstance(data, dict):
        print("  ERROR: Top-level document must be a YAML mapping")
        return False

    validator = Validator(data, str(path))
    ok = validator.validate()

    if ok:
        print("  PASS")
    else:
        print(f"  FAIL ({len(validator.errors)} error(s)):")
        for err in validator.errors:
            print(str(err))

    return ok


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/validate.py <file.yaml|directory> [...]")
        return 1

    files: list[Path] = []
    for arg in sys.argv[1:]:
        target = Path(arg)
        if target.is_dir():
            found = sorted(target.glob("*.yaml"))
            if not found:
                print(f"No .yaml files found in {target}")
                return 1
            files.extend(found)
        elif target.is_file():
            files.append(target)
        else:
            print(f"ERROR: Path not found: {target}")
            return 1

    results = [validate_file(f) for f in files]

    total = len(results)
    passed = sum(results)
    failed = total - passed

    if total > 1:
        print(f"\nSummary: {passed}/{total} passed, {failed} failed")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
