from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from config.database import Base




class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str
    email: EmailStr



class PasswordResetTokenData(BaseModel):
    email: EmailStr

class CurrentUser(BaseModel):
    user_id: str
    full_name: str
    type: str
    email: str
    phone_no: int
    company_name: str
    company_url: str



class EmailReset(BaseModel):
    email: EmailStr


class  ResetPassword(BaseModel):
    new_password:str
    token : str

class UpdatePassword(BaseModel):
    current_password: str
    new_password: str

   