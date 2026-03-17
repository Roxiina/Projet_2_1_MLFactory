#!/bin/bash
# Script de génération de documentation pour Linux/MacOS

set -e

echo "🚀 Génération de la documentation ML Factory"
echo ""

# Vérifier que nous sommes dans le bon dossier
if [ ! -f "conf.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le dossier docs/"
    exit 1
fi

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
if ! command -v sphinx-build &> /dev/null; then
    echo "⚠️  Sphinx n'est pas installé. Installation..."
    pip install -e "../[docs]"
fi

# Nettoyer les anciens builds
echo "🧹 Nettoyage des anciens builds..."
make clean

# Générer la documentation
echo "📝 Génération HTML..."
make html

# Vérifier les warnings
echo ""
echo "⚠️  Vérification des warnings..."
WARNINGS=$(make html 2>&1 | grep -i "warning" | wc -l)
if [ "$WARNINGS" -gt 0 ]; then
    echo "⚠️  $WARNINGS warning(s) détecté(s)"
    make html 2>&1 | grep -i "warning"
else
    echo "✅ Aucun warning détecté"
fi

# Vérifier les liens (optionnel, peut être lent)
read -p "🔗 Vérifier les liens externes? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Vérification des liens..."
    make linkcheck
fi

# Succès
echo ""
echo "✅ Documentation générée avec succès!"
echo ""
echo "📂 Localisation: _build/html/index.html"
echo ""
echo "🌐 Pour ouvrir dans le navigateur:"
echo "   Linux:   xdg-open _build/html/index.html"
echo "   MacOS:   open _build/html/index.html"
echo ""

# Proposer d'ouvrir
read -p "🚀 Ouvrir dans le navigateur? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open _build/html/index.html
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open _build/html/index.html
    fi
fi
