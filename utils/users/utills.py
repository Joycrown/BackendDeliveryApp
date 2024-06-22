from passlib.context import CryptContext
from config.environ import settings
import os
import secrets
from PIL import Image

if settings.production_server == "false" :
    server_host = settings.local_server_host
else: 
    server_host = settings.production_server_host



PROFILE_PICTURES_DIR = "staticfiles/profile_pictures"
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash (password: str) :
    return pwd_context.hash(password)



def verify (plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)



async def profile_picture_upload(file):
    FILEPATH = "./staticfiles/profile_pictures/"
    filename = file.filename
    extension =filename.split(".")[1]
    if extension not in [ 'jpg', 'jpeg','png']:
        raise ValueError("Invalid image type")
    token_name = secrets.token_hex(10)+'.'+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name,'wb') as file:
        file.write(file_content)
    img = Image.open(generated_name)
    # Resize the image to be no wider than 192 pixels or no higher than 192 pixels. 
    img =img.resize(size=((250,250)))
    
    # Save the image as a jpeg at quality of 95 under that size 
    img.save(generated_name,quality=150)
    file.close()
    
    file_url = server_host + generated_name[1:]
    return file_url
