# 🎯 Guide d'Évaluation - ML Factory Zero-Downtime

## 📋 Modalités d'Évaluation

---

## ⚡ Critères de Performance à Démontrer

### 1️⃣ Réactivité (< 10 secondes)

**Critère :** L'API détecte et charge la nouvelle version du modèle "Production" en moins de 10 secondes après le changement d'alias.

**Comment le prouver :**

```markdown
1. Ouvrir 2 onglets côte à côte :
   - MLflow UI (http://localhost:5000)
   - Streamlit (http://localhost:8501)

2. Noter l'heure exacte : [14:30:00]

3. Dans MLflow → Models → iris_classifier :
   - Changer l'alias "Production" de v2 vers v3
   - Clic sur "Save"
   - Noter l'heure : [14:30:02]

4. Observer Streamlit :
   - Le badge change automatiquement en 5-7 secondes max
   - Noter l'heure du changement : [14:30:07]
   - ✅ Delta = 5 secondes (< 10 secondes requis)
```

**Configuration technique :**

```python
# src/api/main.py
MODEL_RELOAD_INTERVAL = 5  # Polling toutes les 5 secondes

@app.on_event("startup")
async def schedule_model_reload():
    async def reload_task():
        while True:
            await asyncio.sleep(MODEL_RELOAD_INTERVAL)
            await reload_model_if_changed()
```

> **"Le polling de 5 secondes garantit une détection en moins de 10 secondes, largement sous la limite requise."**

---

### 2️⃣ Traçabilité (Version dans chaque réponse)

**Critère :** Chaque réponse de l'API contient explicitement le numéro de version du modèle utilisé.

**Comment le prouver :**

```bash
# Test via curl
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

**Réponse JSON :**

```json
{
  "predicted_class": 0,
  "class_name": "setosa",
  "probabilities": {
    "setosa": 0.98,
    "versicolor": 0.01,
    "virginica": 0.01
  },
  "model_version": "3",          ← ✅ Version explicite
  "model_name": "iris_classifier",
  "run_id": "a1b2c3d4e5f6..."     ← ✅ Run ID pour traçabilité totale
}
```

**Code source à montrer :**

```python
# src/api/main.py - Ligne ~150
@app.post("/predict", response_model=PredictionResponse)
async def predict(features: IrisFeatures):
    # ... prédiction ...
    return PredictionResponse(
        predicted_class=int(prediction[0]),
        class_name=iris_classes[int(prediction[0])],
        probabilities=probabilities_dict,
        model_version=str(current_model_version),  # ← Version ajoutée
        model_name=MODEL_NAME,
        run_id=current_run_id
    )
```

> **"Chaque réponse inclut 3 niveaux de traçabilité : Version (3), Nom (iris_classifier), Run ID (UUID MLflow). On peut remonter jusqu'aux hyperparamètres de l'entraînement."**

---

### 3️⃣ Isolation (Conteneurs distincts)

**Critère :** Les services sont correctement isolés dans des conteneurs distincts avec des dépendances gérées par UV ou Pip.

**Comment le prouver :**

```bash
# Vérifier l'isolation des conteneurs
docker-compose ps

# Résultat attendu :
NAME      IMAGE                   PORTS
api       projet_api              0.0.0.0:8000->8000/tcp
front     projet_front            0.0.0.0:8501->8501/tcp
mlflow    ghcr.io/mlflow/mlflow   0.0.0.0:5000->5000/tcp
minio     minio/minio             0.0.0.0:9000-9001->9000-9001/tcp
```

**Preuve d'isolation des dépendances :**

```bash
# API : requirements.txt avec versions précises
cd src/api
cat requirements.txt
# fastapi==0.109.0
# mlflow==2.17.2
# scikit-learn==1.5.0
# uvicorn[standard]==0.27.0

# Frontend : requirements.txt différent
cd src/front
cat requirements.txt
# streamlit==1.40.0
# requests==2.32.0
# plotly==5.18.0
```

**Architecture réseau isolée :**

```yaml
# docker-compose.yml
networks:
  ml_network:
    driver: bridge  # ← Réseau privé isolé

services:
  api:
    networks:
      - ml_network  # ← Pas d'accès direct à l'hôte
    ports:
      - "8000:8000" # ← Port exposé contrôlé
```

> **"Chaque service a son propre Dockerfile, ses propres dépendances, et communique via un réseau Docker isolé. Si l'API crashe, Streamlit continue de tourner."**

**Test d'isolation :**

```bash
# Arrêter uniquement l'API
docker stop api

# Vérifier que Streamlit fonctionne toujours (affiche une erreur réseau, mais ne crash pas)
curl http://localhost:8501  # ← 200 OK

# Redémarrer l'API
docker start api  # ← Streamlit reconnecte automatiquement
```

---

### 4️⃣ Persistance (Survie à docker-compose down)

**Critère :** Les modèles entraînés et les métadonnées MLflow survivent à un `docker-compose down`.

**Comment le prouver :**

```bash
# 1. État initial : noter les modèles actuels
curl http://localhost:8000/model-info
# {"model_name": "iris_classifier", "version": "3", "run_id": "abc123"}

# 2. Arrêter TOUS les containers
docker-compose down

# Résultat :
# Stopping front  ... done
# Stopping api    ... done
# Stopping mlflow ... done
# Stopping minio  ... done
# Removing front  ... done
# Removing api    ... done
# Removing mlflow ... done
# Removing minio  ... done
# Removing network projet_2_1_mlfactory_ml_network ... done

# 3. Vérifier que les volumes persistent
docker volume ls | grep projet

# Résultat :
# projet_2_1_mlfactory_mlflow_data
# projet_2_1_mlfactory_minio_data

# 4. Redémarrer l'infrastructure
docker-compose up -d

# 5. Vérifier que les données sont toujours là
curl http://localhost:8000/model-info
# {"model_name": "iris_classifier", "version": "3", "run_id": "abc123"}
# ✅ Même version, même run_id → Persistance confirmée

# 6. Vérifier MLflow UI
# http://localhost:5000 → Tous les runs et modèles sont toujours présents
```

**Configuration technique de la persistance :**

```yaml
# docker-compose.yml
volumes:
  mlflow_data:   # ← Volume nommé (persiste après down)
  minio_data:    # ← Volume nommé (persiste après down)

services:
  mlflow:
    volumes:
      - mlflow_data:/mlflow  # ← Montage dans le conteneur
    command: >
      mlflow server
      --backend-store-uri sqlite:///mlflow.db  # ← DB SQLite dans le volume
      --default-artifact-root s3://mlflow/     # ← Artifacts dans MinIO

  minio:
    volumes:
      - minio_data:/data  # ← Bucket mlflow/ stocké ici
```

**Preuve visuelle :**

```bash
# Inspecter le contenu du volume MLflow
docker run --rm -v projet_2_1_mlfactory_mlflow_data:/data alpine ls -lh /data

# Résultat :
# drwxr-xr-x  mlflow.db        ← Base de données SQLite
# -rw-r--r--  mlflow.db-shm
# -rw-r--r--  mlflow.db-wal

# Inspecter le contenu du volume MinIO
docker run --rm -v projet_2_1_mlfactory_minio_data:/data alpine ls -lh /data/mlflow

# Résultat :
# drwxr-xr-x  1/abc123/artifacts/model/  ← Modèle v1
# drwxr-xr-x  1/def456/artifacts/model/  ← Modèle v2
# drwxr-xr-x  1/ghi789/artifacts/model/  ← Modèle v3
```

> **"Les volumes Docker nommés garantissent que les données survivent aux redémarrages. Même après docker-compose down, les 3 versions de modèles et toutes les métriques MLflow sont conservées. On peut faire un rollback à v1 à tout moment."**

**⚠️ Attention : docker-compose down -v supprime les volumes !**

```bash
# Ne PAS faire ça en production :
docker-compose down -v  # ← Supprime les volumes (perte de données)

# Commande recommandée :
docker-compose down     # ← Garde les volumes intacts
```

---

## 📊 Tableau Récapitulatif des Critères

| Critère | Valeur Cible | Valeur Projet | Validation |
|---------|--------------|---------------|------------|
| **Réactivité** | < 10 secondes | **5 secondes** (polling) | ✅ |
| **Traçabilité** | Version dans réponse | `model_version`, `run_id` | ✅ |
| **Isolation** | Conteneurs distincts | 4 services + réseau privé | ✅ |
| **Persistance** | Survive à `down` | Volumes Docker nommés | ✅ |

---

## 📋 Modalités d'Évaluation

### 1️⃣ Démonstration Technique (Zero-Downtime)

#### 🎬 Scénario de démonstration

**Objectif :** Prouver que l'API change de modèle **sans redémarrage** et **sans interruption de service**.

#### 📝 Script de démonstration

```markdown
1. **État Initial**
   - Ouvrir Streamlit : http://localhost:8501
   - Montrer le badge "Model Version: v1" (ou v2 selon l'historique)
   - Faire une prédiction → noter les probabilités

2. **Entraînement d'un nouveau modèle**
   - Ouvrir le notebook : notebooks/train_model.ipynb
   - Exécuter les cellules d'entraînement (Logistic Regression + Random Forest)
   - Montrer les métriques comparées (accuracy, F1-score)
   - Le meilleur modèle est automatiquement promu en "Production"

3. **Vérification MLflow**
   - Ouvrir MLflow UI : http://localhost:5000
   - Aller dans "Models" → "iris_classifier"
   - Montrer les versions (v1, v2, v3...)
   - Montrer l'alias "Production" pointant vers la dernière version

4. **Observation du Zero-Downtime**
   - Retourner sur Streamlit (http://localhost:8501)
   - Attendre 5 secondes (polling automatique de l'API)
   - Le badge change automatiquement : "Model Version: v3" 
   - Faire une nouvelle prédiction avec les MÊMES features
   - Les probabilités peuvent différer (nouveau modèle chargé)

5. **Preuve technique**
   - Ouvrir les logs Docker : `docker-compose logs api -f`
   - Montrer la ligne : "[INFO] Model version changed from vX to vY. Reloading..."
   - Montrer qu'aucun redémarrage n'a eu lieu (pas de "Starting server" ou "Application startup")
```

#### 🗣️ Points clés à mentionner

> **"Le Zero-Downtime repose sur 3 piliers :**
> 
> 1. **Détection automatique** : L'API interroge MLflow toutes les 5 secondes pour vérifier la version du modèle en Production.
> 
> 2. **Hot-reload intelligent** : Si la version change, l'API recharge uniquement le modèle en mémoire via `mlflow.pyfunc.load_model()` sans redémarrer le processus.
> 
> 3. **Isolation des modèles** : Le stockage des modèles est externalisé dans MLflow + MinIO, donc l'API peut charger n'importe quelle version à chaud."

---

### 2️⃣ Revue de Code

#### 📁 Fichier 1 : Gestion des variables d'environnement

**Fichier :** `.env`, `.env.local`

```markdown
**Organisation des environnements :**

1. `.env` : Configuration pour les services Docker
   - `MLFLOW_TRACKING_URI=http://mlflow:5000` (hostname Docker)
   - `MLFLOW_S3_ENDPOINT_URL=http://minio:9000` (réseau interne)
   
2. `.env.local` : Configuration pour développement local (notebook)
   - `MLFLOW_TRACKING_URI=http://localhost:5000` (accès depuis l'hôte)
   - `MLFLOW_S3_ENDPOINT_URL=http://localhost:9000`

**Pourquoi cette séparation ?**
- Les containers Docker communiquent via DNS interne (`mlflow`, `minio`)
- Le notebook Jupyter tourne sur l'hôte Windows → nécessite `localhost`
- Protection des secrets : `.env` est gitignored, `.env.local` override les valeurs
```

**Fichier :** `notebooks/train_model.ipynb` (Cellule 4)

```python
# Détection automatique Docker vs Localhost
if "mlflow:" in MLFLOW_TRACKING_URI:
    MLFLOW_TRACKING_URI = MLFLOW_TRACKING_URI.replace("http://mlflow:", "http://localhost:")
    print(f"⚠️  URI Docker détectée, conversion en localhost")
```

> **"Cette logique garantit que le notebook fonctionne même si l'utilisateur oublie de créer `.env.local`, en convertissant automatiquement les hostnames Docker."**

#### 🛡️ Fichier 2 : Robustesse de l'API

**Fichier :** `src/api/main.py`

**Gestion d'erreurs robuste :**

```python
@app.get("/model-info")
async def get_model_info():
    """Endpoint avec gestion d'erreur si le modèle n'existe pas."""
    try:
        model_version_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        return {
            "model_name": MODEL_NAME,
            "version": model_version_info.version,
            "run_id": model_version_info.run_id
        }
    except MlflowException as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Model '{MODEL_NAME}' with alias '{MODEL_ALIAS}' not found"
        )
```

**Points de robustesse à mentionner :**

1. **Validation Pydantic** : Les entrées `/predict` sont validées via `IrisFeatures` (schéma strict)
2. **Gestion des exceptions MLflow** : Si le modèle n'existe pas, retourne HTTP 404 au lieu de crasher
3. **Health check** : Endpoint `/health` pour vérifier que l'API répond
4. **Retry logic** : Si MLflow est temporairement indisponible, l'API attend (depends_on dans docker-compose)

---

### 3️⃣ Entretien Oral - Justification des Choix d'Architecture

#### ❓ Question : "Pourquoi découpler le stockage des modèles de l'API ?"

**Réponse structurée :**

> **"J'ai découplé le stockage pour 3 raisons principales :"**

#### 1️⃣ **Scalabilité horizontale**

```
Problème sans découplage :
┌─────────────┐
│  API + Model│  ← 2 GB de RAM (modèle embarqué)
│  (v1 seul)  │
└─────────────┘

Solution avec MLflow Registry :
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  API        │   │  API        │   │  API        │
│  (charge v1)│   │  (charge v1)│   │  (charge v1)│
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                ┌────────▼───────┐
                │ MLflow Registry│ ← Stockage centralisé
                │ (v1, v2, v3...) │
                └─────────────────┘
```

> **"Je peux lancer 10 instances de l'API sans dupliquer les modèles. Toutes chargent depuis MLflow."**

#### 2️⃣ **Zero-Downtime et versioning**

```
Architecture découplée :
┌─────────────┐
│  API (v1)   │  ← Charge le modèle en mémoire
└──────┬──────┘
       │ polling toutes les 5s
       │
┌──────▼──────┐
│ MLflow      │
│ Registry    │ ← alias "Production" = v2
│             │
│ v1: setosa  │ (ancien)
│ v2: setosa  │ (actuel) ← alias "Production"
│ v3: setosa  │ (test)
└─────────────┘

Quand l'alias change :
→ API détecte : "Production" = v3 maintenant
→ mlflow.pyfunc.load_model("models:/iris_classifier@Production")
→ Remplacement en mémoire (pas de redémarrage)
```

> **"Le découplage permet de changer le modèle en production sans toucher au code de l'API. On modifie juste l'alias dans MLflow."**

#### 3️⃣ **Traçabilité et gouvernance**

| Aspect | Sans MLflow | Avec MLflow Registry |
|--------|-------------|---------------------|
| Historique | ❌ Écrasement du fichier .pkl | ✅ Toutes les versions conservées |
| Rollback | ❌ Impossible (sauf Git) | ✅ Changer l'alias en 1 clic |
| Métriques | ❌ Perdues après training | ✅ Liées au modèle (accuracy, F1...) |
| Artifacts | ❌ Fichier local fragile | ✅ S3 (MinIO) avec redondance |
| Audit | ❌ Qui a déployé v2 ? | ✅ Run ID, timestamp, auteur |

> **"En production réelle, je dois pouvoir répondre : 'Quel modèle tourne actuellement ? Quelles étaient ses performances ? Qui l'a entraîné ?' MLflow centralise tout ça."**

#### 4️⃣ **Séparation des responsabilités (SoC)**

```
Rôles découplés :
┌─────────────────────────┐
│  Data Scientist         │ ← Entraîne et enregistre dans MLflow
│  (notebooks/train.py)   │
└────────┬────────────────┘
         │
         │ mlflow.sklearn.log_model()
         │
┌────────▼────────────────┐
│  MLflow Registry        │ ← Stockage centralisé
│  + MinIO (S3)           │
└────────┬────────────────┘
         │
         │ mlflow.pyfunc.load_model()
         │
┌────────▼────────────────┐
│  API FastAPI            │ ← Sert les prédictions
│  (production)           │
└─────────────────────────┘
```

> **"Le Data Scientist n'a pas besoin de connaître le code de l'API. Il entraîne, enregistre dans MLflow, et l'API se met à jour automatiquement. C'est la philosophie MLOps."**

---

## 🎤 Questions Pièges Potentielles

### Q1 : "Que se passe-t-il si MLflow est en panne ?"

**Réponse :**
> "L'API continue de servir avec le dernier modèle chargé en mémoire. Le polling échoue mais ne crashe pas l'API. J'ai isolé la logique de rechargement dans un try/except. Les prédictions continuent de fonctionner."

### Q2 : "Pourquoi 5 secondes de polling ? C'est pas trop lent ?"

**Réponse :**
> "5 secondes est un bon compromis :
> - Assez rapide pour une démo (changement visible rapidement)
> - Assez lent pour ne pas surcharger MLflow (12 requêtes/minute)
> - En production, on peut ajuster avec une variable d'environnement `MODEL_RELOAD_INTERVAL`
> - Alternative : utiliser un webhook MLflow pour notification instantanée"

### Q3 : "Pourquoi MinIO et pas directement le filesystem ?"

**Réponse :**
> "MinIO simule un S3 réel :
> - Compatible avec AWS S3, Azure Blob, GCS (même API)
> - Permet la redondance et la scalabilité
> - En production, on remplace juste l'endpoint par `s3://bucket-prod/mlflow`
> - Le code ne change pas, c'est juste une variable d'environnement"

### Q4 : "Comment testes-tu que le Zero-Downtime fonctionne réellement ?"

**Réponse :**
> "J'ai 3 preuves :
> 1. **Badge de version dans Streamlit** : Change sans refresh manuel
> 2. **Logs de l'API** : Message 'Model reloaded' sans 'Starting server'
> 3. **Test de charge** : `curl http://localhost:8000/predict` en boucle pendant le changement → 0 erreur 5xx"

---

## 📊 Checklist de Préparation

### Avant la démonstration :

- [ ] Démarrer tous les services : `docker-compose up -d`
- [ ] Vérifier que les 4 services sont UP : `docker-compose ps`
- [ ] **Vérifier la persistance** : `docker volume ls | grep projet` (2 volumes doivent exister)
- [ ] Ouvrir les 4 onglets du navigateur :
  - [ ] Streamlit : http://localhost:8501
  - [ ] MLflow : http://localhost:5000
  - [ ] FastAPI : http://localhost:8000/docs
  - [ ] MinIO : http://localhost:9001 (minioadmin/minioadmin)
- [ ] Avoir un terminal prêt pour : `docker-compose logs api -f`
- [ ] Ouvrir le notebook : `notebooks/train_model.ipynb`
- [ ] **Tester la traçabilité** : `curl http://localhost:8000/model-info` (noter la version actuelle)
- [ ] **Tester une prédiction** avec curl pour vérifier que `model_version` apparaît dans la réponse

### Tests des critères de performance :

- [ ] **Réactivité** : Chronomètre prêt pour mesurer le temps de rechargement (doit être < 10s)
- [ ] **Traçabilité** : Vérifier que `/predict` retourne bien `model_version` et `run_id`
- [ ] **Isolation** : Préparer `docker-compose ps` pour montrer les 4 conteneurs distincts
- [ ] **Persistance** : Optionnel - faire un test `docker-compose down && docker-compose up -d` avant la démo

### Pendant la démo :

- [ ] Parler lentement et expliquer chaque étape
- [ ] Montrer le code source (API, notebook) si demandé
- [ ] Justifier chaque choix technique (pourquoi FastAPI ? pourquoi MLflow ?)
- [ ] Être prêt à répondre aux questions sur la scalabilité

### Points forts à valoriser :

- ✅ Architecture complète MLOps (training → registry → serving → monitoring)
- ✅ Zero-Downtime prouvé en conditions réelles
- ✅ Séparation des environnements (Docker vs Local)
- ✅ Documentation exhaustive (README, Sphinx, docstrings)
- ✅ Réutilisabilité (facile d'adapter à un autre modèle)

---

---

## 🧪 Scripts de Test Prêts à l'Emploi

### Test 1 : Vérifier la traçabilité

```powershell
# Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

```bash
# Linux/Mac
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

**Sortie attendue :**
```json
{
  "predicted_class": 0,
  "class_name": "setosa",
  "probabilities": {...},
  "model_version": "3",           ← ✅ Critère validé
  "model_name": "iris_classifier",
  "run_id": "..."
}
```

---

### Test 2 : Mesurer la réactivité (avec chronomètre)

```powershell
# 1. Noter l'heure de début
Get-Date -Format "HH:mm:ss"

# 2. Changer l'alias dans MLflow UI (manuellement)

# 3. Boucle de vérification (toutes les 2 secondes)
while ($true) {
    $response = Invoke-RestMethod "http://localhost:8000/model-info"
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Version: $($response.version)"
    Start-Sleep -Seconds 2
}
```

**Sortie attendue :**
```
14:30:00 - Version: 2
14:30:02 - Version: 2  ← Alias changé dans MLflow à cette heure
14:30:04 - Version: 2
14:30:06 - Version: 3  ← ✅ Détection en 4 secondes (< 10s)
```

---

### Test 3 : Vérifier l'isolation des conteneurs

```powershell
# Voir les 4 conteneurs distincts
docker-compose ps

# Voir les réseaux isolés
docker network ls | Select-String "projet"

# Voir les dépendances du service API
docker exec api pip list | Select-String "fastapi|mlflow|scikit"
```

---

### Test 4 : Tester la persistance

```powershell
# 1. Sauvegarder la version actuelle
$versionAvant = (Invoke-RestMethod "http://localhost:8000/model-info").version
Write-Host "Version avant: $versionAvant"

# 2. Arrêter tous les services
docker-compose down

# 3. Vérifier que les volumes existent toujours
docker volume ls | Select-String "projet"

# 4. Redémarrer
docker-compose up -d
Start-Sleep -Seconds 15  # Attendre le démarrage complet

# 5. Vérifier que la version est identique
$versionApres = (Invoke-RestMethod "http://localhost:8000/model-info").version
Write-Host "Version après: $versionApres"

if ($versionAvant -eq $versionApres) {
    Write-Host "✅ PERSISTANCE VALIDÉE" -ForegroundColor Green
} else {
    Write-Host "❌ ERREUR: Version différente" -ForegroundColor Red
}
```

---

## 🎯 Conclusion

> **"Ce projet démontre une architecture MLOps production-ready avec :**
> 
> **1. Zero-Downtime garanti** par un hot-reloading avec détection en moins de 5 secondes
> 
> **2. Traçabilité complète** : Chaque prédiction retourne la version du modèle, le nom et le run ID MLflow
> 
> **3. Isolation robuste** : 4 conteneurs Docker distincts communiquant via un réseau privé, chacun avec ses propres dépendances
> 
> **4. Persistance garantie** : Volumes Docker nommés assurant la survie des modèles et métadonnées après redémarrages
> 
> **Cette approche répond aux 4 critères de performance et est conforme aux bonnes pratiques MLOps de l'industrie (versioning, audit, scalabilité, résilience)."**

---

### 📈 Dépassement des Critères

| Critère | Requis | Projet | Bonus |
|---------|--------|--------|-------|
| Réactivité | < 10s | **5s** | 🌟 Configurable via variable d'environnement |
| Traçabilité | Version | **Version + Run ID + Nom** | 🌟 Lien vers MLflow UI possible |
| Isolation | Conteneurs | **+ Réseau privé** | 🌟 Healthchecks pour orchestration |
| Persistance | Survive down | **+ Backup possible (volumes)** | 🌟 Compatible S3 réel en prod |

---

💡 **Conseil final :** Entraîne-toi à faire la démo 2-3 fois avant l'évaluation pour être fluide. Chronomètre-toi : la démo complète doit prendre **5-7 minutes maximum**. Prépare les scripts de test dans un fichier `.txt` pour les copier-coller rapidement pendant l'évaluation.
