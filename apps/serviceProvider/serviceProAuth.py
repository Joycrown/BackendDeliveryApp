# from fastapi import APIRouter, Depends, HTTPException, status, Form
# from fastapi.security.oauth2 import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session 
# from config.database import get_db
# from models.users.usersModel import ServiceProvider
# from utils.users.utills import verify, hash
# from apps.serviceProvider.serviceProviderOauth import get_current_user,create_tokens,verify_refresh_token,create_password_reset_token,verify_access_token,verify_access_token_password_reset
# from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut
# from schemas.serviceProvider.serviceProviderAuth import ServiceProviderUpdatePassword
# from schemas.user.UserAuth import CurrentUser,UpdatePassword, EmailReset,ResetPassword
# from typing import Annotated

# router = APIRouter(
#     tags=["Service Provider Auth"]
# )


# """
# service Provider Login route

# """
# @router.post('/service_provider/login', response_model=dict)
# def login(
#     details: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(ServiceProvider).filter(ServiceProvider.email == details.username).first()
#     if not user or not verify(details.password, user.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#     access_token, refresh_token = create_tokens(user)
#     return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "current_user": user.full_name}




# """
# To refresh token
# """

# @router.post('/provider/refresh', response_model=dict)
# def refresh_token(
#     refresh_token: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     token_data = verify_refresh_token(refresh_token)
#     user = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == token_data.id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

#     access_token, new_refresh_token = create_tokens(user)
#     return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer", "current_user": user.full_name}





# """
# To Update User's Password
# """
# @router.put('/password/service_provider')
# async def update_password(
#     password_data: ServiceProviderUpdatePassword,
#     current_user: ServiceProvider = Depends(get_current_user),
#     db: Session = Depends(get_db),
    
# ):
 
#     # Verify the current password
#     if not verify(password_data.current_password, current_user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect current password",
#         )

#     # Hash and update the new password
#     hashed_password = hash(password_data.new_password)
#     current_user.password = hashed_password
#     # Commit the changes to the database
#     db.commit()

#     return {"message": "Password updated successfully"}



# """
# To get current user
# """

# @router.get('/current_service_provider',response_model=ServiceProviderOut)
# async def get_current_authenticated_user(current_user: Annotated[CurrentUser, Depends(get_current_user)]):
#     if current_user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No servicer provider with: me found")
#     return current_user




# """
# User route
# To reset users password
# """

# @router.post('/forgot_password/service_provider')
# async def password_reset(email: EmailReset, db: Session = Depends(get_db)):
#     email_exist = db.query(ServiceProvider).filter(ServiceProvider.email == email.email).first()
#     if not email_exist:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Service Provider with this email not found"
#         )
    
#     reset_token = create_password_reset_token(data={ "email": email_exist.email})
#     reset_link = f"https://localhost/{reset_token}"


#     return reset_link



# """
# User route
# To set new user's password
# """
# @router.put('/set_password/service_provider' )
# async def password(data: ResetPassword, db: Session = Depends(get_db)):
  
#   credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
#     detail=f"couldnt validate credentials", headers={"WWW-Authenticate":"Bearer"})
#   user =  verify_access_token_password_reset(data.token,credentials_exception)
#   print(user)
#   user_update= db.query(ServiceProvider).filter(ServiceProvider.email== user.email)
  
#   if not user_update:
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="User not found"
#     )
#   update_password = hash(data.new_password)
#   user_update.password = update_password
#   db.commit()
#   return {"message": "Password reset successful"}
