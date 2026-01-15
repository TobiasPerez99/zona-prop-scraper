import sys

import pandas as pd

from src import utils
from src.browser import Browser
from src.scraper import Scraper
from src.database import get_session


def main(url):
    base_url = utils.parse_zonaprop_url(url)
    print(f'Running scraper for {base_url}')
    print(f'This may take a while...')

    # Inicializar browser y scraper
    browser = Browser()
    scraper = Scraper(browser, base_url)

    # Inicializar sesión de BD y habilitar guardado automático
    db_session = get_session()
    scraper.enable_database_save(db_session)
    print('Guardado en BD habilitado - cada propiedad se guardara inmediatamente\n')

    # Ejecutar scraping (ahora guarda en BD automáticamente)
    estates = scraper.scrap_website()

    # Cerrar sesión de BD
    db_session.close()

    # Guardar CSV al final
    df = pd.DataFrame(estates)
    print('\nScraping finished !!!')
    print('Saving data to csv file')
    filename = utils.get_filename_from_datetime(base_url, 'csv')
    utils.save_df_to_csv(df, filename)
    print(f'Data saved to {filename}')

    print('\nScrap finished !!!')

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.zonaprop.com.ar/departamentos-alquiler.html'
    main(url)
