"""
Punto de entrada para Streamlit Cloud
Importa el dashboard NBA simplificado
"""
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar y ejecutar el dashboard NBA
from src.dashboard.nba_dashboard import main

if __name__ == "__main__":
    main()
