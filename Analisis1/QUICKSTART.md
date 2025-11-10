# 🚀 Guía de Inicio Rápido - NBA Predictor

## Instalación y Setup

### 1. Crear entorno virtual (recomendado)

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si hay error de permisos en PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

**Nota**: La instalación puede tomar 5-10 minutos dependiendo de tu conexión.

## Pipeline Completo (Opción Automática)

Ejecuta todo el pipeline con un solo comando:

```powershell
python scripts/run_full_pipeline.py
```

Este script:
1. ✅ Instala dependencias
2. ✅ Descarga datos de la NBA (2022-2025)
3. ✅ Procesa y genera features
4. ✅ Entrena modelos
5. ✅ Te muestra los próximos pasos

**Tiempo estimado**: 10-20 minutos (depende de la API de la NBA)

---

## Pipeline Manual (Paso a Paso)

Si prefieres ejecutar cada paso manualmente:

### Paso 1: Descargar datos

```powershell
python scripts/download_nba_data.py --seasons 2022-23 2023-24 2024-25
```

### Paso 2: Procesar features

```powershell
python scripts/process_features.py
```

### Paso 3: Entrenar modelos

```powershell
python scripts/train_models.py --test-size 0.2
```

---

## Uso del Sistema

### 📊 Dashboard Interactivo (Recomendado)

```powershell
streamlit run dashboard/app.py
```

Abre tu navegador en `http://localhost:8501`

**Características**:
- 🎯 Predicciones interactivas de partidos
- 📈 Visualizaciones de datos
- 📊 Métricas del modelo
- 🏀 Análisis por equipo

### 📓 Análisis Exploratorio (Jupyter)

```powershell
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

### 🐍 Uso programático

```python
from src.models.predictor import NBAPredictor
import pandas as pd

# Cargar modelo entrenado
predictor = NBAPredictor()
predictor.load('models/nba_predictor_baseline.joblib')

# Cargar datos
df = pd.read_parquet('data/processed/games_with_features.parquet')

# Hacer predicción para un partido
features = {
    'HOME_ELO_BEFORE': 1600,
    'AWAY_ELO_BEFORE': 1500,
    'ELO_DIFF': 100,
    'HOME_PTS_ROLL_5': 115,
    'AWAY_PTS_ROLL_5': 108,
    # ... más features
}

prediction = predictor.predict_game(
    home_team='Los Angeles Lakers',
    away_team='Boston Celtics',
    features=features
)

print(f"Probabilidad victoria local: {prediction['home_win_probability']:.1%}")
print(f"Marcador predicho: {prediction['predicted_home_score']:.0f} - {prediction['predicted_away_score']:.0f}")
```

---

## Estructura de Archivos

```
Analisis/
├── data/
│   ├── raw/                          # Datos crudos de la API
│   │   ├── games_2022_23.csv
│   │   ├── games_2023_24.csv
│   │   └── games_2024_25.csv
│   └── processed/
│       └── games_with_features.parquet  # Datos procesados listos
│
├── models/
│   └── nba_predictor_baseline.joblib   # Modelos entrenados
│
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb  # EDA completo
│
├── scripts/
│   ├── download_nba_data.py            # Descargar datos
│   ├── process_features.py             # Feature engineering
│   ├── train_models.py                 # Entrenar modelos
│   └── run_full_pipeline.py            # Pipeline completo
│
├── src/
│   ├── data/
│   │   └── data_loader.py              # Carga de datos
│   ├── features/
│   │   └── feature_engineering.py      # Features avanzadas
│   └── models/
│       └── predictor.py                # Modelos predictivos
│
└── dashboard/
    └── app.py                          # Dashboard Streamlit
```

---

## Solución de Problemas

### Error: "nba_api no está instalado"

```powershell
pip install nba_api
```

### Error: "No se pudo conectar a la API"

- Verifica tu conexión a internet
- La API de la NBA puede tener rate limits
- Espera 1-2 minutos y reintenta

### Error: "Archivo no encontrado"

Asegúrate de estar en el directorio raíz del proyecto:

```powershell
cd c:\Users\guerr\Analisis
```

### Error de permisos en PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Reiniciar desde cero

```powershell
# Eliminar datos procesados
Remove-Item -Recurse -Force data/raw/*
Remove-Item -Recurse -Force data/processed/*
Remove-Item -Recurse -Force models/*

# Volver a ejecutar pipeline
python scripts/run_full_pipeline.py
```

---

## Métricas Esperadas

Con los datos de 2022-2025, deberías obtener:

- **Accuracy (Victoria)**: ~60-65%
- **Log Loss**: ~0.60-0.65
- **Brier Score**: ~0.23-0.25
- **ROC AUC**: ~0.65-0.70
- **MAE (Margen)**: ~10-12 puntos
- **MAE (Total)**: ~12-15 puntos

Estas métricas son competitivas con sistemas profesionales de predicción NBA.

---

## Próximos Pasos (Opcional)

### Mejorar el modelo

1. **Modelos avanzados**: Implementar XGBoost/LightGBM
2. **Más features**: Añadir lesiones, playoffs, clutch time
3. **Backtesting**: Validación temporal rigurosa
4. **Ensemble**: Combinar múltiples modelos

### Despliegue

1. **Dockerizar** la aplicación
2. **Deploy** en Railway/Render/Heroku
3. **Automatización** de actualización de datos
4. **API REST** para integraciones

---

## Soporte

Si encuentras problemas:

1. Revisa el README.md principal
2. Verifica que todos los archivos estén en su lugar
3. Asegúrate de tener Python 3.10+ instalado
4. Consulta la documentación de las bibliotecas usadas

---

**¡Disfruta analizando y prediciendo partidos de la NBA! 🏀**
