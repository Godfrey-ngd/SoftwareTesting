from app.services.prompt_manager import PromptManager


def test_get_prompt_v4_includes_switch_fields():
    prompt = PromptManager.get_prompt(
        version="v4",
        input_type="requirements",
        technique="ep_bva",
        requirement_text="A system with rule X.",
        code_context="",
    )

    assert "Input type:" in prompt
    assert "Technique:" in prompt
    assert "requirements" in prompt
    assert "ep_bva" in prompt


def test_get_prompt_v4_decision_table_includes_table_keys():
    prompt = PromptManager.get_prompt(
        version="v4",
        input_type="requirements",
        technique="decision_table",
        requirement_text="Some rules.",
        code_context="",
    )
    assert "\"conditions\"" in prompt
    assert "\"actions\"" in prompt
    assert "\"rules\"" in prompt


def test_get_prompt_v4_state_transition_includes_suitability_check():
    prompt = PromptManager.get_prompt(
        version="v4",
        input_type="requirements",
        technique="state_transition",
        requirement_text="Some single-submit validation rules.",
        code_context="",
    )
    assert "Suitability detection" in prompt


def test_get_prompt_v1_backwards_compat_formatting():
    prompt = PromptManager.get_prompt(
        version="v1",
        input_type="requirements",
        technique="ep_bva",
        requirement_text="Hello",
        code_context="ignored",
    )
    assert "Requirement:" in prompt
    assert "Hello" in prompt
