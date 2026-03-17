"""Script d'entraînement pour le projet ML Factory.

Ce module gère l'entraînement et l'enregistrement des modèles de classification Iris
dans MLflow avec support de promotion automatique ou manuelle en production.

Le script supporte deux modes de déploiement:
    - **Automatique**: Le modèle est automatiquement promu en Production après l'entraînement
    - **Manuel**: Le modèle est enregistré mais nécessite une promotion manuelle via l'UI MLflow

Examples:
    Entraînement avec promotion automatique::

        $ python train.py

    Pour le mode manuel, modifier AUTO_PROMOTE=False dans le script avant l'exécution.

Attributes:
    MLFLOW_TRACKING_URI (str): URI du serveur MLflow pour le tracking
    MODEL_NAME (str): Nom du modèle enregistré dans le registre MLflow
    AUTO_PROMOTE (bool): Active/désactive la promotion automatique en Production

Note:
    Ce script doit être exécuté en dehors de Docker avec les dépendances installées localement.
"""

import os
from dotenv import load_dotenv
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import pandas as pd

# Charger les variables d'environnement
# Priorité: .env.local (pour dev local) > .env (pour Docker)
import pathlib
script_dir = pathlib.Path(__file__).parent.parent.parent
env_local_path = script_dir / ".env.local"
if env_local_path.exists():
    load_dotenv(env_local_path)
    print(f"📝 Configuration chargée depuis: {env_local_path}")
else:
    load_dotenv()
    print("📝 Configuration chargée depuis: .env")

# Configuration MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris_classifier")
AUTO_PROMOTE = True  # Mettre à False pour la phase 2 (promotion manuelle)

# Configuration MinIO/S3
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000")
os.environ["MLFLOW_S3_IGNORE_TLS"] = "true"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


def load_data():
    """Charge et prépare le dataset Iris pour l'entraînement.
    
    Cette fonction charge le dataset Iris depuis scikit-learn, crée un échantillon
    de test pour l'interface utilisateur, et retourne les données divisées en
    ensembles d'entraînement et de test.
    
    Returns:
        tuple: Un tuple de 4 éléments (X_train, X_test, y_train, y_test):
            - X_train (pd.DataFrame): Features d'entraînement
            - X_test (pd.DataFrame): Features de test
            - y_train (pd.Series): Labels d'entraînement
            - y_test (pd.Series): Labels de test
    
    Side Effects:
        Crée un fichier CSV '../data/iris_test.csv' contenant 10 échantillons de test
        avec leurs labels pour l'interface Streamlit.
    
    Example:
        >>> X_train, X_test, y_train, y_test = load_data()
        >>> print(X_train.shape)
    """
    print("📊 Chargement du dataset Iris...")
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name="target")
    
    # Sauvegarder un fichier de test pour le frontend
    X_test_sample = X.sample(n=10, random_state=42)
    y_test_sample = y.loc[X_test_sample.index]
    test_df = X_test_sample.copy()
    test_df["target"] = y_test_sample
    
    os.makedirs("../data", exist_ok=True)
    test_df.to_csv("../data/iris_test.csv", index=False)
    print(f"✅ Fichier de test sauvegardé: ../data/iris_test.csv")
    
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_model(model_type="logistic_regression"):
    """Entraîne un modèle de classification et l'enregistre dans MLflow.
    
    Cette fonction gère le cycle complet d'entraînement:
    - Chargement et préparation des données
    - Entraînement du modèle sélectionné
    - Calcul des métriques de performance
    - Logging des paramètres et métriques dans MLflow
    - Enregistrement du modèle dans le Model Registry
    - Promotion automatique ou manuelle en Production
    
    Args:
        model_type (str): Type de modèle à entraîner. Options:
            - "logistic_regression": Régression logistique (léger, rapide)
            - "random_forest": Random Forest (plus complexe, meilleure performance)
    
    Returns:
        tuple: Un tuple contenant:
            - model_version (str): Numéro de version du modèle dans MLflow
            - accuracy (float): Score d'accuracy sur l'ensemble de test
    
    Raises:
        ValueError: Si model_type n'est pas reconnu
        MLflowException: En cas d'erreur lors de l'enregistrement dans MLflow
    
    Examples:
        >>> version, acc = train_model("logistic_regression")
        >>> print(f"Modèle v{version} - Accuracy: {acc:.4f}")
        Modèle v1 - Accuracy: 0.9667
        
        >>> version, acc = train_model("random_forest")
        >>> print(f"Modèle v{version} - Accuracy: {acc:.4f}")
        Modèle v2 - Accuracy: 0.9833
    
    Note:
        Le comportement de promotion dépend de la variable globale AUTO_PROMOTE:
        - Si True: Le modèle est automatiquement promu avec l'alias "Production"
        - Si False: Une intervention manuelle est requise via l'UI MLflow
    """
    print(f"\n🚀 Démarrage de l'entraînement: {model_type}")
    
    # Chargement des données
    X_train, X_test, y_train, y_test = load_data()
    
    # Choix du modèle
    if model_type == "logistic_regression":
        model = LogisticRegression(max_iter=200, random_state=42)
        params = {"max_iter": 200, "solver": "lbfgs"}
    else:  # random_forest
        model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        params = {"n_estimators": 100, "max_depth": 5}
    
    # Démarrer l'expérience MLflow
    mlflow.set_experiment("iris_classification")
    
    with mlflow.start_run(run_name=f"{model_type}_training") as run:
        print(f"🔬 Run ID: {run.info.run_id}")
        
        # Entraînement
        print("⏳ Entraînement en cours...")
        model.fit(X_train, y_train)
        
        # Prédictions et métriques
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        precision = precision_score(y_test, y_pred, average="weighted")
        recall = recall_score(y_test, y_pred, average="weighted")
        
        # Log des paramètres et métriques
        mlflow.log_params(params)
        mlflow.log_param("model_type", model_type)
        mlflow.log_metrics({
            "accuracy": accuracy,
            "f1_score": f1,
            "precision": precision,
            "recall": recall
        })
        
        print(f"📈 Accuracy: {accuracy:.4f}")
        print(f"📈 F1-Score: {f1:.4f}")
        
        # Enregistrement du modèle (compatible MLflow 2.x et 3.x)
        print("💾 Enregistrement du modèle dans MLflow...")
        
        # Log du modèle comme artifact
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model"
        )
        
        # Enregistrement dans le Model Registry
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        client = MlflowClient()
        
        # Créer ou obtenir le registered model
        try:
            client.create_registered_model(MODEL_NAME)
        except:
            pass  # Le modèle existe déjà
        
        # Créer une nouvelle version
        model_version_info = client.create_model_version(
            name=MODEL_NAME,
            source=model_uri,
            run_id=run_id
        )
        model_version = model_version_info.version
        print(f"✅ Modèle enregistré: {MODEL_NAME} (Version {model_version})")
        
        # Gestion de l'alias "Production"
        if AUTO_PROMOTE:
            print(f"🎯 Promotion automatique en Production (Version {model_version})...")
            client.set_registered_model_alias(
                name=MODEL_NAME,
                alias="Production",
                version=model_version
            )
            print("✅ Modèle promu en Production automatiquement")
        else:
            print(f"⚠️  Mode manuel activé: Allez sur MLflow UI pour promouvoir la Version {model_version}")
            print(f"   URL: {MLFLOW_TRACKING_URI}")
        
        return model_version, accuracy


if __name__ == "__main__":
    print("="*60)
    print("🏭 ML FACTORY - ENTRAÎNEMENT DE MODÈLE")
    print("="*60)
    
    # Phase 1: Régression Logistique (AUTO_PROMOTE=True)
    # Décommentez la ligne suivante pour Phase 1
    version, acc = train_model("logistic_regression")
    
    # Phase 2: Random Forest (AUTO_PROMOTE=False)
    # Décommentez les lignes suivantes et commentez la ligne ci-dessus pour Phase 2
    # version, acc = train_model("random_forest")
    
    print("\n" + "="*60)
    print(f"✅ Entraînement terminé - Version: {version} - Accuracy: {acc:.4f}")
    print("="*60)
