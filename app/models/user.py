from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.utils.db_utils import Base

default_profile_pic = "https://example.com/default.png"  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_pic = Column(String, default=default_profile_pic)
    tasks = relationship("Task", back_populates="owner")  

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    profile_pic: Optional[str] = None

    class Config:
        orm_mode = True
