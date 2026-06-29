from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, UserCreate, UserLogin, UserResponse, ForgotPasswordRequest
from middleware.auth import get_password_hash, verify_password, create_access_token, get_current_user
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )
    
    # Hash password and save user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login(response: Response, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and set JWT inside an httpOnly cookie.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Store token in httpOnly cookie
    # Setting max_age to 24 hours (86400 seconds)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=86400,
        expires=86400,
        samesite="lax",
        secure=False  # Set to True in production if HTTPS is configured
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    """
    Clear access token cookie to log out.
    """
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Mock forgot password flow.
    Generates a password reset token and returns it in the API response (for presentation/demo).
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user registered with this email address."
        )
    
    # In a real environment, we'd send an email with this reset token.
    # For this SaaS demo, we will output it in the response.
    reset_token = str(uuid.uuid4())
    return {
        "message": f"Password reset link generated successfully. (Demo Mode: Reset token generated)",
        "reset_token": reset_token,
        "info": "Normally, a password reset link containing this token would be sent to the user's email."
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Fetch the logged-in user profile details.
    """
    return current_user
