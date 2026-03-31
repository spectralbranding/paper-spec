# Journal Requirement Profiles

Machine-readable requirement profiles for academic journals. Each file encodes a journal's submission standards — reporting rules, data policies, methodological requirements — in a format that can be checked against a `paper.yaml` before submission.

## Concept

A journal spec answers: "Does this paper meet the technical submission requirements of this venue?"

```
paper.yaml  +  journal_specs/jm.yaml  →  validate  →  compliance report
```

This is not peer review. Journal specs encode mechanical requirements: must report exact p-values, must share data, must include effect sizes. They cannot assess whether a paper is good, only whether it is formatted and reported in the way the journal demands.

## Files

| File | Journal | Source |
|------|---------|--------|
| `jm.yaml` | Journal of Marketing | Steenkamp et al. (2026) editorial |
| `jcr.yaml` | Journal of Consumer Research | Public editorial policies |
| `nature.yaml` | Nature | Nature author guidelines |

## File Structure

Each journal spec contains two top-level sections:

```yaml
journal:
  name: ...          # Full journal name
  abbreviation: ...  # Common abbreviation
  publisher: ...
  issn: ...
  source: ...        # Where these requirements come from

requirements:
  results: ...       # Reporting standards
  methodology: ...   # Design and analysis requirements
  data: ...          # Data availability policy
  code: ...          # Code availability policy
  replication: ...   # Reproducibility requirements
  claims: ...        # Hypothesis and claim requirements
```

Each requirement entry has:

- `required: true/false` — hard requirement vs. recommendation
- `recommended: true/false` — encouraged but not mandatory
- `prohibited: true/false` — explicitly forbidden
- `note` — plain-language explanation from the source policy

## Usage

Journal specs are reference documents today. A future validator will check `paper.yaml` fields against a journal spec and report gaps. For example: if `jm.yaml` requires `effect_size` and your `results` entries omit `effect_size`, the validator flags a mismatch before you submit.

## Scope

Journal specs encode only what the journal's published policies or editorials state explicitly. Requirements are not inferred or interpreted beyond what the source documents say. When a requirement is editorial guidance rather than a written rule, this is noted.

## Contributing

To add a journal:

1. Find the journal's author guidelines or a recent methods editorial.
2. Copy the structure from an existing spec.
3. Encode only what the source explicitly states.
4. Set `source` to the specific document (with DOI if available).
5. Submit a PR with the source document cited.
