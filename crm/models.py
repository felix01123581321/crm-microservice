from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional

class LeadBase(BaseModel):
    name: str
    email: EmailStr
    status: str = "new"
    url: Optional[str] = None

    @field_validator('email')
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower()

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    model_config = ConfigDict(from_attributes=True) 