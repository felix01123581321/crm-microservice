from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class LeadBase(BaseModel):
    name: str
    email: EmailStr
    status: str = "new"
    url: Optional[str] = None

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    pass

class Lead(LeadBase):
    id: int

    class Config:
        orm_mode = True 