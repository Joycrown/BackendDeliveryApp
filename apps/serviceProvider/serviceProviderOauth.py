from jose import JWTError, jwt
from datetime import datetime, timedelta
from config.database import get_db
from schemas.user.UserAuth import TokenData,PasswordResetTokenData
from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.users.usersModel import Users, ServiceProvider
from config.environ import settings



SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = settings.reset_password_token_expire_minutes


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='service_provider/login/')

def create_access_token(data: dict):
    to_encode= data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token_password_reset(token: str, credentials_exception):
    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # id = payload.get("user_id")
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = PasswordResetTokenData(email=email)
        return token_data
    except JWTError:
        raise credentials_exception
    

def verify_access_token(token: str, credentials_exception):
    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("service_provider_id")
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(id=id, email=email)
        return token_data
    except JWTError:
        raise credentials_exception

def create_tokens(user: ServiceProvider):
    to_encode = {"service_provider_id": user.service_provider_id, "email": user.email}
    access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": access_expire})
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    to_encode.update({"exp": refresh_expire})
    refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return access_token, refresh_token


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("service_provider_id")
        email = payload.get("email")
        if user_id is None or email is None:
            raise JWTError
        token_data = TokenData(id=user_id, email=email)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return token_data
    


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = verify_access_token(token, credentials_exception)
    current_user = db.query(ServiceProvider).filter(ServiceProvider.service_provider_id == user.id).first()
    return current_user


def create_password_reset_token(data: dict):
    to_encode= data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt