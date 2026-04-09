class PromptManager:
    PROMPTS = {
        "v1": """You are a software testing assistant.
Given the following requirements, do:
1) list input variables
2) derive equivalence partitions (valid/invalid)
3) derive boundary values
4) produce concrete test cases with expected results
Return in JSON format.

Requirement: {requirement_text}
""",
        "v2": """You are a software testing assistant.
Return a JSON object with keys: input_variables, equivalence_partitions, boundary_values, test_cases, notes.
Each equivalence partition must include id, description, valid.
Each boundary item must include variable and values.
Each test case must include id, scenario, inputs, expected.
Do not include any extra keys.

Requirement: {requirement_text}
""",
        "v3": """You are a software testing assistant.
Return a JSON object with keys: input_variables, equivalence_partitions, boundary_values, test_cases, notes.
Before finalizing, self-check for missing boundaries, invalid cases, and contradictions.
If any issues are found, fix them and mention them in notes.
Do not include any extra keys.

Requirement: {requirement_text}
""",
        "v4": """You are a black-box testing assistant.

You will be given either:
- requirement text, or
- a testing codebase/module snippet (may contain API endpoints, validations, constraints).

Your task is to generate black-box test design artifacts based on the selected technique:
- ep_bva: Equivalence Partitioning + Boundary Value Analysis
- decision_table: Decision Table Testing
- state_transition: State Transition Testing (model + tests)
- combinatorial: Input combinations (pairwise-focused)

Output MUST be a single JSON object.

You MUST output ONLY the fields required by the selected technique.
Do NOT include fields from other techniques.

Hard rules:
- Include both valid and invalid cases. Invalid means violating at least one explicit constraint.
- Every boundary value must be derived from a specific numeric/count/time/length boundary stated or implied.
- Every test_case must map to at least one equivalence partition and/or boundary value (mention mapping in scenario text briefly).
- Do NOT invent system features that are not in the input. If something is unknown, state assumptions in notes and keep tests conservative.
- Return strict JSON only (no markdown, no extra text).

Technique instructions:
1) If technique=ep_bva:
   - Identify ALL input variables and constraints:
     - In input_variables, list variable names.
     - In notes, add a "constraints:" section describing for each variable: type, allowed range/enum, and dependencies.
   - Equivalence partitions (EP):
     - For EACH variable, create >=1 valid EP and >=1 invalid EP (if invalid inputs exist).
     - Each EP MUST include: id, description, valid, representative_values (>=1 concrete value).
     - Include robustness EP where applicable: missing/null, empty string, wrong type, out-of-range, invalid format/charset.
     - Cross-field/business rules MUST be modeled as combined EP entries (valid=false) with representative_values as a full input object demonstrating the violation.
   - Boundary value analysis (BVA):
     - For ordered types (number/length/date/time/money/count), for each variable generate rows for:
       min-1, min, min+1, max-1, max, max+1 (if applicable).
       Each boundary_values row MUST include: variable, boundary_type, value, expected_valid.
     - For enum/discrete types, include one boundary_values row per variable stating:
       boundary_type="enum_no_ordered_boundary", value=null, expected_valid=null.
   - Test cases (minimal but complete):
     - Cover every valid EP at least once (success).
     - Cover every invalid EP (including cross-field EP) at least once (failure).
     - Cover every BVA row with expected_valid=true/false at least once with a dedicated case.
     - scenario MUST explicitly list covered EP ids and boundary rows (variable+boundary_type+value).
     - expected MUST be precise: "HTTP <code>; field=<field>; code=<error_code>" or "HTTP 201 Created".
   - Coverage summary:
     - Output coverage_summary with:
       total_equivalence_partitions, covered_partitions, total_boundary_conditions, covered_boundary_conditions, notes.
2) If technique=decision_table:
   - Output MUST strictly follow this JSON shape (no extra keys):
     {{
       "input_variables": [...],
       "conditions": [{{"id","description","values"}}],
       "actions": [{{"id","description"}}],
       "rules": [{{"rule_id","condition_entries","action_entries","description"}}],
       "test_cases": [{{"id","covers_rule","inputs","expected"}}],
       "coverage": {{"total_rules","covered_rules","notes"}},
       "notes": "",
       "meta": {{"technique","model","temperature"}}
     }}
   - Modeling:
     - Each condition must be boolean or finite-enum; list allowed values in conditions[i].values.
     - Build rules as columns; condition_entries order MUST match the conditions array.
     - Use "-" for don't care in condition_entries.
     - action_entries order MUST match the actions array; use "X" to mark action executed, otherwise "".
     - Merge rules when actions are identical and only irrelevant conditions differ (use "-").
   - Test cases:
     - One test case per rule (covers_rule=rule_id).
     - Inputs must satisfy the rule column and expected must align with the rule's marked action(s).
   - Prohibitions:
     - Do NOT output EP/BVA/combinatorial/state-transition fields.
3) If technique=state_transition:
   - Output MUST strictly follow this JSON shape (no extra keys):
     {{
       "states": [{{"id","name","description"}}],
       "events": [{{"id","name","description"}}],
       "transitions": [{{"id","from_state","to_state","event","guard","action","output"}}],
       "test_cases": [{{"id","description","initial_state","event","context","expected_state","expected_output"}}],
       "coverage": {{"total_transitions","covered_transitions","uncovered_transition_ids","notes"}},
       "meta": {{"technique","model","temperature"}}
     }}
   - Suitability detection:
     - If no stateful behavior is detected, output:
       {{"error": "No stateful behavior detected. State transition testing is not applicable.", "coverage": ..., "meta": ...}}
   - State modeling:
     - States must be stable internal phases, NOT input values.
     - Do NOT use a flat model with only initial/success/reject. Include at least one intermediate state (e.g., submitted/validating/validation_failed/success).
   - Events:
     - Define events as triggers (API call, user action, timeout, callback).
   - Transitions:
     - Each transition must reference state/event IDs (S#/E#) and have non-empty guard when conditions apply.
     - Negative transitions: illegal event should keep state or go to an error state with 4xx output.
   - Test cases:
     - Each test case should cover one transition (single-step transition preferred) OR a short path.
     - For this tool's schema, use single-step cases: initial_state + event + context -> expected_state/output.
     - expected_output MUST match the referenced transition.output.
   - Coverage:
     - covered_transitions should equal number of transition IDs referenced by test cases.
4) If technique=combinatorial:
   - Output MUST strictly follow this JSON shape (no extra keys):
     {{
       "parameters": [{{"name","values","type"}}],
       "constraints": [{{"id","description","invalid_combinations"}}],
       "test_cases": [{{"id","description","inputs","expected"}}],
       "coverage": {{"total_pairs","covered_pairs","pairwise_coverage_percent","notes"}},
       "meta": {{"technique","strategy","model","temperature"}}
     }}
   - Default strategy is pairwise (2-way), so meta.strategy MUST be "pairwise".
   - parameters:
     - Include only VALID values (invalid enums/formats go into separate negative tests, not the pairwise set).
     - Provide a simple type label: "enum" | "boolean" | "numeric_range".
   - constraints:
     - List business-rule invalid combinations explicitly and include at least one concrete invalid combination object each.
     - Pairwise generation must avoid invalid combinations; if some pairs become impossible, explain in coverage.notes.
   - test_cases:
     - Create a minimized suite that aims for 100% pairwise coverage (of valid pairs), subject to constraints.
     - Each test case assigns exactly one value per parameter.
     - expected should be "HTTP 201 Created" or "HTTP 400; field=...; code=..." based on constraints/rules.
   - Prohibitions:
     - Do NOT output EP/BVA/decision-table/state-transition fields.

Before finalizing:
- self-check for missing negative cases, missing boundaries, contradictions, duplicate variables, and JSON validity.

Input type: {input_type}
Technique: {technique}

Requirement text:
{requirement_text}

Code context:
{code_context}
""",
    }

    @classmethod
    def get_prompt(
        cls,
        version: str,
        input_type: str,
        technique: str,
        requirement_text: str,
        code_context: str,
    ) -> str:
        prompt = cls.PROMPTS.get(version, cls.PROMPTS["v1"])
        return prompt.format(
            input_type=input_type,
            technique=technique,
            requirement_text=requirement_text or "",
            code_context=code_context or "",
        )
