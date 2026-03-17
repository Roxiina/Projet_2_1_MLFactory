Installation
============

Ce guide vous accompagne dans l'installation complète de ML Factory.

Prérequis
---------

Avant de commencer, assurez-vous d'avoir installé:

Obligatoires
~~~~~~~~~~~~

* **Docker** (version 20.10+)
* **Docker Compose** (version 2.0+)
* **Python** (version 3.10+)

Recommandés
~~~~~~~~~~~

* **UV** - Gestionnaire de paquets Python rapide
* **Git** - Pour cloner le repository
* **VS Code** ou autre IDE

Vérification des Prérequis
---------------------------

.. code-block:: bash

   # Docker
   docker --version
   # Docker version 24.0.0, build ...

   # Docker Compose
   docker-compose --version
   # Docker Compose version v2.20.0

   # Python
   python --version
   # Python 3.11.0

Installation de UV (Recommandé)
-------------------------------

UV est un gestionnaire de paquets Python ultra-rapide:

Windows (PowerShell)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Installation via PowerShell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

Linux/MacOS
~~~~~~~~~~~

.. code-block:: bash

   # Installation via curl
   curl -LsSf https://astral.sh/uv/install.sh | sh

Vérification
~~~~~~~~~~~~

.. code-block:: bash

   uv --version
   # uv 0.1.0

Installation du Projet
----------------------

Méthode 1: Avec UV (Recommandée)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Cloner le repository
   git clone https://github.com/simplon-france/ml-factory.git
   cd ml-factory

   # Installer les dépendances
   uv pip install -e .

   # Installer les dépendances de développement
   uv pip install -e ".[dev]"

   # Installer les dépendances de documentation
   uv pip install -e ".[docs]"

   # Installer toutes les dépendances
   uv pip install -e ".[all]"

Méthode 2: Avec Pip
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Cloner le repository
   git clone https://github.com/simplon-france/ml-factory.git
   cd ml-factory

   # Créer un environnement virtuel
   python -m venv venv

   # Activer l'environnement (Windows)
   .\venv\Scripts\activate

   # Activer l'environnement (Linux/MacOS)
   source venv/bin/activate

   # Installer les dépendances
   pip install -e .

   # Ou avec toutes les dépendances
   pip install -e ".[all]"

Infrastructure Docker
---------------------

Configuration
~~~~~~~~~~~~~

1. **Vérifier le fichier .env**

   Le fichier ``.env`` contient les variables de configuration:

   .. code-block:: bash

      # MinIO Configuration
      MINIO_ROOT_USER=minioadmin
      MINIO_ROOT_PASSWORD=minioadmin
      
      # MLflow Configuration
      MLFLOW_TRACKING_URI=http://mlflow:5000
      
      # Model Configuration
      MODEL_NAME=iris_classifier
      MODEL_ALIAS=Production

2. **Personnaliser (optionnel)**

   Modifiez les valeurs selon vos besoins.

Démarrage des Services
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Démarrer tous les services
   docker-compose up -d

   # Vérifier l'état des services
   docker-compose ps

   # Voir les logs
   docker-compose logs -f

**Temps de démarrage:** ~30 secondes

Services Disponibles
~~~~~~~~~~~~~~~~~~~~

Une fois démarrés, les services sont accessibles:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Service
     - URL
     - Credentials
   * - MLflow UI
     - http://localhost:5000
     - Aucun
   * - MinIO Console
     - http://localhost:9001
     - minioadmin/minioadmin
   * - FastAPI Docs
     - http://localhost:8000/docs
     - Aucun
   * - Streamlit App
     - http://localhost:8501
     - Aucun

Vérification de l'Installation
-------------------------------

Tests de Connectivité
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test de l'API
   curl http://localhost:8000/health

   # Réponse attendue (sans modèle entraîné):
   # {"status":"healthy","model_loaded":false,...}

Tests de Base
~~~~~~~~~~~~~

.. code-block:: bash

   # Entraîner un premier modèle
   cd src/train
   python train.py

   # Test de prédiction via l'API
   curl -X POST http://localhost:8000/predict \
        -H "Content-Type: application/json" \
        -d '{"sepal_length":5.1,"sepal_width":3.5,
             "petal_length":1.4,"petal_width":0.2}'

Résolution de Problèmes
-----------------------

Port Déjà Utilisé
~~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: text

   ERROR: for mlflow  Cannot start service mlflow: 
   Ports are not available: port is already allocated

**Solution:**

Modifier les ports dans ``docker-compose.yml``:

.. code-block:: yaml

   services:
     mlflow:
       ports:
         - "5001:5000"  # Changer 5000 → 5001

Docker Non Démarré
~~~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: text

   Cannot connect to the Docker daemon

**Solution:**

.. code-block:: bash

   # Windows: Démarrer Docker Desktop
   # Linux: Démarrer le service Docker
   sudo systemctl start docker

Permissions Insuffisantes
~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur (Linux):**

.. code-block:: text

   permission denied while trying to connect to the Docker daemon

**Solution:**

.. code-block:: bash

   # Ajouter l'utilisateur au groupe docker
   sudo usermod -aG docker $USER
   
   # Se déconnecter/reconnecter ou redémarrer la session

Espace Disque Insuffisant
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: text

   no space left on device

**Solution:**

.. code-block:: bash

   # Nettoyer Docker
   docker system prune -a

   # Vérifier l'espace des volumes
   docker system df

Dépendances Python Non Installées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: text

   ModuleNotFoundError: No module named 'mlflow'

**Solution:**

.. code-block:: bash

   # Avec UV
   uv pip install -e .

   # Avec pip
   pip install -e .

Prochaines Étapes
-----------------

Maintenant que l'installation est terminée:

1. 📖 Consultez le :doc:`quickstart` pour démarrer rapidement
2. 🔬 Entraînez votre premier modèle
3. 🎯 Testez le Zero-Downtime deployment
4. 📚 Explorez la :doc:`/api/training` pour plus de détails

Désinstallation
---------------

Arrêt des Services
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Arrêter les services
   docker-compose down

   # Arrêter et supprimer les volumes (⚠️ supprime les données)
   docker-compose down -v

Suppression Complète
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Supprimer les images Docker
   docker rmi $(docker images -q ml-factory-*)

   # Supprimer l'environnement virtuel
   rm -rf venv/

   # Supprimer le projet
   cd ..
   rm -rf ml-factory/

Support
-------

En cas de problème:

* 📖 Consultez la :doc:`troubleshooting`
* 🐛 Ouvrez une issue sur `GitHub <https://github.com/simplon-france/ml-factory/issues>`_
* 💬 Contactez l'équipe Simplon France
