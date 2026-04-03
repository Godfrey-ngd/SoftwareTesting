from fastapi import APIRouter, HTTPException

from app.schemas.output import GenerateRequest, GenerateResponse
from app.services.llm_client import LLMClient
from app.services.prompt_manager import PromptManager

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    prompt = PromptManager.get_prompt(request.prompt_version, request.requirements)
    client = LLMClient()

    try:
        data = client.generate_json(
            prompt=prompt,
            model=request.model,
            temperature=request.temperature,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="LLM request failed") from exc

    return GenerateResponse(**data)
