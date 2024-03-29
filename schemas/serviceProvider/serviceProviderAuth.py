from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from config.database import Base




class ServiceProviderLogin(BaseModel):
    email: str
    password: str


class ServiceProviderToken(BaseModel):
    access_token: str
    token_type: str


class ServiceProviderTokenData(BaseModel):
    id: str
    email: EmailStr



class ServiceProviderPasswordResetTokenData(BaseModel):
    email: EmailStr

class CurrentServiceProvider(BaseModel):
    user_id: str
    full_name: str
    type: str
    email: str
    is_verified: bool
    phone_no: int
    company_name: str
    company_url: str



class ServiceProviderEmailReset(BaseModel):
    email: EmailStr


class  ServiceProviderResetPassword(BaseModel):
    new_password:str
    token : str

class ServiceProviderUpdatePassword(BaseModel):
    current_password: str
    new_password: str

   