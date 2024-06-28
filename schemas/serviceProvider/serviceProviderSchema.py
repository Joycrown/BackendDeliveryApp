
from typing import Optional
from pydantic import BaseModel, EmailStr




class ServiceProviderIn(BaseModel):

    full_name: str
    type: str
    email: EmailStr
    country: str
    city: str
    street_address: str
    phone_no: int
    service_offered: str
    company_name: Optional[str]
    company_url: Optional[str]
    password:str
    gender: str



class ServiceProviderUpdate(BaseModel):

    full_name: Optional[str]
    phone_no: Optional [str]
    company_name: Optional[str]
    company_url: Optional[str]
    service_offered: Optional[str]
    city: Optional[str]
    country: Optional[str]
    street_address:Optional[str]



class ServiceProviderOut(BaseModel):

    service_provider_id: str
    full_name: str
    type: str
    email: str
    phone_no: str
    company_name: str
    company_url: str
    service_offered:str
    is_verified: bool
    stripe_account:str
    rating: str
    profile_picture:str
    gender: str
    city: str
    user_type: str
    stripeId_status: bool
    email_is_verified: bool
    security_question_status:bool
    street_address: str
    country: str

    # created_at: datetime


    class Config:
        from_attributes = True