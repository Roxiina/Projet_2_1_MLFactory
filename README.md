# 🏭 ML Factory - MLOps Zero-Downtime

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![MLflow](https://img.shields.io/badge/MLflow-2.10+-green.svg)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Plateforme MLOps complète avec déploiement **Zero-Downtime**, Model Registry MLflow et hot-reloading automatique.

---

## 🚀 Démarrage Rapide (3 minutes)

```bash
# 1. Démarrer l'infrastructure
docker-compose up -d

# 2. Entraîner le premier modèle
cd src/train && python train.py

# 3. Ouvrir l'interface
# → http://localhost:8501
```

### 🌐 Services Disponibles

| Service | URL | Credentials |
|---------|-----|-------------|
| **Streamlit** | http://localhost:8501 | - |
| **FastAPI** | http://localhost:8000/docs | - |
| **MLflow** | http://localhost:5000 | - |
| **MinIO** | http://localhost:9001 | admin / admin123 |

---

## 📚 Documentation Complète

**Toute la documentation est dans Sphinx** - Générez-la avec:

```bash
# Installer les dépendances docs
uv pip install -e ".[docs]"

# Générer la documentation
cd docs
make html  # ou .\make.bat html sur Windows

# Ouvrir
start _build/html/index.html  # Windows
# ou: xdg-open _build/html/index.html  # Linux
# ou: open _build/html/index.html      # MacOS
```

### 📖 Contenu de la Documentation

La documentation Sphinx contient:

- **Guides Utilisateur** (Installation, Quickstart, Troubleshooting)
- **Guides Développeur** (Architecture, Entraînement Custom, Déploiement)
- **Référence API** (Documentation complète des modules Python)
- **Exemples et Tutoriels** (Zero-Downtime workflow, etc.)

---

## ✨ Fonctionnalités Clés

✅ **Zero-Downtime Deployment** - Changez de modèle sans restart  
✅ **Hot-Reloading** - Détection automatique des nouvelles versions  
✅ **Model Registry MLflow** - Versioning et promotion auto/manuelle  
✅ **API REST** - FastAPI avec 5 endpoints documentés  
✅ **Interface Interactive** - Streamlit avec dual input (manuel + CSV)  
✅ **Object Storage** - MinIO S3-compatible pour les artefacts  

---

## 🏗️ Architecture

```
Utilisateur
    ↓
Streamlit (8501) → FastAPI (8000) → MLflow (5000)
                        ↓
                   MinIO (9000)
```

**Pattern clé:** L'API interroge l'alias "Production" sur MLflow à chaque requête, télécharge le nouveau modèle si la version a changé, et met à jour le cache en mémoire. **Aucun restart nécessaire!**

---

## 🔄 Workflow Zero-Downtime

```bash
# 1. Entraîner v1 (LogisticRegression)
python src/train/train.py

# 2. Entraîner v2 en mode manuel
# Modifier train.py: AUTO_PROMOTE=False, model_type="random_forest"
python src/train/train.py

# 3. Streamlit affiche toujours v1 → Aucune interruption ✅

# 4. Promouvoir manuellement sur MLflow UI
# Models → iris_classifier → Version 2 → Set alias "Production"

# 5. Streamlit détecte v2 instantanément! 🎉
```

**Résultat:** Changement de modèle transparent, sans downtime.

---

## 🛠️ Scripts Utilitaires

```powershell
# Windows PowerShell
.\manage.ps1 start    # Démarrer tous les services
.\manage.ps1 train    # Entraîner un modèle
.\manage.ps1 status   # Vérifier l'état
.\manage.ps1 logs     # Voir les logs
.\manage.ps1 stop     # Arrêter les services
```

---

## 📦 Technologies

- **MLflow** - Model Registry et Experiment Tracking
- **FastAPI** - API REST avec hot-reloading
- **Streamlit** - Interface interactive
- **MinIO** - Object Storage S3-compatible
- **Scikit-learn** - Machine Learning
- **Docker** - Containerisation
- **Sphinx** - Documentation professionnelle

---

## 🚨 Besoin d'Aide?

**Consultez la documentation Sphinx pour:**
- Installation détaillée et prérequis
- Guide de dépannage complet
- Tutoriel Zero-Downtime pas-à-pas
- Architecture technique détaillée
- Déploiement en production (Docker, Kubernetes, Cloud)
- Personnalisation et extensions

```bash
cd docs && make html
```

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

## 🎓 Projet Simplon France

Développé dans le cadre de la formation MLOps - **Simplon France 2026**

---

**⚡ Pour démarrer immédiatement:** `docker-compose up -d && cd src/train && python train.py`

**📚 Pour la doc complète:** `cd docs && make html`
