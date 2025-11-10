"""
Script para buscar y predecir partidos NBA específicos
Uso: python scripts/predict_nba_game.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
import joblib

def load_model():
    """Carga el modelo NBA entrenado"""
    try:
        model = joblib.load('models/nba_model.pkl')
        print("✓ Modelo NBA cargado correctamente")
        return model
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        return None

def load_nba_data():
    """Carga los datos NBA"""
    try:
        df = pd.read_parquet('data/nba_games.parquet')
        print(f"✓ Cargados {len(df)} partidos NBA")
        return df
    except Exception as e:
        print(f"✗ Error cargando datos: {e}")
        return None

def search_teams(df, query):
    """Busca equipos por nombre"""
    query_lower = query.lower()
    
    # Buscar en home_team
    home_matches = df[df['home_team'].str.lower().str.contains(query_lower, na=False)]
    # Buscar en away_team
    away_matches = df[df['away_team'].str.lower().str.contains(query_lower, na=False)]
    
    # Combinar y eliminar duplicados
    all_matches = pd.concat([home_matches, away_matches]).drop_duplicates()
    
    return all_matches

def get_team_names(df):
    """Obtiene lista única de equipos"""
    home_teams = df['home_team'].unique()
    away_teams = df['away_team'].unique()
    all_teams = sorted(set(list(home_teams) + list(away_teams)))
    return all_teams

def show_recent_games(df, team1, team2=None, limit=5):
    """Muestra partidos recientes de un equipo o H2H"""
    if team2:
        # Head to Head
        h2h = df[
            ((df['home_team'].str.contains(team1, case=False, na=False)) & 
             (df['away_team'].str.contains(team2, case=False, na=False))) |
            ((df['home_team'].str.contains(team2, case=False, na=False)) & 
             (df['away_team'].str.contains(team1, case=False, na=False)))
        ].tail(limit)
        
        if len(h2h) > 0:
            print(f"\n{'='*80}")
            print(f"ÚLTIMOS {len(h2h)} ENFRENTAMIENTOS: {team1} vs {team2}")
            print(f"{'='*80}")
            for idx, row in h2h.iterrows():
                winner = "✓" if row.get('home_win', False) else "✗"
                print(f"{winner} {row['home_team']} {row.get('home_score', 'N/A')} - "
                      f"{row.get('away_score', 'N/A')} {row['away_team']}")
        else:
            print(f"\nNo se encontraron enfrentamientos previos entre {team1} y {team2}")
    else:
        # Últimos partidos de un equipo
        team_games = df[
            (df['home_team'].str.contains(team1, case=False, na=False)) |
            (df['away_team'].str.contains(team1, case=False, na=False))
        ].tail(limit)
        
        if len(team_games) > 0:
            print(f"\n{'='*80}")
            print(f"ÚLTIMOS {len(team_games)} PARTIDOS: {team1}")
            print(f"{'='*80}")
            for idx, row in team_games.iterrows():
                print(f"{row['home_team']} {row.get('home_score', 'N/A')} - "
                      f"{row.get('away_score', 'N/A')} {row['away_team']}")

def predict_game(model, home_team, away_team, df):
    """Predice el resultado de un partido"""
    if model is None:
        print("\n⚠️ No hay modelo cargado. Mostrando análisis estadístico...")
        return show_statistical_analysis(home_team, away_team, df)
    
    # Preparar features (simplificado - ajusta según tu modelo)
    try:
        # Calcular estadísticas del equipo local
        home_games = df[df['home_team'] == home_team]
        if len(home_games) > 0:
            home_wins = home_games['home_win'].mean() if 'home_win' in home_games.columns else 0.5
            home_avg_score = home_games['home_score'].mean() if 'home_score' in home_games.columns else 100
        else:
            home_wins = 0.5
            home_avg_score = 100
        
        # Calcular estadísticas del equipo visitante
        away_games = df[df['away_team'] == away_team]
        if len(away_games) > 0:
            away_wins = (1 - away_games['home_win'].mean()) if 'home_win' in away_games.columns else 0.5
            away_avg_score = away_games['away_score'].mean() if 'away_score' in away_games.columns else 100
        else:
            away_wins = 0.5
            away_avg_score = 100
        
        # Crear feature vector
        features = np.array([[
            home_wins,
            away_wins,
            home_avg_score,
            away_avg_score,
            home_avg_score - away_avg_score
        ]])
        
        # Predicción
        prediction = model.predict_proba(features)[0]
        
        print(f"\n{'='*80}")
        print(f"PREDICCIÓN: {home_team} vs {away_team}")
        print(f"{'='*80}")
        print(f"🏠 Probabilidad {home_team}: {prediction[1]*100:.1f}%")
        print(f"✈️  Probabilidad {away_team}: {prediction[0]*100:.1f}%")
        print(f"\n🎯 PREDICCIÓN: {'GANA ' + home_team if prediction[1] > 0.5 else 'GANA ' + away_team}")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\n⚠️ Error en predicción: {e}")
        print("Mostrando análisis estadístico...")
        show_statistical_analysis(home_team, away_team, df)

def show_statistical_analysis(home_team, away_team, df):
    """Muestra análisis estadístico cuando no hay modelo"""
    print(f"\n{'='*80}")
    print(f"ANÁLISIS ESTADÍSTICO: {home_team} vs {away_team}")
    print(f"{'='*80}")
    
    # Estadísticas local
    home_games = df[df['home_team'] == home_team]
    if len(home_games) > 0 and 'home_win' in home_games.columns:
        home_win_rate = home_games['home_win'].mean() * 100
        print(f"\n🏠 {home_team}:")
        print(f"   - Win rate en casa: {home_win_rate:.1f}%")
        if 'home_score' in home_games.columns:
            print(f"   - Promedio puntos: {home_games['home_score'].mean():.1f}")
    
    # Estadísticas visitante
    away_games = df[df['away_team'] == away_team]
    if len(away_games) > 0 and 'home_win' in away_games.columns:
        away_win_rate = (1 - away_games['home_win'].mean()) * 100
        print(f"\n✈️  {away_team}:")
        print(f"   - Win rate de visitante: {away_win_rate:.1f}%")
        if 'away_score' in away_games.columns:
            print(f"   - Promedio puntos: {away_games['away_score'].mean():.1f}")
    
    # Head to Head
    h2h = df[
        ((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
        ((df['home_team'] == away_team) & (df['away_team'] == home_team))
    ]
    
    if len(h2h) > 0:
        print(f"\n📊 Enfrentamientos directos: {len(h2h)} partidos")
        if 'home_win' in h2h.columns:
            home_wins_h2h = len(h2h[(h2h['home_team'] == home_team) & (h2h['home_win'] == True)])
            away_wins_h2h = len(h2h[(h2h['away_team'] == home_team) & (h2h['home_win'] == False)])
            total_home_wins = home_wins_h2h + away_wins_h2h
            
            print(f"   - {home_team}: {total_home_wins} victorias")
            print(f"   - {away_team}: {len(h2h) - total_home_wins} victorias")
    
    print(f"{'='*80}\n")

def interactive_mode(df, model):
    """Modo interactivo para buscar y predecir partidos"""
    print("\n" + "="*80)
    print("🏀 PREDICTOR NBA - MODO INTERACTIVO")
    print("="*80)
    print("Comandos:")
    print("  - Escribe el nombre de un equipo para ver sus últimos partidos")
    print("  - 'EQUIPO1 vs EQUIPO2' para ver predicción")
    print("  - 'equipos' para ver lista de equipos")
    print("  - 'salir' para terminar")
    print("="*80 + "\n")
    
    while True:
        try:
            query = input("\n🔍 Buscar: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['salir', 'exit', 'quit']:
                print("\n¡Hasta luego! 👋\n")
                break
            
            if query.lower() == 'equipos':
                teams = get_team_names(df)
                print(f"\n📋 {len(teams)} EQUIPOS NBA:")
                print("="*80)
                for i, team in enumerate(teams, 1):
                    print(f"{i:2d}. {team}")
                print("="*80)
                continue
            
            # Verificar si es una búsqueda de partido (vs)
            if ' vs ' in query.lower():
                parts = query.lower().split(' vs ')
                if len(parts) == 2:
                    team1, team2 = parts[0].strip(), parts[1].strip()
                    
                    # Buscar equipos más cercanos
                    all_teams = get_team_names(df)
                    home_match = [t for t in all_teams if team1 in t.lower()]
                    away_match = [t for t in all_teams if team2 in t.lower()]
                    
                    if home_match and away_match:
                        home_team = home_match[0]
                        away_team = away_match[0]
                        
                        # Mostrar H2H
                        show_recent_games(df, home_team, away_team)
                        
                        # Predicción
                        predict_game(model, home_team, away_team, df)
                    else:
                        if not home_match:
                            print(f"❌ No se encontró equipo: {team1}")
                        if not away_match:
                            print(f"❌ No se encontró equipo: {team2}")
                continue
            
            # Búsqueda simple de equipo
            matches = search_teams(df, query)
            
            if len(matches) > 0:
                # Encontrar el equipo más probable
                all_teams = get_team_names(df)
                matched_team = [t for t in all_teams if query.lower() in t.lower()]
                
                if matched_team:
                    team = matched_team[0]
                    show_recent_games(df, team)
                    
                    print(f"\n💡 Para ver predicción escribe: {team} vs EQUIPO_RIVAL")
                else:
                    print(f"✓ {len(matches)} partidos encontrados")
            else:
                print(f"❌ No se encontraron resultados para '{query}'")
                print("\n💡 Intenta con:")
                print("   - Nombre completo del equipo (ej: 'Lakers')")
                print("   - 'Lakers vs Celtics' para predicción")
                print("   - 'equipos' para ver lista completa")
        
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego! 👋\n")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")

def main():
    """Función principal"""
    print("\n🏀 CARGANDO SISTEMA NBA...")
    
    # Cargar datos
    df = load_nba_data()
    if df is None:
        print("\n❌ No se pudieron cargar los datos. Verifica que existe data/nba_games.parquet")
        return
    
    # Cargar modelo (opcional)
    model = load_model()
    
    # Modo interactivo
    interactive_mode(df, model)

if __name__ == "__main__":
    main()
