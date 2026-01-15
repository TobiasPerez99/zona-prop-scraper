"""
Configuración de la API Flask
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base de la aplicación Flask"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # API Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

    # Webhook
    WEBHOOK_TIMEOUT = 10  # seconds

    # Scraping
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
