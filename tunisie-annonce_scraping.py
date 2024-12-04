from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import csv
import re
import time

# Configuration du WebDriver
service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Paramètres de l'URL de base
base_url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=101&rech_cod_typ=10102&rech_cod_sou_typ=&rech_cod_pay=TN&rech_cod_reg=101&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31&rech_page_num="

# Création du fichier CSV
with open('appartements.csv', 'a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Type", "Price", "Surface", "Rooms", "Location", "Etage", "Ascenseur"])

    # Numéro de la page initiale
    page_number = 1

    # Boucle pour parcourir toutes les pages (de 1 à 61 par exemple)
    while page_number <= 61:
        url = base_url + str(page_number)
        print(f"Accès à la page {page_number}: {url}")
        driver.get(url)

        # Attendre que les résultats soient chargés
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table[width='100%']")))

        try:
            listings = driver.find_elements(By.CSS_SELECTOR, "a[href*='DetailsAnnonceImmobilier']")

            if not listings:
                print(f"Aucune annonce trouvée sur la page {page_number}.")
                page_number += 1  # Passer à la page suivante
                continue  # Passer à l'itération suivante

            for i, listing in enumerate(listings):
                try:
                    listings = driver.find_elements(By.CSS_SELECTOR, "a[href*='DetailsAnnonceImmobilier']")
                    if i < len(listings):
                        listings[i].click()
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "td.da_field_text")))

                        # Extraire les informations
                        try:
                            title = driver.find_element(By.CSS_SELECTOR, "a[href*='DetailsAnnonceImmobilier']").text
                        except NoSuchElementException:
                            title = "N/A"

                        # Extraction et condition pour le type de bien
                        try:
                            type_element = driver.find_element(By.XPATH, "//a[contains(text(),'Appart.')]")
                            property_type = type_element.text
                            # Mettre le type "Appartement" si le type contient "Appart."
                            if "Appart." in property_type:
                                property_type = "Appartement"
                            else:
                                continue  # Passer cette annonce si ce n'est pas un "Appartement"
                        except NoSuchElementException:
                            property_type = "N/A"
                            continue  # Passer cette annonce si le type est indéfini

                        try:
                            price_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Dinar Tunisien')]")
                            price = price_element.text.split("Dinar Tunisien")[0].strip()
                        except NoSuchElementException:
                            price = "N/A"

                        try:
                            surface_element = driver.find_element(By.XPATH, "//td[contains(text(),'m²')]")
                            surface = surface_element.text.split("m²")[0].strip()
                        except NoSuchElementException:
                            surface = "N/A"

                        try:
                            rooms_element = driver.find_element(By.XPATH, "//a[contains(text(),'Appart.')]")
                            rooms_text = rooms_element.text
                            rooms = rooms_text.split("Appart.")[1].split()[0].strip()
                        except NoSuchElementException:
                            rooms = "N/A"

                        try:
                            location_element = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Adresse')]]")
                            location = location_element.text.split("Adresse")[1].strip()
                        except NoSuchElementException:
                            location = "N/A"

                        # Utiliser BeautifulSoup pour extraire l'étage et la présence d'ascenseur
                        try:
                            # Récupérer tout le HTML de la page
                            html_content = driver.page_source
                            soup = BeautifulSoup(html_content, 'html.parser')

                            # Rechercher l'étage dans le texte
                            description_text = soup.get_text()

                            # Expression régulière pour l'étage
                            etage_match = re.search(r'(\d+)\s*(?:[èe]?m[e]?|er|ème)?\s*(?:étage)', description_text, re.IGNORECASE)
                            if etage_match:
                                etage = etage_match.group(1)
                            else:
                                etage = "1"

                            # Détection de la présence d'un ascenseur
                            if re.search(r'\bascenseur\b', description_text, re.IGNORECASE):
                                ascenseur = "Oui"
                            else:
                                ascenseur = "Non"
                        except Exception as e:
                            etage = "1"
                            ascenseur = "Non"

                        # Affichage pour débogage
                        print(f"Title: {title}, Type: {property_type}, Price: {price}, Surface: {surface}, Rooms: {rooms}, Location: {location}, Etage: {etage}, Ascenseur: {ascenseur}")

                        # Écriture dans le fichier CSV
                        writer.writerow([title, property_type, price, surface, rooms, location, etage, ascenseur])

                        # Retour à la page principale
                        driver.back()

                        # Attendre que la page principale soit complètement chargée
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table[width='100%']")))

                        time.sleep(1)

                except Exception as e:
                    print("Erreur lors de l'extraction des données:", e)
                    driver.back()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table[width='100%']")))

        except Exception as e:
            print("Erreur générale:", e)

        # Incrémenter le numéro de la page pour passer à la suivante
        page_number += 1

# Fermeture du WebDriver
driver.quit()
