from pydantic import BaseModel, EmailStr, Field

# ---------- User Schemas ----------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

# ---------- Token Schema ----------

class Token(BaseModel):
    access_token: str
    token_type: str

