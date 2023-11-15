import csv
import time
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# preparing csv file to store parsing result later
with open('open_to_work_v6.csv', 'a', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    # If the file is empty, write the header row
    if file.tell() == 0:
        writer.writerow(['Name', 'Open To Work', 'Profile Url'])

    chromedriver_path = '/usr/local/bin/chromedriver'

    start_page = 1
    end_page = 2
    max_pages_per_iteration = 3  # Set the maximum number of pages per iteration

        # Define a function to extract profile information
    def extract_profile_info(soup):
        # Extract the information you need from the soup
        profile_name_elements = soup.select('.entity-result__title-text a')
        return [(name.text.strip(), name['href']) for name in profile_name_elements]


    # Define a function to extract experience from a profile page
    def open_to_work_func(driver, ln_url):
        driver.get(ln_url)
        sleep(10)  # Adjust sleep time as needed

        # Extract experience information from the current profile page
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the div with class "pv-open-to-carousel"
        div_exists = soup.find('div', class_='pv-open-to-carousel') is not None

        # Find the button with class "pv-top-card-profile-picture"
        button_tag = soup.find('button', class_='pv-top-card-profile-picture')

        photo_with_open_to_work = False;

        # Check if the button is found and get the associated img tag
        if button_tag:
            img_tag = button_tag.find('img')
            # Check if the title attribute of the img tag contains "#OPEN_TO_WORK"
            if img_tag and '#OPEN_TO_WORK' in img_tag.get('title', ''):
                photo_with_open_to_work = True
                print("The title contains '#OPEN_TO_WORK'")
            else:
                photo_with_open_to_work = False
                print("The title does not contain '#OPEN_TO_WORK'")

        if div_exists or photo_with_open_to_work:
            print("The div exists.")
            open_to_work = 'Open To Work'
        else:
            print("The div does not exist.")
            open_to_work = 'Not open To Work'

        return open_to_work

    while start_page <= 43:
        # Initialize Chrome WebDriver with the correct executable path
        driver = webdriver.Chrome(service=Service(chromedriver_path))

        # Add your LinkedIn login credentials here
        linkedin_email = 'edw_antikatesthse_to_me_to_diko_sou_linkedin_usenrmae'
        linkedin_password = 'edw_me_to_diko_sou_linkedin_password'

        driver.get('https://www.linkedin.com/')

        # Wait for the username input field to be present
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'session_key')))
        sleep(1)
        # Fill in the username
        username_input.send_keys(linkedin_email)

        # Wait for the password input field to be present
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'session_password')))
        # Fill in the password
        password_input.send_keys(linkedin_password)

        # Wait for the "Sign in" button to be clickable
        sign_in_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        # Click the "Sign in" button
        sign_in_button.click()

        # Check if the page contains a CAPTCHA
        if 'checkpoint/challenge' in driver.current_url:
            print("Please complete the CAPTCHA manually.")
            time.sleep(30)  # Wait for 2 minutes for manual interaction
            # You may want to add additional logic here to check if the CAPTCHA was successfully completed

        pages_run = 1  # Counter for the number of pages run in the current iteration

        for page_num in range(start_page, end_page + 1):
            print(start_page)
            driver.get(f'https://www.linkedin.com/search/results/people/?keywords=housekeeper%20AND%20Greece&origin=SWITCH_SEARCH_VERTICAL&sid=gwT&page={page_num}')
            sleep(10)

            for _ in range(3):
                driver.find_element('tag name', 'body').send_keys(Keys.END)
                sleep(10)

            # Extract profile names and links from the current page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            profiles = extract_profile_info(soup)

            # Loop through each profile, click, extract experience and education, and store in CSV
            for name, ln_url in profiles:
                driver.get(ln_url)
                opentowork = open_to_work_func(driver, ln_url)
                if opentowork == 'Open To Work':
                    print("OPEN to work.")
                    writer.writerow([name, opentowork, ln_url])
        
            pages_run += 1

            if pages_run >= max_pages_per_iteration:
                break  # Exit the loop if the maximum number of pages is reached

        # Close the WebDriver at the end of each batch
        driver.quit()
        print("This is the end of the page number: " + str(start_page))
        # Sleep for 1 minute after closing the WebDriver
        time.sleep(20)

        # Update start and end pages for the next batch
        start_page = end_page + 1
        end_page = min(start_page + 2, 43)  # Ensure end_page doesn't go beyond the last page
