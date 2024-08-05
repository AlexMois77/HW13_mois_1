import cloudinary
import cloudinary.uploader
import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
    BackgroundTasks,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth.models import User
from src.auth.email_utils import send_verification
from src.auth.pass_utils import verify_password
from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    create_verification_token,
    decode_verification_token,
    get_current_user,
)
from src.auth.repo import UserRepository
from src.auth.schemas import Token, UserBase, UserCreate, UserResponse
from config.db import get_db
from jinja2 import Environment, FileSystemLoader
from config.general import settings

router = APIRouter()
env = Environment(loader=FileSystemLoader("src/templates"))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        cloudinary.config(
            cloud_name=settings.cloudinary_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )
        user_repo = UserRepository(db)
        result = cloudinary.uploader.upload(file.file)

        url = result.get("secure_url")
        if not url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image to Cloudinary",
            )

        logger.debug(f"Updating user avatar URL to {url}")

        user = user_repo.update_avatar(current_user.email, url)
        return user

    except Exception as e:
        logger.exception("Failed to update avatar")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update avatar",
        )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = user_repo.create_user(user_create)
    verification_token = create_verification_token(user.email)
    verification_link = (
        f"http://localhost:8000/auth/verify-email?token={verification_token}"
    )

    template = env.get_template("verification_email.html")
    email_body = template.render(verification_link=verification_link)

    background_tasks.add_task(send_verification, user.email, email_body)
    return user


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    email: str = decode_verification_token(token)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_repo.activate_user(user)
    return {"msg": "Email verified successfully"}


@router.post("/token", response_model=Token, status_code=status.HTTP_201_CREATED)
def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token, status_code=status.HTTP_201_CREATED)
def refresh_token():
    pass
