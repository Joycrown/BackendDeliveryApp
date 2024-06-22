from fastapi import  Depends,HTTPException,status,APIRouter
import random
from models.users.usersModel import Users, ServiceProvider
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderIn,ServiceProviderOut,ServiceProviderUpdate
from config.database import get_db
from sqlalchemy.orm import Session 
from utils.users.utills import hash
from typing import List
from utils.users.email import account_purchased
from .serviceProviderOauth import get_current_user




router= APIRouter(
    tags=["Service Provider"]
)


"""
Service Provider sign up

"""
def generate_custom_id(prefix: str, n_digits: int) -> str:
    """Generate a custom ID with a given prefix and a certain number of random digits"""
    random_digits = ''.join([str(random.randint(0,9)) for i in range(n_digits)])
    return f"{prefix}{random_digits}"


@router.post('/service_provider/signup', status_code=status.HTTP_201_CREATED, response_model=ServiceProviderOut)
async def new_user (user:ServiceProviderIn, db: Session = Depends(get_db)):
    check_email= db.query(ServiceProvider).filter(ServiceProvider.email == user.email).first()
    check_phone= db.query(ServiceProvider).filter(ServiceProvider.phone_no == user.phone_no).first()
    if check_email : 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Email already in use")
    if check_phone : 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Phone no already in use")
    hashed_password = hash(user.password)
    user.password = hashed_password
    custom_id = generate_custom_id("SP", 5)
    new_account = ServiceProvider(service_provider_id=custom_id, **user.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
#     await account_purchased("Registration Successful", user.email, {
#     "title": "Account Purchase Successful",
#     "name": user.full_name,
    
#   })
    return  new_account

"""
To fetch all users
"""
@router.get('/service_provider',response_model=List[ServiceProviderOut])
async def get_all_user( db: Session = Depends(get_db)):
  user_details = db.query(ServiceProvider).all()
  return user_details

"""
To fetch a single user
"""
@router.get('/service_provider/{id}',response_model=ServiceProviderOut)
async def get_user(id: str, db: Session = Depends(get_db),current_user: ServiceProviderOut = Depends(get_current_user)):
  user_details = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id== id).first()
  if not user_details:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user with: {id} found")
  return user_details




"""
To Update a single user
"""

@router.patch('/update/service_provider', response_model=ServiceProviderOut)
async def update_service_provider(
    user_update: ServiceProviderUpdate,
    db: Session = Depends(get_db),
    current_user: ServiceProviderOut = Depends(get_current_user)
):
    existing_user = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {current_user.service_provider_id} not found")

    # Check if the new phone number is already in use
    if user_update.phone_no and user_update.phone_no != existing_user.phone_no:
        existing_phone = db.query(ServiceProvider).filter(ServiceProvider.phone_no == user_update.phone_no).first()
        if existing_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Phone number {user_update.phone_no} is already in use")

    # Update user details
    for field, value in user_update.dict().items():
        setattr(existing_user, field, value)

    db.commit()
    db.refresh(existing_user)

    return existing_user

