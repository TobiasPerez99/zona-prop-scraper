import sys

import pandas as pd

from src import utils
from src.browser import Browser
from src.scraper import Scraper
from src.database import save_estates_to_db


def main(url):
    base_url = utils.parse_zonaprop_url(url)
    print(f'Running scraper for {base_url}')
    print(f'This may take a while...')
    browser = Browser()
    scraper = Scraper(browser, base_url)
    estates = scraper.scrap_website()

    # Guardar CSV (compatibilidad)
    df = pd.DataFrame(estates)
    print('\nScraping finished !!!')
    print('Saving data to csv file')
    filename = utils.get_filename_from_datetime(base_url, 'csv')
    utils.save_df_to_csv(df, filename)
    print(f'Data saved to {filename}')

    # Guardar en base de datos
    print('\n--- Guardando en base de datos ---')
    try:
        saved_count = save_estates_to_db(estates)
        print(f'[OK] {saved_count} propiedades guardadas en la base de datos')
    except Exception as e:
        print(f'[ERROR] Error guardando en base de datos: {e}')
        import traceback
        traceback.print_exc()

    print('\nScrap finished !!!')

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.zonaprop.com.ar/departamentos-alquiler.html'
    main(url)
