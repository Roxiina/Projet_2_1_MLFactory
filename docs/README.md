# 🏭 ML Factory - Documentation Complète

Bienvenue dans la documentation du projet **ML Factory** !

## 📚 Navigation Rapide

### Pour les Utilisateurs
- **[Guide d'Installation](user-guide/installation.rst)** - Installation complète du projet
- **[Démarrage Rapide](user-guide/quickstart.rst)** - Opérationnel en 5 minutes
- **[Dépannage](user-guide/troubleshooting.rst)** - Solutions aux problèmes courants

### Pour les Développeurs
- **[Architecture](dev-guide/architecture.rst)** - Architecture détaillée du système
- **[Guide d'Entraînement](dev-guide/training.rst)** - Personnaliser l'entraînement des modèles
- **[Guide de Déploiement](dev-guide/deployment.rst)** - Déployer en production

### Référence API
- **[Module Training](api/training.rst)** - API d'entraînement
- **[Module Serving](api/serving.rst)** - API de prédiction (FastAPI)
- **[Module Frontend](api/frontend.rst)** - Interface utilisateur (Streamlit)

## 🚀 Générer la Documentation

### Installation des Dépendances

```bash
# Avec UV (recommandé)
uv pip install -e ".[docs]"

# Ou avec pip
pip install -e ".[docs]"
```

### Build Local

```bash
# Aller dans le dossier docs
cd docs

# Générer HTML
make html

# Ouvrir dans le navigateur
# Windows:
start _build/html/index.html

# Linux/MacOS:
open _build/html/index.html
```

### Build PDF (Nécessite LaTeX)

```bash
cd docs
make latexpdf
```

### Nettoyage

```bash
cd docs
make clean
```

## 🌐 Documentation en Ligne

La documentation est automatiquement déployée sur **GitHub Pages** à chaque push sur `main`.

**URL:** https://simplon-france.github.io/ml-factory/

## ✍️ Contribuer à la Documentation

### Format reStructuredText

La documentation utilise le format `.rst` (reStructuredText).

**Exemple:**

```rst
Titre Principal
===============

Sous-titre
----------

* Liste item 1
* Liste item 2

.. code-block:: python

   def hello():
       print("Hello World")

:doc:`lien-vers-autre-page`
```

### Ajouter une Nouvelle Page

1. **Créer le fichier** `.rst` dans le bon dossier:
   - `user-guide/` pour les guides utilisateur
   - `dev-guide/` pour les guides développeur
   - `api/` pour la documentation API

2. **Ajouter dans le toctree** de `index.rst`:

```rst
.. toctree::
   :maxdepth: 2
   
   user-guide/ma-nouvelle-page
```

3. **Générer et vérifier:**

```bash
cd docs
make clean html
```

### DocStrings Python

Utiliser le format **Google** dans le code Python:

```python
def ma_fonction(param1: str, param2: int) -> bool:
    """Brève description de la fonction.
    
    Description plus détaillée si nécessaire.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre
    
    Returns:
        Description de ce qui est retourné
    
    Raises:
        ValueError: Quand param2 est négatif
    
    Examples:
        >>> ma_fonction("test", 42)
        True
    
    Note:
        Notes importantes pour les utilisateurs
    """
    pass
```

## 🔍 Vérification

### Vérifier les Warnings

```bash
cd docs
make html 2>&1 | grep WARNING
```

### Vérifier les Liens

```bash
cd docs
make linkcheck
```

### Vérifier la Couverture

```bash
cd docs
make coverage
cat _build/coverage/python.txt
```

## 📦 Extensions Sphinx Utilisées

- `sphinx.ext.autodoc` - Génération auto depuis docstrings
- `sphinx.ext.napoleon` - Support docstrings Google/NumPy
- `sphinx.ext.viewcode` - Liens vers code source
- `sphinx.ext.intersphinx` - Liens vers autres docs
- `sphinx_autodoc_typehints` - Amélioration type hints
- `myst_parser` - Support Markdown
- `sphinx_rtd_theme` - Thème Read the Docs

## 🎨 Structure

```
docs/
├── conf.py                    # Configuration Sphinx
├── index.rst                  # Page d'accueil
├── Makefile                   # Commandes build (Linux/Mac)
├── make.bat                   # Commandes build (Windows)
├── .nojekyll                  # Config GitHub Pages
├── requirements.txt           # Dépendances Sphinx
├── README.md                  # Ce fichier
├── CONTRIBUTING_DOCS.md       # Guide de contribution
├── user-guide/
│   ├── installation.rst       # Installation complète
│   ├── quickstart.rst         # Démarrage rapide
│   └── troubleshooting.rst    # Dépannage
├── dev-guide/
│   ├── architecture.rst       # Architecture détaillée
│   ├── training.rst           # Guide d'entraînement
│   └── deployment.rst         # Déploiement production
└── api/
    ├── training.rst           # Référence API training
    ├── serving.rst            # Référence API serving
    └── frontend.rst           # Référence API frontend
```

## 🤖 GitHub Actions

Le workflow `.github/workflows/docs.yml` déploie automatiquement:

1. Déclenché à chaque push sur `main`
2. Installe les dépendances avec `pip install -e ".[docs]"`
3. Build avec `make html`
4. Déploie sur GitHub Pages

**Configuration requise:**
- Settings → Pages → Source: "GitHub Actions"

## 📚 Ressources

- [Documentation Sphinx](https://www.sphinx-doc.org/)
- [Guide reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Google Docstring Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

## 🆘 Support

Pour des questions sur la documentation:

- 📖 Consultez [CONTRIBUTING_DOCS.md](CONTRIBUTING_DOCS.md)
- 🐛 Ouvrez une issue sur [GitHub](https://github.com/simplon-france/ml-factory/issues)
- 💬 Contactez l'équipe Simplon France

## ⚡ Commandes Rapides

```bash
# Installation
uv pip install -e ".[docs]"

# Build
cd docs && make html

# Vérification
make linkcheck

# Nettoyage
make clean

# Build PDF
make latexpdf
```

---

**Bon développement! 🚀**
