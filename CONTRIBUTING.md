# Contributing to paper-spec

Thank you for contributing. This document covers how to add a paper, propose spec changes, and follow style conventions.

---

## Adding your own paper.yaml

1. Fork this repository on GitHub.

2. Create a new file in `examples/` named after your paper:

   ```
   examples/surname-YYYY-short-slug.yaml
   ```

   Convention: lowercase, hyphens only, no spaces. Example: `green-2024-signaling-theory.yaml`

3. Write your spec. Use `examples/zharnikov-2026a-sbt.yaml` as a reference. Every `paper.yaml` must have a `meta` section with at least `title`, `authors`, and `date`.

4. Validate your file before opening a pull request:

   ```
   python tools/validate.py examples/surname-YYYY-short-slug.yaml
   ```

   The validator must exit with code 0 (no errors).

5. Open a pull request with the title `add: surname-YYYY-short-slug`. Include a one-sentence description of the paper in the PR body.

---

## Suggesting spec changes

The spec evolves conservatively. Changes to field names or required fields can break existing files, so they require discussion first.

To propose a change:

1. Open a GitHub issue.
2. Apply the label `spec-change`.
3. Describe:
   - What field or section you want to add, modify, or remove.
   - Why it is needed (cite a concrete use case, not a hypothetical).
   - Whether it is backward compatible (additive changes preferred).

Breaking changes (removing required fields, renaming keys, changing enum values) require at least two maintainer approvals and a migration note in `CHANGELOG.md`.

---

## Style guidelines

**YAML formatting**

- 2-space indentation throughout.
- Use double-quoted strings for values that contain colons, special characters, or are long enough to risk ambiguity.
- Use block scalars (`|` or `>`) for multi-sentence fields such as `statement`, `abstract`, and `criterion`.
- Do not include trailing whitespace or a trailing newline after the final field.

**Claim IDs**

- Short, uppercase, and stable across revisions. Examples: `H1`, `H2`, `P1`, `T3`, `C2`.
- Use a letter prefix that reflects the type:
  - `H` for hypothesis
  - `P` for proposition
  - `T` for theorem
  - `C` for conjecture
  - `D` for definition
- Never reuse an ID within the same file. If a claim is removed, retire its ID rather than reassigning it.

**DOIs**

- Always use the canonical DOI format: `10.NNNN/suffix`. Do not prefix with `https://doi.org/`.
- Verify DOIs resolve before committing. A broken DOI in a dependency fails validation.

**Dates**

- Use ISO 8601: `YYYY-MM-DD` for published papers, `YYYY` for preprints where only the year is known.

**Authors**

- List in citation order (as the paper lists them), not alphabetical.
- Use full names as they appear on the paper, not shortened forms.

---

## Code of conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) (version 2.1). By participating you agree to abide by its terms. Report violations to the maintainers via GitHub private message or the email in `meta/contact` if present.
