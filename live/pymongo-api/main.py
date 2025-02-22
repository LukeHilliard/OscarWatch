# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
from pymongo import MongoClient
from routes import router as user_router
import os
load_dotenv(override=True)
app = FastAPI()
print(os.getenv("API_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)


@app.on_event("startup")
def startup_db_client():
        app.mongodb_client = MongoClient(os.getenv("DB_URI"))
        app.database = app.mongodb_client[os.getenv("DB_NAME")]
        print("Connected to MongoDB atlas")
        print(f"Collections: {app.database.list_collection_names()}")

@app.on_event("shutdown")
def shutdown_db_client():
      app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "OscarWatch API Server"}

@app.get("/test_db")
def test_db():
    try:
        collections = app.database.list_collection_names()
        return {"collections": collections}
    except Exception as e:
        return {"error": str(e)}

app.include_router(user_router, prefix="/api", tags=["users"])
