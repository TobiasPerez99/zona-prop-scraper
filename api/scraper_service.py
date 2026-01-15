"""
Servicio de scraping que encapsula la lógica de scraping
"""
import pandas as pd
from src import utils
from src.browser import Browser
from src.scraper import Scraper
from src.database import get_session


def run_scraping(url, job_id):
    """
    Ejecuta el scraping de una URL de ZonaProp

    Args:
        url (str): URL de ZonaProp a scrapear
        job_id (str): ID del job de scraping

    Returns:
        dict: Diccionario con los resultados del scraping
              {
                  'count': int,  # Número de propiedades scrapeadas
                  'csv_file': str,  # Ruta del archivo CSV generado
                  'job_id': str  # ID del job
              }

    Raises:
        Exception: Si hay algún error durante el scraping
    """
    base_url = utils.parse_zonaprop_url(url)
    print(f'[{job_id}] Iniciando scraping para {base_url}')

    # Inicializar browser y scraper
    browser = Browser()
    scraper = Scraper(browser, base_url)

    # Inicializar sesión de BD y habilitar guardado automático
    db_session = get_session()
    scraper.enable_database_save(db_session)
    print(f'[{job_id}] Guardado en BD habilitado')

    try:
        # Ejecutar scraping (guarda en BD automáticamente)
        estates = scraper.scrap_website()

        # Cerrar sesión de BD
        db_session.close()

        # Guardar CSV al final
        df = pd.DataFrame(estates)
        filename = utils.get_filename_from_datetime(base_url, 'csv')
        utils.save_df_to_csv(df, filename)

        print(f'[{job_id}] Scraping completado: {len(estates)} propiedades')

        return {
            'count': len(estates),
            'csv_file': filename,
            'job_id': job_id
        }

    except Exception as e:
        # Cerrar sesión de BD en caso de error
        db_session.close()
        print(f'[{job_id}] Error durante scraping: {str(e)}')
        raise e
