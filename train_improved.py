"""Script temporal para entrenar modelo mejorado con XGBoost."""
import sys
sys.path.insert(0, '.')

from src.models.nba_predictor import NBAPredictor
import pandas as pd

print("=" * 70)
print("🚀 ENTRENAMIENTO MEJORADO - XGBoost + Features Avanzadas")
print("=" * 70)

# Cargar datos
df = pd.read_parquet('data/processed/games_with_features.parquet')
print(f"\n📊 Datos cargados: {len(df)} partidos con {df.shape[1]} features")

# Entrenar
predictor = NBAPredictor()
metrics = predictor.train(df, test_size=0.2, random_state=42)

# Mostrar resultados
print("\n" + "=" * 70)
print("🎯 RESULTADO FINAL")
print("=" * 70)
print(f"✅ Precisión del Modelo: {metrics['win_accuracy']:.1%}")
print(f"📈 Mejora esperada: 72.6% → {metrics['win_accuracy']:.1%}")
print("=" * 70)

# Guardar
predictor.save('models/nba_predictor.joblib')
print("\n💾 Modelo guardado exitosamente en: models/nba_predictor.joblib")
