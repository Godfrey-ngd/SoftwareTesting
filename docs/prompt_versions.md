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

## Prompt Tuning Workflow

1) Start with V1 to see raw coverage.
2) Switch to V2 if JSON is unstable or incomplete.
3) Use V3 for self-check and final output.
4) Record issues found by humans and refine prompt wording.
