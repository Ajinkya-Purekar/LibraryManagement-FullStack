from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRegister(BaseModel):
    username:str = Field(..., min_length=2, max_length=50)
    email:EmailStr = Field(..., max_length=255)
    password:str = Field(..., min_length=8)
    role: str = "USER"


    @validator("password")
    def validate_password(cls, value):
        if " " in value:
            raise ValueError("Password must not contain spaces")
        
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"[0-9]",value):
            raise ValueError("Password must conatin at least one number")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"