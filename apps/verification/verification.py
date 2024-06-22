from fastapi import APIRouter, Depends, HTTPException, status, UploadFile,File
from sqlalchemy.orm import Session 
from config.database import get_db
from models.users.usersModel import ServiceProvider,Users
from utils.users.utills import verify, hash
from schemas.user.usersSchema import UserOut
from schemas.verification.verificationSchema import SecurityQuestion,SecurityQuestionsUpdate,SecurityCheck,SecurityAnswer,StripeIn
from schemas.serviceProvider.serviceProviderSchema import ServiceProviderOut
from apps.users.auth import get_current_user
from utils.users.email import verify_account_email
from utils.users.utills import profile_picture_upload
import random
from typing import Union, List
from datetime import datetime, timedelta



router = APIRouter(
    tags=["Verification"]
)



def generate_otp():
    otp = str(random.randint(100000, 999999))
    expiry_time = datetime.utcnow() + timedelta(minutes=10)  # OTP expires in 10 minutes
    return otp, expiry_time


""""
Email verification

"""

@router.post('/account/verification')
async def verify_account(
    current_user: Union[UserOut, ServiceProviderOut] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
      if current_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already verified")
      
      otp, expiry_time = generate_otp()
      
      user = db.query(Users).filter(Users.user_id == current_user.user_id).first()
      if not user:
        # If not a user, check if the email belongs to a service provider
        service_provider = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()
        if not service_provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user = service_provider
      
      user.otp = otp
      user.otp_expiry=expiry_time
      
      await verify_account_email("Account Verification", user.email, {
          "title": "Account Verification",
          "name": user.full_name,
          "otp": otp
      })
      
      db.commit()
      return {"message": "Account verification email sent successfully"}
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))


""""
Verification of OTP

"""

@router.patch('/account/verify_otp')
async def verify_otp(otp:int, current_user: Union[UserOut, ServiceProviderOut] = Depends(get_current_user), db: Session = Depends(get_db)):
  if current_user.is_verified:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already verified")
  
  user = db.query(Users).filter(Users.user_id == current_user.user_id).first()
  if not user:
    # If not a user, check if the email belongs to a service provider
    service_provider = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()
    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user = service_provider
  if user.otp != otp:
      raise HTTPException(status_code=400, detail="Invalid OTP")
  
  if datetime.utcnow() > user.otp_expiry:
      raise HTTPException(status_code=400, detail="OTP has expired")
  

  user.email_is_verified = True
  user.otp = None
  user.otp_expiry = None
  db.commit()

  db.refresh(user)
  
  return {"message": "Account verified successfully"}
  

"""""
Security Question
"""""

    
@router.put("/account/security-questions")
def update_security_questions(
    security_questions: SecurityQuestionsUpdate,
    db: Session = Depends(get_db),
    current_user: Union[Users,ServiceProviderOut] = Depends(get_current_user)
):
    try:
      if len(security_questions.security_questions) != 2:
          raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly 3 security questions and answers are required"
        )
      user = db.query(Users).filter(Users.user_id == current_user.user_id).first()
      if not user:
        # If not a user, check if the email belongs to a service provider
        service_provider = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()
        if not service_provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user = service_provider
      # Update security questions and answers
      user.security_question_1 = security_questions.security_questions[0].question
      user.security_answer_1 = hash(security_questions.security_questions[0].answer)
      user.security_question_2 = security_questions.security_questions[1].question
      user.security_answer_2 = hash(security_questions.security_questions[1].answer)
      user.security_question_status = True
      db.commit()
      
      return {"message": "Security questions updated successfully"}
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))



""""
security check
"""""

@router.patch("/account/security-check")
def security_check_and_stripe_update(
    security_check: SecurityCheck,
    db: Session = Depends(get_db),
    current_user: Union[Users,ServiceProviderOut] = Depends(get_current_user)
):
    try:
      if len(security_check.answers) != 2:
          raise HTTPException(
              status_code=status.HTTP_400_BAD_REQUEST,
              detail="Exactly 2 security answers are required"
          )

      user = db.query(Users).filter(Users.user_id == current_user.user_id).first()
      if not user:
        # If not a user, check if the email belongs to a service provider
        service_provider = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()
        if not service_provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user = service_provider

      # Verify each answer
      correct_answers = 0
      for answer in security_check.answers:
          if answer.question == user.security_question_1 and verify(answer.answer, user.security_answer_1):
              correct_answers += 1
          elif answer.question == user.security_question_2 and verify(answer.answer, user.security_answer_2):
              correct_answers += 1
          

      if correct_answers == 2:
          if security_check.stripe_id:
             service_provider.stripe_account =security_check.stripe_id
             return {"message": "Stripe Id Updated successfully"}
          return {"message": "Security check passed"}
      else:
          raise HTTPException(
              status_code=status.HTTP_400_BAD_REQUEST,
              detail="Incorrect answers provided"
          )
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))
    



"""""
to fetch the security question of current user

"""""



@router.get("/account/my_security_questions", response_model=List[SecurityQuestion])
def get_security_questions(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    try:
       
        user = db.query(Users).filter(Users.user_id == current_user.user_id).first()
        if not user:
        # If not a user, check if the email belongs to a service provider
            service_provider = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()
            if not service_provider:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user = service_provider

        questions = [
            SecurityQuestion(question=user.security_question_1),
            SecurityQuestion(question=user.security_question_2),
        ]

        return questions
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))



""""
To update profile picture

"""


@router.post("/account/profile_picture")
async def update_profile_picture(
    profile_picture: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Union[ServiceProviderOut,UserOut] = Depends(get_current_user)
):
    try:
        user = db.query(Users).filter(Users.user_id == current_user.user_id).first()
        if not user:
        # If not a user, check if the email belongs to a service provider
            service_provider = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == current_user.service_provider_id).first()
            if not service_provider:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user = service_provider

        profile_picture_link = await profile_picture_upload(profile_picture)
        print(profile_picture_link)
        user.profile_picture=profile_picture_link
        db.commit()
        return {"message": "Profile Picture Updated"}
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))