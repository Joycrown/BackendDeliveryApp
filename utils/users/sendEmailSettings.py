import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = 'joycrowntech@gmail.com'
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    async with aiosmtplib.SMTP('smtp.gmail.com', 587) as server:
        await server.starttls()
        await server.login('joycrowntech@gmail.com', 'neso ljxo tlkp plvg')
        await server.send_message(msg)

# @app.post("/send-email")
# async def send_email_endpoint(to_email: str, subject: str, body: str):
#     await send_email(to_email, subject, body)
#     return {"message": "Email sent successfully"}