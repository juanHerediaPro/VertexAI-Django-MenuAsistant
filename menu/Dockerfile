# Usa una imagen base de Python ligera
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /usr/src/app

# Copia e instala dependencias (incluyendo gunicorn, que debe estar en requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Recolecta archivos estáticos para que el contenedor los sirva
RUN python manage.py collectstatic --no-input

# Define el puerto que Cloud Run debe usar
ENV PORT 8080
# Comando de inicio con Gunicorn
CMD exec gunicorn --bind :$PORT --workers 2 config.wsgi