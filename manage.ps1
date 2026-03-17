# Script PowerShell pour gérer le projet ML Factory
# Usage: .\manage.ps1 [command]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$ProjectName = "ML Factory"
$Services = @("minio", "mlflow", "api", "front")

function Show-Help {
    Write-Host "`n🏭 $ProjectName - Gestionnaire de Projet`n" -ForegroundColor Cyan
    Write-Host "Usage: .\manage.ps1 [command]`n"
    Write-Host "Commandes disponibles:"
    Write-Host "  start           Démarrer tous les services Docker" -ForegroundColor Green
    Write-Host "  stop            Arrêter tous les services" -ForegroundColor Yellow
    Write-Host "  restart         Redémarrer tous les services" -ForegroundColor Blue
    Write-Host "  logs [service]  Afficher les logs (tous ou service spécifique)" -ForegroundColor Magenta
    Write-Host "  status          Vérifier l'état des services" -ForegroundColor Cyan
    Write-Host "  clean           Arrêter et supprimer les volumes (⚠️  supprime les données)" -ForegroundColor Red
    Write-Host "  train           Lancer l'entraînement du modèle" -ForegroundColor Green
    Write-Host "  open [service]  Ouvrir un service dans le navigateur" -ForegroundColor Cyan
    Write-Host "  help            Afficher cette aide`n"
    Write-Host "Services disponibles:"
    Write-Host "  - mlflow  (http://localhost:5000)"
    Write-Host "  - minio   (http://localhost:9001)"
    Write-Host "  - api     (http://localhost:8000/docs)"
    Write-Host "  - front   (http://localhost:8501)`n"
}

function Start-Services {
    Write-Host "`n🚀 Démarrage des services..." -ForegroundColor Green
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Services démarrés avec succès!" -ForegroundColor Green
        Write-Host "`nAccès aux services:"
        Write-Host "  - MLflow UI:      http://localhost:5000" -ForegroundColor Cyan
        Write-Host "  - MinIO Console:  http://localhost:9001" -ForegroundColor Cyan
        Write-Host "  - FastAPI Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "  - Streamlit App:  http://localhost:8501" -ForegroundColor Cyan
        Write-Host "`nUtilisez '.\manage.ps1 status' pour vérifier l'état`n"
    } else {
        Write-Host "`n❌ Erreur lors du démarrage des services" -ForegroundColor Red
    }
}

function Stop-Services {
    Write-Host "`n🛑 Arrêt des services..." -ForegroundColor Yellow
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Services arrêtés avec succès!`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Erreur lors de l'arrêt des services`n" -ForegroundColor Red
    }
}

function Restart-Services {
    Write-Host "`n🔄 Redémarrage des services..." -ForegroundColor Blue
    docker-compose restart
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Services redémarrés avec succès!`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Erreur lors du redémarrage des services`n" -ForegroundColor Red
    }
}

function Show-Logs {
    param([string]$Service)
    
    if ($Service) {
        Write-Host "`n📋 Logs du service: $Service" -ForegroundColor Magenta
        docker-compose logs -f $Service
    } else {
        Write-Host "`n📋 Logs de tous les services (Ctrl+C pour quitter)" -ForegroundColor Magenta
        docker-compose logs -f
    }
}

function Show-Status {
    Write-Host "`n📊 État des services:`n" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
}

function Clean-All {
    Write-Host "`n⚠️  ATTENTION: Cette commande va supprimer tous les volumes et données!" -ForegroundColor Red
    $confirmation = Read-Host "Êtes-vous sûr? (oui/non)"
    
    if ($confirmation -eq "oui") {
        Write-Host "`n🧹 Nettoyage en cours..." -ForegroundColor Yellow
        docker-compose down -v
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Nettoyage terminé!`n" -ForegroundColor Green
        } else {
            Write-Host "`n❌ Erreur lors du nettoyage`n" -ForegroundColor Red
        }
    } else {
        Write-Host "`n❌ Opération annulée`n" -ForegroundColor Yellow
    }
}

function Start-Training {
    Write-Host "`n🔬 Lancement de l'entraînement...`n" -ForegroundColor Green
    
    # Vérifier si les dépendances sont installées
    $pythonPath = Get-Command python -ErrorAction SilentlyContinue
    
    if (-not $pythonPath) {
        Write-Host "❌ Python n'est pas installé ou pas dans le PATH" -ForegroundColor Red
        return
    }
    
    # Aller dans le dossier train
    Push-Location "src/train"
    
    Write-Host "📦 Vérification des dépendances..." -ForegroundColor Cyan
    python -m pip install -q mlflow scikit-learn pandas numpy python-dotenv
    
    Write-Host "🏃 Exécution du script d'entraînement...`n" -ForegroundColor Green
    python train.py
    
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Entraînement terminé!`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Erreur lors de l'entraînement`n" -ForegroundColor Red
    }
}

function Open-Service {
    param([string]$Service)
    
    $urls = @{
        "mlflow" = "http://localhost:5000"
        "minio" = "http://localhost:9001"
        "api" = "http://localhost:8000/docs"
        "front" = "http://localhost:8501"
    }
    
    if ($Service -and $urls.ContainsKey($Service)) {
        $url = $urls[$Service]
        Write-Host "`n🌐 Ouverture de $Service ($url)...`n" -ForegroundColor Cyan
        Start-Process $url
    } elseif ($Service) {
        Write-Host "`n❌ Service inconnu: $Service" -ForegroundColor Red
        Write-Host "Services disponibles: mlflow, minio, api, front`n"
    } else {
        Write-Host "`n🌐 Ouverture de tous les services...`n" -ForegroundColor Cyan
        foreach ($url in $urls.Values) {
            Start-Process $url
            Start-Sleep -Milliseconds 500
        }
    }
}

# Traitement de la commande
switch ($Command.ToLower()) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "logs" { Show-Logs -Service $args[0] }
    "status" { Show-Status }
    "clean" { Clean-All }
    "train" { Start-Training }
    "open" { Open-Service -Service $args[0] }
    "help" { Show-Help }
    default {
        Write-Host "`n❌ Commande inconnue: $Command`n" -ForegroundColor Red
        Show-Help
    }
}
