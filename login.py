import os
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd

url = "https://newuat.travelwings.com/ae/en"

# File path for the login details CSV file
login_details_file = r"C:\test1\login.csv"

# Create the directory if it doesn't exist
log_dir = r"C:\test1"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging
log_file = os.path.join(log_dir, "login.log")
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read login details from CSV file
def read_login_details_from_csv(file_path):
    login_details = pd.read_csv(file_path)
    logging.debug(f"Login details: {login_details}")
    return login_details

# Fixture to initialize WebDriver
@pytest.fixture(scope="module")
def driver():
    logging.debug("Setting up WebDriver")
    options = webdriver.FirefoxOptions()
    # Uncomment the line below to run the browser in headless mode
    # options.add_argument("--headless")
    driver_instance = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    yield driver_instance
    logging.debug("Tearing down WebDriver")
    driver_instance.quit()

# Function to automate login process
def automate_login(driver, username, password):
    try:
        driver.get(url)
        logging.debug(f"Navigating to URL: {url}")
        
        # Click on My Account dropdown
        my_account_dropdown = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='userName']"))
        )
        my_account_dropdown.click()
        logging.debug("Clicked on My Account dropdown")
        
        # Click on login option
        login_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))
        )
        login_option.click()
        logging.debug("Clicked on login option")

        # Enter username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userAlias"))
        )
        username_field.clear()
        username_field.send_keys(username)

        # Enter password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(password)

        # Click login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "bttn-green"))
        )
        login_button.click()

        # Check if error message is displayed
        error_message = None
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "common-error-msg"))
            ).text
        except TimeoutException:
            pass

        if error_message:
            logging.error(f"Login failed for username: {username}. Error message: {error_message}")
            return False
        else:
            logging.info(f"Login successful for username: {username}")
            return True
    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
        driver.save_screenshot(os.path.join(log_dir, f"element_not_found_{username}.png"))
        logging.error(driver.page_source)
        return False
    except Exception as e:
        logging.error(f"Error occurred during login: {str(e)}")
        driver.save_screenshot(os.path.join(log_dir, f"error_{username}.png"))
        logging.error(driver.page_source)
        return False

# Test function for login process
def test_login(driver):
    login_data = read_login_details_from_csv(login_details_file)

    success_count = 0
    for index, row in login_data.iterrows():
        username = row['username']
        password = row['password']

        logging.debug(f"Testing login for username: {username}")

        login_success = automate_login(driver, username, password)
        if login_success:
            success_count += 1
            logging.info(f"Login successful for username: {username}")
        else:
            logging.warning(f"Login failed for username: {username}")

    # Ensure at least one successful login
    assert success_count > 0, "All login attempts failed."

if __name__ == "__main__":
    pytest.main([__file__, '--alluredir=report','--junitxml=result.xml', '--html=report.html'])
