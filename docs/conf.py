# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ML Factory"
copyright = "2026, Simplon France"
author = "Simplon France"
release = "0.1.0"
version = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Génération automatique de la documentation
    "sphinx.ext.napoleon",  # Support des docstrings Google et NumPy
    "sphinx.ext.viewcode",  # Liens vers le code source
    "sphinx.ext.intersphinx",  # Liens vers d'autres documentations
    "sphinx.ext.todo",  # Support des TODOs
    "sphinx.ext.coverage",  # Couverture de la documentation
    "sphinx.ext.githubpages",  # Support GitHub Pages
    # "sphinx_autodoc_typehints",  # Amélioration des type hints (nécessite: pip install sphinx-autodoc-typehints)
    # "myst_parser",  # Support Markdown (nécessite: pip install myst-parser)
]

# Configuration Napoleon pour les docstrings Google
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Configuration autodoc
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Support MyST (Markdown) - Décommentez si myst_parser est installé
# myst_enable_extensions = [
#     "colon_fence",
#     "deflist",
#     "substitution",
#     "tasklist",
# ]

# Templates path
templates_path = ["_templates"]

# Patterns to exclude
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Source suffix
source_suffix = {
    ".rst": "restructuredtext",
    # ".md": "markdown",  # Décommentez si myst_parser est installé
}

# Master document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Theme options
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_title = f"{project} v{release}"
html_short_title = project
html_logo = None
html_favicon = None

# Additional HTML context
html_context = {
    "display_github": True,
    "github_user": "simplon-france",
    "github_repo": "ml-factory",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# Output file base name for HTML help builder
htmlhelp_basename = "MLFactorydoc"

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "10pt",
}

latex_documents = [
    (
        master_doc,
        "MLFactory.tex",
        "ML Factory Documentation",
        "Simplon France",
        "manual",
    ),
]

# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, "mlfactory", "ML Factory Documentation", [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "MLFactory",
        "ML Factory Documentation",
        author,
        "MLFactory",
        "MLOps Zero-Downtime Deployment Project",
        "Miscellaneous",
    ),
]

# -- Options for Intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
    "mlflow": ("https://mlflow.org/docs/latest/", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
    "streamlit": ("https://docs.streamlit.io/", None),
}

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True

# -- Options for coverage extension ------------------------------------------

coverage_write_headline = True
coverage_show_missing_items = True
