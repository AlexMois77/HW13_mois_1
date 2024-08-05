from fastapi_mail import ConnectionConfig, MessageSchema, FastMail, MessageType
from config.general import settings
from pydantic import BaseModel, EmailStr

# logging.basicConfig(level=logging.DEBUG)


class EmailSchema(BaseModel):
    email: EmailStr


mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_verification(email: str, email_body: str):
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=email_body,
        subtype="html",
    )
    fm = FastMail(mail_conf)
    await fm.send_message(message)
