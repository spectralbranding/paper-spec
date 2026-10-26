"""
validate.py — paper-spec YAML validator

Usage:
    python tools/validate.py examples/zharnikov-2026a-sbt.yaml
    python tools/validate.py examples/

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


# ---------------------------------------------------------------------------
# DOI format: 10.NNNN/anything
# ---------------------------------------------------------------------------
DOI_PATTERN = re.compile(r"^10\.\d{4,}/\S+$")

SPEC_VERSION_PATTERN = re.compile(r"^0\.[12]\.\d+$")

# The vocabularies are read from the JSON Schema, so the schema is their one source.
# Only the standard library is needed for that: callers such as
# spectral-branding's generate_paper_yaml.py run this file in their own venv.
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "paper-spec.schema.json"
ROOT_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
SCHEMA = ROOT_SCHEMA["properties"]


def _enum(section: str, field: str) -> set[str]:
    node = SCHEMA[section]
    prop = node.get("items", node)["properties"][field]
    return set(prop.get("items", prop)["enum"])


CLAIM_TYPES = _enum("claims", "type")
CLAIM_STATUSES = _enum("claims", "status")
EVIDENCE_BASES = _enum("claims", "evidence_basis")
RESULT_STATUSES = _enum("results", "status")
METHODOLOGY_TYPES = _enum("methodology", "type")
DEPENDENCY_RELATIONSHIPS = _enum("dependencies", "relationship")
LIMITATION_SEVERITIES = _enum("limitations", "severity")
SUBMISSION_DECISIONS = _enum("submission_history", "decision")


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
        self.errors.append(ValidationError(path, message))

    # ------------------------------------------------------------------
    # Type helpers
    # ------------------------------------------------------------------

    def _require_str(self, obj: dict, key: str, path: str) -> str | None:
        val = obj.get(key)
        if val is None:
            self.err(path, f"required field '{key}' is missing")
            return None
        if not isinstance(val, str):
            self.err(path, f"'{key}' must be a string, got {type(val).__name__}")
            return None
        if not val.strip():
            self.err(path, f"'{key}' must not be empty")
            return None
        return val

    def _require_list(self, obj: dict, key: str, path: str) -> list | None:
        val = obj.get(key)
        if val is None:
            self.err(path, f"required field '{key}' is missing")
            return None
        if not isinstance(val, list):
            self.err(path, f"'{key}' must be a list, got {type(val).__name__}")
            return None
        return val

    def _opt_bool(self, obj: dict, key: str, path: str) -> None:
        val = obj.get(key)
        if val is not None and not isinstance(val, bool):
            self.err(path, f"'{key}' must be a boolean, got {type(val).__name__}")

    def _opt_enum(self, obj: dict, key: str, allowed: set, path: str) -> None:
        val = obj.get(key)
        if val is not None and val not in allowed:
            self.err(path, f"'{key}' must be one of {sorted(allowed)}, got '{val}'")

    def _req_enum(self, obj: dict, key: str, allowed: set, path: str) -> None:
        if obj.get(key) is None:
            self.err(path, f"required field '{key}' is missing")
        else:
            self._opt_enum(obj, key, allowed, path)

    def _opt_enum_list(self, obj: dict, key: str, allowed: set, path: str) -> None:
        val = obj.get(key)
        if val is None:
            return
        if not isinstance(val, list):
            self.err(path, f"'{key}' must be a list")
            return
        for item in val:
            if item not in allowed:
                self.err(
                    path,
                    f"'{key}' entries must be one of {sorted(allowed)}, got '{item}'",
                )
        if len(set(map(str, val))) != len(val):
            self.err(path, f"'{key}' must not repeat a value")

    def _valid_doi(self, doi: str) -> bool:
        return bool(DOI_PATTERN.match(doi))

    # ------------------------------------------------------------------
    # Section validators
    # ------------------------------------------------------------------

    def validate_keys(self, node: dict, value: object, path: str) -> None:
        """Report keys the schema does not define, wherever it sets additionalProperties false."""
        if isinstance(value, dict) and "properties" in node:
            props = node["properties"]
            for key, item in value.items():
                if key in props:
                    self.validate_keys(
                        props[key], item, f"{path}.{key}" if path else key
                    )
                elif node.get("additionalProperties") is False:
                    self.err(path or "(root)", f"unknown field '{key}'")
        elif isinstance(value, list) and "items" in node:
            for i, item in enumerate(value):
                self.validate_keys(node["items"], item, f"{path}[{i}]")

    def validate_spec_version(self) -> None:
        version = self.data.get("spec_version")
        if version is None:
            self.err("spec_version", "required field 'spec_version' is missing")
            return
        if not isinstance(version, str) or not SPEC_VERSION_PATTERN.match(version):
            self.err(
                "spec_version",
                f"'spec_version' must be a 0.1.x or 0.2.x version, got '{version}'",
            )

    def validate_meta(self) -> None:
        path = "meta"
        meta = self.data.get("meta")
        if meta is None:
            self.err(path, "required section 'meta' is missing")
            return
        if not isinstance(meta, dict):
            self.err(path, "'meta' must be a mapping")
            return

        self._require_str(meta, "title", path)

        authors = self._require_list(meta, "authors", path)
        if authors is not None and len(authors) == 0:
            self.err(path, "'authors' list must not be empty")
        for i, author in enumerate(authors or []):
            if not isinstance(author, dict):
                self.err(f"{path}.authors[{i}]", "each author must be a mapping")
            else:
                self._require_str(author, "name", f"{path}.authors[{i}]")

        doi = meta.get("doi")
        if doi is not None:
            if not isinstance(doi, str):
                self.err(path, "'doi' must be a string")
            elif not self._valid_doi(doi):
                self.err(
                    path, f"'doi' does not match DOI format (10.NNNN/...): '{doi}'"
                )

    def validate_claims(self) -> set[str]:
        """Returns the set of valid claim IDs."""
        valid_ids: set[str] = set()
        claims = self.data.get("claims")
        if claims is None:
            return valid_ids
        if not isinstance(claims, list):
            self.err("claims", "'claims' must be a list")
            return valid_ids

        seen_ids: set[str] = set()
        for i, claim in enumerate(claims):
            path = f"claims[{i}]"
            if not isinstance(claim, dict):
                self.err(path, "each claim must be a mapping")
                continue

            cid = self._require_str(claim, "id", path)
            if cid is not None:
                if cid in seen_ids:
                    self.err(path, f"duplicate claim id '{cid}'")
                else:
                    seen_ids.add(cid)
                    valid_ids.add(cid)

            self._require_str(claim, "statement", path)
            self._req_enum(claim, "type", CLAIM_TYPES, path)
            self._opt_bool(claim, "testable", path)
            self._opt_bool(claim, "tested_in_paper", path)
            self._opt_enum(claim, "status", CLAIM_STATUSES, path)
            self._opt_enum_list(claim, "evidence_basis", EVIDENCE_BASES, path)

            depends_on = claim.get("depends_on")
            if depends_on is not None:
                if not isinstance(depends_on, list):
                    self.err(path, "'depends_on' must be a list")

        return valid_ids

    def validate_methodology(self) -> None:
        meth = self.data.get("methodology")
        if meth is None:
            return
        path = "methodology"
        if not isinstance(meth, dict):
            self.err(path, "'methodology' must be a mapping")
            return
        self._req_enum(meth, "type", METHODOLOGY_TYPES, path)
        self._opt_enum_list(meth, "secondary_types", METHODOLOGY_TYPES, path)

    def validate_acceptance(self, valid_claim_ids: set[str]) -> None:
        acceptance = self.data.get("acceptance")
        if acceptance is None:
            return
        if not isinstance(acceptance, list):
            self.err("acceptance", "'acceptance' must be a list")
            return
        for i, ac in enumerate(acceptance):
            path = f"acceptance[{i}]"
            if not isinstance(ac, dict):
                self.err(path, "each acceptance criterion must be a mapping")
                continue
            cid = self._require_str(ac, "claim_id", path)
            if cid is not None and valid_claim_ids and cid not in valid_claim_ids:
                self.err(
                    path, f"'claim_id' '{cid}' does not reference a known claim id"
                )
            if ac.get("criterion") is None and ac.get("falsification") is None:
                self.err(path, "needs 'criterion', 'falsification' or both")
            for key in ("criterion", "falsification"):
                if ac.get(key) is not None:
                    self._require_str(ac, key, path)

    def validate_dependencies(self) -> set[str]:
        """Returns the set of dependency DOIs declared."""
        dep_dois: set[str] = set()
        deps = self.data.get("dependencies")
        if deps is None:
            return dep_dois
        if not isinstance(deps, list):
            self.err("dependencies", "'dependencies' must be a list")
            return dep_dois
        for i, dep in enumerate(deps):
            path = f"dependencies[{i}]"
            if not isinstance(dep, dict):
                self.err(path, "each dependency must be a mapping")
                continue
            doi = dep.get("doi")
            ref = dep.get("reference")
            if doi is not None and isinstance(doi, str) and doi.strip():
                if not self._valid_doi(doi):
                    self.err(
                        path, f"'doi' does not match DOI format (10.NNNN/...): '{doi}'"
                    )
                else:
                    dep_dois.add(doi)
            elif ref is not None and isinstance(ref, str) and ref.strip():
                pass  # reference string is acceptable for works without DOIs
            else:
                self.err(path, "each dependency must have either 'doi' or 'reference'")
            self._opt_enum(dep, "relationship", DEPENDENCY_RELATIONSHIPS, path)
            self._opt_bool(dep, "critical", path)
        return dep_dois

    def validate_contradictions(self) -> None:
        contras = self.data.get("contradictions")
        if contras is None:
            return
        if not isinstance(contras, list):
            self.err("contradictions", "'contradictions' must be a list")
            return
        for i, c in enumerate(contras):
            path = f"contradictions[{i}]"
            if not isinstance(c, dict):
                self.err(path, "each contradiction must be a mapping")
                continue
            doi = c.get("doi")
            ref = c.get("reference")
            if doi is not None and isinstance(doi, str) and doi.strip():
                if not self._valid_doi(doi):
                    self.err(
                        path, f"'doi' does not match DOI format (10.NNNN/...): '{doi}'"
                    )
            elif ref is not None and isinstance(ref, str) and ref.strip():
                pass  # reference string acceptable for works without DOIs
            else:
                self.err(
                    path, "each contradiction must have either 'doi' or 'reference'"
                )
            self._require_str(c, "claim", path)
            self._require_str(c, "our_position", path)

    def validate_results(self, valid_claim_ids: set[str]) -> None:
        results = self.data.get("results")
        if results is None:
            return
        if not isinstance(results, list):
            self.err("results", "'results' must be a list")
            return
        for i, result in enumerate(results):
            path = f"results[{i}]"
            if not isinstance(result, dict):
                self.err(path, "each result must be a mapping")
                continue
            cid = self._require_str(result, "claim_id", path)
            if cid is not None and valid_claim_ids and cid not in valid_claim_ids:
                self.err(
                    path, f"'claim_id' '{cid}' does not reference a known claim id"
                )
            self._req_enum(result, "status", RESULT_STATUSES, path)

    def validate_limitations(self) -> None:
        limitations = self.data.get("limitations")
        if limitations is None:
            return
        if not isinstance(limitations, list):
            self.err("limitations", "'limitations' must be a list")
            return
        for i, lim in enumerate(limitations):
            path = f"limitations[{i}]"
            if not isinstance(lim, dict):
                self.err(path, "each limitation must be a mapping")
                continue
            self._require_str(lim, "description", path)
            self._opt_enum(lim, "severity", LIMITATION_SEVERITIES, path)
            self._opt_bool(lim, "addressable", path)

    def validate_data_section(self) -> None:
        data = self.data.get("data")
        if data is None:
            return
        path = "data"
        if not isinstance(data, dict):
            self.err(path, "'data' must be a mapping")
            return
        if data.get("available") is None:
            self.err(path, "required field 'available' is missing")
        self._opt_bool(data, "available", path)

    def validate_code_section(self) -> None:
        code = self.data.get("code")
        if code is None:
            return
        path = "code"
        if not isinstance(code, dict):
            self.err(path, "'code' must be a mapping")
            return
        if code.get("available") is None:
            self.err(path, "required field 'available' is missing")
        self._opt_bool(code, "available", path)

    def validate_replication(self) -> None:
        rep = self.data.get("replication")
        if rep is None:
            return
        path = "replication"
        if not isinstance(rep, dict):
            self.err(path, "'replication' must be a mapping")
            return
        self._opt_bool(rep, "feasible", path)

    def validate_repositories(self) -> None:
        repos = self.data.get("repositories")
        if repos is None:
            return
        if not isinstance(repos, list):
            self.err("repositories", "'repositories' must be a list")
            return
        for i, repo in enumerate(repos):
            path = f"repositories[{i}]"
            if not isinstance(repo, dict):
                self.err(path, "each repository entry must be a mapping")
                continue
            self._require_str(repo, "platform", path)
            self._require_str(repo, "url", path)
            doi = repo.get("doi")
            if doi is not None:
                if not isinstance(doi, str):
                    self.err(path, "'doi' must be a string")
                elif not self._valid_doi(doi):
                    self.err(
                        path, f"'doi' does not match DOI format (10.NNNN/...): '{doi}'"
                    )

    def validate_submission_history(self) -> None:
        history = self.data.get("submission_history")
        if history is None:
            return
        if not isinstance(history, list):
            self.err("submission_history", "'submission_history' must be a list")
            return
        for i, entry in enumerate(history):
            path = f"submission_history[{i}]"
            if not isinstance(entry, dict):
                self.err(path, "each submission_history entry must be a mapping")
                continue
            self._require_str(entry, "venue", path)
            self._require_str(entry, "date_submitted", path)
            self._opt_enum(entry, "decision", SUBMISSION_DECISIONS, path)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        self.validate_keys(ROOT_SCHEMA, self.data, "")
        self.validate_spec_version()
        self.validate_meta()
        valid_claim_ids = self.validate_claims()
        self.validate_methodology()
        self.validate_acceptance(valid_claim_ids)
        self.validate_dependencies()
        self.validate_contradictions()
        self.validate_results(valid_claim_ids)
        self.validate_limitations()
        self.validate_data_section()
        self.validate_code_section()
        self.validate_replication()
        self.validate_repositories()
        self.validate_submission_history()
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
