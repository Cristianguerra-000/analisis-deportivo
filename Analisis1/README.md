# Sistema Avanzado de Análisis y Predicción NBA

Sistema de análisis estadístico y modelado probabilístico para predecir resultados de partidos de la NBA.

## 🎯 Características

- **Predicciones probabilísticas**:
  - Probabilidad de victoria (equipo local vs visitante)
  - Margen de puntos esperado
  - Over/Under de puntos totales
  
- **Features avanzadas**:
  - Sistema ELO dinámico
  - Rolling statistics (últimos 5, 10, 20 partidos)
  - Home court advantage
  - Análisis de back-to-back games
  - Days of rest
  - Eficiencia ofensiva/defensiva
  - Ritmo de juego (pace)

- **Modelos**:
  - Baseline: Logistic Regression + Poisson
  - Avanzado: XGBoost / LightGBM
  - Calibración de probabilidades
  - Backtesting temporal

- **Visualización**:
  - Dashboard interactivo (Streamlit)
  - API REST para predicciones
  - Notebooks de análisis exploratorio

## 📁 Estructura del proyecto

```
Analisis/
├── data/
│   ├── raw/              # Datos crudos descargados
│   ├── processed/        # Datos procesados con features
│   └── predictions/      # Predicciones generadas
├── src/
│   ├── data/            # Módulos de ingesta y ETL
│   ├── features/        # Feature engineering
│   ├── models/          # Definiciones de modelos
│   ├── evaluation/      # Métricas y validación
│   └── api/             # API REST
├── notebooks/           # Jupyter notebooks para EDA
├── tests/              # Tests unitarios
├── dashboard/          # Streamlit app
├── configs/            # Archivos de configuración
└── scripts/            # Scripts de setup y ejecución
```

## 🚀 Quick Start

### 1. Instalación

```powershell
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Descargar datos

```powershell
python scripts/download_nba_data.py --seasons 2022-23 2023-24 2024-25
```

### 3. Entrenar modelos

```powershell
python scripts/train_models.py --model all
```

### 4. Ejecutar dashboard

```powershell
streamlit run dashboard/app.py
```

### 5. API (opcional)

```powershell
python src/api/server.py
```

## 📊 Métricas de evaluación

- **Log Loss**: Calidad de probabilidades predichas
- **Brier Score**: Calibración de probabilidades
- **AUC-ROC**: Discriminación victoria/derrota
- **MAE**: Error absoluto medio en margen de puntos
- **R²**: Varianza explicada en puntos totales

## 🔧 Configuración

Edita `configs/config.yaml` para personalizar:
- Temporadas a analizar
- Hiperparámetros de modelos
- Features a utilizar
- Umbrales de probabilidad

## 📈 Uso avanzado

Ver notebooks en `notebooks/`:
- `01_exploratory_data_analysis.ipynb`: EDA completo
- `02_feature_engineering.ipynb`: Creación de features
- `03_model_baseline.ipynb`: Modelos baseline
- `04_advanced_models.ipynb`: Modelos ML avanzados
- `05_backtesting.ipynb`: Validación temporal

## ⚠️ Disclaimer

Este sistema es únicamente para **análisis educativo y estadístico**. No debe ser utilizado para actividades de apuestas comerciales sin las licencias apropiadas y el cumplimiento de las regulaciones locales.

## 📝 Licencia

MIT License - Uso educativo y de investigación

---
**Desarrollado**: Noviembre 2025  
**Stack**: Python 3.10+, Pandas, scikit-learn, XGBoost, Streamlit
