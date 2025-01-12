# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
import base64

from models import * 

router = APIRouter()


# --------------------- User CRUD ---------------------

# Create a new user to collection (register)
#
@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(request: Request, user: User = Body(...)):
    user = jsonable_encoder(user)
    print(f"Adding : \n{user}\n : to 'users' collection")

    # check if user with the same email or Google ID already exists
    existing_user = request.app.database["users"].find_one({
        "$or": [{"email": user.get("email")}]
    })

    if existing_user:
        raise HTTPException(status_code=400, detail="User with the given email or Google ID already exists.")

    # if a user does not register with google their profile picture will be flagged as default, triggering the base64 conversion and assignment, if registered with google then the https images provided by google will be used
    print(f"profile picture --> {user["profile_picture"]}")
    if user["profile_picture"] == "default":
        user["profile_picture"] = "../static/images/default_profile_picture.png"

        

    # insert the new user
    new_user = request.app.database["users"].insert_one(user)
    created_user = request.app.database["users"].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user


# Get a single user by _id
#
@router.get("/{id}", response_description="Get a user by id", response_model=User)
def find_user(id: str, request: Request):
    if(user := request.app.database["users"].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")


# Get a list of all users
#
@router.get("/", response_description="List all users", response_model=List[User])
def list_users(request: Request):
    users = list(request.app.database["users"].find(limit=100))
    return users
    

# Update a user by _id
#
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


# Upload a users screenshot
#
@router.post("/screenshot/{id}", response_description="Append screenshots to user's list")
async def add_images(id: str, request: Request, image_request: ImageUploadRequest):

    user = request.app.database["users"].find_one({"_id": id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    
    #print(f"user found: {user}")

    # append images to the user's screenshots
    result = request.app.database["users"].update_one(
        {"_id": id},
        {"$push": {"screenshots": {"$each": image_request.images}}}
    )

    if result.modified_count == 1:
        return {"message": "Screenshots appended successfully", "user_id": id, "images_appended": len(image_request.images)}
    else:
        raise HTTPException(status_code=500, detail="Failed to append screenshots")
    

# Get a list of users screenshots
#
@router.get("/all_screenshots/{id}", response_description="Return a list of a users screenshots")
async def get_all_images(id: str, request: Request):
    user = request.app.database["users"].find_one({"_id": id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    
    return {"screenshots": user.get("screenshots", [])}
    


# Delete a user by _id
#
@router.delete("/{id}", response_description="Delete a user")
def delete_user(id: str, request: Request, response: Response):
    delete_result = request.app.database["users"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} not found")

# --------------------------------------------------------
# --------------------- Helper ---------------------

# check if a users exists based on email
#
@router.get("/check_if_exists/{email}", response_description="Check if a user exists via email")
def find_user_by_email(email: str, request: Request):
    user = request.app.database["users"].find_one({"email": email})
    if user:
        print(f"User does exist with email:{email}")
        request.app.database["users"].update_one({"email": user["email"]}, {"$set": {"login": "1"}})
        return { "exists": "True", "id": user["_id"] }
    else:
        print("User does not exist")
        return { "exists": "False" }


# --------------------------------------------------------

        
# --------------------- Security ---------------------

# login with email and password
#
@router.post("/login", response_description="Login with email")
def login(request: Request, loginDetails: LoginRequest = Body(...)):
    email = loginDetails.email
    password = loginDetails.password

    user = request.app.database["users"].find_one({"email": email})

    # TODO add hash comparison logic here 
    if user: # matching email found
        if user["password"] == password: # check passwords
            request.app.database["users"].update_one({"email": user["email"]}, {"$set": {"login": "1"}})
            return { "login": "True", "id": user["_id"]}
        else:
            print(f"Incorrect password entered on account {user["_id"]}")
            return { "login": "False", "cause": "password" }  
    else:
        print("Email not found within 'users' collection")
        return { "login": "False", "cause": "email" }    
    
# logout with id
#
@router.post("/logout/{id}", response_description="Logout")
def logout(request: Request, id: str):
    print(f"ID passed to logout route -> {id}")
    result = request.app.database["users"].update_one({"_id": id}, {"$set": {"login": "0"}})
    
    if result.modified_count == 1:
        print(f"Logging out User->{id}")
        return {"logout": "True"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")


# --------------------------------------------------------
    

    