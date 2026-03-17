# 📓 Notebooks Jupyter - ML Factory

Ce dossier contient des notebooks Jupyter interactifs pour l'entraînement et l'exploration des modèles.

## 📋 Notebooks disponibles

### `train_model.ipynb` - Entraînement Interactif

Notebook complet pour :
- 📊 Explorer le dataset Iris avec visualisations
- 🤖 Entraîner plusieurs modèles (Logistic Regression, Random Forest)
- 📈 Comparer les performances avec graphiques
- 🚀 Enregistrer et promouvoir dans MLflow
- ✅ Tester le Zero-Downtime en temps réel

## 🚀 Démarrage Rapide

### Option 1 : Via le script de gestion (recommandé)

```powershell
# Windows PowerShell
.\manage.ps1 notebook
```

### Option 2 : Manuellement

```bash
# Installer les dépendances
cd notebooks
pip install -r requirements.txt

# Lancer Jupyter Lab
jupyter lab

# Ou Jupyter Notebook classique
jupyter notebook
```

## 📦 Dépendances

Le fichier `requirements.txt` contient :
- **Jupyter Lab/Notebook** - Interface interactive
- **MLflow** - Tracking et Model Registry
- **Scikit-learn** - Machine Learning
- **Pandas/Numpy** - Manipulation de données
- **Matplotlib/Seaborn/Plotly** - Visualisations

## 🎯 Workflow Recommandé

1. **Démarrer l'infrastructure** :
   ```powershell
   .\manage.ps1 start
   ```

2. **Lancer Jupyter Lab** :
   ```powershell
   .\manage.ps1 notebook
   ```

3. **Ouvrir `train_model.ipynb`** et exécuter les cellules séquentiellement

4. **Observer les résultats** :
   - MLflow UI : http://localhost:5000
   - API : http://localhost:8000/docs
   - Streamlit : http://localhost:8501

## 💡 Conseils

### Mode Automatique vs Manuel

Dans le notebook, vous pouvez configurer :

```python
AUTO_PROMOTE = True   # Promotion automatique en Production
AUTO_PROMOTE = False  # Promotion manuelle via MLflow UI
```

### Exploration vs Production

- **Exploration** : Testez différents hyperparamètres dans le notebook
- **Production** : Une fois satisfait, utilisez `train.py` pour l'automatisation

### Visualisations

Le notebook inclut :
- Pairplots pour les relations entre features
- Matrices de corrélation
- Matrices de confusion
- Comparaisons de performances

## 🔄 Intégration CI/CD

Pour la production, préférez le script `src/train/train.py` qui peut être :
- Exécuté depuis CI/CD (GitHub Actions)
- Planifié avec cron/scheduled tasks
- Intégré dans des pipelines MLOps

Les notebooks sont parfaits pour :
- Développement et expérimentation
- Formation et démonstrations
- Analyses ad-hoc

## 📚 Ressources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

---

**🎓 Projet Simplon France - MLOps 2026**
