# Invoice Query Backend

Backend API desarrollado con Django REST Framework para consultar facturas desde una tabla existente en base de datos.

## Descripción

Este proyecto expone un endpoint REST para consultar facturas almacenadas en la tabla `invoices`.

La tabla es externa/existente, por lo que el modelo `Invoice` usa:

```python
managed = False
```

Esto significa que Django no intentará crear, modificar ni migrar la tabla `invoices`.

## Tareas programadas

El sistema ejecuta una tarea programada diariamente usando Celery Beat.

### Email con top 10 de días con mayores ventas.

Todos los días a las 8:00 AM (hora de México), el sistema ejecuta una tarea background que:

- Consulta los 10 días con mayores ventas.
- Genera un resumen.
- Envía el reporte por email.

## Entorno

Esta aplicación backend fue desarrollada y probada utilizando:

- Ubuntu Linux
- Python 3
- pip

Se espera compatibilidad con macOS y Windows, aunque no fue validada formalmente durante el desarrollo.

## Tecnologías usadas

- Python
- Django
- Django REST Framework
- django-filter
- PostgreSQL
- Celery
- Redis

## Instalar Redis
Redis es requerido para ejecutar Celery y Celery Beat.

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install redis-server
```

### Verificar instalación

```bash
redis-cli ping
```

Respuesta esperada:

```txt
PONG
```

## Setup del proyecto

### 1. Crear entorno virtual
El siguiente comando debe ejecutarse en la carpeta invoice-query-backend.

```bash
python3 -m venv .venv
```

Si surge algún error en el comando anterior. Instalar `python-venv ejecutando el siguiente comando y volver a ejecutar el paso anterior:
```bash
sudo apt install python3.14-venv
```

### 2. Activar entorno virtual
El siguiente comando debe ejecutarse en la carpeta invoice-query-backend.
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias
El siguiente comando debe ejecutarse en la carpeta invoice-query-backend.
```bash
python3 -m pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` basado en `.env.example`, el siguiente comando debe ejecutarse en la carpeta invoice-query-backend.

```bash
cp .env.example .env
```

Ejemplo de variables necesarias:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
REPORT_RECIPIENT_EMAIL=recipient_email@example.com
```

### 5. Configuración de email

El proyecto utiliza SMTP de Gmail para enviar el reporte diario de ventas.

Variables requeridas:

```env
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
REPORT_RECIPIENT_EMAIL=recipient_email@example.com
```

### Gmail App Password

Para usar Gmail SMTP es necesario generar un App Password:

1. Activar 2FA en la cuenta Gmail.
2. Ir a Google Account Settings.
3. Security → App Passwords.
4. Generar una contraseña para la aplicación.

La contraseña generada debe usarse en:

```env
EMAIL_HOST_PASSWORD=your_app_password
```
ver más: https://youtu.be/srGxqsPwAlw?si=x5fHS7jld2UYaHZy

### Emails para desarrollo local

Para evitar enviar emails reales durante desarrollo, puede usarse en el archivo invoice-query-backend/app/app/settings.py la siguiente variable:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

Con esto los emails se imprimirán en consola.

### 6. Levantar servidor local
El siguiente comando debe ejecutarse en la carpeta invoice-query-backend/app y con el ambiente virtual encendido [Ir a la sección de activar entorno virtual](#2-activar-entorno-virtual).
```bash
python3 manage.py runserver
```

El backend quedará disponible en:

```txt
http://localhost:8000
```

## Ejecutar Celery

### 1. Levantar Redis
En una nueva terminal ejecutar:
```bash
redis-server
```

### 2. Levantar worker de Celery
El siguiente comando debe ejecutarse en una nueva terminal y dentro de la carpeta invoice-query-backend/app teniendo en cuenta que el ambiente virtual debe estar activo [Ir a la sección de activar entorno virtual](#2-activar-entorno-virtual).
```bash
celery -A app worker -l info
```

### 3. Levantar Celery Beat
El siguiente comando debe ejecutarse en una nueva terminal y dentro de la carpeta invoice-query-backend/app teniendo en cuenta que el ambiente virtual debe estar activo [Ir a la sección de activar entorno virtual](#2-activar-entorno-virtual).
```bash
celery -A app beat -l info
```

## Endpoint principal

```txt
GET /api/v1/invoices/
```

Ejemplo:

```bash
curl "http://localhost:8000/api/v1/invoices/"
```

## Filtros disponibles

La API permite filtrar por:

- `invoice_date__gte` (Filtrar invoices con fecha mayores a)
- `invoice_date__lte` (Filtrar invoices con fecha menores a)
- `active` (Si existe puede filtrar por facturas activas (true) o inactivas (false))

## Ejemplos de consultas

### Consultar todas las facturas

```bash
curl "http://localhost:8000/api/v1/invoices/"
```

### Consultar facturas activas

```bash
curl "http://localhost:8000/api/v1/invoices/?active=true"
```

### Consultar facturas inactivas

```bash
curl "http://localhost:8000/api/v1/invoices/?active=false"
```

### Consultar facturas desde una fecha

```bash
curl "http://localhost:8000/api/v1/invoices/?invoice_date__gte=2024-01-01"
```

### Consultar facturas hasta una fecha

```bash
curl "http://localhost:8000/api/v1/invoices/?invoice_date__lte=2024-12-31"
```

### Consultar facturas por rango de fechas

```bash
curl "http://localhost:8000/api/v1/invoices/?invoice_date__gte=2024-01-01&invoice_date__lte=2024-12-31"
```

### Consultar facturas activas por rango de fechas

```bash
curl "http://localhost:8000/api/v1/invoices/?active=true&invoice_date__gte=2024-01-01&invoice_date__lte=2024-12-31"
```

## Paginación

El proyecto usa paginación tipo `limit` y `offset`.

Ejemplo:

```bash
curl "http://localhost:8000/api/v1/invoices/?limit=10&offset=0"
```

Siguiente página:

```bash
curl "http://localhost:8000/api/v1/invoices/?limit=10&offset=10"
```

## Formato de respuesta

Ejemplo de respuesta:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/invoices/?limit=50&offset=50",
  "previous": null,
  "results": [
    {
      "id": 1,
      "invoice_number": "INV-001",
      "total": "1500.00",
      "invoice_date": "2024-01-15T10:30:00",
      "status": "paid",
      "active": true
    }
  ]
}
```

## Notas importantes

- La tabla `invoices` debe existir previamente en la base de datos.
- Django no administrará la tabla `invoices`.
- El endpoint principal está versionado usando URL versioning.
- La versión actual soportada es `v1`.
- Redis es necesario para ejecutar Celery y Celery Beat.


## Verificar cache en Redis
El proyecto utiliza Redis para cachear respuestas del endpoint de facturas.

### Entrar a la base de datos con el cache de Redis

```bash
redis-cli -n 1
```

### Ver keys almacenadas

```redis
KEYS *
```

Ejemplo de keys generadas por Django:

```txt
:1:views.decorators.cache.cache_page...
:1:views.decorators.cache.cache_header...
```

### Monitorear operaciones en tiempo real

```bash
redis-cli -n 1 monitor
```

Después ejecutar una request:

```bash
curl "http://localhost:8000/api/v1/invoices/?active=true"
```

Redis mostrará operaciones como:

```txt
GET ...
SET ...
EXPIRE ...
```

## Verificar Redis usado por Celery

Celery utiliza una base Redis distinta (`/0`).

Entrar:

```bash
redis-cli -n 0
```

Ver keys:

```redis
KEYS *
```

Ejemplo:

```txt
celery-task-meta-...
_kombu.binding...
```


## Ejecutar pruebas unitarias
### Ejecutar todas las pruebas
El siguiente comando debe ejecutarse en una nueva terminal y dentro de la carpeta invoice-query-backend/app teniendo en cuenta que el ambiente virtual debe estar activo [Ir a la sección de activar entorno virtual](#2-activar-entorno-virtual).
```bash
python3 manage.py test
```