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



app = FastAPI()


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
# app.include_router(serviceProAuth.router)
app.include_router(serviceProviderBudget.router)
app.include_router(serviceProviderQuote.router)
app.include_router(usersQuote.router)
app.include_router(usersBudget.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/testing')
def test_db(db: Session = Depends(get_db)):
  user= db.query(Users).all()
  return user
