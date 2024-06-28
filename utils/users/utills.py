from passlib.context import CryptContext
from config.environ import settings
import os
import secrets
from PIL import Image,ImageOps

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
    extension = filename.split(".")[-1].lower()
    if extension not in ['jpg', 'jpeg', 'png']:
        raise ValueError("Invalid image type")
    
    token_name = secrets.token_hex(10) + '.' + extension
    generated_name = os.path.join(FILEPATH, token_name)
    
    file_content = await file.read()
    with open(generated_name, 'wb') as f:
        f.write(file_content)
    
    with Image.open(generated_name) as img:
        # Convert image to RGB if it's not
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Apply some enhancements
        img = ImageOps.autocontrast(img, cutoff=0.5)
        img = ImageOps.equalize(img)
        
        # Set target size (increased for higher quality)
        target_size = (500, 500)
        
        # Resize image
        img = ImageOps.contain(img, target_size, method=Image.LANCZOS)
        
        # Create a new image with white background
        new_img = Image.new("RGB", target_size, (255, 255, 255))
        
        # Paste the resized image onto the center of the new image
        paste_x = (target_size[0] - img.width) // 2
        paste_y = (target_size[1] - img.height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        # Save the image
        new_img.save(generated_name, format='JPEG', quality=95, optimize=True, progressive=True)
    
    file_url = server_host + generated_name[1:]
    return file_url
