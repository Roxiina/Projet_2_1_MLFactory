"""Interface Streamlit pour tester le modèle de classification Iris.

Cette application fournit une interface web interactive pour:
- Visualiser la version du modèle actuellement en production
- Effectuer des prédictions individuelles avec saisie manuelle
- Charger et tester des données depuis un fichier CSV
- Afficher les probabilités de prédiction pour chaque classe

L'application communique avec l'API FastAPI pour obtenir les prédictions
et détecte automatiquement les changements de version du modèle grâce au
système de cache avec TTL (Time To Live).

Features:
    - **Badge de version dynamique**: Affiche la version du modèle en production
    - **Deux modes de saisie**: Manuelle (sliders) ou fichier CSV
    - **Visualisation des probabilités**: Graphiques et tableaux
    - **Rafraîchissement à la demande**: Bouton pour forcer le check de version
    - **Validation des prédictions**: Compare avec les vraies classes si disponibles

Environment Variables:
    API_URL: URL de l'API FastAPI (défaut: http://api:8000)
    MLFLOW_TRACKING_URI: URI du serveur MLflow (défaut: http://mlflow:5000)

Examples:
    Démarrage local::

        $ streamlit run app.py

    Avec configuration personnalisée::

        $ API_URL=http://localhost:8000 streamlit run app.py

Note:
    L'application utilise un cache avec TTL de 5 secondes pour les informations
    du modèle, permettant de détecter rapidement les mises à jour sans surcharger l'API.
"""

import os
import streamlit as st
import requests
import pandas as pd
from mlflow.tracking import MlflowClient
import mlflow
import plotly.graph_objects as go

# Configuration
API_URL = os.getenv("API_URL", "http://api:8000")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Configuration de la page
st.set_page_config(
    page_title="ML Factory - Iris Classifier",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé moderne
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Header avec gradient animé */
    .main-header {
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(120deg, #ffd89b 0%, #19547b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        animation: gradient 3s ease infinite;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.3rem;
        color: #ffffff;
        font-weight: 300;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Cards modernes avec glassmorphism */
    .glassmorphism-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .glassmorphism-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Metric cards avec gradients */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .metric-title {
        font-size: 0.9rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Badge de version animé */
    .version-badge {
        display: inline-block;
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.3rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(245, 87, 108, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Result card avec gradient */
    .prediction-result {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Success/Error cards modernisés */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 50px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tabs modernisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: white;
        font-weight: 600;
    }
    
    /* Sliders */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* Charts */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: white;
        padding: 2rem;
        margin-top: 3rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=5)
def get_model_info():
    """Récupère les informations du modèle depuis l'API avec cache.
    
    Cette fonction interroge l'endpoint /model-info de l'API pour obtenir
    les métadonnées du modèle actuellement en production. Les résultats
    sont mis en cache pendant 5 secondes pour éviter des requêtes excessives.
    
    Returns:
        dict or None: Dictionnaire contenant les informations du modèle:
            - model_name (str): Nom du modèle
            - model_version (str): Numéro de version
            - model_alias (str): Alias du modèle (ex: "Production")
            - run_id (str): ID du run MLflow
            - status (str): Statut du modèle
            - creation_timestamp (int): Timestamp de création
            
            Retourne None en cas d'erreur de connexion.
    
    Examples:
        >>> info = get_model_info()
        >>> if info:
        ...     print(f"Version: {info['model_version']}")
        Version: 2
    
    Note:
        Le TTL de 5 secondes permet à l'interface de détecter rapidement
        les changements de version tout en limitant la charge sur l'API.
    """
    try:
        response = requests.get(f"{API_URL}/model-info", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"⚠️ Erreur de connexion à l'API: {e}")
        return None


def get_api_health():
    """Vérifie l'état de santé de l'API.
    
    Envoie une requête à l'endpoint /health pour vérifier que l'API est
    accessible et opérationnelle, et que le modèle est chargé.
    
    Returns:
        tuple: Un tuple contenant:
            - is_healthy (bool): True si l'API répond avec succès (status 200)
            - health_data (dict or None): Données de santé retournées par l'API
                si succès, None sinon
    
    Examples:
        >>> is_healthy, data = get_api_health()
        >>> if is_healthy:
        ...     print(f"Modèle chargé: {data['model_loaded']}")
        Modèle chargé: True
    
    Note:
        Cette fonction est appelée au démarrage de l'application pour
        afficher un message d'état et arrêter l'exécution si l'API n'est
        pas disponible.
    """
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None


def predict(features):
    """Envoie une requête de prédiction à l'API.
    
    Transforme les features en format JSON compatible avec l'API et envoie
    une requête POST à l'endpoint /predict.
    
    Args:
        features (dict): Dictionnaire contenant les features:
            - "sepal length (cm)" (float): Longueur du sépale
            - "sepal width (cm)" (float): Largeur du sépale
            - "petal length (cm)" (float): Longueur du pétale
            - "petal width (cm)" (float): Largeur du pétale
    
    Returns:
        dict or None: Réponse de l'API contenant:
            - prediction (int): Classe prédite (0, 1, ou 2)
            - prediction_label (str): Nom de la classe
            - probabilities (dict): Probabilités par classe
            - model_version (str): Version du modèle utilisé
            - model_name (str): Nom du modèle
            
            Retourne None en cas d'erreur.
    
    Examples:
        >>> features = {
        ...     "sepal length (cm)": 5.1,
        ...     "sepal width (cm)": 3.5,
        ...     "petal length (cm)": 1.4,
        ...     "petal width (cm)": 0.2
        ... }
        >>> result = predict(features)
        >>> if result:
        ...     print(f"Classe prédite: {result['prediction_label']}")
        Classe prédite: Setosa
    
    Note:
        Les erreurs HTTP sont affichées via st.error() pour informer l'utilisateur.
    """
    try:
        payload = {
            "sepal_length": features["sepal length (cm)"],
            "sepal_width": features["sepal width (cm)"],
            "petal_length": features["petal length (cm)"],
            "petal_width": features["petal width (cm)"]
        }
        
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la prédiction: {e}")
        return None


# En-tête de l'application avec design moderne
st.markdown('<div class="main-header">🏭 ML Factory</div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">✨ Classification Iris avec Zero-Downtime Deployment ✨</p>', unsafe_allow_html=True)

# Vérification de la connexion API
is_healthy, health_info = get_api_health()

if is_healthy:
    st.markdown("""
        <div style="text-align: center; margin: 1rem 0;">
            <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                         padding: 0.5rem 1.5rem; border-radius: 50px; color: white;
                         font-weight: 600; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);">
                ✅ API Connectée & Opérationnelle
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Affichage des informations du modèle avec glassmorphism
    model_info = get_model_info()
    
    if model_info:
        st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="metric-title">🎯 Modèle</div>
                    <div class="metric-value">{model_info.get("model_name", "N/A")}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div class="metric-title">📦 Version</div>
                    <div class="metric-value">v{model_info.get("model_version", "N/A")}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div class="metric-title">🏷️ Alias</div>
                    <div class="metric-value">{model_info.get("model_alias", "N/A")}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div style="text-align: center; margin-top: 1.5rem;"><span class="version-badge">🚀 Version en Production: v{}</span></div>'.format(model_info.get("model_version", "N/A")), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                     padding: 1rem 2rem; border-radius: 20px; color: white; margin: 2rem 0;
                     box-shadow: 0 8px 25px rgba(238, 90, 111, 0.4);">
            <h3>❌ Impossible de se connecter à l'API</h3>
            <p>Vérifiez que les services Docker sont démarrés</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("---")

# Interface de prédiction avec design moderne
st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #667eea;">🔮 Faire une Prédiction</h2>', unsafe_allow_html=True)

# Deux modes: manuel ou depuis fichier
tab1, tab2 = st.tabs(["📝 Saisie Manuelle", "📁 Charger depuis Fichier"])

with tab1:
    st.subheader("Caractéristiques de la fleur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sepal_length = st.slider(
            "Longueur du Sépale (cm)",
            min_value=4.0,
            max_value=8.0,
            value=5.1,
            step=0.1
        )
        
        sepal_width = st.slider(
            "Largeur du Sépale (cm)",
            min_value=2.0,
            max_value=4.5,
            value=3.5,
            step=0.1
        )
    
    with col2:
        petal_length = st.slider(
            "Longueur du Pétale (cm)",
            min_value=1.0,
            max_value=7.0,
            value=1.4,
            step=0.1
        )
        
        petal_width = st.slider(
            "Largeur du Pétale (cm)",
            min_value=0.1,
            max_value=2.5,
            value=0.2,
            step=0.1
        )
    
    features_manual = {
        "sepal length (cm)": sepal_length,
        "sepal width (cm)": sepal_width,
        "petal length (cm)": petal_length,
        "petal width (cm)": petal_width
    }
    
    if st.button("🎯 Prédire", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyse en cours..."):
            result = predict(features_manual)
            
            if result:
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
                         padding: 2rem; border-radius: 20px; margin: 1.5rem 0;
                         box-shadow: 0 10px 30px rgba(142, 197, 252, 0.4);">
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 15px;
                             box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                            <h2 style="color: #667eea; margin: 0;">🌸 Espèce Prédite</h2>
                            <h1 style="color: #f5576c; font-size: 3rem; margin: 0.5rem 0;">{result['prediction_label']}</h1>
                            <p style="color: #666; font-size: 1.1rem;">
                                🔖 Modèle: <strong>Version {result['model_version']}</strong>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                             padding: 2rem; border-radius: 15px; text-align: center; color: white;
                             box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);">
                            <div style="font-size: 0.9rem; opacity: 0.9;">Classe</div>
                            <div style="font-size: 3rem; font-weight: 700;">{result['prediction']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Affichage des probabilités avec chart moderne
                if result.get('probabilities'):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<h3 style="text-align: center; color: #667eea;">📊 Probabilités par Classe</h3>', unsafe_allow_html=True)
                    
                    import plotly.graph_objects as go
                    
                    classes = list(result['probabilities'].keys())
                    values = list(result['probabilities'].values())
                    
                    # Graphique en barres moderne avec Plotly
                    fig = go.Figure(data=[
                        go.Bar(
                            x=classes,
                            y=values,
                            marker=dict(
                                color=values,
                                colorscale='Blues',
                                line=dict(color='white', width=2)
                            ),
                            text=[f"{v*100:.1f}%" for v in values],
                            textposition='auto',
                            hovertemplate='<b>%{x}</b><br>Probabilité: %{y:.2%}<extra></extra>'
                        )
                    ])
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Poppins", size=14, color='#667eea'),
                        xaxis=dict(title="Classe", gridcolor='rgba(255,255,255,0.3)'),
                        yaxis=dict(title="Probabilité", gridcolor='rgba(255,255,255,0.3)', tickformat='.0%'),
                        height=300,
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau des probabilités
                    prob_df = pd.DataFrame({
                        '🌸 Classe': classes,
                        '📊 Probabilité': [f"{v*100:.2f}%" for v in values]
                    })
                    st.dataframe(prob_df, use_container_width=True, hide_index=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<h3 style="color: #667eea;">📁 Charger des Données de Test</h3>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
             padding: 1rem; border-radius: 15px; margin: 1rem 0;">
            <p style="margin: 0; color: #666;">
                💡 Un fichier <code>iris_test.csv</code> est généré automatiquement lors de l'entraînement dans <code>data/</code>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Vérification des colonnes requises
            required_cols = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
            
            if all(col in df.columns for col in required_cols):
                st.success(f"✅ Fichier chargé: {len(df)} lignes")
                
                # Afficher les données
                st.dataframe(df.head(10), use_container_width=True)
                
                # Sélectionner une ligne
                row_idx = st.selectbox("Sélectionner une ligne pour prédiction", range(len(df)))
                
                selected_row = df.iloc[row_idx]
                
                # Afficher les features sélectionnées
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Sepal Length", f"{selected_row['sepal length (cm)']:.2f}")
                col2.metric("Sepal Width", f"{selected_row['sepal width (cm)']:.2f}")
                col3.metric("Petal Length", f"{selected_row['petal length (cm)']:.2f}")
                col4.metric("Petal Width", f"{selected_row['petal width (cm)']:.2f}")
                
                if st.button("🎯 Prédire cette ligne", type="primary", use_container_width=True):
                    features_file = {
                        "sepal length (cm)": float(selected_row['sepal length (cm)']),
                        "sepal width (cm)": float(selected_row['sepal width (cm)']),
                        "petal length (cm)": float(selected_row['petal length (cm)']),
                        "petal width (cm)": float(selected_row['petal width (cm)'])
                    }
                    
                    with st.spinner("🔄 Analyse en cours..."):
                        result = predict(features_file)
                        
                        if result:
                            st.markdown("""
                                <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                                     padding: 2rem; border-radius: 20px; margin: 1.5rem 0;
                                     box-shadow: 0 10px 30px rgba(168, 237, 234, 0.4);">
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                    <div style="background: white; padding: 1.5rem; border-radius: 15px;
                                         box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                                        <h2 style="color: #667eea; margin: 0;">🌸 Espèce Prédite</h2>
                                        <h1 style="color: #f5576c; font-size: 3rem; margin: 0.5rem 0;">{result['prediction_label']}</h1>
                                        <p style="color: #666; font-size: 1.1rem;">
                                            🔖 Modèle: <strong>Version {result['model_version']}</strong>
                                        </p>
                                """, unsafe_allow_html=True)
                                
                                # Afficher la vraie classe si disponible
                                if 'target' in df.columns:
                                    true_class = int(selected_row['target'])
                                    class_names = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}
                                    
                                    if result['prediction'] == true_class:
                                        st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                                                 color: white; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                                                🎯 Vraie classe: <strong>{class_names.get(true_class, true_class)}</strong>
                                                <br>✅ Prédiction Correcte!
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                                                 color: white; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                                                🎯 Vraie classe: <strong>{class_names.get(true_class, true_class)}</strong>
                                                <br>❌ Prédiction Incorrecte
                                            </div>
                                        """, unsafe_allow_html=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                         padding: 2rem; border-radius: 15px; text-align: center; color: white;
                                         box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                                        <div style="font-size: 0.9rem; opacity: 0.9;">Classe</div>
                                        <div style="font-size: 3rem; font-weight: 700;">{result['prediction']}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"❌ Le fichier doit contenir les colonnes: {', '.join(required_cols)}")
        
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # Fermeture glassmorphism-card

# Bouton de rafraîchissement avec design moderne
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Rafraîchir les Informations du Modèle", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Footer moderne
st.markdown("""
    <div class="footer">
        <h2 style="color: white; margin: 0;">🏭 ML Factory</h2>
        <p style="font-size: 1.2rem; margin: 0.5rem 0; opacity: 0.9;">
            Zero-Downtime ML Deployment Platform
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="opacity: 0.8; margin: 0;">
                ⚡ Mise à jour automatique sans redémarrage • 
                🔄 Hot-Reloading • 
                🚀 Production-Ready
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)
