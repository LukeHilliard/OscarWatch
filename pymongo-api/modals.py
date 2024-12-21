import uuid
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    password: str = Field(...)
    token: str = Field(...)
    login: int = Field(...)
    read_access: int = Field(...)
    write_access: int = Field(...)
    is_admin: int = Field(...)

    class Config: 
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Luke",
                "password": "wijpyf-pYjbu3-pesmep",
                "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUxZDcxYzE3MjhjZTgyNDNiZmM5ZWU2NWFjYjhkMTI3NThjZmViOTgiLCJ0eXAiOiJKV1QifQ...",
                "login": 0,
                "read_access": 1,
                "write_access": 1,
                "is_admin": 1,
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str]
    password: Optional[str]
    login: Optional[int]
    read_access: Optional[int]
    write_access: Optional[int]
    is_admin: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Luke Hilliard",
                "password": "wijpyf-pYjbu3-pesmep",
                "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjUxZDcxYzE3MjhjZTgyNDNiZmM5ZWU2NWFjYjhkMTI3NThjZmViOTgiLCJ0eXAiOiJKV1QifQ...",
                "login": 1,
                "read_access": 1,
                "write_access": 0,
                "is_admin": 0,
            }
        }