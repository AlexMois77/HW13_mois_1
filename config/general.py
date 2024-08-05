from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str
    database_url: str
    secret_key: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int
    origins: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

