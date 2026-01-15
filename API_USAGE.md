# API Usage Guide

Documentación de uso de la API Flask para scraping de ZonaProp.

## Descripción

API REST que permite ejecutar scraping de propiedades de ZonaProp de forma síncrona. Al completar el job, puede enviar una notificación webhook a una URL proporcionada.

## Endpoints

### 1. Health Check

Verifica que la API esté funcionando.

**Request:**
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2026-01-15T12:00:00.000000"
}
```

**Ejemplo con curl:**
```bash
curl http://localhost:5000/health
```

---

### 2. Ejecutar Scraping

Ejecuta un job de scraping de forma síncrona (bloquea hasta terminar).

**Request:**
```http
POST /api/scrape
Content-Type: application/json

{
  "url": "https://www.zonaprop.com.ar/...",
  "webhook_url": "https://tu-servidor.com/webhook"  // Opcional
}
```

**Parámetros:**
- `url` (string, requerido): URL de ZonaProp a scrapear
- `webhook_url` (string, opcional): URL donde enviar notificación al finalizar

**Response (200 OK - Éxito):**
```json
{
  "job_id": "job_20260115_123456",
  "status": "completed",
  "properties_count": 25,
  "csv_file": "data/departamentos-alquiler-monte-grande-2026-01-15-12-34-56.csv"
}
```

**Response (400 Bad Request - Error de validación):**
```json
{
  "error": "URL is required"
}
```

**Response (500 Internal Server Error - Error de scraping):**
```json
{
  "job_id": "job_20260115_123456",
  "status": "failed",
  "error": "Error message here"
}
```

**Ejemplo con curl (sin webhook):**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html"
  }'
```

**Ejemplo con curl (con webhook):**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html",
    "webhook_url": "https://webhook.site/tu-uuid"
  }'
```

---

## Webhook

Si se proporciona `webhook_url`, la API enviará una notificación POST al finalizar el job.

**Request enviado al webhook:**
```http
POST {webhook_url}
Content-Type: application/json

{
  "job_id": "job_20260115_123456",
  "status": "completed",  // o "failed"
  "message": "Scraping completed. 25 properties saved",
  "timestamp": "2026-01-15T12:35:30.123456"
}
```

**Estados posibles:**
- `completed`: Job completado exitosamente
- `failed`: Job falló con error

---

## Testing Local

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar .env

Crear archivo `.env` en la raíz del proyecto:
```
DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=xintel_network
DB_USERNAME=root
DB_PASSWORD=root
SECRET_KEY=dev-secret-key
```

### 3. Ejecutar API en modo desarrollo

```bash
# Opción 1: Flask development server
python -m flask --app api.app run --debug

# Opción 2: Python directo
python -m api.app

# Opción 3: Gunicorn (producción)
gunicorn --config gunicorn_config.py wsgi:app
```

### 4. Probar health check

```bash
curl http://localhost:5000/health
```

Respuesta esperada:
```json
{"status": "ok", "timestamp": "..."}
```

### 5. Probar scraping (sin webhook)

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html"
  }'
```

Este comando bloqueará hasta que termine el scraping (puede tomar varios minutos).

### 6. Probar scraping (con webhook)

Para probar el webhook, usar [webhook.site](https://webhook.site):

1. Ir a https://webhook.site
2. Copiar tu URL única
3. Ejecutar:

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html",
    "webhook_url": "https://webhook.site/TU-UUID-AQUI"
  }'
```

4. Al finalizar el scraping, verás la notificación en webhook.site

---

## Ejemplos de URLs de ZonaProp

```bash
# Departamentos en alquiler en Monte Grande
https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html

# Casas en venta en Capital Federal
https://www.zonaprop.com.ar/casas-venta-capital-federal.html

# Departamentos en alquiler en Palermo
https://www.zonaprop.com.ar/departamentos-alquiler-palermo.html

# Alquileres en general
https://www.zonaprop.com.ar/departamentos-alquiler.html
```

---

## Integración con Otros Sistemas

### Ejemplo: Python

```python
import requests

url = "http://tu-vps.com/api/scrape"
payload = {
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html",
    "webhook_url": "https://tu-backend.com/webhook/scraping-done"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Job ID: {result['job_id']}")
print(f"Status: {result['status']}")
if result['status'] == 'completed':
    print(f"Properties: {result['properties_count']}")
```

### Ejemplo: JavaScript (Node.js)

```javascript
const axios = require('axios');

async function runScraping() {
  try {
    const response = await axios.post('http://tu-vps.com/api/scrape', {
      url: 'https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html',
      webhook_url: 'https://tu-backend.com/webhook/scraping-done'
    });

    console.log('Job ID:', response.data.job_id);
    console.log('Status:', response.data.status);
    if (response.data.status === 'completed') {
      console.log('Properties:', response.data.properties_count);
    }
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

runScraping();
```

### Ejemplo: PHP

```php
<?php

$url = 'http://tu-vps.com/api/scrape';
$data = [
    'url' => 'https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html',
    'webhook_url' => 'https://tu-backend.com/webhook/scraping-done'
];

$options = [
    'http' => [
        'header'  => "Content-type: application/json\r\n",
        'method'  => 'POST',
        'content' => json_encode($data)
    ]
];

$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);

$response = json_decode($result, true);

echo "Job ID: " . $response['job_id'] . "\n";
echo "Status: " . $response['status'] . "\n";
if ($response['status'] === 'completed') {
    echo "Properties: " . $response['properties_count'] . "\n";
}
?>
```

---

## Consideraciones Importantes

### Timeouts

- El scraping es **síncrono** (bloquea hasta terminar)
- El timeout está configurado en **5 minutos** (300 segundos)
- Para URLs con muchas propiedades, puede tomar varios minutos
- Asegurar que el cliente HTTP tenga timeout suficiente

### Rate Limiting

- ZonaProp tiene protección anti-bot
- El scraper incluye delays entre páginas (3 segundos)
- No ejecutar múltiples jobs simultáneos a la misma URL

### Almacenamiento

- Las propiedades se guardan en MySQL automáticamente
- Se genera un CSV en el directorio `data/`
- El CSV incluye timestamp en el nombre

### Webhook

- El webhook se envía solo si se proporciona `webhook_url`
- Timeout del webhook: 10 segundos
- Si el webhook falla, no afecta el resultado del scraping
- El webhook NO incluye los resultados, solo notificación

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200    | Scraping completado exitosamente |
| 400    | Error de validación (URL faltante o inválida) |
| 500    | Error durante scraping |

---

## Logs

Los logs se guardan en:
- `logs/access.log` - Requests HTTP
- `logs/error.log` - Errores de la aplicación

Ver logs en tiempo real:
```bash
tail -f logs/access.log
tail -f logs/error.log
```

---

## Próximos Pasos

Mejoras futuras opcionales:
1. **Jobs asíncronos**: No bloquear el request, retornar inmediatamente
2. **Queue system**: Cola de jobs con Celery + Redis
3. **Job status endpoint**: Consultar estado de job con GET /api/jobs/{job_id}
4. **Authentication**: API Keys o JWT
5. **Rate limiting**: Límite de requests por IP
6. **Dashboard**: UI para ver jobs y resultados
