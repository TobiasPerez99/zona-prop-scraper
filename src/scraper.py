import re
import time
import json
from functools import reduce

from bs4 import BeautifulSoup

PAGE_URL_SUFFIX = '-pagina-'
HTML_EXTENSION = '.html'

FEATURE_UNIT_DICT = {
    'm²': 'square_meters_area',
    'amb': 'rooms',
    'dorm': 'bedrooms',
    'baño': 'bathrooms',
    'baños': 'bathrooms',
    'coch' : 'parking',
    }

LABEL_DICT = {
    'POSTING_CARD_PRICE' : 'price',
    'expensas' : 'expenses',
    'POSTING_CARD_LOCATION' : 'location',
    'POSTING_CARD_DESCRIPTION' : 'description',
}

class Scraper:
    def __init__(self, browser, base_url):
        self.browser = browser
        self.base_url = base_url

    def scrap_page(self, page_number):
        if page_number == 1:
            page_url = f'{self.base_url}{HTML_EXTENSION}'
        else:
            page_url = f'{self.base_url}{PAGE_URL_SUFFIX}{page_number}{HTML_EXTENSION}'

        print(f'URL: {page_url}')

        page = self.browser.get_text(page_url)

        soup = BeautifulSoup(page, 'lxml')
        script_tag = soup.find('script', id="preloadedData")

        if not script_tag:
            print("No se encontró el tag script con id='preloadedData'")
            return []

        # Extraer el texto del script y parsear el JSON
        script_text = script_tag.text.strip()

        # Buscar específicamente window.__PRELOADED_STATE__ =
        preloaded_state_marker = 'window.__PRELOADED_STATE__ = '
        start_index = script_text.find(preloaded_state_marker)

        if start_index == -1:
            print("No se encontró window.__PRELOADED_STATE__")
            return []

        # Empezar después del marcador
        start_index += len(preloaded_state_marker)

        # Encontrar el final del objeto JSON (el próximo ;)
        json_start = start_index
        brace_count = 0
        json_end = -1

        for i in range(json_start, len(script_text)):
            if script_text[i] == '{':
                brace_count += 1
            elif script_text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

        if json_end == -1:
            print("No se pudo encontrar el final del JSON")
            return []

        json_text = script_text[json_start:json_end]

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
            return []

        # Extraer las propiedades de la estructura JSON
        estate_posts = data.get('listStore', {}).get('listPostings', [])

        print(f"Encontradas {len(estate_posts)} propiedades")

        estates = []
        for estate_post in estate_posts:
            estate = self.parse_estate(estate_post)
            estates.append(estate)
        return estates

    def scrap_website(self):
        page_number = 1
        estates = []
        estates_scraped = 0
        estates_quantity = self.get_estates_quantity()
        while estates_quantity > estates_scraped:
            print(f'Page: {page_number}')
            estates += self.scrap_page(page_number)
            page_number += 1
            estates_scraped = len(estates)
            time.sleep(3)

        return estates


    def get_estates_quantity(self):
        page_url = f'{self.base_url}{HTML_EXTENSION}'
        page = self.browser.get_text(page_url)
        soup = BeautifulSoup(page, 'lxml')

        # Extraer el JSON del script tag
        script_tag = soup.find('script', id="preloadedData")

        if not script_tag:
            print("No se encontró el tag script con id='preloadedData'")
            return 0

        script_text = script_tag.text.strip()

        # Buscar específicamente window.__PRELOADED_STATE__ =
        preloaded_state_marker = 'window.__PRELOADED_STATE__ = '
        start_index = script_text.find(preloaded_state_marker)

        if start_index == -1:
            print("No se encontró window.__PRELOADED_STATE__")
            return 0

        # Empezar después del marcador
        start_index += len(preloaded_state_marker)

        # Encontrar el final del objeto JSON
        json_start = start_index
        brace_count = 0
        json_end = -1

        for i in range(json_start, len(script_text)):
            if script_text[i] == '{':
                brace_count += 1
            elif script_text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

        if json_end == -1:
            print("No se pudo encontrar el final del JSON")
            return 0

        json_text = script_text[json_start:json_end]

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
            return 0

        # Obtener la cantidad total de propiedades del paging
        paging = data.get('listStore', {}).get('paging', {})
        estates_quantity = paging.get('total', 0)

        print(f"Total de propiedades encontradas: {estates_quantity}")
        return estates_quantity

    def parse_estate(self, estate_post):
        """
        Parsea un diccionario JSON de una propiedad y extrae la información relevante
        """
        estate = {}

        print(estate_post)
        return

        # ID y títulos
        estate['posting_id'] = estate_post.get('postingId', '')
        estate['title'] = estate_post.get('title', '')
        estate['generated_title'] = estate_post.get('generatedTitle', '')

        # URL
        estate['url'] = 'https://www.zonaprop.com.ar' + estate_post.get('url', '')

        # Precio
        price_operations = estate_post.get('priceOperationTypes', [])
        if price_operations and len(price_operations) > 0:
            prices = price_operations[0].get('prices', [])
            if prices and len(prices) > 0:
                estate['price_value'] = prices[0].get('amount', '')
                estate['price_currency'] = prices[0].get('currency', '')
            else:
                estate['price_value'] = ''
                estate['price_currency'] = ''
        else:
            estate['price_value'] = ''
            estate['price_currency'] = ''

        # Expensas
        expenses = estate_post.get('expenses')
        if expenses:
            estate['expenses_value'] = expenses.get('amount', '')
            estate['expenses_currency'] = expenses.get('currency', '')
        else:
            estate['expenses_value'] = ''
            estate['expenses_currency'] = ''

        # Características principales
        main_features = estate_post.get('mainFeatures', {})

        # Superficie total
        if 'CFT100' in main_features:
            estate['superficie_total'] = main_features['CFT100'].get('value', '')
        else:
            estate['superficie_total'] = ''

        # Superficie cubierta
        if 'CFT101' in main_features:
            estate['superficie_cubierta'] = main_features['CFT101'].get('value', '')
        else:
            estate['superficie_cubierta'] = ''

        # Ambientes
        if 'CFT1' in main_features:
            estate['ambientes'] = main_features['CFT1'].get('value', '')
        else:
            estate['ambientes'] = ''

        # Dormitorios
        if 'CFT2' in main_features:
            estate['dormitorios'] = main_features['CFT2'].get('value', '')
        else:
            estate['dormitorios'] = ''

        # Baños
        if 'CFT3' in main_features:
            estate['baños'] = main_features['CFT3'].get('value', '')
        else:
            estate['baños'] = ''

        # Cocheras
        if 'CFT7' in main_features:
            estate['cocheras'] = main_features['CFT7'].get('value', '')
        else:
            estate['cocheras'] = ''

        # Antigüedad
        if 'CFT5' in main_features:
            estate['antiguedad'] = main_features['CFT5'].get('value', '')
        else:
            estate['antiguedad'] = ''

        # Publisher (inmobiliaria)
        publisher = estate_post.get('publisher', {})
        estate['publisher_name'] = publisher.get('name', '')
        estate['publisher_id'] = publisher.get('publisherId', '')

        # Ubicación
        posting_location = estate_post.get('postingLocation', {})

        # Dirección
        address = posting_location.get('address', {})
        estate['address'] = address.get('name', '')

        # Barrio/zona
        location = posting_location.get('location', {})
        estate['location'] = location.get('name', '')

        # Ciudad
        parent_location = location.get('parent', {})
        estate['city'] = parent_location.get('name', '')

        # Descripción
        estate['description'] = estate_post.get('descriptionNormalized', '')

        # Tipo de propiedad
        real_estate_type = estate_post.get('realEstateType', {})
        estate['property_type'] = real_estate_type.get('name', '')

        return estate

    def parse_currency_value(self, text):
        try:
            currency_value = re.findall(r'\d+\.?\d+', text)[0]
            currency_value = currency_value.replace('.', '')
            currency_value = int(currency_value)
            currency_type = re.findall(r'(USD)|(ARS)|(\$)', text)[0]
            currency_type = [x for x in currency_type if x != ''][0]
            return currency_value, currency_type
        except:
            return text, None

    def parse_text(self, text):
        text = text.replace('\n', '')
        text = text.replace('\t', '')
        text = text.strip()
        return text

    def parse_features(self, text):

        features_matches = re.compile(r'(\d+\.?\d*)\s(\w+)').findall(text)

        features_appearance = {'square_meters_area': 0, 'rooms': 0, 'bedrooms': 0, 'bathrooms': 0, 'parking' : 0}

        features = {}

        for feature in features_matches:
            try:
                feature_unit = f'{FEATURE_UNIT_DICT[feature[1]]}_{features_appearance[FEATURE_UNIT_DICT[feature[1]]]}'
                features_appearance[FEATURE_UNIT_DICT[feature[1]]] += 1
            except:
                feature_unit = feature[1]
            features[feature_unit] = feature[0]
        return features