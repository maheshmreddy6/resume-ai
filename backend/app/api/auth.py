from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import UserOut, UserRegister
from app.security import create_access_token, get_current_user, verify_password
from app.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

user_service = UserService()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.get_user(form_data.username)

    if not user or not verify_password(
        form_data.password,
        user["password"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={
            "sub": form_data.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserOut)
def register(payload: UserRegister):
    user_service.create_user(payload.username, payload.password)
    return UserOut(username=payload.username)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: str = Depends(get_current_user)):
    return UserOut(username=current_user)
