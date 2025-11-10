"""
Punto de entrada para Streamlit Cloud
Importa la aplicación principal desde src/dashboard/
"""
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar y ejecutar la app principal
from src.dashboard.multi_sport_app import main

if __name__ == "__main__":
    main()
