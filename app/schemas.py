from pydantic import BaseModel, EmailStr, validator

class CustomerIn(BaseModel):
    name: str
    email: EmailStr
    age: int

    @validator("age")
    def age_must_be_18(cls, v):
        if v < 18:
            raise ValueError("Age must be 18 or above")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
