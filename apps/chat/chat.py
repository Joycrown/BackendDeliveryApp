from fastapi import FastAPI, Depends, APIRouter,HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.chat.chatSchema import ChatRoomCreate,MessageCreate,MessageResponse,ChatRoomResponse
from models.users.usersModel import ChatRoom,Messages,Users,ServiceProvider
from typing import List, Union
from apps.users.auth import get_current_user
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut
from schemas.user.usersSchema import UserOut
from fastapi_socketio import SocketManager


router = APIRouter(
    tags=["Chat Room"]
)


socket_manager = SocketManager(app=router, mount_location='/ws')


@router.post("/create_chat_room/", response_model=ChatRoomResponse)
async def create_chat_room(chat_room: ChatRoomCreate, db: Session = Depends(get_db), current_user: Union[UserOut, ServiceProviderOut] = Depends(get_current_user)):
    sender_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.service_provider_id
    sender_type = "user" if hasattr(current_user, 'user_id') else "service_provider"

    # Validate receiver exists
    if chat_room.receiver_type == "user":
        receiver = db.query(Users).filter(Users.user_id == chat_room.receiver_id).first()
    else:
        receiver = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == chat_room.receiver_id).first()

    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )

    db_chat_room = ChatRoom(
        sender_id=sender_id,
        sender_type=sender_type,
        receiver_id=chat_room.receiver_id,
        receiver_type=chat_room.receiver_type
    )
    db.add(db_chat_room)
    db.commit()
    db.refresh(db_chat_room)

    sender_details = UserOut.model_validate(current_user) if sender_type == "user" else ServiceProviderOut.model_validate(current_user)
    receiver_details = UserOut.model_validate(receiver) if chat_room.receiver_type == "user" else ServiceProviderOut.model_validate(receiver)

    return ChatRoomResponse(
        room_id=db_chat_room.room_id,
        sender_id=db_chat_room.sender_id,
        sender_type=db_chat_room.sender_type,
        receiver_id=db_chat_room.receiver_id,
        receiver_type=db_chat_room.receiver_type,
        created_at=db_chat_room.created_at,
        sender=sender_details,
        receiver=receiver_details
    )



@router.post("/send_message/", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: Session = Depends(get_db),current_user: Union[UserOut, ServiceProviderOut] = Depends(get_current_user)):
    sender_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.service_provider_id
    sender_type = "user" if hasattr(current_user, 'user_id') else "service_provider"
    # check if chatroom exist
    check_room= db.query(ChatRoom).filter(ChatRoom.room_id == message.chat_room_id).first()
    if not check_room:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    if sender_id != check_room.sender_id and sender_id != check_room.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to send messages in this chat room"
        )
    db_message = Messages(sender_id=sender_id,sender_type=sender_type,**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    sender_details = UserOut.model_validate(current_user) if sender_type == "user" else ServiceProviderOut.model_validate(current_user)
    await socket_manager.emit('message', {'content': message.content, 'timestamp': str(db_message.timestamp)}, room=message.chat_room_id)
    return MessageResponse(
        message_id=db_message.message_id,
        chat_room_id=db_message.chat_room_id,
        sender_id=db_message.sender_id,
        content=db_message.content,
        timestamp=db_message.timestamp,
        sender=sender_details
    )



@router.get("/get_messages/{chat_room_id}", response_model=List[MessageResponse])
async def get_messages(chat_room_id: int, db: Session = Depends(get_db),current_user: Union[UserOut, ServiceProviderOut] = Depends(get_current_user)):
    sender_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.service_provider_id
    room = db.query(ChatRoom).filter(ChatRoom.room_id == chat_room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    if sender_id != room.sender_id and sender_id != room.receiver_id :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view messages in this chat room"
        )
    messages = db.query(Messages).filter_by(chat_room_id=chat_room_id).all()
    message_responses = []

    for message in messages:
        # Fetch the sender details
        if message.sender_type == "user":
            sender = db.query(Users).filter(Users.user_id == message.sender_id).first()
            sender_details = UserOut.model_validate(sender)
        else:
            sender = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == message.sender_id).first()
            sender_details = ServiceProviderOut.model_validate(sender)

        message_responses.append(MessageResponse(
            message_id=message.message_id,
            chat_room_id=message.chat_room_id,
            sender_id=message.sender_id,
            content=message.content,
            timestamp=message.timestamp,
            sender=sender_details
        ))

    return message_responses



@router.get("/my_chat_rooms/", response_model=List[ChatRoomResponse])
async def get_my_chat_rooms(db: Session = Depends(get_db), current_user: Union[UserOut, ServiceProviderOut] = Depends(get_current_user)):
    user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.service_provider_id
    user_type = "user" if hasattr(current_user, 'user_id') else "service_provider"

    # Query chat rooms where the current user is either the sender or the receiver
    chat_rooms = db.query(ChatRoom).filter(
        (ChatRoom.sender_id == user_id) | 
        (ChatRoom.receiver_id == user_id)
    ).all()

    chat_room_responses = []

    for chat_room in chat_rooms:
        # Fetch the sender details
        if chat_room.sender_type == "user":
            sender = db.query(Users).filter(Users.user_id == chat_room.sender_id).first()
            sender_details = UserOut.model_validate(sender)
        else:
            sender = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == chat_room.sender_id).first()
            sender_details = ServiceProviderOut.model_validate(sender)

        # Fetch the receiver details
        if chat_room.receiver_type == "user":
            receiver = db.query(Users).filter(Users.user_id == chat_room.receiver_id).first()
            receiver_details = UserOut.model_validate(receiver)
        else:
            receiver = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == chat_room.receiver_id).first()
            receiver_details = ServiceProviderOut.model_validate(receiver)

        chat_room_responses.append(ChatRoomResponse(
            room_id=chat_room.room_id,
            sender_id=chat_room.sender_id,
            sender_type=chat_room.sender_type,
            receiver_id=chat_room.receiver_id,
            receiver_type=chat_room.receiver_type,
            created_at=chat_room.created_at,
            sender=sender_details,
            receiver=receiver_details
        ))

    return chat_room_responses


@socket_manager.on('join')
async def join_room(sid, message):
    await socket_manager.enter_room(sid, message['room'])

@socket_manager.on('leave')
async def leave_room(sid, message):
    await socket_manager.leave_room(sid, message['room'])

