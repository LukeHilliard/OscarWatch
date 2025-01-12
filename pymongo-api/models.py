# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
# Request Body: https://fastapi.tiangolo.com/tutorial/body/

import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    google_id: str = Field(...)
    name: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    profile_picture: Optional[str] = Field(...)
    screenshots: Optional[list[str]] = Field(default_factory=list)
    token: str = Field(...)
    login: str = Field(...)
    read_access: str = Field(...)
    write_access: str = Field(...)
    is_admin: str = Field(...)

    class Config: 
        populate_by_name = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)  # Ensure UUIDs are serialized as strings
        }
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "google_id": "google-123456789",
                "name": "Luke",
                "email": "luke@gmail.com",
                "password": "wijpyf-pYjbu3-pesmep",
                "profile_picture": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD...",
                "screenshots": [
                    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD...",
                    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
                ],
                "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUxZDcxYzE3MjhjZTgyNDNiZmM5ZWU2NWFjYjhkMTI3NThjZmViOTgiLCJ0eXAiOiJKV1QifQ...",
                "login": "0",
                "read_access": "1",
                "write_access": "1",
                "is_admin": "1",
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    profile_picture: Optional[str] = Field(...)
    screenshots: Optional[list[str]] = Field(default_factory=list)
    login: Optional[int]
    read_access: Optional[int]
    write_access: Optional[int]
    is_admin: Optional[int]

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "google_id": "google-123456789",
                "name": "Luke Hilliard",
                "email": "luke@gmail.com",
                "password": "wijpyf-pYjbu3-pesmep",
                "profile_picture": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD...",
                "screenshots": [
                    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD...",
                    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
                ],
                "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUxZDcxYzE3MjhjZTgyNDNiZmM5ZWU2NWFjYjhkMTI3NThjZmViOTgiLCJ0eXAiOiJKV1QifQ...",
                "login": "1",
                "read_access": "1",
                "write_access": "0",
                "is_admin": "0",
            }
        }

class LoginRequest(BaseModel):
    email: str
    password: str

class LogoutRequest(BaseModel):
    id: str

class ImageUploadRequest(BaseModel):
    images: List[str]