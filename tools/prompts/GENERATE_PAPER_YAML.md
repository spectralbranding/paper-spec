# Generate paper.yaml from a Paper

Paste this prompt into any LLM (Claude, GPT-4, Gemini) along with your paper's text to generate a draft paper.yaml file.

---

## Prompt

You are a research assistant. Read the paper below and generate a `paper.yaml` file following the Paper Spec v0.1.0 standard.

**Instructions:**

1. Extract ALL formal claims (hypotheses, propositions, theorems, definitions, conjectures) from the paper. Give each a unique ID (H1, P1, T1, D1, etc.).

2. For each claim, determine:
   - `type`: one of `hypothesis`, `proposition`, `theorem`, `conjecture`, `definition`
   - `statement`: plain language description
   - `formal`: mathematical/formal statement (if present in paper)
   - `testable`: is this empirically testable?
   - `tested_in_paper`: was it tested in this paper?
   - `status`: one of `supported`, `refuted`, `inconclusive`, `not_tested`
   - `depends_on`: IDs of other claims it depends on

3. Extract methodology: type (one of `empirical`, `theoretical`, `computational`, `mixed`, `meta_analysis`, `review`), design description, analysis methods.

4. For each claim, write acceptance criteria (what would confirm it) and falsification criteria (what would refute it).

5. Extract dependencies: papers this work builds on. Use DOIs where available. Relationship must be one of: `extends`, `applies`, `tests`, `contradicts`, `refines`.

6. Note limitations with severity: `minor`, `moderate`, `major`.

7. Include repository information (where the paper is available) and submission history if known.

**Output format:**

```yaml
# paper.yaml -- Paper Spec v0.1.0
spec_version: "0.1.0"

meta:
  title: "[paper title]"
  authors:
    - name: "[Last, First]"
      orcid: "[if known]"
      affiliation: "[institution]"
  doi: "[if published]"
  date: "[YYYY-MM-DD]"
  venue: "[journal/conference or 'Preprint']"
  license: "[SPDX identifier, e.g., CC-BY-4.0]"
  keywords:
    - [keyword 1]
    - [keyword 2]

claims:
  - id: "[H1/P1/T1/D1]"
    type: "[hypothesis/proposition/theorem/conjecture/definition]"
    statement: >
      [plain language claim]
    formal: "[mathematical statement if applicable]"
    testable: [true/false]
    tested_in_paper: [true/false]
    status: "[supported/refuted/inconclusive/not_tested]"
    depends_on: ["[other claim IDs]"]

methodology:
  type: "[empirical/theoretical/computational/mixed/meta_analysis/review]"
  design: >
    [description of research design]
  analysis:
    method: "[analysis approach]"
    software: "[tools used]"

acceptance:
  - claim_id: "[claim ID]"
    criterion: >
      [what would confirm this claim]
    falsification: >
      [what would refute this claim]

data:
  available: [true/false]
  url: "[data URL]"
  notes: "[access conditions]"

code:
  available: [true/false]
  url: "[code URL]"
  notes: "[what the code does]"

replication:
  feasible: [true/false]
  estimated_cost: "[cost estimate]"
  estimated_time: "[time estimate]"
  requirements:
    - "[requirement 1]"
    - "[requirement 2]"

dependencies:
  - doi: "[DOI of dependency]"
    claim: "[what this paper takes from the dependency]"
    relationship: "[extends/applies/tests/contradicts/refines]"
    critical: [true/false]

contradictions: []

results:
  - claim_id: "[claim ID]"
    status: "[supported/refuted/partially_supported/inconclusive/not_tested]"
    notes: >
      [summary of evidence]

limitations:
  - description: >
      [limitation description]
    severity: "[minor/moderate/major]"
    addressable: [true/false]

repositories:
  - platform: "[Zenodo/arXiv/GitHub/etc.]"
    url: "[URL]"
    doi: "[DOI if applicable]"

submission_history: []
```

**Rules:**
- Only use the enum values listed above for type, status, relationship, severity
- Claim IDs must be unique within the file
- Use `>` for multi-line YAML strings
- If a field is unknown, omit it rather than guessing
- Be conservative with `status` -- use `not_tested` unless the paper clearly tests the claim

---

## How to Use

1. Copy the prompt above
2. Paste your paper's full text after the prompt
3. Send to any LLM
4. Review and edit the generated paper.yaml
5. Validate: `python tools/validate.py your-paper.yaml`

Expected time: 10-15 minutes (LLM generation + human review)
