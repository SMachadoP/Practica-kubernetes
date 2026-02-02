# ====================================================
# Dockerfile para Frontend (Nginx)
# ====================================================
# Este archivo define cómo construir la imagen del contenedor
# para servir el frontend con Nginx

# Imagen base: Nginx en Alpine Linux (muy liviana ~25MB)
FROM nginx:alpine

# LABEL: Metadatos de la imagen
LABEL maintainer="tu-email@ejemplo.com"
LABEL description="Frontend para práctica de Kubernetes"
LABEL version="1.0"

# Eliminar la configuración por defecto de Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copiar archivos estáticos al directorio de Nginx
COPY index.html /usr/share/nginx/html/

# Copiar configuración personalizada de Nginx
# Esta configuración incluye el proxy reverso al backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

# EXPOSE: Puerto 80 (HTTP estándar)
EXPOSE 80

# El comando por defecto de la imagen nginx ya ejecuta nginx
# No necesitamos especificar CMD
