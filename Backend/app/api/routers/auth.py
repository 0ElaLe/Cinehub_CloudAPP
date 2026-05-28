from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import LoginRequest, LoginResponse, UserOut
from app.services.auth_service import authenticate_user, create_mock_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(payload.email, payload.password, db)
    token = create_mock_token(user)
    return LoginResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    return current_user
