"""
Utilidades para la API Flask
"""
import requests
from datetime import datetime
from api.config import Config


def generate_job_id():
    """
    Genera un ID único para el job de scraping
    Formato: job_YYYYMMDD_HHMMSS
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'job_{timestamp}'


def send_webhook(webhook_url, payload):
    """
    Envía una notificación POST a la URL del webhook

    Args:
        webhook_url (str): URL del webhook a llamar
        payload (dict): Datos a enviar en el body del POST

    Returns:
        bool: True si el webhook se envió exitosamente, False si falló
    """
    if not webhook_url:
        return False

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=Config.WEBHOOK_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code >= 200 and response.status_code < 300:
            print(f'[OK] Webhook enviado a {webhook_url}')
            return True
        else:
            print(f'[WARNING] Webhook retornó status {response.status_code}')
            return False

    except requests.exceptions.Timeout:
        print(f'[ERROR] Timeout enviando webhook a {webhook_url}')
        return False
    except requests.exceptions.RequestException as e:
        print(f'[ERROR] Error enviando webhook: {e}')
        return False
