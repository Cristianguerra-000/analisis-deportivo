# 🔥 NBA Predictor con Firebase - Guía Completa

## 🎯 ¿Por qué Firebase?

Firebase es **PERFECTA** para tu app NBA Predictor porque ofrece:

- ✅ **Hosting gratuito** (para tu dashboard web)
- ✅ **Firestore Database** (almacenar predicciones y estadísticas)
- ✅ **Cloud Functions** (ejecutar modelos Python en la nube)
- ✅ **Authentication** (login de usuarios)
- ✅ **Firebase App Distribution** (distribuir tu APK)
- ✅ **Analytics** (ver cómo usan tu app)
- ✅ **Push Notifications** (alertas de partidos)

---

## 🏗️ Arquitectura con Firebase

```
┌─────────────────────┐
│   App Android       │
│   (Flutter/PWA)     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Firebase Services  │
├─────────────────────┤
│  • Hosting          │ ← Dashboard Streamlit
│  • Firestore DB     │ ← Guardar predicciones
│  • Cloud Functions  │ ← Ejecutar modelos ML
│  • Authentication   │ ← Login usuarios
│  • Storage         │ ← Datos y modelos
└─────────────────────┘
           │
           ↓
┌─────────────────────┐
│  Modelos ML         │
│  (Python/scikit)    │
└─────────────────────┘
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### **Fase 1: Setup Firebase (30 minutos)**

#### 1. Crear Proyecto Firebase

```powershell
# 1. Ir a: https://console.firebase.google.com/
# 2. Click "Agregar proyecto"
# 3. Nombre: "NBA-Predictor-Pro"
# 4. Activar Google Analytics (opcional)
# 5. Crear proyecto
```

#### 2. Instalar Firebase CLI

```powershell
# Instalar Node.js primero (si no lo tienes)
# Descargar de: https://nodejs.org/

# Instalar Firebase CLI
npm install -g firebase-tools

# Login en Firebase
firebase login

# Inicializar en tu proyecto
cd C:\Users\guerr\Analisis
firebase init
```

Durante `firebase init`, selecciona:
- ✅ **Hosting** (para dashboard web)
- ✅ **Functions** (para API Python)
- ✅ **Firestore** (para base de datos)

---

### **Fase 2: Configurar Firestore Database (15 minutos)**

#### 1. Crear estructura de base de datos

En Firebase Console → Firestore Database:

```
nba_predictor/
├── predictions/
│   ├── {prediction_id}/
│   │   ├── home_team: string
│   │   ├── away_team: string
│   │   ├── home_win_prob: number
│   │   ├── predicted_score: string
│   │   ├── timestamp: timestamp
│   │   └── user_id: string
│   
├── teams/
│   ├── {team_id}/
│   │   ├── name: string
│   │   ├── current_elo: number
│   │   ├── win_pct: number
│   │   └── last_updated: timestamp
│   
└── users/
    ├── {user_id}/
    │   ├── email: string
    │   ├── predictions_count: number
    │   └── created_at: timestamp
```

#### 2. Reglas de seguridad

En Firestore Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir lectura a todos
    match /teams/{teamId} {
      allow read: if true;
      allow write: if false; // Solo admin
    }
    
    // Predicciones: usuarios autenticados
    match /predictions/{predId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null 
        && resource.data.user_id == request.auth.uid;
    }
    
    // Usuarios: solo su propia info
    match /users/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
  }
}
```

---

### **Fase 3: Cloud Functions con Python (45 minutos)**

#### 1. Crear Cloud Function para predicciones

Crea `functions/main.py`:

```python
from firebase_functions import https_fn, firestore_fn
from firebase_admin import initialize_app, firestore
import pickle
import numpy as np
from datetime import datetime

# Inicializar Firebase
initialize_app()
db = firestore.client()

# Cargar modelo (se carga una vez)
import joblib
MODEL = None

def load_model():
    global MODEL
    if MODEL is None:
        # Cargar desde Firebase Storage
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket('nba-predictor-pro.appspot.com')
        blob = bucket.blob('models/nba_predictor_baseline.joblib')
        
        # Descargar temporalmente
        blob.download_to_filename('/tmp/model.joblib')
        MODEL = joblib.load('/tmp/model.joblib')
    return MODEL

@https_fn.on_request()
def predict_game(req: https_fn.Request) -> https_fn.Response:
    """Cloud Function para predecir partidos."""
    
    # CORS headers
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Parse request
        data = req.get_json()
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        features = data.get('features')
        user_id = data.get('user_id', 'anonymous')
        
        # Cargar modelo
        predictor = load_model()
        
        # Hacer predicción
        prediction = predictor.predict_game(home_team, away_team, features)
        
        # Guardar en Firestore
        prediction_ref = db.collection('predictions').document()
        prediction_ref.set({
            'home_team': home_team,
            'away_team': away_team,
            'home_win_probability': prediction['home_win_probability'],
            'away_win_probability': prediction['away_win_probability'],
            'predicted_home_score': prediction['predicted_home_score'],
            'predicted_away_score': prediction['predicted_away_score'],
            'predicted_margin': prediction['predicted_margin'],
            'predicted_total': prediction['predicted_total'],
            'user_id': user_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
        })
        
        return https_fn.Response(
            response=prediction,
            status=200,
            headers=headers
        )
        
    except Exception as e:
        return https_fn.Response(
            response={'error': str(e)},
            status=500,
            headers=headers
        )

@https_fn.on_request()
def get_teams(req: https_fn.Request) -> https_fn.Response:
    """Obtener lista de equipos con stats."""
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        teams_ref = db.collection('teams')
        teams = []
        
        for team_doc in teams_ref.stream():
            team_data = team_doc.to_dict()
            team_data['id'] = team_doc.id
            teams.append(team_data)
        
        return https_fn.Response(
            response={'teams': teams},
            status=200,
            headers=headers
        )
    except Exception as e:
        return https_fn.Response(
            response={'error': str(e)},
            status=500,
            headers=headers
        )

@firestore_fn.on_document_created(document="predictions/{predId}")
def on_prediction_created(event: firestore_fn.Event) -> None:
    """Trigger cuando se crea una predicción."""
    
    # Obtener datos de la predicción
    prediction_data = event.data.to_dict()
    user_id = prediction_data.get('user_id')
    
    if user_id and user_id != 'anonymous':
        # Incrementar contador de predicciones del usuario
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'predictions_count': firestore.Increment(1),
            'last_prediction': firestore.SERVER_TIMESTAMP
        })
```

#### 2. Configurar requirements

Crea `functions/requirements.txt`:

```txt
firebase-functions>=0.4.0
firebase-admin>=6.0.0
google-cloud-storage>=2.10.0
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
joblib>=1.3.0
```

#### 3. Deploy Functions

```powershell
cd functions
firebase deploy --only functions
```

---

### **Fase 4: Subir Modelo a Firebase Storage (10 minutos)**

#### 1. Subir modelo entrenado

```powershell
# Instalar SDK
pip install firebase-admin google-cloud-storage

# Crear script para subir modelo
```

Crea `scripts/upload_model_to_firebase.py`:

```python
from firebase_admin import credentials, storage, initialize_app
from pathlib import Path

# Inicializar Firebase Admin
cred = credentials.Certificate('path/to/serviceAccountKey.json')
initialize_app(cred, {
    'storageBucket': 'nba-predictor-pro.appspot.com'
})

# Subir modelo
bucket = storage.bucket()

# Subir modelo principal
blob = bucket.blob('models/nba_predictor_baseline.joblib')
blob.upload_from_filename('models/nba_predictor_baseline.joblib')
print("✅ Modelo subido a Firebase Storage")

# Subir datos procesados
blob = bucket.blob('data/games_with_features.parquet')
blob.upload_from_filename('data/processed/games_with_features.parquet')
print("✅ Datos subidos a Firebase Storage")
```

---

### **Fase 5: Adaptar Dashboard para Firebase (30 minutos)**

#### 1. Crear versión del dashboard con Firebase

Crea `dashboard/firebase_app.py`:

```python
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests

# Configurar Firebase
if not firebase_admin._apps:
    # Usar credenciales desde secrets de Streamlit
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("🏀 NBA Predictor Pro")

# URL de tu Cloud Function
CLOUD_FUNCTION_URL = "https://us-central1-nba-predictor-pro.cloudfunctions.net/predict_game"

# Obtener equipos
@st.cache_data
def get_teams():
    teams_ref = db.collection('teams')
    teams = [doc.to_dict()['name'] for doc in teams_ref.stream()]
    return sorted(teams)

teams = get_teams()

# Selección de equipos
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Equipo Local", teams)
with col2:
    away_team = st.selectbox("✈️ Equipo Visitante", [t for t in teams if t != home_team])

if st.button("🔮 PREDECIR", type="primary"):
    with st.spinner("Calculando predicción..."):
        # Llamar a Cloud Function
        response = requests.post(CLOUD_FUNCTION_URL, json={
            'home_team': home_team,
            'away_team': away_team,
            'features': {},  # Aquí irían las features reales
            'user_id': 'demo_user'
        })
        
        if response.status_code == 200:
            prediction = response.json()
            
            # Mostrar resultados
            st.success("✅ Predicción completada")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    home_team,
                    f"{prediction['home_win_probability']*100:.1f}%",
                    "Prob. Victoria"
                )
            with col2:
                st.metric(
                    away_team,
                    f"{prediction['away_win_probability']*100:.1f}%",
                    "Prob. Victoria"
                )
            
            st.subheader("📊 Marcador Predicho")
            st.write(f"**{prediction['predicted_home_score']:.0f}** - **{prediction['predicted_away_score']:.0f}**")

# Historial de predicciones
st.subheader("📜 Últimas Predicciones")
predictions_ref = db.collection('predictions').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5)

for doc in predictions_ref.stream():
    pred = doc.to_dict()
    st.write(f"**{pred['home_team']}** vs **{pred['away_team']}** - {pred['timestamp'].strftime('%Y-%m-%d %H:%M')}")
```

#### 2. Configurar secrets en Streamlit

Crea `.streamlit/secrets.toml`:

```toml
[firebase]
type = "service_account"
project_id = "nba-predictor-pro"
private_key_id = "TU_PRIVATE_KEY_ID"
private_key = "TU_PRIVATE_KEY"
client_email = "firebase-adminsdk-xxxxx@nba-predictor-pro.iam.gserviceaccount.com"
client_id = "TU_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "TU_CERT_URL"
```

---

### **Fase 6: Deploy a Firebase Hosting (15 minutos)**

#### 1. Configurar firebase.json

```json
{
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  },
  "functions": {
    "source": "functions",
    "runtime": "python311"
  },
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  }
}
```

#### 2. Deploy completo

```powershell
# Deploy todo
firebase deploy

# O deploy específico
firebase deploy --only hosting
firebase deploy --only functions
firebase deploy --only firestore:rules
```

---

### **Fase 7: Crear App Android (Flutter + Firebase)**

#### 1. Configurar Flutter con Firebase

```bash
flutter create nba_predictor_app
cd nba_predictor_app

# Añadir Firebase
flutter pub add firebase_core
flutter pub add cloud_firestore
flutter pub add firebase_auth
flutter pub add http
```

#### 2. Configurar Firebase en Flutter

```bash
# Instalar FlutterFire CLI
dart pub global activate flutterfire_cli

# Configurar Firebase
flutterfire configure
```

#### 3. Código Flutter con Firebase

Actualiza `lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(NBAApp());
}

class NBAApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NBA Predictor Pro',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: PredictorScreen(),
    );
  }
}

class PredictorScreen extends StatefulWidget {
  @override
  _PredictorScreenState createState() => _PredictorScreenState();
}

class _PredictorScreenState extends State<PredictorScreen> {
  List<String> teams = [];
  String? selectedHomeTeam;
  String? selectedAwayTeam;
  Map<String, dynamic>? prediction;
  bool loading = false;
  
  final String cloudFunctionUrl = 
    'https://us-central1-nba-predictor-pro.cloudfunctions.net/predict_game';
  
  @override
  void initState() {
    super.initState();
    loadTeams();
  }
  
  Future<void> loadTeams() async {
    final snapshot = await FirebaseFirestore.instance
        .collection('teams')
        .orderBy('name')
        .get();
    
    setState(() {
      teams = snapshot.docs.map((doc) => doc['name'] as String).toList();
    });
  }
  
  Future<void> makePrediction() async {
    if (selectedHomeTeam == null || selectedAwayTeam == null) return;
    
    setState(() => loading = true);
    
    try {
      final response = await http.post(
        Uri.parse(cloudFunctionUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'home_team': selectedHomeTeam,
          'away_team': selectedAwayTeam,
          'features': {},
          'user_id': 'flutter_user',
        }),
      );
      
      if (response.statusCode == 200) {
        setState(() {
          prediction = jsonDecode(response.body);
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => loading = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🏀 NBA Predictor Pro'),
        elevation: 2,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Selector de equipos
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  children: [
                    DropdownButtonFormField<String>(
                      decoration: InputDecoration(
                        labelText: '🏠 Equipo Local',
                        border: OutlineInputBorder(),
                      ),
                      value: selectedHomeTeam,
                      items: teams.map((team) {
                        return DropdownMenuItem(value: team, child: Text(team));
                      }).toList(),
                      onChanged: (value) => setState(() => selectedHomeTeam = value),
                    ),
                    SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      decoration: InputDecoration(
                        labelText: '✈️ Equipo Visitante',
                        border: OutlineInputBorder(),
                      ),
                      value: selectedAwayTeam,
                      items: teams.where((t) => t != selectedHomeTeam).map((team) {
                        return DropdownMenuItem(value: team, child: Text(team));
                      }).toList(),
                      onChanged: (value) => setState(() => selectedAwayTeam = value),
                    ),
                  ],
                ),
              ),
            ),
            
            SizedBox(height: 16),
            
            // Botón predecir
            ElevatedButton(
              onPressed: loading ? null : makePrediction,
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.all(16),
                textStyle: TextStyle(fontSize: 18),
              ),
              child: loading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('🔮 PREDECIR'),
            ),
            
            // Resultados
            if (prediction != null) ...[
              SizedBox(height: 24),
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Text(
                        prediction!['home_team'],
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${(prediction!['home_win_probability'] * 100).toStringAsFixed(1)}%',
                        style: TextStyle(fontSize: 48, color: Colors.blue),
                      ),
                      Divider(height: 32),
                      Text('VS', style: TextStyle(fontSize: 16)),
                      Divider(height: 32),
                      Text(
                        prediction!['away_team'],
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${(prediction!['away_win_probability'] * 100).toStringAsFixed(1)}%',
                        style: TextStyle(fontSize: 48, color: Colors.orange),
                      ),
                      Divider(height: 32),
                      Text(
                        'Marcador Predicho',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${prediction!['predicted_home_score'].toStringAsFixed(0)} - ${prediction!['predicted_away_score'].toStringAsFixed(0)}',
                        style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            
            SizedBox(height: 24),
            
            // Historial
            Text('📜 Últimas Predicciones', 
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            StreamBuilder<QuerySnapshot>(
              stream: FirebaseFirestore.instance
                  .collection('predictions')
                  .orderBy('timestamp', descending: true)
                  .limit(10)
                  .snapshots(),
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return CircularProgressIndicator();
                }
                
                return Column(
                  children: snapshot.data!.docs.map((doc) {
                    final data = doc.data() as Map<String, dynamic>;
                    return Card(
                      child: ListTile(
                        title: Text('${data['home_team']} vs ${data['away_team']}'),
                        subtitle: Text(
                          '${(data['home_win_probability'] * 100).toStringAsFixed(1)}% - ${(data['away_win_probability'] * 100).toStringAsFixed(1)}%'
                        ),
                      ),
                    );
                  }).toList(),
                );
              },
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
```

APK estará en: `build/app/outputs/flutter-apk/app-release.apk`

---

## 💰 COSTOS DE FIREBASE

### Plan Spark (GRATIS)
- ✅ **Firestore**: 1 GB almacenamiento, 50K lecturas/día
- ✅ **Functions**: 125K invocaciones/mes, 40K GB-segundos
- ✅ **Hosting**: 10 GB transferencia/mes
- ✅ **Storage**: 5 GB
- ✅ **Authentication**: Ilimitado

### Plan Blaze (Pago por uso)
- 💰 **Firestore**: $0.06 por 100K lecturas
- 💰 **Functions**: $0.40 por millón invocaciones
- 💰 **Hosting**: $0.15 por GB transferencia

**Para tu app NBA**: El plan GRATIS es suficiente para empezar y hasta ~1000 usuarios/día.

---

## 🎯 RESUMEN DE PASOS

1. ✅ **Crear proyecto Firebase** (5 min)
2. ✅ **Configurar Firestore** (15 min)
3. ✅ **Subir modelo a Storage** (10 min)
4. ✅ **Crear Cloud Functions** (45 min)
5. ✅ **Deploy Functions** (10 min)
6. ✅ **Configurar Flutter app** (30 min)
7. ✅ **Compilar APK** (10 min)

**Total**: ~2 horas para tener tu app Android con Firebase ✅

---

## 🚀 **¿EMPEZAMOS?**

¿Quieres que te ayude paso a paso a:
1. Crear el proyecto en Firebase
2. Configurar Firestore
3. Subir tu modelo entrenado
4. Crear las Cloud Functions

**¡Podemos hacerlo ahora!** 🔥
