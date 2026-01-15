"""
Aplicación Flask para ejecutar scraping de ZonaProp con webhooks
"""
from flask import Flask, request, jsonify
from datetime import datetime
from api.config import Config
from api.utils import generate_job_id, send_webhook
from api.scraper_service import run_scraping

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    Retorna el estado de la API
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/scrape', methods=['POST'])
def scrape():
    """
    Endpoint para ejecutar scraping de ZonaProp

    Body (JSON):
        {
            "url": "https://www.zonaprop.com.ar/...",
            "webhook_url": "https://tu-servidor.com/webhook"  # Opcional
        }

    Returns:
        JSON con el resultado del scraping:
        - Success (200): {job_id, status, properties_count, csv_file}
        - Error (400/500): {job_id, status, error}
    """
    # Validar que el request tenga JSON
    if not request.is_json:
        return jsonify({
            'error': 'Content-Type must be application/json'
        }), 400

    data = request.get_json()
    url = data.get('url')
    webhook_url = data.get('webhook_url')

    # Validar que la URL esté presente
    if not url:
        return jsonify({
            'error': 'URL is required'
        }), 400

    # Validar que la URL sea de ZonaProp
    if 'zonaprop.com.ar' not in url:
        return jsonify({
            'error': 'URL must be from zonaprop.com.ar'
        }), 400

    # Generar ID único para el job
    job_id = generate_job_id()

    print(f'\n[{job_id}] Nueva solicitud de scraping')
    print(f'[{job_id}] URL: {url}')
    if webhook_url:
        print(f'[{job_id}] Webhook: {webhook_url}')

    try:
        # Ejecutar scraping (SÍNCRONO - bloquea hasta terminar)
        result = run_scraping(url, job_id)

        # Enviar webhook si se proporcionó
        if webhook_url:
            webhook_payload = {
                'job_id': job_id,
                'status': 'completed',
                'message': f'Scraping completed. {result["count"]} properties saved',
                'timestamp': datetime.now().isoformat()
            }
            send_webhook(webhook_url, webhook_payload)

        # Retornar respuesta exitosa
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'properties_count': result['count'],
            'csv_file': result['csv_file']
        }), 200

    except Exception as e:
        error_message = str(e)
        print(f'[{job_id}] ERROR: {error_message}')

        # Enviar webhook de error si se proporcionó
        if webhook_url:
            webhook_payload = {
                'job_id': job_id,
                'status': 'failed',
                'message': error_message,
                'timestamp': datetime.now().isoformat()
            }
            send_webhook(webhook_url, webhook_payload)

        # Retornar respuesta de error
        return jsonify({
            'job_id': job_id,
            'status': 'failed',
            'error': error_message
        }), 500


if __name__ == '__main__':
    # Solo para desarrollo - en producción usar Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
