# ====================================================
# Dockerfile para Backend API (Python Flask)
# ====================================================
# Este archivo define cómo construir la imagen del contenedor
# para nuestra aplicación backend

# Imagen base: Python 3.11 en Alpine Linux (liviana ~50MB)
# Alpine reduce el tamaño final de la imagen considerablemente
FROM python:3.11-alpine

# LABEL: Metadatos de la imagen (buena práctica)
LABEL maintainer="tu-email@ejemplo.com"
LABEL description="Backend API para práctica de Kubernetes"
LABEL version="1.0"

# WORKDIR: Establece el directorio de trabajo dentro del contenedor
# Todos los comandos siguientes se ejecutarán desde este directorio
WORKDIR /app

# Copiar primero requirements.txt (optimización de caché de Docker)
# Si requirements.txt no cambia, Docker usa la capa en caché
COPY requirements.txt .

# RUN: Ejecuta comandos durante la construcción de la imagen
# --no-cache-dir: No guarda caché de pip (reduce tamaño de imagen)
RUN pip install --no-cache-dir -r requirements.txt

# COPY: Copia el código fuente al contenedor
# El punto (.) significa "directorio actual" en ambos lados
COPY . .

# ENV: Variables de entorno por defecto
# Pueden ser sobrescritas en Kubernetes con env o configMapRef
ENV PORT=5000
ENV FLASK_DEBUG=false

# EXPOSE: Documenta el puerto que usa la aplicación
# No abre el puerto, solo es documentación (el puerto se abre con -p)
EXPOSE 5000

# USER: Por seguridad, no ejecutar como root
# Primero creamos un usuario no privilegiado
RUN adduser -D appuser
USER appuser

# CMD: Comando que se ejecuta cuando inicia el contenedor
# Usamos gunicorn en producción (más robusto que el servidor de Flask)
# -w 4: 4 workers (procesos)
# -b 0.0.0.0:5000: Escuchar en todas las interfaces, puerto 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
