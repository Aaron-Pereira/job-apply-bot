import os
import time
import pyautogui
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from gmail_reader import wait_for_code_from_subject

def find_jobs():
    # --- Load environment variables ---
    load_dotenv()
    username = os.getenv("JOBBOT_USERNAME")
    email = f"{username}@gmail.com"

    # --- Set up WebDriver ---
    CHROMEDRIVER_PATH = "/Users/aaronmitchell/Downloads/chromedriver-mac-arm64/chromedriver"
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    # --- Open the website ---
    driver.get("https://www.seek.com.au")

    # --- Start login process ---
    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/header/div/div/div/div[1]/div[2]/div[1]/div/div/div/a")))
    sign_in_button.click()

    # --- Enter email ---
    input_box = wait.until(EC.element_to_be_clickable((By.ID, "emailAddress")))
    input_box.clear()
    input_box.send_keys(email)

    # --- Click login ---
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-cy="login"]')))
    login_button.click()

    # --- Wait for and input verification code ---
    time.sleep(5)
    code = wait_for_code_from_subject()
    if code:
        print("Retrieved login code:", code)
        code_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="verification input"]')))
        code_input.send_keys(code)
        pyautogui.press('enter')
    else:
        print("No verification code received.")

