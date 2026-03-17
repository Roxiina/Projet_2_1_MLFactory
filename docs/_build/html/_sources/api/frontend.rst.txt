Frontend Streamlit
==================

Module: ``front.app``
---------------------

Ce module implémente l'interface utilisateur Streamlit pour tester les modèles de classification.

Fonctions Principales
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: front.app.get_model_info

.. autofunction:: front.app.get_api_health

.. autofunction:: front.app.predict

Interface Utilisateur
~~~~~~~~~~~~~~~~~~~~~

L'application Streamlit est organisée en plusieurs sections:

En-tête
^^^^^^^

- Titre principal "ML Factory"
- Badge de statut de connexion API
- Affichage des métriques du modèle (nom, version, alias)
- Badge de version en production (mis à jour dynamiquement)

Onglet "Saisie Manuelle"
^^^^^^^^^^^^^^^^^^^^^^^^^

Permet de saisir les features via des sliders:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Feature
     - Plage
     - Défaut
   * - Longueur du Sépale
     - 4.0 - 8.0 cm
     - 5.1 cm
   * - Largeur du Sépale
     - 2.0 - 4.5 cm
     - 3.5 cm
   * - Longueur du Pétale
     - 1.0 - 7.0 cm
     - 1.4 cm
   * - Largeur du Pétale
     - 0.1 - 2.5 cm
     - 0.2 cm

Onglet "Charger depuis fichier"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Permet de charger un fichier CSV contenant des données de test:

1. Upload du fichier CSV
2. Affichage des premières lignes
3. Sélection d'une ligne spécifique
4. Affichage des features
5. Bouton de prédiction
6. Comparaison avec la vraie classe (si disponible)

Affichage des Résultats
~~~~~~~~~~~~~~~~~~~~~~~~

Après une prédiction, l'interface affiche:

**Prédiction Principale**
   - Classe prédite en grand (ex: "Setosa")
   - Version du modèle utilisé
   - Badge coloré pour la classe

**Probabilités**
   - Graphique en barres des probabilités
   - Tableau détaillé avec pourcentages
   - Mise en évidence de la classe la plus probable

**Validation (mode fichier)**
   - Vraie classe si disponible dans le CSV
   - Indicateur de succès/échec
   - Badge de comparaison

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
   * - ``API_URL``
     - URL de l'API FastAPI
     - ``http://api:8000``
   * - ``MLFLOW_TRACKING_URI``
     - URI du serveur MLflow
     - ``http://mlflow:5000``

Cache Streamlit
^^^^^^^^^^^^^^^

La fonction ``get_model_info()`` utilise le cache Streamlit avec un TTL de 5 secondes:

.. code-block:: python

   @st.cache_data(ttl=5)
   def get_model_info():
       ...

**Avantages:**

- Réduit la charge sur l'API
- Détection rapide des changements de version (5 sec max)
- Améliore la réactivité de l'interface

Classes Iris
~~~~~~~~~~~~

Les trois classes de fleurs Iris sont :

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Code
     - Nom
   * - 0
     - **Setosa** - Petites dimensions, facile à classifier
   * - 1
     - **Versicolor** - Dimensions moyennes
   * - 2
     - **Virginica** - Grandes dimensions

Style et Thème
~~~~~~~~~~~~~~

L'interface utilise un CSS personnalisé pour:

- Mise en page responsive
- Badges de version colorés
- Cards pour les métriques
- Animations et transitions
- Thème cohérent avec le branding ML Factory

Exemples d'Utilisation
~~~~~~~~~~~~~~~~~~~~~~

Démarrage Local
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Installation
   cd src/front
   pip install -r requirements.txt

   # Lancement
   streamlit run app.py

Avec Docker
^^^^^^^^^^^

.. code-block:: bash

   # Build
   docker build -t ml-factory-front ./src/front

   # Run
   docker run -p 8501:8501 \
              -e API_URL=http://localhost:8000 \
              ml-factory-front

Configuration Personnalisée
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Avec port personnalisé
   streamlit run app.py --server.port 8502

   # Avec URL API différente
   API_URL=http://production-api:8000 streamlit run app.py

Workflow Utilisateur
~~~~~~~~~~~~~~~~~~~~

Scénario 1: Test Rapide
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   1. Ouvrir http://localhost:8501
      ↓
   2. Vérifier le badge de version
      ↓
   3. Ajuster les sliders (onglet "Saisie Manuelle")
      ↓
   4. Cliquer sur "🎯 Prédire"
      ↓
   5. Voir la prédiction et les probabilités

Scénario 2: Test Batch
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   1. Aller sur l'onglet "Charger depuis fichier"
      ↓
   2. Uploader data/iris_test.csv
      ↓
   3. Sélectionner une ligne dans le dropdown
      ↓
   4. Cliquer sur "🎯 Prédire cette ligne"
      ↓
   5. Comparer avec la vraie classe

Scénario 3: Validation Zero-Downtime
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   1. Noter la version affichée (ex: v1)
      ↓
   2. Entraîner un nouveau modèle (autre terminal)
      ↓
   3. Promouvoir sur MLflow UI
      ↓
   4. Cliquer sur "🔄 Rafraîchir" dans Streamlit
      ↓
   5. Observer le changement instantané (v1 → v2)
      ↓
   6. Tester une prédiction avec le nouveau modèle

Gestion des Erreurs
~~~~~~~~~~~~~~~~~~~

Connexion API Échouée
^^^^^^^^^^^^^^^^^^^^^

Si l'API n'est pas accessible:

.. code-block:: python

   ❌ Impossible de se connecter à l'API.
   Vérifiez que les services sont démarrés.

**Solutions:**

1. Vérifier que l'API est démarrée: ``docker-compose ps api``
2. Tester l'API directement: ``curl http://localhost:8000/health``
3. Vérifier la configuration réseau Docker

Fichier CSV Invalide
^^^^^^^^^^^^^^^^^^^^^

Si le fichier uploadé ne contient pas les bonnes colonnes:

.. code-block:: python

   ❌ Le fichier doit contenir les colonnes: 
   sepal length (cm), sepal width (cm), 
   petal length (cm), petal width (cm)

**Solution:** Utiliser le fichier d'exemple ``data/iris_test.csv`` comme template.

Timeout API
^^^^^^^^^^^

Si l'API met trop de temps à répondre:

.. code-block:: python

   ⚠️ Erreur de connexion à l'API: timeout

**Solutions:**

1. Vérifier que MLflow et MinIO sont opérationnels
2. Augmenter le timeout dans le code (actuellement 5s pour /model-info, 10s pour /predict)

Personnalisation
~~~~~~~~~~~~~~~~

Modifier le Theme
^^^^^^^^^^^^^^^^^

Créer un fichier ``.streamlit/config.toml``:

.. code-block:: toml

   [theme]
   primaryColor = "#1f77b4"
   backgroundColor = "#ffffff"
   secondaryBackgroundColor = "#f0f2f6"
   textColor = "#262730"
   font = "sans serif"

Ajouter des Features
^^^^^^^^^^^^^^^^^^^^

Pour ajouter une nouvelle fonctionnalité:

.. code-block:: python

   # Exemple: Export des prédictions en CSV
   
   import pandas as pd
   
   # Après une prédiction
   results_df = pd.DataFrame({
       'features': [features],
       'prediction': [result['prediction']],
       'label': [result['prediction_label']]
   })
   
   csv = results_df.to_csv(index=False)
   st.download_button(
       label="📥 Télécharger les résultats",
       data=csv,
       file_name="predictions.csv",
       mime="text/csv"
   )

Monitoring
~~~~~~~~~~

Métriques Streamlit
^^^^^^^^^^^^^^^^^^^

Streamlit expose des métriques de performance:

- Temps de chargement des pages
- Nombre de reruns
- Cache hits/misses

.. code-block:: bash

   # Voir les métriques dans les logs
   docker-compose logs front

Logs Utilisateur
^^^^^^^^^^^^^^^^

Pour tracker les actions utilisateur:

.. code-block:: python

   import logging
   
   logger = logging.getLogger(__name__)
   
   # Dans la fonction predict()
   logger.info(f"Prédiction demandée: {features}")
   logger.info(f"Résultat: {result['prediction_label']}")

Bonnes Pratiques
~~~~~~~~~~~~~~~~

1. **Cache Intelligent**
   
   Utiliser le cache Streamlit pour les données qui changent rarement.

2. **Feedback Utilisateur**
   
   Toujours afficher des spinners et messages de statut.

3. **Validation des Entrées**
   
   Utiliser les sliders avec des plages appropriées pour éviter les erreurs.

4. **Responsive Design**
   
   Tester l'interface sur différentes tailles d'écran.

5. **Accessibilité**
   
   Utiliser des couleurs contrastées et des labels clairs.

6. **Documentation Inline**
   
   Ajouter des tooltips et des messages d'aide pour guider l'utilisateur.
