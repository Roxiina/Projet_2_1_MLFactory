Architecture du Projet
======================

Cette page détaille l'architecture technique de ML Factory et les choix de conception.

📐 Vue d'Ensemble
-----------------

ML Factory est une plateforme MLOps complète permettant le déploiement Zero-Downtime de modèles de Machine Learning.

Principes de Conception
~~~~~~~~~~~~~~~~~~~~~~~~

* **Séparation des responsabilités**: Chaque service a un rôle unique et bien défini
* **Découplage**: Les services communiquent via des interfaces standardisées
* **Versioning**: Tous les artefacts sont versionnés et traçables
* **Hot-Reloading**: Changement de modèle sans interruption de service
* **Observabilité**: Logs, métriques et traçabilité complète

🏗️ Architecture Globale
------------------------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                         ML Factory                           │
   └─────────────────────────────────────────────────────────────┘
   
        User Interface              API Layer           Storage
   
   ┌─────────────────┐        ┌──────────────┐     ┌──────────┐
   │                 │        │              │     │          │
   │   Streamlit     │───────▶│   FastAPI    │────▶│  MinIO   │
   │    Frontend     │        │   Serving    │     │   (S3)   │
   │                 │        │              │     │          │
   └─────────────────┘        └──────────────┘     └──────────┘
          │                          │                    │
          │                          │                    │
          │                   ┌──────▼──────┐             │
          │                   │             │             │
          └──────────────────▶│   MLflow    │◀────────────┘
                              │  Tracking   │
                              │  Registry   │
                              └─────────────┘
                                     ▲
                                     │
                              ┌──────┴──────┐
                              │             │
                              │  Training   │
                              │   Script    │
                              └─────────────┘

Services et Responsabilités
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Service
     - Responsabilité
     - Technologies
   * - **MinIO**
     - Stockage objet (S3-compatible)
     - MinIO, S3 API
   * - **MLflow**
     - Tracking, Registry, Metadata
     - MLflow Server, SQLite
   * - **FastAPI**
     - API de prédiction, Hot-reload
     - FastAPI, Uvicorn, Pydantic
   * - **Streamlit**
     - Interface utilisateur
     - Streamlit, Pandas
   * - **Training**
     - Entraînement des modèles
     - Scikit-learn, MLflow Client

🔄 Flux de Données
------------------

Flux d'Entraînement
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Training Script
      │
      ├─▶ Load Data (Iris dataset)
      │
      ├─▶ Train Model (LogReg / RandomForest)
      │
      ├─▶ Log Metrics to MLflow
      │   (Accuracy, F1, Confusion Matrix)
      │
      ├─▶ Register Model in MLflow
      │   (Auto version: v1, v2, v3...)
      │
      └─▶ Promote to Production (optional)
          └─▶ Set Alias "Production" → Version X

Flux de Prédiction
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. User Request
      │
      ├─▶ Streamlit UI (manual input / CSV upload)
      │
      └─▶ POST /predict to FastAPI
          │
          ├─▶ Check Production Model Version
          │   (Query MLflow alias "Production")
          │
          ├─▶ Reload Model if Version Changed
          │   (Download from MinIO via MLflow)
          │
          ├─▶ Run Prediction
          │   (Model.predict + predict_proba)
          │
          └─▶ Return Response
              (Prediction, Probabilities, Version)

Flux Zero-Downtime
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Time: T0
   ─────────────────────────────────────────
   API uses Model v1 (alias: Production)
   All requests → Model v1 predictions
   
   Time: T1 (New model trained)
   ─────────────────────────────────────────
   Training script creates Model v2
   MLflow Registry: v1 (Production), v2 (None)
   API still uses v1 (no alias change yet)
   
   Time: T2 (Manual promotion on MLflow UI)
   ─────────────────────────────────────────
   User sets alias "Production" → v2 on MLflow
   
   Time: T3 (Next API request)
   ─────────────────────────────────────────
   API checks alias: "Production" → v2 (changed!)
   API downloads v2 from MinIO
   API caches v2 in memory (app_state)
   All new requests → Model v2 predictions
   
   ⚠️ NO DOWNTIME! No restart! Zero interruption!

🧩 Composants Détaillés
-----------------------

1. MinIO (Object Storage)
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rôle:**

Stockage centralisé des artefacts de modèles

**Configuration:**

.. code-block:: yaml

   services:
     minio:
       image: minio/minio
       ports:
         - "9000:9000"  # S3 API
         - "9001:9001"  # Console Web
       environment:
         MINIO_ROOT_USER: minioadmin
         MINIO_ROOT_PASSWORD: minioadmin
       command: server /data --console-address ":9001"
       volumes:
         - minio_data:/data

**Buckets:**

* ``mlflow``: Stocke tous les artefacts MLflow (modèles, métriques, plots)

**API Endpoint:**

* S3 API: ``http://minio:9000`` (interne Docker)
* Console: ``http://localhost:9001`` (externe)

2. MLflow (Tracking & Registry)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rôle:**

* **Tracking Server**: Enregistre les expériences, runs, métriques, paramètres
* **Model Registry**: Gère le versioning et les alias des modèles

**Configuration:**

.. code-block:: yaml

   services:
     mlflow:
       build:
         context: ./src/mlflow
       ports:
         - "5000:5000"
       environment:
         AWS_ACCESS_KEY_ID: minioadmin
         AWS_SECRET_ACCESS_KEY: minioadmin
         MLFLOW_S3_ENDPOINT_URL: http://minio:9000
       command: >
         mlflow server
         --host 0.0.0.0
         --port 5000
         --backend-store-uri sqlite:///mlflow.db
         --default-artifact-root s3://mlflow/
       volumes:
         - mlflow_data:/mlflow

**Base de données:**

* SQLite (``mlflow.db``): Métadonnées (runs, paramètres, métriques)
* MinIO (S3): Artefacts (modèles, fichiers, plots)

**Model Registry:**

.. code-block:: text

   Model: iris_classifier
   ├── Version 1
   │   ├── Alias: Production ✓
   │   ├── Artifact URI: s3://mlflow/1/.../model
   │   └── Metrics: accuracy=0.96
   ├── Version 2
   │   ├── Alias: Staging
   │   ├── Artifact URI: s3://mlflow/2/.../model
   │   └── Metrics: accuracy=0.97
   └── Version 3
       ├── Alias: (none)
       └── ...

3. FastAPI (Serving Layer)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rôle:**

API REST pour les prédictions avec hot-reloading automatique

**Endpoints:**

.. list-table::
   :header-rows: 1
   :widths: 10 20 50 20

   * - Method
     - Path
     - Description
     - Auth
   * - GET
     - ``/``
     - Welcome message
     - None
   * - GET
     - ``/health``
     - Health check + model status
     - None
   * - GET
     - ``/model-info``
     - Metadata du modèle actuel
     - None
   * - POST
     - ``/predict``
     - Prédiction single sample
     - None
   * - POST
     - ``/predict-batch``
     - Prédiction batch (CSV)
     - None

**Configuration:**

.. code-block:: yaml

   services:
     api:
       build:
         context: ./src/api
       ports:
         - "8000:8000"
       environment:
         MLFLOW_TRACKING_URI: http://mlflow:5000
         MODEL_NAME: iris_classifier
         MODEL_ALIAS: Production
         AWS_ACCESS_KEY_ID: minioadmin
         AWS_SECRET_ACCESS_KEY: minioadmin
         MLFLOW_S3_ENDPOINT_URL: http://minio:9000
       depends_on:
         - mlflow
         - minio

**Hot-Reloading Mechanism:**

.. code-block:: python

   # Pseudo-code
   def load_production_model():
       # 1. Query MLflow for alias "Production"
       latest_version = mlflow_client.get_model_version_by_alias(
           name="iris_classifier",
           alias="Production"
       )
       
       # 2. Check if version changed
       if latest_version != app_state["current_version"]:
           # 3. Download new model from MinIO
           model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
           model = mlflow.pyfunc.load_model(model_uri)
           
           # 4. Update cache
           app_state["model"] = model
           app_state["current_version"] = latest_version
           
           return "Model reloaded!"
       
       return "Model already up-to-date"

**Request Lifecycle:**

.. code-block:: text

   1. HTTP POST /predict
      │
   2. Pydantic Validation (IrisFeatures)
      │
   3. load_production_model()
      ├─▶ Check MLflow alias
      └─▶ Reload if needed
      │
   4. Model Prediction
      ├─▶ model.predict([features])
      └─▶ model.predict_proba([features])
      │
   5. Response (PredictionResponse)
      └─▶ JSON with prediction + probabilities + version

4. Streamlit (Frontend)
~~~~~~~~~~~~~~~~~~~~~~~~

**Rôle:**

Interface utilisateur pour tester les prédictions et visualiser les modèles

**Pages:**

1. **Saisie Manuelle**: Sliders pour ajuster les features manuellement
2. **Charger depuis fichier**: Upload CSV pour batch testing

**Configuration:**

.. code-block:: yaml

   services:
     front:
       build:
         context: ./src/front
       ports:
         - "8501:8501"
       environment:
         API_URL: http://api:8000
       depends_on:
         - api

**Features:**

* Badge de santé API (vert/rouge)
* Badge de version de modèle avec mise à jour dynamique
* Métriques du modèle (accuracy, F1, etc.)
* Graphiques de probabilités
* Upload CSV avec sélection de ligne
* Cache avec TTL de 5 secondes pour réactivité

**Caching Strategy:**

.. code-block:: python

   @st.cache_data(ttl=5)  # Refresh every 5 seconds
   def get_model_info():
       """Fetch model metadata from API."""
       response = requests.get(f"{API_URL}/model-info")
       return response.json()

5. Training Script
~~~~~~~~~~~~~~~~~~

**Rôle:**

Entraînement et enregistrement des modèles dans MLflow

**Modes:**

* **Auto-Promote** (``AUTO_PROMOTE=True``): Assigne automatiquement l'alias "Production"
* **Manual-Promote** (``AUTO_PROMOTE=False``): Nécessite une promotion manuelle sur MLflow UI

**Algorithmes Supportés:**

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Algorithme
     - Paramètres
     - Use Case
   * - Logistic Regression
     - ``max_iter=200, random_state=42``
     - Baseline rapide
   * - Random Forest
     - ``n_estimators=100, random_state=42``
     - Meilleure accuracyacy

**MLflow Logging:**

.. code-block:: python

   with mlflow.start_run(run_name=f"{model_type}_training"):
       # 1. Log parameters
       mlflow.log_param("model_type", model_type)
       mlflow.log_param("n_samples", len(X_train))
       
       # 2. Log metrics
       mlflow.log_metric("accuracy", accuracy)
       mlflow.log_metric("f1_score", f1)
       
       # 3. Log artifacts
       mlflow.log_artifact("confusion_matrix.png")
       
       # 4. Log model
       mlflow.sklearn.log_model(
           sk_model=model,
           artifact_path="model",
           registered_model_name="iris_classifier"
       )

🔐 Sécurité
-----------

Authentification
~~~~~~~~~~~~~~~~

**État actuel:**

* Aucune authentification (développement)
* Accès ouvert à tous les endpoints

**Recommandations pour la production:**

* **FastAPI**: Ajouter OAuth2 / JWT
* **MLflow**: Activer l'authentification basique
* **MinIO**: Rotations de credentials régulières
* **Streamlit**: Ajouter un mécanisme de login

Variables d'Environnement
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Sensibles** (à ne pas commiter):

* ``MINIO_ROOT_USER``
* ``MINIO_ROOT_PASSWORD``
* ``AWS_ACCESS_KEY_ID``
* ``AWS_SECRET_ACCESS_KEY``

**Bonne pratique:**

* Utiliser un fichier ``.env`` (exclu de Git)
* En production: utiliser des secrets managers (Azure Key Vault, AWS Secrets Manager)

🚀 Scalabilité
--------------

Goulots d'Étranglement Actuels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **MLflow SQLite**: Limite pour usage concurrent élevé
2. **MinIO Single Node**: Pas de réplication
3. **FastAPI Single Instance**: Pas de load balancing

Améliorations pour la Production
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**MLflow:**

.. code-block:: yaml

   # Remplacer SQLite par PostgreSQL
   --backend-store-uri postgresql://user:pass@postgres:5432/mlflow

**MinIO:**

.. code-block:: yaml

   # Utiliser un mode distribué ou Azure Blob Storage
   mlflow server --default-artifact-root wasbs://<container>@<account>.blob.core.windows.net/

**FastAPI:**

.. code-block:: yaml

   # Déployer plusieurs réplicas avec load balancer
   services:
     api:
       deploy:
         replicas: 3

**Kubernetes Deployment:**

Pour une vraie production à grande échelle, déployer sur Kubernetes avec:

* **HPA** (Horizontal Pod Autoscaler)
* **Ingress** avec NGINX
* **Persistent Volumes** pour MLflow et MinIO
* **Service Mesh** (Istio/Linkerd)

📊 Observabilité
----------------

Logs
~~~~

.. code-block:: bash

   # Voir tous les logs
   docker-compose logs
   
   # Logs d'un service
   docker-compose logs api
   
   # Logs en direct
   docker-compose logs -f

Metrics
~~~~~~~

**MLflow UI:**

* Expériences et runs
* Métriques d'entraînement
* Comparaison de modèles

**FastAPI:**

* ``/health`` endpoint avec statut du modèle
* Logs de rechargement du modèle

**Recommandations production:**

* Ajouter Prometheus pour les métriques système
* Grafana pour les dashboards
* ELK Stack pour les logs centralisés

Tracing
~~~~~~~

**Ajout recommandé:**

* OpenTelemetry pour tracer les requêtes end-to-end
* Jaeger pour visualiser les traces

📂 Structure des Données
-------------------------

Arborescence
~~~~~~~~~~~~

.. code-block:: text

   Projet_2_1_MLFactory/
   ├── data/
   │   ├── iris_test.csv          # Données de test générées
   │   ├── minio/                 # Volume MinIO (créé par Docker)
   │   └── mlflow/                # Volume MLflow (créé par Docker)
   ├── src/
   │   ├── train/
   │   │   └── train.py           # Script d'entraînement
   │   ├── api/
   │   │   ├── main.py            # FastAPI application
   │   │   ├── Dockerfile
   │   │   └── requirements.txt
   │   ├── front/
   │   │   ├── app.py             # Streamlit application
   │   │   ├── Dockerfile
   │   │   └── requirements.txt
   │   └── mlflow/
   │       └── Dockerfile
   ├── docs/                      # Documentation Sphinx
   ├── docker-compose.yml         # Orchestration
   ├── .env                       # Variables d'environnement
   ├── pyproject.toml             # Deps + config Python
   └── README.md

Volumes Docker
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Volume
     - Contenu
   * - ``minio_data``
     - Artefacts MLflow (modèles, plots, logs)
   * - ``mlflow_data``
     - Base SQLite de MLflow + fichiers locaux

📚 Références Techniques
------------------------

Frameworks et Librairies
~~~~~~~~~~~~~~~~~~~~~~~~~

* **MLflow** 2.10+: Model Registry, Tracking, Projects
* **FastAPI** 0.109+: Modern web framework avec Pydantic
* **Streamlit** 1.31+: Rapid UI development
* **Scikit-learn** 1.4+: ML algorithms
* **MinIO**: S3-compatible object storage
* **Docker** 20.10+: Containerization
* **UV**: Fast Python package manager

Standards
~~~~~~~~~

* **REST API**: Endpoints JSON standard
* **S3 Protocol**: Compatibilité avec AWS S3
* **MLflow Model Format**: Portable model packaging
* **Pydantic**: Data validation avec type hints
* **OpenAPI**: Documentation automatique de l'API

Patterns
~~~~~~~~

* **Model Registry Pattern**: Versioning centralisé
* **Hot-Reloading**: Dynamic model updates
* **Microservices**: Découplage des services
* **API-First**: Frontend agnostique
* **Immutable Infrastructure**: Conteneurs stateless

🔄 Prochaines Étapes
--------------------

Pour aller plus loin:

1. 🚀 :doc:`deployment` - Guide de déploiement en production
2. 📚 :doc:`api-reference` - Référence complète de l'API
3. 🧪 :doc:`training` - Personnaliser l'entraînement
4. 📖 :doc:`/user-guide/quickstart` - Démarrage rapide
