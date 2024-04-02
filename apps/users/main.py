from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import Users
from schemas.user.usersSchema import UserIn, UserOut, UserUpdate
from config.database import get_db
from sqlalchemy.orm import Session 
from utils.users.utills import hash
from utils.users.email import account_purchased
from typing import List
from .oauth import get_current_user




router= APIRouter(
    tags=["Users"]
)


"""
User sign up

"""
def generate_custom_id(prefix: str, n_digits: int) -> str:
  """Generate a custom ID with a given prefix and a certain number of random digits"""
  random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
  return f"{prefix}{random_digits}"


@router.post('/user/signup/', status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def new_user (user:UserIn, db: Session = Depends(get_db)):
    check_email= db.query(Users).filter(Users.email == user.email).first()
    if check_email : 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Email already in use")
    hashed_password = hash(user.password)
    user.password = hashed_password
    custom_id = generate_custom_id("FR", 5)
    new_account = Users(user_id=custom_id, **user.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
  #   await account_purchased("Registration Successful", user.email, {
  #   "title": "Account Purchase Successful",
  #   "name": user.full_name,
    
  # })
    return  new_account

"""
To fetch all users
"""
@router.get('/user',response_model=List[UserOut])
async def get_all_user( db: Session = Depends(get_db)):
  user_details = db.query(Users).all()
  return user_details

"""
To fetch a single user
"""
@router.get('/user/{id}',response_model=UserOut)
async def get_user(id: str, db: Session = Depends(get_db),current_user: UserOut = Depends(get_current_user)):
  user_details = db.query(Users).filter(Users.user_id == id).first()
  if not user_details:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user with: {id} found")
  return user_details


"""
To Update a single user
"""

@router.put('/user/{user_id}', response_model=UserOut)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    existing_user = db.query(Users).filter(Users.user_id == user_id).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

    # Update user details
    for field, value in user_update.dict().items():
        setattr(existing_user, field, value)

    db.commit()
    db.refresh(existing_user)

    return existing_user


"To delete all users"
@router.delete("/users")
async def delete_order( db: Session = Depends(get_db)):
    # Check if the order exists
    users = db.query(Users).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user found")

    # Check if the current user is the owner of the order (optional)
  
    # Delete the order from the database
    for user in users:
      db.delete(user)
    db.commit()

    return {"message": f"Users deleted successfully"}



