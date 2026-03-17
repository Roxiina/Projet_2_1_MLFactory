Guide d'Entraînement Personnalisé
==================================

Ce guide explique comment personnaliser l'entraînement des modèles dans ML Factory.

🎯 Vue d'Ensemble
-----------------

Le script ``src/train/train.py`` permet d'entraîner des modèles de classification sur le dataset Iris avec:

* Deux algorithmes supportés (Logistic Regression, Random Forest)
* Logging automatique dans MLflow
* Promotion automatique ou manuelle vers Production
* Métriques complètes et visualisations

📁 Structure du Script
----------------------

.. code-block:: python

   # src/train/train.py
   
   # 1. Configuration
   AUTO_PROMOTE = True  # Mode automatique/manuel
   MODEL_NAME = "iris_classifier"
   MODEL_ALIAS = "Production"
   
   # 2. Fonctions principales
   def load_data() -> tuple:
       """Charge le dataset Iris et crée le fichier de test."""
       ...
   
   def train_model(model_type: str) -> tuple:
       """Entraîne un modèle et l'enregistre dans MLflow."""
       ...
   
   # 3. Point d'entrée
   if __name__ == "__main__":
       ...

⚙️ Modes d'Entraînement
-----------------------

Mode Automatique
~~~~~~~~~~~~~~~~

**Configuration:**

.. code-block:: python

   AUTO_PROMOTE = True

**Comportement:**

* Entraîne le modèle
* L'enregistre dans MLflow avec un nouveau numéro de version
* **Assigne automatiquement** l'alias "Production" à la nouvelle version
* L'API détecte et charge le nouveau modèle immédiatement

**Use Case:**

* Développement et prototypage rapide
* CI/CD avec tests automatiques de validation

**Commande:**

.. code-block:: bash

   cd src/train
   python train.py

Mode Manuel
~~~~~~~~~~~

**Configuration:**

.. code-block:: python

   AUTO_PROMOTE = False

**Comportement:**

* Entraîne le modèle
* L'enregistre dans MLflow avec un nouveau numéro de version
* **N'assigne PAS d'alias** automatiquement
* Nécessite une promotion manuelle sur MLflow UI

**Use Case:**

* Production avec validation humaine
* Tests A/B entre plusieurs versions
* Rollback contrôlé

**Workflow:**

1. Entraîner:

   .. code-block:: bash

      cd src/train
      python train.py

2. Vérifier sur MLflow UI (http://localhost:5000)

3. Promouvoir manuellement:

   * Models → iris_classifier → Version X
   * Set alias → "Production"

🤖 Algorithmes Supportés
-------------------------

1. Logistic Regression
~~~~~~~~~~~~~~~~~~~~~~~

**Code:**

.. code-block:: python

   from sklearn.linear_model import LogisticRegression
   
   model = LogisticRegression(max_iter=200, random_state=42)

**Caractéristiques:**

* **Complexité:** Faible
* **Vitesse:** Rapide (~1 seconde)
* **Accuracy:** ~96% sur Iris
* **Taille:** Petit modèle (~10 KB)

**Use Case:**

* Baseline rapide
* Production avec faibles ressources
* Interprétabilité importante

2. Random Forest
~~~~~~~~~~~~~~~~

**Code:**

.. code-block:: python

   from sklearn.ensemble import RandomForestClassifier
   
   model = RandomForestClassifier(n_estimators=100, random_state=42)

**Caractéristiques:**

* **Complexité:** Élevée
* **Vitesse:** Plus lent (~5 secondes)
* **Accuracy:** ~97-98% sur Iris
* **Taille:** Modèle plus grand (~100 KB)

**Use Case:**

* Meilleure performance
* Moins sensible au surapprentissage
* Extraction d'importance des features

🔧 Personnalisation des Modèles
-------------------------------

Ajouter un Nouvel Algorithme
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Exemple: Support Vector Machine (SVM)**

1. **Modifier** ``train_model()`` dans ``src/train/train.py``:

.. code-block:: python

   from sklearn.svm import SVC
   
   def train_model(model_type: str = "logistic_regression") -> tuple:
       """Entraîne un modèle de classification sur le dataset Iris.
       
       Args:
           model_type: Type de modèle à entraîner
               - "logistic_regression"
               - "random_forest"
               - "svm"  # ✅ Nouveau!
       """
       X_train, X_test, y_train, y_test = load_data()
       
       # Sélection du modèle
       if model_type == "logistic_regression":
           model = LogisticRegression(max_iter=200, random_state=42)
       elif model_type == "random_forest":
           model = RandomForestClassifier(n_estimators=100, random_state=42)
       elif model_type == "svm":  # ✅ Nouveau!
           model = SVC(kernel='rbf', probability=True, random_state=42)
       else:
           raise ValueError(f"Model type '{model_type}' non supporté")
       
       # ... rest of the function

2. **Utiliser:**

.. code-block:: python

   # Dans le if __name__ == "__main__":
   version, acc = train_model("svm")

Modifier les Hyperparamètres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Exemple: Tuning du Random Forest**

.. code-block:: python

   from sklearn.model_selection import GridSearchCV
   
   def train_model_with_tuning(model_type: str = "random_forest"):
       """Entraîne avec Grid Search pour optimiser les hyperparamètres."""
       X_train, X_test, y_train, y_test = load_data()
       
       if model_type == "random_forest":
           # Grid de paramètres
           param_grid = {
               'n_estimators': [50, 100, 200],
               'max_depth': [10, 20, None],
               'min_samples_split': [2, 5, 10]
           }
           
           base_model = RandomForestClassifier(random_state=42)
           grid_search = GridSearchCV(
               base_model,
               param_grid,
               cv=5,
               scoring='accuracy',
               n_jobs=-1
           )
           
           # Entraînement
           with mlflow.start_run(run_name=f"{model_type}_tuning"):
               grid_search.fit(X_train, y_train)
               
               # Best model
               model = grid_search.best_estimator_
               
               # Log best params
               mlflow.log_params(grid_search.best_params_)
               
               # ... rest of the training

📊 Métriques Personnalisées
---------------------------

Ajouter des Métriques
~~~~~~~~~~~~~~~~~~~~~

**Exemple: Précision, Rappel, AUC-ROC**

.. code-block:: python

   from sklearn.metrics import precision_score, recall_score, roc_auc_score
   
   # Dans train_model(), après la prédiction:
   
   # Métriques existantes
   accuracy = accuracy_score(y_test, y_pred)
   f1 = f1_score(y_test, y_pred, average='weighted')
   
   # Nouvelles métriques
   precision = precision_score(y_test, y_pred, average='weighted')
   recall = recall_score(y_test, y_pred, average='weighted')
   
   # AUC-ROC (multi-class)
   y_proba = model.predict_proba(X_test)
   auc_roc = roc_auc_score(
       y_test,
       y_proba,
       multi_class='ovr',
       average='weighted'
   )
   
   # Logging dans MLflow
   mlflow.log_metric("accuracy", accuracy)
   mlflow.log_metric("f1_score", f1)
   mlflow.log_metric("precision", precision)  # ✅
   mlflow.log_metric("recall", recall)        # ✅
   mlflow.log_metric("auc_roc", auc_roc)      # ✅

Visualisations Personnalisées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Exemple: Courbe ROC**

.. code-block:: python

   from sklearn.metrics import RocCurveDisplay
   import matplotlib.pyplot as plt
   
   # Dans train_model():
   
   # ROC curve pour chaque classe
   fig, ax = plt.subplots(1, 1, figsize=(10, 6))
   
   for i in range(len(iris.target_names)):
       y_test_binary = (y_test == i).astype(int)
       y_proba_class = y_proba[:, i]
       
       RocCurveDisplay.from_predictions(
           y_test_binary,
           y_proba_class,
           ax=ax,
           name=f"Class {iris.target_names[i]}"
       )
   
   ax.set_title("ROC Curves - Multiclass")
   plt.tight_layout()
   
   # Sauvegarder et logger
   plt.savefig("roc_curve.png")
   mlflow.log_artifact("roc_curve.png")
   plt.close()

🗃️ Travailler avec d'Autres Datasets
-------------------------------------

Remplacer Iris par un Custom Dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Étape 1: Modifier** ``load_data()``

.. code-block:: python

   import pandas as pd
   
   def load_data() -> tuple:
       """Charge un dataset custom depuis un CSV."""
       # Charger le dataset
       df = pd.read_csv("data/my_custom_dataset.csv")
       
       # Séparer features et target
       X = df.drop('target', axis=1).values
       y = df['target'].values
       
       # Split train/test
       X_train, X_test, y_train, y_test = train_test_split(
           X, y,
           test_size=0.2,
           random_state=42,
           stratify=y
       )
       
       # Créer fichier de test (optionnel)
       test_df = pd.DataFrame(X_test)
       test_df['target'] = y_test
       test_df.to_csv("data/my_test.csv", index=False)
       
       return X_train, X_test, y_train, y_test

**Étape 2: Adapter les classes**

.. code-block:: python

   # Dans train_model():
   
   # Si classes non ordonnées (ex: ["dog", "cat", "bird"])
   from sklearn.preprocessing import LabelEncoder
   
   label_encoder = LabelEncoder()
   y_train_encoded = label_encoder.fit_transform(y_train)
   y_test_encoded = label_encoder.transform(y_test)
   
   # Entraîner avec les labels encodés
   model.fit(X_train, y_train_encoded)
   y_pred = model.predict(X_test)
   
   # Sauvegarder le label encoder avec le modèle
   mlflow.sklearn.log_model(
       sk_model=model,
       artifact_path="model",
       registered_model_name=MODEL_NAME,
       metadata={"label_encoder": label_encoder.classes_.tolist()}
   )

Augmentation de Données
~~~~~~~~~~~~~~~~~~~~~~~~

**Exemple: SMOTE pour rééquilibrer les classes**

.. code-block:: python

   from imblearn.over_sampling import SMOTE
   
   def load_data_with_augmentation() -> tuple:
       """Charge les données et applique SMOTE."""
       X_train, X_test, y_train, y_test = load_data()
       
       # Appliquer SMOTE
       smote = SMOTE(random_state=42)
       X_train_resampled, y_train_resampled = smote.fit_resample(
           X_train, y_train
       )
       
       print(f"Avant SMOTE: {len(X_train)} samples")
       print(f"Après SMOTE: {len(X_train_resampled)} samples")
       
       return X_train_resampled, X_test, y_train_resampled, y_test

🔁 Pipeline de Préprocessing
----------------------------

Ajouter un Pipeline Scikit-learn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from sklearn.pipeline import Pipeline
   from sklearn.preprocessing import StandardScaler
   from sklearn.decomposition import PCA
   
   def train_model_with_pipeline(model_type: str = "logistic_regression"):
       """Entraîne avec un pipeline de preprocessing."""
       X_train, X_test, y_train, y_test = load_data()
       
       # Construire le pipeline
       if model_type == "logistic_regression":
           base_estimator = LogisticRegression(max_iter=200, random_state=42)
       elif model_type == "random_forest":
           base_estimator = RandomForestClassifier(n_estimators=100, random_state=42)
       
       pipeline = Pipeline([
           ('scaler', StandardScaler()),      # Normalisation
           ('pca', PCA(n_components=3)),      # Réduction de dimension
           ('classifier', base_estimator)      # Modèle
       ])
       
       # Entraîner le pipeline complet
       with mlflow.start_run(run_name=f"{model_type}_pipeline"):
           pipeline.fit(X_train, y_train)
           
           # Prédictions
           y_pred = pipeline.predict(X_test)
           accuracy = accuracy_score(y_test, y_pred)
           
           # Logging
           mlflow.log_param("model_type", model_type)
           mlflow.log_param("preprocessing", "StandardScaler + PCA")
           mlflow.log_metric("accuracy", accuracy)
           
           # Enregistrer le pipeline complet
           mlflow.sklearn.log_model(
               sk_model=pipeline,
               artifact_path="model",
               registered_model_name=MODEL_NAME
           )

📦 Versioning et Gestion des Datasets
--------------------------------------

Versionner les Datasets avec DVC
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Installation:**

.. code-block:: bash

   uv pip install dvc dvc-s3

**Configuration:**

.. code-block:: bash

   # Initialiser DVC
   dvc init
   
   # Configurer le remote (MinIO)
   dvc remote add -d minio s3://datasets
   dvc remote modify minio endpointurl http://localhost:9000
   dvc remote modify minio access_key_id minioadmin
   dvc remote modify minio secret_access_key minioadmin
   
   # Tracker le dataset
   dvc add data/my_dataset.csv
   
   # Commit
   git add data/my_dataset.csv.dvc .dvc/config
   git commit -m "Track dataset with DVC"
   
   # Push vers MinIO
   dvc push

**Utilisation dans le script:**

.. code-block:: python

   import subprocess
   
   def load_data():
       """Charge le dataset après un DVC pull."""
       # Pull la dernière version du dataset
       subprocess.run(["dvc", "pull"], check=True)
       
       # Charger le dataset
       df = pd.read_csv("data/my_dataset.csv")
       ...

🧪 Tests et Validation
----------------------

Test de Régression de Performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_model_performance():
       """Vérifie que le nouveau modèle n'est pas moins performant."""
       # Charger le modèle Production actuel
       current_model_uri = f"models:/{MODEL_NAME}@Production"
       current_model = mlflow.pyfunc.load_model(current_model_uri)
       
       # Charger les données de test
       X_train, X_test, y_train, y_test = load_data()
       
       # Performance actuelle
       current_pred = current_model.predict(X_test)
       current_accuracy = accuracy_score(y_test, current_pred)
       
       # Entraîner le nouveau modèle
       version, new_accuracy = train_model("random_forest")
       
       # Vérification
       print(f"Current model accuracy: {current_accuracy:.4f}")
       print(f"New model accuracy: {new_accuracy:.4f}")
       
       if new_accuracy >= current_accuracy:
           print("✅ Le nouveau modèle est au moins aussi bon!")
           return True
       else:
           print("❌ Le nouveau modèle est moins performant!")
           return False
   
   # Dans le if __name__ == "__main__":
   if test_model_performance():
       # Promouvoir automatiquement
       pass

Cross-Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from sklearn.model_selection import cross_val_score
   
   def train_with_cv(model_type: str = "logistic_regression"):
       """Entraîne avec validation croisée."""
       X_train, X_test, y_train, y_test = load_data()
       
       if model_type == "logistic_regression":
           model = LogisticRegression(max_iter=200, random_state=42)
       elif model_type == "random_forest":
           model = RandomForestClassifier(n_estimators=100, random_state=42)
       
       # Cross-validation (5-fold)
       cv_scores = cross_val_score(
           model,
           X_train,
           y_train,
           cv=5,
           scoring='accuracy'
       )
       
       print(f"CV Scores: {cv_scores}")
       print(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
       
       # Entraîner sur tout le train set
       with mlflow.start_run(run_name=f"{model_type}_cv"):
           model.fit(X_train, y_train)
           
           # Log CV metrics
           mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
           mlflow.log_metric("cv_std_accuracy", cv_scores.std())
           
           # ... rest of training

🔄 Automatisation
-----------------

Script d'Entraînement Planifié
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cron Job (Linux):**

.. code-block:: bash

   # Entraîner tous les jours à 2h du matin
   0 2 * * * cd /path/to/ml-factory/src/train && python train.py >> /var/log/ml-factory-train.log 2>&1

**GitHub Actions (CI/CD):**

.. code-block:: yaml

   # .github/workflows/train.yml
   name: Train Model
   
   on:
     schedule:
       - cron: '0 2 * * *'  # Tous les jours à 2h
     workflow_dispatch:      # Déclenchement manuel
   
   jobs:
     train:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       
       - name: Setup Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Install Dependencies
         run: |
           pip install uv
           uv pip install -e .
       
       - name: Train Model
         env:
           MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
         run: |
           cd src/train
           python train.py

Réentraînement Conditionnel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import datetime
   
   def should_retrain() -> bool:
       """Détermine si un réentraînement est nécessaire."""
       client = mlflow.MlflowClient(MLFLOW_TRACKING_URI)
       
       try:
           # Récupérer la version Production
           prod_version = client.get_model_version_by_alias(
               name=MODEL_NAME,
               alias=MODEL_ALIAS
           )
           
           # Vérifier la date de création
           created_timestamp = int(prod_version.creation_timestamp) / 1000
           created_date = datetime.datetime.fromtimestamp(created_timestamp)
           days_old = (datetime.datetime.now() - created_date).days
           
           print(f"Le modèle Production a {days_old} jours")
           
           # Réentraîner si > 7 jours
           return days_old > 7
       
       except Exception:
           # Pas de modèle Production, entraîner
           return True
   
   if __name__ == "__main__":
       if should_retrain():
           print("🚀 Réentraînement nécessaire!")
           version, acc = train_model("random_forest")
       else:
           print("✅ Le modèle est encore récent, pas de réentraînement")

📚 Ressources
-------------

* :doc:`/api/training` - Référence de l'API
* :doc:`architecture` - Architecture détaillée
* `Scikit-learn Documentation <https://scikit-learn.org/stable/>`_
* `MLflow Documentation <https://mlflow.org/docs/latest/index.html>`_

🆘 Support
----------

Pour des questions sur l'entraînement:

* 📖 Consultez la :doc:`/user-guide/troubleshooting`
* 🐛 `GitHub Issues <https://github.com/simplon-france/ml-factory/issues>`_
* 💬 Support Simplon France
