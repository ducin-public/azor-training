from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
import os

class LlamaConfig(BaseModel):
    engine: Literal["LLAMA"] = Field(default="LLAMA")
    model_name: str = Field(..., description="Llama model name")
    llama_model_path: str = Field(..., description="Path to the .gguf model file")
    llama_gpu_layers: int = Field(default=1, ge=0, description="Number of GPU layers")
    llama_context_size: int = Field(default=2048, ge=1, description="Context size")
    
    @validator('llama_model_path')
    def validate_model_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Model file does not exist: {v}")
        if not v.endswith('.gguf'):
            raise ValueError("Model file must have the .gguf extension")
        return v
