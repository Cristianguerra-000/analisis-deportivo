"""Modelos base para predicción de partidos NBA."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score, accuracy_score, mean_absolute_error, r2_score
from xgboost import XGBClassifier, XGBRegressor
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
            
            # NUEVAS FEATURES DEFENSIVAS
            'HOME_STL_ROLL_5', 'AWAY_STL_ROLL_5',
            'HOME_BLK_ROLL_5', 'AWAY_BLK_ROLL_5',
        ]
        
        # Filtrar solo las columnas que existen
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < len(feature_cols):
            missing = set(feature_cols) - set(available_features)
            print(f"⚠️  Features faltantes: {missing}")
        
        self.feature_columns = available_features
        
        # Preparar datos
        X = df[available_features].copy()
        
        # CREAR FEATURES DE INTERACCIÓN
        if 'ELO_DIFF' in X.columns and 'HOME_REST_DAYS' in X.columns:
            X['ELO_DIFF_X_REST'] = X['ELO_DIFF'] * (X['HOME_REST_DAYS'] - X['AWAY_REST_DAYS'])
        
        if 'HOME_WIN_PCT' in X.columns and 'AWAY_WIN_PCT' in X.columns:
            X['WIN_PCT_DIFF'] = X['HOME_WIN_PCT'] - X['AWAY_WIN_PCT']
        
        if 'HOME_PTS_ROLL_5' in X.columns and 'AWAY_PTS_ROLL_5' in X.columns:
            X['PTS_DIFF_ROLL_5'] = X['HOME_PTS_ROLL_5'] - X['AWAY_PTS_ROLL_5']
        
        if 'HOME_FG_PCT_ROLL_5' in X.columns and 'AWAY_FG_PCT_ROLL_5' in X.columns:
            X['FG_PCT_DIFF_ROLL_5'] = X['HOME_FG_PCT_ROLL_5'] - X['AWAY_FG_PCT_ROLL_5']
        
        # Actualizar feature_columns con las nuevas features de interacción
        self.feature_columns = X.columns.tolist()
        
        # Eliminar filas con NaN
        valid_mask = ~X.isna().any(axis=1)
        X = X[valid_mask]
        
        # Targets
        y_win = df.loc[valid_mask, 'HOME_WL'].astype(int)
        y_margin = df.loc[valid_mask, 'POINT_DIFF']
        y_total = df.loc[valid_mask, 'TOTAL_PTS']
        
        return X, y_win, y_margin, y_total
    
    def prepare_features_for_game(self, home_team: str, away_team: str, df: pd.DataFrame) -> Dict[str, float]:
        """
        Prepara features para predecir un partido específico.
        
        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante
            df: DataFrame histórico con features
            
        Returns:
            Diccionario con features para predicción
        """
        # Obtener el último partido de cada equipo para calcular features
        home_games = df[
            (df['HOME_TEAM_NAME'] == home_team) | 
            (df['AWAY_TEAM_NAME'] == home_team)
        ].sort_values('GAME_DATE', ascending=False)
        
        away_games = df[
            (df['HOME_TEAM_NAME'] == away_team) | 
            (df['AWAY_TEAM_NAME'] == away_team)
        ].sort_values('GAME_DATE', ascending=False)
        
        if home_games.empty or away_games.empty:
            raise ValueError(f"No hay datos suficientes para uno de los equipos: {home_team}, {away_team}")
        
        # Tomar el último partido de cada equipo
        home_last = home_games.iloc[0]
        away_last = away_games.iloc[0]
        
        # Determinar si el equipo juega en casa o fuera en su último partido
        home_is_home = home_last['HOME_TEAM_NAME'] == home_team
        away_is_home = away_last['HOME_TEAM_NAME'] == away_team
        
        # Extraer features del último partido de cada equipo
        features = {}
        
        # ELO ratings
        features['HOME_ELO_BEFORE'] = home_last.get('HOME_ELO_BEFORE' if home_is_home else 'AWAY_ELO_BEFORE', 1500)
        features['AWAY_ELO_BEFORE'] = away_last.get('HOME_ELO_BEFORE' if away_is_home else 'AWAY_ELO_BEFORE', 1500)
        features['ELO_DIFF'] = features['HOME_ELO_BEFORE'] - features['AWAY_ELO_BEFORE']
        
        # Rolling stats (últimos 5 partidos) - simplificado usando el último partido
        features['HOME_PTS_ROLL_5'] = home_last.get('HOME_PTS' if home_is_home else 'AWAY_PTS', 110)
        features['AWAY_PTS_ROLL_5'] = away_last.get('HOME_PTS' if away_is_home else 'AWAY_PTS', 110)
        
        # Usar porcentajes por defecto si no están disponibles
        features['HOME_FG_PCT_ROLL_5'] = home_last.get('HOME_FG_PCT' if home_is_home else 'AWAY_FG_PCT', 0.45)
        features['AWAY_FG_PCT_ROLL_5'] = away_last.get('HOME_FG_PCT' if away_is_home else 'AWAY_FG_PCT', 0.45)
        
        features['HOME_FG3_PCT_ROLL_5'] = home_last.get('HOME_FG3_PCT' if home_is_home else 'AWAY_FG3_PCT', 0.35)
        features['AWAY_FG3_PCT_ROLL_5'] = away_last.get('HOME_FG3_PCT' if away_is_home else 'AWAY_FG3_PCT', 0.35)
        
        features['HOME_REB_ROLL_5'] = home_last.get('HOME_REB' if home_is_home else 'AWAY_REB', 45)
        features['AWAY_REB_ROLL_5'] = away_last.get('HOME_REB' if away_is_home else 'AWAY_REB', 45)
        
        features['HOME_AST_ROLL_5'] = home_last.get('HOME_AST' if home_is_home else 'AWAY_AST', 25)
        features['AWAY_AST_ROLL_5'] = away_last.get('HOME_AST' if away_is_home else 'AWAY_AST', 25)
        
        features['HOME_TOV_ROLL_5'] = home_last.get('HOME_TOV' if home_is_home else 'AWAY_TOV', 15)
        features['AWAY_TOV_ROLL_5'] = away_last.get('HOME_TOV' if away_is_home else 'AWAY_TOV', 15)
        
        # Rolling stats (últimos 10 partidos) - usar mismos valores por simplicidad
        features['HOME_PTS_ROLL_10'] = features['HOME_PTS_ROLL_5']
        features['AWAY_PTS_ROLL_10'] = features['AWAY_PTS_ROLL_5']
        
        # Rest days - asumir 2 días de descanso por defecto
        features['HOME_REST_DAYS'] = 2
        features['AWAY_REST_DAYS'] = 2
        
        # Back to back - asumir no
        features['HOME_BACK_TO_BACK'] = 0
        features['AWAY_BACK_TO_BACK'] = 0
        
        # Win streaks - calcular basado en últimos partidos
        home_recent_games = home_games.head(5)
        away_recent_games = away_games.head(5)
        
        home_wins = 0
        for _, game in home_recent_games.iterrows():
            if game['HOME_TEAM_NAME'] == home_team and game['HOME_WL'] == 1:
                home_wins += 1
            elif game['AWAY_TEAM_NAME'] == home_team and game['HOME_WL'] == 0:
                home_wins += 1
        
        away_wins = 0
        for _, game in away_recent_games.iterrows():
            if game['HOME_TEAM_NAME'] == away_team and game['HOME_WL'] == 1:
                away_wins += 1
            elif game['AWAY_TEAM_NAME'] == away_team and game['HOME_WL'] == 0:
                away_wins += 1
        
        features['HOME_WIN_STREAK'] = home_wins
        features['AWAY_WIN_STREAK'] = away_wins
        
        # Win percentage - calcular basado en temporada
        home_total_games = len(home_games)
        away_total_games = len(away_games)
        
        home_win_pct = home_games['HOME_WL'].mean() if home_total_games > 0 else 0.5
        away_win_pct = away_games['HOME_WL'].mean() if away_total_games > 0 else 0.5
        
        features['HOME_WIN_PCT'] = home_win_pct
        features['AWAY_WIN_PCT'] = away_win_pct
        
        # NUEVAS FEATURES DEFENSIVAS (valores por defecto si no existen)
        features['HOME_STL_ROLL_5'] = home_last.get('HOME_STL' if home_is_home else 'AWAY_STL', 7.5)
        features['AWAY_STL_ROLL_5'] = away_last.get('HOME_STL' if away_is_home else 'AWAY_STL', 7.5)
        features['HOME_BLK_ROLL_5'] = home_last.get('HOME_BLK' if home_is_home else 'AWAY_BLK', 5.0)
        features['AWAY_BLK_ROLL_5'] = away_last.get('HOME_BLK' if away_is_home else 'AWAY_BLK', 5.0)
        
        # FEATURES DE INTERACCIÓN
        features['ELO_DIFF_X_REST'] = features['ELO_DIFF'] * (features['HOME_REST_DAYS'] - features['AWAY_REST_DAYS'])
        features['WIN_PCT_DIFF'] = features['HOME_WIN_PCT'] - features['AWAY_WIN_PCT']
        features['PTS_DIFF_ROLL_5'] = features['HOME_PTS_ROLL_5'] - features['AWAY_PTS_ROLL_5']
        features['FG_PCT_DIFF_ROLL_5'] = features['HOME_FG_PCT_ROLL_5'] - features['AWAY_FG_PCT_ROLL_5']
        
        return features
    
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
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 1. Modelo de probabilidad de victoria - MEJORADO CON XGBOOST
        print("  - Entrenando modelo de victoria (XGBoost)...")
        self.win_model = XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            eval_metric='logloss'
        )
        self.win_model.fit(X_train_scaled, y_win_train, verbose=False)
        
        # 2. Modelo de margen de puntos - MEJORADO CON XGBOOST
        print("  - Entrenando modelo de margen (XGBoost optimizado)...")
        self.margin_model = XGBRegressor(
            n_estimators=180,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state
        )
        self.margin_model.fit(X_train_scaled, y_margin_train, verbose=False)
        
        # 3. Modelo de puntos totales - MEJORADO CON XGBOOST
        print("  - Entrenando modelo de total de puntos (XGBoost optimizado)...")
        self.total_model = XGBRegressor(
            n_estimators=180,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state
        )
        self.total_model.fit(X_train_scaled, y_total_train, verbose=False)
        
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
        X_scaled = self.scaler.transform(X[self.feature_columns])
        
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
        self.feature_columns = save_data['feature_columns']
        
        print(f"✅ Modelos cargados desde: {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str):
        """Método de clase para cargar un modelo entrenado."""
        instance = cls()
        instance.load(filepath)
        return instance


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
