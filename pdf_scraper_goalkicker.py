import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Set up Edge options for headless browsing
edge_options = Options()
edge_options.use_chromium = True
edge_options.add_argument("--headless")
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")

# Initialise the Edge driver
try:
    driver_service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=driver_service, options=edge_options)
except WebDriverException as e:
    print(f"Error initialising Edge driver: {e}")
    exit(1)

# Go to the target website
try:
    driver.get("https://goalkicker.com/")
except TimeoutException as e:
    print(f"Error loading the website: {e}")
    driver.quit()
    exit(1)

# Find all book elements on the page
try:
    books = driver.find_elements(By.CLASS_NAME, "bookContainer")
    if not books:
        print("No books found on the page.")
        driver.quit()
        exit(1)
except NoSuchElementException as e:
    print(f"Error finding book elements: {e}")
    driver.quit()
    exit(1)

book_urls = []
for book in books:
    try:
        book_url = book.find_element(By.TAG_NAME, "a").get_attribute("href")
        book_urls.append(book_url)
    except NoSuchElementException as e:
        print(f"Error finding book URL: {e}")

def download_pdf(book_url):
    try:
        driver.get(book_url)
        time.sleep(2)
    except TimeoutException as e:
        print(f"Error loading book page {book_url}: {e}")
        return

    try:
        download_button = driver.find_element(By.CLASS_NAME, "download")
        pdf_url = download_button.get_attribute("onclick").split("'")[1]
        pdf_full_url = book_url.rsplit('/', 1)[0] + '/' + pdf_url
    except NoSuchElementException as e:
        print(f"Error finding download button on {book_url}: {e}")
        return
    except IndexError as e:
        print(f"Error parsing download URL on {book_url}: {e}")
        return

    retries = 3
    for attempt in range(retries):
        try:
            pdf_response = requests.get(pdf_full_url)
            pdf_response.raise_for_status()
            pdf_name = pdf_url.split('/')[-1]
            with open(pdf_name, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)
            print(f"Downloaded: {pdf_name}")
            break
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} - Error downloading PDF from {pdf_full_url}: {e}")
            if attempt == retries - 1:
                print(f"Failed to download PDF after {retries} attempts.")
            else:
                time.sleep(2)

for url in book_urls:
    download_pdf(url)

driver.quit()
