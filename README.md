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

A minimal `paper.yaml` (just metadata):

```yaml
spec_version: "0.1.0"

meta:
  title: "Why Most Published Research Findings Are False"
  authors:
    - name: "Ioannidis, John P. A."
      orcid: "0000-0003-3118-6859"
      affiliation: "University of Ioannina School of Medicine"
  doi: "10.1371/journal.pmed.0020124"
  date: "2005-08-30"
  venue: "PLoS Medicine"
```

A more complete one -- Kahneman & Tversky's prospect theory:

```yaml
spec_version: "0.1.0"

meta:
  title: "Prospect Theory: An Analysis of Decision under Risk"
  authors:
    - name: "Kahneman, Daniel"
      affiliation: "Hebrew University of Jerusalem"
    - name: "Tversky, Amos"
      affiliation: "Stanford University"
  doi: "10.2307/1914185"
  date: "1979-03-01"
  venue: "Econometrica"
  license: "proprietary"
  keywords:
    - decision making
    - risk
    - utility theory
    - prospect theory
    - loss aversion

claims:
  - id: "H1"
    type: hypothesis
    statement: >
      People underweight outcomes that are merely probable compared to outcomes
      that are obtained with certainty (the certainty effect), leading to risk
      aversion in choices involving sure gains and risk seeking in choices
      involving sure losses.
    testable: true
    tested_in_paper: true
    status: supported

  - id: "H2"
    type: hypothesis
    statement: >
      The value function is defined on deviations from a reference point, is
      generally concave for gains and convex for losses, and is steeper for
      losses than for gains (loss aversion).
    testable: true
    tested_in_paper: true
    status: supported
    depends_on: ["H1"]

acceptance:
  - claim_id: "H1"
    criterion: >
      In forced-choice experiments, a statistically significant majority of
      subjects prefer a certain gain over a probabilistically equivalent or
      superior gamble, and prefer a gamble over a certain loss of equivalent
      expected value.
    falsification: >
      Subjects show no systematic preference for certainty in gains or
      gambling in losses -- choices are consistent with expected utility theory.

results:
  - claim_id: "H1"
    status: supported
    notes: >
      Problem 1: 80% chose certain 2,500 over (3,000, p=0.80). Problem 7:
      92% chose (6,000, p=0.45) over certain 3,000 loss. N=72 university
      students per problem.

  - claim_id: "H2"
    status: supported
    notes: >
      The reflection effect (Problems 3-4, 7-8) demonstrates convexity for
      losses mirroring concavity for gains. Loss aversion ratio estimated
      at approximately 2:1 from median responses.

dependencies:
  - reference: "von Neumann, J., & Morgenstern, O. (1947). Theory of Games and Economic Behavior."
    claim: "Expected utility theory -- the baseline model that prospect theory replaces"
    relationship: "contradicts"
    critical: true

  - reference: "Allais, M. (1953). Le comportement de l'homme rationnel devant le risque."
    claim: "The Allais paradox -- first documented violation of expected utility axioms"
    relationship: "extends"
    critical: true

limitations:
  - description: >
      All experiments used hypothetical choices with university students.
      No real monetary stakes were involved. Generalizability to real economic
      decisions and non-student populations is assumed but not tested.
    severity: major
    addressable: true
```

Every section except `meta` is optional. Add what you have. Each section adds value independently.

The [examples/](examples/) directory contains 23 real `paper.yaml` files from two active research programs, including papers with full submission histories across multiple journals.

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