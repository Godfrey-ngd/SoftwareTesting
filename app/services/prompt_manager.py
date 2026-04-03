class PromptManager:
    PROMPTS = {
        "v1": """You are a software testing assistant.\n"
        "Given the following requirements, do:\n"
        "1) list input variables\n"
        "2) derive equivalence partitions (valid/invalid)\n"
        "3) derive boundary values\n"
        "4) produce concrete test cases with expected results\n"
        "Return in JSON format.\n\n"
        "Requirement: {requirement_text}\n""",
        "v2": """You are a software testing assistant.\n"
        "Return a JSON object with keys: input_variables, equivalence_partitions, "
        "boundary_values, test_cases, notes.\n"
        "Each equivalence partition must include id, description, valid.\n"
        "Each boundary item must include variable and values.\n"
        "Each test case must include id, scenario, inputs, expected.\n\n"
        "Requirement: {requirement_text}\n""",
        "v3": """You are a software testing assistant.\n"
        "Return a JSON object with keys: input_variables, equivalence_partitions, "
        "boundary_values, test_cases, notes.\n"
        "Before finalizing, self-check for missing boundaries, invalid cases, and contradictions.\n"
        "If any issues are found, fix them and mention them in notes.\n\n"
        "Requirement: {requirement_text}\n""",
    }

    @classmethod
    def get_prompt(cls, version: str, requirement_text: str) -> str:
        prompt = cls.PROMPTS.get(version, cls.PROMPTS["v1"])
        return prompt.format(requirement_text=requirement_text)
