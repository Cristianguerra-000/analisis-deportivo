"""Script para entrenar modelos de predicción."""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.predictor import NBAPredictor
import argparse


def main():
    parser = argparse.ArgumentParser(description="Entrenar modelos de predicción NBA")
    parser.add_argument(
        "--data",
        default="data/processed/games_with_features.parquet",
        help="Archivo con datos procesados"
    )
    parser.add_argument(
        "--output",
        default="models/nba_predictor_baseline.joblib",
        help="Donde guardar el modelo entrenado"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proporción de datos para test (default: 0.2)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏋️  ENTRENAMIENTO DE MODELOS NBA")
    print("=" * 60)
    
    # Cargar datos
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"\n❌ Archivo no encontrado: {data_path}")
        print("\nPrimero ejecuta:")
        print("  1. python scripts/download_nba_data.py")
        print("  2. python scripts/process_features.py")
        return 1
    
    print(f"\n📂 Cargando datos desde: {data_path}")
    df = pd.read_parquet(data_path)
    print(f"✅ Cargados {len(df)} partidos con {df.shape[1]} features")
    
    # Entrenar modelos
    predictor = NBAPredictor()
    metrics = predictor.train(df, test_size=args.test_size)
    
    # Guardar
    print(f"\n💾 Guardando modelos en: {args.output}")
    predictor.save(args.output)
    
    print("\n" + "=" * 60)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    print("\nPara usar los modelos:")
    print("  - Dashboard: streamlit run dashboard/app.py")
    print("  - API: python src/api/server.py")
    print("  - Notebook: notebooks/05_make_predictions.ipynb")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
