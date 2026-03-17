Dépannage et Résolution de Problèmes
====================================

Ce guide propose des solutions aux problèmes courants rencontrés avec ML Factory.

🐛 Problèmes d'Infrastructure
------------------------------

Docker
~~~~~~

**Erreur: "Cannot connect to Docker daemon"**

.. code-block:: text

   Cannot connect to the Docker daemon at unix:///var/run/docker.sock

**Causes:**

* Docker n'est pas démarré
* Permissions insuffisantes (Linux)

**Solutions:**

.. code-block:: bash

   # Windows: Démarrer Docker Desktop
   
   # Linux: Démarrer le service
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Vérifier
   docker ps

   # Ajouter l'utilisateur au groupe docker (Linux)
   sudo usermod -aG docker $USER
   # Se déconnecter/reconnecter

---

**Erreur: "Port is already allocated"**

.. code-block:: text

   ERROR: for mlflow  Cannot start service mlflow: 
   Ports are not available: port is already allocated

**Solution:**

Modifier ``docker-compose.yml`` pour utiliser des ports différents:

.. code-block:: yaml

   services:
     mlflow:
       ports:
         - "5001:5000"  # Changer le port externe
     
     api:
       ports:
         - "8001:8000"
     
     front:
       ports:
         - "8502:8501"

---

**Erreur: "No space left on device"**

.. code-block:: text

   no space left on device

**Solution:**

.. code-block:: bash

   # Nettoyer Docker
   docker system prune -a --volumes
   
   # Vérifier l'espace
   docker system df

Docker Compose
~~~~~~~~~~~~~~

**Les services ne démarrent pas**

.. code-block:: bash

   # Vérifier les logs
   docker-compose logs
   
   # Logs d'un service spécifique
   docker-compose logs mlflow
   
   # Logs en direct
   docker-compose logs -f

**Redémarrer proprement:**

.. code-block:: bash

   # Arrêter
   docker-compose down
   
   # Supprimer les volumes (⚠️ perte de données)
   docker-compose down -v
   
   # Reconstruire les images
   docker-compose build --no-cache
   
   # Démarrer
   docker-compose up -d

🔌 Problèmes de Connexion
-------------------------

MLflow
~~~~~~

**Erreur: "Connection refused" lors de l'entraînement**

.. code-block:: python

   requests.exceptions.ConnectionError: 
   HTTPConnectionPool(host='mlflow', port=5000)

**Causes:**

* MLflow n'est pas démarré
* Mauvaise configuration de ``MLFLOW_TRACKING_URI``

**Solutions:**

1. **Vérifier que MLflow est actif:**

   .. code-block:: bash

      docker-compose ps mlflow
      # Doit afficher "Up" et "healthy"

2. **Vérifier depuis le host:**

   .. code-block:: bash

      curl http://localhost:5000/health

3. **Vérifier la variable d'environnement:**

   .. code-block:: bash

      # Dans .env:
      MLFLOW_TRACKING_URI=http://mlflow:5000

      # Si vous lancez train.py localement (hors Docker):
      export MLFLOW_TRACKING_URI=http://localhost:5000

MinIO
~~~~~

**Erreur: "S3 connection failed"**

**Causes:**

* MinIO n'est pas démarré
* Credentials incorrects
* Bucket n'existe pas

**Solutions:**

1. **Vérifier MinIO:**

   .. code-block:: bash

      docker-compose ps minio
      
      # Accéder à la console
      # http://localhost:9001
      # minioadmin / minioadmin

2. **Vérifier les variables d'environnement:**

   .. code-block:: bash

      # Dans .env:
      MINIO_ROOT_USER=minioadmin
      MINIO_ROOT_PASSWORD=minioadmin

3. **Créer le bucket manuellement:**

   - Ouvrir http://localhost:9001
   - Se connecter
   - Buckets → Create Bucket → "mlflow"

API
~~~

**Erreur: "Connection refused" sur /predict**

.. code-block:: bash

   curl: (7) Failed to connect to localhost port 8000

**Solutions:**

.. code-block:: bash

   # Vérifier que le conteneur est actif
   docker-compose ps api
   
   # Voir les logs
   docker-compose logs api
   
   # Redémarrer
   docker-compose restart api

🤖 Problèmes de Modèle
----------------------

Modèle Non Trouvé
~~~~~~~~~~~~~~~~~

**Erreur dans l'API:**

.. code-block:: text

   INVALID_PARAMETER_VALUE: Model 'iris_classifier' not found

**Causes:**

* Aucun modèle n'a été entraîné
* Le nom du modèle est incorrect

**Solutions:**

1. **Entraîner un modèle:**

   .. code-block:: bash

      cd src/train
      python train.py

2. **Vérifier sur MLflow UI:**

   - http://localhost:5000
   - Menu "Models"
   - Doit afficher "iris_classifier"

3. **Vérifier le nom dans ``.env``:**

   .. code-block:: bash

      MODEL_NAME=iris_classifier

Alias Non Défini
~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: text

   RESOURCE_DOES_NOT_EXIST: Model alias 'Production' not found

**Cause:**

L'alias "Production" n'est pas assigné

**Solutions:**

1. **Mode automatique** (recommandé pour dev):

   .. code-block:: python

      # Dans src/train/train.py
      AUTO_PROMOTE = True

2. **Mode manuel:**

   - Ouvrir http://localhost:5000
   - Models → iris_classifier → Version X
   - Set alias → "Production"

Rechargement du Modèle Échoue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptôme:**

L'API continue d'utiliser l'ancienne version même après promotion

**Solutions:**

1. **Vérifier les logs de l'API:**

   .. code-block:: bash

      docker-compose logs api | grep "Model reloaded"

2. **Forcer le rechargement:**

   .. code-block:: bash

      # Redémarrer le conteneur API
      docker-compose restart api

3. **Vérifier le cache Streamlit:**

   - Cliquer sur "🔄 Rafraîchir les informations"
   - Ou attendre 5 secondes (cache TTL)

📊 Problèmes de Prédiction
---------------------------

Prédiction Retourne une Erreur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur 422: "Validation Error"**

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

**Cause:**

Données d'entrée incorrectes ou manquantes

**Solution:**

Vérifier le format JSON:

.. code-block:: json

   {
     "sepal_length": 5.1,
     "sepal_width": 3.5,
     "petal_length": 1.4,
     "petal_width": 0.2
   }

**Tous les champs sont requis et doivent être des nombres.**

---

**Erreur: "Model prediction failed"**

**Solutions:**

1. **Vérifier que le modèle est chargé:**

   .. code-block:: bash

      curl http://localhost:8000/model-info

2. **Vérifier les logs:**

   .. code-block:: bash

      docker-compose logs api

3. **Test avec des valeurs connues:**

   .. code-block:: bash

      curl -X POST http://localhost:8000/predict \
           -H "Content-Type: application/json" \
           -d '{"sepal_length":5.1,"sepal_width":3.5,
                "petal_length":1.4,"petal_width":0.2}'

Prédiction en Batch Échoue
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur: "Invalid CSV format"**

**Solutions:**

1. **Vérifier le format du CSV:**

   .. code-block:: text

      sepal_length,sepal_width,petal_length,petal_width
      5.1,3.5,1.4,0.2
      4.9,3.0,1.4,0.2

2. **Headers obligatoires** (noms exacts)

3. **Pas de colonne "class" dans le CSV**

🎨 Problèmes de Frontend
-------------------------

Streamlit Ne Démarre Pas
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Vérifier le conteneur
   docker-compose ps front
   
   # Voir les logs
   docker-compose logs front
   
   # Redémarrer
   docker-compose restart front

"API Non Accessible"
~~~~~~~~~~~~~~~~~~~~

**Symptôme:**

Badge rouge dans Streamlit "❌ API inaccessible"

**Solutions:**

1. **Vérifier que l'API est active:**

   .. code-block:: bash

      docker-compose ps api
      curl http://localhost:8000/health

2. **Vérifier l'URL dans le code:**

   .. code-block:: python

      # src/front/app.py
      API_URL = os.getenv("API_URL", "http://api:8000")
      
      # Depuis l'extérieur: http://localhost:8000
      # Depuis Docker: http://api:8000

3. **Redémarrer le frontend:**

   .. code-block:: bash

      docker-compose restart front

Informations du Modèle Non Affichées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptôme:**

Pas de métrique, pas de version de modèle

**Causes:**

* Aucun modèle entraîné
* API non accessible

**Solutions:**

1. Entraîner un modèle
2. Vérifier l'API (voir ci-dessus)
3. Cliquer sur "🔄 Rafraîchir"

🐍 Problèmes Python
-------------------

ModuleNotFoundError
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ModuleNotFoundError: No module named 'mlflow'

**Solution:**

.. code-block:: bash

   # Avec UV
   uv pip install -e .
   
   # Ou avec pip
   pip install -e .

Import Errors dans le Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: python

   from train.train import train_model
   ImportError: cannot import name 'train_model'

**Solution:**

Vérifier la structure des imports:

.. code-block:: python

   # Depuis src/train/train.py
   from train import train_model
   
   # Ou en absolu
   import sys
   sys.path.append('src')
   from train.train import train_model

📝 Problèmes de Données
-----------------------

Fichier iris_test.csv Non Trouvé
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Erreur:**

.. code-block:: text

   FileNotFoundError: [Errno 2] No such file or directory: 'data/iris_test.csv'

**Solution:**

Le fichier est créé automatiquement lors du premier entraînement:

.. code-block:: bash

   cd src/train
   python train.py

Ou créez-le manuellement avec le format:

.. code-block:: text

   sepal_length,sepal_width,petal_length,petal_width,class
   5.1,3.5,1.4,0.2,0
   4.9,3.0,1.4,0.2,0

🔧 Problèmes de Performance
---------------------------

API Lente
~~~~~~~~~

**Symptôme:**

Prédictions prennent plusieurs secondes

**Causes possibles:**

* Hot-reloading vérifie MLflow à chaque requête
* MinIO lent

**Solutions:**

1. **Augmenter le cache (optionnel):**

   Modifier ``src/api/main.py`` pour ne pas vérifier à chaque requête

2. **Désactiver le hot-reloading en production:**

   .. code-block:: python

      # src/api/main.py
      # Commenter la ligne dans load_production_model():
      # return _reload_model_if_needed(...)

3. **Utiliser un volume local pour MinIO:**

   .. code-block:: yaml

      # docker-compose.yml
      minio:
        volumes:
          - ./data/minio:/data

MLflow UI Lent
~~~~~~~~~~~~~~

**Cause:**

Trop d'expériences ou de runs

**Solution:**

Nettoyer les anciennes expériences:

.. code-block:: python

   import mlflow
   
   client = mlflow.MlflowClient("http://localhost:5000")
   
   # Lister et supprimer les vieux runs
   experiment = client.get_experiment_by_name("iris_classification")
   runs = client.search_runs(experiment.experiment_id)
   
   for run in runs[10:]:  # Garder les 10 derniers
       client.delete_run(run.info.run_id)

🛠️ Commandes de Diagnostic
---------------------------

Vérifier l'État Complet
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Statut de tous les services
   docker-compose ps
   
   # Health checks
   curl http://localhost:5000/health  # MLflow
   curl http://localhost:8000/health  # API
   curl http://localhost:9000/minio/health/live  # MinIO
   
   # Logs récents
   docker-compose logs --tail=50
   
   # Ressources utilisées
   docker stats

Réinitialisation Complète
~~~~~~~~~~~~~~~~~~~~~~~~~

**⚠️ ATTENTION: Supprime toutes les données!**

.. code-block:: bash

   # Arrêter et supprimer tout
   docker-compose down -v
   
   # Supprimer les images
   docker-compose down --rmi all
   
   # Nettoyer Docker
   docker system prune -a
   
   # Redémarrer proprement
   docker-compose up -d
   
   # Réentraîner un modèle
   cd src/train
   python train.py

📋 Checklist de Dépannage
--------------------------

.. rst-class:: checklist

   ☐ Docker est démarré et accessible
   
   ☐ Tous les services Docker sont "Up" (``docker-compose ps``)
   
   ☐ Tous les services sont "healthy"
   
   ☐ Les ports ne sont pas déjà utilisés
   
   ☐ Le fichier ``.env`` existe et est configuré
   
   ☐ MLflow est accessible (http://localhost:5000)
   
   ☐ MinIO est accessible (http://localhost:9001)
   
   ☐ API est accessible (http://localhost:8000/docs)
   
   ☐ Au moins un modèle est entraîné
   
   ☐ L'alias "Production" est assigné
   
   ☐ Streamlit peut communiquer avec l'API

🆘 Besoin d'Aide Supplémentaire?
---------------------------------

Si le problème persiste:

1. **Collecter les informations:**

   .. code-block:: bash

      # Créer un rapport de diagnostic
      docker-compose ps > diagnostic.txt
      docker-compose logs >> diagnostic.txt
      docker system df >> diagnostic.txt

2. **Ouvrir une issue GitHub:**

   - Repository: https://github.com/simplon-france/ml-factory
   - Inclure le rapport de diagnostic
   - Décrire les étapes pour reproduire

3. **Contacter le support Simplon France**

📚 Ressources Supplémentaires
------------------------------

* :doc:`installation` - Guide d'installation complet
* :doc:`quickstart` - Démarrage rapide
* :doc:`/dev-guide/architecture` - Architecture détaillée
* `Docker Documentation <https://docs.docker.com/>`_

---

🎓 Problèmes Rencontrés en Développement
=========================================

Cette section documente des problèmes réels rencontrés pendant le développement du projet
et leurs solutions. Ces erreurs sont typiques d'un projet MLOps multi-conteneurs.

🔧 Problème #1: Scripts PowerShell avec Emojis
-----------------------------------------------

**Contexte**

Création de scripts de test automatisés (``TEST_SCRIPTS.ps1``, ``manage.ps1``) avec emojis
pour améliorer la lisibilité.

**Erreur rencontrée:**

.. code-block:: powershell

   Au caractère ...:17 : 136
   Jeton inattendu « : » dans l'expression ou l'instruction.
   Le terminateur ' est manquant dans la chaîne.

**Cause**

PowerShell 5.1 sur Windows ne gère pas correctement les caractères Unicode (emojis, box drawing)
dans les scripts, même avec l'encodage UTF-8.

**Symptômes:**

* ✅ ❌ ⚠️ 💡 🚀 → Erreurs de parsing
* Caractères de box drawing (╔ ║ ═) → Terminateurs manquants
* Accents français (é, è, à) → Problèmes dans les chaînes

**Solution appliquée:**

Remplacer tous les caractères Unicode par des équivalents ASCII:

.. code-block:: powershell

   # ❌ Avant (avec emojis)
   Write-Host "✅ Services démarrés avec succès!" -ForegroundColor Green
   Write-Host "❌ Erreur lors du démarrage" -ForegroundColor Red
   
   # ✅ Après (ASCII uniquement)
   Write-Host "[OK] Services demarres avec succes!" -ForegroundColor Green
   Write-Host "[ERREUR] Erreur lors du demarrage" -ForegroundColor Red

**Recommandations:**

1. Utiliser des préfixes entre crochets: ``[OK]``, ``[ERREUR]``, ``[ATTENTION]``
2. Éviter les accents dans le code (OK dans les commentaires)
3. Utiliser ``-ForegroundColor`` pour la couleur au lieu d'emojis
4. Tester les scripts avec ``Get-Content -Encoding`` pour vérifier l'encodage

**Fichiers concernés:**

* ``tests/TEST_SCRIPTS.ps1``
* ``tests/manage.ps1``

---

🔧 Problème #2: Notebooks et Connexion MLflow
----------------------------------------------

**Contexte**

Exécution du notebook ``train_model.ipynb`` sur Windows host avec Docker Compose actif.

**Erreur rencontrée:**

.. code-block:: python

   requests.exceptions.ConnectionError: 
   HTTPConnectionPool(host='mlflow', port=5000): 
   Max retries exceeded

**Cause**

Le notebook s'exécute sur le **host Windows** (pas dans Docker) et essaie de se connecter
à ``http://mlflow:5000``. Le hostname ``mlflow`` n'existe que dans le réseau Docker interne.

**Solution implémentée:**

Détection automatique de l'environnement dans le notebook:

.. code-block:: python

   import os
   import pathlib
   from dotenv import load_dotenv
   
   # Charger .env.local avec override
   env_local_path = pathlib.Path("../.env.local").resolve()
   load_dotenv(env_local_path, override=True)
   
   # Récupérer les variables
   MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
   MLFLOW_S3_ENDPOINT_URL = os.getenv("MLFLOW_S3_ENDPOINT_URL")
   
   # Conversion automatique Docker → Localhost
   if "mlflow:" in MLFLOW_TRACKING_URI:
       MLFLOW_TRACKING_URI = MLFLOW_TRACKING_URI.replace(
           "http://mlflow:", 
           "http://localhost:"
       )
   
   if "minio:" in MLFLOW_S3_ENDPOINT_URL:
       MLFLOW_S3_ENDPOINT_URL = MLFLOW_S3_ENDPOINT_URL.replace(
           "http://minio:", 
           "http://localhost:"
       )
   
   print(f"MLflow URI: {MLFLOW_TRACKING_URI}")
   print(f"MinIO URL: {MLFLOW_S3_ENDPOINT_URL}")

**Fichier de configuration recommandé:**

Créer ``.env.local`` à la racine:

.. code-block:: bash

   # .env.local (pour notebooks sur host)
   MLFLOW_TRACKING_URI=http://localhost:5000
   MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
   AWS_ACCESS_KEY_ID=minioadmin
   AWS_SECRET_ACCESS_KEY=minioadmin

**Fichiers concernés:**

* ``notebooks/train_model.ipynb`` (Cell 4)

---

🔧 Problème #3: Chemins Relatifs dans Notebooks
------------------------------------------------

**Contexte**

Chargement du fichier ``iris_test.csv`` depuis le notebook.

**Erreur rencontrée:**

.. code-block:: python

   FileNotFoundError: [Errno 2] No such file or directory: 
   '../../data/iris_test.csv'

**Cause**

Le notebook s'exécute dans ``notebooks/`` et le chemin relatif ``../../data/`` 
remonte trop haut dans l'arborescence.

**Structure réelle:**

.. code-block:: text

   projet/
   ├── data/
   │   └── iris_test.csv
   └── notebooks/
       └── train_model.ipynb

**Solution:**

Correction du chemin relatif:

.. code-block:: python

   # ❌ Avant (remonte de 2 niveaux)
   test_data = pd.read_csv("../../data/iris_test.csv")
   
   # ✅ Après (remonte de 1 niveau)
   test_data = pd.read_csv("../data/iris_test.csv")

**Méthode robuste avec pathlib:**

.. code-block:: python

   from pathlib import Path
   
   # Obtenir le répertoire racine du projet
   PROJECT_ROOT = Path(__file__).parent.parent
   
   # Construire le chemin absolu
   data_path = PROJECT_ROOT / "data" / "iris_test.csv"
   test_data = pd.read_csv(data_path)

**Fichiers concernés:**

* ``notebooks/train_model.ipynb`` (Cell 12)

---

🔧 Problème #4: Credentials MinIO Incorrects
---------------------------------------------

**Contexte**

Documentation indiquait des credentials MinIO différents de la configuration réelle.

**Erreur rencontrée:**

.. code-block:: text

   S3 Access Denied (403)
   The Access Key Id you provided does not exist in our records.

**Cause**

Documentation ``README.md`` mentionnait:

.. code-block:: text

   Credentials: admin / admin123

Mais le fichier ``.env`` contenait:

.. code-block:: bash

   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=minioadmin

**Solution:**

Mis à jour de la documentation pour correspondre à la configuration réelle.

**Dans README.md:**

.. code-block:: markdown

   | Service | URL | Credentials |
   |---------|-----|-------------|
   | **MinIO** | http://localhost:9001 | minioadmin / minioadmin |

**Recommandations:**

1. Toujours utiliser les credentials par défaut de MinIO: ``minioadmin / minioadmin``
2. Centraliser la configuration dans ``.env``
3. Synchroniser la doc avec le code
4. Ne jamais commiter ``.env`` avec de vrais secrets

**Fichiers concernés:**

* ``README.md``
* ``.env`` (exemple)

---

🔧 Problème #5: Hot-Reloading Non Détecté
------------------------------------------

**Contexte**

Après avoir changé l'alias "Production" sur MLflow UI, l'API continue 
d'utiliser l'ancienne version du modèle.

**Symptômes:**

* Version affichée dans Streamlit ne change pas
* ``/model-info`` retourne toujours l'ancienne version
* Logs API ne montrent pas de rechargement

**Causes possibles:**

1. **Polling désactivé:**

   .. code-block:: python

      # src/api/main.py
      # Si CHECK_INTERVAL est trop grand ou infini
      CHECK_INTERVAL = 999999  # ❌ Trop long

2. **Cache Streamlit non rafraîchi:**

   Le cache TTL par défaut est de 60 secondes

3. **Alias non modifié correctement:**

   Vérifier sur MLflow UI que l'alias "Production" pointe bien vers la nouvelle version

**Solutions:**

1. **Vérifier le polling interval:**

   .. code-block:: python

      # src/api/main.py
      CHECK_INTERVAL = 5  # ✅ Vérification toutes les 5 secondes

2. **Forcer le rechargement dans Streamlit:**

   .. code-block:: python

      # src/front/app.py
      @st.cache_data(ttl=5)  # ✅ Cache de 5 secondes
      def get_model_info():
          ...

3. **Vérifier les logs API:**

   .. code-block:: bash

      docker-compose logs api | grep -i "model"
      
      # Sortie attendue:
      # Model reloaded: version changed from 1 to 2

4. **Test manuel:**

   .. code-block:: bash

      # Obtenir la version actuelle
      curl http://localhost:8000/model-info
      
      # Changer l'alias sur MLflow UI
      
      # Attendre 5-10 secondes
      sleep 10
      
      # Vérifier la nouvelle version
      curl http://localhost:8000/model-info

**Fichiers concernés:**

* ``src/api/main.py`` (fonction ``_reload_model_if_needed``)
* ``src/front/app.py`` (cache Streamlit)

---

🔧 Problème #6: Tests Automatisés Échouent
-------------------------------------------

**Contexte**

Exécution du script ``tests/TEST_SCRIPTS.ps1`` pour valider les 4 critères.

**Erreur #1: API non accessible**

.. code-block:: powershell

   [ERREUR] Impossible de contacter l'API
   Verifier que Docker est demarre: docker-compose ps

**Solution:**

.. code-block:: powershell

   # Vérifier que tous les services sont UP
   docker-compose ps
   
   # Attendre que l'API soit prête (health check)
   Start-Sleep -Seconds 10
   
   # Relancer le script
   .\tests\TEST_SCRIPTS.ps1

**Erreur #2: Volumes non détectés**

.. code-block:: powershell

   [ATTENTION] Nombre de volumes insuffisant: 0/2

**Cause:**

Les volumes ne contiennent pas le nom du projet dans leur nom.

**Solution:**

Vérifier que ``docker-compose.yml`` définit bien les volumes nommés:

.. code-block:: yaml

   volumes:
     mlflow_data:
       name: projet_2_1_mlfactory_mlflow_data
     minio_data:
       name: projet_2_1_mlfactory_minio_data

**Erreur #3: Dépendances non trouvées**

.. code-block:: powershell

   docker exec api pip list | Select-String "fastapi"
   # Aucun résultat

**Cause:**

Le conteneur n'est pas encore prêt ou les dépendances ne sont pas installées.

**Solution:**

.. code-block:: bash

   # Reconstruire les images
   docker-compose build --no-cache api
   
   # Redémarrer
   docker-compose up -d api
   
   # Vérifier les logs d'installation
   docker-compose logs api | grep "pip install"

**Fichiers concernés:**

* ``tests/TEST_SCRIPTS.ps1``
* ``docker-compose.yml``

---

🔧 Problème #7: Documentation Sphinx Non Buildable
---------------------------------------------------

**Contexte**

Tentative de génération de la documentation HTML avec Sphinx.

**Erreur rencontrée:**

.. code-block:: bash

   sphinx-build: command not found

**Cause**

Dépendances de documentation non installées.

**Solution:**

.. code-block:: bash

   # Avec UV (recommandé)
   uv pip install -e ".[docs]"
   
   # Ou avec pip
   pip install -e ".[docs]"
   
   # Vérifier l'installation
   sphinx-build --version
   
   # Builder la documentation
   cd docs
   make html  # Linux/Mac
   .\make.bat html  # Windows

**Erreur #2: "No module named 'train'"**

.. code-block:: bash

   WARNING: autodoc: failed to import module 'train'

**Cause:**

Le package n'est pas installé en mode éditable.

**Solution:**

.. code-block:: bash

   # Installer le projet
   pip install -e .
   
   # Vérifier
   python -c "import train; print(train.__file__)"

**Fichiers concernés:**

* ``pyproject.toml`` (dépendances ``[docs]``)
* ``docs/conf.py``

---

📝 Leçons Apprises
==================

1. **Encodage et Scripts**
   
   * Toujours tester les scripts PowerShell avant de commiter
   * Préférer ASCII pour la compatibilité Windows/PowerShell 5.1
   * Utiliser ``-ForegroundColor`` pour les couleurs

2. **Notebooks et Docker**
   
   * Les notebooks s'exécutent sur le host, pas dans Docker
   * Toujours prévoir une conversion ``mlflow:5000`` → ``localhost:5000``
   * Créer un fichier ``.env.local`` séparé pour les notebooks

3. **Chemins Relatifs**
   
   * Utiliser ``pathlib.Path`` pour des chemins robustes
   * Toujours tester depuis le répertoire d'exécution réel
   * Documenter l'arborescence attendue

4. **Configuration Centralisée**
   
   * Un seul fichier ``.env`` pour toute la config
   * Synchroniser README.md avec ``.env.example``
   * Ne jamais hardcoder les credentials

5. **Hot-Reloading**
   
   * Ajouter des logs explicites (``Model reloaded: v1 → v2``)
   * Exposer ``/model-info`` pour debugging
   * Configurer un polling interval court (5s) en dev

6. **Tests Automatisés**
   
   * Attendre que les services soient prêts (health checks)
   * Valider chaque critère séparément
   * Fournir des messages d'erreur clairs avec solutions

7. **Documentation**
   
   * Installer toutes les dépendances optionnelles (``[docs]``)
   * Tester le build de la doc avant de commiter
   * Maintenir troubleshooting.rst à jour avec les problèmes réels

---

🆘 Besoin d'Aide?
=================

Si vous rencontrez un problème non documenté ici:

1. **Rechercher dans la documentation complète:**

   * :doc:`installation`
   * :doc:`quickstart`
   * :doc:`/dev-guide/architecture`

2. **Consulter les logs:**

   .. code-block:: bash

      docker-compose logs > diagnostic.txt

3. **Ouvrir une issue GitHub** avec:

   * Description du problème
   * Étapes pour reproduire
   * Logs pertinents
   * Configuration (.env anonymisé)

**Repository:** https://github.com/Roxiina/Projet_2_1_MLFactory
* `MLflow Documentation <https://mlflow.org/docs/latest/index.html>`_
