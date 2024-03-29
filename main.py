from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models.users.usersModel import Users
from config.database import  get_db
from sqlalchemy.orm import Session
from apps.users import main, auth
from apps.serviceProvider import serviceProAuth, serviceProviderMain
from apps.orders import orderMain, quote



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
app.include_router(serviceProAuth.router)
app.include_router(orderMain.router)
app.include_router(quote.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/testing')
def test_db(db: Session = Depends(get_db)):
  user= db.query(Users).all()
  return user
