"""
🏀 DASHBOARD NBA - Sistema de Predicciones Avanzadas

Dashboard especializado para NBA con:
- Predicciones con 3 modelos (77.0% accuracy)
- Análisis histórico completo (13,691 partidos, 10 temporadas)
- Gráficos interactivos con Plotly
- Sistema ELO + XGBoost + 33 features avanzadas
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
    # Prioridad 1: Datos completos procesados (local)
    try:
        df = pd.read_parquet('data/processed/games_with_features.parquet')
        st.info("✅ Datos avanzados cargados (13,691 partidos con 103 features, 10 temporadas 2015-2025)")
        return df
    except FileNotFoundError:
        pass
    
    # Prioridad 2: Datos de despliegue (Cloud)
    try:
        df = pd.read_parquet('data/deployment_data.parquet')
        st.info("✅ Datos cargados (2,000 partidos recientes para predicciones)")
        return df
    except FileNotFoundError:
        pass
    
    # Prioridad 3: Datos raw
    try:
        import glob
        csv_files = glob.glob('data/raw/games_*.csv')
        if csv_files:
            # Cargar el archivo más reciente
            latest_file = max(csv_files)
            df = pd.read_csv(latest_file)
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
            st.info(f"✅ Datos cargados desde {latest_file}")
            return df
    except Exception:
        pass
    
    # Si no hay archivos, crear datos de ejemplo mínimos
    st.warning("⚠️ No se encontraron archivos de datos. Usando datos de ejemplo...")
    
    teams = ['Lakers', 'Celtics', 'Warriors', 'Heat', 'Bucks', 'Nets', 'Suns', 'Mavericks']
    import numpy as np
    from datetime import datetime, timedelta
    
    data = []
    for i in range(100):
        home_team = np.random.choice(teams)
        away_team = np.random.choice([t for t in teams if t != home_team])
        
        data.append({
            'GAME_DATE': datetime.now() - timedelta(days=i),
            'HOME_TEAM_NAME': home_team,
            'AWAY_TEAM_NAME': away_team,
            'HOME_PTS': np.random.randint(95, 125),
            'AWAY_PTS': np.random.randint(95, 125),
            'HOME_ELO_BEFORE': 1500 + np.random.randint(-100, 100),
            'AWAY_ELO_BEFORE': 1500 + np.random.randint(-100, 100),
        })
    
    df = pd.DataFrame(data)
    st.info("ℹ️ Datos de ejemplo. Para predicciones reales, carga datos históricos.")
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

        # Calcular puntos esperados para cada equipo
        # Margen positivo = local gana, margen negativo = visitante gana
        margin = predictions['predicted_margin']
        total_pts = predictions['predicted_total']
        
        # Calcular puntos individuales usando margen y total
        home_pts = (total_pts + margin) / 2
        away_pts = (total_pts - margin) / 2

        # Mostrar resultados principales
        st.markdown("### 🎯 Predicción del Partido")
        
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
                f"{abs(margin):.1f} pts",
                help=f"Diferencia de puntos esperada ({winner_team} por {abs(margin):.1f})"
            )

        with col3:
            st.metric(
                "🎯 Total Puntos",
                f"{total_pts:.1f} pts",
                help="Total de puntos esperados en el partido"
            )

        # Mostrar puntos predichos para cada equipo
        st.markdown("### 📊 Puntos Predichos por Equipo")
        
        col_home, col_away = st.columns(2)
        
        with col_home:
            st.markdown(f"""
            <div style='background-color: #e8f4f8; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3>🏠 {home_team}</h3>
                <h1 style='color: #4ECDC4; font-size: 3rem;'>{home_pts:.1f}</h1>
                <p style='color: #7f8c8d;'>Puntos Esperados</p>
                <p style='font-size: 1.2rem;'>Probabilidad: {predictions['home_win_probability']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_away:
            st.markdown(f"""
            <div style='background-color: #ffeaa7; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3>✈️ {away_team}</h3>
                <h1 style='color: #FF6B6B; font-size: 3rem;'>{away_pts:.1f}</h1>
                <p style='color: #7f8c8d;'>Puntos Esperados</p>
                <p style='font-size: 1.2rem;'>Probabilidad: {predictions['away_win_probability']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

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
            st.metric("🤖 Modelo", "XGBoost", help="3 modelos XGBoost entrenados con 13,691 partidos")
        else:
            st.metric("🤖 Modelo", "INACTIVO", help="Modelo no disponible")

    with col4:
        accuracy = "77.0%" if predictor else "N/A"
        st.metric("🎯 Precisión", accuracy, help="77% precisión en 2,738 partidos de test")

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

    # ====== HISTORIAL HEAD-TO-HEAD ======
    st.markdown("---")
    st.markdown(f"### 📊 Historial: {home_team} vs {away_team}")
    
    # Filtrar enfrentamientos directos entre estos equipos
    h2h = df_nba[
        ((df_nba[home_col] == home_team) & (df_nba[away_col] == away_team)) |
        ((df_nba[home_col] == away_team) & (df_nba[away_col] == home_team))
    ].copy()
    
    if len(h2h) > 0:
        # Calcular estadísticas generales
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        # Victorias totales
        home_wins = len(h2h[(h2h[home_col] == home_team) & (h2h['HOME_PTS'] > h2h['AWAY_PTS'])]) + \
                    len(h2h[(h2h[away_col] == home_team) & (h2h['AWAY_PTS'] > h2h['HOME_PTS'])])
        away_wins = len(h2h) - home_wins
        
        with col_stat1:
            st.metric(f"🏆 Victorias {home_team}", home_wins)
        
        with col_stat2:
            st.metric(f"🏆 Victorias {away_team}", away_wins)
        
        with col_stat3:
            st.metric("📅 Enfrentamientos", len(h2h))
        
        with col_stat4:
            if len(h2h) > 0:
                date_col = 'GAME_DATE' if 'GAME_DATE' in h2h.columns else 'game_date'
                last_game = pd.to_datetime(h2h[date_col]).max()
                st.metric("📆 Último Partido", last_game.strftime('%Y-%m-%d'))
        
        # Mostrar últimos 5 enfrentamientos
        st.markdown("#### 📋 Últimos 5 Enfrentamientos")
        
        h2h_recent = h2h.sort_values(date_col, ascending=False).head(5)
        
        # Crear DataFrame para mostrar
        display_data = []
        for _, game in h2h_recent.iterrows():
            # Determinar quién jugó de local y visitante
            if game[home_col] == home_team:
                local = home_team
                visitante = away_team
                pts_local = game['HOME_PTS']
                pts_visitante = game['AWAY_PTS']
            else:
                local = away_team
                visitante = home_team
                pts_local = game['HOME_PTS']
                pts_visitante = game['AWAY_PTS']
            
            ganador = local if pts_local > pts_visitante else visitante
            margen = abs(pts_local - pts_visitante)
            
            display_data.append({
                'Fecha': pd.to_datetime(game[date_col]).strftime('%Y-%m-%d'),
                'Local': local,
                'Visitante': visitante,
                'Resultado': f"{int(pts_local)} - {int(pts_visitante)}",
                'Ganador': f"🏆 {ganador}",
                'Margen': f"{int(margen)} pts"
            })
        
        h2h_df = pd.DataFrame(display_data)
        st.dataframe(h2h_df, use_container_width=True, hide_index=True)
        
        # Estadísticas promedio en enfrentamientos
        st.markdown("#### 📈 Promedios en Enfrentamientos")
        col_avg1, col_avg2 = st.columns(2)
        
        with col_avg1:
            st.markdown(f"**{home_team}:**")
            # Calcular promedio de puntos del home_team en estos partidos
            home_as_home = h2h[h2h[home_col] == home_team]['HOME_PTS'].mean()
            home_as_away = h2h[h2h[away_col] == home_team]['AWAY_PTS'].mean()
            home_avg = h2h[
                ((h2h[home_col] == home_team) & h2h['HOME_PTS']) |
                ((h2h[away_col] == home_team) & h2h['AWAY_PTS'])
            ]
            
            # Calcular correctamente
            home_pts_list = []
            for _, g in h2h.iterrows():
                if g[home_col] == home_team:
                    home_pts_list.append(g['HOME_PTS'])
                else:
                    home_pts_list.append(g['AWAY_PTS'])
            
            if home_pts_list:
                st.metric("Puntos Promedio", f"{sum(home_pts_list)/len(home_pts_list):.1f}")
        
        with col_avg2:
            st.markdown(f"**{away_team}:**")
            # Calcular promedio de puntos del away_team en estos partidos
            away_pts_list = []
            for _, g in h2h.iterrows():
                if g[home_col] == away_team:
                    away_pts_list.append(g['HOME_PTS'])
                else:
                    away_pts_list.append(g['AWAY_PTS'])
            
            if away_pts_list:
                st.metric("Puntos Promedio", f"{sum(away_pts_list)/len(away_pts_list):.1f}")
        
    else:
        st.info(f"ℹ️ No hay historial de enfrentamientos entre {home_team} y {away_team} en los datos disponibles.")
    
    st.markdown("---")

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
    st.markdown("### 📋 Últimos Partidos Reales")

    if len(df_nba) > 0:
        # Detectar columna de fecha
        date_col = 'GAME_DATE' if 'GAME_DATE' in df_nba.columns else 'game_date'

        if date_col in df_nba.columns:
            # Filtrar solo partidos hasta hoy (eliminar proyecciones futuras)
            from datetime import datetime
            today = pd.Timestamp(datetime.now())
            df_past = df_nba[pd.to_datetime(df_nba[date_col]) <= today].copy()
            
            if len(df_past) == 0:
                st.warning("⚠️ No hay partidos históricos disponibles. Los datos parecen ser proyecciones futuras.")
                df_past = df_nba  # Usar todos los datos si no hay históricos
            
            # Ordenar por fecha descendente y tomar últimos 10
            recent = df_past.sort_values(date_col, ascending=False).head(10)

            # Determinar columnas a mostrar según tipo de datos
            if 'HOME_TEAM_NAME' in df_nba.columns:
                # Agregar columna de ganador
                def get_winner(row):
                    if row['HOME_PTS'] > row['AWAY_PTS']:
                        return f"🏆 {row['HOME_TEAM_NAME']}"
                    else:
                        return f"🏆 {row['AWAY_TEAM_NAME']}"
                
                recent_display = recent.copy()
                recent_display['Ganador'] = recent.apply(get_winner, axis=1)
                recent_display['Resultado'] = recent['HOME_PTS'].astype(str) + ' - ' + recent['AWAY_PTS'].astype(str)
                
                display_cols = [date_col, 'HOME_TEAM_NAME', 'AWAY_TEAM_NAME', 'Resultado', 'Ganador']
                rename_dict = {
                    date_col: 'Fecha',
                    'HOME_TEAM_NAME': 'Local',
                    'AWAY_TEAM_NAME': 'Visitante',
                }
            else:
                display_cols = [date_col, 'home_team', 'home_score', 'away_score', 'away_team']
                rename_dict = {
                    date_col: 'Fecha',
                    'home_team': 'Local',
                    'home_score': 'Pts Local',
                    'away_score': 'Pts Visitante',
                    'away_team': 'Visitante'
                }
                recent_display = recent

            available_cols = [col for col in display_cols if col in recent_display.columns]

            if available_cols:
                display_df = recent_display[available_cols].rename(columns=rename_dict)
                
                # Formatear fecha
                if 'Fecha' in display_df.columns:
                    display_df['Fecha'] = pd.to_datetime(display_df['Fecha']).dt.strftime('%Y-%m-%d')
                
                st.dataframe(display_df, use_container_width=True, height=400)
                
                # Mostrar info de fechas
                fecha_min = pd.to_datetime(df_past[date_col]).min()
                fecha_max = pd.to_datetime(df_past[date_col]).max()
                st.caption(f"📅 Rango de datos: {fecha_min.strftime('%Y-%m-%d')} a {fecha_max.strftime('%Y-%m-%d')} ({len(df_past):,} partidos)")
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