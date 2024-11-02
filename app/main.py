from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.database import engine, Base
from app.database.models import UserRole
from app.routers import auth, admin, member
from app.utils.auth import login_required

# Initialize FastAPI app
app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")

# Create all tables
Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(member.router)

# Root route
@app.get("/")
async def root(request: Request):
    try:
        user = request.session.get("user")
        if user:
            if user["role"] == UserRole.ADMIN.value:
                return RedirectResponse(url="/admin/dashboard", status_code=303)
            else:
                return RedirectResponse(url="/member/dashboard", status_code=303)
    except:
        pass
    
    return RedirectResponse(url="/auth/login", status_code=303)