# main.py
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
# 1. THE WEBSITE URL IS CORRECTLY SET
WEBSITE_URL = "https://uiudsc.uiu.ac.bd/qr-generator"

# 2. ADD ALL THE MEMBER IDS YOU WANT TO PROCESS HERE
MEMBER_IDS = [
    "011211001",
    "011211002",
    "011211003",
    # Add as many member IDs as you need
]

# 3. SET THE FOLDER WHERE QR CODES WILL BE SAVED
# The download directory has been updated to your specified path.
DOWNLOAD_DIRECTORY = r"C:/Musfique's Folder/UIU DSC/Events/Orientation"

# --- Main Script ---

def setup_driver():
    """Sets up the Chrome WebDriver with options to auto-download files."""
    
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)
        print(f"Created directory: {DOWNLOAD_DIRECTORY}")

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIRECTORY,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def process_qr_codes(driver, member_ids):
    """
    Navigates to the site, and for each member ID, generates and downloads
    the corresponding QR code using the correct element selectors.
    """
    print("Navigating to the website...")
    driver.get(WEBSITE_URL)
    
    for member_id in member_ids:
        try:
            print(f"\nProcessing Member ID: {member_id}...")
            
            # --- Step 1: Find the input field by its NAME attribute ---
            # The 'name' attribute is stable, unlike the dynamic 'id'.
            print("  - Waiting for Member ID input field...")
            member_id_input = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.NAME, "memberId"))
            )
            
            print("  - Clearing and entering text...")
            member_id_input.clear()
            member_id_input.send_keys(member_id)
            print(f"  - Entered '{member_id}' into the input field.")

            # --- Step 2: Find and click the "Generate QR Code" button ---
            print("  - Waiting for 'Generate QR Code' button...")
            generate_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            print("  - Clicking 'Generate QR Code' button...")
            generate_button.click()

            # --- Step 3: Wait for and click the "Download QR Code" button ---
            print("  - Waiting for 'Download QR Code' button...")
            download_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download QR Code')]"))
            )
            print("  - Clicking 'Download QR Code' button...")
            # Using a JavaScript click here can be more reliable if a normal click fails.
            driver.execute_script("arguments[0].click();", download_button)
            
            # Wait for the download to start.
            time.sleep(4) 
            print(f"  - Download initiated for {member_id}.")

        except TimeoutException:
            print(f"  - A timeout error occurred while processing {member_id}. The element could not be found.")
            print("  - Refreshing page to try and recover...")
            driver.refresh()
            time.sleep(3)
            continue
        except Exception as e:
            print(f"  - An unexpected error occurred while processing {member_id}: {e}")
            print("  - Refreshing page to try and recover...")
            driver.refresh()
            time.sleep(3)
            continue

def main():
    """Main function to run the automation."""
    driver = setup_driver()
    process_qr_codes(driver, MEMBER_IDS)
    
    driver.quit()
    print("\nAutomation complete. All QR codes have been processed.")
    print(f"Files should be saved in: {DOWNLOAD_DIRECTORY}")

if __name__ == "__main__":
    main()
