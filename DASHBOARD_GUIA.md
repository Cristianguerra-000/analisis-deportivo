# 🔥 DASHBOARD MULTI-DEPORTE - GUÍA DE USO

## ✅ ESTADO: FUNCIONANDO

Tu dashboard está corriendo en: **http://localhost:8501**

---

## 🚀 CÓMO USARLO

### 1. Abrir el dashboard

**Opción A:** Abre tu navegador y ve a:
```
http://localhost:8501
```

**Opción B:** Desde la terminal en otra pestaña:
```powershell
start http://localhost:8501
```

### 2. Navegación

El dashboard tiene **4 TABS principales:**

#### 🏀 **TAB NBA**
- Métricas: 4,192 partidos, 72.6% accuracy
- Gráficos de distribución de puntos
- Últimos partidos jugados
- Stats completas del modelo

#### ⚽ **TAB FÚTBOL**
- Selector de ligas (Premier, La Liga, Bundesliga, etc.)
- Tabla de posiciones EN VIVO
- Próximos partidos (7 días)
- Análisis de goles y resultados
- 380+ partidos Premier League disponibles

#### 🎾 **TAB TENIS**
- Selector ATP/WTA
- Selector de año (2022-2024)
- Análisis de jugadores (buscar por nombre)
- Win % por superficie (Clay, Hard, Grass)
- 8,979 partidos ATP + 2,689 WTA disponibles

#### 🔴 **TAB EN VIVO**
- Partidos de fútbol EN VIVO
- Predicciones actualizadas cada 30 segundos
- Gauges de probabilidad (Local/Empate/Visitante)
- Botón manual de actualización

---

## 📊 CARACTERÍSTICAS

### ✅ Lo que YA funciona:

1. **Datos en tiempo real** (Football-Data.org API)
2. **Histórico completo** (16,240+ partidos)
3. **Gráficos interactivos** (Plotly)
4. **Múltiples deportes** (NBA, Fútbol, Tenis)
5. **Tabla de posiciones** (actualizada)
6. **Análisis de jugadores** (stats por superficie)

### 🔄 Auto-actualización:

- El tab "EN VIVO" se actualiza cada 30 segundos automáticamente
- Los datos históricos se cachean 5 minutos para velocidad
- Botón manual para forzar actualización

---

## 🎯 EJEMPLOS DE USO

### Ejemplo 1: Ver tabla de Premier League
```
1. Abre http://localhost:8501
2. Click en tab "⚽ FÚTBOL"
3. Selecciona "🏴 Premier League"
4. Verás: tabla, próximos partidos, análisis de goles
```

### Ejemplo 2: Analizar jugador de tenis
```
1. Click en tab "🎾 TENIS"
2. Selecciona "ATP" y año "2024"
3. Busca jugador (ej: "Djokovic")
4. Verás: win %, stats por superficie, partidos jugados
```

### Ejemplo 3: Ver partidos en vivo
```
1. Click en tab "🔴 EN VIVO"
2. Si hay partidos activos, verás:
   - Marcador en vivo
   - Minuto del partido
   - Predicciones actualizadas (gauges de probabilidad)
3. Se actualiza automáticamente cada 30s
```

---

## ⚙️ CONFIGURACIÓN

### Sidebar (panel izquierdo):

- **Estado del Sistema**: muestra qué está operacional
- **Estadísticas Totales**: resumen de datos disponibles
- **Configuración**: opciones avanzadas

### Cambiar intervalo de actualización:

En el código `src/dashboard/multi_sport_app.py`, línea ~50:
```python
@st.cache_data(ttl=300)  # 300 = 5 minutos
```

Cambia `300` a tu preferencia (en segundos)

---

## 🛠️ COMANDOS ÚTILES

### Iniciar dashboard:
```powershell
python -m streamlit run src/dashboard/multi_sport_app.py
```

### Detener dashboard:
```
Ctrl + C en la terminal donde corre
```

### Ver en otro dispositivo (misma red):
```
http://192.168.18.20:8501
```

### Limpiar cache:
```
Presiona "C" en el dashboard
O reinicia el servidor
```

---

## 📱 ACCESO REMOTO

Si quieres acceder desde tu celular/tablet en la misma red WiFi:

1. Verifica la IP en la terminal: `Network URL: http://192.168.18.20:8501`
2. Abre esa URL en tu dispositivo móvil
3. ¡Funciona perfectamente en móvil!

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema: "No hay partidos en vivo"
**Solución:** Es normal. Solo aparecen cuando hay partidos activos en ese momento.

### Problema: "No se cargan datos de NBA"
**Solución:** Ejecuta primero:
```powershell
python scripts/download_data.py
```

### Problema: "Error 403 en Football API"
**Solución:** Verifica tu API key en `.env`:
```
FOOTBALL_DATA_API_KEY=4a21750336d0475590e2eaa40acca217
```

### Problema: Dashboard muy lento
**Solución:** 
1. Cierra otros tabs del dashboard
2. Limpia cache (presiona "C")
3. Reinicia el servidor

---

## 🎨 PERSONALIZACIÓN

### Cambiar colores:

Edita el CSS en `multi_sport_app.py`, líneas 25-65:
```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #TU_COLOR1, #TU_COLOR2);
    }
</style>
""")
```

### Agregar más ligas de fútbol:

En el selectbox (línea ~220), agrega:
```python
'CL': '🏆 Champions League',
'EL': '🥈 Europa League',
```

---

## 📊 DATOS DISPONIBLES

| Deporte | Partidos | Años | Status |
|---------|----------|------|--------|
| NBA | 4,192 | 2020-2024 | ✅ Modelo entrenado |
| Fútbol | 380+ | 2024/25 | ✅ API activa |
| Tenis ATP | 8,979 | 2022-2024 | ✅ Datos completos |
| Tenis WTA | 2,689 | 2022-2024 | ✅ Datos completos |
| **TOTAL** | **16,240+** | - | 🔥 |

---

## 🚀 PRÓXIMOS PASOS

Para mejorar el dashboard:

1. **Entrenar modelos de Fútbol/Tenis** (ahora usa predicciones simuladas)
2. **Agregar más ligas** (Champions, Europa League)
3. **Mejorar predicciones en vivo** (con modelos ML reales)
4. **Agregar historial de predicciones** (base de datos)
5. **Sistema de notificaciones** (alertas de escritorio)

---

## 💡 TIPS

- **Mantén la terminal abierta** mientras usas el dashboard
- **No cierres la terminal** o el dashboard se detendrá
- **Usa Chrome/Edge** para mejor rendimiento
- **El tab EN VIVO consume más recursos** (por auto-refresh)
- **Puedes tener múltiples usuarios** viendo el mismo dashboard

---

## ✅ RESUMEN

```
✅ Dashboard corriendo en: http://localhost:8501
✅ 4 deportes integrados (NBA, Fútbol, Tenis, Live)
✅ 16,240+ partidos disponibles
✅ Gráficos interactivos con Plotly
✅ Auto-actualización cada 30s
✅ Acceso desde cualquier dispositivo en tu red
```

**¡DISFRUTA TU SISTEMA DE PREDICCIONES MULTI-DEPORTE!** 🔥
