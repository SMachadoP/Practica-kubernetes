"""
Backend API - Aplicación Flask para práctica de Kubernetes

Esta aplicación simula una API REST simple que:
- Devuelve información del sistema/pod
- Permite operaciones CRUD básicas en memoria
- Demuestra el uso de variables de entorno y ConfigMaps
"""

from flask import Flask, jsonify, request
import os
import socket
from datetime import datetime

app = Flask(__name__)

# Base de datos en memoria (para demostración)
tareas = []

# Variables de entorno que serán inyectadas por Kubernetes
APP_NAME = os.getenv('APP_NAME', 'Mi App Kubernetes')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
DB_HOST = os.getenv('DB_HOST', 'localhost')


@app.route('/')
def home():
    """
    Endpoint raíz - Muestra información del pod/contenedor
    Útil para verificar balanceo de carga y réplicas
    """
    return jsonify({
        'mensaje': f'¡Bienvenido a {APP_NAME}!',
        'hostname': socket.gethostname(),  # Nombre del pod en Kubernetes
        'ip': socket.gethostbyname(socket.gethostname()),
        'ambiente': ENVIRONMENT,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """
    Health Check - Usado por Kubernetes para liveness y readiness probes
    Kubernetes usa este endpoint para saber si el pod está saludable
    """
    return jsonify({
        'status': 'healthy',
        'service': 'backend-api',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/ready')
def ready():
    """
    Readiness Check - Indica si el servicio está listo para recibir tráfico
    Diferente al health check: puede estar vivo pero no listo
    """
    # Aquí podrías verificar conexiones a DB, cache, etc.
    return jsonify({
        'status': 'ready',
        'db_host': DB_HOST,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/info')
def info():
    """
    Muestra información de configuración
    Demuestra cómo las variables de entorno son inyectadas
    """
    return jsonify({
        'app_name': APP_NAME,
        'environment': ENVIRONMENT,
        'db_host': DB_HOST,
        'hostname': socket.gethostname(),
        # No exponer secretos en producción, esto es solo demo
        'secret_configured': SECRET_KEY != 'default-secret'
    })


# ============ CRUD de Tareas ============

@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    """Obtiene todas las tareas"""
    return jsonify({
        'tareas': tareas,
        'total': len(tareas),
        'servidor': socket.gethostname()
    })


@app.route('/tareas', methods=['POST'])
def crear_tarea():
    """Crea una nueva tarea"""
    data = request.get_json()
    if not data or 'titulo' not in data:
        return jsonify({'error': 'Se requiere el campo titulo'}), 400
    
    tarea = {
        'id': len(tareas) + 1,
        'titulo': data['titulo'],
        'completada': False,
        'creada_en': datetime.now().isoformat(),
        'creada_en_pod': socket.gethostname()
    }
    tareas.append(tarea)
    return jsonify(tarea), 201


@app.route('/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    """Actualiza una tarea existente"""
    tarea = next((t for t in tareas if t['id'] == id), None)
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    data = request.get_json()
    if 'titulo' in data:
        tarea['titulo'] = data['titulo']
    if 'completada' in data:
        tarea['completada'] = data['completada']
    
    return jsonify(tarea)


@app.route('/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    """Elimina una tarea"""
    global tareas
    tarea = next((t for t in tareas if t['id'] == id), None)
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    tareas = [t for t in tareas if t['id'] != id]
    return jsonify({'mensaje': 'Tarea eliminada', 'id': id})


@app.route('/stress')
def stress():
    """
    Endpoint para probar auto-scaling (HPA)
    Genera carga de CPU artificialmente
    """
    import math
    result = 0
    for i in range(1000000):
        result += math.sqrt(i)
    return jsonify({
        'mensaje': 'Cálculo intensivo completado',
        'resultado': result,
        'pod': socket.gethostname()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
