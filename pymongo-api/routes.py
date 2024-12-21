# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import User, UserUpdate

router = APIRouter()

@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(request: Request, user: User = Body(...)):
    user = jsonable_encoder(user)
    new_user = request.app.database["users"].insert_one(user)
    created_user = request.app.database["users"].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user

@router.get("/", response_description="List all users", response_model=List[User])
def list_users(request: Request):
    users = list(request.app.database["users"].find(limit=100))
    return users

@router.get("/{id}", response_description="Get a user by id", response_model=User)
def find_user(id: str, request: Request):
    if(user := request.app.database["users"].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

@router.put("/{id}", response_description="Update a user", response_model=User)
def update_user(id: str, request: Request, user: UserUpdate = Body(...)):
    user = {k: v for k, v in user.dict().items() if v is not None}
    if len(user) >=1:
        update_result = request.app.database["users"].update_one(
            {"_id": id}, {"$set": user}
        )

        if update_result.modifier_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
        
    if (
        existing_book := request.app.database["users"].find_one({"_id": id})
    ) is not None:
        return existing_book
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
    
@router.delete("/{id}", response_description="Delete a user")
def delete_user(id: str, request: Request, response: Response):
    delete_result = request.app.database["users"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")
    