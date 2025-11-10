"""Ejemplo de uso del sistema NBA Predictor."""

from pathlib import Path
import pandas as pd
import sys

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.predictor import NBAPredictor

def main():
    print("="*70)
    print("  🏀 NBA PREDICTOR - EJEMPLO DE USO")
    print("="*70)
    
    # 1. Cargar modelo entrenado
    print("\n1️⃣ Cargando modelo entrenado...")
    model_path = Path("models/nba_predictor_baseline.joblib")
    
    if not model_path.exists():
        print("❌ Modelo no encontrado. Primero ejecuta:")
        print("   python scripts/train_models.py")
        return
    
    predictor = NBAPredictor()
    predictor.load(str(model_path))
    print("✅ Modelo cargado")
    
    # 2. Cargar datos
    print("\n2️⃣ Cargando datos procesados...")
    data_path = Path("data/processed/games_with_features.parquet")
    
    if not data_path.exists():
        print("❌ Datos no encontrados. Primero ejecuta:")
        print("   python scripts/process_features.py")
        return
    
    df = pd.read_parquet(data_path)
    print(f"✅ Cargados {len(df)} partidos")
    
    # 3. Hacer predicción de ejemplo
    print("\n3️⃣ Haciendo predicción de ejemplo...")
    print("   Partido: Los Angeles Lakers (local) vs Boston Celtics (visitante)")
    
    # Obtener features de ejemplo (últimos partidos de cada equipo)
    lakers_recent = df[df['HOME_TEAM_NAME'] == 'Los Angeles Lakers'].tail(1)
    celtics_recent = df[df['AWAY_TEAM_NAME'] == 'Boston Celtics'].tail(1)
    
    if len(lakers_recent) == 0 or len(celtics_recent) == 0:
        print("⚠️  No hay datos históricos para estos equipos")
        print("   Usando valores por defecto...")
        
        # Features por defecto
        features = {
            'HOME_ELO_BEFORE': 1550,
            'AWAY_ELO_BEFORE': 1520,
            'ELO_DIFF': 30,
            'HOME_PTS_ROLL_5': 115,
            'AWAY_PTS_ROLL_5': 112,
            'HOME_FG_PCT_ROLL_5': 0.47,
            'AWAY_FG_PCT_ROLL_5': 0.46,
            'HOME_FG3_PCT_ROLL_5': 0.36,
            'AWAY_FG3_PCT_ROLL_5': 0.35,
            'HOME_REB_ROLL_5': 46,
            'AWAY_REB_ROLL_5': 44,
            'HOME_AST_ROLL_5': 26,
            'AWAY_AST_ROLL_5': 25,
            'HOME_TOV_ROLL_5': 13,
            'AWAY_TOV_ROLL_5': 14,
            'HOME_PTS_ROLL_10': 114,
            'AWAY_PTS_ROLL_10': 111,
            'HOME_REST_DAYS': 2,
            'AWAY_REST_DAYS': 1,
            'HOME_BACK_TO_BACK': 0,
            'AWAY_BACK_TO_BACK': 0,
            'HOME_WIN_STREAK': 2,
            'AWAY_WIN_STREAK': 3,
            'HOME_WIN_PCT': 0.55,
            'AWAY_WIN_PCT': 0.58,
        }
    else:
        # Usar datos reales
        lakers_row = lakers_recent.iloc[0]
        celtics_row = celtics_recent.iloc[0]
        
        features = {
            'HOME_ELO_BEFORE': lakers_row.get('HOME_ELO_AFTER', 1500),
            'AWAY_ELO_BEFORE': celtics_row.get('AWAY_ELO_AFTER', 1500),
            'ELO_DIFF': lakers_row.get('HOME_ELO_AFTER', 1500) - celtics_row.get('AWAY_ELO_AFTER', 1500),
            'HOME_PTS_ROLL_5': lakers_row.get('HOME_PTS_ROLL_5', 110),
            'AWAY_PTS_ROLL_5': celtics_row.get('AWAY_PTS_ROLL_5', 110),
            'HOME_FG_PCT_ROLL_5': lakers_row.get('HOME_FG_PCT_ROLL_5', 0.45),
            'AWAY_FG_PCT_ROLL_5': celtics_row.get('AWAY_FG_PCT_ROLL_5', 0.45),
            'HOME_FG3_PCT_ROLL_5': lakers_row.get('HOME_FG3_PCT_ROLL_5', 0.35),
            'AWAY_FG3_PCT_ROLL_5': celtics_row.get('AWAY_FG3_PCT_ROLL_5', 0.35),
            'HOME_REB_ROLL_5': lakers_row.get('HOME_REB_ROLL_5', 45),
            'AWAY_REB_ROLL_5': celtics_row.get('AWAY_REB_ROLL_5', 45),
            'HOME_AST_ROLL_5': lakers_row.get('HOME_AST_ROLL_5', 25),
            'AWAY_AST_ROLL_5': celtics_row.get('AWAY_AST_ROLL_5', 25),
            'HOME_TOV_ROLL_5': lakers_row.get('HOME_TOV_ROLL_5', 14),
            'AWAY_TOV_ROLL_5': celtics_row.get('AWAY_TOV_ROLL_5', 14),
            'HOME_PTS_ROLL_10': lakers_row.get('HOME_PTS_ROLL_10', 110),
            'AWAY_PTS_ROLL_10': celtics_row.get('AWAY_PTS_ROLL_10', 110),
            'HOME_REST_DAYS': 2,
            'AWAY_REST_DAYS': 2,
            'HOME_BACK_TO_BACK': 0,
            'AWAY_BACK_TO_BACK': 0,
            'HOME_WIN_STREAK': lakers_row.get('HOME_WIN_STREAK', 0),
            'AWAY_WIN_STREAK': celtics_row.get('AWAY_WIN_STREAK', 0),
            'HOME_WIN_PCT': lakers_row.get('HOME_WIN_PCT', 0.5),
            'AWAY_WIN_PCT': celtics_row.get('AWAY_WIN_PCT', 0.5),
        }
    
    # Predecir
    prediction = predictor.predict_game(
        home_team='Los Angeles Lakers',
        away_team='Boston Celtics',
        features=features
    )
    
    # 4. Mostrar resultados
    print("\n" + "="*70)
    print("  📊 RESULTADOS DE LA PREDICCIÓN")
    print("="*70)
    
    print(f"\n🏠 {prediction['home_team']}")
    print(f"   Probabilidad de victoria: {prediction['home_win_probability']*100:.1f}%")
    print(f"   Puntos predichos: {prediction['predicted_home_score']:.0f}")
    
    print(f"\n✈️  {prediction['away_team']}")
    print(f"   Probabilidad de victoria: {prediction['away_win_probability']*100:.1f}%")
    print(f"   Puntos predichos: {prediction['predicted_away_score']:.0f}")
    
    print(f"\n📈 Marcador predicho: {prediction['predicted_home_score']:.0f} - {prediction['predicted_away_score']:.0f}")
    print(f"📊 Margen esperado: {abs(prediction['predicted_margin']):.1f} puntos")
    print(f"🔢 Total de puntos: {prediction['predicted_total']:.0f}")
    
    # Determinar favorito
    if prediction['home_win_probability'] > 0.5:
        favorite = prediction['home_team']
        prob = prediction['home_win_probability']
    else:
        favorite = prediction['away_team']
        prob = prediction['away_win_probability']
    
    print(f"\n⭐ Favorito: {favorite} ({prob*100:.1f}%)")
    
    # 5. Ejemplo de predicción en batch
    print("\n" + "="*70)
    print("  📦 PREDICCIONES EN BATCH (últimos 5 partidos)")
    print("="*70)
    
    recent_games = df.tail(5)
    X_recent = recent_games[predictor.feature_columns]
    
    predictions_batch = predictor.predict(X_recent)
    
    print("\n{:<30} {:<30} {:<15}".format("Local", "Visitante", "Prob. Local"))
    print("-"*70)
    
    for idx, (_, game) in enumerate(recent_games.iterrows()):
        home_team = game['HOME_TEAM_NAME']
        away_team = game['AWAY_TEAM_NAME']
        prob = predictions_batch['win_probability'][idx]
        actual = "✅" if game['HOME_WL'] == 1 else "❌"
        
        print("{:<30} {:<30} {:>6.1f}% {}".format(
            home_team[:28], 
            away_team[:28], 
            prob * 100,
            actual
        ))
    
    print("\n" + "="*70)
    print("  ✅ EJEMPLO COMPLETADO")
    print("="*70)
    
    print("\n💡 Próximos pasos:")
    print("   - Ejecuta: streamlit run dashboard/app.py")
    print("   - Abre: notebooks/01_exploratory_data_analysis.ipynb")
    print("   - Lee: QUICKSTART.md para más información")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
