"""
Configuración de Gunicorn para producción
"""
import os

# Directorios
BASE_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Crear directorio de logs si no existe
os.makedirs(LOGS_DIR, exist_ok=True)

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 300  # 5 minutos para jobs largos de scraping
keepalive = 2

# Logging
accesslog = os.path.join(LOGS_DIR, 'access.log')
errorlog = os.path.join(LOGS_DIR, 'error.log')
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'zona-prop-scraper'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (descomentar y configurar para HTTPS)
# keyfile = None
# certfile = None
