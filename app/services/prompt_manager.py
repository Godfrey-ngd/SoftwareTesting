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
     - If no explicit states are described, infer them from the requirement (e.g., "idle", "processing", "success", "failure", etc.).
     - Every requirement has some internal state—even a simple "input → output" can be modeled as transitions between implicit states.
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
"""
    }

    @classmethod
    def get_prompt_conditions_actions(cls, input_type: str, requirement_text: str, code_context: str) -> str:
        return f"""You are a black-box testing assistant.

Your task is to identify decision tables from requirements for Decision Table Testing.
Group related conditions and actions into separate decision tables.

Output MUST be a JSON object with this structure:
{{{{"decision_tables": [{{"name": "table_name", "conditions": [{{"id": "C1", "description": "...", "values": ["val1", "val2"]}}], "actions": [{{"id": "A1", "description": "..."}}]}}], "notes": ""}}}}

Hard rules:
- Group conditions and actions into logical decision tables (e.g., "Payment Processing", "Order Approval").
- Each condition must have id, description, and values (list of possible values).
- Each action must have id and description.
- Return strict JSON only (no markdown, no extra text).

Input type: {input_type}

Requirement text:
{requirement_text}

Code context:
{code_context}
"""

    @classmethod
    def get_prompt_rules_from_conditions_actions(
        cls,
        input_type: str,
        requirement_text: str,
        code_context: str,
        conditions_actions_result: str,
    ) -> str:
        return f"""You are a black-box testing assistant.

You will receive decision tables (conditions and actions) from step 1.
Your task is to generate rules for each decision table.

Output MUST be a JSON object with this structure:
{{{{"decision_tables": [{{"name": "table_name", "rules": [{{"rule_id": "R1", "condition_entries": ["val1", "val2", "-"], "action_entries": ["X", ""], "description": "..."}}]}}]}}}}

Hard rules:
- For each decision table, generate rules combining condition values.
- condition_entries must align with conditions array order.
- action_entries must align with actions array order; use "X" for executed, "" for not executed.
- Use "-" for don't care conditions.
- Return strict JSON only (no markdown, no extra text).

IMPORTANT: Use the following decision tables to generate rules:

{conditions_actions_result}

Input type: {input_type}

Requirement text:
{requirement_text}

Code context:
{code_context}
"""

    @classmethod
    def get_prompt_tc_from_rules(
        cls,
        input_type: str,
        requirement_text: str,
        code_context: str,
        conditions_actions_result: str,
        rules_result: str,
    ) -> str:
        return f"""You are a black-box testing assistant.

You will receive decision tables with rules from previous steps.
Your task is to generate test cases for each decision table.

Output MUST be a JSON object with this structure:
{{{{"decision_tables": [{{"name": "table_name", "test_cases": [{{"id": "TC1", "covers_rule": "R1", "inputs": {{"var1": "concrete_value1", "var2": "concrete_value2"}}, "expected": "concrete outcome description"}}]}}]}}}}

Hard rules:
- Generate one test case per rule.
- inputs must use CONCRETE VALUES that satisfy the rule's condition_entries.
- expected must describe the concrete outcome based on executed actions.
- Return strict JSON only (no markdown, no extra text).

IMPORTANT:
1) Decision tables structure:
{conditions_actions_result}

2) Decision tables with rules:
{rules_result}

Input type: {input_type}

Requirement text:
{requirement_text}

Code context:
{code_context}
"""

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

    @classmethod
    def get_prompt_ecp_bva_only(
        cls,
        input_type: str,
        requirement_text: str,
        code_context: str,
    ) -> str:
        prompt = """You are a black-box testing assistant.

You will be given either:
- requirement text, or
- a testing codebase/module snippet (may contain API endpoints, validations, constraints).

Your task is to perform Equivalence Partitioning and Boundary Value Analysis (EP_BVA) ONLY.
Output MUST be a single JSON object containing ONLY input_variables, equivalence_partitions, boundary_values, and notes.
Do NOT generate test cases in this step.

Hard rules:
- Include both valid and invalid cases. Invalid means violating at least one explicit constraint.
- Every boundary value must be derived from a specific numeric/count/time/length boundary stated or implied.
- Do NOT invent system features that are not in the input. If something is unknown, state assumptions in notes and keep tests conservative.
- Return strict JSON only (no markdown, no extra text).

Step 1 - EP_BVA Analysis:

1) Identify ALL input variables and constraints:
   - In input_variables, list variable names.
   - In notes, add a "constraints:" section describing for each variable: type, allowed range/enum, and dependencies.

2) Equivalence partitions (EP):
   - For EACH variable, create >=1 valid EP and >=1 invalid EP (if invalid inputs exist).
   - Each EP MUST include: id, description, valid, representative_values (>=1 concrete value).
   - Include robustness EP where applicable: missing/null, empty string, wrong type, out-of-range, invalid format/charset.
   - Cross-field/business rules MUST be modeled as combined EP entries (valid=false) with representative_values as a full input object demonstrating the violation.

3) Boundary value analysis (BVA):
   - For ordered types (number/length/date/time/money/count), for each variable generate rows for:
     min-1, min, min+1, max-1, max, max+1 (if applicable).
     Each boundary_values row MUST include: variable, boundary_type, value, expected_valid.
   - For enum/discrete types, include one boundary_values row per variable stating:
     boundary_type="enum_no_ordered_boundary", value=null, expected_valid=null.

4) Coverage summary:
   - Output coverage_summary with:
     total_equivalence_partitions, covered_partitions, total_boundary_conditions, covered_boundary_conditions, notes.

Input type: {input_type}

Requirement text:
{requirement_text}

Code context:
{code_context}
"""
        return prompt.format(
            input_type=input_type,
            requirement_text=requirement_text or "",
            code_context=code_context or "",
        )

    @classmethod
    def get_prompt_tc_from_ecp_bva(
        cls,
        input_type: str,
        requirement_text: str,
        code_context: str,
        ecp_bva_result: str,
    ) -> str:
        return f"""You are a black-box testing assistant.

You will receive:
1) The original requirement/code context
2) Pre-computed equivalence partitions (EP) and boundary values (BVA) from a previous analysis step

Your task is to generate test cases (TC) based on the provided ECP/BVA analysis.
Output MUST be a single JSON object containing ONLY test_cases with the same structure as shown below.
Do NOT re-generate input_variables, equivalence_partitions, or boundary_values.

Hard rules:
- Every test_case must map to at least one equivalence partition and/or boundary value (mention mapping in scenario text briefly).
- expected MUST be precise: "HTTP <code>; field=<field>; code=<error_code>" or "HTTP 201 Created".
- Return strict JSON only (no markdown, no extra text).

Step 2 - Test Case Generation:

Test cases (minimal but complete):
- Cover every valid EP at least once (success).
- Cover every invalid EP (including cross-field EP) at least once (failure).
- Cover every BVA row with expected_valid=true/false at least once with a dedicated case.
- scenario MUST explicitly list covered EP ids and boundary rows (variable+boundary_type+value).
- Each test case MUST include: id, scenario, inputs, expected.

IMPORTANT: The test_cases must be generated based on the following pre-computed ECP/BVA analysis:

{ecp_bva_result}

Input type: {input_type}

Requirement text:
{requirement_text}

Code context:
{code_context}
"""
