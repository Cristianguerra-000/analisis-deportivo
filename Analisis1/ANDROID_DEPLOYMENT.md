# 📱 Guía para Convertir NBA Predictor a App Android

## 🎯 Opciones Disponibles

Hay **3 opciones principales** para convertir tu sistema NBA Predictor en una app Android:

---

## ✅ **Opción 1: Progressive Web App (PWA) - MÁS FÁCIL**

### Ventajas
- ✅ **Más fácil y rápido** (1-2 horas)
- ✅ **No requiere Google Play Store**
- ✅ Funciona en Android, iOS y PC
- ✅ Se instala desde el navegador
- ✅ Actualizaciones automáticas

### Desventajas
- ❌ Requiere conexión a internet
- ❌ Acceso limitado a funciones nativas del teléfono

### Pasos para implementar:

#### 1. Deploy del Dashboard en la Nube

**Opción A: Streamlit Cloud (GRATIS)**

```powershell
# 1. Crear cuenta en Streamlit Cloud
# Ir a: https://streamlit.io/cloud

# 2. Conectar tu repositorio de GitHub
# (primero debes subir tu código a GitHub)

# 3. Deploy automático
# Streamlit Cloud detectará dashboard/app.py y lo desplegará
```

**Opción B: Railway (GRATIS con límites)**

```powershell
# 1. Instalar Railway CLI
npm install -g railway

# 2. Login
railway login

# 3. Deploy
railway init
railway up

# Tu app estará en: https://tu-app.railway.app
```

**Opción C: Render (GRATIS)**

```powershell
# 1. Crear cuenta en Render.com

# 2. Crear archivo render.yaml en la raíz:
```

Crea `render.yaml`:

```yaml
services:
  - type: web
    name: nba-predictor
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
```

#### 2. Hacer PWA tu Dashboard

Crea un archivo `dashboard/manifest.json`:

```json
{
  "name": "NBA Predictor Pro",
  "short_name": "NBA Predictor",
  "description": "Sistema de predicción de partidos NBA con IA",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1f77b4",
  "orientation": "portrait",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

#### 3. Instalar en Android

1. Abre el navegador Chrome en Android
2. Ve a tu URL desplegada (ej: `https://tu-app.streamlit.app`)
3. Toca el menú (⋮) → **"Instalar app"** o **"Añadir a pantalla de inicio"**
4. ¡Listo! Funciona como app nativa

**Tiempo estimado: 1-2 horas**

---

## 🔥 **Opción 2: Kivy + BeeWare (App Nativa Python)**

### Ventajas
- ✅ App nativa real (APK)
- ✅ Funciona sin internet (una vez descargados los datos)
- ✅ Usa Python (tu código actual)
- ✅ Publica en Google Play Store

### Desventajas
- ❌ Más complejo (requiere rediseñar UI)
- ❌ Streamlit no funciona en móvil nativo
- ❌ Necesitas rehacer la interfaz con Kivy

### Pasos:

#### 1. Instalar Kivy

```powershell
pip install kivy kivymd buildozer
```

#### 2. Crear UI móvil

Crea `mobile_app.py`:

```python
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
import sys
sys.path.insert(0, 'src')
from models.predictor import NBAPredictor

class PredictorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Cargar modelo
        self.predictor = NBAPredictor()
        self.predictor.load('models/nba_predictor_baseline.joblib')
        
        # UI Elements
        self.add_widget(MDLabel(
            text="NBA Predictor Pro",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        ))
        
        self.home_input = MDTextField(
            hint_text="Equipo Local",
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )
        self.add_widget(self.home_input)
        
        self.away_input = MDTextField(
            hint_text="Equipo Visitante",
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        self.add_widget(self.away_input)
        
        predict_btn = MDRaisedButton(
            text="PREDECIR",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.predict
        )
        self.add_widget(predict_btn)
        
        self.result_label = MDLabel(
            text="",
            halign="center",
            pos_hint={'center_y': 0.3}
        )
        self.add_widget(self.result_label)
    
    def predict(self, instance):
        home_team = self.home_input.text
        away_team = self.away_input.text
        
        # Aquí harías la predicción real con features
        # Por ahora un ejemplo simplificado
        
        self.result_label.text = f"Predicción:\n{home_team} vs {away_team}"

class NBAApp(MDApp):
    def build(self):
        return PredictorScreen()

if __name__ == '__main__':
    NBAApp().run()
```

#### 3. Crear APK con Buildozer

Crea `buildozer.spec`:

```ini
[app]
title = NBA Predictor Pro
package.name = nbapredictor
package.domain = org.nbapredictor

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,joblib,parquet

version = 0.1

requirements = python3,kivy,kivymd,numpy,pandas,scikit-learn,joblib

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
```

#### 4. Compilar APK

```bash
# En Linux/Mac o WSL en Windows
buildozer android debug

# El APK estará en: bin/nbapredictor-0.1-debug.apk
```

**Tiempo estimado: 1-2 semanas**

---

## 🚀 **Opción 3: API Backend + App Flutter/React Native**

### Ventajas
- ✅ App nativa profesional
- ✅ Mejor rendimiento
- ✅ UI/UX óptima para móvil
- ✅ Fácil publicar en Play Store

### Desventajas
- ❌ Requiere aprender Flutter/React Native
- ❌ Más tiempo de desarrollo
- ❌ Necesitas backend separado

### Arquitectura:

```
┌─────────────────┐
│  App Android    │
│  (Flutter/RN)   │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│  API Backend    │
│  (Flask/FastAPI)│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Modelos ML     │
│  (tu código)    │
└─────────────────┘
```

### Pasos:

#### 1. Crear API Flask

Crea `src/api/server.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.predictor import NBAPredictor

app = Flask(__name__)
CORS(app)

# Cargar modelo al iniciar
predictor = NBAPredictor()
predictor.load('models/nba_predictor_baseline.joblib')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    features = data.get('features')
    
    try:
        prediction = predictor.predict_game(home_team, away_team, features)
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/teams', methods=['GET'])
def get_teams():
    # Retornar lista de equipos
    teams = [
        "Los Angeles Lakers",
        "Boston Celtics",
        "Golden State Warriors",
        # ... más equipos
    ]
    return jsonify({'teams': teams})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Instala dependencias:

```powershell
pip install flask flask-cors
```

#### 2. Deploy del Backend

**En Railway, Render o Heroku:**

```powershell
# Railway
railway init
railway up

# Tu API estará en: https://tu-api.railway.app
```

#### 3. Crear App Flutter

```bash
# Instalar Flutter
# Descargar de: https://flutter.dev

# Crear proyecto
flutter create nba_predictor_app
cd nba_predictor_app

# Agregar dependencia HTTP
# En pubspec.yaml:
dependencies:
  http: ^1.1.0
  provider: ^6.1.0
```

Código Flutter (`lib/main.dart`):

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(NBAApp());

class NBAApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NBA Predictor',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: PredictorScreen(),
    );
  }
}

class PredictorScreen extends StatefulWidget {
  @override
  _PredictorScreenState createState() => _PredictorScreenState();
}

class _PredictorScreenState extends State<PredictorScreen> {
  String homeTeam = '';
  String awayTeam = '';
  Map<String, dynamic>? prediction;
  bool loading = false;
  
  final String apiUrl = 'https://tu-api.railway.app';
  
  Future<void> makePrediction() async {
    setState(() => loading = true);
    
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/api/predict'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'home_team': homeTeam,
          'away_team': awayTeam,
          'features': {/* features */}
        }),
      );
      
      if (response.statusCode == 200) {
        setState(() {
          prediction = jsonDecode(response.body)['prediction'];
        });
      }
    } catch (e) {
      print('Error: $e');
    } finally {
      setState(() => loading = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('NBA Predictor Pro')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              decoration: InputDecoration(labelText: 'Equipo Local'),
              onChanged: (value) => homeTeam = value,
            ),
            SizedBox(height: 16),
            TextField(
              decoration: InputDecoration(labelText: 'Equipo Visitante'),
              onChanged: (value) => awayTeam = value,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: loading ? null : makePrediction,
              child: loading 
                ? CircularProgressIndicator(color: Colors.white)
                : Text('PREDECIR'),
            ),
            SizedBox(height: 24),
            if (prediction != null)
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Text(
                        '${prediction!['home_team']}',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${(prediction!['home_win_probability'] * 100).toStringAsFixed(1)}%',
                        style: TextStyle(fontSize: 32, color: Colors.blue),
                      ),
                      Text('vs'),
                      Text(
                        '${prediction!['away_team']}',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${(prediction!['away_win_probability'] * 100).toStringAsFixed(1)}%',
                        style: TextStyle(fontSize: 32, color: Colors.orange),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

#### 4. Compilar APK

```bash
flutter build apk --release

# APK en: build/app/outputs/flutter-apk/app-release.apk
```

**Tiempo estimado: 2-4 semanas**

---

## 📊 Comparación de Opciones

| Característica | PWA | Kivy | Flutter+API |
|----------------|-----|------|-------------|
| **Tiempo desarrollo** | 1-2 horas | 1-2 semanas | 2-4 semanas |
| **Dificultad** | ⭐ Fácil | ⭐⭐⭐ Media | ⭐⭐⭐⭐ Alta |
| **Costo** | GRATIS | GRATIS | GRATIS-$5/mes |
| **Funciona offline** | ❌ No | ✅ Sí | ✅ Sí (con caché) |
| **Play Store** | ❌ No | ✅ Sí | ✅ Sí |
| **Calidad app** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Actualizaciones** | ✅ Auto | Manual | Manual |

---

## 🎯 **RECOMENDACIÓN**

### Para empezar YA (hoy mismo):
**→ Opción 1: PWA con Streamlit Cloud**
- Deploy en Streamlit Cloud (15 minutos)
- Instala como PWA en Android
- ¡Listo para usar!

### Para app profesional:
**→ Opción 3: API + Flutter**
- Mejor experiencia de usuario
- Publicable en Play Store
- Escalable y mantenible

---

## 🚀 **PRÓXIMOS PASOS INMEDIATOS**

### 1. Deploy en Streamlit Cloud (15 minutos)

```powershell
# 1. Crear repositorio GitHub
git init
git add .
git commit -m "NBA Predictor Pro"

# 2. Crear repo en GitHub.com
# Ir a: https://github.com/new

# 3. Push código
git remote add origin https://github.com/TU_USUARIO/nba-predictor.git
git push -u origin main

# 4. Deploy en Streamlit Cloud
# Ir a: https://streamlit.io/cloud
# Conectar tu repo GitHub
# ¡Deploy automático!
```

### 2. Instalar como PWA en Android

1. Abre Chrome en tu Android
2. Ve a tu URL de Streamlit Cloud
3. Menú → "Instalar app"
4. ¡Ya tienes tu app!

---

## 📱 **Resultado Final**

Tendrás una app Android que:
- ✅ Se instala en el teléfono
- ✅ Tiene icono propio
- ✅ Abre como app nativa
- ✅ Funciona a pantalla completa
- ✅ Hace predicciones NBA con IA
- ✅ Actualiza automáticamente

**¿Quieres que te ayude a hacer el deploy ahora mismo?**
