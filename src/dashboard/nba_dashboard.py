"""
🏀 DASHBOARD NBA - Sistema de Predicciones Avanzadas

Dashboard especializado para NBA con:
- Predicciones con 3 modelos (72.6% accuracy)
- Análisis histórico completo
- Gráficos interactivos con Plotly
- Sistema ELO + 99 features avanzadas
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.abspath('.'))

from src.models.nba_predictor import NBAPredictor

# Configuración de página
st.set_page_config(
    page_title="🏀 Predicciones NBA Avanzadas",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .live-indicator {
        background-color: #ff4757;
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos NBA
@st.cache_data(ttl=300)  # Cache 5 minutos
def load_nba_data():
    """Carga datos NBA del sistema existente"""
    try:
        # Intentar cargar datos con features completas
        df = pd.read_parquet('data/nba_games_features.parquet')
        st.info("✅ Datos avanzados cargados (4,192 partidos con 99 features)")
    except FileNotFoundError:
        try:
            # Fallback a datos básicos
            df = pd.read_parquet('data/nba_games.parquet')
            st.warning("⚠️ Usando datos básicos (1,000 partidos)")
        except FileNotFoundError:
            st.error("❌ No se encontraron datos NBA")
            return pd.DataFrame()

    return df

# Función para cargar predictor
@st.cache_resource
def load_nba_predictor():
    """Carga el modelo entrenado de NBA"""
    try:
        # Usar ruta absoluta basada en el directorio del archivo actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        model_path = os.path.join(project_root, 'models', 'nba_predictor.joblib')

        predictor = NBAPredictor.load_model(model_path)
        return predictor
    except Exception as e:
        st.error(f"⚠️ No se pudo cargar el modelo NBA. Verifica que existe models/nba_predictor.joblib")
        st.info("💡 Para entrenar el modelo, ejecuta: python Analisis1/scripts/train_models.py")
        return None

# Función para obtener stats de equipo
def get_team_latest_stats(team_name, df_nba, predictor):
    """Extrae las últimas estadísticas de un equipo"""
    if predictor is None or df_nba.empty:
        return None

    try:
        # Obtener el último partido del equipo
        team_games = df_nba[
            (df_nba['HOME_TEAM_NAME'] == team_name) |
            (df_nba['AWAY_TEAM_NAME'] == team_name)
        ].sort_values('GAME_DATE', ascending=False)

        if team_games.empty:
            return None

        latest_game = team_games.iloc[0]

        # Preparar features para predicción
        features = predictor.prepare_features_for_team(team_name, df_nba)
        return features

    except Exception as e:
        st.error(f"Error obteniendo stats para {team_name}: {e}")
        return None

# Función para mostrar predicción avanzada
def show_advanced_prediction(home_team, away_team, df_nba, predictor):
    """Muestra predicción con 3 modelos"""
    if predictor is None:
        st.error("❌ Modelo no disponible")
        return

    try:
        # Preparar features para el partido
        features = predictor.prepare_features_for_game(home_team, away_team, df_nba)
        
        # Obtener predicciones
        predictions = predictor.predict_game(home_team, away_team, features)

        if predictions is None:
            st.error("❌ No se pudieron generar predicciones")
            return

        # Determinar el equipo favorito
        if predictions['home_win_probability'] > predictions['away_win_probability']:
            winner_team = home_team
            winner_prob = predictions['home_win_probability']
            winner_color = "#4ECDC4"  # Verde para local
        else:
            winner_team = away_team
            winner_prob = predictions['away_win_probability']
            winner_color = "#FF6B6B"  # Rojo para visitante

        # Mostrar resultados
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                f"🏆 Favorito: {winner_team}",
                f"{winner_prob:.1%}",
                help=f"Probabilidad de victoria del equipo favorito"
            )

        with col2:
            st.metric(
                "📊 Margen Esperado",
                f"{predictions['predicted_margin']:+.1f} pts",
                help="Diferencia de puntos esperada"
            )

        with col3:
            st.metric(
                "🎯 Total Puntos",
                f"{predictions['predicted_total']:.1f} pts",
                help="Total de puntos esperados en el partido"
            )

        # Gráfico de probabilidades
        fig = go.Figure()

        # Determinar colores basados en quién es favorito
        home_color = winner_color if winner_team == home_team else '#95A5A6'
        away_color = winner_color if winner_team == away_team else '#95A5A6'

        fig.add_trace(go.Bar(
            x=[f'{home_team} ({predictions["home_win_probability"]:.1%})', 
               f'{away_team} ({predictions["away_win_probability"]:.1%})'],
            y=[predictions['home_win_probability'], predictions['away_win_probability']],
            marker_color=[home_color, away_color],
            text=[f"{predictions['home_win_probability']:.1%}", f"{predictions['away_win_probability']:.1%}"],
            textposition='auto'
        ))

        fig.update_layout(
            title=f"🏆 Probabilidades de Victoria - Favorito: {winner_team}",
            yaxis_title="Probabilidad",
            showlegend=False,
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error en predicción: {e}")

# Función para mostrar análisis básico
def show_basic_analysis(df_nba):
    """Muestra análisis básico cuando no hay modelo"""
    if df_nba.empty:
        return

    st.markdown("### 📊 Análisis Básico")

    # Estadísticas generales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📅 Partidos Totales", len(df_nba))

    with col2:
        teams = set(df_nba['HOME_TEAM_NAME'].unique()) | set(df_nba['AWAY_TEAM_NAME'].unique())
        st.metric("🏀 Equipos", len(teams))

    with col3:
        avg_home_pts = df_nba['HOME_PTS'].mean()
        st.metric("🏠 Pts Local Promedio", f"{avg_home_pts:.1f}")

    with col4:
        avg_away_pts = df_nba['AWAY_PTS'].mean()
        st.metric("✈️ Pts Visitante Promedio", f"{avg_away_pts:.1f}")

# Función principal para renderizar NBA
def render_nba_tab():
    """Renderiza la pestaña principal de NBA"""
    st.markdown("## 🏀 NBA - Predicciones Avanzadas")

    # Cargar datos
    df_nba = load_nba_data()
    predictor = load_nba_predictor()

    if df_nba.empty:
        st.error("❌ No se pudieron cargar datos NBA")
        return

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Partidos Analizados", f"{len(df_nba):,}")

    with col2:
        teams = set(df_nba['HOME_TEAM_NAME'].unique()) | set(df_nba['AWAY_TEAM_NAME'].unique())
        st.metric("🏀 Equipos", len(teams))

    with col3:
        if predictor:
            st.metric("🤖 Modelo", "ACTIVO", help="3 modelos entrenados")
        else:
            st.metric("🤖 Modelo", "INACTIVO", help="Modelo no disponible")

    with col4:
        accuracy = "72.6%" if predictor else "N/A"
        st.metric("🎯 Precisión", accuracy)

    st.markdown("---")

    # ====== SECCIÓN DE BÚSQUEDA Y PREDICCIÓN ======
    st.markdown("### 🔍 Buscar y Predecir Partido NBA")

    # Detectar tipo de datos (con features o básicos)
    if 'HOME_TEAM_NAME' in df_nba.columns:
        home_col, away_col = 'HOME_TEAM_NAME', 'AWAY_TEAM_NAME'
    else:
        home_col, away_col = 'home_team', 'away_team'

    # Obtener lista de equipos únicos
    all_teams = sorted(set(list(df_nba[home_col].unique()) + list(df_nba[away_col].unique())))

    col1, col2 = st.columns(2)

    with col1:
        home_team = st.selectbox("🏠 Equipo Local", options=all_teams, key="home_team")

    with col2:
        # Filtrar equipos para evitar duplicados
        away_options = [team for team in all_teams if team != home_team]
        away_team = st.selectbox("✈️ Equipo Visitante", options=away_options, key="away_team")

    # Botón de predicción
    if st.button("🔮 Generar Predicción", type="primary", use_container_width=True):
        if predictor:
            with st.spinner("🤖 Generando predicciones avanzadas..."):
                show_advanced_prediction(home_team, away_team, df_nba, predictor)
        else:
            st.warning("⚠️ Modelo no disponible. Mostrando análisis básico...")
            show_basic_analysis(df_nba)

    st.markdown("---")

    # Últimos partidos
    st.markdown("### 📋 Últimos Partidos")

    if len(df_nba) > 0:
        # Detectar columna de fecha
        date_col = 'GAME_DATE' if 'GAME_DATE' in df_nba.columns else 'game_date'

        if date_col in df_nba.columns:
            recent = df_nba.sort_values(date_col, ascending=False).head(10)

            # Determinar columnas a mostrar según tipo de datos
            if 'HOME_TEAM_NAME' in df_nba.columns:
                display_cols = [date_col, 'HOME_TEAM_NAME', 'HOME_PTS', 'AWAY_PTS', 'AWAY_TEAM_NAME']
                rename_dict = {
                    date_col: 'Fecha',
                    'HOME_TEAM_NAME': 'Equipo Local',
                    'HOME_PTS': 'Pts Local',
                    'AWAY_PTS': 'Pts Visitante',
                    'AWAY_TEAM_NAME': 'Equipo Visitante'
                }
            else:
                display_cols = [date_col, 'home_team', 'home_score', 'away_score', 'away_team']
                rename_dict = {
                    date_col: 'Fecha',
                    'home_team': 'Equipo Local',
                    'home_score': 'Pts Local',
                    'away_score': 'Pts Visitante',
                    'away_team': 'Equipo Visitante'
                }

            available_cols = [col for col in display_cols if col in recent.columns]

            if available_cols:
                display_df = recent[available_cols].rename(columns=rename_dict)
                st.dataframe(display_df, width='stretch', height=400)
        else:
            st.info("No hay información de fechas disponible")

    # Gráfico de distribución de puntos
    st.markdown("### 📊 Distribución de Puntos")

    # Detectar columnas de puntos
    home_pts_col = 'HOME_PTS' if 'HOME_PTS' in df_nba.columns else 'home_score'
    away_pts_col = 'AWAY_PTS' if 'AWAY_PTS' in df_nba.columns else 'away_score'

    if home_pts_col in df_nba.columns and away_pts_col in df_nba.columns:
        col1, col2 = st.columns(2)

        with col1:
            fig_home = px.histogram(df_nba, x=home_pts_col,
                                   title='Distribución Puntos Local',
                                   nbins=30,
                                   color_discrete_sequence=['#4ECDC4'])
            fig_home.update_layout(height=300)
            st.plotly_chart(fig_home, use_container_width=True)

        with col2:
            fig_away = px.histogram(df_nba, x=away_pts_col,
                                   title='Distribución Puntos Visitante',
                                   nbins=30,
                                   color_discrete_sequence=['#FF6B6B'])
            fig_away.update_layout(height=300)
            st.plotly_chart(fig_away, use_container_width=True)

# Función principal
def main():
    """Función principal del dashboard"""

    # Header
    st.markdown('<h1 class="main-header">🏀 SISTEMA DE PREDICCIONES NBA AVANZADO 🏀</h1>',
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Navegación")
        st.markdown("---")

        # Estado del sistema
        st.markdown("### 📊 Estado del Sistema")
        predictor = load_nba_predictor()
        if predictor:
            st.success("✅ NBA: Operacional (72.6%)")
        else:
            st.error("❌ NBA: Modelo no disponible")

        st.markdown("---")

        st.markdown("### 📈 Estadísticas")
        df_nba = load_nba_data()
        if not df_nba.empty:
            teams = set(df_nba['HOME_TEAM_NAME'].unique()) | set(df_nba['AWAY_TEAM_NAME'].unique())
            st.metric("Total Partidos", f"{len(df_nba):,}")
            st.metric("Equipos NBA", len(teams))
            st.metric("Modelo ML", "3 algoritmos" if predictor else "No disponible")

        st.markdown("---")

        st.markdown("### ⚙️ Configuración")
        show_advanced = st.checkbox("🔧 Opciones Avanzadas", value=False)

        if show_advanced:
            st.selectbox("Modo de predicción", ["Tiempo Real", "Histórico"])

    # Contenido principal - Solo NBA
    render_nba_tab()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🏀 Sistema NBA Avanzado v1.0 | Última actualización: {}</p>
        <p>Datos: NBA Stats API | Modelo: 3 algoritmos ML (72.6% accuracy)</p>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()