from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
import re
import traceback

# Configuration de WebDriver
service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)

# URL de base
base_url = "https://www.menzili.tn/immo/appartement-avendre-tunis?tri=1&page="

# Création du fichier CSV
with open('appartements.csv', 'a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Type", "Price", "Surface", "Rooms", "Location", "Etage", "Ascenseur"])

    # Numéro de la page initiale
    page_number = 1

    # Boucle pour parcourir toutes les pages (par exemple jusqu'à 84)
    while page_number <= 74:
        url = base_url + str(page_number)
        print(f"Accès à la page {page_number}: {url}")
        driver.get(url)

        # Attendre que les résultats soient chargés
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#block-listing a"))
            )

            # Récupérer tous les liens des annonces
            listings = driver.find_elements(By.CSS_SELECTOR, "#block-listing a")
            links = [listing.get_attribute("href") for listing in listings]

            if not links:
                print(f"Aucune annonce trouvée sur la page {page_number}.")
                page_number += 1  # Passer à la page suivante
                continue  # Passer à l'itération suivante

            for i, link in enumerate(links):
                try:
                    driver.get(link)

                    # Attendre que les détails de l'annonce soient visibles
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1[itemprop='name']"))
                    )

                    # Extraire les informations
                    try:
                        title = driver.find_element(By.CSS_SELECTOR, "h1[itemprop='name']").text
                    except NoSuchElementException:
                        title = "N/A"

                    try:
                        property_type = driver.find_element(By.CSS_SELECTOR, "a[href*='appartement'] span").text
                    except NoSuchElementException:
                        property_type = "N/A"

                    try:
                        price = driver.find_element(By.XPATH, "//p[contains(text(),'DT')]").text.strip()
                        price = re.split(r'~', price)[0].strip()
                        price = re.sub(r'\s?DT', '', price)
                    except NoSuchElementException:
                        price = "N/A"

                    try:
                        surface = driver.find_element(
                            By.XPATH,
                            "//div[contains(@class, 'block-over')]//span[contains(text(),'Surf habitable')]//following-sibling::strong"
                        ).text.split()[0]
                    except NoSuchElementException:
                        surface = "N/A"

                    try:
                        rooms = driver.find_element(
                            By.XPATH,
                            "//div[contains(@class, 'block-over')]//span[contains(text(),'Piéces (Totale)')]//following-sibling::strong"
                        ).text
                    except NoSuchElementException:
                        rooms = "N/A"

                    try:
                        description = driver.find_element(By.CSS_SELECTOR, "p[itemprop='text']").text

                        # Extraire l'étage
                        etage_match = re.search(
                            r'(\d+)(?:[èe]?m[e]?|er|ème)?\s*(?:et dernier)?\s*étage',
                            description, re.IGNORECASE
                        )
                        if etage_match:
                            etage = etage_match.group(1)
                        elif "rez-de-chaussée" in description.lower():
                            etage = "0"
                        else:
                            etage = "1"

                        # Vérifier la présence d'un ascenseur
                        ascenseur = "Oui" if re.search(r'\bascenseur\b', description, re.IGNORECASE) else "Non"
                    except NoSuchElementException:
                        etage = "1"
                        ascenseur = "Non"

                    try:
                        location = driver.find_element(By.XPATH, "//p[i[contains(@class, 'fa-map-marker')]]").text.strip()
                    except NoSuchElementException:
                        location = "N/A"

                    # Imprimer les informations
                    print(f"Title: {title}, Type: {property_type}, Price: {price}, Surface: {surface}, Rooms: {rooms}, Location: {location}, Etage: {etage}, Ascenseur: {ascenseur}")

                    # Écrire dans le fichier CSV
                    writer.writerow([title, property_type, price, surface, rooms, location, etage, ascenseur])

                except TimeoutException:
                    print(f"Timeout lors du traitement du lien {link}. Passage au suivant.")
                except Exception as e:
                    print(f"Erreur lors du traitement du lien {link}: {e}")
                    traceback.print_exc()

            # Passer à la page suivante
            page_number += 1

        except TimeoutException:
            print(f"Timeout lors du chargement de la page {page_number}. Passage à la suivante.")
            page_number += 1  # Passer à la page suivante en cas d'erreur

# Fermer le driver
driver.quit()
