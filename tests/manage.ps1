# Script PowerShell pour gerer le projet ML Factory
# Usage: .\manage.ps1 [command]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$ProjectName = "ML Factory"
$Services = @("minio", "mlflow", "api", "front")

function Show-Help {
    Write-Host "`n[ML FACTORY] - Gestionnaire de Projet`n" -ForegroundColor Cyan
    Write-Host "Usage: .\manage.ps1 [command]`n"
    Write-Host "Commandes disponibles:"
    Write-Host "  start           Demarrer tous les services Docker" -ForegroundColor Green
    Write-Host "  stop            Arreter tous les services" -ForegroundColor Yellow
    Write-Host "  restart         Redemarrer tous les services" -ForegroundColor Blue
    Write-Host "  logs [service]  Afficher les logs (tous ou service specifique)" -ForegroundColor Magenta
    Write-Host "  status          Verifier l'etat des services" -ForegroundColor Cyan
    Write-Host "  clean           Arreter et supprimer les volumes [ATTENTION: supprime les donnees]" -ForegroundColor Red
    Write-Host "  train           Lancer l'entrainement du modele (script)" -ForegroundColor Green
    Write-Host "  notebook        Lancer Jupyter Lab (entrainement interactif)" -ForegroundColor Magenta
    Write-Host "  open [service]  Ouvrir un service dans le navigateur" -ForegroundColor Cyan
    Write-Host "  help            Afficher cette aide`n"
    Write-Host "Services disponibles:"
    Write-Host "  - mlflow  (http://localhost:5000)"
    Write-Host "  - minio   (http://localhost:9001)"
    Write-Host "  - api     (http://localhost:8000/docs)"
    Write-Host "  - front   (http://localhost:8501)`n"
}

function Start-Services {
    Write-Host "`n[START] Demarrage des services..." -ForegroundColor Green
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[OK] Services demarres avec succes!" -ForegroundColor Green
        Write-Host "`nAccès aux services:"
        Write-Host "  - MLflow UI:      http://localhost:5000" -ForegroundColor Cyan
        Write-Host "  - MinIO Console:  http://localhost:9001" -ForegroundColor Cyan
        Write-Host "  - FastAPI Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "  - Streamlit App:  http://localhost:8501" -ForegroundColor Cyan
        Write-Host "`nUtilisez '.\manage.ps1 status' pour verifier l'etat`n"
    } else {
        Write-Host "`n[ERREUR] Erreur lors du demarrage des services" -ForegroundColor Red
    }
}

function Stop-Services {
    Write-Host "`n[STOP] Arret des services..." -ForegroundColor Yellow
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[OK] Services arretes avec succes!`n" -ForegroundColor Green
    } else {
        Write-Host "`n[ERREUR] Erreur lors de l'arret des services`n" -ForegroundColor Red
    }
}

function Restart-Services {
    Write-Host "`n[RESTART] Redemarrage des services..." -ForegroundColor Blue
    docker-compose restart
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[OK] Services redemarres avec succes!`n" -ForegroundColor Green
    } else {
        Write-Host "`n[ERREUR] Erreur lors du redemarrage des services`n" -ForegroundColor Red
    }
}

function Show-Logs {
    param([string]$Service)
    
    if ($Service) {
        Write-Host "`n[LOGS] Logs du service: $Service" -ForegroundColor Magenta
        docker-compose logs -f $Service
    } else {
        Write-Host "`n[LOGS] Logs de tous les services (Ctrl+C pour quitter)" -ForegroundColor Magenta
        docker-compose logs -f
    }
}

function Show-Status {
    Write-Host "`n[STATUS] Etat des services:`n" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
}

function Clean-All {
    Write-Host "`n[ATTENTION] Cette commande va supprimer tous les volumes et donnees!" -ForegroundColor Red
    $confirmation = Read-Host "Etes-vous sur? (oui/non)"
    
    if ($confirmation -eq "oui") {
        Write-Host "`n[CLEAN] Nettoyage en cours..." -ForegroundColor Yellow
        docker-compose down -v
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n[OK] Nettoyage termine!`n" -ForegroundColor Green
        } else {
            Write-Host "`n[ERREUR] Erreur lors du nettoyage`n" -ForegroundColor Red
        }
    } else {
        Write-Host "`n[ANNULE] Operation annulee`n" -ForegroundColor Yellow
    }
}

function Start-Training {
    Write-Host "`n[TRAIN] Lancement de l'entrainement...`n" -ForegroundColor Green
    
    # Verifier si les dependances sont installees
    $pythonPath = Get-Command python -ErrorAction SilentlyContinue
    
    if (-not $pythonPath) {
        Write-Host "[ERREUR] Python n'est pas installe ou pas dans le PATH" -ForegroundColor Red
        return
    }
    
    # Aller dans le dossier train
    Push-Location "src/train"
    
    Write-Host "[INSTALL] Verification des dependances..." -ForegroundColor Cyan
    python -m pip install -q mlflow scikit-learn pandas numpy python-dotenv
    
    Write-Host "[RUN] Execution du script d'entrainement...`n" -ForegroundColor Green
    python train.py
    
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[OK] Entrainement termine!`n" -ForegroundColor Green
    } else {
        Write-Host "`n[ERREUR] Erreur lors de l'entrainement`n" -ForegroundColor Red
    }
}

function Start-Notebook {
    Write-Host "`n[NOTEBOOK] Lancement de Jupyter Lab...`n" -ForegroundColor Magenta
    
    # Verifier si Python est installe
    $pythonPath = Get-Command python -ErrorAction SilentlyContinue
    
    if (-not $pythonPath) {
        Write-Host "[ERREUR] Python n'est pas installe ou pas dans le PATH" -ForegroundColor Red
        return
    }
    
    # Verifier si Jupyter est installe
    $jupyterCheck = python -c "import jupyterlab" 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INSTALL] Installation de Jupyter Lab..." -ForegroundColor Cyan
        Push-Location "notebooks"
        python -m pip install -r requirements.txt
        Pop-Location
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`n[ERREUR] Erreur lors de l'installation de Jupyter`n" -ForegroundColor Red
            return
        }
    }
    
    # Lancer Jupyter Lab
    Write-Host "[START] Demarrage de Jupyter Lab sur http://localhost:8888" -ForegroundColor Green
    Write-Host "   (Ctrl+C pour arreter)`n" -ForegroundColor Yellow
    
    Push-Location "notebooks"
    python -m jupyter lab --no-browser
    Pop-Location
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
        Write-Host "`n[OPEN] Ouverture de $Service ($url)...`n" -ForegroundColor Cyan
        Start-Process $url
    } elseif ($Service) {
        Write-Host "`n[ERREUR] Service inconnu: $Service" -ForegroundColor Red
        Write-Host "Services disponibles: mlflow, minio, api, front`n"
    } else {
        Write-Host "`n[OPEN] Ouverture de tous les services...`n" -ForegroundColor Cyan
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
    "notebook" { Start-Notebook }
    "open" { Open-Service -Service $args[0] }
    "help" { Show-Help }
    default {
        Write-Host "`n[ERREUR] Commande inconnue: $Command`n" -ForegroundColor Red
        Show-Help
    }
}
