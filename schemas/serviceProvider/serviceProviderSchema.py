
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
    type: Optional[str]
    phone_no: Optional [int]
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
    phone_no: int
    company_name: str
    company_url: str
    service_offered:str
    is_verified: bool
    rating: str
    gender: str
    city: str
    user_type: str
    is_verified: bool
    street_address: str
    country: str

    # created_at: datetime


    class Config:
        from_attributes = True