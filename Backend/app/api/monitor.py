import os
import uuid  # Import UUID module to generate unique filenames
from fastapi import APIRouter, Request, HTTPException
from json.decoder import JSONDecodeError
from app.api.db import save_data, get_all_objects
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from fastapi.responses import FileResponse
import logging
from dotenv import load_dotenv

monitor_router = APIRouter()

load_dotenv()
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')
SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR')

@monitor_router.post("/webhook")
async def github_webhook(request: Request):
    try:
        payload = await request.json()
    except JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    action = payload.get("action")
    pull_request = payload.get("pull_request", {})
    print(f"Action: {action}, PR: {pull_request.get('html_url')}")

    try:
        # Take a screenshot of the pull request page
        screenshot_path = await take_screenshot(pull_request.get("html_url"))
        print(f"Screenshot saved: {screenshot_path}")

        # Save pull request details and screenshot path to the database
        document_id = await save_data(pull_request, screenshot_path)
        print(f"Pull request details and screenshot path saved. Document ID: {document_id}")
    except Exception as e:
        print(f"Error saving pull request details or taking screenshot: {e}")

    return {"message": "Webhook received"}

async def take_screenshot(url: str) -> str:
    screenshots_dir = SCREENSHOTS_DIR  # Use the environment variable
    os.makedirs(screenshots_dir, exist_ok=True)
    
    screenshot_filename = str(uuid.uuid4()) + ".png"
    screenshot_path = os.path.join(screenshots_dir, screenshot_filename)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.binary_location = CHROME_DRIVER_PATH  # Use the environment variable
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    except WebDriverException as e:
        raise RuntimeError(f"Error taking screenshot: {e}")
    finally:
        driver.quit()


@monitor_router.get("/pull-requests")
async def get_pull_requests():
    try:
        # Get all objects from the database
        objects = await get_all_objects()
        return objects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving objects: {e}")
    
@monitor_router.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    file_path = os.path.join(SCREENSHOTS_DIR, filename)  # Use the environment variable

    logging.info(f"Attempting to serve file from: {file_path}")

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(path=file_path, media_type='image/png', filename=filename)
