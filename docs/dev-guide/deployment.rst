Guide de Déploiement
====================

Ce guide explique comment déployer ML Factory en production sur différentes plateformes.

🎯 Prérequis Production
-----------------------

Infrastructure
~~~~~~~~~~~~~~

* **Serveur**: Linux (Ubuntu 20.04+ recommandé)
* **RAM**: Minimum 4 GB (8 GB recommandé)
* **CPU**: 2+ cores
* **Stockage**: 20 GB+ SSD
* **Réseau**: Connexion stable, ports ouverts

Logiciels
~~~~~~~~~

* Docker 20.10+
* Docker Compose 2.0+
* Nginx (en tant que reverse proxy)
* Certificats SSL (Let's Encrypt recommandé)

🔐 Sécurité Production
----------------------

Variables d'Environnement
~~~~~~~~~~~~~~~~~~~~~~~~~

**Créer un fichier** ``.env.production``:

.. code-block:: bash

   # MinIO - Changez ces valeurs!
   MINIO_ROOT_USER=admin_prod_xyz123
   MINIO_ROOT_PASSWORD=ChangeThisSecurePassword123!
   
   # MLflow
   MLFLOW_TRACKING_URI=http://mlflow:5000
   
   # Model Configuration
   MODEL_NAME=iris_classifier
   MODEL_ALIAS=Production
   
   # AWS Credentials (pour MinIO)
   AWS_ACCESS_KEY_ID=admin_prod_xyz123
   AWS_SECRET_ACCESS_KEY=ChangeThisSecurePassword123!
   
   # S3 Endpoint
   MLFLOW_S3_ENDPOINT_URL=http://minio:9000

**⚠️ IMPORTANT:**

* **Ne jamais commiter** ce fichier
* Utiliser des mots de passe forts (20+ caractères)
* Rotation régulière des credentials

Authentification FastAPI
~~~~~~~~~~~~~~~~~~~~~~~~~

Ajouter OAuth2 / JWT à l'API:

.. code-block:: python

   # src/api/main.py
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   
   security = HTTPBearer()
   
   def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
       """Vérifie le token JWT."""
       token = credentials.credentials
       # Implémenter votre logique de vérification
       if not is_valid_token(token):
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid authentication credentials"
           )
       return token
   
   @app.post("/predict")
   async def predict(
       features: IrisFeatures,
       token: str = Depends(verify_token)  # ✅ Protection
   ):
       ...

Authentification MLflow
~~~~~~~~~~~~~~~~~~~~~~~

Activer l'authentification basique:

.. code-block:: yaml

   # docker-compose.prod.yml
   services:
     mlflow:
       command: >
         mlflow server
         --host 0.0.0.0
         --port 5000
         --backend-store-uri postgresql://user:pass@postgres:5432/mlflow
         --default-artifact-root s3://mlflow/
         --app-name basic-auth  # ✅ Authentification

Puis configurer les utilisateurs dans MLflow UI.

🏗️ Déploiement Docker
----------------------

Méthode 1: Docker Compose (Simple)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Fichier** ``docker-compose.prod.yml``:

.. code-block:: yaml

   version: '3.8'
   
   services:
     minio:
       image: minio/minio:latest
       restart: always
       ports:
         - "9000:9000"
         - "9001:9001"
       environment:
         MINIO_ROOT_USER: ${MINIO_ROOT_USER}
         MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
       volumes:
         - minio_data:/data
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
         interval: 30s
         timeout: 10s
         retries: 3
   
     postgres:  # ⚠️ Remplacer SQLite
       image: postgres:15
       restart: always
       environment:
         POSTGRES_USER: mlflow
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
         POSTGRES_DB: mlflow
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
     mlflow:
       build:
         context: ./src/mlflow
       restart: always
       ports:
         - "5000:5000"
       environment:
         AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
         AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
         MLFLOW_S3_ENDPOINT_URL: http://minio:9000
       command: >
         mlflow server
         --host 0.0.0.0
         --port 5000
         --backend-store-uri postgresql://mlflow:${POSTGRES_PASSWORD}@postgres:5432/mlflow
         --default-artifact-root s3://mlflow/
       depends_on:
         - minio
         - postgres
       volumes:
         - mlflow_data:/mlflow
   
     api:
       build:
         context: ./src/api
       restart: always
       ports:
         - "8000:8000"
       environment:
         MLFLOW_TRACKING_URI: http://mlflow:5000
         MODEL_NAME: ${MODEL_NAME}
         MODEL_ALIAS: ${MODEL_ALIAS}
         AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
         AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
         MLFLOW_S3_ENDPOINT_URL: http://minio:9000
       depends_on:
         - mlflow
         - minio
       deploy:  # ✅ Scalabilité
         replicas: 2
         resources:
           limits:
             cpus: '1'
             memory: 512M
   
     front:
       build:
         context: ./src/front
       restart: always
       ports:
         - "8501:8501"
       environment:
         API_URL: http://api:8000
       depends_on:
         - api
   
   volumes:
     minio_data:
     mlflow_data:
     postgres_data:

**Déploiement:**

.. code-block:: bash

   # Créer .env.production
   cp .env .env.production
   # Éditer .env.production avec des credentials sécurisés
   
   # Déployer
   docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
   
   # Vérifier
   docker-compose -f docker-compose.prod.yml ps

Méthode 2: Docker Swarm (Cluster)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Initialiser Swarm:**

.. code-block:: bash

   # Sur le manager node
   docker swarm init --advertise-addr <MANAGER_IP>
   
   # Sur les worker nodes
   docker swarm join --token <TOKEN> <MANAGER_IP>:2377

**Déployer le stack:**

.. code-block:: bash

   # Créer les secrets
   echo "admin_prod_xyz123" | docker secret create minio_user -
   echo "ChangeThisSecurePassword123!" | docker secret create minio_password -
   
   # Déployer
   docker stack deploy -c docker-compose.prod.yml ml-factory
   
   # Vérifier
   docker stack services ml-factory
   docker stack ps ml-factory

🌐 Nginx Reverse Proxy
-----------------------

Configuration
~~~~~~~~~~~~~

**Fichier** ``/etc/nginx/sites-available/ml-factory``:

.. code-block:: nginx

   upstream mlflow_backend {
       server localhost:5000;
   }
   
   upstream api_backend {
       server localhost:8000;
       server localhost:8001;  # Si plusieurs réplicas
   }
   
   upstream streamlit_backend {
       server localhost:8501;
   }
   
   # Redirection HTTP → HTTPS
   server {
       listen 80;
       server_name ml-factory.example.com;
       return 301 https://$server_name$request_uri;
   }
   
   # HTTPS
   server {
       listen 443 ssl http2;
       server_name ml-factory.example.com;
   
       # SSL Certificates (Let's Encrypt)
       ssl_certificate /etc/letsencrypt/live/ml-factory.example.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/ml-factory.example.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
   
       # MLflow UI
       location /mlflow/ {
           proxy_pass http://mlflow_backend/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   
       # FastAPI
       location /api/ {
           proxy_pass http://api_backend/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   
       # Streamlit
       location / {
           proxy_pass http://streamlit_backend;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   
       # Security Headers
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header X-XSS-Protection "1; mode=block" always;
   }

**Activer et redémarrer Nginx:**

.. code-block:: bash

   sudo ln -s /etc/nginx/sites-available/ml-factory /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx

SSL avec Let's Encrypt
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Installer Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Obtenir un certificat
   sudo certbot --nginx -d ml-factory.example.com
   
   # Renouvellement automatique (cron)
   sudo certbot renew --dry-run

☸️ Déploiement Kubernetes
--------------------------

Namespace et ConfigMap
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # namespace.yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: ml-factory

.. code-block:: yaml

   # configmap.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: ml-factory-config
     namespace: ml-factory
   data:
     MODEL_NAME: "iris_classifier"
     MODEL_ALIAS: "Production"
     MLFLOW_TRACKING_URI: "http://mlflow-service:5000"
     MLFLOW_S3_ENDPOINT_URL: "http://minio-service:9000"

Secrets
~~~~~~~

.. code-block:: bash

   kubectl create secret generic ml-factory-secrets \
     --from-literal=minio-user=admin_prod_xyz123 \
     --from-literal=minio-password=ChangeThisSecurePassword123! \
     --namespace=ml-factory

Deployments
~~~~~~~~~~~

**MinIO:**

.. code-block:: yaml

   # minio-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: minio
     namespace: ml-factory
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: minio
     template:
       metadata:
         labels:
           app: minio
       spec:
         containers:
         - name: minio
           image: minio/minio:latest
           args:
           - server
           - /data
           - --console-address
           - ":9001"
           env:
           - name: MINIO_ROOT_USER
             valueFrom:
               secretKeyRef:
                 name: ml-factory-secrets
                 key: minio-user
           - name: MINIO_ROOT_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: ml-factory-secrets
                 key: minio-password
           ports:
           - containerPort: 9000
           - containerPort: 9001
           volumeMounts:
           - name: data
             mountPath: /data
         volumes:
         - name: data
           persistentVolumeClaim:
             claimName: minio-pvc

**MLflow:**

.. code-block:: yaml

   # mlflow-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mlflow
     namespace: ml-factory
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: mlflow
     template:
       metadata:
         labels:
           app: mlflow
       spec:
         containers:
         - name: mlflow
           image: your-registry/mlflow:latest
           command:
           - mlflow
           - server
           - --host
           - 0.0.0.0
           - --port
           - "5000"
           - --backend-store-uri
           - postgresql://user:pass@postgres:5432/mlflow
           - --default-artifact-root
           - s3://mlflow/
           env:
           - name: AWS_ACCESS_KEY_ID
             valueFrom:
               secretKeyRef:
                 name: ml-factory-secrets
                 key: minio-user
           - name: AWS_SECRET_ACCESS_KEY
             valueFrom:
               secretKeyRef:
                 name: ml-factory-secrets
                 key: minio-password
           - name: MLFLOW_S3_ENDPOINT_URL
             valueFrom:
               configMapKeyRef:
                 name: ml-factory-config
                 key: MLFLOW_S3_ENDPOINT_URL
           ports:
           - containerPort: 5000

**FastAPI:**

.. code-block:: yaml

   # api-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: api
     namespace: ml-factory
   spec:
     replicas: 3  # ✅ Scalabilité
     selector:
       matchLabels:
         app: api
     template:
       metadata:
         labels:
           app: api
       spec:
         containers:
         - name: api
           image: your-registry/api:latest
           envFrom:
           - configMapRef:
               name: ml-factory-config
           env:
           - name: AWS_ACCESS_KEY_ID
             valueFrom:
               secretKeyRef:
                 name: ml-factory-secrets
                 key: minio-user
           - name: AWS_SECRET_ACCESS_KEY
             valueFrom:
               secretKeyRef:
                 name: ml-factory-secrets
                 key: minio-password
           ports:
           - containerPort: 8000
           resources:
             requests:
               memory: "256Mi"
               cpu: "500m"
             limits:
               memory: "512Mi"
               cpu: "1000m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 20
             periodSeconds: 5

Services et Ingress
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # services.yaml
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mlflow-service
     namespace: ml-factory
   spec:
     selector:
       app: mlflow
     ports:
     - port: 5000
       targetPort: 5000
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: api-service
     namespace: ml-factory
   spec:
     selector:
       app: api
     ports:
     - port: 8000
       targetPort: 8000
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: front-service
     namespace: ml-factory
   spec:
     selector:
       app: front
     ports:
     - port: 8501
       targetPort: 8501

.. code-block:: yaml

   # ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: ml-factory-ingress
     namespace: ml-factory
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
       nginx.ingress.kubernetes.io/ssl-redirect: "true"
   spec:
     ingressClassName: nginx
     tls:
     - hosts:
       - ml-factory.example.com
       secretName: ml-factory-tls
     rules:
     - host: ml-factory.example.com
       http:
         paths:
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: api-service
               port:
                 number: 8000
         - path: /mlflow
           pathType: Prefix
           backend:
             service:
               name: mlflow-service
               port:
                 number: 5000
         - path: /
           pathType: Prefix
           backend:
             service:
               name: front-service
               port:
                 number: 8501

Déployer
~~~~~~~~

.. code-block:: bash

   kubectl apply -f namespace.yaml
   kubectl apply -f configmap.yaml
   kubectl create secret generic ml-factory-secrets ...
   kubectl apply -f minio-deployment.yaml
   kubectl apply -f mlflow-deployment.yaml
   kubectl apply -f api-deployment.yaml
   kubectl apply -f front-deployment.yaml
   kubectl apply -f services.yaml
   kubectl apply -f ingress.yaml
   
   # Vérifier
   kubectl get pods -n ml-factory
   kubectl get svc -n ml-factory
   kubectl get ingress -n ml-factory

☁️ Déploiement Cloud
--------------------

Azure (AKS + Azure Blob)
~~~~~~~~~~~~~~~~~~~~~~~~

**1. Créer un cluster AKS:**

.. code-block:: bash

   az aks create \
     --resource-group ml-factory-rg \
     --name ml-factory-aks \
     --node-count 3 \
     --enable-addons monitoring \
     --generate-ssh-keys

**2. Remplacer MinIO par Azure Blob Storage:**

.. code-block:: yaml

   # mlflow-deployment-azure.yaml (extrait)
   env:
   - name: AZURE_STORAGE_CONNECTION_STRING
     valueFrom:
       secretKeyRef:
         name: azure-storage-secret
         key: connection-string
   command:
   - mlflow
   - server
   - --default-artifact-root
   - wasbs://mlflow@<storage-account>.blob.core.windows.net/

**3. Utiliser Azure Database for PostgreSQL:**

.. code-block:: bash

   az postgres server create \
     --resource-group ml-factory-rg \
     --name mlflow-postgres \
     --sku-name B_Gen5_1

AWS (EKS + S3)
~~~~~~~~~~~~~~

**1. Créer un cluster EKS:**

.. code-block:: bash

   eksctl create cluster \
     --name ml-factory-eks \
     --region us-east-1 \
     --nodegroup-name standard-workers \
     --node-type t3.medium \
     --nodes 3

**2. Utiliser S3 natif:**

.. code-block:: yaml

   # mlflow-deployment-aws.yaml (extrait)
   env:
   - name: AWS_ACCESS_KEY_ID
     valueFrom:
       secretKeyRef:
         name: aws-credentials
         key: access-key
   - name: AWS_SECRET_ACCESS_KEY
     valueFrom:
       secretKeyRef:
         name: aws-credentials
         key: secret-key
   command:
   - mlflow
   - server
   - --default-artifact-root
   - s3://ml-factory-bucket/

**3. Utiliser RDS PostgreSQL:**

.. code-block:: bash

   aws rds create-db-instance \
     --db-instance-identifier mlflow-postgres \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password <password>

📊 Monitoring et Logs
---------------------

Prometheus + Grafana
~~~~~~~~~~~~~~~~~~~~

**Installer kube-prometheus-stack:**

.. code-block:: bash

   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring --create-namespace

**Dashboard Grafana pour ML Factory:**

* CPU/Memory des pods
* Requêtes API (rate, latency)
* Nombre de modèles chargés
* Taille des artefacts MLflow

ELK Stack (Logs)
~~~~~~~~~~~~~~~~

**Elasticsearch + Kibana + Filebeat:**

.. code-block:: bash

   helm repo add elastic https://helm.elastic.co
   helm install elasticsearch elastic/elasticsearch \
     --namespace logging --create-namespace
   helm install kibana elastic/kibana --namespace logging
   helm install filebeat elastic/filebeat --namespace logging

🔄 CI/CD Pipeline
-----------------

GitHub Actions
~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/deploy.yml
   name: Deploy to Production
   
   on:
     push:
       branches: [main]
   
   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       
       - name: Login to Docker Hub
         uses: docker/login-action@v2
         with:
           username: ${{ secrets.DOCKERHUB_USERNAME }}
           password: ${{ secrets.DOCKERHUB_TOKEN }}
       
       - name: Build and Push Images
         run: |
           docker-compose -f docker-compose.prod.yml build
           docker-compose -f docker-compose.prod.yml push
       
       - name: Deploy to Kubernetes
         env:
           KUBECONFIG: ${{ secrets.KUBECONFIG }}
         run: |
           kubectl apply -f k8s/
           kubectl rollout status deployment/api -n ml-factory

GitLab CI
~~~~~~~~~

.. code-block:: yaml

   # .gitlab-ci.yml
   stages:
     - build
     - test
     - deploy
   
   build:
     stage: build
     script:
       - docker-compose -f docker-compose.prod.yml build
       - docker-compose -f docker-compose.prod.yml push
   
   test:
     stage: test
     script:
       - pytest tests/
   
   deploy-production:
     stage: deploy
     script:
       - kubectl apply -f k8s/
       - kubectl rollout status deployment/api -n ml-factory
     only:
       - main

📚 Checklist Production
-----------------------

.. rst-class:: checklist

   ☐ Remplacer SQLite par PostgreSQL pour MLflow
   
   ☐ Utiliser un stockage objet scalable (Azure Blob / AWS S3)
   
   ☐ Configurer des credentials sécurisés (secrets managers)
   
   ☐ Activer l'authentification sur tous les services
   
   ☐ Configurer HTTPS avec certificats valides
   
   ☐ Mettre en place un reverse proxy (Nginx/Ingress)
   
   ☐ Déployer plusieurs réplicas de l'API (load balancing)
   
   ☐ Configurer les health checks et liveness probes
   
   ☐ Mettre en place le monitoring (Prometheus + Grafana)
   
   ☐ Centraliser les logs (ELK Stack / Cloud Logging)
   
   ☐ Configurer des backups automatiques (volumes + base de données)
   
   ☐ Tester le rollback en cas de problème
   
   ☐ Documenter la procédure de déploiement
   
   ☐ Planifier la rotation des credentials
   
   ☐ Mettre en place des alertes (Opsgenie / PagerDuty)

🆘 Support
----------

Pour une aide au déploiement:

* 📖 :doc:`architecture` - Architecture détaillée
* 🐛 `GitHub Issues <https://github.com/simplon-france/ml-factory/issues>`_
* 💬 Support Simplon France
