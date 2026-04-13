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

## Specialized Multi-Step Prompts

### EP/BVA Two-Step Generation

Used internally by the API for `ep_bva` technique when calling `/api/generate` or `/api/generate-stream`.

**Step 1** (`get_prompt_ecp_bva_only`): Generate equivalence partitions and boundary values only. No test cases generated in this step.

**Step 2** (`get_prompt_tc_from_ecp_bva`): Generate test cases based on the pre-computed ECP/BVA analysis from Step 1.

### Decision Table Three-Step Generation

Used internally by the API for `decision_table` technique.

**Step 1** (`get_prompt_conditions_actions`): Identify conditions and actions from requirements.

**Step 2** (`get_prompt_rules_from_conditions_actions`): Generate rules combining condition values.

**Step 3** (`get_prompt_tc_from_rules`): Generate test cases covering each rule.

## Prompt Tuning Workflow

1) Start with V1 to see raw coverage.
2) Switch to V2 if JSON is unstable or incomplete.
3) Use V3 for self-check and final output.
4) Use V4 when you need technique switching or codebase-context inputs.
5) For EP/BVA and Decision Table, the API uses specialized multi-step prompts automatically.
6) Record issues found by humans and refine prompt wording.
