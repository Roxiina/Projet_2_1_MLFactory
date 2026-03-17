🎯 Guide de Validation et d'Évaluation
======================================

Ce document guide les évaluateurs à travers les critères de performance et les points clés du projet ML Factory.

📋 Vue d'Ensemble du Projet
----------------------------

**Objectif** : Créer une plateforme MLOps automatisée permettant de mettre à jour des modèles de Machine Learning **sans interruption de service** (Zero-Downtime).

**Contexte** : L'application de prédiction doit rester disponible 24h/24. Chaque mise à jour de modèle se fait de manière **transparente** pour l'utilisateur final grâce à un système de registre (MLflow) et d'alias de production.

✅ Livrables du Projet
-----------------------

Architecture Logicielle
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Projet_2_1_MLFactory/
   ├── .env                    # Configuration des services Docker
   ├── .env.local              # Configuration pour développement local
   ├── .env.example            # Template de configuration
   ├── docker-compose.yml      # Orchestration des services
   ├── manage.ps1             # Script PowerShell de gestion
   ├── requirements.txt        # Dépendances Python
   │
   ├── src/
   │   ├── api/                # API FastAPI de serving
   │   │   ├── main.py         # Code de l'API avec hot-reloading
   │   │   ├── Dockerfile      # Image Docker pour l'API
   │   │   └── requirements.txt
   │   │
   │   ├── front/              # Interface utilisateur Streamlit
   │   │   ├── app.py          # Code de l'interface
   │   │   ├── Dockerfile      # Image Docker pour le frontend
   │   │   └── requirements.txt
   │   │
   │   └── train/              # Scripts d'entraînement
   │       └── train.py        # Script d'entraînement avec MLflow
   │
   ├── data/                   # Données de test
   │   └── iris_test.csv
   │
   └── docs/                   # Documentation Sphinx

Services Docker
~~~~~~~~~~~~~~~

Le projet comprend **4 services orchestrés** via docker-compose :

.. list-table::
   :header-rows: 1
   :widths: 20 30 10 40

   * - Service
     - Image
     - Port
     - Rôle
   * - **MLflow**
     - ghcr.io/mlflow/mlflow:v2.14.0
     - 5000
     - Model Registry & Tracking
   * - **MinIO**
     - minio/minio:latest
     - 9000/9001
     - Stockage S3 des artefacts
   * - **API**
     - Build from src/api
     - 8000
     - API de prédiction FastAPI
   * - **Front**
     - Build from src/front
     - 8501
     - Interface Streamlit

Fichiers de Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

* ✅ **docker-compose.yml** : Orchestration complète avec volumes persistants
* ✅ **.env** : Variables d'environnement pour Docker
* ✅ **.env.local** : Variables pour exécution locale (hors Docker)
* ✅ **.env.example** : Template documenté

🎭 Démonstration Technique
---------------------------

Scénario 1 : Promotion Automatique (Zero-Downtime)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Prouver qu'un changement de modèle ne nécessite **aucun redémarrage** de l'API.

Étapes de la Démonstration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **État initial** :

   .. code-block:: powershell

      # Démarrer l'infrastructure
      docker-compose up -d
      
      # Vérifier que tout est opérationnel
      docker-compose ps

2. **Entraîner le premier modèle (v1 - Logistic Regression)** :

   .. code-block:: powershell

      # Dans src/train/train.py, vérifier:
      # - AUTO_PROMOTE = True
      # - train_model("logistic_regression")
      
      python src/train/train.py

   **Résultat attendu** :

   * ✅ Modèle Version 1 créé dans MLflow
   * ✅ Alias "Production" assigné automatiquement
   * ✅ L'API charge automatiquement le modèle

3. **Vérification sur l'interface** :

   * Ouvrir http://localhost:8501
   * Observer : **Badge "Version: v1"**
   * Faire une prédiction
   * Observer : **"Modèle: Version 1"** dans le résultat

4. **Entraîner un nouveau modèle (v2 - Random Forest)** :

   .. code-block:: powershell

      # Dans src/train/train.py, modifier:
      # train_model("random_forest")
      
      python src/train/train.py

   **Résultat attendu** :

   * ✅ Modèle Version 2 créé dans MLflow
   * ✅ Alias "Production" déplacé vers Version 2
   * ⚠️ **L'API n'est PAS redémarrée**

5. **Observer le changement automatique** :

   * ⏱️ **Attendre 5-10 secondes**
   * Rafraîchir l'interface Streamlit
   * Observer : **Badge "Version: v2"**
   * Faire une nouvelle prédiction
   * Observer : **"Modèle: Version 2"** dans le résultat

Points Clés de la Démonstration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ✅ **Aucun** ``docker-compose restart`` **n'a été exécuté**
* ✅ **Aucune interruption** de l'API (vérifiable via les logs)
* ✅ **Détection automatique** de la nouvelle version en < 10 secondes
* ✅ **Traçabilité complète** : la version est affichée dans chaque réponse

Scénario 2 : Promotion Manuelle (Validation Humaine)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Simuler un workflow où un humain valide le modèle avant la mise en production.

Étapes de la Démonstration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Désactiver la promotion automatique** :

   .. code-block:: python

      # Dans src/train/train.py, ligne ~60:
      AUTO_PROMOTE = False

2. **Entraîner un nouveau modèle (v3)** :

   .. code-block:: powershell

      # Modifier train.py pour entraîner logistic_regression
      python src/train/train.py

   **Résultat attendu** :

   * ✅ Modèle Version 3 créé dans MLflow
   * ⚠️ **Alias "Production" reste sur Version 2**
   * ⚠️ L'API continue d'utiliser Version 2

3. **Validation manuelle via MLflow UI** :

   * Ouvrir http://localhost:5000
   * Naviguer : **Models** → **iris_classifier**
   * Observer : 3 versions enregistrées
   * Cliquer sur **Version 3**
   * Cliquer sur **"Set alias"**
   * Saisir "**Production**" et valider

4. **Observer le changement** :

   * Retourner sur Streamlit
   * Cliquer sur "🔄 Rafraîchir"
   * Observer : **Badge "Version: v3"**
   * L'API utilise maintenant Version 3 **sans redémarrage**

Points Clés de la Démonstration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ✅ **Workflow flexible** : automatique OU manuel
* ✅ **Validation humaine** possible avant mise en production
* ✅ **Même mécanisme de hot-reloading** dans les deux cas

📊 Critères de Performance
---------------------------

1. Réactivité (< 10 secondes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Test** :

1. Promouvoir un nouveau modèle en production (via MLflow UI)
2. Chronomètrer le temps jusqu'à la détection par l'API
3. **Critère de réussite** : Changement détecté en **moins de 10 secondes**

**Mécanisme technique** :

* L'API vérifie la version du modèle "Production" **à chaque requête de prédiction**
* Si la version a changé, elle télécharge et charge le nouveau modèle
* Le cache Streamlit a un **TTL de 5 secondes** pour les informations du modèle

2. Traçabilité
~~~~~~~~~~~~~~

**Test** :

1. Faire une prédiction via l'API
2. Inspecter la réponse JSON
3. **Critère de réussite** : La réponse contient **explicitement** :
   
   * ``model_version`` (ex: "2")
   * ``model_name`` (ex: "iris_classifier")

**Exemple de réponse** :

.. code-block:: json

   {
     "prediction": 0,
     "prediction_label": "Setosa",
     "probabilities": {
       "Setosa": 0.98,
       "Versicolor": 0.01,
       "Virginica": 0.01
     },
     "model_version": "2",
     "model_name": "iris_classifier"
   }

3. Isolation des Services
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Test** :

1. Lister les conteneurs : ``docker-compose ps``
2. Vérifier les réseaux : ``docker network ls``
3. **Critère de réussite** :
   
   * ✅ Chaque service tourne dans son **propre conteneur**
   * ✅ Les services communiquent via le **réseau** ``ml_network``
   * ✅ Les dépendances sont gérées **indépendamment** (requirements.txt séparés)

4. Persistance des Données
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Test** :

1. Entraîner un modèle et vérifier qu'il est en production
2. Arrêter les services : ``docker-compose down`` (⚠️ **sans** ``-v``)
3. Redémarrer : ``docker-compose up -d``
4. **Critère de réussite** :
   
   * ✅ Le modèle est **toujours présent** dans MLflow
   * ✅ Les métadonnées (runs, experiments) sont **préservées**
   * ✅ Les volumes Docker ``minio_data`` et ``mlflow_data`` **existent toujours**

**Commande de vérification** :

.. code-block:: powershell

   docker volume ls | Select-String "mlfactory"

🧪 Revue de Code
-----------------

Points Clés à Examiner
~~~~~~~~~~~~~~~~~~~~~~

1. Gestion des Variables d'Environnement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Fichiers à examiner** :

* ``.env`` : Configuration Docker
* ``.env.local`` : Configuration locale
* ``.env.example`` : Template documenté

**Questions à poser** :

* ❓ Pourquoi deux fichiers .env et .env.local ?
* **Réponse** : Les services Docker utilisent des **noms de services** (ex: ``http://mlflow:5000``), tandis que les scripts locaux utilisent ``localhost``.

2. Hot-Reloading dans l'API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Fichier** : ``src/api/main.py``

**Fonction clé** : ``load_production_model()`` (lignes ~113-143)

.. code-block:: python

   def load_production_model():
       """Charge le modèle en production depuis MLflow
       Utilise l'alias pour récupérer la dernière version validée
       """
       try:
           client = MlflowClient()
           
           # Récupérer les informations du modèle via l'alias
           model_version_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
           version = model_version_info.version
           
           # 🔑 POINT CLÉ: Vérifier si on doit recharger le modèle
           if app_state["model_version"] != version:
               print(f"🔄 Chargement du modèle {MODEL_NAME} (Version {version})...")
               model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
               model = mlflow.pyfunc.load_model(model_uri)
               
               app_state["model"] = model
               app_state["model_version"] = version
               
               print(f"✅ Modèle chargé : Version {version}")
           
           return app_state["model"], app_state["model_version"]
       except Exception as e:
           raise HTTPException(status_code=503, detail=f"Erreur: {str(e)}")

**Questions à poser** :

* ❓ Quand cette fonction est-elle appelée ?
* **Réponse** : **À chaque requête de prédiction** (ligne ~250 dans ``/predict``)
* ❓ Comment éviter de télécharger le modèle à chaque fois ?
* **Réponse** : La **vérification de version** (``if app_state["model_version"] != version``) garantit qu'on ne recharge que si nécessaire.

3. Cache Streamlit
^^^^^^^^^^^^^^^^^^

**Fichier** : ``src/front/app.py``

**Fonction clé** : ``get_model_info()`` (lignes ~240-260)

.. code-block:: python

   @st.cache_data(ttl=5)
   def get_model_info():
       """Récupère les informations du modèle avec cache de 5 secondes"""
       try:
           response = requests.get(f"{API_URL}/model-info", timeout=5)
           if response.status_code == 200:
               return response.json()
           return None
       except Exception as e:
           st.error(f"⚠️ Erreur de connexion: {e}")
           return None

**Questions à poser** :

* ❓ Pourquoi un TTL de 5 secondes ?
* **Réponse** : Équilibre entre **détection rapide** des mises à jour et **limitation de la charge** sur l'API.

🎤 Entretien Oral - Questions Fréquentes
-----------------------------------------

Architecture
~~~~~~~~~~~~

**Q1: Pourquoi découpler le stockage (MinIO) de l'API ?**

**Réponse attendue** :

1. **Scalabilité** : Le stockage peut grandir indépendamment (ajout de disques)
2. **Résilience** : Si l'API crashe, les modèles sont **préservés**
3. **Partage** : Plusieurs instances d'API peuvent utiliser les **mêmes modèles**
4. **Séparation des responsabilités** : Stockage ≠ Serving ≠ Training

**Q2: Pourquoi utiliser MLflow comme Model Registry ?**

**Réponse attendue** :

1. **Versionnage automatique** : Chaque modèle a un numéro de version unique
2. **Metadata tracking** : Paramètres, métriques, artefacts liés
3. **Alias** : Permet de désigner dynamiquement un modèle "Production"
4. **Governance** : Historique complet, transitions d'état (Staging → Production)

Implémentation
~~~~~~~~~~~~~~

**Q3: Comment fonctionne le hot-reloading ?**

**Réponse attendue** :

1. À **chaque requête**, l'API interroge MLflow pour connaître la version "Production"
2. Si la version a **changé**, elle télécharge le nouveau modèle depuis MinIO
3. Le modèle est **mis en cache** en mémoire (``app_state``)
4. **Aucun redémarrage** de l'API n'est nécessaire

**Q4: Que se passe-t-il si MLflow est indisponible pendant une requête ?**

**Réponse attendue** :

1. L'API retourne une **erreur 503** (Service Unavailable)
2. Si un modèle était **déjà chargé**, il reste en mémoire (dernier modèle connu)
3. Les **dépendances Docker** (``depends_on``) garantissent que MLflow démarre **avant** l'API

Déploiement
~~~~~~~~~~~

**Q5: Comment gérer plusieurs instances d'API (load balancing) ?**

**Réponse attendue** :

1. Déployer plusieurs conteneurs ``api`` avec ``docker-compose scale api=3``
2. Ajouter un **reverse proxy** (Nginx, Traefik) pour le load balancing
3. Chaque instance partage le **même Model Registry** (MLflow) et **stockage** (MinIO)
4. Le hot-reloading fonctionne **indépendamment** sur chaque instance

**Q6: Quelles améliorations possibles pour la production ?**

**Réponse attendue** :

1. **Authentification** : Ajouter une couche d'authentification (OAuth2, API Keys)
2. **Monitoring** : Prometheus + Grafana pour métriques (latence, throughput)
3. **Canary Deployment** : Router 10% du trafic vers la nouvelle version
4. **A/B Testing** : Comparer deux modèles en parallèle
5. **CI/CD** : GitHub Actions pour tests automatiques et déploiement
6. **Health checks avancés** : Vérifier la qualité des prédictions en temps réel

🛠️ Commandes de Vérification
------------------------------

Vérifier les Logs
~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Logs de l'API (pour voir le rechargement)
   docker-compose logs -f api

   # Logs de MLflow
   docker-compose logs -f mlflow

**Indicateur de succès** : Observer les messages suivants dans les logs de l'API :

.. code-block:: text

   🔄 Chargement du modèle iris_classifier (Version 2) via alias 'Production'...
   ✅ Modèle chargé avec succès: Version 2

Vérifier l'État de l'API
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Health check
   curl http://localhost:8000/health

   # Informations du modèle
   curl http://localhost:8000/model-info

Faire une Prédiction Manuelle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   curl -X POST http://localhost:8000/predict `
     -H "Content-Type: application/json" `
     -d '{
       "sepal_length": 5.1,
       "sepal_width": 3.5,
       "petal_length": 1.4,
       "petal_width": 0.2
     }'

**Réponse attendue** :

.. code-block:: json

   {
     "prediction": 0,
     "prediction_label": "Setosa",
     "probabilities": {...},
     "model_version": "2",
     "model_name": "iris_classifier"
   }

📈 Grille d'Évaluation Suggérée
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 10 60

   * - Critère
     - Points
     - Validation
   * - **Architecture**
     - /5
     - ✅ 4 services orchestrés, volumes persistants, réseau isolé
   * - **Réactivité**
     - /5
     - ✅ Détection < 10s, hot-reloading fonctionnel
   * - **Traçabilité**
     - /4
     - ✅ Version dans chaque réponse, logs détaillés
   * - **Isolation**
     - /3
     - ✅ Conteneurs séparés, dépendances gérées
   * - **Persistance**
     - /3
     - ✅ Données survivent à docker-compose down
   * - **Code Quality**
     - /5
     - ✅ Variables d'environnement, gestion d'erreurs, documentation
   * - **Documentation**
     - /3
     - ✅ README, documentation Sphinx, commentaires dans le code
   * - **Démonstration**
     - /5
     - ✅ Scénarios automatique ET manuel démontrés
   * - **Entretien**
     - /7
     - ✅ Justifications techniques claires
   * - **TOTAL**
     - **/40**
     - 

🚀 Résumé des Réussites du Projet
----------------------------------

✅ **Objectif atteint** : Mise à jour de modèle **sans interruption de service**

✅ **Hot-reloading** : L'API détecte et charge automatiquement les nouveaux modèles

✅ **Traçabilité** : Chaque prédiction affiche la version du modèle

✅ **Flexibilité** : Promotion automatique OU manuelle selon les besoins

✅ **Scalabilité** : Architecture découplée prête pour la production

✅ **Résilience** : Données persistantes, gestion d'erreurs robuste
