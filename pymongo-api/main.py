# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
from fastapi import FastAPI
from dotenv import load_dotenv
from pymongo import MongoClient
from routes import router as user_router
import os
load_dotenv(override=True)
app = FastAPI()
print(os.getenv("API_URL"))

@app.on_event("startup")
def startup_db_client():
        app.mongodb_client = MongoClient(os.getenv("DB_URI"))
        app.database = app.mongodb_client[os.getenv("DB_NAME")]
        print(app.database.list_collection_names())
        print("Connected to MongoDB atlas")

@app.on_event("shutdown")
def shutdown_db_client():
      app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the PyMongo tutorial!"}

app.include_router(user_router, prefix="/api", tags=["users"])
