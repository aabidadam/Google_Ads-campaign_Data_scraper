import time
from datetime import datetime, timedelta
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


# Setup logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
# REMOVE headless mode for debugging
# options.add_argument("--headless")  

service = ChromeService("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

def break_into_weekly_chunks(start_date, end_date):
    """
    Breaks a date range into chunks from Monday to Sunday.

    Parameters:
    start_date : str : Start date in 'MM/DD/YYYY' format
    end_date : str : End date in 'MM/DD/YYYY' format

    Returns:
    List of date range tuples in 'MM/DD/YYYY' format
    """

    # Convert string dates to datetime objects
    start = datetime.strptime(start_date, "%m/%d/%Y")
    end = datetime.strptime(end_date, "%m/%d/%Y")
    
    result = []
    current_start = start

    while current_start <= end:
        # Find the next Sunday
        next_sunday = current_start + timedelta(days=(6 - current_start.weekday()))

        # Ensure we don't go past the end date
        current_end = min(next_sunday, end)

        # Append the chunk
        result.append((current_start.strftime("%m/%d/%Y"), current_end.strftime("%m/%d/%Y")))

        # Move to the next Monday
        current_start = current_end + timedelta(days=1)

    return result


def select_date_range(driver, start_date, end_date):
    """
    Selects a date range in the calendar widget.

    Parameters:
    driver : WebDriver instance
    start_date : str : Start date in 'MM/DD/YYYY' format
    end_date : str : End date in 'MM/DD/YYYY' format
    """
    try:
        # Click Calendar
        calender_xpath = "//div[@aria-label[contains(., 'Not applicable')]]"
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, calender_xpath))).click()
        print("✅ Clicked on Calendar")
        time.sleep(2)

        # Wait for Start Date Field
        start_date_xpath = "//label[.//span[text()='Start date']]/input"
        end_date_xpath = "//label[.//span[text()='End date']]/input"


        # Enter Start Date
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, start_date_xpath))).click()
        start_date_input = driver.find_element(By.XPATH, start_date_xpath)
        time.sleep(2)
        start_date_input.clear()
        time.sleep(2)
        start_date_input.send_keys(start_date)
        time.sleep(2)
        start_date_input.send_keys(Keys.RETURN)
        time.sleep(2)
        print(f"✅ Start Date Set: {start_date}")

        time.sleep(2)

        # Enter End Date
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, end_date_xpath))).click()
        end_date_input = driver.find_element(By.XPATH, end_date_xpath)
        time.sleep(2)
        end_date_input.clear()
        time.sleep(2)  # Small delay for stability
        end_date_input.send_keys(end_date)
        time.sleep(2)
        end_date_input.send_keys(Keys.RETURN)
        time.sleep(2)
        print(f"✅ End Date Set: {end_date}")

        # Click Apply Button (if required)
        apply_button_xpath = "//div[contains(text(), 'Apply')]"
        try:
            apply_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, apply_button_xpath)))
            time.sleep(2)
            driver.execute_script("arguments[0].click();", apply_button)
            print("✅ Clicked on Apply Button")
        except:
            print("⚠️ No Apply button found, skipping...")

        print("🎉 Date range selected successfully!")

    except Exception as e:
        print(f"❌ Error selecting date range: {e}")

   

def login_and_navigate_google_ads(driver, email, password):
    try:
        logging.info("Opening Google Sign-In Page...")
        driver.get("https://accounts.google.com/signin")

        # Enter Email
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "identifier"))).send_keys(email)
        logging.info("Entered Email.")

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="identifierNext"]/div/button'))).click()
        logging.info("Clicked Next after Email.")

        # Enter Password
        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Passwd")))
        logging.info("Password field is visible.")

        password_field.send_keys(password)
        logging.info("Entered Password.")

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button'))).click()
        logging.info("Clicked Next after Password.")

        time.sleep(20)  # Wait for potential 2FA or redirects

        # Ensure successful login
        WebDriverWait(driver, 20).until(EC.url_contains("myaccount.google.com"))
        logging.info("Login Successful!")

        # Navigate to Google Ads
        driver.get("https://ads.google.com/aw/campaigns")
        logging.info("Navigated to Google Ads Dashboard.")

        # Click navigation item
        navigation_item_xpath = "/html/body/div[1]/root/div[2]/nav-view-loader/multiaccount-view/div/div[2]/div/div[1]/material-list/material-list-item[2]"
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, navigation_item_xpath))).click()
        logging.info("Clicked on first navigation item.")
        time.sleep(2)

        # Click Campaigns -> Assets
        campaigns_assets_xpath = '//*[@id="navigation.campaigns.assets"]/div/a/navigation-drawer-item'
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, campaigns_assets_xpath))).click()
        logging.info("Clicked on Campaigns -> Assets.")
        time.sleep(2)

        # Click Assets -> Associations
        assets_associations_xpath = '//*[@id="navigation.campaigns.assets.assets.associations"]/div/a/navigation-drawer-item/div[1]'
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, assets_associations_xpath))).click()
        logging.info("Clicked on Assets -> Associations.")
        time.sleep(2)

        # Click on Location filter
        location_fil = '//*[@id="cmExtensionPoint-id"]/base-root/div/div[2]/div[1]/view-loader/asset-multi-view/div/asset-navigation-header/div/asset-type-filter-chips/material-chips/div/material-chip[13]'
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,  location_fil))).click()
        logging.info("Clicked on Location filter.")
        time.sleep(2)

        logging.info("✅ Navigation to Google Ads assets completed successfully!")

    except Exception as e:
        logging.error(f"❌ Error during navigation: {e}")


def add_filter(driver, filter_name, operator, value):
    """
    Adds a filter in the UI.
    
    :param driver: WebDriver instance
    :param filter_name: Name of the filter to select (e.g., "Campaign name")
    :param operator: Operator to select (e.g., "does not contain", "contains")
    :param value: Value to enter in the text area
    """
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    try:
        # Click "Add Filter" input box
        add_filter_input = wait.until(EC.element_to_be_clickable((By.XPATH, 
            '/html/body/div[1]/root/div/div[1]/div[2]/div/div[3]/div/workspace-filters-portal/div/workspace-filter/filter-bar/div/div[3]/menu-suggest-input/div/input')))
        add_filter_input.click()
        logging.info("Clicked on add filter")
        time.sleep(2)

        # Select the filter by name
        campaign_name_filter = driver.find_element(By.XPATH, f'//material-select-item[@aria-label="{filter_name}"]')
        actions.move_to_element(campaign_name_filter).click().perform()
        time.sleep(2)

        # Click the operator dropdown
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@aria-label, "Select operator")]')))
        dropdown.click()
        logging.info("Dropdown clicked successfully.")
        time.sleep(2)

        # Select the operator (e.g., "does not contain")
        operator_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//material-select-dropdown-item[.//span[contains(text(), '{operator}')]]")))
        operator_option.click()
        logging.info(f'"{operator}" operator selected successfully.')
        time.sleep(2)

        # Enter the value in the textarea
        textarea = driver.find_element(By.XPATH, '//textarea[@aria-label="Value"]')
        textarea.send_keys(value)
        time.sleep(2)

        # Click the "Apply" button
        apply_button = driver.find_element(By.XPATH, '//material-button[@aria-label="Apply"]')
        actions.move_to_element(apply_button).click().perform()
        logging.info(f'Filter applied: {filter_name} {operator} "{value}"')
        time.sleep(3)

    except Exception as e:
        logging.error(f"Error while adding filter: {e}")




def extract_multiple_pages(driver, table_xpath, next_page_xpath, max_pages=10):

    page_num = 1
    dataframes = []

    while page_num <= max_pages:
        logging.info(f"Extracting data from page {page_num}...")

        # Extract data from the current page
        df = extract_google_ads_data(driver, table_xpath)
        
        if df is not None:
            dataframes.append(df)
        else:
            logging.warning(f"⚠️ No data extracted from page {page_num}")

        # Try to move to the next page
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, next_page_xpath))
            )
            # time.sleep(2)
            next_button.click()
            time.sleep(2)  # Allow time for the next page to load
        except Exception as e:
            logging.error(f"No more Rows")
            break  # Stop if we can't navigate to the next page

        page_num += 1

    return dataframes


def extract_google_ads_data(driver, table_xpath, max_scroll_attempts=15, wait_time=1):
   
    try:
        # Wait for the table to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ess-table-canvas")))
        # time.sleep(2)
        table_div = driver.find_element(By.XPATH, table_xpath)

        # Scroll down multiple times to load all data
        for _ in range(max_scroll_attempts):
            table_div.send_keys(Keys.PAGE_DOWN)  # Scroll inside the div
            time.sleep(wait_time)
        
        time.sleep(2)
        # Extract the table's HTML content
        full_html = table_div.get_attribute("outerHTML")
        soup = BeautifulSoup(full_html, "html.parser")

        # Find all rows
        rows = soup.find_all("div", {"role": "row"})
        if not rows:
            print("❌ No rows found. Check the HTML structure.")
            return None

        # Extract data from each row
        data = []
        for row in rows:
            cells = row.find_all("ess-cell")  # Target all <ess-cell> elements
            row_data = []

            for cell in cells:
                divs = cell.find_all("div")
                cell_text = " ".join(div.get_text(strip=True) for div in divs if div.get_text(strip=True))
                row_data.append(cell_text)

            if row_data:
                data.append(row_data)

        # Convert to Pandas DataFrame
        df = pd.DataFrame(data)
        df.columns = df.columns.astype(str)  # Ensure column names are strings

        # Drop column "0" if it exists
        if "0" in df.columns:
            df = df.drop(columns=["0"])

        # Rename columns
        df = df.rename(columns={
            "1": "Asset",
            "2": "Clicks",
            "3": "Impr.",
            "4": "CTR",
            "5": "Avg. CPC",
            "6": "Cost"
        })

        return df

    except Exception as e:
        logging.error(f"Error during extraction: {e}")
        return None

try:
   
    login_and_navigate_google_ads(driver, "", "")
    time.sleep(3)

    add_filter(driver, "Campaign name", "does not contain", "mohey")
    add_filter(driver, "Campaign name", "contains", "omni")

    Start_date = "1/6/2025"
    End_date = "1/26/2025"

    date_chunks=break_into_weekly_chunks(Start_date, End_date)
    table_xpath = '//*[@id="cmExtensionPoint-id"]/base-root/div/div[2]/div[1]/view-loader/asset-multi-view/asset-stats-view/tableview/div[6]/ess-table/ess-particle-table/div[1]/div/div[2]'
    next_page_xpath = '//*[@id="cmExtensionPoint-id"]/base-root/div/div[2]/div[1]/view-loader/asset-multi-view/asset-stats-view/tableview/div[6]/div/div/div/pagination-bar/div/div[2]/div[2]/div[2]/material-button[3]/material-ripple'

    for date_chunk in date_chunks:
      print(date_chunk)
      select_date_range(driver, date_chunk[0], date_chunk[1])
      time.sleep(5)
      dataframes = extract_multiple_pages(driver, table_xpath, next_page_xpath, max_pages=8)
  
      if dataframes: 
          final_df = pd.concat(dataframes, ignore_index=True)
          csv_filename = f"{date_chunk[0].replace('/', '-')}_{date_chunk[1].replace('/', '-')}.csv"
          final_df.to_csv(csv_filename, index=False, encoding="utf-8")
          print(f"✅ Data saved to {csv_filename}")
      else:
          print("⚠️ No data extracted, skipping CSV saving.")

      first_page = '//*[@id="cmExtensionPoint-id"]/base-root/div/div[2]/div[1]/view-loader/asset-multi-view/asset-stats-view/tableview/div[6]/div/div/div/pagination-bar/div/div[2]/div[2]/div[2]/material-button[1]/material-ripple'
      WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, first_page))).click()
      logging.info("Back to first page")
      time.sleep(2)

except Exception as e:
    logging.error(f"Error occurred: {e}")

finally:
    # Close browser
    driver.quit()
    logging.info("Browser closed.")
