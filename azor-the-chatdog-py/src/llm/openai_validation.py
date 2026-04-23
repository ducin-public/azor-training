from pydantic import BaseModel, Field, validator
from typing import Literal

class OpenAIConfig(BaseModel):
    engine: Literal["OPENAI"] = Field(default="OPENAI")
    model_name: str = Field(..., description="OpenAI model name")
    openai_api_key: str = Field(..., min_length=1, description="OpenAI API key")

    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("OPENAI_API_KEY cannot be empty")
        return v.strip()
