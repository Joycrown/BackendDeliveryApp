
from typing import Optional
from pydantic import BaseModel, EmailStr




class UserIn(BaseModel):
    full_name: str
    type: str
    email: EmailStr
    country: str
    phone_no: str
    company_name: Optional[str]
    company_url: Optional[str]
    password:str



class UserUpdate(BaseModel):
    full_name: Optional[str]
    type: Optional[str]
    phone_no: Optional [str]
    company_name: Optional[str]
    company_url: Optional[str]





class UserOut(BaseModel):

    user_id: str
    full_name: str
    type: str
    country: str
    email: str
    user_type: str
    phone_no: str
    company_name: str
    company_url: str
    is_verified:bool
    


    class Config:
        from_attributes = True