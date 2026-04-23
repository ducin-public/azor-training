from pydantic import BaseModel, Field, validator
from typing import Literal


class OpenRouterConfig(BaseModel):
    engine: Literal["OPENROUTER"] = Field(default="OPENROUTER")
    model_name: str = Field(..., description="OpenRouter model name")
    openrouter_api_key: str = Field(..., min_length=1, description="OpenRouter API key")

    @validator('openrouter_api_key')
    def validate_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("OPENROUTER_API_KEY cannot be empty")
        return v.strip()
