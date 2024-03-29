from fastapi_mail import  MessageSchema, FastMail
from config.email import conf



# Send Email for successful signup
async def account_purchased(subject: str, email_to: str, body:dict):
    message= MessageSchema(
        subject=subject,
        recipients= [email_to],
        template_body= body,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="accountSignup.html")



# Send Mail to reset password
async def password_rest_email(subject: str, email_to: str, body:dict):
    message= MessageSchema(
        subject=subject,
        recipients= [email_to],
        template_body= body,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_reset.html")