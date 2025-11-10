"""Script para descargar datos de la NBA."""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.data_loader import NBADataLoader
import argparse


def main():
    parser = argparse.ArgumentParser(description="Descargar datos de partidos NBA")
    parser.add_argument(
        "--seasons",
        nargs="+",
        default=["2022-23", "2023-24", "2024-25"],
        help="Temporadas a descargar (formato: 2024-25)"
    )
    parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Directorio donde guardar los datos"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏀 NBA DATA DOWNLOADER")
    print("=" * 60)
    print(f"\nTemporadas a descargar: {', '.join(args.seasons)}")
    print(f"Directorio de salida: {args.data_dir}\n")
    
    loader = NBADataLoader(data_dir=args.data_dir)
    
    # Descargar todas las temporadas
    all_games = loader.download_multiple_seasons(args.seasons, save=True)
    
    if not all_games.empty:
        print("\n" + "=" * 60)
        print("✅ DESCARGA COMPLETADA")
        print("=" * 60)
        print(f"\nTotal de partidos: {len(all_games)}")
        print(f"Rango de fechas: {all_games['GAME_DATE'].min().strftime('%Y-%m-%d')} a {all_games['GAME_DATE'].max().strftime('%Y-%m-%d')}")
        print(f"\nEquipos únicos: {all_games['HOME_TEAM_NAME'].nunique()}")
        
        # Estadísticas básicas
        print(f"\n📊 Estadísticas básicas:")
        print(f"  - Puntos promedio local: {all_games['HOME_PTS'].mean():.1f}")
        print(f"  - Puntos promedio visitante: {all_games['AWAY_PTS'].mean():.1f}")
        print(f"  - % victorias local: {all_games['HOME_WL'].mean()*100:.1f}%")
        print(f"  - Puntos totales promedio: {all_games['TOTAL_PTS'].mean():.1f}")
        
    else:
        print("\n❌ No se pudieron descargar datos")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
