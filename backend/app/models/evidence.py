from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source: str = Field(..., min_length=1)
    method: str = Field(..., min_length=1)
    observed_value: str = Field(..., min_length=1)
    expected_value: str = Field(..., min_length=1)
    command_hint: str | None = None
    notes: str | None = None
