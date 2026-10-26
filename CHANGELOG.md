# Changelog

Changes to the Paper Spec standard, its JSON Schema, tools and examples. The normative list of
specification changes is the Version history section of [SPECIFICATION.md](SPECIFICATION.md).

## 0.2.0 (2026-10-26)

- Specification: new claim types `lemma` and `corollary`, methodology type `conceptual`,
  dependency relationships `cites`, `obtains_background_from` and `cites_as_related` (mapped
  to CiTO 2.9.0), and optional `claims[].evidence_basis` (ECO evidence classes),
  `methodology.secondary_types`, notes fields and `meta.superseded_by`. Acceptance entries
  need a criterion or a falsification condition. Every v0.1.0 file stays valid.
- Schema: matches the specification text; it previously rejected `spec_version` and author
  objects, so no conforming file passed it.
- `tools/validate.py`: applies the schema's rules itself (needs only PyYAML), reports unknown
  fields, accepts several paths; `tools/template.py` and the generation prompt use the 0.2.0
  vocabulary.
- `tests/`: every example against both validators, the two validators against each other, and
  the specification's enum tables against the schema. `reproduce.sh` fails when an example
  does not validate.
- Examples: 13 files migrated to 0.2.0 vocabulary and field names.

## 0.1.0 (2026-03-25)

- First release.
