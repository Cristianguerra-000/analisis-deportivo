"""Script para preparar datos ligeros para despliegue en Streamlit Cloud."""

import pandas as pd
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("📦 PREPARANDO DATOS PARA DESPLIEGUE")
print("=" * 70)

# Cargar datos completos
try:
    df_full = pd.read_parquet('data/processed/games_with_features.parquet')
    print(f"\n✅ Datos completos cargados: {len(df_full)} partidos, {df_full.shape[1]} columnas")
except FileNotFoundError:
    print("❌ No se encontró games_with_features.parquet")
    sys.exit(1)

# Seleccionar solo columnas esenciales para predicción
essential_columns = [
    'GAME_DATE',
    'HOME_TEAM_NAME',
    'AWAY_TEAM_NAME',
    'HOME_PTS',
    'AWAY_PTS',
    'HOME_WL',  # Necesario para el modelo
    'POINT_DIFF',  # Necesario para el modelo
    'TOTAL_PTS',  # Necesario para el modelo
    'HOME_ELO_BEFORE',
    'AWAY_ELO_BEFORE',
    'HOME_ELO_AFTER',
    'AWAY_ELO_AFTER',
    'ELO_DIFF',
    'HOME_PTS_ROLL_5',
    'AWAY_PTS_ROLL_5',
    'HOME_FG_PCT_ROLL_5',
    'AWAY_FG_PCT_ROLL_5',
    'HOME_FG3_PCT_ROLL_5',
    'AWAY_FG3_PCT_ROLL_5',
    'HOME_STL_ROLL_5',
    'AWAY_STL_ROLL_5',
    'HOME_BLK_ROLL_5',
    'AWAY_BLK_ROLL_5',
    'HOME_REB_ROLL_5',
    'AWAY_REB_ROLL_5',
    'HOME_AST_ROLL_5',
    'AWAY_AST_ROLL_5',
    'HOME_REST_DAYS',
    'AWAY_REST_DAYS',
    'HOME_WIN_STREAK',
    'AWAY_WIN_STREAK',
    'HOME_WIN_PCT',
    'AWAY_WIN_PCT',
]

# Filtrar columnas que existen
available_columns = [col for col in essential_columns if col in df_full.columns]
print(f"\n📋 Columnas seleccionadas: {len(available_columns)}")

# Crear DataFrame reducido
df_lite = df_full[available_columns].copy()

# IMPORTANTE: Filtrar solo partidos hasta HOY (eliminar proyecciones futuras)
from datetime import datetime
today = pd.Timestamp(datetime.now())
df_lite = df_lite[pd.to_datetime(df_lite['GAME_DATE']) <= today]

print(f"\n🗓️  Partidos filtrados hasta hoy: {len(df_lite)}")

# Tomar los últimos 2000 partidos históricos
df_lite = df_lite.sort_values('GAME_DATE').tail(2000)

print(f"\n📉 Datos reducidos: {len(df_lite)} partidos, {df_lite.shape[1]} columnas")
print(f"📅 Rango: {df_lite['GAME_DATE'].min()} a {df_lite['GAME_DATE'].max()}")

# Guardar en formato comprimido
output_path = 'data/deployment_data.parquet'
df_lite.to_parquet(output_path, compression='gzip', index=False)

# Calcular tamaño
import os
size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n💾 Archivo guardado: {output_path}")
print(f"📦 Tamaño: {size_mb:.2f} MB")

print("\n" + "=" * 70)
print("✅ DATOS PREPARADOS PARA DESPLIEGUE")
print("=" * 70)
print(f"\n💡 Ahora ejecuta: git add {output_path}")
print(f"                   git commit -m 'Agregar datos para despliegue'")
print(f"                   git push")
