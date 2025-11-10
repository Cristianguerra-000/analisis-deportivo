"""Script para procesar datos crudos y generar features."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.data_loader import NBADataLoader
from src.features.feature_engineering import NBAFeatureEngineer
import argparse


def main():
    parser = argparse.ArgumentParser(description="Procesar datos y generar features")
    parser.add_argument(
        "--input",
        default="data/raw/games_all_seasons.csv",
        help="Archivo de entrada con datos crudos"
    )
    parser.add_argument(
        "--output",
        default="data/processed/games_with_features.parquet",
        help="Archivo de salida con features"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("⚙️  NBA FEATURE ENGINEERING")
    print("=" * 60)
    
    # Cargar datos
    print(f"\n📂 Cargando datos desde: {args.input}")
    loader = NBADataLoader()
    games_df = loader.load_local_data(Path(args.input).name)
    
    if games_df.empty:
        print("❌ No se pudieron cargar los datos")
        return 1
    
    print(f"✅ Cargados {len(games_df)} partidos")
    
    # Generar features
    print("\n🔧 Procesando features...")
    engineer = NBAFeatureEngineer()
    games_with_features = engineer.create_all_features(games_df)
    
    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    games_with_features.to_parquet(output_path, index=False)
    
    print("\n" + "=" * 60)
    print("✅ PROCESAMIENTO COMPLETADO")
    print("=" * 60)
    print(f"\nDatos guardados en: {output_path}")
    print(f"Total de features: {games_with_features.shape[1]} columnas")
    print(f"Total de partidos: {len(games_with_features)}")
    
    # Mostrar algunas features importantes
    feature_cols = [col for col in games_with_features.columns if 'ELO' in col or 'ROLL' in col or 'STREAK' in col]
    print(f"\n📊 Algunas features generadas:")
    for col in feature_cols[:10]:
        print(f"  - {col}")
    
    if len(feature_cols) > 10:
        print(f"  ... y {len(feature_cols) - 10} más")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
