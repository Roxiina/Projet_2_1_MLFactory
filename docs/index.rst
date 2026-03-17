ML Factory Documentation
========================

.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.10+

.. image:: https://img.shields.io/badge/MLOps-Zero--Downtime-green.svg
   :alt: Zero-Downtime

.. image:: https://img.shields.io/badge/docs-sphinx-blue.svg
   :target: https://simplon-france.github.io/ml-factory/
   :alt: Documentation

Bienvenue dans la documentation de **ML Factory**, un projet MLOps complet démontrant
le déploiement "Zero-Downtime" d'un modèle de Machine Learning avec mise à jour dynamique
sans redémarrage de conteneurs.

🎯 Vision du Projet
-------------------

Ce projet illustre une architecture où le modèle ML est **totalement découplé** de
l'application qui le consomme. Grâce à **MLflow Model Registry** et **MinIO (S3)**,
vous pouvez mettre à jour l'intelligence de votre API sans jamais redémarrer un seul conteneur.

🏗️ Architecture
---------------

Le projet repose sur 4 composants principaux:

* **MLflow**: Registre des modèles et tracking des expériences
* **MinIO**: Stockage S3 compatible pour les artefacts
* **FastAPI**: API de prédiction avec hot-reloading automatique
* **Streamlit**: Interface utilisateur interactive

🚀 Démarrage Rapide
-------------------

1. **Démarrer l'infrastructure**

   .. code-block:: bash

      docker-compose up -d

2. **Entraîner le premier modèle**

   .. code-block:: bash

      cd src/train
      python train.py

3. **Tester l'application**

   Ouvrir http://localhost:8501 dans votre navigateur

📚 Sections de la Documentation
-------------------------------

.. toctree::
   :maxdepth: 2
   :caption: Guide Utilisateur

   user-guide/installation
   user-guide/quickstart
   user-guide/validation
   user-guide/troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Guide Développeur

   dev-guide/architecture
   dev-guide/api-reference
   dev-guide/training
   dev-guide/deployment

.. toctree::
   :maxdepth: 3
   :caption: Référence API

   api/training
   api/serving
   api/frontend

.. toctree::
   :maxdepth: 1
   :caption: Annexes

   contributing
   changelog
   license

🔧 Modules du Projet
--------------------

Module d'Entraînement
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: train.train
   :members:
   :undoc-members:
   :show-inheritance:

Module API (Serving)
~~~~~~~~~~~~~~~~~~~~

.. automodule:: api.main
   :members:
   :undoc-members:
   :show-inheritance:

Module Frontend
~~~~~~~~~~~~~~~

.. automodule:: front.app
   :members:
   :undoc-members:
   :show-inheritance:

✨ Fonctionnalités Principales
------------------------------

**Hot-Reloading**
   L'API détecte automatiquement les nouvelles versions du modèle et les charge
   sans interruption de service.

**Model Registry**
   Versioning et gestion des alias (Production, Staging) via MLflow.

**Zero-Downtime**
   Changement de modèle sans redémarrage de conteneurs.

**API-First**
   Architecture découplée avec API RESTful documentée.

**Interface Interactive**
   Application Streamlit pour tester les modèles facilement.

📖 Concepts Clés
----------------

Model Registry
~~~~~~~~~~~~~~

MLflow Model Registry permet de:

* Versionner les modèles
* Attribuer des alias (Production, Staging, etc.)
* Tracer la lignée des modèles
* Auditer les changements

Object Storage
~~~~~~~~~~~~~~

MinIO fournit un stockage compatible S3 pour:

* Les artefacts MLflow
* Les modèles sérialisés
* La persistance des données

Zero-Downtime Deployment
~~~~~~~~~~~~~~~~~~~~~~~~

Grâce au découplage:

1. Le modèle est stocké dans MinIO
2. L'API interroge MLflow pour l'alias "Production"
3. Si une nouvelle version est détectée, rechargement à chaud
4. Aucun redémarrage nécessaire

🔗 Liens Utiles
---------------

* `Repository GitHub <https://github.com/simplon-france/ml-factory>`_
* `MLflow Documentation <https://mlflow.org/docs/latest/>`_
* `FastAPI Documentation <https://fastapi.tiangolo.com/>`_
* `Streamlit Documentation <https://docs.streamlit.io/>`_

📝 Licence
----------

Projet éducatif - Simplon France

Indices et Tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
