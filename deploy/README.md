# Deployment Guide - Zona Prop Scraper API

Guía para desplegar la API en un servidor VPS Ubuntu/Debian.

## Requisitos

- VPS con Ubuntu 20.04+ o Debian 11+
- Acceso root o sudo
- MySQL instalado y configurado
- Dominio o IP pública (opcional)

## Instalación Automática

1. Copiar el proyecto al servidor:
```bash
# En tu máquina local
scp -r zona-prop-scraper user@tu-vps:/tmp/
```

2. Conectar al VPS y ejecutar el script de instalación:
```bash
ssh user@tu-vps
cd /tmp/zona-prop-scraper
sudo bash deploy/install.sh
```

El script instalará:
- Dependencias del sistema
- Entorno virtual Python
- Dependencias Python
- Servicio systemd
- Configuración Nginx

## Configuración Manual

### 1. Preparar el servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv nginx mysql-client
```

### 2. Configurar la aplicación

```bash
# Crear directorio
sudo mkdir -p /var/www/zona-prop-scraper
sudo chown $USER:$USER /var/www/zona-prop-scraper
cd /var/www/zona-prop-scraper

# Copiar archivos del proyecto aquí

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env`:
```bash
nano .env
```

Contenido:
```
DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=xintel_network
DB_USERNAME=root
DB_PASSWORD=tu_password_seguro
SECRET_KEY=genera_un_key_random_aqui
```

### 4. Configurar base de datos

```bash
python setup_database.py
```

### 5. Configurar systemd

```bash
# Copiar servicio
sudo cp deploy/zona-scraper.service /etc/systemd/system/

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable zona-scraper
sudo systemctl start zona-scraper

# Verificar estado
sudo systemctl status zona-scraper
```

### 6. Configurar Nginx

```bash
# Copiar configuración
sudo cp deploy/nginx.conf /etc/nginx/sites-available/zona-scraper

# Editar dominio
sudo nano /etc/nginx/sites-available/zona-scraper
# Cambiar "tu-dominio.com" por tu dominio real

# Activar sitio
sudo ln -s /etc/nginx/sites-available/zona-scraper /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 7. Ajustar permisos

```bash
sudo chown -R www-data:www-data /var/www/zona-prop-scraper
sudo chmod -R 755 /var/www/zona-prop-scraper
```

## Verificación

### Health Check
```bash
curl http://localhost:5000/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "timestamp": "2026-01-15T12:00:00.000000"
}
```

### Test de Scraping
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zonaprop.com.ar/departamentos-alquiler-monte-grande.html"
  }'
```

## Logs

### Logs de la aplicación
```bash
# Logs de Gunicorn
tail -f /var/www/zona-prop-scraper/logs/access.log
tail -f /var/www/zona-prop-scraper/logs/error.log

# Logs de systemd
sudo journalctl -u zona-scraper -f
```

### Logs de Nginx
```bash
sudo tail -f /var/log/nginx/zona-scraper-access.log
sudo tail -f /var/log/nginx/zona-scraper-error.log
```

## Comandos Útiles

### Reiniciar servicio
```bash
sudo systemctl restart zona-scraper
```

### Ver estado
```bash
sudo systemctl status zona-scraper
```

### Detener servicio
```bash
sudo systemctl stop zona-scraper
```

### Ver logs en tiempo real
```bash
sudo journalctl -u zona-scraper -f
```

### Actualizar código
```bash
cd /var/www/zona-prop-scraper
git pull  # Si usas git
sudo systemctl restart zona-scraper
```

## Firewall

Si usas UFW, permitir HTTP/HTTPS:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## SSL/HTTPS con Let's Encrypt (Opcional)

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com

# Renovación automática ya está configurada
```

## Troubleshooting

### Servicio no inicia
```bash
# Ver logs detallados
sudo journalctl -u zona-scraper -n 50 --no-pager

# Verificar permisos
ls -la /var/www/zona-prop-scraper

# Verificar .env
cat /var/www/zona-prop-scraper/.env
```

### Error de conexión a BD
```bash
# Verificar que MySQL está corriendo
sudo systemctl status mysql

# Probar conexión manual
mysql -h localhost -u root -p
```

### Nginx error 502
```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status zona-scraper

# Verificar puerto 5000
sudo netstat -tulpn | grep 5000
```

## Seguridad

Recomendaciones:
1. Usar contraseñas seguras en `.env`
2. Configurar firewall (UFW)
3. Habilitar HTTPS con Let's Encrypt
4. Considerar autenticación API (API Keys)
5. Limitar rate limiting en Nginx
6. Actualizar sistema regularmente

## Monitoreo

Considerar herramientas:
- **Uptime monitoring**: UptimeRobot, Pingdom
- **Application monitoring**: Sentry, New Relic
- **Server monitoring**: Netdata, Prometheus
