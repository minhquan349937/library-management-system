from pydantic import BaseModel, EmailStr
from app.database.models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str

class User(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True 