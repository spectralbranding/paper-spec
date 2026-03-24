"""
template.py -- Generate a blank paper.yaml skeleton

Usage:
    python tools/template.py                    # theoretical paper (default)
    python tools/template.py --type empirical   # empirical paper
    python tools/template.py --type review      # review/survey paper
    python tools/template.py -o my-paper.yaml   # specify output file

Generates a starter paper.yaml with all sections and placeholder comments.
Fill in the sections, then validate with: python tools/validate.py my-paper.yaml
"""

import argparse
import sys
from pathlib import Path


TEMPLATES = {
    "theoretical": {
        "methodology_type": "theoretical",
        "methodology_design": "Framework construction / formal proof / analytical derivation.",
        "claim_types": ["proposition", "theorem", "definition"],
        "data_note": "No primary data collected. Illustrative examples only.",
        "replication_note": "Empirical validation requires survey/experiment design.",
    },
    "empirical": {
        "methodology_type": "empirical",
        "methodology_design": (
            "Describe: study design (RCT, quasi-experimental, observational), "
            "sample (size, population, recruitment), measures (instruments, reliability), "
            "procedure."
        ),
        "claim_types": ["hypothesis"],
        "data_note": "Describe data availability, URL, access conditions.",
        "replication_note": "Describe materials, cost, and time needed to replicate.",
    },
    "review": {
        "methodology_type": "review",
        "methodology_design": (
            "Describe: search strategy (databases, keywords, date range), "
            "inclusion/exclusion criteria, synthesis method "
            "(narrative, systematic, meta-analytic)."
        ),
        "claim_types": ["proposition", "conjecture"],
        "data_note": "Based on published literature. No primary data.",
        "replication_note": "Replicate by re-running search with documented strategy.",
    },
    "computational": {
        "methodology_type": "computational",
        "methodology_design": (
            "Describe: model specification, simulation parameters, "
            "validation approach, software/hardware."
        ),
        "claim_types": ["hypothesis", "proposition"],
        "data_note": "Simulated data. Parameters documented in methodology.",
        "replication_note": "Replicate by re-running code with documented parameters.",
    },
}


def generate_template(paper_type: str) -> str:
    cfg = TEMPLATES.get(paper_type, TEMPLATES["theoretical"])
    claim_example = cfg["claim_types"][0]

    return f"""# paper.yaml -- Paper Spec v0.1.0
# Generated with: python tools/template.py --type {paper_type}
# Fill in the sections below, then validate: python tools/validate.py this-file.yaml
spec_version: "0.1.0"

meta:
  title: ""          # Paper title
  authors:
    - name: ""       # "Last, First" format
      orcid: ""      # Optional: ORCID identifier
      affiliation: ""
  # doi: ""          # Uncomment when published
  date: ""           # YYYY-MM-DD
  venue: ""          # Journal, conference, or "Preprint"
  license: "CC-BY-4.0"
  keywords:
    - # keyword 1
    - # keyword 2
    - # keyword 3

claims:
  # Add one entry per claim. Unique IDs: H1, P1, T1, D1, C1, etc.
  - id: "{claim_example.upper()[0]}1"
    type: {claim_example}
    statement: >
      Describe the claim in plain language.
    # formal: ""     # Optional: mathematical/formal statement
    testable: true
    tested_in_paper: false
    status: not_tested
    depends_on: []

methodology:
  type: {cfg["methodology_type"]}
  design: >
    {cfg["methodology_design"]}
  analysis:
    method: ""
    software: ""

acceptance:
  - claim_id: "{claim_example.upper()[0]}1"
    criterion: >
      What evidence would confirm this claim?
    falsification: >
      What evidence would refute this claim?

data:
  available: false
  url: ""
  notes: >
    {cfg["data_note"]}

code:
  available: false
  url: ""
  notes: ""

replication:
  feasible: true
  estimated_cost: ""
  estimated_time: ""
  requirements:
    - "{cfg["replication_note"]}"

dependencies:
  # Add papers this work builds on. Use DOI or reference string.
  - doi: ""
    claim: "What this paper takes from the dependency"
    relationship: extends    # extends | applies | tests | contradicts | refines
    critical: true

contradictions: []

results:
  - claim_id: "{claim_example.upper()[0]}1"
    status: not_tested
    notes: >
      Summarize evidence for/against this claim.

limitations:
  - description: >
      Describe limitation.
    severity: moderate    # minor | moderate | major
    addressable: true

repositories:
  - platform: ""          # Zenodo, arXiv, GitHub, etc.
    url: ""
    # doi: ""             # Uncomment if applicable

submission_history: []
# Uncomment and fill if applicable:
# - venue: ""
#   date_submitted: ""    # YYYY-MM-DD
#   decision: under_review  # under_review | desk_reject | reject | revise_resubmit | accepted | published | withdrawn
#   notes: ""
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a blank paper.yaml template"
    )
    parser.add_argument(
        "--type",
        choices=list(TEMPLATES.keys()),
        default="theoretical",
        help="Paper type (default: theoretical)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    content = generate_template(args.type)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Template written to {args.output}")
        print(f"Next: fill in the sections, then run: python tools/validate.py {args.output}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
