from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    status: str = "ok"
    data: dict
    meta: dict = Field(default_factory=dict)
