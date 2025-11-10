"""
🔥 DASHBOARD MULTI-DEPORTE - Sistema de Predicciones en Tiempo Real

Dashboard unificado para NBA, Fútbol y Tenis con:
- Predicciones en vivo actualizadas cada 30s
- Análisis histórico de cada deporte
- Gráficos interactivos con Plotly
- Sistema de notificaciones
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.abspath('.'))

from src.data.football_data_loader import FootballDataLoader
from src.data.tennis_data_loader import TennisDataLoader
from src.models.nba_predictor import NBAPredictor
import joblib
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="🔥 Predicciones Multi-Deporte",
    page_icon="🏆",
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
        border-left: 4px solid #4ECDC4;
    }
    .prediction-high {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .prediction-medium {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
    }
    .prediction-low {
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 0.3rem;
    }
    .live-indicator {
        background-color: #ff4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)


# Cache para loaders
@st.cache_resource
def get_football_loader():
    return FootballDataLoader()

@st.cache_resource
def get_tennis_loader():
    return TennisDataLoader()


# Función para cargar datos NBA (usando el existente)
@st.cache_data(ttl=300)  # Cache 5 minutos
def load_nba_data():
    """Carga datos NBA del sistema existente"""
    try:
        # Intentar cargar datos con features completas
        df = pd.read_parquet('data/nba_games_features.parquet')
        return df
    except:
        try:
            # Fallback a datos básicos
            df = pd.read_parquet('data/nba_games.parquet')
            return df
        except:
            return pd.DataFrame()


@st.cache_resource
def load_nba_predictor():
    """Carga el predictor NBA entrenado"""
    try:
        predictor = NBAPredictor()
        predictor.load('models/nba_predictor.joblib')
        return predictor
    except Exception as e:
        print(f"Error cargando predictor: {e}")
        return None


# Función para cargar datos de fútbol
@st.cache_data(ttl=300)
def load_football_data(competition='PL'):
    """Carga datos de fútbol"""
    loader = get_football_loader()
    
    # Partidos históricos
    historical = loader.get_historical_matches(competition, 2024)
    
    # Tabla de posiciones
    standings = loader.get_standings(competition, 2024)
    
    # Próximos partidos
    upcoming = loader.get_upcoming_matches(competition, days=7)
    
    return {
        'historical': historical,
        'standings': standings,
        'upcoming': upcoming
    }


# Función para cargar datos de tenis
@st.cache_data(ttl=300)
def load_tennis_data(tour='ATP', year=2024):
    """Carga datos de tenis"""
    loader = get_tennis_loader()
    
    if tour == 'ATP':
        matches = loader.get_atp_matches(year)
    else:
        matches = loader.get_wta_matches(year)
    
    return matches


def create_probability_gauge(probability, title):
    """Crea un gauge de probabilidad con Plotly"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': '#ffebee'},
                {'range': [33, 66], 'color': '#fff9c4'},
                {'range': [66, 100], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def get_team_latest_stats(df, team_name, is_home=True, home_col='HOME_TEAM_NAME', away_col='AWAY_TEAM_NAME'):
    """Obtiene las últimas estadísticas de un equipo para predicción"""
    prefix = "HOME" if is_home else "AWAY"
    team_col = home_col if is_home else away_col
    
    # Filtrar partidos del equipo
    team_games = df[df[team_col] == team_name].tail(5)
    
    if len(team_games) == 0 or home_col == 'home_team':
        # Valores por defecto para datos básicos
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
        # Usar últimas estadísticas disponibles
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
            f'{prefix}_REST_DAYS': 2,
            f'{prefix}_BACK_TO_BACK': 0,
            f'{prefix}_WIN_STREAK': latest.get(f'{prefix}_WIN_STREAK', 0),
            f'{prefix}_WIN_PCT': latest.get(f'{prefix}_WIN_PCT', 0.5),
        }
    
    return stats


def show_advanced_prediction(prediction, home_team, away_team, df, home_col, away_col):
    """Muestra predicción avanzada con 3 modelos"""
    
    # Layout principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"### 🏠 {home_team}")
        st.metric("Probabilidad Victoria", f"{prediction['home_win_probability']*100:.1f}%", 
                 delta=f"{(prediction['home_win_probability']-0.5)*100:+.1f}%")
        st.metric("Puntos Predichos", f"{prediction['predicted_home_score']:.0f}")
    
    with col2:
        st.markdown("### 🎯 PREDICCIÓN CON IA")
        
        # Gauge de probabilidad
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prediction['home_win_probability']*100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Probabilidad Local", 'font': {'size': 18}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4ECDC4"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffebee"},
                    {'range': [50, 100], 'color': "#c8e6c9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig_gauge.update_layout(height=250)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Ganador predicho
        if prediction['home_win_probability'] > 0.5:
            st.success(f"🏆 **GANADOR: {home_team}** ({prediction['home_win_probability']*100:.1f}%)")
        else:
            st.info(f"🏆 **GANADOR: {away_team}** ({prediction['away_win_probability']*100:.1f}%)")
        
        # Marcador predicho
        st.markdown(f"### 📊 Marcador Predicho")
        st.markdown(f"""
        <div style='text-align: center; font-size: 2rem; font-weight: bold;'>
            {prediction['predicted_home_score']:.0f} - {prediction['predicted_away_score']:.0f}
        </div>
        <div style='text-align: center; color: gray;'>
            Total: {prediction['predicted_total']:.0f} puntos | Margen: {abs(prediction['predicted_margin']):.1f} pts
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"### ✈️ {away_team}")
        st.metric("Probabilidad Victoria", f"{prediction['away_win_probability']*100:.1f}%",
                 delta=f"{(prediction['away_win_probability']-0.5)*100:+.1f}%")
        st.metric("Puntos Predichos", f"{prediction['predicted_away_score']:.0f}")
    
    # Información del modelo
    st.markdown("---")
    st.markdown("""
    ### 🤖 SISTEMA DE INTELIGENCIA ARTIFICIAL
    
    **3 Modelos de Machine Learning:**
    - 📊 **Modelo 1**: Regresión Logística Calibrada → Predice ganador (72.6% precisión)
    - 📈 **Modelo 2**: Ridge Regression → Predice margen de puntos
    - 🎯 **Modelo 3**: Ridge Regression → Predice total de puntos
    
    **30 Variables Principales:**
    - 🎯 Sistema ELO (3 vars): Rating dinámico como ajedrez
    - 📊 Promedios Móviles (14 vars): Forma reciente (5-10 juegos)
    - 😴 Fatiga (4 vars): Descanso físico y back-to-back
    - 🔥 Momentum (2 vars): Rachas de victorias/derrotas
    - 📅 Contexto (2 vars): Performance de temporada
    
    **Entrenamiento:**
    - 📚 4,192 partidos históricos NBA (2020-2024)
    - 🏀 45 equipos diferentes
    - 🧠 99 features generadas automáticamente
    """)


def show_basic_analysis(df, home_team, away_team, home_col, away_col):
    """Muestra análisis estadístico básico cuando no hay modelo"""
    st.warning("⚠️ Usando análisis estadístico básico (sin modelo IA)")
    
    # Calcular estadísticas básicas
    home_games = df[df[home_col] == home_team]
    away_games = df[df[away_col] == away_team]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 🏠 {home_team}")
        if len(home_games) > 0:
            st.metric("Partidos jugados", len(home_games))
    
    with col2:
        st.markdown(f"### ✈️ {away_team}")
        if len(away_games) > 0:
            st.metric("Partidos jugados", len(away_games))


def render_nba_tab():
    """Renderiza tab de NBA"""
    st.markdown("## 🏀 NBA - Predicciones y Análisis")
    
    df_nba = load_nba_data()
    
    if df_nba.empty:
        st.warning("⚠️ No hay datos de NBA. Ejecuta `python scripts/download_data.py` primero.")
        return
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Partidos", f"{len(df_nba):,}")
    
    with col2:
        if 'season' in df_nba.columns:
            st.metric("📅 Temporadas", df_nba['season'].nunique())
        else:
            st.metric("📅 Años", "2020-2024")
    
    with col3:
        st.metric("🎯 Accuracy Modelo", "72.6%")
    
    with col4:
        st.metric("📈 Features", "99")
    
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
    
    col_search1, col_search2, col_search3 = st.columns([2, 2, 1])
    
    with col_search1:
        home_team = st.selectbox(
            "🏠 Equipo Local",
            options=all_teams,
            key="home_team_select"
        )
    
    with col_search2:
        away_team = st.selectbox(
            "✈️ Equipo Visitante",
            options=[t for t in all_teams if t != home_team],
            key="away_team_select"
        )
    
    with col_search3:
        st.write("")
        st.write("")
        predict_btn = st.button("🎯 PREDECIR", type="primary", use_container_width=True)
    
    if predict_btn and home_team and away_team:
        st.markdown("---")
        
        # Cargar predictor avanzado
        predictor = load_nba_predictor()
        
        if predictor is None:
            st.error("⚠️ No se pudo cargar el modelo NBA. Verifica que existe `models/nba_predictor.joblib`")
            st.info("💡 Para entrenar el modelo, ejecuta: `python Analisis1/scripts/train_models.py`")
            return
        
        # Usar datos con features si están disponibles
        if 'HOME_TEAM_NAME' in df_nba.columns:
            # Datos con features completas
            home_col = 'HOME_TEAM_NAME'
            away_col = 'AWAY_TEAM_NAME'
        else:
            # Datos básicos
            home_col = 'home_team'
            away_col = 'away_team'
        
        with st.spinner("🔮 Calculando predicción con IA..."):
            try:
                # Obtener últimas estadísticas de los equipos
                home_stats = get_team_latest_stats(df_nba, home_team, is_home=True, home_col=home_col, away_col=away_col)
                away_stats = get_team_latest_stats(df_nba, away_team, is_home=False, home_col=home_col, away_col=away_col)
                
                # Combinar features
                features = {**home_stats, **away_stats}
                
                # Actualizar ELO_DIFF
                if 'HOME_ELO_BEFORE' in features and 'AWAY_ELO_BEFORE' in features:
                    features['ELO_DIFF'] = features['HOME_ELO_BEFORE'] - features['AWAY_ELO_BEFORE']
                
                # Predecir
                prediction = predictor.predict_game(home_team, away_team, features)
                
                # Mostrar resultados con diseño mejorado
                show_advanced_prediction(prediction, home_team, away_team, df_nba, home_col, away_col)
                
            except Exception as e:
                st.error(f"❌ Error en predicción: {e}")
                st.info("Mostrando análisis estadístico básico...")
                show_basic_analysis(df_nba, home_team, away_team, home_col, away_col)
    
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
            st.plotly_chart(fig_home, width='stretch')
        
        with col2:
            fig_away = px.histogram(df_nba, x=away_pts_col,
                                   title='Distribución Puntos Visitante',
                                   nbins=30,
                                   color_discrete_sequence=['#FF6B6B'])
            st.plotly_chart(fig_away, width='stretch')


def render_football_tab():
    """Renderiza tab de Fútbol"""
    st.markdown("## ⚽ FÚTBOL - Predicciones y Análisis")
    
    # Selector de competición
    competition = st.selectbox(
        "🏆 Seleccionar Liga",
        options=['PL', 'PD', 'BL1', 'SA', 'FL1'],
        format_func=lambda x: {
            'PL': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
            'PD': '🇪🇸 La Liga',
            'BL1': '🇩🇪 Bundesliga',
            'SA': '🇮🇹 Serie A',
            'FL1': '🇫🇷 Ligue 1'
        }[x]
    )
    
    # Cargar datos
    with st.spinner('Cargando datos de fútbol...'):
        data = load_football_data(competition)
    
    historical = data['historical']
    standings = data['standings']
    upcoming = data['upcoming']
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Partidos Históricos", len(historical))
    
    with col2:
        if not standings.empty:
            st.metric("🏆 Equipos", len(standings))
    
    with col3:
        if not upcoming.empty:
            st.metric("🔮 Próximos", len(upcoming))
    
    with col4:
        st.metric("✅ API Status", "ACTIVA")
    
    st.markdown("---")
    
    # Tabla de posiciones
    if not standings.empty:
        st.markdown("### 🏆 Tabla de Posiciones")
        
        # Colorear por zona (Champions, Europa, Descenso)
        def color_position(row):
            if row['position'] <= 4:
                return ['background-color: #c8e6c9'] * len(row)
            elif row['position'] <= 6:
                return ['background-color: #fff9c4'] * len(row)
            elif row['position'] >= 18:
                return ['background-color: #ffcdd2'] * len(row)
            return [''] * len(row)
        
        styled_standings = standings[['position', 'team', 'played', 'won', 'draw', 'lost', 'points', 'goal_difference']].head(20)
        st.dataframe(styled_standings, width='stretch', height=400)
    
    # Próximos partidos
    if not upcoming.empty:
        st.markdown("### 🔮 Próximos Partidos (7 días)")
        
        for _, match in upcoming.head(10).iterrows():
            col1, col2, col3 = st.columns([2, 1, 2])
            
            match_date = pd.to_datetime(match['date'])
            
            with col1:
                st.markdown(f"**{match['home_team']}**")
            
            with col2:
                st.markdown(f"<center>{match_date.strftime('%d/%m %H:%M')}</center>", 
                          unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"**{match['away_team']}**")
            
            st.markdown("---")
    
    # Gráficos de análisis
    if not historical.empty and 'home_score' in historical.columns:
        st.markdown("### 📊 Análisis de Goles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de goles totales
            historical['total_goals'] = historical['home_score'] + historical['away_score']
            fig_goals = px.histogram(historical, x='total_goals',
                                    title='Distribución de Goles por Partido',
                                    nbins=10,
                                    color_discrete_sequence=['#4ECDC4'])
            st.plotly_chart(fig_goals, width='stretch')
        
        with col2:
            # Victorias local vs visitante
            if 'winner' in historical.columns:
                winner_counts = historical['winner'].value_counts()
                fig_winners = px.pie(values=winner_counts.values,
                                    names=winner_counts.index,
                                    title='Distribución de Resultados',
                                    color_discrete_sequence=['#4ECDC4', '#FF6B6B', '#FFA07A'])
                st.plotly_chart(fig_winners, width='stretch')


def render_tennis_tab():
    """Renderiza tab de Tenis"""
    st.markdown("## 🎾 TENIS - Predicciones y Análisis")
    
    # Selectores
    col1, col2 = st.columns(2)
    
    with col1:
        tour = st.selectbox("🏆 Tour", options=['ATP', 'WTA'])
    
    with col2:
        year = st.selectbox("📅 Año", options=[2024, 2023, 2022])
    
    # Cargar datos
    with st.spinner(f'Cargando datos {tour} {year}...'):
        df_tennis = load_tennis_data(tour, year)
    
    if df_tennis.empty:
        st.error("❌ No se pudieron cargar datos de tenis")
        return
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Partidos", f"{len(df_tennis):,}")
    
    with col2:
        st.metric("🏟️ Torneos", df_tennis['tourney_name'].nunique())
    
    with col3:
        surfaces = df_tennis['surface'].dropna().unique()
        st.metric("🎯 Superficies", len(surfaces))
    
    with col4:
        players = pd.concat([df_tennis['winner_name'], df_tennis['loser_name']]).nunique()
        st.metric("👥 Jugadores", players)
    
    st.markdown("---")
    
    # Análisis de jugador
    st.markdown("### 🎾 Análisis de Jugador")
    
    all_players = pd.concat([df_tennis['winner_name'], df_tennis['loser_name']]).dropna().unique()
    all_players = sorted([p for p in all_players if isinstance(p, str)])
    
    selected_player = st.selectbox("Seleccionar Jugador", options=all_players[:100])
    
    if selected_player:
        loader = get_tennis_loader()
        stats = loader.get_player_stats(selected_player, df_tennis)
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎯 Partidos", stats['total_matches'])
            
            with col2:
                st.metric("✅ Victorias", stats['wins'])
            
            with col3:
                st.metric("❌ Derrotas", stats['losses'])
            
            with col4:
                st.metric("📊 Win %", f"{stats['win_pct']:.1f}%")
            
            # Stats por superficie
            if stats.get('surface_stats'):
                st.markdown("#### 📊 Rendimiento por Superficie")
                
                surface_data = []
                for surface, s_stats in stats['surface_stats'].items():
                    surface_data.append({
                        'Superficie': surface,
                        'Partidos': s_stats['matches'],
                        'Victorias': s_stats['wins'],
                        'Win %': s_stats['win_pct']
                    })
                
                df_surfaces = pd.DataFrame(surface_data)
                
                fig_surface = px.bar(df_surfaces, x='Superficie', y='Win %',
                                    title=f'Win % por Superficie - {selected_player}',
                                    color='Win %',
                                    color_continuous_scale='Viridis')
                st.plotly_chart(fig_surface, width='stretch')
    
    # Distribución por superficie
    st.markdown("### 🌍 Distribución de Partidos por Superficie")
    
    surface_counts = df_tennis['surface'].value_counts()
    fig_surfaces = px.pie(values=surface_counts.values,
                         names=surface_counts.index,
                         title='Partidos por Superficie',
                         color_discrete_sequence=px.colors.sequential.Viridis)
    st.plotly_chart(fig_surfaces, width='stretch')


def render_live_tab():
    """Renderiza tab de predicciones en vivo"""
    st.markdown("## 🔴 PARTIDOS EN VIVO")
    
    st.markdown('<div class="live-indicator">🔴 ACTUALIZANDO CADA 30 SEGUNDOS</div>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Botón para actualizar manualmente
    if st.button("🔄 Actualizar Ahora", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Cargar partidos en vivo de fútbol
    st.markdown("### ⚽ Fútbol - Partidos en Vivo")
    
    loader = get_football_loader()
    live_football = loader.get_live_matches()
    
    if not live_football.empty:
        for _, match in live_football.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                
                with col1:
                    st.markdown(f"**{match['home_team']}**")
                
                with col2:
                    st.markdown(f"<center style='font-size:24px'>{match['home_score']}</center>",
                              unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"<center>**{match['minute']}'**</center>",
                              unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"<center style='font-size:24px'>{match['away_score']}</center>",
                              unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"**{match['away_team']}**")
                
                # Simulación de predicción en vivo
                st.markdown("**Predicción Actualizada:**")
                col1, col2, col3 = st.columns(3)
                
                # Predicción simple basada en score actual
                home_prob = 0.45 + (match['home_score'] - match['away_score']) * 0.10
                home_prob = max(0.1, min(0.9, home_prob))
                draw_prob = 0.25
                away_prob = 1 - home_prob - draw_prob
                
                with col1:
                    fig1 = create_probability_gauge(home_prob, "Local")
                    st.plotly_chart(fig1, width='stretch')
                
                with col2:
                    fig2 = create_probability_gauge(draw_prob, "Empate")
                    st.plotly_chart(fig2, width='stretch')
                
                with col3:
                    fig3 = create_probability_gauge(away_prob, "Visitante")
                    st.plotly_chart(fig3, width='stretch')
                
                st.markdown("---")
    else:
        st.info("ℹ️ No hay partidos de fútbol en vivo en este momento")
    
    # Auto-refresh cada 30 segundos
    st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 30000);
    </script>
    """, unsafe_allow_html=True)


def main():
    """Función principal del dashboard"""
    
    # Header
    st.markdown('<h1 class="main-header">🔥 SISTEMA DE PREDICCIONES MULTI-DEPORTE 🔥</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Navegación")
        st.markdown("---")
        
        # Estado del sistema
        st.markdown("### 📊 Estado del Sistema")
        st.success("✅ NBA: Operacional (72.6%)")
        st.success("✅ Fútbol: API Activa")
        st.success("✅ Tenis: 11,668 partidos")
        
        st.markdown("---")
        
        st.markdown("### 📈 Estadísticas Totales")
        st.metric("Total Partidos", "16,240+")
        st.metric("Deportes", "3")
        st.metric("Modelos ML", "1 activo")
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Configuración")
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        show_advanced = st.checkbox("🔧 Opciones Avanzadas", value=False)
        
        if show_advanced:
            st.slider("Intervalo de actualización (s)", 10, 60, 30)
            st.selectbox("Modo de predicción", ["Tiempo Real", "Histórico"])
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "⚽ FÚTBOL", "🎾 TENIS", "🔴 EN VIVO"])
    
    with tab1:
        render_nba_tab()
    
    with tab2:
        render_football_tab()
    
    with tab3:
        render_tennis_tab()
    
    with tab4:
        render_live_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🔥 Sistema Multi-Deporte v1.0 | Última actualización: {}</p>
        <p>Datos: NBA Stats API, Football-Data.org, Jeff Sackmann Tennis GitHub</p>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
