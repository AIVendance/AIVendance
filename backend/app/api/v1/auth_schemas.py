from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    role: str = Field(pattern="(?i)^(student|instructor|admin)$", description="User role (case-insensitive)")
    user_id: str = Field(description="University ID for students, username for instructors/admins")
    password: str = Field(description="User password")
    
    @field_validator('role')
    @classmethod
    def normalize_role(cls, v):
        """Convert role to lowercase for consistent processing"""
        return v.lower() if v else v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    full_name: str
