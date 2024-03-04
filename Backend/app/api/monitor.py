import os
import uuid  # Import UUID module to generate unique filenames
from fastapi import APIRouter, Request, HTTPException
from json.decoder import JSONDecodeError
from app.api.db import save_data, get_all_objects
from fastapi.responses import FileResponse
import logging
from dotenv import load_dotenv
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.remote.remote_connection import RemoteConnection
from playwright.async_api import async_playwright


monitor_router = APIRouter()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
    logging.info(f"Action: {action}, PR: {pull_request.get('html_url')}")

    try:
        # Take a screenshot of the pull request page
        screenshot_path = await take_screenshot(pull_request.get("html_url"))
        logging.info(f"Screenshot saved: {screenshot_path}")

        # Save pull request details and screenshot path to the database
        document_id = await save_data(pull_request, screenshot_path)
        logging.info(f"Pull request details and screenshot path saved. Document ID: {document_id}")
    except Exception as e:
        logging.error(f"Error saving pull request details or taking screenshot: {e}")

    return {"message": "Webhook received"}

async def take_screenshot(url: str) -> str:
    # Define the directory to save screenshots
    SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR')
    if SCREENSHOTS_DIR is None:
        raise EnvironmentError("SCREENSHOTS_DIR environment variable is not set.")

    # Create the directory if it doesn't exist
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # Generate a unique filename for the screenshot
    screenshot_filename = str(uuid.uuid4()) + ".png"
    screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Navigate to the specified URL
            await page.goto(url)
            # Take a screenshot of the page
            await page.screenshot(path=screenshot_path)
        except Exception as e:
            # Handle any errors
            raise RuntimeError(f"Error taking screenshot: {e}")
        finally:
            # Close the browser
            await browser.close()

    return screenshot_path

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
