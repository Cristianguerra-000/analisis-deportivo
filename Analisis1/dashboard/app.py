"""Dashboard interactivo para predicciones NBA con Streamlit."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.predictor import NBAPredictor
from src.features.feature_engineering import NBAFeatureEngineer


# Configuración de la página
st.set_page_config(
    page_title="NBA Predictor Pro",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .prediction-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    """Carga el modelo entrenado."""
    model_path = Path("models/nba_predictor_baseline.joblib")
    if model_path.exists():
        predictor = NBAPredictor()
        predictor.load(str(model_path))
        return predictor
    return None


@st.cache_data
def load_data():
    """Carga los datos procesados."""
    data_path = Path("data/processed/games_with_features.parquet")
    if data_path.exists():
        return pd.read_parquet(data_path)
    return None


def main():
    # Header
    st.markdown('<div class="main-header">🏀 NBA Predictor Pro</div>', unsafe_allow_html=True)
    st.markdown("### Sistema Avanzado de Análisis y Predicción de Partidos NBA")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuración")
    page = st.sidebar.selectbox(
        "Selecciona una vista",
        ["🎯 Predicciones", "📊 Análisis de Datos", "📈 Métricas del Modelo", "ℹ️ Acerca de"]
    )
    
    # Cargar datos y modelo
    df = load_data()
    predictor = load_model()
    
    if df is None:
        st.error("❌ No se encontraron datos procesados. Ejecuta primero los scripts de procesamiento.")
        st.code("python scripts/download_nba_data.py")
        st.code("python scripts/process_features.py")
        return
    
    if predictor is None and page == "🎯 Predicciones":
        st.error("❌ No se encontró el modelo entrenado. Ejecuta primero el script de entrenamiento.")
        st.code("python scripts/train_models.py")
        return
    
    # Páginas
    if page == "🎯 Predicciones":
        show_predictions_page(df, predictor)
    elif page == "📊 Análisis de Datos":
        show_analysis_page(df)
    elif page == "📈 Métricas del Modelo":
        show_metrics_page(df, predictor)
    else:
        show_about_page()


def show_predictions_page(df, predictor):
    """Página de predicciones interactivas."""
    st.header("🎯 Hacer Predicciones")
    
    # Obtener equipos únicos
    teams = sorted(pd.concat([df['HOME_TEAM_NAME'], df['AWAY_TEAM_NAME']]).unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Equipo Local")
        home_team = st.selectbox("Selecciona equipo local", teams, key="home")
    
    with col2:
        st.subheader("✈️ Equipo Visitante")
        away_team = st.selectbox("Selecciona equipo visitante", 
                                 [t for t in teams if t != home_team], key="away")
    
    if st.button("🔮 Predecir Resultado", type="primary", use_container_width=True):
        with st.spinner("Calculando predicción..."):
            # Obtener últimas estadísticas de los equipos
            home_stats = get_latest_team_stats(df, home_team, is_home=True)
            away_stats = get_latest_team_stats(df, away_team, is_home=False)
            
            # Combinar features
            features = {**home_stats, **away_stats}
            
            # Predecir
            prediction = predictor.predict_game(home_team, away_team, features)
            
            # Mostrar resultados
            show_prediction_results(prediction)


def get_latest_team_stats(df, team_name, is_home=True):
    """Obtiene las últimas estadísticas de un equipo."""
    prefix = "HOME" if is_home else "AWAY"
    team_col = f"{prefix}_TEAM_NAME"
    
    # Últimos partidos del equipo
    team_games = df[df[team_col] == team_name].tail(5)
    
    if len(team_games) == 0:
        # Valores por defecto
        stats = {
            f'{prefix}_ELO_BEFORE': 1500,
            f'{prefix}_PTS_ROLL_5': 110,
            f'{prefix}_FG_PCT_ROLL_5': 0.45,
            f'{prefix}_FG3_PCT_ROLL_5': 0.35,
            f'{prefix}_REB_ROLL_5': 45,
            f'{prefix}_AST_ROLL_5': 25,
            f'{prefix}_TOV_ROLL_5': 14,
            f'{prefix}_PTS_ROLL_10': 110,
            f'{prefix}_REST_DAYS': 2,
            f'{prefix}_BACK_TO_BACK': 0,
            f'{prefix}_WIN_STREAK': 0,
            f'{prefix}_WIN_PCT': 0.5,
        }
    else:
        latest = team_games.iloc[-1]
        stats = {
            f'{prefix}_ELO_BEFORE': latest.get(f'{prefix}_ELO_AFTER', 1500),
            f'{prefix}_PTS_ROLL_5': latest.get(f'{prefix}_PTS_ROLL_5', 110),
            f'{prefix}_FG_PCT_ROLL_5': latest.get(f'{prefix}_FG_PCT_ROLL_5', 0.45),
            f'{prefix}_FG3_PCT_ROLL_5': latest.get(f'{prefix}_FG3_PCT_ROLL_5', 0.35),
            f'{prefix}_REB_ROLL_5': latest.get(f'{prefix}_REB_ROLL_5', 45),
            f'{prefix}_AST_ROLL_5': latest.get(f'{prefix}_AST_ROLL_5', 25),
            f'{prefix}_TOV_ROLL_5': latest.get(f'{prefix}_TOV_ROLL_5', 14),
            f'{prefix}_PTS_ROLL_10': latest.get(f'{prefix}_PTS_ROLL_10', 110),
            f'{prefix}_REST_DAYS': 2,  # Valor por defecto
            f'{prefix}_BACK_TO_BACK': 0,
            f'{prefix}_WIN_STREAK': latest.get(f'{prefix}_WIN_STREAK', 0),
            f'{prefix}_WIN_PCT': latest.get(f'{prefix}_WIN_PCT', 0.5),
        }
    
    # Calcular ELO_DIFF
    if is_home:
        stats['ELO_DIFF'] = stats['HOME_ELO_BEFORE'] - 1500  # Se actualizará después
    
    return stats


def show_prediction_results(prediction):
    """Muestra los resultados de la predicción de forma visual."""
    st.markdown("---")
    st.subheader("📊 Resultados de la Predicción")
    
    # Probabilidades
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
        st.metric(
            label=f"🏠 {prediction['home_team']}",
            value=f"{prediction['home_win_probability']*100:.1f}%",
            delta="Probabilidad de Victoria"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
        st.metric(
            label=f"✈️ {prediction['away_team']}",
            value=f"{prediction['away_win_probability']*100:.1f}%",
            delta="Probabilidad de Victoria"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico de probabilidades
    fig = go.Figure(data=[
        go.Bar(
            x=[prediction['home_team'], prediction['away_team']],
            y=[prediction['home_win_probability'], prediction['away_win_probability']],
            marker_color=['#1f77b4', '#ff7f0e'],
            text=[f"{prediction['home_win_probability']*100:.1f}%", 
                  f"{prediction['away_win_probability']*100:.1f}%"],
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Probabilidades de Victoria",
        yaxis_title="Probabilidad",
        yaxis=dict(tickformat='.0%'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Marcador predicho
    st.markdown("### 🎯 Marcador Predicho")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.metric(
            label=prediction['home_team'],
            value=f"{prediction['predicted_home_score']:.0f}",
        )
    
    with col2:
        st.markdown("### vs")
    
    with col3:
        st.metric(
            label=prediction['away_team'],
            value=f"{prediction['predicted_away_score']:.0f}",
        )
    
    # Detalles adicionales
    st.markdown("### 📈 Detalles Adicionales")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Margen Predicho", f"{abs(prediction['predicted_margin']):.1f} puntos")
    
    with col2:
        st.metric("Total de Puntos", f"{prediction['predicted_total']:.0f}")


def show_analysis_page(df):
    """Página de análisis de datos."""
    st.header("📊 Análisis de Datos NBA")
    
    # Estadísticas generales
    st.subheader("📈 Estadísticas Generales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Partidos", f"{len(df):,}")
    
    with col2:
        st.metric("Puntos Promedio (Local)", f"{df['HOME_PTS'].mean():.1f}")
    
    with col3:
        st.metric("Puntos Promedio (Visitante)", f"{df['AWAY_PTS'].mean():.1f}")
    
    with col4:
        st.metric("% Victoria Local", f"{df['HOME_WL'].mean()*100:.1f}%")
    
    # Distribución de puntos
    st.subheader("📊 Distribución de Puntos")
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df['HOME_PTS'], name='Local', opacity=0.7))
    fig.add_trace(go.Histogram(x=df['AWAY_PTS'], name='Visitante', opacity=0.7))
    fig.update_layout(
        title="Distribución de Puntos por Equipo",
        xaxis_title="Puntos",
        yaxis_title="Frecuencia",
        barmode='overlay',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Total de puntos
    st.subheader("🔢 Total de Puntos por Partido")
    
    fig = px.histogram(df, x='TOTAL_PTS', nbins=50,
                       title="Distribución del Total de Puntos")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Ventaja de local
    st.subheader("🏠 Análisis de Ventaja de Local")
    
    home_advantage = df['POINT_DIFF'].mean()
    st.metric("Ventaja Promedio de Local", f"{home_advantage:.2f} puntos")
    
    # Evolución temporal
    if 'GAME_DATE' in df.columns:
        st.subheader("📅 Evolución Temporal")
        
        df_temp = df.copy()
        df_temp['GAME_DATE'] = pd.to_datetime(df_temp['GAME_DATE'])
        df_monthly = df_temp.groupby(df_temp['GAME_DATE'].dt.to_period('M')).agg({
            'HOME_PTS': 'mean',
            'AWAY_PTS': 'mean',
            'TOTAL_PTS': 'mean'
        }).reset_index()
        df_monthly['GAME_DATE'] = df_monthly['GAME_DATE'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_monthly['GAME_DATE'], y=df_monthly['HOME_PTS'],
                                name='Puntos Local', mode='lines+markers'))
        fig.add_trace(go.Scatter(x=df_monthly['GAME_DATE'], y=df_monthly['AWAY_PTS'],
                                name='Puntos Visitante', mode='lines+markers'))
        fig.update_layout(
            title="Evolución Mensual de Puntos Promedio",
            xaxis_title="Mes",
            yaxis_title="Puntos Promedio",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_metrics_page(df, predictor):
    """Página de métricas del modelo."""
    st.header("📈 Métricas del Modelo")
    
    st.info("🔄 Evaluando modelo en el conjunto de test...")
    
    # Preparar datos
    X, y_win, y_margin, y_total = predictor.prepare_features(df)
    
    # Split temporal
    split_idx = int(len(X) * 0.8)
    X_test = X.iloc[split_idx:]
    y_win_test = y_win.iloc[split_idx:]
    y_margin_test = y_margin.iloc[split_idx:]
    y_total_test = y_total.iloc[split_idx:]
    
    # Evaluar
    X_test_scaled = predictor.scaler.transform(X_test)
    metrics = predictor.evaluate(X_test_scaled, y_win_test, y_margin_test, y_total_test)
    
    # Mostrar métricas
    st.subheader("🎯 Modelo de Predicción de Victoria")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accuracy", f"{metrics['win_accuracy']:.3f}")
    with col2:
        st.metric("Log Loss", f"{metrics['win_log_loss']:.3f}")
    with col3:
        st.metric("Brier Score", f"{metrics['win_brier_score']:.3f}")
    with col4:
        st.metric("ROC AUC", f"{metrics['win_roc_auc']:.3f}")
    
    st.subheader("📏 Modelo de Margen de Puntos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("MAE", f"{metrics['margin_mae']:.2f} puntos")
    with col2:
        st.metric("R²", f"{metrics['margin_r2']:.3f}")
    
    st.subheader("🔢 Modelo de Total de Puntos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("MAE", f"{metrics['total_mae']:.2f} puntos")
    with col2:
        st.metric("R²", f"{metrics['total_r2']:.3f}")


def show_about_page():
    """Página informativa."""
    st.header("ℹ️ Acerca del Sistema")
    
    st.markdown("""
    ## 🏀 NBA Predictor Pro
    
    Sistema avanzado de análisis estadístico y modelado probabilístico para predecir resultados 
    de partidos de la NBA.
    
    ### 🎯 Características
    
    - **Predicciones probabilísticas** de victoria, margen y total de puntos
    - **Features avanzadas**: ELO dinámico, rolling statistics, análisis de descanso
    - **Modelos calibrados** con validación temporal
    - **Dashboard interactivo** para exploración de datos
    
    ### 🔧 Tecnologías Utilizadas
    
    - **Python 3.10+**
    - **scikit-learn**: Modelos de Machine Learning
    - **Pandas & NumPy**: Procesamiento de datos
    - **Streamlit**: Dashboard interactivo
    - **Plotly**: Visualizaciones
    - **nba_api**: Datos de la NBA
    
    ### 📊 Metodología
    
    1. **Recolección de datos**: API oficial de la NBA
    2. **Feature Engineering**: Creación de 30+ features predictivas
    3. **Modelado**: Ensemble de modelos calibrados
    4. **Evaluación**: Backtesting temporal con métricas probabilísticas
    
    ### ⚠️ Disclaimer
    
    Este sistema es únicamente para **análisis educativo y estadístico**. No debe ser 
    utilizado para actividades de apuestas comerciales.
    
    ---
    
    **Desarrollado**: Noviembre 2025  
    **Versión**: 0.1.0
    """)


if __name__ == "__main__":
    main()
