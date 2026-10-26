"""The examples, the JSON Schema and tools/validate.py agree.

Every example must pass both validators, and both must give the same verdict on the
v0.2.0 rules, so the schema and the bundled validator cannot drift apart again.
"""

import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "paper-spec.schema.json").read_text())
EXAMPLES = sorted((ROOT / "examples").glob("*.yaml"))

_spec = importlib.util.spec_from_file_location(
    "validate", ROOT / "tools" / "validate.py"
)
assert _spec and _spec.loader
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)

MINIMAL = {
    "spec_version": "0.2.0",
    "meta": {"title": "T", "authors": [{"name": "Doe, Jane"}]},
    "claims": [
        {"id": "P1", "type": "proposition", "statement": "S", "status": "not_tested"}
    ],
}


def verdicts(doc: dict) -> tuple[bool, bool]:
    """(schema accepts, validate.py accepts)."""
    schema_ok = jsonschema.Draft202012Validator(SCHEMA).is_valid(doc)
    return schema_ok, validate.Validator(doc, "test").validate()


def test_schema_is_valid_draft_2020_12() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_passes_both_validators(path: Path) -> None:
    doc = yaml.safe_load(path.read_text())
    errors = [
        e.message for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(doc)
    ]
    assert errors == []
    validator = validate.Validator(doc, str(path))
    assert validator.validate(), [str(e) for e in validator.errors]


def test_a_v010_file_stays_valid() -> None:
    doc = copy.deepcopy(MINIMAL)
    doc["spec_version"] = "0.1.0"
    assert verdicts(doc) == (True, True)


def edited(path: str, value: object) -> dict:
    """MINIMAL with one change; path is dotted, list items as integers."""
    doc = copy.deepcopy(MINIMAL)
    *parents, last = [int(k) if k.isdigit() else k for k in path.split(".")]
    node = doc
    for key in parents:
        node = node[key]
    if value is DELETE:
        del node[last]
    else:
        node[last] = value
    return doc


DELETE = object()


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        ("claims.0.status", "proposed", False),
        ("claims.0.type", "corollary", True),
        ("claims.0.type", DELETE, False),
        ("claims.0.evidence_basis", ["deductive", "computational"], True),
        ("claims.0.evidence_basis", ["simulation"], False),
        ("claims.0.falsification", "F", False),
        ("spec_version", DELETE, False),
        ("spec_version", "1.0.0", False),
        ("meta.authors", ["Doe, Jane"], False),
        ("meta.superseded_by", "10.5281/zenodo.1", True),
        ("acceptance", [{"claim_id": "P1", "falsification": "F"}], True),
        ("acceptance", [{"claim_id": "P1"}], False),
        (
            "methodology",
            {"type": "conceptual", "secondary_types": ["computational"]},
            True,
        ),
        ("methodology", {"type": "theoretical_synthesis"}, False),
        (
            "dependencies",
            [{"reference": "R", "relationship": "cites_as_related"}],
            True,
        ),
        ("dependencies", [{"reference": "R", "relationship": "contextualizes"}], False),
        ("submission_history", [{"venue": "V", "date_submitted": "2026-03"}], True),
        (
            "submission_history",
            [{"venue": "V", "date_submitted": "2026", "decision": "rejected"}],
            False,
        ),
        ("data", {"available": False, "notes": "IRB"}, True),
        ("data", {"notes": "IRB"}, False),
    ],
)
def test_both_validators_give_the_same_verdict(
    path: str, value: object, expected: bool
) -> None:
    assert verdicts(edited(path, value)) == (expected, expected)
