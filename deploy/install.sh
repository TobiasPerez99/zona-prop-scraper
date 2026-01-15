#!/bin/bash
# Script de instalación para VPS Ubuntu/Debian

set -e  # Salir si hay error

echo "=== Instalación de Zona Prop Scraper API ==="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que se ejecuta con sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Por favor ejecutar con sudo"
    exit 1
fi

# Actualizar sistema
print_info "Actualizando sistema..."
apt update
apt upgrade -y

# Instalar dependencias del sistema
print_info "Instalando dependencias..."
apt install -y python3 python3-pip python3-venv nginx mysql-client

# Crear usuario si no existe
if ! id "www-data" &>/dev/null; then
    print_info "Creando usuario www-data..."
    useradd -r -s /bin/false www-data
fi

# Crear directorio de aplicación
APP_DIR="/var/www/zona-prop-scraper"
print_info "Creando directorio de aplicación en $APP_DIR..."
mkdir -p $APP_DIR
chown $USER:$USER $APP_DIR

# Copiar archivos (asumir que el script se ejecuta desde el repo)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

print_info "Copiando archivos al servidor..."
cp -r $REPO_DIR/* $APP_DIR/
cd $APP_DIR

# Crear entorno virtual
print_info "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual e instalar dependencias
print_info "Instalando dependencias de Python..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios necesarios
print_info "Creando directorios de trabajo..."
mkdir -p logs data

# Configurar .env
if [ ! -f .env ]; then
    print_warning "Archivo .env no encontrado"
    print_info "Por favor crear archivo .env con las credenciales de la BD"
    echo ""
    echo "Ejemplo de .env:"
    echo "DB_CONNECTION=mysql"
    echo "DB_HOST=localhost"
    echo "DB_PORT=3306"
    echo "DB_DATABASE=xintel_network"
    echo "DB_USERNAME=root"
    echo "DB_PASSWORD=tu_password"
    echo "SECRET_KEY=tu_secret_key_random"
    echo ""
    read -p "Presiona Enter para continuar después de crear el archivo .env..."
fi

# Setup base de datos
if [ -f .env ]; then
    print_info "Configurando base de datos..."
    python setup_database.py
else
    print_error "No se puede configurar la BD sin archivo .env"
fi

# Instalar servicio systemd
print_info "Instalando servicio systemd..."
cp deploy/zona-scraper.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable zona-scraper

# Configurar Nginx
print_info "Configurando Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/zona-scraper
ln -sf /etc/nginx/sites-available/zona-scraper /etc/nginx/sites-enabled/

# Verificar configuración de Nginx
print_info "Verificando configuración de Nginx..."
nginx -t

# Ajustar permisos
print_info "Ajustando permisos..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Iniciar servicios
print_info "Iniciando servicios..."
systemctl start zona-scraper
systemctl restart nginx

# Verificar estado
print_info "Verificando estado del servicio..."
systemctl status zona-scraper --no-pager

echo ""
print_info "=== Instalación completada ==="
echo ""
print_info "Para verificar que funciona:"
echo "  curl http://localhost:5000/health"
echo ""
print_info "Logs disponibles en:"
echo "  - Aplicación: $APP_DIR/logs/"
echo "  - Systemd: journalctl -u zona-scraper"
echo "  - Nginx: /var/log/nginx/zona-scraper-*.log"
echo ""
print_warning "Recuerda configurar el dominio en /etc/nginx/sites-available/zona-scraper"
