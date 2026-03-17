Guide de Génération de la Documentation
========================================

Ce guide explique comment générer et contribuer à la documentation Sphinx.

🔧 Installation des Dépendances
-------------------------------

Avec UV (Recommandé)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv pip install -e ".[docs]"

Avec Pip
~~~~~~~~

.. code-block:: bash

   pip install -e ".[docs]"

📝 Génération de la Documentation
---------------------------------

HTML (Local)
~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make html

   # Ouvrir dans le navigateur
   # Windows:
   start _build/html/index.html
   
   # Linux/MacOS:
   open _build/html/index.html

PDF (LaTeX requis)
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make latexpdf

Nettoyage
~~~~~~~~~

.. code-block:: bash

   cd docs
   make clean

📖 Structure de la Documentation
--------------------------------

.. code-block:: text

   docs/
   ├── conf.py              # Configuration Sphinx
   ├── index.rst            # Page d'accueil
   ├── Makefile             # Build automation (Linux/Mac)
   ├── make.bat             # Build automation (Windows)
   ├── api/                 # Documentation de l'API
   │   ├── training.rst
   │   ├── serving.rst
   │   └── frontend.rst
   ├── user-guide/          # Guides utilisateur
   │   ├── installation.rst
   │   ├── quickstart.rst
   │   ├── validation.rst
   │   └── troubleshooting.rst
   └── dev-guide/           # Guides développeur
       ├── architecture.rst
       ├── api-reference.rst
       ├── training.rst
       └── deployment.rst

✍️ Écrire de la Documentation
-----------------------------

Format reStructuredText
~~~~~~~~~~~~~~~~~~~~~~~

La documentation utilise le format reStructuredText (.rst):

**Titres:**

.. code-block:: rst

   Titre Niveau 1
   ==============

   Titre Niveau 2
   --------------

   Titre Niveau 3
   ~~~~~~~~~~~~~~

**Listes:**

.. code-block:: rst

   * Item 1
   * Item 2
     
     * Sous-item
   
   1. Élément numéroté
   2. Autre élément

**Code:**

.. code-block:: rst

   .. code-block:: python

      def hello():
          print("Hello World")

**Liens:**

.. code-block:: rst

   `Texte du lien <https://example.com>`_
   
   :doc:`autre-page`
   :ref:`section-label`

Autodoc avec Sphinx
~~~~~~~~~~~~~~~~~~~

Pour documenter automatiquement du code Python:

.. code-block:: rst

   .. automodule:: train.train
      :members:
      :undoc-members:
      :show-inheritance:

   .. autofunction:: train.train.train_model

   .. autoclass:: api.main.IrisFeatures
      :members:

Format des DocStrings
~~~~~~~~~~~~~~~~~~~~~

Utiliser le format Google pour les docstrings:

.. code-block:: python

   def ma_fonction(param1, param2):
       """Brève description de la fonction.
       
       Description plus détaillée si nécessaire, peut s'étendre
       sur plusieurs lignes.
       
       Args:
           param1 (str): Description du premier paramètre
           param2 (int): Description du deuxième paramètre
       
       Returns:
           bool: Description de ce qui est retourné
       
       Raises:
           ValueError: Quand param2 est négatif
       
       Examples:
           >>> ma_fonction("test", 42)
           True
       
       Note:
           Notes importantes pour les utilisateurs
       """
       pass

🚀 Déploiement sur GitHub Pages
-------------------------------

Automatique via GitHub Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le workflow ``.github/workflows/docs.yml`` déploie automatiquement:

1. À chaque push sur ``main``
2. Génère la documentation HTML
3. Déploie sur GitHub Pages

**Configuration requise:**

1. Dans les paramètres du repository GitHub:
   
   * Settings → Pages
   * Source: "GitHub Actions"

2. Le workflow se déclenche automatiquement

Manuel
~~~~~~

.. code-block:: bash

   # Générer la documentation
   cd docs
   make html

   # Copier vers un repository gh-pages
   cp -r _build/html/* /path/to/gh-pages-repo/

   # Commit et push
   cd /path/to/gh-pages-repo/
   git add .
   git commit -m "Update documentation"
   git push

🔍 Vérification de la Documentation
-----------------------------------

Vérifier les Warnings
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make html 2>&1 | grep WARNING

**Types de warnings courants:**

* Références manquantes
* Liens cassés
* Docstrings incomplètes
* Fichiers non inclus

Vérifier la Couverture
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make coverage

   # Voir le rapport
   cat _build/coverage/python.txt

Vérifier les Liens
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make linkcheck

📚 Bonnes Pratiques
-------------------

1. **Clarté**
   
   Écrire de manière concise et claire

2. **Exemples**
   
   Toujours inclure des exemples d'utilisation

3. **Code Blocks**
   
   Spécifier le langage pour la coloration syntaxique

4. **Cross-References**
   
   Utiliser ``:doc:``, ``:ref:`` pour lier les pages

5. **Versions**
   
   Documenter les changements de version

6. **Screenshots**
   
   Ajouter des captures d'écran si pertinent

7. **Tests**
   
   Vérifier que les exemples fonctionnent

🎨 Personnalisation du Thème
----------------------------

Le thème Read the Docs peut être personnalisé dans ``conf.py``:

.. code-block:: python

   html_theme_options = {
       'logo_only': False,
       'display_version': True,
       'prev_next_buttons_location': 'bottom',
       'style_external_links': True,
       'collapse_navigation': False,
       'sticky_navigation': True,
       'navigation_depth': 4,
   }

CSS Personnalisé
~~~~~~~~~~~~~~~~

Créer ``docs/_static/custom.css``:

.. code-block:: css

   .wy-nav-content {
       max-width: 1200px;
   }

Puis dans ``conf.py``:

.. code-block:: python

   html_static_path = ['_static']
   html_css_files = ['custom.css']

🔄 Workflow de Contribution
---------------------------

1. **Créer une branche**

   .. code-block:: bash

      git checkout -b docs/nouvelle-page

2. **Écrire/modifier la documentation**

   Créer ou éditer les fichiers ``.rst``

3. **Générer localement**

   .. code-block:: bash

      cd docs
      make html

4. **Vérifier**

   Ouvrir dans le navigateur et vérifier

5. **Commit**

   .. code-block:: bash

      git add docs/
      git commit -m "docs: Ajouter guide XYZ"

6. **Push et PR**

   .. code-block:: bash

      git push origin docs/nouvelle-page

7. **Review**

   Vérifier que le build GitHub Actions passe

📦 Extensions Sphinx Utilisées
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Extension
     - Description
   * - ``sphinx.ext.autodoc``
     - Génération auto depuis docstrings
   * - ``sphinx.ext.napoleon``
     - Support docstrings Google/NumPy
   * - ``sphinx.ext.viewcode``
     - Liens vers code source
   * - ``sphinx.ext.intersphinx``
     - Liens vers autres docs
   * - ``sphinx.ext.todo``
     - Support des TODOs
   * - ``sphinx_autodoc_typehints``
     - Amélioration type hints
   * - ``myst_parser``
     - Support Markdown

🆘 Dépannage
------------

Erreur: "No module named 'X'"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Installer les dépendances manquantes
   uv pip install -e ".[docs]"

Erreur: "Sphinx-build not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Installer Sphinx
   uv pip install sphinx

Warnings de Références
~~~~~~~~~~~~~~~~~~~~~~

Vérifier que:

* Les modules sont dans le PYTHONPATH
* Les imports sont corrects
* Les fichiers .rst sont dans un toctree

Build Lent
~~~~~~~~~~

.. code-block:: bash

   # Build incrémental (plus rapide)
   make html

   # Build complet (propre)
   make clean html

📖 Ressources
-------------

* `Sphinx Documentation <https://www.sphinx-doc.org/>`_
* `reStructuredText Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
* `Google Docstring Style <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_
* `Read the Docs Theme <https://sphinx-rtd-theme.readthedocs.io/>`_
