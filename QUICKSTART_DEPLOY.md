# 🚀 GUÍA RÁPIDA DE DESPLIEGUE

## ⚡ Despliegue en 5 Minutos (Streamlit Cloud)

### 1️⃣ Subir a GitHub

```bash
# Inicializar git (si no está inicializado)
git init

# Añadir archivos
git add .

# Commit
git commit -m "Sistema multi-deporte listo para producción"

# Crear repo en GitHub y conectar
git remote add origin https://github.com/TU_USUARIO/analisis-deportivo.git
git branch -M main
git push -u origin main
```

### 2️⃣ Desplegar en Streamlit Cloud

1. Ve a: **https://share.streamlit.io/**
2. Click **"New app"**
3. Selecciona tu repositorio: `TU_USUARIO/analisis-deportivo`
4. Branch: `main`
5. Main file: `src/dashboard/multi_sport_app.py`
6. Click **"Advanced settings"**:
   - Python version: `3.11`
   - Requirements file: `requirements-streamlit.txt`
7. En **Secrets**, añade:
   ```toml
   FOOTBALL_API_KEY = "tu_api_key_de_football-data.org"
   ```
8. Click **"Deploy"** ✅

### 3️⃣ ¡Listo! 🎉

Tu app estará en: `https://tu-usuario-analisis-deportivo.streamlit.app`

---

## 📱 Acceder desde tu Móvil/App

Una vez desplegado, puedes:

1. **Abrir desde cualquier navegador**:
   - Copia el link: `https://tu-app.streamlit.app`
   - Ábrelo en Chrome/Safari móvil
   - Funciona como una web responsive

2. **Crear acceso directo en móvil**:
   - **iPhone**: Safari > Share > "Add to Home Screen"
   - **Android**: Chrome > ⋮ > "Add to Home screen"
   - Se verá como una app nativa

3. **Compartir con otros**:
   - Envía el link por WhatsApp/Telegram
   - Cualquiera puede usarlo sin instalar nada

---

## 🔑 Obtener API Key de Football-Data.org

1. Ve a: https://www.football-data.org/client/register
2. Regístrate (gratis)
3. Confirma tu email
4. Ve a tu perfil y copia tu API key
5. Pégala en los "Secrets" de Streamlit Cloud

---

## 💡 Opciones de Despliegue

| Plataforma | Precio | RAM | Dificultad |
|------------|--------|-----|------------|
| **Streamlit Cloud** ⭐ | GRATIS | 1GB | Muy fácil |
| Railway | $5/mes | 8GB | Fácil |
| Render | GRATIS* | 512MB | Fácil |

*Se duerme tras 15min de inactividad

---

## ⚠️ Importante

- El archivo `requirements-streamlit.txt` está optimizado para la nube
- Streamlit Cloud usa Python 3.11 (no 3.14)
- Los datos grandes (`.parquet`) no se suben a Git por `.gitignore`
- El modelo `nba_predictor.joblib` SÍ se sube (es necesario)

---

## 🆘 Solución de Problemas

### ❌ Error: "File not found: nba_games_features.parquet"

**Solución**: El archivo es muy grande para GitHub. Opciones:

1. **Opción A**: Sube el archivo a Google Drive y carga desde URL
2. **Opción B**: Usa Git LFS para archivos grandes
3. **Opción C**: Genera los datos en el primer arranque

**Implementar Opción A** (recomendado):

```python
# En multi_sport_app.py, modificar load_nba_data():

@st.cache_data
def load_nba_data():
    try:
        # Intentar local primero
        df = pd.read_parquet('data/nba_games_features.parquet')
    except FileNotFoundError:
        # Cargar desde URL si no existe local
        url = "https://drive.google.com/uc?id=TU_FILE_ID"
        df = pd.read_parquet(url)
    return df
```

### ❌ Error: "Module not found"

- Asegúrate de usar `requirements-streamlit.txt`
- Verifica que todas las importaciones estén en el archivo

---

## 📞 ¿Necesitas Ayuda?

Avísame si:
- ✅ Quieres que suba automáticamente los datos a Drive
- ✅ Necesitas optimizar para 1GB de RAM
- ✅ Quieres configurar dominio personalizado
- ✅ Tienes errores al desplegar

¡Vamos a ponerlo online! 🚀
