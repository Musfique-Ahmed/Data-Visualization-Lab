# main.py
import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
# 1. THE WEBSITE URL IS CORRECTLY SET
WEBSITE_URL = "https://uiudsc.uiu.ac.bd/qr-generator"

# 2. THE MEMBER IDS LIST IS POPULATED
MEMBER_IDS = [
    "25P0046", "25P0047", "25P0048", "25P0049", "25P0050", "25P0052", "25P0053",
    "25P0054", "25P0055", "25P0056", "25P0057", "25P0058", "25P0059", "25P0060",
    "25P0062", "25P0063", "25P0064", "25P0065", "25P0066", "25P0067", "25P0068",
    "25P0069", "25P0070", "25P0072", "25P0073", "25P0074", "25P0075", "25P0076",
    "25P0077", "25P0078", "25P0079", "25P0080", "25P0081", "25P0082", "25P0083"
]

# 3. THE DOWNLOAD DIRECTORY IS SET
DOWNLOAD_DIRECTORY = r"C:/Musfique's Folder/UIU DSC/Events/Orientation"

# --- Main Script ---

def setup_driver():
    """Sets up a robust Chrome WebDriver."""
    
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)
        print(f"Created directory: {DOWNLOAD_DIRECTORY}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def process_qr_codes(driver, member_ids):
    """
    For each member ID, generates the QR code and saves it by extracting the
    image data directly from the page using a JavaScript-powered polling loop.
    """
    print("Navigating to the website...")
    driver.get(WEBSITE_URL)
    
    for member_id in member_ids:
        try:
            print(f"\nProcessing Member ID: {member_id}...")
            
            # --- Step 1: Find and fill the input field ---
            print("  - Waiting for Member ID input field...")
            member_id_input = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.NAME, "memberId"))
            )
            
            print("  - Clearing and entering text...")
            member_id_input.send_keys(Keys.CONTROL + "a")
            member_id_input.send_keys(Keys.DELETE)
            member_id_input.send_keys(member_id)
            print(f"  - Entered '{member_id}' into the input field.")

            # --- Step 2: Find and click the "Generate QR Code" button ---
            print("  - Waiting for 'Generate QR Code' button...")
            generate_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            generate_button.click()
            print("  - Clicked 'Generate QR Code' button.")

            # --- Step 3: Find the QR code image with a robust JavaScript polling loop ---
            print("  - Waiting for QR code to generate...")

            # 3a: Wait for the placeholder text to disappear.
            placeholder_xpath = "//p[text()='Enter Member ID to generate QR code']"
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, placeholder_xpath))
            )
            print("  - Placeholder text disappeared. UI is updating.")
            
            # 3b: Define the robust XPath for the image.
            qr_image_xpath = "//div[contains(@class, 'rounded-xl') and .//div[contains(., 'Generated QR Code')]]//img"
            
            # 3c: **FINAL, MOST ROBUST POLLING LOOP USING JAVASCRIPT**
            print("  - Polling for QR code image data to load via JavaScript...")
            start_time = time.time()
            img_src = None
            while time.time() - start_time < 30:  # 30-second timeout
                try:
                    # Re-find the element in each loop iteration to avoid stale element errors
                    qr_image = driver.find_element(By.XPATH, qr_image_xpath)
                    # Use JavaScript to get the 'src' property, which is more reliable
                    img_src = driver.execute_script("return arguments[0].src;", qr_image)
                    if img_src and 'data:image/png;base64,' in img_src:
                        print("  - QR code image data has loaded.")
                        break  # Exit the loop successfully
                except (StaleElementReferenceException, NoSuchElementException):
                    # The page was re-rendering, or the element isn't there yet.
                    # This is expected, so we just continue the loop.
                    pass
                time.sleep(0.5)  # Wait 500ms before checking again
            else:  # This 'else' belongs to the 'while' loop, it executes if the loop finishes without a 'break'
                raise TimeoutException("Timed out waiting for QR code image src attribute to be populated.")

            # 3d: Now that the data is loaded, save the file.
            header, encoded_data = img_src.split(',', 1)
            decoded_data = base64.b64decode(encoded_data)
            
            file_name = f"qr-{member_id}.png"
            file_path = os.path.join(DOWNLOAD_DIRECTORY, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(decoded_data)
            print(f"  - SUCCESS: QR code saved to {file_path}")
            
            time.sleep(1)

        except TimeoutException as e:
            print(f"  - A timeout error occurred while processing {member_id}: {e.msg}")
            print("  - Refreshing page to try and recover...")
            driver.refresh()
            time.sleep(2)
            continue
        except Exception as e:
            print(f"  - An unexpected error occurred while processing {member_id}: {e}")
            print("  - Refreshing page to try and recover...")
            driver.refresh()
            time.sleep(2)
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
