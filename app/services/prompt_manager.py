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
    }

    @classmethod
    def get_prompt(cls, version: str, requirement_text: str) -> str:
        prompt = cls.PROMPTS.get(version, cls.PROMPTS["v1"])
        return prompt.format(requirement_text=requirement_text)
