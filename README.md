# Paper Spec

A machine-readable specification format for scientific papers.

## The Problem

Scientific knowledge is locked inside unstructured PDFs. A paper's claims, methods, acceptance criteria, data locations, and dependencies are all expressed in natural language, scattered across sections, and formatted differently in every journal.

This means:

- **Verification does not scale.** Checking whether a paper's claims are actually tested requires reading the whole thing.
- **Dependency tracking is manual.** When a foundational paper is retracted, there is no systematic way to find everything that depends on it.
- **Replication is guesswork.** Figuring out what you need to reproduce a study means excavating details from Methods sections written for reviewers, not replicators.
- **Meta-analysis is expensive.** Extracting structured data from papers is still largely done by hand.

## The Solution

Paper Spec defines `paper.yaml` -- a structured companion file that lives alongside a paper. It makes the paper's core epistemic content machine-readable: what it claims, how those claims were tested, what would falsify them, and what the paper depends on.

A `paper.yaml` does not replace the paper. It indexes it.

## Quick Example

A minimal `paper.yaml`:

```yaml
spec_version: "0.1.0"

meta:
  title: "The Effect of Sleep Deprivation on Decision Quality"
  authors:
    - name: "Chen, Wei"
      orcid: "0000-0002-1234-5678"
  date: "2026-03-15"
  venue: "Journal of Experimental Psychology"
```

A more complete one:

```yaml
spec_version: "0.1.0"

meta:
  title: "The Effect of Sleep Deprivation on Decision Quality"
  authors:
    - name: "Chen, Wei"
      orcid: "0000-0002-1234-5678"
      affiliation: "University of Amsterdam"
  doi: "10.1234/example.2026.001"
  date: "2026-03-15"
  venue: "Journal of Experimental Psychology"

claims:
  - id: "H1"
    type: hypothesis
    statement: "Sleep deprivation (24+ hours) reduces multi-attribute decision accuracy by at least 10%."
    testable: true
    tested_in_paper: true
    status: supported

acceptance:
  - claim_id: "H1"
    criterion: "Mean accuracy drops by >= 10 percentage points in sleep-deprived condition."
    falsification: "Accuracy difference < 5 percentage points or favors sleep-deprived condition."
    threshold: "Cohen's d >= 0.5, p < .005"

results:
  - claim_id: "H1"
    status: supported
    effect_size: "Cohen's d = 0.72"
    p_value: "p < .001"

data:
  available: true
  url: "https://doi.org/10.5281/zenodo.1234567"
  format: "CSV"
```

Every section except `meta` is optional. Add what you have. Each section adds value independently.

## Specification

The full specification is in [SPECIFICATION.md](SPECIFICATION.md). It defines all sections, field types, validation levels, and the relationship to existing standards (FAIR, CiTO, JATS, nanopubs, registered reports).

## Validation

```bash
# Validate against the JSON Schema
pip install jsonschema pyyaml
python -c "
import yaml, jsonschema, json
with open('paper.yaml') as f: doc = yaml.safe_load(f)
with open('schema/paper-spec-v0.1.0.json') as f: schema = json.load(f)
jsonschema.validate(doc, schema)
print('Valid.')
"
```

Validation levels range from Level 0 (just metadata) to Level 4 (all sections present). Any level is valid.

## Contributing

Paper Spec is in early development (v0.1.0). Contributions are welcome:

1. **Use it.** Write a `paper.yaml` for one of your papers and report what was unclear or missing.
2. **Open an issue.** Suggestions for new fields, better names, or structural changes.
3. **Submit a PR.** Fixes, examples, tooling, or schema improvements.

Before proposing new fields, consider whether the information is something a paper's authors would reasonably know and write down in 30 minutes. If it requires external analysis or subjective judgment, it probably belongs in a downstream tool, not the spec.

## License

- **Specification:** CC-BY-4.0
- **Code and tooling:** MIT