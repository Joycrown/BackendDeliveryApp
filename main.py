from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apps.serviceProvider.orders import serviceProviderBudget
from models.users.usersModel import Users
from config.database import  get_db
from sqlalchemy.orm import Session
from apps.users import main, auth
from apps.users.orders import usersBudget, usersQuote
from apps.serviceProvider import serviceProAuth, serviceProviderMain
from apps.serviceProvider.orders import serviceProviderQuote
from apps.escrowPayment import payment
from apps.verification import verification
from apps.chat import chat
import socketio
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="Delivery Transport Connect App APIs",
    description="This is a custom API documentation.",
    version="1.0.0",
    
)

app.mount("/staticfiles", StaticFiles(directory="staticfiles"), name="staticfiles")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length"],
    max_age=600,
)




app.include_router(main.router)
app.include_router(auth.router)
app.include_router(serviceProviderMain.router)
app.include_router(payment.router)
app.include_router(serviceProviderBudget.router)
app.include_router(serviceProviderQuote.router)
app.include_router(usersQuote.router)
app.include_router(usersBudget.router)
app.include_router(verification.router)
app.include_router(chat.router)



# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_room(sid, data):
    room = data['room']
    sio.enter_room(sid, room)
    print(f"Client {sid} joined room {room}")

@sio.event
async def leave_room(sid, data):
    room = data['room']
    sio.leave_room(sid, room)
    print(f"Client {sid} left room {room}")

@sio.event
async def send_message(sid, data):
    room = data['room']
    message = data['message']
    await sio.emit('new_message', {'message': message}, room=room, skip_sid=sid)

# Include your existing routes here

# Use the Socket.IO app as the main application
app = socket_app
