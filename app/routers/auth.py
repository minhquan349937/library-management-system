from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database.connection import get_db
from ..database.models import User, UserRole
from ..utils.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/auth/login"}
        )
    return user

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "auth/signup.html", 
        {"request": request}
    )

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    
    if existing_user:
        return templates.TemplateResponse(
            "auth/signup.html",
            {
                "request": request, 
                "error": "Username or email already registered",
                "username": username,
                "email": email
            }
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return RedirectResponse(
            url="/auth/login?success=Account created successfully! Please login.",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "auth/signup.html",
            {
                "request": request, 
                "error": "An error occurred. Please try again.",
                "username": username,
                "email": email
            }
        )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html", 
        {"request": request}
    )

@router.post("/login")
async def login(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Check if login is with email or username
        user = db.query(User).filter(
            or_(
                User.email == username_or_email,
                User.username == username_or_email
            )
        ).first()

        if not user:
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "User does not exist",
                    "username_or_email": username_or_email
                }
            )
        
        if not verify_password(password, user.hashed_password):
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Incorrect password",
                    "username_or_email": username_or_email
                }
            )

        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value
        }
        
        # Redirect based on user role
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "An error occurred during login",
                "username_or_email": username_or_email
            }
        )

@router.get("/logout")
async def logout(request: Request):
    # Xóa session khi logout
    request.session.clear()
    return RedirectResponse(
        url="/auth/login",
        status_code=303
    )