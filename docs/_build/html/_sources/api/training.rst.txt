API de Training
===============

Module: ``train.train``
-----------------------

Ce module gère l'entraînement des modèles de classification Iris et leur enregistrement dans MLflow.

Fonctions Principales
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: train.train.load_data

.. autofunction:: train.train.train_model

Configuration
~~~~~~~~~~~~~

Variables d'Environnement
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Variable
     - Description
     - Défaut
   * - ``MLFLOW_TRACKING_URI``
     - URI du serveur MLflow
     - ``http://localhost:5000``
   * - ``MODEL_NAME``
     - Nom du modèle dans le registre
     - ``iris_classifier``
   * - ``AWS_ACCESS_KEY_ID``
     - Clé d'accès MinIO/S3
     - ``minioadmin``
   * - ``AWS_SECRET_ACCESS_KEY``
     - Secret MinIO/S3
     - ``minioadmin``
   * - ``MLFLOW_S3_ENDPOINT_URL``
     - URL du endpoint S3
     - ``http://localhost:9000``

Paramètres Globaux
^^^^^^^^^^^^^^^^^^

.. py:data:: AUTO_PROMOTE
   :type: bool
   :value: True

   Active ou désactive la promotion automatique en Production.
   
   - ``True``: Le modèle est automatiquement promu avec l'alias "Production"
   - ``False``: Nécessite une promotion manuelle via l'UI MLflow

Types de Modèles Supportés
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Régression Logistique
^^^^^^^^^^^^^^^^^^^^^

Modèle léger et rapide, idéal pour Phase 1:

.. code-block:: python

   version, acc = train_model("logistic_regression")

**Paramètres:**
   - ``max_iter``: 200
   - ``solver``: "lbfgs"
   - ``random_state``: 42

Random Forest
^^^^^^^^^^^^^

Modèle plus complexe avec meilleure performance, pour Phase 2:

.. code-block:: python

   version, acc = train_model("random_forest")

**Paramètres:**
   - ``n_estimators``: 100
   - ``max_depth``: 5
   - ``random_state``: 42

Métriques Enregistrées
~~~~~~~~~~~~~~~~~~~~~~

Pour chaque entraînement, les métriques suivantes sont loggées dans MLflow:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Métrique
     - Description
   * - ``accuracy``
     - Précision globale sur l'ensemble de test
   * - ``f1_score``
     - F1-Score weighted (moyenne pondérée)
   * - ``precision``
     - Précision weighted
   * - ``recall``
     - Rappel weighted

Workflow d'Entraînement
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Chargement du dataset Iris
      ↓
   2. Split train/test (80/20)
      ↓
   3. Création d'un échantillon de test pour le frontend
      ↓
   4. Entraînement du modèle
      ↓
   5. Calcul des métriques
      ↓
   6. Logging dans MLflow
      ↓
   7. Enregistrement dans Model Registry
      ↓
   8. Promotion (auto ou manuelle)

Exemples d'Utilisation
~~~~~~~~~~~~~~~~~~~~~~

Entraînement avec Promotion Automatique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Dans train.py, s'assurer que AUTO_PROMOTE = True
   from train import train_model

   # Entraîner une régression logistique
   version, accuracy = train_model("logistic_regression")
   print(f"Modèle v{version} entraîné avec succès")
   print(f"Accuracy: {accuracy:.4f}")

   # Le modèle est automatiquement en Production ✅

Entraînement avec Promotion Manuelle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Dans train.py, définir AUTO_PROMOTE = False
   from train import train_model

   # Entraîner un random forest
   version, accuracy = train_model("random_forest")
   
   # ⚠️ Modèle enregistré mais pas encore en Production
   # Aller sur MLflow UI pour promouvoir manuellement

Exécution depuis la Ligne de Commande
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Installation des dépendances
   cd src/train
   pip install -e ../../[train]

   # Entraînement
   python train.py

   # Avec variables d'environnement personnalisées
   MLFLOW_TRACKING_URI=http://localhost:5000 python train.py

Gestion des Erreurs
~~~~~~~~~~~~~~~~~~~

Connexion MLflow Échouée
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Si MLflow n'est pas accessible
   # Erreur: requests.exceptions.ConnectionError
   
   # Solution: Vérifier que MLflow est démarré
   docker-compose ps mlflow

Alias Production Déjà Utilisé
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lors de la promotion automatique, l'ancien alias est automatiquement déplacé vers la nouvelle version.

Espace de Stockage Insuffisant
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MinIO requiert de l'espace pour stocker les modèles. Vérifier le volume Docker:

.. code-block:: bash

   docker volume inspect projet_2_1_mlfactory_minio_data

Bonnes Pratiques
~~~~~~~~~~~~~~~~

1. **Tests de Modèles**
   
   Toujours valider les métriques avant de promouvoir en Production.

2. **Nommage des Runs**
   
   Les runs sont automatiquement nommés ``{model_type}_training`` pour faciliter
   l'identification dans MLflow.

3. **Reproductibilité**
   
   Tous les modèles utilisent ``random_state=42`` pour assurer la reproductibilité.

4. **Monitoring**
   
   Vérifier les métriques dans MLflow UI après chaque entraînement.

5. **Promotion Prudente**
   
   En production réelle, utiliser le mode manuel (``AUTO_PROMOTE=False``) et
   valider le modèle avant de le promouvoir.
