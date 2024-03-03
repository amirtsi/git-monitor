from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.api.monitor import monitor_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.db import connect_to_mongo, close_mongo_connection, check_mongo_connection

load_dotenv()  # Load environment variables

app = FastAPI()
origins = ["*"]  # Adjust the list of allowed origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Connect to MongoDB Atlas at startup
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    # Close MongoDB Atlas connection at shutdown
    await close_mongo_connection()

@app.get("/check-mongo-connection")
async def check_mongo():
    # Check the MongoDB connection
    is_connected = await check_mongo_connection()
    if is_connected:
        return {"message": "MongoDB connection is successful"}
    else:
        return {"message": "MongoDB connection failed"}



app.include_router(monitor_router, prefix='/api/v1/monitor_router', tags=['monitor_router'])
