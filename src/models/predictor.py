"""Modelos base para predicción de partidos NBA."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score, accuracy_score, mean_absolute_error, r2_score
import joblib
from pathlib import Path
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')


class NBAPredictor:
    """Sistema de predicción para partidos NBA."""
    
    def __init__(self):
        self.win_model = None
        self.margin_model = None
        self.total_model = None
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='constant', fill_value=0)  # Rellenar NaN con 0
        self.feature_columns = None
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """
        Prepara features y targets para entrenamiento.
        
        Returns:
            X, y_win, y_margin, y_total
        """
        # Seleccionar features relevantes
        feature_cols = [
            # ELO
            'HOME_ELO_BEFORE', 'AWAY_ELO_BEFORE', 'ELO_DIFF',
            
            # Rolling stats (últimos 5 partidos)
            'HOME_PTS_ROLL_5', 'AWAY_PTS_ROLL_5',
            'HOME_FG_PCT_ROLL_5', 'AWAY_FG_PCT_ROLL_5',
            'HOME_FG3_PCT_ROLL_5', 'AWAY_FG3_PCT_ROLL_5',
            'HOME_REB_ROLL_5', 'AWAY_REB_ROLL_5',
            'HOME_AST_ROLL_5', 'AWAY_AST_ROLL_5',
            'HOME_TOV_ROLL_5', 'AWAY_TOV_ROLL_5',
            
            # Rolling stats (últimos 10 partidos)
            'HOME_PTS_ROLL_10', 'AWAY_PTS_ROLL_10',
            
            # Rest y back-to-back
            'HOME_REST_DAYS', 'AWAY_REST_DAYS',
            'HOME_BACK_TO_BACK', 'AWAY_BACK_TO_BACK',
            
            # Win streaks
            'HOME_WIN_STREAK', 'AWAY_WIN_STREAK',
            
            # Season stats
            'HOME_WIN_PCT', 'AWAY_WIN_PCT',
        ]
        
        # Filtrar solo las columnas que existen
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < len(feature_cols):
            missing = set(feature_cols) - set(available_features)
            print(f"⚠️  Features faltantes: {missing}")
        
        self.feature_columns = available_features
        
        # Preparar datos
        X = df[available_features].copy()
        
        # Eliminar filas con NaN
        valid_mask = ~X.isna().any(axis=1)
        X = X[valid_mask]
        
        # Targets
        y_win = df.loc[valid_mask, 'HOME_WL'].astype(int)
        y_margin = df.loc[valid_mask, 'POINT_DIFF']
        y_total = df.loc[valid_mask, 'TOTAL_PTS']
        
        return X, y_win, y_margin, y_total
    
    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Entrena los tres modelos principales.
        
        Args:
            df: DataFrame con features y targets
            test_size: Proporción de datos para test
            random_state: Semilla aleatoria
            
        Returns:
            Diccionario con métricas de evaluación
        """
        print("🏋️  Entrenando modelos...")
        
        # Preparar datos
        X, y_win, y_margin, y_total = self.prepare_features(df)
        
        # Split temporal (importante para series de tiempo)
        split_idx = int(len(X) * (1 - test_size))
        
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_win_train, y_win_test = y_win.iloc[:split_idx], y_win.iloc[split_idx:]
        y_margin_train, y_margin_test = y_margin.iloc[:split_idx], y_margin.iloc[split_idx:]
        y_total_train, y_total_test = y_total.iloc[:split_idx], y_total.iloc[split_idx:]
        
        # Imputar valores faltantes
        X_train = pd.DataFrame(
            self.imputer.fit_transform(X_train),
            columns=X_train.columns
        )
        X_test = pd.DataFrame(
            self.imputer.transform(X_test),
            columns=X_test.columns
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 1. Modelo de probabilidad de victoria
        print("  - Entrenando modelo de victoria...")
        base_win_model = LogisticRegression(max_iter=1000, random_state=random_state)
        self.win_model = CalibratedClassifierCV(base_win_model, method='isotonic', cv=5)
        self.win_model.fit(X_train_scaled, y_win_train)
        
        # 2. Modelo de margen de puntos
        print("  - Entrenando modelo de margen...")
        self.margin_model = Ridge(alpha=1.0, random_state=random_state)
        self.margin_model.fit(X_train_scaled, y_margin_train)
        
        # 3. Modelo de puntos totales
        print("  - Entrenando modelo de total de puntos...")
        self.total_model = Ridge(alpha=1.0, random_state=random_state)
        self.total_model.fit(X_train_scaled, y_total_train)
        
        # Evaluar
        print("\n📊 Evaluando modelos en test set...")
        metrics = self.evaluate(X_test_scaled, y_win_test, y_margin_test, y_total_test)
        
        return metrics
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_win_test: pd.Series,
        y_margin_test: pd.Series,
        y_total_test: pd.Series
    ) -> Dict[str, float]:
        """Evalúa los modelos y retorna métricas."""
        metrics = {}
        
        # Predicciones de victoria
        y_win_proba = self.win_model.predict_proba(X_test)[:, 1]
        y_win_pred = (y_win_proba > 0.5).astype(int)
        
        metrics['win_accuracy'] = accuracy_score(y_win_test, y_win_pred)
        metrics['win_log_loss'] = log_loss(y_win_test, y_win_proba)
        metrics['win_brier_score'] = brier_score_loss(y_win_test, y_win_proba)
        metrics['win_roc_auc'] = roc_auc_score(y_win_test, y_win_proba)
        
        # Predicciones de margen
        y_margin_pred = self.margin_model.predict(X_test)
        metrics['margin_mae'] = mean_absolute_error(y_margin_test, y_margin_pred)
        metrics['margin_r2'] = r2_score(y_margin_test, y_margin_pred)
        
        # Predicciones de total
        y_total_pred = self.total_model.predict(X_test)
        metrics['total_mae'] = mean_absolute_error(y_total_test, y_total_pred)
        metrics['total_r2'] = r2_score(y_total_test, y_total_pred)
        
        # Imprimir resultados
        print("\n✅ RESULTADOS DE EVALUACIÓN")
        print("=" * 50)
        print("\n🎯 Modelo de Victoria:")
        print(f"  - Accuracy: {metrics['win_accuracy']:.3f}")
        print(f"  - Log Loss: {metrics['win_log_loss']:.3f}")
        print(f"  - Brier Score: {metrics['win_brier_score']:.3f}")
        print(f"  - ROC AUC: {metrics['win_roc_auc']:.3f}")
        
        print("\n📏 Modelo de Margen:")
        print(f"  - MAE: {metrics['margin_mae']:.2f} puntos")
        print(f"  - R²: {metrics['margin_r2']:.3f}")
        
        print("\n🔢 Modelo de Total:")
        print(f"  - MAE: {metrics['total_mae']:.2f} puntos")
        print(f"  - R²: {metrics['total_r2']:.3f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Realiza predicciones para nuevos partidos.
        
        Args:
            X: DataFrame con features
            
        Returns:
            Diccionario con predicciones
        """
        # Imputar valores faltantes
        X_imputed = pd.DataFrame(
            self.imputer.transform(X[self.feature_columns]),
            columns=self.feature_columns
        )
        
        # Escalar
        X_scaled = self.scaler.transform(X_imputed)
        
        predictions = {
            'win_probability': self.win_model.predict_proba(X_scaled)[:, 1],
            'point_margin': self.margin_model.predict(X_scaled),
            'total_points': self.total_model.predict(X_scaled)
        }
        
        return predictions
    
    def predict_game(
        self,
        home_team: str,
        away_team: str,
        features: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Predice un partido individual.
        
        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante
            features: Diccionario con valores de features
            
        Returns:
            Diccionario con predicciones
        """
        # Crear DataFrame con features
        X = pd.DataFrame([features])
        
        # Predecir
        preds = self.predict(X)
        
        result = {
            'home_team': home_team,
            'away_team': away_team,
            'home_win_probability': float(preds['win_probability'][0]),
            'away_win_probability': float(1 - preds['win_probability'][0]),
            'predicted_margin': float(preds['point_margin'][0]),
            'predicted_total': float(preds['total_points'][0]),
            'predicted_home_score': float((preds['total_points'][0] + preds['point_margin'][0]) / 2),
            'predicted_away_score': float((preds['total_points'][0] - preds['point_margin'][0]) / 2),
        }
        
        return result
    
    def save(self, filepath: str):
        """Guarda los modelos entrenados."""
        save_data = {
            'win_model': self.win_model,
            'margin_model': self.margin_model,
            'total_model': self.total_model,
            'scaler': self.scaler,
            'imputer': self.imputer,
            'feature_columns': self.feature_columns
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(save_data, filepath)
        print(f"💾 Modelos guardados en: {filepath}")
    
    def load(self, filepath: str):
        """Carga modelos entrenados."""
        save_data = joblib.load(filepath)
        
        self.win_model = save_data['win_model']
        self.margin_model = save_data['margin_model']
        self.total_model = save_data['total_model']
        self.scaler = save_data['scaler']
        self.imputer = save_data['imputer']
        self.feature_columns = save_data['feature_columns']
        
        print(f"✅ Modelos cargados desde: {filepath}")


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    # Cargar datos procesados
    data_path = Path("data/processed/games_with_features.parquet")
    
    if data_path.exists():
        df = pd.read_parquet(data_path)
        
        # Entrenar
        predictor = NBAPredictor()
        metrics = predictor.train(df, test_size=0.2)
        
        # Guardar
        predictor.save("models/nba_predictor_baseline.joblib")
        
    else:
        print(f"❌ Archivo no encontrado: {data_path}")
        print("Ejecuta primero: python scripts/process_features.py")
