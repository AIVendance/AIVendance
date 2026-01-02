from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    role: str = Field(pattern="^(student|instructor|admin)$")
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    full_name: str
