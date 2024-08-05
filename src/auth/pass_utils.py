from passlib.context import CryptContext


pwd_contex = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_contex.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_contex.verify(password, hashed_password)
