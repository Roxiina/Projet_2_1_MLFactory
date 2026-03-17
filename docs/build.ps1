# Script de génération de documentation pour Windows PowerShell

Write-Host "🚀 Génération de la documentation ML Factory" -ForegroundColor Green
Write-Host ""

# Vérifier que nous sommes dans le bon dossier
if (-not (Test-Path "conf.py")) {
    Write-Host "❌ Erreur: Ce script doit être exécuté depuis le dossier docs/" -ForegroundColor Red
    exit 1
}

# Vérifier les dépendances
Write-Host "📦 Vérification des dépendances..." -ForegroundColor Cyan
if (-not (Get-Command sphinx-build -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  Sphinx n'est pas installé. Installation..." -ForegroundColor Yellow
    pip install -e "..[docs]"
}

# Nettoyer les anciens builds
Write-Host "🧹 Nettoyage des anciens builds..." -ForegroundColor Cyan
if (Test-Path "_build") {
    Remove-Item -Recurse -Force "_build"
}

# Générer la documentation
Write-Host "📝 Génération HTML..." -ForegroundColor Cyan
& make.bat html

# Vérifier les warnings
Write-Host ""
Write-Host "⚠️  Vérification des warnings..." -ForegroundColor Cyan
$warnings = & make.bat html 2>&1 | Select-String -Pattern "warning" -CaseSensitive:$false
if ($warnings) {
    Write-Host "⚠️  $($warnings.Count) warning(s) détecté(s)" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
} else {
    Write-Host "✅ Aucun warning détecté" -ForegroundColor Green
}

# Vérifier les liens (optionnel, peut être lent)
$verifyLinks = Read-Host "🔗 Vérifier les liens externes? (y/N)"
if ($verifyLinks -eq "y" -or $verifyLinks -eq "Y") {
    Write-Host "🔍 Vérification des liens..." -ForegroundColor Cyan
    & make.bat linkcheck
}

# Succès
Write-Host ""
Write-Host "✅ Documentation générée avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Localisation: _build\html\index.html" -ForegroundColor Cyan
Write-Host ""

# Proposer d'ouvrir
$openBrowser = Read-Host "🚀 Ouvrir dans le navigateur? (y/N)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "_build\html\index.html"
}
