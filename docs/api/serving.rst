API de Serving
==============

Module: ``api.main``
--------------------

Ce module implémente l'API FastAPI pour servir les prédictions avec hot-reloading automatique.

Classes Pydantic
~~~~~~~~~~~~~~~~

IrisFeatures
^^^^^^^^^^^^

.. autoclass:: api.main.IrisFeatures
   :members:
   :undoc-members:
   :show-inheritance:

PredictionResponse
^^^^^^^^^^^^^^^^^^

.. autoclass:: api.main.PredictionResponse
   :members:
   :undoc-members:
   :show-inheritance:

Fonctions Principales
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: api.main.load_production_model

.. autofunction:: api.main.lifespan

Endpoints
~~~~~~~~~

GET /
^^^^^

**Endpoint racine avec informations sur l'API**

.. code-block:: http

   GET / HTTP/1.1
   Host: localhost:8000

**Réponse:**

.. code-block:: json

   {
     "message": "ML Factory API",
     "status": "running",
     "model_name": "iris_classifier",
     "model_alias": "Production",
     "endpoints": {
       "health": "/health",
       "predict": "/predict",
       "model_info": "/model-info"
     }
   }

GET /health
^^^^^^^^^^^

**Health check de l'API et du modèle**

.. code-block:: http

   GET /health HTTP/1.1
   Host: localhost:8000

**Réponse (succès):**

.. code-block:: json

   {
     "status": "healthy",
     "model_loaded": true,
     "model_version": "2",
     "model_name": "iris_classifier"
   }

**Codes de statut:**

- ``200 OK``: Service opérationnel
- ``503 Service Unavailable``: Service non disponible

GET /model-info
^^^^^^^^^^^^^^^

**Informations détaillées du modèle en production**

.. code-block:: http

   GET /model-info HTTP/1.1
   Host: localhost:8000

**Réponse:**

.. code-block:: json

   {
     "model_name": "iris_classifier",
     "model_version": "2",
     "model_alias": "Production",
     "run_id": "abc123def456",
     "status": "READY",
     "creation_timestamp": 1710604800000
   }

POST /predict
^^^^^^^^^^^^^

**Prédiction sur une instance individuelle**

.. code-block:: http

   POST /predict HTTP/1.1
   Host: localhost:8000
   Content-Type: application/json

   {
     "sepal_length": 5.1,
     "sepal_width": 3.5,
     "petal_length": 1.4,
     "petal_width": 0.2
   }

**Réponse:**

.. code-block:: json

   {
     "prediction": 0,
     "prediction_label": "Setosa",
     "probabilities": {
       "Setosa": 0.95,
       "Versicolor": 0.03,
       "Virginica": 0.02
     },
     "model_version": "2",
     "model_name": "iris_classifier"
   }

**Codes de statut:**

- ``200 OK``: Prédiction réussie
- ``422 Unprocessable Entity``: Données invalides
- ``500 Internal Server Error``: Erreur lors de la prédiction
- ``503 Service Unavailable``: Modèle non chargé

POST /predict-batch
^^^^^^^^^^^^^^^^^^^

**Prédictions en batch sur plusieurs instances**

.. code-block:: http

   POST /predict-batch HTTP/1.1
   Host: localhost:8000
   Content-Type: application/json

   [
     {
       "sepal_length": 5.1,
       "sepal_width": 3.5,
       "petal_length": 1.4,
       "petal_width": 0.2
     },
     {
       "sepal_length": 6.7,
       "sepal_width": 3.0,
       "petal_length": 5.2,
       "petal_width": 2.3
     }
   ]

**Réponse:**

.. code-block:: json

   {
     "predictions": [
       {
         "prediction": 0,
         "prediction_label": "Setosa"
       },
       {
         "prediction": 2,
         "prediction_label": "Virginica"
       }
     ],
     "model_version": "2",
     "model_name": "iris_classifier",
     "count": 2
   }

Mécanisme de Hot-Reloading
~~~~~~~~~~~~~~~~~~~~~~~~~~~

L'API implémente un système de rechargement à chaud du modèle:

.. code-block:: text

   Requête → load_production_model()
              ↓
           Récupération de l'alias "Production" via MLflow
              ↓
           Comparaison avec la version en cache
              ↓
           Version différente ?
              ↓ OUI          ↓ NON
        Rechargement      Utilisation du cache
        depuis MinIO          
              ↓                 ↓
           Mise à jour du cache
              ↓
           Prédiction avec le nouveau modèle

**Avantages:**

- ✅ Aucun redémarrage de conteneur
- ✅ Changement instantané de modèle
- ✅ Zero-downtime deployment
- ✅ Rollback rapide si nécessaire

Cache et Performance
~~~~~~~~~~~~~~~~~~~~

Le modèle est mis en cache dans ``app_state`` pour éviter des rechargements inutiles:

.. code-block:: python

   app_state = {
       "model": None,           # Modèle chargé en mémoire
       "model_version": None,   # Version actuellement chargée
       "client": None           # Client MLflow
   }

Le rechargement n'a lieu que si:

1. La requête est la première (cache vide)
2. L'alias "Production" pointe vers une nouvelle version

Configuration CORS
~~~~~~~~~~~~~~~~~~

L'API autorise toutes les origines pour faciliter l'intégration:

.. code-block:: python

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

**⚠️ En production**, restreindre les origines autorisées:

.. code-block:: python

   allow_origins=["https://votre-domaine.com"]

Exemples d'Utilisation
~~~~~~~~~~~~~~~~~~~~~~

Avec cURL
^^^^^^^^^

.. code-block:: bash

   # Health check
   curl http://localhost:8000/health

   # Prédiction
   curl -X POST http://localhost:8000/predict \
        -H "Content-Type: application/json" \
        -d '{"sepal_length": 5.1, "sepal_width": 3.5, 
             "petal_length": 1.4, "petal_width": 0.2}'

Avec Python Requests
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import requests

   # Prédiction
   url = "http://localhost:8000/predict"
   data = {
       "sepal_length": 5.1,
       "sepal_width": 3.5,
       "petal_length": 1.4,
       "petal_width": 0.2
   }

   response = requests.post(url, json=data)
   result = response.json()
   
   print(f"Classe prédite: {result['prediction_label']}")
   print(f"Version du modèle: {result['model_version']}")

Avec JavaScript/Fetch
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

   const predictFlower = async (features) => {
     const response = await fetch('http://localhost:8000/predict', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
       },
       body: JSON.stringify(features),
     });
     
     const result = await response.json();
     console.log(`Prédiction: ${result.prediction_label}`);
     console.log(`Version: ${result.model_version}`);
   };

   // Utilisation
   predictFlower({
     sepal_length: 5.1,
     sepal_width: 3.5,
     petal_length: 1.4,
     petal_width: 0.2
   });

Gestion des Erreurs
~~~~~~~~~~~~~~~~~~~

Modèle Non Trouvé
^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "detail": "Impossible de charger le modèle en production: ..."
   }

**Causes possibles:**

- Aucun modèle entraîné
- Alias "Production" non défini
- Problème de connexion à MLflow ou MinIO

**Solution:**

1. Entraîner un modèle via ``src/train/train.py``
2. Vérifier que l'alias existe sur MLflow UI
3. Vérifier la connectivité réseau

Données Invalides
^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "detail": [
       {
         "loc": ["body", "sepal_length"],
         "msg": "field required",
         "type": "value_error.missing"
       }
     ]
   }

**Solution:** Fournir toutes les features requises avec les bons types.

Monitoring et Logs
~~~~~~~~~~~~~~~~~~

Les logs de l'API incluent:

- ✅ Démarrage et arrêt de l'application
- ✅ Chargement et rechargement des modèles
- ✅ Erreurs et exceptions
- ✅ Informations de version

.. code-block:: bash

   # Voir les logs en temps réel
   docker-compose logs -f api

Déploiement
~~~~~~~~~~~

Production avec Uvicorn
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

Avec Docker
^^^^^^^^^^^

.. code-block:: bash

   docker build -t ml-factory-api ./src/api
   docker run -p 8000:8000 ml-factory-api

Bonnes Pratiques
~~~~~~~~~~~~~~~~

1. **Rate Limiting**
   
   En production, implémenter un rate limiting pour éviter les abus.

2. **Authentication**
   
   Ajouter une authentification (API keys, OAuth) pour sécuriser l'accès.

3. **Logging Structuré**
   
   Utiliser un logger structuré (JSON) pour faciliter l'analyse.

4. **Métriques**
   
   Exposer des métriques Prometheus pour le monitoring.

5. **Timeouts**
   
   Configurer des timeouts appropriés pour les requêtes MLflow et MinIO.
