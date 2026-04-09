# Prompt Versions

## V1

Goal: extract variables, EP/BVA, and test cases in JSON.

Usage notes:
- Best for quick drafts and early iteration.
- Expect occasional missing fields; fix in V2/V3.

## V2

Goal: enforce JSON schema with explicit valid/invalid flags and consistent fields.

Usage notes:
- Use when you need stable JSON for parsing.
- Reject outputs with extra keys or missing required fields.

## V3

Goal: add self-check for missing boundaries, invalid cases, and contradictions.

Usage notes:
- Use for final generation runs.
- Prioritize correctness and coverage over creativity.

## V4

Goal: support **technique selection** (EP/BVA, decision table, state transition, combinatorial) and **input type selection** (requirements vs codebase context), with strict JSON-only output and stronger self-check.

Usage notes:
- Use as the default for submissions and demos.
- Put decision table / transition model summaries into `notes` (keep JSON-only).
- Keep temperature low (0.0-0.3) for stable structure.

## Prompt Tuning Workflow

1) Start with V1 to see raw coverage.
2) Switch to V2 if JSON is unstable or incomplete.
3) Use V3 for self-check and final output.
4) Use V4 when you need technique switching or codebase-context inputs.
5) Record issues found by humans and refine prompt wording.
