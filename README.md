abrir docker desktop
minikube start
minikube dashboard
1:
# Crear el deployment directamente desde la consola
kubectl create deployment hello-deployment --image=nginxdemos/hello:latest
# Verificar que el deployment se creó correctamente
kubectl get deployments
# Ver el pod en ejecución
kubectl get pods
# Ver detalles del deployment
kubectl describe deployment hello-deployment
2:
# Exponer el deployment como servicio ClusterIP 
kubectl expose deployment hello-deployment --port=80  --type=ClusterIP            opcional para renombrar --name=hello-service
# Verificar el servicio
kubectl get services
# Ver detalles del servicio
kubectl describe service hello-deployment

# Obtener la IP del servicio
kubectl get svc hello-deployment
# Probar desde dentro del clúster usando un pod temporal Este te muestra "la bola de cosas" = el HTML completo
kubectl run curl-test --image=curlimages/curl -i --rm --restart=Never -- curl http://hello-deployment
# O ver los endpoints del servicio Este te muestra solo la IP:puerto
kubectl get endpoints hello-deployment

# OPCIÓN 2: O editar interactivamente (se abre un editor)
kubectl edit service hello-deployment
# Cambiar la línea: type: ClusterIP por type: NodePort
# Guardar y salir
# Verificar el cambio y ver el puerto asignado
kubectl get svc hello-deployment
# Ver detalles completos incluyendo el NodePort
kubectl describe service hello-deployment

# Si usas minikube
x minikube ip
minikube service hello-service --url
# Probar acceso (reemplaza <NODE_IP> y <NODE_PORT> con tus valores)
curl http://<NODE_IP>:<NODE_PORT>
# Abrir en el navegador con minikube
minikube service hello-service
3:
# Escalar a 4 réplicas
kubectl scale deployment hello-deployment --replicas=4
# Verificar el escalado inmediatamente
kubectl get deployment hello-deployment
# Ver todos los pods creados
kubectl get pods
# Observar el proceso de escalado en tiempo real (Ctrl+C para salir)
kubectl get pods -w
# Verificar que todas las réplicas están listas
kubectl rollout status deployment hello-deployment
# Ver detalles del deployment incluyendo réplicas
kubectl describe deployment hello-deployment
4:
# Actualizar la imagen del deployment a nginx:alpine
kubectl set image deployment/hello-deployment hello=nginx:alpine
# Observar el proceso de actualización en tiempo real
kubectl rollout status deployment hello-deployment
# Confirmar que los pods están corriendo con la nueva imagen
kubectl get deployment hello-deployment -o wide


# 🚀 Práctica de Kubernetes con Minikube

Este repositorio contiene una práctica completa para aprender Kubernetes desde cero utilizando Minikube. Incluye una aplicación full-stack (backend + frontend) con todos los manifiestos de Kubernetes necesarios.

---

Actua como experto en Sistemas distribuidos. Especialmente en kubernetes con minikube. Crea esta practica en la carpeta que tengo en tu entorno scratch. no quiero que me muestres plan de implementacion y pidas aprobacion, quiero que directamente hagas la practica. Ten en cuenta que debe de inicialmente funcionar con docker compose y luego transformar a kubernetes con el Kompose. Tiene que ser muy sencillo, poco codigo solo lo necesario, no pongas nada inservible solo por adornar, ten en cuenta que voy a tener que sustentar asi que debe ser muy sencillo. Tambien debes crear un readmi explicando que hace cada cosa de la practica y tambien debe estar todos los comandos que voy a necesitar para correr la transformacion a kubernetes, teniendo en cuenta que los archivos .yaml deberian crearse en una carpeta llamada k8s. Y tambien los comandos para ejecutar y probar.

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Prerrequisitos](#prerrequisitos)
5. [Comandos de Docker](#comandos-de-docker)
6. [Comandos de Kubernetes](#comandos-de-kubernetes)
7. [Pasos para Ejecutar el Proyecto](#pasos-para-ejecutar-el-proyecto)
8. [Explicación de Cada Archivo](#explicación-de-cada-archivo)
9. [Escenarios de Práctica](#escenarios-de-práctica)
10. [Troubleshooting](#troubleshooting)
11. [Recursos Adicionales](#recursos-adicionales)

---

## 📖 Descripción del Proyecto

Este proyecto es una aplicación de práctica que consiste en:

- **Backend**: API REST en Python/Flask que simula operaciones CRUD de tareas
- **Frontend**: Interfaz web en HTML/JS servida por Nginx

La aplicación demuestra los siguientes conceptos de Kubernetes:
- Deployments y ReplicaSets
- Services (ClusterIP, NodePort)
- ConfigMaps y Secrets
- Ingress
- Horizontal Pod Autoscaler (HPA)
- Persistent Volume Claims (PVC)
- Resource Quotas y Limit Ranges
- Network Policies
- Jobs y CronJobs

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLUSTER KUBERNETES                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Namespace: prackube                       ││
│  │                                                              ││
│  │  ┌──────────────┐      ┌──────────────┐                     ││
│  │  │   Ingress    │      │  ConfigMap   │                     ││
│  │  │  (opcional)  │      │   Secrets    │                     ││
│  │  └──────┬───────┘      └──────────────┘                     ││
│  │         │                      │                             ││
│  │         ▼                      │                             ││
│  │  ┌──────────────┐             │                             ││
│  │  │   Service    │             │                             ││
│  │  │  (NodePort)  │             │                             ││
│  │  │  frontend    │             │                             ││
│  │  └──────┬───────┘             │                             ││
│  │         │                      │                             ││
│  │         ▼                      │                             ││
│  │  ┌──────────────┐             │                             ││
│  │  │  Deployment  │             │                             ││
│  │  │  frontend    │             │                             ││
│  │  │  (Nginx)     │             │                             ││
│  │  │  ┌────┬────┐ │             │                             ││
│  │  │  │Pod1│Pod2│ │             │                             ││
│  │  └──┴────┴────┴─┘             │                             ││
│  │         │                      │                             ││
│  │         │ /api                 │                             ││
│  │         ▼                      ▼                             ││
│  │  ┌──────────────┐      ┌──────────────┐                     ││
│  │  │   Service    │◄─────│  Deployment  │                     ││
│  │  │  (ClusterIP) │      │   backend    │                     ││
│  │  │   backend    │      │   (Flask)    │                     ││
│  │  └──────────────┘      │  ┌────┬────┐ │                     ││
│  │                        │  │Pod1│Pod2│ │                     ││
│  │                        └──┴────┴────┴─┘                     ││
│  │                               ▲                              ││
│  │                               │                              ││
│  │                        ┌──────┴──────┐                      ││
│  │                        │     HPA     │                      ││
│  │                        │ (autoscaler)│                      ││
│  │                        └─────────────┘                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ :30080
                              ▼
                    ┌──────────────────┐
                    │   Tu Navegador   │
                    │  localhost:30080 │
                    └──────────────────┘
```

---

## 📁 Estructura del Proyecto

```
prackube/
├── backend/
│   ├── app.py              # Aplicación Flask (API REST)
│   ├── requirements.txt    # Dependencias de Python
│   └── Dockerfile          # Imagen Docker del backend
├── frontend/
│   ├── index.html          # Interfaz web
│   ├── nginx.conf          # Configuración de Nginx
│   └── Dockerfile          # Imagen Docker del frontend
├── k8s/
│   ├── 01-namespace.yaml       # Namespace aislado
│   ├── 02-configmap.yaml       # Configuración de la app
│   ├── 03-secret.yaml          # Datos sensibles
│   ├── 04-deployment-backend.yaml  # Deployment del backend
│   ├── 05-deployment-frontend.yaml # Deployment del frontend
│   ├── 06-service.yaml         # Services para networking
│   ├── 07-ingress.yaml         # Ingress para routing HTTP
│   ├── 08-hpa.yaml             # Autoscaling horizontal
│   ├── 09-pvc.yaml             # Almacenamiento persistente
│   ├── 10-resource-quota.yaml  # Límites de recursos
│   ├── 11-network-policy.yaml  # Políticas de red
│   └── 12-job-cronjob.yaml     # Jobs programados
└── README.md
```

---

## ✅ Prerrequisitos

### Software necesario:

1. **Docker Desktop** o **Docker Engine**
   ```powershell
   # Verificar instalación
   docker --version
   ```

2. **Minikube**
   ```powershell
   # Instalar con Chocolatey (Windows)
   choco install minikube
   
   # O descargar de: https://minikube.sigs.k8s.io/docs/start/
   
   # Verificar instalación
   minikube version
   ```

3. **kubectl** (cliente de Kubernetes)
   ```powershell
   # Instalar con Chocolatey
   choco install kubernetes-cli
   
   # Verificar instalación
   kubectl version --client
   ```

---

## 🐳 Comandos de Docker

### Comandos Básicos

| Comando | Descripción |
|---------|-------------|
| `docker build -t nombre:tag .` | Construir imagen desde Dockerfile |
| `docker images` | Listar imágenes locales |
| `docker run -p 8080:80 imagen` | Ejecutar contenedor mapeando puertos |
| `docker ps` | Listar contenedores corriendo |
| `docker ps -a` | Listar todos los contenedores |
| `docker stop <id>` | Detener un contenedor |
| `docker rm <id>` | Eliminar un contenedor |
| `docker rmi <imagen>` | Eliminar una imagen |
| `docker logs <id>` | Ver logs de un contenedor |
| `docker exec -it <id> sh` | Ejecutar shell en contenedor |

### Comandos para este Proyecto

```powershell
# Construir imagen del backend
docker build -t prackube-backend:latest ./backend

# Construir imagen del frontend
docker build -t prackube-frontend:latest ./frontend

# Probar backend localmente (sin Kubernetes)
docker run -p 5000:5000 prackube-backend:latest

# Probar frontend localmente
docker run -p 8080:80 prackube-frontend:latest

# Ver imágenes creadas
docker images | findstr prackube
```

---

## ☸️ Comandos de Kubernetes

### Comandos de Minikube

| Comando | Descripción |
|---------|-------------|
| `minikube start` | Iniciar cluster de Minikube |
| `minikube start --driver=docker` | Iniciar con driver específico |
| `minikube stop` | Detener el cluster |
| `minikube delete` | Eliminar el cluster completamente |
| `minikube status` | Ver estado del cluster |
| `minikube ip` | Obtener IP del cluster |
| `minikube dashboard` | Abrir dashboard web de Kubernetes |
| `minikube addons list` | Listar addons disponibles |
| `minikube addons enable <addon>` | Habilitar un addon |
| `minikube service <nombre> -n <ns>` | Abrir servicio en navegador |
| `minikube ssh` | Conectar por SSH al nodo |
| `minikube logs` | Ver logs de Minikube |

### Comandos de kubectl - Información

| Comando | Descripción |
|---------|-------------|
| `kubectl cluster-info` | Información del cluster |
| `kubectl get nodes` | Listar nodos del cluster |
| `kubectl get all -n <namespace>` | Listar todos los recursos |
| `kubectl get pods -n <namespace>` | Listar pods |
| `kubectl get pods -o wide` | Listar pods con más detalles |
| `kubectl get deployments` | Listar deployments |
| `kubectl get services` | Listar services |
| `kubectl get configmaps` | Listar configmaps |
| `kubectl get secrets` | Listar secrets |
| `kubectl get ingress` | Listar ingress |
| `kubectl get hpa` | Listar autoscalers |
| `kubectl get pvc` | Listar persistent volume claims |
| `kubectl get events` | Ver eventos del cluster |
| `kubectl get namespaces` | Listar namespaces |

### Comandos de kubectl - Aplicar/Crear

| Comando | Descripción |
|---------|-------------|
| `kubectl apply -f archivo.yaml` | Aplicar configuración |
| `kubectl apply -f directorio/` | Aplicar todos los YAML de un directorio |
| `kubectl create namespace nombre` | Crear namespace |
| `kubectl delete -f archivo.yaml` | Eliminar recursos definidos en YAML |
| `kubectl delete pod <nombre>` | Eliminar un pod específico |
| `kubectl delete deployment <nombre>` | Eliminar un deployment |

### Comandos de kubectl - Debugging

| Comando | Descripción |
|---------|-------------|
| `kubectl describe pod <nombre>` | Detalles completos de un pod |
| `kubectl describe deployment <nombre>` | Detalles de un deployment |
| `kubectl describe service <nombre>` | Detalles de un service |
| `kubectl logs <pod>` | Ver logs de un pod |
| `kubectl logs <pod> -f` | Seguir logs en tiempo real |
| `kubectl logs <pod> -c <container>` | Logs de contenedor específico |
| `kubectl logs <pod> --previous` | Logs del contenedor anterior (crash) |
| `kubectl exec -it <pod> -- /bin/sh` | Shell interactivo en pod |
| `kubectl exec <pod> -- comando` | Ejecutar comando en pod |
| `kubectl port-forward <pod> 8080:80` | Reenvío de puertos local |
| `kubectl top pods` | Ver uso de CPU/memoria |
| `kubectl top nodes` | Ver recursos de nodos |

### Comandos de kubectl - Escalado

| Comando | Descripción |
|---------|-------------|
| `kubectl scale deployment <nombre> --replicas=5` | Escalar manualmente |
| `kubectl autoscale deployment <nombre> --min=2 --max=10 --cpu-percent=50` | Configurar HPA |
| `kubectl rollout status deployment <nombre>` | Ver estado de despliegue |
| `kubectl rollout history deployment <nombre>` | Ver historial de versiones |
| `kubectl rollout undo deployment <nombre>` | Revertir a versión anterior |
| `kubectl rollout restart deployment <nombre>` | Reiniciar pods gradualmente |

### Comandos de kubectl - Namespace

| Comando | Descripción |
|---------|-------------|
| `kubectl config set-context --current --namespace=<ns>` | Cambiar namespace por defecto |
| `kubectl get pods -n prackube` | Listar pods en namespace específico |
| `kubectl get all --all-namespaces` | Listar todo en todos los namespaces |

---

## 🚀 Pasos para Ejecutar el Proyecto

### Paso 1: Iniciar Minikube

```powershell
# Iniciar cluster (primera vez puede tardar varios minutos)
minikube start --driver=docker

# Verificar que está corriendo
minikube status

# Habilitar addons necesarios
minikube addons enable metrics-server    # Para HPA
minikube addons enable ingress           # Para Ingress (opcional)
```

### Paso 2: Configurar Docker para usar Minikube

```powershell
# IMPORTANTE: Ejecutar esto en la terminal donde construirás las imágenes
# Esto hace que Docker use el daemon de Minikube

# En PowerShell:
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# En CMD:
@FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i

# Verificar (deberías ver imágenes de Kubernetes)
docker images
```

### Paso 3: Construir las Imágenes Docker

```powershell
# Navegar al directorio del proyecto
cd c:\Users\salej\Desktop\prackube

# Construir imagen del backend
docker build -t prackube-backend:latest ./backend

# Construir imagen del frontend
docker build -t prackube-frontend:latest ./frontend

# Verificar que las imágenes se crearon
docker images | findstr prackube
```

### Paso 4: Desplegar en Kubernetes

```powershell
# Aplicar los manifiestos en orden
# Opción 1: Aplicar todos de una vez
kubectl apply -f ./k8s/

# Opción 2: Aplicar uno por uno (recomendado para aprender)
kubectl apply -f ./k8s/01-namespace.yaml
kubectl apply -f ./k8s/02-configmap.yaml
kubectl apply -f ./k8s/03-secret.yaml
kubectl apply -f ./k8s/04-deployment-backend.yaml
kubectl apply -f ./k8s/05-deployment-frontend.yaml
kubectl apply -f ./k8s/06-service.yaml

# Opcional (comentar/descomentar según necesites)
kubectl apply -f ./k8s/07-ingress.yaml       # Requiere addon ingress
kubectl apply -f ./k8s/08-hpa.yaml           # Requiere metrics-server
kubectl apply -f ./k8s/09-pvc.yaml           # Almacenamiento
kubectl apply -f ./k8s/10-resource-quota.yaml
# kubectl apply -f ./k8s/11-network-policy.yaml  # Requiere CNI especial
kubectl apply -f ./k8s/12-job-cronjob.yaml
```

### Paso 5: Verificar el Despliegue

```powershell
# Ver todos los recursos en el namespace
kubectl get all -n prackube

# Esperar a que los pods estén Ready
kubectl get pods -n prackube -w   # -w para watch (Ctrl+C para salir)

# Ver logs del backend
kubectl logs -n prackube -l app=backend

# Ver logs del frontend
kubectl logs -n prackube -l app=frontend
```

### Paso 6: Acceder a la Aplicación

```powershell
# Opción 1: Usando minikube service (abre navegador automáticamente)
minikube service frontend-service -n prackube

# Opción 2: Obtener URL manualmente
minikube service frontend-service -n prackube --url
# Luego abrir esa URL en el navegador

# Opción 3: Port-forward (si las anteriores no funcionan)
kubectl port-forward -n prackube service/frontend-service 8080:80
# Abrir http://localhost:8080

# Opción 4: Con NodePort directamente
minikube ip
# Abrir http://<minikube-ip>:30080
```

### Paso 7: Probar la Aplicación

Una vez en el navegador:
1. Verifica que el estado del backend sea "Conectado"
2. Crea algunas tareas
3. Observa en qué pod se crean (balanceo de carga)
4. Ejecuta el test de estrés para ver el HPA en acción

---

## 📚 Explicación de Cada Archivo

### Backend (`backend/`)

#### `app.py`
Aplicación Flask que implementa:
- **`GET /`**: Retorna información del pod (hostname, IP) - útil para ver load balancing
- **`GET /health`**: Endpoint de liveness probe - Kubernetes verifica si el contenedor está vivo
- **`GET /ready`**: Endpoint de readiness probe - indica si puede recibir tráfico
- **`GET /info`**: Muestra configuración desde ConfigMaps y Secrets
- **`GET/POST/PUT/DELETE /tareas`**: CRUD de tareas en memoria
- **`GET /stress`**: Genera carga de CPU para probar autoscaling

#### `Dockerfile`
- **FROM**: Imagen base Python Alpine (liviana)
- **WORKDIR**: Directorio de trabajo `/app`
- **COPY requirements.txt + RUN pip install**: Instala dependencias (optimiza caché Docker)
- **COPY .**: Copia código fuente
- **USER**: Ejecuta como usuario no-root (seguridad)
- **CMD**: Inicia gunicorn (servidor WSGI de producción)

### Frontend (`frontend/`)

#### `index.html`
Interfaz web que:
- Muestra estado de conexión con backend
- Permite gestionar tareas (CRUD)
- Visualiza ConfigMaps/Secrets en uso
- Ejecuta tests de estrés para probar HPA
- Muestra qué pod responde cada petición

#### `nginx.conf`
Configuración de Nginx:
- Sirve archivos estáticos en `/`
- Proxy reverso a `backend-service:5000` para `/api/*`
- Endpoint `/nginx-health` para health checks

### Kubernetes (`k8s/`)

#### `01-namespace.yaml`
**Namespace**: Espacio aislado para organizar recursos. Permite:
- Separar ambientes (dev, staging, prod)
- Aplicar quotas por namespace
- Gestionar permisos (RBAC)

#### `02-configmap.yaml`
**ConfigMap**: Almacena configuración como pares clave-valor:
- `APP_NAME`: Nombre de la aplicación
- `ENVIRONMENT`: Ambiente actual
- `DB_HOST`: Host de base de datos
- Se inyectan como variables de entorno en los pods

#### `03-secret.yaml`
**Secret**: Similar a ConfigMap pero para datos sensibles:
- Valores codificados en base64
- `SECRET_KEY`, `DB_USER`, `DB_PASSWORD`
- Nunca exponer en logs o interfaces

#### `04-deployment-backend.yaml`
**Deployment**: Gestiona pods del backend:
- `replicas: 2`: Mantiene 2 pods corriendo
- `selector`: Identifica qué pods gestiona
- `strategy`: RollingUpdate sin downtime
- `containers`: Define la imagen y puertos
- `env`: Variables de entorno desde ConfigMap/Secret
- `resources`: Límites de CPU/memoria
- `livenessProbe`: Reinicia si `/health` falla
- `readinessProbe`: Remueve del Service si `/ready` falla

#### `05-deployment-frontend.yaml`
**Deployment**: Similar al backend pero para Nginx/frontend.

#### `06-service.yaml`
**Service**: Expone pods como servicio de red:
- `backend-service` (ClusterIP): Solo accesible dentro del cluster
- `frontend-service` (NodePort): Accesible desde fuera en puerto 30080
- El nombre del servicio actúa como DNS interno

#### `07-ingress.yaml`
**Ingress**: Enrutamiento HTTP avanzado:
- Enruta por dominio o path
- Requiere `minikube addons enable ingress`
- Permite múltiples servicios en un solo punto de entrada

#### `08-hpa.yaml`
**HorizontalPodAutoscaler**: Escala automáticamente:
- Monitorea CPU/memoria de pods
- Escala entre `minReplicas` y `maxReplicas`
- `targetUtilization: 50%`: Escala si CPU > 50%

#### `09-pvc.yaml`
**PersistentVolumeClaim**: Solicita almacenamiento:
- Datos persisten aunque el pod se elimine
- `accessModes`: RWO (un nodo puede escribir)
- `storage: 1Gi`: Solicita 1GB

#### `10-resource-quota.yaml`
**ResourceQuota**: Límites por namespace:
- Máximo de CPU, memoria, pods, services
- Evita que un equipo consuma todo el cluster

**LimitRange**: Límites por pod/contenedor:
- Valores por defecto si no se especifican
- Rangos válidos (min/max)

#### `11-network-policy.yaml`
**NetworkPolicy**: Control de tráfico de red:
- Define qué pods pueden comunicarse
- Por defecto todo está permitido
- Requiere CNI compatible (Calico, Cilium)

#### `12-job-cronjob.yaml`
**Job**: Tarea que corre hasta completarse:
- `completions`: Cuántas veces debe completarse
- `parallelism`: Pods simultáneos

**CronJob**: Job programado:
- `schedule`: Formato cron (ej: `*/5 * * * *`)
- Útil para backups, limpieza, reportes

---

## 🎯 Escenarios de Práctica

### Escenario 1: Escalar Manualmente

```powershell
# Escalar a 5 réplicas
kubectl scale deployment backend-deployment -n prackube --replicas=5

# Ver los pods creándose
kubectl get pods -n prackube -w

# Probar balanceo de carga (abrir la app y hacer requests)
# Observar diferentes hostnames respondiendo

# Volver a 2 réplicas
kubectl scale deployment backend-deployment -n prackube --replicas=2
```

### Escenario 2: Probar Autoscaling (HPA)

```powershell
# Asegurarse que metrics-server está habilitado
minikube addons enable metrics-server

# Aplicar HPA
kubectl apply -f ./k8s/08-hpa.yaml

# Ver estado del HPA
kubectl get hpa -n prackube -w

# En otra terminal, generar carga
kubectl run -n prackube load-test --rm -it --image=busybox -- /bin/sh
# Dentro del pod:
while true; do wget -q -O- http://backend-service:5000/stress; done

# Observar cómo escala (puede tardar 1-2 minutos)
kubectl get pods -n prackube -w
kubectl get hpa -n prackube -w
```

### Escenario 3: Simular Fallo de Pod

```powershell
# Ver pods actuales
kubectl get pods -n prackube

# Eliminar un pod del backend
kubectl delete pod -n prackube -l app=backend --wait=false

# Ver cómo Kubernetes recrea el pod automáticamente
kubectl get pods -n prackube -w

# El Deployment siempre mantiene el número deseado de réplicas
```

### Escenario 4: Rolling Update

```powershell
# Modificar la imagen (simulación de nueva versión)
kubectl set image deployment/backend-deployment -n prackube \
  backend=prackube-backend:v2

# Ver el rollout
kubectl rollout status deployment/backend-deployment -n prackube

# Ver historial
kubectl rollout history deployment/backend-deployment -n prackube

# Revertir a versión anterior
kubectl rollout undo deployment/backend-deployment -n prackube
```

### Escenario 5: Modificar ConfigMap en Caliente

```powershell
# Editar ConfigMap
kubectl edit configmap backend-config -n prackube
# Cambiar APP_NAME a otro valor

# Los pods actuales NO ven el cambio automáticamente
# Opción 1: Reiniciar pods gradualmente
kubectl rollout restart deployment/backend-deployment -n prackube

# Opción 2: Eliminar pods (se recrean con nueva config)
kubectl delete pods -n prackube -l app=backend
```

### Escenario 6: Usar Diferentes Namespaces

```powershell
# Crear namespace de producción
kubectl create namespace prackube-prod

# Copiar recursos a nuevo namespace (modificar namespace en YAMLs)
# O usar herramientas como Kustomize para gestionar ambientes

# Cambiar namespace por defecto
kubectl config set-context --current --namespace=prackube-prod
```

### Escenario 7: Depurar un Pod Problemático

```powershell
# Ver eventos del pod
kubectl describe pod <nombre-pod> -n prackube

# Ver logs
kubectl logs <nombre-pod> -n prackube

# Ejecutar shell en el pod
kubectl exec -it <nombre-pod> -n prackube -- /bin/sh

# Dentro del pod, verificar conectividad
wget -qO- http://backend-service:5000/health
env | grep APP_
```

### Escenario 8: Practicar con Jobs

```powershell
# Crear un Job manual
kubectl apply -f ./k8s/12-job-cronjob.yaml

# Ver Jobs
kubectl get jobs -n prackube

# Ver pods creados por el Job
kubectl get pods -n prackube -l app=demo-job

# Ver logs del Job
kubectl logs -n prackube -l app=demo-job

# Ver CronJobs
kubectl get cronjobs -n prackube

# Ejecutar CronJob manualmente
kubectl create job --from=cronjob/demo-cronjob manual-run -n prackube
```

### Escenario 9: Cambiar a Producción

Para simular un ambiente de producción, modifica:

1. **ConfigMap** (`02-configmap.yaml`):
```yaml
data:
  ENVIRONMENT: "production"
  FLASK_DEBUG: "false"
```

2. **Deployment** - Aumentar réplicas y recursos:
```yaml
spec:
  replicas: 3
  template:
    spec:
      containers:
        - resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "1"
```

3. **HPA** - Ajustar límites:
```yaml
spec:
  minReplicas: 3
  maxReplicas: 20
```

### Escenario 10: Practicar con Ingress

```powershell
# Habilitar Ingress en Minikube
minikube addons enable ingress

# Aplicar Ingress
kubectl apply -f ./k8s/07-ingress.yaml

# Obtener IP de Minikube
minikube ip

# Agregar entrada a C:\Windows\System32\drivers\etc\hosts (como Admin)
# <minikube-ip> prackube.local

# Acceder via: http://prackube.local
```

---

## 🔧 Troubleshooting

### Problema: Pods en estado "ImagePullBackOff"

```powershell
# Causa: La imagen no existe en el registry de Minikube
# Solución: Construir la imagen dentro del contexto de Minikube

# Configurar Docker para usar Minikube
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Reconstruir imágenes
docker build -t prackube-backend:latest ./backend
docker build -t prackube-frontend:latest ./frontend
```

### Problema: Pods en estado "CrashLoopBackOff"

```powershell
# Ver logs del pod
kubectl logs <pod-name> -n prackube

# Ver logs del contenedor anterior (si crasheó)
kubectl logs <pod-name> -n prackube --previous

# Verificar eventos
kubectl describe pod <pod-name> -n prackube
```

### Problema: No puedo acceder al servicio

```powershell
# Verificar que los pods están Running
kubectl get pods -n prackube

# Verificar el servicio
kubectl get svc -n prackube
kubectl describe svc frontend-service -n prackube

# Usar port-forward como alternativa
kubectl port-forward -n prackube svc/frontend-service 8080:80
```

### Problema: HPA no escala

```powershell
# Verificar que metrics-server está habilitado
minikube addons enable metrics-server

# Esperar 1-2 minutos para que colecte métricas
kubectl top pods -n prackube

# Verificar estado del HPA
kubectl describe hpa backend-hpa -n prackube
```

### Problema: ConfigMap/Secret no se actualiza en pods

```powershell
# Los pods no ven cambios automáticamente en ConfigMaps/Secrets
# Reiniciar el deployment para aplicar cambios
kubectl rollout restart deployment/backend-deployment -n prackube
```

---

## � Convertir Docker Compose a Kubernetes con Kompose

### ¿Qué es Kompose?

**Kompose** es una herramienta oficial que convierte archivos `docker-compose.yml` a manifiestos de Kubernetes automáticamente. Es útil para:
- Migrar aplicaciones existentes de Docker Compose a Kubernetes
- Generar una base de YAML que luego puedes personalizar
- Aprender cómo se mapean los conceptos de Docker a Kubernetes

### Instalación de Kompose

```powershell
# Opción 1: Con Chocolatey (Windows)
choco install kompose

# Opción 2: Descargar binario directamente
# Ir a: https://github.com/kubernetes/kompose/releases
# Descargar kompose-windows-amd64.exe y renombrar a kompose.exe

# Verificar instalación
kompose version
```

### Comandos de Kompose

| Comando | Descripción |
|---------|-------------|
| `kompose convert` | Convierte docker-compose.yml a YAML de Kubernetes |
| `kompose convert -o directorio/` | Guarda los YAML en un directorio específico |
| `kompose convert -f archivo.yml` | Especifica un archivo compose diferente |
| `kompose convert --stdout` | Muestra el YAML en consola sin crear archivos |
| `kompose convert -c` | Genera Helm Chart en vez de YAML |
| `kompose up` | Convierte Y despliega directamente en Kubernetes |
| `kompose down` | Elimina los recursos creados con `kompose up` |

### Usar Kompose con este Proyecto

```powershell
# 1. Navegar al proyecto
cd c:\Users\salej\Desktop\prackube

# 2. Convertir a Kubernetes (genera archivos en el directorio actual)
kompose convert

# 3. O guardar en un directorio separado para comparar
kompose convert -o k8s-generado/

# 4. Ver qué generaría sin crear archivos
kompose convert --stdout

# 5. Aplicar directamente sin generar archivos
kompose up

# 6. Eliminar lo desplegado
kompose down
```

### Ejemplo: Conversión del docker-compose.yml

El archivo `docker-compose.yml` de este proyecto:

```yaml
services:
  backend:
    image: prackube-backend:latest
    ports:
      - "5000:5000"
    environment:
      - APP_NAME=Mi App
    deploy:
      replicas: 2
```

Se convierte automáticamente a:

```yaml
# backend-deployment.yaml (generado por Kompose)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
        - name: backend
          image: prackube-backend:latest
          ports:
            - containerPort: 5000
          env:
            - name: APP_NAME
              value: "Mi App"
---
# backend-service.yaml (generado por Kompose)
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    app: backend
```

### Labels especiales de Kompose

Puedes usar labels en docker-compose.yml para controlar la conversión:

```yaml
services:
  frontend:
    image: mi-frontend
    labels:
      # Tipo de Service
      kompose.service.type: NodePort
      kompose.service.nodeport.port: "30080"
      
      # Política de imagen
      kompose.image-pull-policy: Never
      
      # Exponer como Ingress
      kompose.service.expose: "true"
      kompose.service.expose.ingress-class-name: "nginx"
      
      # Volúmenes
      kompose.volume.size: 1Gi
```

### Mapeo Docker Compose → Kubernetes

| Docker Compose | Kubernetes |
|----------------|------------|
| `services` | Deployment + Service |
| `ports` | Service ports + containerPort |
| `environment` | env en el container |
| `volumes` | PersistentVolumeClaim |
| `deploy.replicas` | spec.replicas |
| `deploy.resources` | resources.limits/requests |
| `healthcheck` | livenessProbe (parcial) |
| `depends_on` | ❌ No hay equivalente directo |
| `networks` | ❌ Ignorado (K8s maneja diferente) |

### ⚠️ Limitaciones de Kompose

Kompose **NO genera** automáticamente:

| Recurso | Debes crear manualmente |
|---------|------------------------|
| **HPA** | Horizontal Pod Autoscaler para autoescalado |
| **Ingress avanzado** | Routing por dominio, TLS, etc. |
| **Network Policies** | Reglas de firewall entre pods |
| **Resource Quotas** | Límites por namespace |
| **Secrets** | Manejo seguro de contraseñas |
| **Jobs/CronJobs** | Tareas programadas |
| **Readiness Probes** | Solo genera liveness básico |
| **ConfigMaps** | Variables en archivos separados |

### Flujo recomendado

```
┌─────────────────────┐
│  docker-compose.yml │
└──────────┬──────────┘
           │
           ▼ kompose convert
┌─────────────────────┐
│  YAML básico        │
│  (Deployment +      │
│   Service)          │
└──────────┬──────────┘
           │
           ▼ Editar manualmente
┌─────────────────────┐
│  YAML completo      │
│  + HPA              │
│  + Ingress          │
│  + Probes           │
│  + ConfigMaps       │
│  + Secrets          │
└─────────────────────┘
```

### Comparar: Generado vs Manual

```powershell
# Generar con Kompose
kompose convert -o k8s-generado/

# Comparar archivos
# k8s-generado/backend-deployment.yaml  → Básico (~30 líneas)
# k8s/04-deployment-backend.yaml        → Completo (~100 líneas con comentarios)
```

Los archivos en `k8s/` de este proyecto incluyen:
- ✅ Comentarios educativos detallados
- ✅ Liveness Y Readiness probes
- ✅ Recursos (requests/limits)
- ✅ ConfigMaps y Secrets separados
- ✅ HPA configurado
- ✅ Estrategia de rolling update

---

## �📚 Recursos Adicionales

### Documentación Oficial
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Minikube Docs](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### Cursos y Tutoriales
- [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way)
- [Play with Kubernetes](https://labs.play-with-k8s.com/)
- [Katacoda Kubernetes](https://www.katacoda.com/courses/kubernetes)

### Herramientas Útiles
- **k9s**: Terminal UI para Kubernetes
- **Lens**: IDE visual para Kubernetes
- **Helm**: Gestor de paquetes para Kubernetes
- **Kustomize**: Personalización de manifiestos YAML

---

## 🧹 Limpiar Recursos

```powershell
# Eliminar todos los recursos del namespace
kubectl delete namespace prackube

# O eliminar recursos específicos
kubectl delete -f ./k8s/

# Detener Minikube
minikube stop

# Eliminar cluster completamente (si quieres empezar de cero)
minikube delete
```

---

## 📝 Notas Finales

- Los archivos YAML están numerados para aplicarse en orden lógico
- Todos los manifiestos tienen comentarios explicativos
- La aplicación usa `imagePullPolicy: Never` para usar imágenes locales
- Para producción real, usar un registry de imágenes (DockerHub, ECR, GCR, etc.)

¡Buena suerte con tu práctica de Kubernetes! 🚀

cd c:\ruta\a\tu\proyecto
git init
git add .
git commit -m "Descripción del proyecto"
git branch -M main
git remote add origin https://github.com/USUARIO/REPO.git
git push -u origin main
