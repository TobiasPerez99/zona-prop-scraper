# Zona Prop Scraper

Scraper de Zonaprop con almacenamiento en MySQL y API REST para ejecución remota.

## Características

- Scraping de propiedades de ZonaProp
- Almacenamiento automático en MySQL durante scraping
- Exportación a CSV
- API REST Flask para ejecución remota
- Webhooks para notificaciones
- Listo para deployment en VPS

## Instalación

### 1. Instalar dependencias

Con pip:
```bash
pip install -r requirements.txt
```

Con conda:
```bash
conda install --file requirements.txt
```

### 2. Configurar base de datos

Crear archivo `.env` en la raíz del proyecto:
```
DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=xintel_network
DB_USERNAME=root
DB_PASSWORD=root
SECRET_KEY=tu-secret-key-aqui
```

Ejecutar setup de base de datos:
```bash
python setup_database.py
```

## Uso

### Opción 1: Script de línea de comandos

Ejecutar el script `zonaprop-scraping.py` pasando la URL de ZonaProp:

```bash
python zonaprop-scraping.py <url>
```

Ejemplo:
```bash
python zonaprop-scraping.py https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html
```

El script:
- Scrapeará todas las páginas de resultados
- Guardará cada propiedad en MySQL automáticamente
- Generará un archivo CSV en el directorio `data/`

### Opción 2: API REST

#### Ejecutar API localmente

Modo desarrollo:
```bash
python -m flask --app api.app run --debug
```

Modo producción:
```bash
gunicorn --config gunicorn_config.py wsgi:app
```

#### Endpoints

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Ejecutar Scraping:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html",
    "webhook_url": "https://tu-servidor.com/webhook"
  }'
```

Ver [API_USAGE.md](API_USAGE.md) para documentación completa de la API.

## Deployment en VPS

Ver guía completa en [deploy/README.md](deploy/README.md).

Instalación rápida:
```bash
# Copiar proyecto al servidor
scp -r zona-prop-scraper user@tu-vps:/tmp/

# Ejecutar script de instalación
ssh user@tu-vps
cd /tmp/zona-prop-scraper
sudo bash deploy/install.sh
```

## Estructura del Proyecto

```
zona-prop-scraper/
├── api/                    # API Flask
│   ├── __init__.py
│   ├── app.py             # Endpoints
│   ├── config.py          # Configuración
│   ├── scraper_service.py # Servicio de scraping
│   └── utils.py           # Utilidades
├── src/                   # Lógica de scraping
│   ├── browser.py         # Cliente HTTP
│   ├── database.py        # ORM y conexión BD
│   ├── models.py          # Modelos SQLAlchemy
│   ├── scraper.py         # Lógica de scraping
│   └── utils.py           # Helpers
├── deploy/                # Configuración deployment
│   ├── install.sh         # Script instalación VPS
│   ├── nginx.conf         # Config Nginx
│   ├── zona-scraper.service  # Systemd service
│   └── README.md          # Guía deployment
├── data/                  # Archivos CSV generados
├── logs/                  # Logs de la aplicación
├── analysis/              # Notebooks de análisis
├── .env                   # Variables de entorno
├── database_schema.sql    # Schema de BD
├── setup_database.py      # Setup inicial BD
├── zonaprop-scraping.py   # Script CLI
├── wsgi.py               # Entry point WSGI
├── gunicorn_config.py    # Config Gunicorn
├── requirements.txt       # Dependencias Python
├── API_USAGE.md          # Documentación API
└── README.md             # Este archivo
```

## Base de Datos

El proyecto usa MySQL con las siguientes tablas:
- `properties` - Propiedades scrapeadas
- `publisher` - Inmobiliarias/publicadores
- `sources_data` - Fuentes de datos (ZonaProp)
- `images` - Imágenes de propiedades

Ver [database_schema.sql](database_schema.sql) para el schema completo.

## Análisis de Datos

Ver análisis exploratorio en [analysis/exploratory-analysis.ipynb](analysis/exploratory-analysis.ipynb).

Ejemplo de cómo utilizar los datos scrapeados para análisis.

## Documentación

- [API_USAGE.md](API_USAGE.md) - Documentación completa de la API
- [deploy/README.md](deploy/README.md) - Guía de deployment
- [CLAUDE.md](CLAUDE.md) - Instrucciones para Claude Code

## Tecnologías

- Python 3.8+
- Flask 3.0+
- SQLAlchemy 2.0+
- BeautifulSoup4
- cloudscraper
- MySQL/MariaDB
- Gunicorn
- Nginx

## Licencia

Este proyecto es de código abierto.
