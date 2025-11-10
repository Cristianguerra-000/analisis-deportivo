# 🚀 Guía de Despliegue en la Nube

## Opción 1: Streamlit Community Cloud (RECOMENDADO - GRATIS)

### Paso 1: Preparar el Repositorio Git

```bash
# Inicializar git (si no está inicializado)
git init

# Añadir todos los archivos
git add .

# Hacer commit
git commit -m "Preparar para despliegue en Streamlit Cloud"

# Crear repositorio en GitHub
# Ir a https://github.com/new y crear repositorio público

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/analisis-deportivo.git
git branch -M main
git push -u origin main
```

### Paso 2: Desplegar en Streamlit Cloud

1. **Ir a**: https://share.streamlit.io/
2. **Sign in** con tu cuenta de GitHub
3. **Click en "New app"**
4. **Seleccionar**:
   - Repository: `TU_USUARIO/analisis-deportivo`
   - Branch: `main`
   - Main file path: `src/dashboard/multi_sport_app.py`
5. **Advanced settings** (opcional):
   - Python version: `3.11` (Streamlit Cloud no soporta 3.14 aún)
   - Añadir secrets si tienes API keys

### Paso 3: Configurar Secrets (API Keys)

En Streamlit Cloud, ve a **App settings > Secrets** y añade:

```toml
FOOTBALL_API_KEY = "tu_api_key_aqui"
```

### Paso 4: ¡Listo! 🎉

Tu app estará disponible en: `https://tu-usuario-analisis-deportivo.streamlit.app`

---

## Opción 2: Render (Alternativa Gratuita)

### Paso 1: Crear cuenta en Render
- Ir a: https://render.com/
- Sign up con GitHub

### Paso 2: Crear Web Service
1. Click en **"New +"** > **"Web Service"**
2. Conectar tu repositorio de GitHub
3. Configurar:
   - **Name**: `analisis-deportivo`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run src/dashboard/multi_sport_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Plan**: Free

### Paso 3: Variables de Entorno
- Añadir: `FOOTBALL_API_KEY` = tu_key

---

## Opción 3: Railway (Muy Fácil)

### Paso 1: Crear cuenta
- Ir a: https://railway.app/
- Sign up con GitHub

### Paso 2: Deploy
1. Click **"New Project"**
2. **"Deploy from GitHub repo"**
3. Seleccionar tu repositorio
4. Railway detecta automáticamente que es Streamlit
5. **Variables de entorno**: Añadir `FOOTBALL_API_KEY`

---

## Opción 4: Google Cloud Run (Escalable)

### Paso 1: Crear Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD streamlit run src/dashboard/multi_sport_app.py --server.port=8080 --server.address=0.0.0.0
```

### Paso 2: Desplegar

```bash
# Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Crear proyecto
gcloud projects create analisis-deportivo

# Configurar proyecto
gcloud config set project analisis-deportivo

# Habilitar Cloud Run API
gcloud services enable run.googleapis.com

# Build y deploy
gcloud run deploy analisis-deportivo \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FOOTBALL_API_KEY=tu_key
```

---

## 📊 Comparación de Opciones

| Plataforma | Precio | RAM | CPU | Uptime | Dificultad |
|------------|--------|-----|-----|--------|------------|
| **Streamlit Cloud** | Gratis | 1GB | Compartido | 100% | ⭐ Muy Fácil |
| **Render** | Gratis | 512MB | Compartido | Se duerme | ⭐⭐ Fácil |
| **Railway** | $5/mes | 8GB | 8vCPU | 100% | ⭐⭐ Fácil |
| **Google Cloud Run** | Pay-as-you-go | 4GB | 2vCPU | 100% | ⭐⭐⭐ Medio |
| **Heroku** | $7/mes | 512MB | 1vCPU | 100% | ⭐⭐ Fácil |

---

## 🔧 Ajustes para Producción

### 1. Optimizar requirements.txt

Crear `requirements-prod.txt` sin dependencias de desarrollo:

```txt
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
streamlit>=1.29.0
plotly>=5.18.0
requests>=2.31.0
pyarrow>=14.0.0
python-dotenv>=1.0.0
joblib>=1.3.0
```

### 2. Configurar .gitignore

```gitignore
# No subir datos pesados
data/*.parquet
data/*.csv

# No subir modelos grandes (opcional)
models/*.joblib

# Archivos locales
.env
.venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
```

### 3. Usar secretos para API keys

```python
# En tu código, cambiar:
# API_KEY = os.getenv("FOOTBALL_API_KEY")

# Por:
import streamlit as st

try:
    API_KEY = st.secrets["FOOTBALL_API_KEY"]
except:
    API_KEY = os.getenv("FOOTBALL_API_KEY")
```

### 4. Cachear datos

```python
@st.cache_data(ttl=3600)  # Cachear 1 hora
def load_data():
    return pd.read_parquet('data/nba_games.parquet')
```

---

## ⚠️ Limitaciones a Considerar

### Streamlit Cloud (Gratis)
- ✅ Perfecto para prototipos y demos
- ⚠️ 1GB RAM (puede quedarse sin memoria con datasets grandes)
- ⚠️ No soporta Python 3.14 (usar 3.11)
- ⚠️ Se reinicia después de inactividad

### Solución para datasets grandes:
1. **Subir datos a Google Drive/Dropbox**
2. **Cargar desde URL**:
```python
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=TU_FILE_ID"
    return pd.read_parquet(url)
```

---

## 🎯 Mi Recomendación

Para tu caso específico:

1. **Para empezar**: **Streamlit Community Cloud**
   - Gratis, fácil, perfecto para demos
   - Comparte el link con amigos/familia

2. **Si crece**: **Railway ($5/mes)**
   - Más recursos (8GB RAM)
   - Bases de datos incluidas
   - Sin límites de tiempo de ejecución

3. **Largo plazo**: **Google Cloud Run**
   - Pagas solo por uso
   - Escala automáticamente
   - Muy confiable

---

## 🚀 Siguiente Paso

¿Quieres que te ayude a:

1. **Subir a GitHub y desplegar en Streamlit Cloud** (15 minutos)
2. **Crear Dockerfile para Docker/Railway** (20 minutos)
3. **Optimizar el código para reducir uso de RAM** (30 minutos)

¿Cuál prefieres? 🤔
