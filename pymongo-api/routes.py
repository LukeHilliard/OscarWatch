# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
import base64

from models import * 

router = APIRouter()




# add a new user to collection
@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(request: Request, user: User = Body(...)):
    user = jsonable_encoder(user)
    print(f"users to be added : {user}")

    # check if user with the same email or Google ID already exists
    existing_user = request.app.database["users"].find_one({
        "$or": [{"email": user.get("email")}]
    })

    if existing_user:
        raise HTTPException(status_code=400, detail="User with the given email or Google ID already exists.")

    # if a user does not register with google their profile picture will be flagged as default, triggering the base64 conversion and assignment, if registered with google then the https images provided by google will be used
    print(f"profile picture --> {user["profile_picture"]}")
    if user["profile_picture"] == "default":
        print("User using default profile picture")
        with open("../static/images/default_profile_picture.jpg", "rb") as imageFile: # https://stackoverflow.com/questions/47668507/how-to-store-images-in-mongodb-through-pymongo
            base64_str = base64.b64encode(imageFile.read())
            user["profile_picture"] = base64_str
        

    # insert the new user
    new_user = request.app.database["users"].insert_one(user)
    created_user = request.app.database["users"].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user
    

# login with email and password
@router.post("/login", response_description="Login with email")
def login(request: Request, loginDetails: LoginRequest = Body(...)):
    email = loginDetails.email
    password = loginDetails.password

    user = request.app.database["users"].find_one({"email": email})

    # TODO add hash comparison logic here 
    if user: # matching email found
        if user["password"] == password: # check passwords
            return { "login": "True", "id": user["_id"]}
        else:
            print(f"Incorrect password entered on account {user["_id"]}")
            return { "login": "False", "cause": "password" }  
    else:
        print("Email not found within 'users' collection")
        return { "login": "False", "cause": "email" }    

# check if a users exists based on email
@router.get("/check_if_exists/{email}", response_description="Check if a user exists via email")
def find_user_by_email(email: str, request: Request):
    user = request.app.database["users"].find_one({"email": email})
    if user:
        print(f"User does exist with email:{email}")
        return { "exists": "True", "id": user["_id"] }
    else:
        print("User does not exist")
        return { "exists": "False" }
    



@router.get("/", response_description="List all users", response_model=List[User])
def list_users(request: Request):
    users = list(request.app.database["users"].find(limit=100))
    return users

# Get user by _id
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
    

    