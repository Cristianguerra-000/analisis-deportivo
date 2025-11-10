"""
Script para generar datos NBA realistas con equipos reales
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def generate_nba_data():
    """Genera datos NBA con equipos reales"""
    
    print("\n🏀 Generando datos NBA con equipos reales...")
    
    # Crear directorio data si no existe
    Path("data").mkdir(exist_ok=True)
    
    # Equipos NBA reales (30 equipos)
    nba_teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
        'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
        'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
        'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
        'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
        'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
        'Utah Jazz', 'Washington Wizards'
    ]
    
    # Generar datos más realistas
    np.random.seed(42)
    n_games = 1000  # 1000 partidos
    
    games = []
    start_date = datetime(2023, 10, 1)  # Inicio temporada 2023-24
    
    print(f"Generando {n_games} partidos...")
    
    for i in range(n_games):
        # Seleccionar equipos aleatorios (sin repetir)
        home_team = np.random.choice(nba_teams)
        away_team = np.random.choice([t for t in nba_teams if t != home_team])
        
        # Generar puntos con distribución realista
        # NBA promedio: ~112 puntos por equipo, ventaja local ~3 puntos
        home_score = int(np.random.normal(114, 10))  # Media 114, std 10
        away_score = int(np.random.normal(109, 10))  # Media 109, std 10
        
        # Asegurar puntos razonables (85-140)
        home_score = max(85, min(145, home_score))
        away_score = max(85, min(145, away_score))
        
        # Fecha del partido (distribuir a lo largo de la temporada)
        game_date = start_date + timedelta(days=i//6)  # ~6 partidos por día
        
        games.append({
            'game_date': game_date,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'home_win': home_score > away_score,
            'season': '2023-24',
            'total_points': home_score + away_score,
            'point_diff': home_score - away_score
        })
    
    df = pd.DataFrame(games)
    
    # Guardar
    output_path = "data/nba_games.parquet"
    df.to_parquet(output_path)
    
    # Estadísticas
    print(f"\n✅ DATOS GENERADOS EXITOSAMENTE")
    print("="*60)
    print(f"📊 Total partidos: {len(df):,}")
    print(f"🏀 Equipos únicos: {df['home_team'].nunique()}")
    print(f"📅 Rango fechas: {df['game_date'].min().date()} a {df['game_date'].max().date()}")
    print(f"🏠 Win rate local: {df['home_win'].mean()*100:.1f}%")
    print(f"📈 Puntos promedio: Local {df['home_score'].mean():.1f}, Visitante {df['away_score'].mean():.1f}")
    print(f"💾 Guardado en: {output_path}")
    print("="*60)
    
    # Muestra de datos
    print("\n📋 Muestra de datos:")
    print(df.head(5).to_string(index=False))
    
    # Equipos más comunes
    print(f"\n🔝 Top 5 equipos locales más frecuentes:")
    print(df['home_team'].value_counts().head(5).to_string())
    
    return df

if __name__ == "__main__":
    df = generate_nba_data()
    
    print("\n" + "="*60)
    print("✅ ¡LISTO! Ahora puedes iniciar el dashboard:")
    print("   python -m streamlit run src/dashboard/multi_sport_app.py")
    print("="*60 + "\n")
