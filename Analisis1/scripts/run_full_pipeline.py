"""Script maestro para ejecutar el pipeline completo de análisis NBA."""

import sys
import subprocess
from pathlib import Path
import time

def print_header(text):
    """Imprime un header formateado."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(description, command):
    """Ejecuta un comando y maneja errores."""
    print(f"▶️  {description}")
    print(f"   Comando: {command}\n")
    
    result = subprocess.run(command, shell=True, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error ejecutando: {description}")
        return False
    
    print(f"✅ {description} - Completado\n")
    return True

def main():
    print_header("🏀 NBA PREDICTOR - PIPELINE COMPLETO")
    
    # Verificar que estamos en el directorio correcto
    if not Path("README.md").exists():
        print("❌ Error: Ejecuta este script desde la raíz del proyecto (Analisis/)")
        return 1
    
    # Paso 1: Instalar dependencias
    print_header("1️⃣ INSTALACIÓN DE DEPENDENCIAS")
    print("📦 Instalando paquetes de Python...")
    
    if not run_command(
        "Instalación de dependencias",
        "pip install -r requirements.txt"
    ):
        print("\n⚠️  Algunas dependencias pueden haber fallado.")
        print("   Esto es normal si algunos paquetes ya están instalados.")
        print("   Continuando con el pipeline...\n")
        time.sleep(2)
    
    # Paso 2: Descargar datos
    print_header("2️⃣ DESCARGA DE DATOS NBA")
    
    if not run_command(
        "Descarga de datos de temporadas 2022-25",
        "python scripts/download_nba_data.py --seasons 2022-23 2023-24 2024-25"
    ):
        print("❌ No se pudieron descargar los datos")
        print("   Verifica tu conexión a internet y que nba_api esté instalado")
        return 1
    
    # Paso 3: Procesar features
    print_header("3️⃣ PROCESAMIENTO Y FEATURE ENGINEERING")
    
    if not run_command(
        "Generación de features avanzadas",
        "python scripts/process_features.py"
    ):
        print("❌ Error procesando features")
        return 1
    
    # Paso 4: Entrenar modelos
    print_header("4️⃣ ENTRENAMIENTO DE MODELOS")
    
    if not run_command(
        "Entrenamiento de modelos baseline",
        "python scripts/train_models.py --test-size 0.2"
    ):
        print("❌ Error entrenando modelos")
        return 1
    
    # Resumen final
    print_header("✅ PIPELINE COMPLETADO EXITOSAMENTE")
    
    print("📊 Archivos generados:")
    print("   ✓ data/raw/games_*.csv - Datos crudos descargados")
    print("   ✓ data/processed/games_with_features.parquet - Datos procesados")
    print("   ✓ models/nba_predictor_baseline.joblib - Modelos entrenados")
    
    print("\n🚀 Próximos pasos:")
    print("\n1. Explorar datos:")
    print("   jupyter notebook notebooks/01_exploratory_data_analysis.ipynb")
    
    print("\n2. Ejecutar dashboard interactivo:")
    print("   streamlit run dashboard/app.py")
    
    print("\n3. Hacer predicciones individuales:")
    print("   python -c \"")
    print("   from src.models.predictor import NBAPredictor")
    print("   predictor = NBAPredictor()")
    print("   predictor.load('models/nba_predictor_baseline.joblib')")
    print("   # ... hacer predicciones")
    print("   \"")
    
    print("\n" + "="*70)
    print("🎉 ¡Sistema NBA Predictor listo para usar!")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)
