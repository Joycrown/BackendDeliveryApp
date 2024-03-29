from fastapi_mail import  ConnectionConfig
from config.environ import settings








conf = ConnectionConfig (
    MAIL_USERNAME = settings.email,
    MAIL_PASSWORD =settings.email_password,
    MAIL_FROM = settings.email,
    MAIL_PORT = settings.email_port,
    MAIL_SERVER = settings.email_server,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER="utils/templates"
)