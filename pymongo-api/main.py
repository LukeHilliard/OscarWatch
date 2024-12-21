# To create this I followed this tutorial - https://www.mongodb.com/resources/languages/pymongo-tutorial
from fastapi import FastAPI
from dotenv import load_dotenv
from pymongo import MongoClient
import os
load_dotenv()
app = FastAPI()

@app.on_event("startup")
def startup_db_client():
        app.mongodb_client = MongoClient(os.getenv("DB_URI"))
        app.database = app.mongodb_client[os.getenv("DB_NAME")]
        print("Connected to MongoDB atlas")

@app.on_event("shutdown")
def shutdown_db_client():
      app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the PyMongo tutorial!"}

