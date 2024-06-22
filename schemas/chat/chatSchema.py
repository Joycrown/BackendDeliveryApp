from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Union
from schemas.user.usersSchema import UserOut
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut




class ChatRoomCreate(BaseModel):
  receiver_id: str
  receiver_type: str




class MessageCreate(BaseModel):
  chat_room_id: int
  content: str


class MessageResponse(BaseModel):
  content: str
  timestamp: str


class ChatRoomResponse(BaseModel):
  room_id: int
  sender_id: str
  sender_type: str
  receiver_id: str
  receiver_type: str
  created_at: datetime
  sender: Union[UserOut, ServiceProviderOut]
  receiver: Union[UserOut, ServiceProviderOut]


  class Config:
    from_attributes = True


class MessageResponse(BaseModel):
    message_id: int
    chat_room_id: int
    sender_id: str
    content: str
    timestamp: datetime
    sender: Union[UserOut, ServiceProviderOut]

    class Config:
        from_attributes = True