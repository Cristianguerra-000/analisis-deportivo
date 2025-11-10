"""
Script para descargar datos de NBA (si no existen)
Usa el data_loader existente del proyecto NBA
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from pathlib import Path

def download_nba_data():
    """Descarga o verifica datos de NBA"""
    
    print("\n" + "="*60)
    print("VERIFICANDO DATOS NBA")
    print("="*60 + "\n")
    
    # Verificar si ya existen datos
    data_path = Path('data/nba_games.parquet')
    
    if data_path.exists():
        print(f"✅ Datos NBA ya existen: {data_path}")
        
        # Cargar y mostrar info
        df = pd.read_parquet(data_path)
        print(f"   Partidos: {len(df):,}")
        
        if 'game_date' in df.columns:
            print(f"   Rango fechas: {df['game_date'].min()} a {df['game_date'].max()}")
        
        print("\n✅ No es necesario descargar. Datos listos.")
        return True
    
    else:
        print("⚠️ No se encontraron datos de NBA en data/nba_games.parquet")
        print("\nOPCIONES:")
        print("1. Si tienes datos NBA previos, cópialos a: data/nba_games.parquet")
        print("2. O ejecuta el script original de descarga NBA")
        print("3. El dashboard funcionará sin NBA (solo Fútbol y Tenis)")
        
        # Crear directorio data si no existe
        Path('data').mkdir(exist_ok=True)
        
        # Crear archivo dummy para que el dashboard no falle
        print("\n📝 Creando archivo placeholder...")
        df_dummy = pd.DataFrame({
            'game_date': pd.date_range('2024-01-01', periods=10),
            'home_team': ['Team A'] * 10,
            'away_team': ['Team B'] * 10,
            'home_score': [100, 105, 98, 110, 95, 102, 108, 99, 104, 107],
            'away_score': [98, 102, 100, 105, 97, 99, 106, 101, 102, 105],
        })
        
        df_dummy.to_parquet(data_path)
        print(f"✅ Creado: {data_path} (datos de ejemplo)")
        print("   El dashboard funcionará, pero mostrará datos de ejemplo para NBA")
        
        return False


if __name__ == "__main__":
    download_nba_data()
    
    print("\n" + "="*60)
    print("SIGUIENTE PASO")
    print("="*60)
    print("\nPara iniciar el dashboard:")
    print("   python -m streamlit run src/dashboard/multi_sport_app.py")
    print("   O ejecuta: .\\start_dashboard.ps1\n")
