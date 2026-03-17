"""API FastAPI pour servir les prédictions du modèle Iris avec hot-reloading.

Ce module implémente une API RESTful pour effectuer des prédictions de classification
sur le dataset Iris en utilisant MLflow Model Registry. L'API supporte le hot-reloading
automatique des modèles, permettant de mettre à jour l'intelligence sans redémarrer le service.

Architecture:
    - **Zero-Downtime**: Rechargement dynamique du modèle à chaque requête si nécessaire
    - **Model Registry**: Utilise MLflow pour récupérer les modèles via des alias
    - **S3 Storage**: Les modèles sont stockés dans MinIO (compatible S3)
    - **CORS Enabled**: Support des requêtes cross-origin pour le frontend

Endpoints:
    - GET  /            : Informations sur l'API
    - GET  /health      : Health check avec état du modèle
    - GET  /model-info  : Informations détaillées du modèle en production
    - POST /predict     : Prédiction sur une instance individuelle
    - POST /predict-batch : Prédictions en batch sur plusieurs instances

Environment Variables:
    MLFLOW_TRACKING_URI: URI du serveur MLflow (défaut: http://mlflow:5000)
    MODEL_NAME: Nom du modèle dans le registre (défaut: iris_classifier)
    MODEL_ALIAS: Alias du modèle à utiliser (défaut: Production)
    AWS_ACCESS_KEY_ID: Clé d'accès MinIO/S3
    AWS_SECRET_ACCESS_KEY: Secret MinIO/S3
    MLFLOW_S3_ENDPOINT_URL: URL du endpoint S3 (défaut: http://minio:9000)

Examples:
    Démarrage local::

        $ uvicorn main:app --host 0.0.0.0 --port 8000

    Prédiction avec curl::

        $ curl -X POST http://localhost:8000/predict \\
               -H "Content-Type: application/json" \\
               -d '{"sepal_length": 5.1, "sepal_width": 3.5, 
                    "petal_length": 1.4, "petal_width": 0.2}'

Note:
    L'API vérifie automatiquement à chaque requête si une nouvelle version
    du modèle est disponible via l'alias "Production". Si détectée, le modèle
    est rechargé à chaud depuis MinIO sans interruption de service.
"""

import os
from typing import List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import mlflow
from mlflow.tracking import MlflowClient
import numpy as np


# Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris_classifier")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "Production")

# Configuration S3/MinIO
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# État global de l'application
app_state = {
    "model": None,
    "model_version": None,
    "client": None
}


class IrisFeatures(BaseModel):
    """Schéma Pydantic pour les features du dataset Iris.
    
    Définit et valide les 4 caractéristiques morphologiques d'une fleur d'Iris
    utilisées pour la classification.
    
    Attributes:
        sepal_length (float): Longueur du sépale en centimètres (0-10 cm)
        sepal_width (float): Largeur du sépale en centimètres (0-10 cm)
        petal_length (float): Longueur du pétale en centimètres (0-10 cm)
        petal_width (float): Largeur du pétale en centimètres (0-10 cm)
    
    Examples:
        >>> features = IrisFeatures(
        ...     sepal_length=5.1,
        ...     sepal_width=3.5,
        ...     petal_length=1.4,
        ...     petal_width=0.2
        ... )
    """
    sepal_length: float = Field(..., ge=0, le=10, description="Longueur du sépale en cm")
    sepal_width: float = Field(..., ge=0, le=10, description="Largeur du sépale en cm")
    petal_length: float = Field(..., ge=0, le=10, description="Longueur du pétale en cm")
    petal_width: float = Field(..., ge=0, le=10, description="Largeur du pétale en cm")


class PredictionResponse(BaseModel):
    """Schéma de la réponse de prédiction"""
    prediction: int
    prediction_label: str
    probabilities: Dict[str, float]
    model_version: str
    model_name: str


def load_production_model():
    """
    Charge le modèle en production depuis MLflow
    Utilise l'alias pour récupérer la dernière version validée
    """
    try:
        client = MlflowClient()
        
        # Récupérer les informations du modèle via l'alias
        model_version_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        version = model_version_info.version
        
        # Vérifier si on doit recharger le modèle
        if app_state["model_version"] != version:
            print(f"🔄 Chargement du modèle {MODEL_NAME} (Version {version}) via alias '{MODEL_ALIAS}'...")
            model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
            model = mlflow.pyfunc.load_model(model_uri)
            
            app_state["model"] = model
            app_state["model_version"] = version
            app_state["client"] = client
            
            print(f"✅ Modèle chargé avec succès: Version {version}")
        
        return app_state["model"], app_state["model_version"]
    
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Impossible de charger le modèle en production: {str(e)}"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    print("🚀 Démarrage de l'API ML Factory...")
    print(f"📡 MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"🏷️  Modèle: {MODEL_NAME} (Alias: {MODEL_ALIAS})")
    
    # Chargement initial du modèle
    try:
        load_production_model()
        print("✅ API prête à recevoir des requêtes")
    except Exception as e:
        print(f"⚠️  Avertissement: Impossible de charger le modèle au démarrage: {e}")
    
    yield
    
    print("🛑 Arrêt de l'API ML Factory")


# Initialisation de l'application
app = FastAPI(
    title="ML Factory API",
    description="API de prédiction pour le modèle de classification Iris avec hot-reloading",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping des classes Iris
IRIS_CLASSES = {
    0: "Setosa",
    1: "Versicolor",
    2: "Virginica"
}


@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API"""
    return {
        "message": "ML Factory API",
        "status": "running",
        "model_name": MODEL_NAME,
        "model_alias": MODEL_ALIAS,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "model_info": "/model-info"
        }
    }


@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API et du modèle"""
    try:
        model, version = load_production_model()
        return {
            "status": "healthy",
            "model_loaded": model is not None,
            "model_version": version,
            "model_name": MODEL_NAME
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/model-info")
async def model_info():
    """Récupère les informations sur le modèle en production"""
    try:
        _, version = load_production_model()
        client = app_state["client"]
        
        model_version_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        
        return {
            "model_name": MODEL_NAME,
            "model_version": version,
            "model_alias": MODEL_ALIAS,
            "run_id": model_version_info.run_id,
            "status": model_version_info.status,
            "creation_timestamp": model_version_info.creation_timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: IrisFeatures):
    """
    Effectue une prédiction sur les features fournies
    Hot-reloading: vérifie automatiquement si une nouvelle version est disponible
    """
    try:
        # Chargement (ou rechargement) du modèle
        model, version = load_production_model()
        
        # Préparation des données
        input_data = np.array([[
            features.sepal_length,
            features.sepal_width,
            features.petal_length,
            features.petal_width
        ]])
        
        # Prédiction
        prediction = model.predict(input_data)[0]
        prediction_int = int(prediction)
        
        # Calcul des probabilités si disponible
        try:
            probabilities_array = model.predict_proba(input_data)[0]
            probabilities = {
                IRIS_CLASSES[i]: float(prob) 
                for i, prob in enumerate(probabilities_array)
            }
        except AttributeError:
            # Si le modèle ne supporte pas predict_proba
            probabilities = {IRIS_CLASSES[i]: 0.0 for i in range(3)}
            probabilities[IRIS_CLASSES[prediction_int]] = 1.0
        
        return PredictionResponse(
            prediction=prediction_int,
            prediction_label=IRIS_CLASSES[prediction_int],
            probabilities=probabilities,
            model_version=str(version),
            model_name=MODEL_NAME
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )


@app.post("/predict-batch")
async def predict_batch(features_list: List[IrisFeatures]):
    """Effectue des prédictions en batch"""
    try:
        model, version = load_production_model()
        
        # Préparation des données
        input_data = np.array([
            [f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]
            for f in features_list
        ])
        
        # Prédictions
        predictions = model.predict(input_data)
        
        results = []
        for pred in predictions:
            pred_int = int(pred)
            results.append({
                "prediction": pred_int,
                "prediction_label": IRIS_CLASSES[pred_int]
            })
        
        return {
            "predictions": results,
            "model_version": str(version),
            "model_name": MODEL_NAME,
            "count": len(results)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction batch: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
