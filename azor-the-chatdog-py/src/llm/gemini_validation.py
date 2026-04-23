from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class GeminiConfig(BaseModel):
    engine: Literal["GEMINI"] = Field(default="GEMINI")
    model_name: str = Field(..., description="Gemini model name")
    gemini_api_key: str = Field(..., min_length=1, description="Google Gemini API key")
    
    @validator('gemini_api_key')
    def validate_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("GEMINI_API_KEY cannot be empty")
        return v.strip()
