import os
import time
import pyautogui
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as soup
import re

from gmail_reader import wait_for_code_from_subject

import csv
from datetime import datetime

def find_jobs():
    # --- Load environment variables ---
    load_dotenv()
    username = os.getenv("JOBBOT_USERNAME")
    if not username:
        raise ValueError("JOBBOT_USERNAME not set in environment variables")
    email = f"{username}@gmail.com"

    # --- Set up WebDriver ---
    CHROMEDRIVER_PATH = "/Users/aaronmitchell/Downloads/chromedriver-mac-arm64/chromedriver"
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)  # increased timeout for slower loads

    # --- Open the website ---
    seek_url = "https://www.seek.com.au"
    driver.get(seek_url)

    # --- Start login process ---
    sign_in_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation="promoteSignIn"]')))
    sign_in_button.click()

    # --- Enter email ---
    input_box = wait.until(EC.element_to_be_clickable((By.ID, "emailAddress")))
    input_box.clear()
    input_box.send_keys(email)

    # --- Click login ---
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-cy="login"]')))
    login_button.click()

    # --- Wait for and input verification code ---
    time.sleep(5)  # wait to receive email
    code = wait_for_code_from_subject()
    if code:
        print("Retrieved login code:", code)
        code_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="verification input"]')))
        code_input.clear()
        code_input.send_keys(code)
        pyautogui.press('enter')
    else:
        print("No verification code received.")
        driver.quit()
        return None, None

    # --- Allow page to load after login ---
    time.sleep(5)

    # --- Scroll the page to load more job listings ---
    scroll_count = 2
    scroll_delay = 2
    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)

    # --- Get the full page source after scrolling ---
    html = driver.page_source

    # --- Parse HTML with BeautifulSoup ---
    market_soup = soup(html, 'html.parser')

    # --- Extract and print job links ---
    job_links = market_soup.find_all("a", href=True)

    recommended_jobs = []
    for a in job_links:
        href = a['href']
        data_automation = a.get('data-automation', '')
        
        if href.startswith("/job/") and data_automation.startswith("recommendedJobLink_"):
            full_url = f"https://www.seek.com.au{href}"
            recommended_jobs.append(full_url)

    # Print the links
    for link in recommended_jobs:
        print(link)

    i = 0
    while i < 20:
        print(str(i) + "\n")
        job_link = recommended_jobs[i]
        print(job_link)
        driver.get(recommended_jobs[i])
        time.sleep(5)
        # Parse html
        # Get the html content from soup
        html = driver.page_source
        market_soup = soup(html, 'html.parser')
        # print(market_soup)

        # Grab job description
        # job_description = get_job_description(market_soup)
        job_details_div = market_soup.find("div", attrs={"data-automation": "jobAdDetails"})

        if job_details_div:
            job_description = job_details_div.get_text(separator="\n", strip=True)
            print("Job Description:\n", job_description)
        else:
            print("Job description not found.")

        # Get job title
        # job_title = get_job_title(market_soup)
        title_tag = market_soup.find("h1", attrs={"data-automation": "job-detail-title"})

        if title_tag:
            job_title = title_tag.get_text(strip=True)
            print("Job Title:", job_title)
        else:
            print("Job title not found.")


        # Get company name
        # company_name = get_company_name(market_soup)

        company_tag = market_soup.find("span", attrs={"data-automation": "advertiser-name"})

        if company_tag:
            company_name = company_tag.get_text(strip=True)
            print("Company Name:", company_name)
        else:
            print("Company name not found.")

        # Save each job to CSV
        save_job(job_link, company_name, job_title, job_description)

        i += 1


    # print(market_soup)

    # return market_soup, driver


def remove_html_tags(text):
    """Removes all HTML tags from the input string and returns plain text."""
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

def get_company_name(html):
    # market_soup = soup(html, 'html.parser')
    company_name = html.find_all(class_="gepq850 eihuid4z eihuidi7 i7p5ej0 i7p5ej1 i7p5ej21 _18ybopc4 i7p5eja")
    company_name_text = ' '.join([element.get_text() for element in company_name])
    parsed_company_name = remove_html_tags(company_name_text)
    return parsed_company_name

def get_job_title(html):
    # market_soup = soup(html, 'html.parser')
    job_title = html.find_all(class_="gepq850 eihuid4z i7p5ej0 i7p5ejl _18ybopc4 i7p5ejs i7p5ej21")
    job_title_text = ' '.join([element.get_text() for element in job_title])
    parsed_job_title = remove_html_tags(job_title_text)
    return parsed_job_title

def get_job_description(html):
    # market_soup = soup(html, 'html.parser')
    job_description = html.find_all(class_="gepq850 _1iptfqa0")
    # Convert ResultSet to a single string
    job_description_text = ' '.join([element.get_text() for element in job_description])
    parsed_job_description = remove_html_tags(job_description_text)
    return parsed_job_description

def save_job(job_link, company_name, job_title, job_description, filename="jobs.csv"):
    # Check if file exists
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), job_link, company_name, job_title, job_description])
