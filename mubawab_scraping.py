from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import csv
import re

# Setup WebDriver
service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)

# List of URLs to scrape
urls = [
    "https://www.mubawab.tn/fr/st/tunis/appartements-a-vendre",
    "https://www.mubawab.tn/fr/st/tunis/appartements-a-vendre:p:2",
    "https://www.mubawab.tn/fr/st/tunis/appartements-a-vendre:p:3",
    "https://www.mubawab.tn/fr/st/tunis/appartements-a-vendre:p:4"
]

# Create CSV file
with open('appartements.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Type", "Price", "Surface", "Rooms", "Location", "Etage", "Ascenseur"])

    for url in urls:
        driver.get(url)

        # Automatically accept cookies if the button is present
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "leadFormButton"))
            )
            cookie_button.click()
        except (TimeoutException, NoSuchElementException):
            print("Cookie acceptance button not found or not clickable.")

        # Wait for listings to load
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col-7.contentBox")))

        # Extract apartment data
        listings = driver.find_elements(By.CSS_SELECTOR, "div.col-7.contentBox")

        # If no listings are found, skip to the next URL
        if not listings:
            print(f"No listings found on {url}.")
            continue

        for listing in listings:
            try:
                title_element = listing.find_element(By.CSS_SELECTOR, "h2.listingTit a")
                title = title_element.text

                # Click to open the listing to reveal price and other details
                title_element.click()

                # Wait for the detailed view to load
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "orangeTit")))

                # Extract property type
                try:
                    type_element = driver.find_element(By.CSS_SELECTOR, "div.adMainFeatureContent p.adMainFeatureContentValue")
                    property_type = type_element.text
                except NoSuchElementException:
                    property_type = "N/A"

                # Extract price
                try:
                    price = driver.find_element(By.CLASS_NAME, "orangeTit").text
                except NoSuchElementException:
                    price = "N/A"

                # Extract surface area (value in <span>)
                try:
                    surface_element = driver.find_element(By.XPATH, "//span[contains(text(),'m²')]")
                    surface = surface_element.text.split()[0]  # Get the number part before "m²"
                except NoSuchElementException:
                    surface = "N/A"

                # Extract number of rooms
                try:
                    rooms_element = driver.find_element(By.CSS_SELECTOR, "i.icon-house-boxes + span")
                    rooms_text = rooms_element.text
                    # Extract only the numeric part
                    rooms_match = re.search(r'\d+', rooms_text)
                    rooms = rooms_match.group(0) if rooms_match else "N/A"
                except NoSuchElementException:
                    rooms = "N/A"

                # Extract location
                try:
                    location = driver.find_element(By.CLASS_NAME, "greyTit").text
                except NoSuchElementException:
                    location = "N/A"

                # Extract floor information (etage) and elevator (ascenseur)
                try:
                    description_element = driver.find_element(By.CSS_SELECTOR, "div.blockProp p")
                    description_text = description_element.text

                    # Search for floor number
                    etage_match = re.search(r'(\d+)\s*(?:[èe]?m[e]?|er|ème)?\s*(?:étage)', description_text, re.IGNORECASE)
                    if etage_match:
                        etage = etage_match.group(1)
                    else:
                        etage = "1"  # Default to 1 if no floor number is found

                    # Search for elevator presence
                    if re.search(r'\bascenseur\b', description_text, re.IGNORECASE):
                        ascenseur = "Oui"
                    else:
                        ascenseur = "Non"
                except NoSuchElementException:
                    etage = "1"  # Default to 1 if description is missing
                    ascenseur = "Non"

                # Print extracted data for debugging
                print(f"Title: {title}, Type: {property_type}, Price: {price}, Surface: {surface}, Rooms: {rooms}, Location: {location}, Etage: {etage}, Ascenseur: {ascenseur}")

                # Write the data to CSV
                writer.writerow([title, property_type, price, surface, rooms, location, etage, ascenseur])

                # Navigate back to the main list
                driver.back()

                # Wait for the listings to reload
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col-7.contentBox")))

            except Exception as e:
                print("Error while extracting data:", e)

# Close WebDriver
driver.quit()
