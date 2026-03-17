🚀 Guide de Démarrage Rapide
============================

Ce guide vous accompagne pas à pas pour mettre en place votre plateforme MLOps avec déploiement Zero-Downtime.

⚡ Démarrage Express (5 minutes)
---------------------------------

1️⃣ Lancer l'infrastructure Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Démarrer tous les services (MLflow, MinIO, API, Frontend)
   docker-compose up -d

   # Vérifier que tout est démarré
   docker-compose ps

**Services disponibles :**

* 🌐 **Streamlit UI** : http://localhost:8501
* 📊 **API FastAPI** : http://localhost:8000/docs
* 🔬 **MLflow UI** : http://localhost:5000
* 💾 **MinIO Console** : http://localhost:9001 (admin / minioadmin)

2️⃣ Entraîner le premier modèle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Activer l'environnement virtuel
   .venv\Scripts\Activate.ps1

   # Installer les dépendances
   pip install -r requirements.txt

   # Lancer l'entraînement (Régression Logistique)
   cd src\train
   python train.py

**📝 Ce qui se passe :**

* ✅ Entraînement du modèle Logistic Regression
* ✅ Logging des métriques dans MLflow
* ✅ Enregistrement dans le Model Registry avec l'alias "Production"
* ✅ L'API détecte automatiquement le nouveau modèle !

3️⃣ Tester l'interface
~~~~~~~~~~~~~~~~~~~~~~

1. Ouvrez http://localhost:8501
2. Vous devriez voir **Version: v1** dans le badge
3. Utilisez les sliders pour faire une prédiction
4. Le résultat affiche la version du modèle utilisé ✅

🔄 Démonstration du Hot-Reloading (Zero-Downtime)
--------------------------------------------------

Cette section prouve que vous pouvez changer de modèle **SANS redémarrer l'API** !

Étape 1 : Vérifier le modèle actuel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Ouvrez l'interface Streamlit : http://localhost:8501
* Notez la **version affichée** (normalement ``v1``)
* Faites une prédiction et vérifiez que ça fonctionne

Étape 2 : Entraîner un nouveau modèle (Random Forest)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Éditez le fichier ``src/train/train.py`` :

.. code-block:: python

   # À la ligne ~232, changez la ligne:
   # version, acc = train_model("logistic_regression")

   # Par:
   version, acc = train_model("random_forest")

Puis exécutez :

.. code-block:: powershell

   python src\train\train.py

**📝 Ce qui se passe :**

* ✅ Entraînement d'un Random Forest (modèle plus complexe)
* ✅ Création de la Version 2 dans MLflow
* ✅ **Promotion automatique** avec l'alias "Production"

Étape 3 : Observer le changement automatique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **SANS redémarrer l'API** (important !)
2. Retournez sur Streamlit : http://localhost:8501
3. Cliquez sur "🔄 Rafraîchir les Informations du Modèle"
4. **La version devrait maintenant afficher** ``v2`` **🎉**

Étape 4 : Vérifier la traçabilité
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Faites une nouvelle prédiction :

* Le résultat affiche **"Modèle: Version 2"**
* L'API utilise maintenant le Random Forest
* **Aucune interruption de service !**

🎭 Mode Manuel : Promotion via l'UI MLflow
-------------------------------------------

Simulons une validation humaine avant la mise en production.

Étape 1 : Désactiver la promotion automatique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Éditez ``src/train/train.py`` :

.. code-block:: python

   # À la ligne ~60, changez:
   AUTO_PROMOTE = True

   # Par:
   AUTO_PROMOTE = False

Étape 2 : Entraîner un nouveau modèle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Dans train.py, ligne ~232, changez de nouveau:
   version, acc = train_model("logistic_regression")

Exécutez :

.. code-block:: powershell

   python src\train\train.py

**📝 Ce qui se passe :**

* ✅ Création de la Version 3 (Logistic Regression)
* ⚠️ **Mais elle n'est PAS promue automatiquement !**
* L'API continue d'utiliser la Version 2

Étape 3 : Promotion manuelle via MLflow UI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Ouvrez l'interface MLflow : http://localhost:5000
2. Cliquez sur "**Models**" dans le menu
3. Sélectionnez le modèle "**iris_classifier**"
4. Vous verrez les 3 versions enregistrées
5. Cliquez sur la **Version 3**
6. Dans "**Aliases**", cliquez sur "**Set alias**"
7. Saisissez "**Production**" et validez

**🎯 Résultat :**

* La Version 3 est maintenant en production
* Retournez sur Streamlit et rafraîchissez
* L'API utilise maintenant la Version 3 (sans redémarrage !)

📊 Tableau de Bord des Services
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 10 30

   * - Service
     - URL
     - Port
     - Usage
   * - **Streamlit**
     - http://localhost:8501
     - 8501
     - Interface utilisateur pour tester les prédictions
   * - **FastAPI Docs**
     - http://localhost:8000/docs
     - 8000
     - Documentation Swagger de l'API
   * - **MLflow UI**
     - http://localhost:5000
     - 5000
     - Suivi des expériences et Model Registry
   * - **MinIO Console**
     - http://localhost:9001
     - 9001
     - Gestion du stockage S3 des artefacts
   * - **MinIO API**
     - http://localhost:9000
     - 9000
     - Endpoint S3 pour MLflow

🛠️ Commandes Utiles
--------------------

Gestion Docker
~~~~~~~~~~~~~~

.. code-block:: powershell

   # Démarrer tous les services
   docker-compose up -d

   # Voir les logs en temps réel
   docker-compose logs -f

   # Voir les logs d'un service spécifique
   docker-compose logs -f api
   docker-compose logs -f mlflow

   # Arrêter tous les services (GARDE les données)
   docker-compose stop

   # Arrêter et SUPPRIMER les conteneurs (GARDE les volumes)
   docker-compose down

   # Supprimer TOUT (conteneurs + volumes) - ⚠️ PERTE DE DONNÉES
   docker-compose down -v

   # Redémarrer un service spécifique
   docker-compose restart api

   # Reconstruire un service après modification du code
   docker-compose up -d --build api

Vérifications
~~~~~~~~~~~~~

.. code-block:: powershell

   # Vérifier la santé de l'API
   curl http://localhost:8000/health

   # Obtenir des infos sur le modèle
   curl http://localhost:8000/model-info

   # Faire une prédiction via l'API
   curl -X POST http://localhost:8000/predict `
     -H "Content-Type: application/json" `
     -d '{
       "sepal_length": 5.1,
       "sepal_width": 3.5,
       "petal_length": 1.4,
       "petal_width": 0.2
     }'

Entraînement
~~~~~~~~~~~~

.. code-block:: powershell

   # Entraîner une Régression Logistique
   cd src\train
   python train.py  # (avec model_type="logistic_regression" dans le code)

   # Entraîner un Random Forest
   # Modifier train.py: model_type="random_forest", puis:
   python train.py

🔍 Vérification de la Traçabilité
----------------------------------

Chaque réponse de l'API contient **explicitement** :

* ``model_version`` : Numéro de version du modèle (ex: "2")
* ``model_name`` : Nom du modèle (ex: "iris_classifier")

**Exemple de réponse :**

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

🎯 Critères de Réussite du Projet
----------------------------------

Voici ce qui prouve que votre ML Factory fonctionne correctement :

✅ Réactivité (< 10 secondes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ☐ Promouvoir un nouveau modèle via MLflow UI
* ☐ Rafraîchir l'interface Streamlit
* ☐ La nouvelle version s'affiche en moins de 10 secondes

✅ Traçabilité Totale
~~~~~~~~~~~~~~~~~~~~~

* ☐ Chaque prédiction affiche le numéro de version du modèle
* ☐ Les logs de l'API montrent les rechargements de modèle
* ☐ MLflow garde l'historique de toutes les versions

✅ Isolation des Services
~~~~~~~~~~~~~~~~~~~~~~~~~

* ☐ Chaque service tourne dans son propre conteneur
* ☐ Les dépendances sont gérées indépendamment
* ☐ Les services communiquent via le réseau Docker

✅ Persistance des Données
~~~~~~~~~~~~~~~~~~~~~~~~~~

* ☐ Exécuter ``docker-compose down`` (sans ``-v``)
* ☐ Redémarrer avec ``docker-compose up -d``
* ☐ Les modèles et métadonnées MLflow sont toujours présents

📚 Architecture Détaillée
--------------------------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────────┐
   │                         Utilisateur                              │
   └────────────────────┬────────────────────────────────────────────┘
                        │
                        │ HTTP
                        ▼
             ┌──────────────────────┐
             │   Streamlit (Port    │
             │      8501)           │
             └──────────┬───────────┘
                        │
                        │ REST API
                        ▼
             ┌──────────────────────┐         ┌──────────────────┐
             │   FastAPI (Port      │◄────────┤   MLflow         │
             │      8000)           │  gRPC   │   (Port 5000)    │
             │                      ├────────►│                  │
             │  - Hot-Reloading     │         │  - Tracking      │
             │  - Model Cache       │         │  - Registry      │
             │  - Version Check     │         │  - Aliases       │
             └──────────┬───────────┘         └────────┬─────────┘
                        │                              │
                        │                              │ S3 API
                        │                              ▼
                        │                  ┌──────────────────────┐
                        │                  │   MinIO (Port 9000)  │
                        └─────────────────►│                      │
                           S3 API          │  - Artifact Storage  │
                                           │  - Model Files       │
                                           └──────────────────────┘

Flux de Données
~~~~~~~~~~~~~~~

1. **Entraînement** (src/train/train.py) :
   
   * Entraîne le modèle avec scikit-learn
   * Logs les métriques dans MLflow
   * Enregistre le modèle dans le Model Registry
   * Promeut en "Production" (auto ou manuel)
   * Stocke les artefacts dans MinIO

2. **Prédiction** (src/api/main.py) :
   
   * Reçoit une requête de prédiction
   * Vérifie si une nouvelle version "Production" existe
   * Charge le modèle depuis MinIO si nécessaire
   * Met en cache le modèle en mémoire
   * Retourne la prédiction + la version du modèle

3. **Interface** (src/front/app.py) :
   
   * Affiche la version actuelle du modèle
   * Permet de saisir des features
   * Envoie les requêtes à l'API
   * Affiche les résultats avec la version

🎓 Points Clés pour l'Évaluation
---------------------------------

Démonstration Technique
~~~~~~~~~~~~~~~~~~~~~~

* Montrer le passage de v1 (Logistic Regression) à v2 (Random Forest)
* Prouver que l'API ne redémarre pas (vérifier les logs)
* Montrer que le badge de version change sur Streamlit

Revue de Code
~~~~~~~~~~~~~

* Montrer le fichier .env et .env.local
* Expliquer le mécanisme de hot-reloading dans main.py
* Montrer la gestion des erreurs et la robustesse

Entretien Oral - Questions Possibles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Q: Pourquoi découpler le stockage (MinIO) de l'API ?**

**R:**

* **Scalabilité** : Le stockage peut grandir indépendamment
* **Résilience** : Si l'API crashe, les modèles sont préservés
* **Partage** : Plusieurs instances d'API peuvent accéder aux mêmes modèles
* **Séparation des responsabilités** : Stockage ≠ Serving

**Q: Comment fonctionne le hot-reloading ?**

**R:**

* À chaque requête de prédiction, l'API vérifie la version via l'alias "Production"
* Si la version a changé, elle télécharge le nouveau modèle depuis MinIO
* Le modèle est mis en cache en mémoire (app_state)
* Aucun redémarrage nécessaire !

**Q: Que se passe-t-il si MLflow est indisponible ?**

**R:**

* L'API retourne une erreur 503 (Service Unavailable)
* Le dernier modèle chargé reste en mémoire (si déjà chargé)
* Les dépendances Docker (depends_on) garantissent l'ordre de démarrage

🚀 Aller Plus Loin
-------------------

Améliorations Possibles
~~~~~~~~~~~~~~~~~~~~~~~

1. **Authentification** : Ajouter une authentification sur l'API
2. **Monitoring** : Ajouter Prometheus + Grafana pour les métriques
3. **Load Balancing** : Déployer plusieurs instances de l'API derrière Nginx
4. **CI/CD** : Automatiser les tests et le déploiement avec GitHub Actions
5. **Canary Deployment** : Router 10% du trafic vers la nouvelle version
6. **A/B Testing** : Comparer deux modèles en production

📞 Support
----------

En cas de problème :

1. Vérifiez les logs : ``docker-compose logs -f``
2. Vérifiez les variables d'environnement : ``cat .env``
3. Consultez la documentation complète dans ``docs/``
4. Vérifiez que tous les ports sont disponibles

**Dans l'onglet "Charger depuis fichier":**

1. Uploader ``data/iris_test.csv``
2. Sélectionner une ligne (ex: ligne 0)
3. Cliquer sur "🎯 Prédire cette ligne"
4. Comparer avec la vraie classe

🔄 Validation Zero-Downtime
---------------------------

Phase 1: Modèle Initial (Régression Logistique)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**État actuel:**

* ✅ Modèle Version 1 entraîné
* ✅ Alias "Production" sur Version 1
* ✅ Streamlit affiche "v1"

Phase 2: Nouveau Modèle (Random Forest)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Modifier le Script d'Entraînement**

Éditer ``src/train/train.py``:

.. code-block:: python

   # Ligne 26: Désactiver la promotion automatique
   AUTO_PROMOTE = False  # ⚠️ Passer à False

   # Ligne 178-183: Changer le modèle
   # Commenter cette ligne:
   # version, acc = train_model("logistic_regression")
   
   # Décommenter cette ligne:
   version, acc = train_model("random_forest")

**2. Entraîner le Nouveau Modèle**

.. code-block:: bash

   cd src/train
   python train.py

**Console:**

.. code-block:: text

   🚀 Démarrage de l'entraînement: random_forest
   📊 Chargement des données Iris...
   ⏳ Entraînement en cours...
   📈 Accuracy: 0.9667
   💾 Enregistrement du modèle dans MLflow...
   ✅ Modèle enregistré: iris_classifier (Version 2)
   ⚠️  Mode manuel activé: Allez sur MLflow UI pour promouvoir la Version 2

**3. Vérifier sur Streamlit**

L'application affiche toujours **Version 1** ✅

**4. Promouvoir Manuellement sur MLflow**

1. Ouvrir http://localhost:5000
2. Cliquer sur **"Models"** dans le menu
3. Sélectionner **"iris_classifier"**
4. Cliquer sur **"Version 2"**
5. Dans la section **"Aliases"**, cliquer sur **"Set alias"**
6. Entrer **"Production"** et sauvegarder

.. image:: /_static/mlflow-set-alias.png
   :alt: MLflow Set Alias

**5. Observer le Changement**

Retourner sur Streamlit:

1. Cliquer sur **"🔄 Rafraîchir les informations du modèle"**
2. Observer le changement instantané : **v1 → v2** 🎉
3. Tester une nouvelle prédiction

**🎉 Félicitations!**

Vous venez de changer de modèle **sans redémarrer un seul conteneur!**

📈 Comparaison des Modèles
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Caractéristique
     - Version 1 (LogReg)
     - Version 2 (RF)
   * - Algorithme
     - Régression Logistique
     - Random Forest
   * - Complexité
     - Faible
     - Élevée
   * - Accuracy
     - ~96%
     - ~97-98%
   * - Temps d'entraînement
     - Rapide
     - Plus lent
   * - Taille du modèle
     - Petite
     - Plus grande

🎨 Avec le Script Helper
------------------------

Pour faciliter la gestion, utilisez ``manage.ps1`` (Windows):

Commandes Principales
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Démarrer
   .\manage.ps1 start

   # Entraîner un modèle
   .\manage.ps1 train

   # Voir l'état
   .\manage.ps1 status

   # Ouvrir Streamlit
   .\manage.ps1 open front

   # Ouvrir MLflow
   .\manage.ps1 open mlflow

   # Voir les logs
   .\manage.ps1 logs

   # Arrêter
   .\manage.ps1 stop

📝 Checklist de Validation
--------------------------

.. rst-class:: checklist

   ☐ Tous les services Docker sont "Up"
   
   ☐ MLflow UI accessible (http://localhost:5000)
   
   ☐ MinIO Console accessible (http://localhost:9001)
   
   ☐ FastAPI Docs accessible (http://localhost:8000/docs)
   
   ☐ Streamlit App accessible (http://localhost:8501)
   
   ☐ Modèle Version 1 entraîné et en Production
   
   ☐ Streamlit affiche "Version 1"
   
   ☐ Prédiction fonctionne correctement
   
   ☐ Modèle Version 2 entraîné
   
   ☐ Alias "Production" déplacé manuellement sur Version 2
   
   ☐ Streamlit détecte automatiquement Version 2
   
   ☐ **Zero-Downtime confirmé!** 🎉

🔧 Tests avec cURL
------------------

Si vous préférez tester via la ligne de commande:

Health Check
~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/health

**Réponse:**

.. code-block:: json

   {
     "status": "healthy",
     "model_loaded": true,
     "model_version": "2",
     "model_name": "iris_classifier"
   }

Informations du Modèle
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/model-info

Prédiction
~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/predict \
        -H "Content-Type: application/json" \
        -d '{
          "sepal_length": 5.1,
          "sepal_width": 3.5,
          "petal_length": 1.4,
          "petal_width": 0.2
        }'

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

🎓 Concepts Clés Appris
-----------------------

✅ **Model Registry** 
   Versioning et gestion des modèles via MLflow

✅ **Hot-Reloading**
   Rechargement dynamique du modèle sans redémarrage

✅ **Zero-Downtime**
   Changement de modèle sans interruption de service

✅ **Alias Management**
   Promotion de modèles via des alias (Production, Staging)

✅ **API-First Architecture**
   Découplage complet entre modèle et application

✅ **Object Storage**
   Stockage centralisé des artefacts dans MinIO (S3)

📚 Prochaines Étapes
--------------------

Maintenant que vous maîtrisez les bases:

1. 🏗️ Explorez l':doc:`/dev-guide/architecture` détaillée
2. 📖 Consultez la :doc:`/api/training` pour personnaliser l'entraînement
3. 🔧 Lisez le :doc:`/dev-guide/deployment` pour la prod
4. 🐛 Gardez le :doc:`troubleshooting` sous la main

💡 Astuces
----------

**Démarrage Rapide**
   Ajoutez ``alias ml-start='docker-compose up -d'`` à votre shell

**Auto-refresh Streamlit**
   Streamlit rafraîchit automatiquement toutes les 5 secondes

**Logs en Direct**
   Utilisez ``docker-compose logs -f api`` pour suivre les rechargements

**MLflow Experiments**
   Tous les runs sont groupés dans l'expérience "iris_classification"

🆘 Besoin d'Aide?
-----------------

* 📖 :doc:`troubleshooting` - Solutions aux problèmes courants
* 🐛 `GitHub Issues <https://github.com/simplon-france/ml-factory/issues>`_
* 💬 Support Simplon France
