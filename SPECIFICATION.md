# Paper Spec v0.1.0

A machine-readable specification format for scientific papers.

## Introduction

Scientific papers are published as unstructured PDFs. The claims they make, the methods they use, the data they depend on, and the conditions under which those claims would be falsified are all buried in natural language. This makes systematic verification, replication planning, and dependency tracking expensive and error-prone.

Paper Spec defines `paper.yaml` -- a structured companion file that lives alongside a paper and makes its core content machine-readable. It does not replace the paper. It indexes it.

A `paper.yaml` file answers six questions that every reader eventually asks:

1. **What does this paper claim?** (claims)
2. **How were those claims tested?** (methodology, results)
3. **What would prove them wrong?** (acceptance)
4. **Can I reproduce this?** (data, code, replication)
5. **What does this depend on?** (dependencies)
6. **What are its known limits?** (limitations, contradictions)
7. **Where can I find it, and how did it get there?** (repositories, submission_history)

## Design Principles

1. **Human-writable.** A working researcher should be able to write a `paper.yaml` for their paper in 30 minutes. No tooling required -- a text editor is sufficient.

2. **Machine-parseable.** Standard YAML 1.2, validatable against a JSON Schema. Any language with a YAML parser can consume it.

3. **Incremental adoption.** Every section is optional except `meta`. A `paper.yaml` with nothing but metadata is still useful. Each additional section adds value independently.

4. **Minimal jargon.** Field names should be self-explanatory to a researcher who has never seen the spec. If a field name needs a paragraph of explanation, it is the wrong name.

5. **Stable identifiers.** Claim IDs within a paper are stable across versions, enabling external references that survive revisions.

6. **No opinions on content.** The spec describes structure, not quality. It does not judge whether a claim is good, whether a methodology is sound, or whether a p-value is meaningful. It records what the authors state.

## Document Structure

A `paper.yaml` file contains the following top-level keys:

```yaml
spec_version: "0.1.0"        # Required. Which version of Paper Spec this file conforms to.

meta:           {}            # Required. Bibliographic metadata.
claims:         []            # Strongly recommended. The paper's truth claims.
methodology:    {}            # How the claims were tested or derived.
acceptance:     []            # What would confirm or refute each claim.
data:           {}            # Data availability and location.
code:           {}            # Code availability and location.
replication:    {}            # What someone needs to reproduce this work.
dependencies:   []            # Papers and claims this work builds on.
contradictions: []            # Known contradictions with other work.
results:        []            # Outcomes mapped to claims.
limitations:    []            # Acknowledged limitations.
repositories:   []            # Where the paper can be found (Zenodo, arXiv, GitHub, etc.).
submission_history: []        # Publication journey: submissions, decisions, revisions.
```

All sections except `meta` are optional. Order does not matter, but the order above is conventional.

**A note on provenance.** The `repositories` and `submission_history` sections make the paper's publication journey transparent. `repositories` is strongly recommended -- it solves the "where is the latest version?" problem. `submission_history` is optional but encouraged: it serves open science norms by documenting how the paper reached its current state. An empty `submission_history` is a valid choice; its absence, however, signals that publication history is not being disclosed.

---

## Field Reference

### spec_version

| Property | Value |
|----------|-------|
| Type | string |
| Required | Yes |
| Format | Semantic version (MAJOR.MINOR.PATCH) |

The version of the Paper Spec that this file conforms to. Validators use this to select the correct schema.

```yaml
spec_version: "0.1.0"
```

---

### meta

Bibliographic metadata. The only required section.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Paper title. |
| authors | list of author objects | Yes | At least one author. |
| authors[].name | string | Yes | Author name in "Last, First" format. |
| authors[].orcid | string | No | ORCID identifier (e.g., "0000-0002-1234-5678"). |
| authors[].affiliation | string | No | Institutional affiliation. |
| doi | string | No | DOI if published. Include the full DOI, not a URL. |
| date | string | No | Publication or preprint date in YYYY-MM-DD format. |
| version | string | No | Paper version. Useful for preprints with revisions. |
| venue | string | No | Journal name, conference name, or "Preprint". |
| license | string | No | SPDX license identifier (e.g., "CC-BY-4.0"). |
| keywords | list of strings | No | Subject keywords. |
| abstract | string | No | Full abstract text. Use YAML multi-line syntax for readability. |

Example:

```yaml
meta:
  title: "The Effect of Sleep Deprivation on Decision Quality"
  authors:
    - name: "Chen, Wei"
      orcid: "0000-0002-1234-5678"
      affiliation: "University of Amsterdam"
    - name: "Patel, Ananya"
      affiliation: "ETH Zurich"
  doi: "10.1234/example.2026.001"
  date: "2026-03-15"
  version: "2"
  venue: "Journal of Experimental Psychology"
  license: "CC-BY-4.0"
  keywords:
    - sleep deprivation
    - decision making
    - cognitive load
  abstract: >
    We tested whether 24 hours of sleep deprivation reduces
    decision quality in a multi-attribute choice task. Sixty
    participants completed 200 trials each under rested and
    sleep-deprived conditions. Sleep deprivation reduced
    accuracy by 14% (p < .001, d = 0.72).
```

---

### claims

The paper's truth claims. This is the most valuable section after `meta` -- it makes the paper's contributions explicit and referenceable.

Each claim is an object in a list.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier within this paper (e.g., "H1", "P1", "T1", "D1"). |
| type | enum | Yes | One of: `hypothesis`, `proposition`, `theorem`, `conjecture`, `definition`. |
| statement | string | Yes | The claim in plain language. |
| formal | string | No | Formal or mathematical statement. |
| testable | boolean | No | Is this claim empirically testable? Default: inferred from type. |
| tested_in_paper | boolean | No | Was this claim tested in this paper? |
| status | enum | No | One of: `supported`, `refuted`, `inconclusive`, `not_tested`. |
| depends_on | list of strings | No | IDs of other claims within this paper that this claim depends on. |

Claim IDs must be unique within the file and should remain stable across paper versions to preserve external references.

Example:

```yaml
claims:
  - id: "H1"
    type: hypothesis
    statement: >
      Sleep deprivation (24+ hours) reduces multi-attribute
      decision accuracy by at least 10%.
    testable: true
    tested_in_paper: true
    status: supported

  - id: "H2"
    type: hypothesis
    statement: >
      The accuracy reduction from sleep deprivation is mediated
      by working memory capacity, not attention.
    testable: true
    tested_in_paper: true
    status: inconclusive
    depends_on: ["H1"]
```

---

### methodology

How the claims were tested or derived.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | enum | Yes (if section present) | One of: `empirical`, `theoretical`, `computational`, `mixed`, `meta_analysis`, `review`. |
| design | string | No | Study design in brief (e.g., "within-subjects RCT", "proof by induction"). |
| sample | object | No | Sample details. See below. |
| sample.size | integer | No | Number of participants/observations. |
| sample.population | string | No | Target population. |
| sample.recruitment | string | No | How participants were recruited. |
| sample.exclusion | list of strings | No | Exclusion criteria. |
| measures | list of measure objects | No | Variables and instruments. |
| measures[].variable | string | Yes (if measure present) | Variable name. |
| measures[].instrument | string | No | Measurement instrument. |
| measures[].reliability | string | No | Reliability metric (e.g., "Cronbach alpha = 0.87"). |
| analysis | object | No | Analysis details. |
| analysis.method | string | No | Statistical or analytical method. |
| analysis.software | string | No | Software and version. |

Example:

```yaml
methodology:
  type: empirical
  design: "within-subjects, counterbalanced"
  sample:
    size: 60
    population: "healthy adults aged 18-35"
    recruitment: "university participant pool"
    exclusion:
      - "diagnosed sleep disorder"
      - "shift workers"
      - "caffeine intake > 400mg/day"
  measures:
    - variable: "decision accuracy"
      instrument: "multi-attribute choice task (custom, 200 trials)"
      reliability: "split-half r = 0.91"
    - variable: "working memory"
      instrument: "operation span task"
      reliability: "Cronbach alpha = 0.87"
  analysis:
    method: "mixed-effects logistic regression"
    software: "R 4.3, lme4 1.1-35"
```

---

### acceptance

What would confirm or refute each claim. This is the section that makes Paper Spec more than metadata -- it captures the conditions under which the authors consider their own claims valid.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| claim_id | string | Yes (if entry present) | References a claim ID from the `claims` section. |
| criterion | string | Yes (if entry present) | What would confirm this claim. |
| falsification | string | No | What would refute this claim. |
| threshold | string | No | Quantitative threshold, if applicable. |

Example:

```yaml
acceptance:
  - claim_id: "H1"
    criterion: >
      Mean accuracy in the sleep-deprived condition is at least
      10 percentage points lower than in the rested condition.
    falsification: >
      Mean accuracy difference is less than 5 percentage points
      or favors the sleep-deprived condition.
    threshold: "Cohen's d >= 0.5, p < .005 (two-tailed)"

  - claim_id: "H2"
    criterion: >
      Mediation analysis shows significant indirect effect
      through working memory (95% CI excludes zero) with
      non-significant direct effect.
    falsification: >
      Direct effect remains significant after controlling
      for working memory.
```

---

### data

Data availability and location.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| available | boolean | Yes (if section present) | Is the data publicly available? |
| url | string | No | URL or DOI to the dataset. |
| format | string | No | File format (e.g., "CSV", "JSON", "Parquet"). |
| size | string | No | Human-readable size description. |
| license | string | No | SPDX license identifier for the data. |

Example:

```yaml
data:
  available: true
  url: "https://doi.org/10.5281/zenodo.1234567"
  format: "CSV"
  size: "2.3 MB, 12000 rows x 8 columns"
  license: "CC-BY-4.0"
```

If data cannot be shared (e.g., due to IRB restrictions), set `available: false` and optionally explain in a comment.

---

### code

Code availability and location.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| available | boolean | Yes (if section present) | Is the analysis code publicly available? |
| url | string | No | URL to the repository or archive. |
| language | string | No | Programming language and version. |
| dependencies | string | No | How to install dependencies (e.g., "see requirements.txt"). |

Example:

```yaml
code:
  available: true
  url: "https://github.com/example/sleep-decision-study"
  language: "R 4.3"
  dependencies: "renv.lock in repository root"
```

---

### replication

What someone would need to reproduce this work.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| feasible | boolean | No | Is independent replication practically feasible? |
| estimated_cost | string | No | Estimated cost of replication. |
| estimated_time | string | No | Estimated time to replicate. |
| requirements | list of strings | No | What a replicator would need. |
| contact | string | No | Email address for replication queries. |

Example:

```yaml
replication:
  feasible: true
  estimated_cost: "$2,400 (60 participants x $40 via Prolific)"
  estimated_time: "4 weeks (2 weeks recruitment, 2 weeks data collection)"
  requirements:
    - "sleep lab with polysomnography"
    - "multi-attribute choice task software (open-sourced, see code.url)"
    - "IRB approval for sleep deprivation protocol"
  contact: "replication@example.edu"
```

---

### dependencies

Papers and specific claims this work builds on. This goes beyond a reference list -- it identifies which claims in which papers are load-bearing for the current work.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| doi | string | Yes (if entry present) | DOI of the dependency. |
| claim | string | No | Which specific claim is depended upon (free text). |
| relationship | enum | No | One of: `extends`, `applies`, `tests`, `contradicts`, `refines`. |
| critical | boolean | No | Would this paper's claims fail if the dependency were retracted? |

Example:

```yaml
dependencies:
  - doi: "10.1037/rev0000045"
    claim: "Working memory capacity predicts decision quality under cognitive load"
    relationship: extends
    critical: true

  - doi: "10.1111/sleep.13200"
    claim: "24-hour sleep deprivation impairs executive function equivalently to 0.10% BAC"
    relationship: applies
    critical: false
```

---

### contradictions

Known contradictions with other published work. Honest declaration of conflicts in the literature.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| doi | string | Yes (if entry present) | DOI of the contradicting paper. |
| claim | string | Yes (if entry present) | What the other paper claims. |
| our_position | string | Yes (if entry present) | How this paper reconciles or disagrees. |

Example:

```yaml
contradictions:
  - doi: "10.1016/j.cognition.2024.105432"
    claim: "Sleep deprivation has no significant effect on multi-attribute decisions"
    our_position: >
      That study used a 2-alternative task; our 5-alternative task
      increases cognitive load, which we argue is necessary to
      observe the effect.
```

---

### results

Outcomes mapped back to claims. This creates a direct link between what was claimed and what was found.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| claim_id | string | Yes (if entry present) | References a claim ID. |
| status | enum | Yes (if entry present) | One of: `supported`, `refuted`, `partially_supported`, `inconclusive`. |
| effect_size | string | No | Effect size and measure. |
| confidence_interval | string | No | Confidence interval. |
| p_value | string | No | p-value. |
| notes | string | No | Additional context. |

Example:

```yaml
results:
  - claim_id: "H1"
    status: supported
    effect_size: "Cohen's d = 0.72"
    confidence_interval: "95% CI [0.41, 1.03]"
    p_value: "p < .001"
    notes: "Effect consistent across all age subgroups"

  - claim_id: "H2"
    status: inconclusive
    effect_size: "indirect effect ab = 0.08"
    confidence_interval: "95% CI [-0.02, 0.18]"
    notes: >
      Confidence interval includes zero. Larger sample may be
      needed to detect mediation effect.
```

---

### limitations

Acknowledged limitations and their severity.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| description | string | Yes (if entry present) | Description of the limitation. |
| severity | enum | No | One of: `minor`, `moderate`, `major`. |
| addressable | boolean | No | Could this limitation be addressed in future work? |

Example:

```yaml
limitations:
  - description: "Sample limited to university students aged 18-35"
    severity: moderate
    addressable: true

  - description: "Sleep deprivation was self-reported, not polysomnography-verified"
    severity: major
    addressable: true

  - description: "Single-session design; no longitudinal component"
    severity: minor
    addressable: true
```

---

### repositories

Where the paper can be found. Tracks all deposits across platforms and maps versions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string | yes | Repository name (e.g., "Zenodo", "arXiv", "GitHub", "OSF Preprints", "institutional") |
| `url` | string | yes | Direct URL to the deposit |
| `doi` | string | no | DOI if the platform assigns one |
| `version` | string | no | Version identifier on this platform (e.g., "v3", "2026-03-24") |
| `date` | string | no | Date of this deposit (YYYY-MM-DD) |
| `notes` | string | no | Version-specific notes (e.g., "includes Section 7.5 update") |

**Example:**

```yaml
repositories:
  - platform: "Zenodo"
    doi: "10.5281/zenodo.18945912"
    url: "https://doi.org/10.5281/zenodo.18945912"
    version: "v3"
    date: "2026-03-24"
    notes: "v3: literature review fixes, 6 new references"

  - platform: "GitHub"
    url: "https://github.com/spectralbranding/sbt-papers/spectral-brand-theory"
    version: "latest"
    notes: "Living document; may be ahead of Zenodo version"
```

---

### submission_history

The paper's publication journey. Optional but encouraged for open science transparency.

Each entry documents a submission to a venue. An empty array is valid (paper has never been submitted). Omitting the section entirely is also valid, but signals that the author has chosen not to disclose submission history.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `venue` | string | yes | Journal, conference, or platform name |
| `date_submitted` | string | yes | Submission date (YYYY-MM-DD) |
| `manuscript_id` | string | no | Venue-assigned manuscript ID |
| `date_decision` | string | no | Decision date (YYYY-MM-DD) |
| `decision` | enum | no | `under_review`, `desk_reject`, `reject`, `revise_resubmit`, `accepted`, `published`, `withdrawn` |
| `notes` | string | no | Reviewer feedback summary, reason for rejection, or revision scope |
| `version_submitted` | string | no | Which version/DOI was submitted (links to `repositories`) |

**Example:**

```yaml
submission_history:
  - venue: "Organization Science"
    date_submitted: "2026-03-10"
    manuscript_id: "ORSC-MS-2026-22291"
    date_decision: "2026-03-15"
    decision: desk_reject
    notes: "Editor: extension of existing theory, not novel theory"
    version_submitted: "v1"

  - venue: "Journal of Organization Design"
    date_submitted: "2026-03-21"
    manuscript_id: "JORG-D-26-00036"
    decision: under_review
    version_submitted: "v2"
    notes: "Restructured from AMR rejection; SBT framing removed"
```

**Decision values:**

| Value | Meaning |
|-------|---------|
| `under_review` | Submitted, awaiting decision |
| `desk_reject` | Rejected by editor without peer review |
| `reject` | Rejected after peer review |
| `revise_resubmit` | Invited to revise and resubmit |
| `accepted` | Accepted for publication |
| `published` | Published in final form |
| `withdrawn` | Withdrawn by the author |

---

## Validation

A JSON Schema for `paper.yaml` is provided at `schema/paper-spec-v0.1.0.json` in the Paper Spec repository. Any YAML/JSON validator can check conformance:

```bash
# Example using Python
pip install jsonschema pyyaml
python -c "
import yaml, jsonschema, json
with open('paper.yaml') as f: doc = yaml.safe_load(f)
with open('schema/paper-spec-v0.1.0.json') as f: schema = json.load(f)
jsonschema.validate(doc, schema)
print('Valid.')
"
```

Validation levels:

- **Level 0 (minimal):** `spec_version` and `meta` with `title` and at least one author.
- **Level 1 (descriptive):** Level 0 plus `claims` with at least one claim.
- **Level 2 (testable):** Level 1 plus `acceptance` with entries for all tested claims.
- **Level 3 (reproducible):** Level 2 plus `methodology`, `data`, and `code`.
- **Level 4 (complete):** All sections present.

These levels are informational. A `paper.yaml` at any level is valid if it conforms to the schema.

---

## Versioning

Paper Spec follows semantic versioning:

- **PATCH** (0.1.x): Clarifications, typo fixes, additional examples. No schema changes.
- **MINOR** (0.x.0): New optional fields or sections. Existing files remain valid.
- **MAJOR** (x.0.0): Breaking changes. Existing files may need migration.

The `spec_version` field in each `paper.yaml` declares which version it conforms to. Validators should use this field to select the appropriate schema.

### Migration policy

When a new major version is released, a migration guide and automated migration tool will be provided. The previous major version will remain supported for at least 12 months.

---

## Relationship to Existing Standards

Paper Spec does not replace existing standards. It complements them.

**FAIR Data Principles.** Paper Spec's `data` and `code` sections operationalize FAIR (Findable, Accessible, Interoperable, Reusable) for individual papers. A `paper.yaml` file is itself a FAIR metadata record.

**CiTO (Citation Typing Ontology).** The `dependencies.relationship` field draws on CiTO's vocabulary but simplifies it to five terms. Papers that need full CiTO typing can extend this field.

**JATS (Journal Article Tag Suite).** JATS describes document structure (sections, figures, tables). Paper Spec describes epistemic structure (claims, evidence, falsifiability). They are orthogonal. A JATS-encoded paper can include a `paper.yaml` as supplementary material.

**Nanopublications.** Nanopubs decompose papers into atomic assertions with provenance. Paper Spec operates at a coarser grain -- whole claims rather than individual assertions. A `paper.yaml` could be decomposed into nanopubs by downstream tooling.

**Registered Reports.** The `acceptance` section captures the same information that registered reports require before data collection: what would confirm or refute each hypothesis, and at what threshold. Paper Spec brings this practice to papers that were not pre-registered.

**DataCite / Dublin Core.** The `meta` section overlaps with DataCite and Dublin Core metadata. Paper Spec adds no new metadata vocabulary -- it uses the same fields researchers already know. The value is in combining metadata with claims, methods, and acceptance criteria in a single file.

**Journal Requirement Profiles.** The `journal_specs/` directory in this repository extends Paper Spec with machine-readable profiles encoding what individual journals require at submission: exact p-value format, mandatory effect sizes, data availability policies. A journal profile maps these requirements back to `paper.yaml` fields, enabling pre-submission compliance checking. See `journal_specs/README.md` for the format and `journal_specs/jm.yaml` for a worked example based on an explicit editorial statement of standards.

---

## Scope and Non-Goals

Paper Spec is for indexing papers, not writing them. Specifically:

- It does not standardize how papers are written or structured.
- It does not assess quality or assign scores.
- It does not require any particular methodology or reporting standard.
- It does not replace peer review.
- It does not define an ontology of scientific concepts.

What it does: it gives every paper a machine-readable table of contents for its epistemic content.

---

## License

The Paper Spec specification is licensed under CC-BY-4.0. Reference implementations and tooling are licensed under MIT.