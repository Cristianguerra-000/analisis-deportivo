"""Módulo para feature engineering de datos NBA."""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import timedelta


class NBAFeatureEngineer:
    """Genera features avanzadas para predicción de partidos NBA."""
    
    def __init__(self, initial_elo: int = 1500, k_factor: int = 20, home_advantage: int = 100):
        self.initial_elo = initial_elo
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.team_elo = {}
    
    def calculate_elo_ratings(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula ratings ELO dinámicos para todos los equipos.
        
        Args:
            games_df: DataFrame con partidos ordenados por fecha
            
        Returns:
            DataFrame con columnas ELO agregadas
        """
        games_df = games_df.copy()
        games_df['HOME_ELO_BEFORE'] = 0.0
        games_df['AWAY_ELO_BEFORE'] = 0.0
        games_df['HOME_ELO_AFTER'] = 0.0
        games_df['AWAY_ELO_AFTER'] = 0.0
        
        # Inicializar todos los equipos
        all_teams = pd.concat([
            games_df['HOME_TEAM_ID'],
            games_df['AWAY_TEAM_ID']
        ]).unique()
        
        for team_id in all_teams:
            self.team_elo[team_id] = self.initial_elo
        
        # Calcular ELO partido por partido
        for idx, game in games_df.iterrows():
            home_id = game['HOME_TEAM_ID']
            away_id = game['AWAY_TEAM_ID']
            
            # ELO antes del partido
            home_elo_before = self.team_elo[home_id]
            away_elo_before = self.team_elo[away_id]
            
            games_df.at[idx, 'HOME_ELO_BEFORE'] = home_elo_before
            games_df.at[idx, 'AWAY_ELO_BEFORE'] = away_elo_before
            
            # Probabilidad esperada (con home advantage)
            expected_home = self._expected_score(
                home_elo_before + self.home_advantage,
                away_elo_before
            )
            
            # Resultado real
            actual_home = game['HOME_WL']
            
            # Actualizar ELO
            elo_change = self.k_factor * (actual_home - expected_home)
            
            home_elo_after = home_elo_before + elo_change
            away_elo_after = away_elo_before - elo_change
            
            games_df.at[idx, 'HOME_ELO_AFTER'] = home_elo_after
            games_df.at[idx, 'AWAY_ELO_AFTER'] = away_elo_after
            
            # Actualizar diccionario
            self.team_elo[home_id] = home_elo_after
            self.team_elo[away_id] = away_elo_after
        
        # Feature: diferencia de ELO
        games_df['ELO_DIFF'] = games_df['HOME_ELO_BEFORE'] - games_df['AWAY_ELO_BEFORE']
        
        return games_df
    
    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calcula probabilidad esperada según fórmula ELO."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def add_rolling_stats(
        self,
        games_df: pd.DataFrame,
        windows: List[int] = [5, 10, 20]
    ) -> pd.DataFrame:
        """
        Añade estadísticas rolling (últimos N partidos) para cada equipo.
        
        Args:
            games_df: DataFrame con partidos
            windows: Lista de ventanas temporales (ej: [5, 10, 20] partidos)
            
        Returns:
            DataFrame con features rolling agregadas
        """
        games_df = games_df.copy()
        
        # Crear DataFrames separados para local y visitante
        home_stats = self._create_team_stats_df(games_df, 'HOME')
        away_stats = self._create_team_stats_df(games_df, 'AWAY')
        
        # Calcular rolling para cada ventana
        for window in windows:
            # Home team rolling stats - Estadísticas básicas
            for stat in ['PTS', 'FG_PCT', 'FG3_PCT', 'REB', 'AST', 'TOV']:
                col_name = f'HOME_{stat}_ROLL_{window}'
                games_df[col_name] = home_stats.groupby('TEAM_ID')[stat].transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                )
            
            # Away team rolling stats - Estadísticas básicas
            for stat in ['PTS', 'FG_PCT', 'FG3_PCT', 'REB', 'AST', 'TOV']:
                col_name = f'AWAY_{stat}_ROLL_{window}'
                games_df[col_name] = away_stats.groupby('TEAM_ID')[stat].transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                )
            
            # NUEVAS FEATURES DEFENSIVAS - Solo para ventana 5
            if window == 5 and 'HOME_STL' in games_df.columns:
                # Robos (Steals)
                games_df[f'HOME_STL_ROLL_{window}'] = home_stats.groupby('TEAM_ID')['STL'].transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                ) if 'STL' in home_stats.columns else 0
                
                games_df[f'AWAY_STL_ROLL_{window}'] = away_stats.groupby('TEAM_ID')['STL'].transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                ) if 'STL' in away_stats.columns else 0
                
                # Bloqueos (Blocks)
                games_df[f'HOME_BLK_ROLL_{window}'] = home_stats.groupby('TEAM_ID')['BLK'].transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                ) if 'BLK' in home_stats.columns else 0
                
                games_df[f'AWAY_BLK_ROLL_{window}'] = away_stats.groupby('TEAM_ID')['BLK'].transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                ) if 'BLK' in away_stats.columns else 0
        
        return games_df
    
    def _create_team_stats_df(self, games_df: pd.DataFrame, home_away: str) -> pd.DataFrame:
        """Crea DataFrame de estadísticas por equipo."""
        prefix = home_away
        
        # Columnas básicas que siempre existen
        base_cols = [
            'GAME_DATE',
            f'{prefix}_TEAM_ID',
            f'{prefix}_PTS',
            f'{prefix}_FG_PCT',
            f'{prefix}_FG3_PCT',
            f'{prefix}_REB',
            f'{prefix}_AST',
            f'{prefix}_TOV'
        ]
        
        # Agregar columnas defensivas si existen
        optional_cols = []
        for col in [f'{prefix}_STL', f'{prefix}_BLK']:
            if col in games_df.columns:
                optional_cols.append(col)
        
        all_cols = base_cols + optional_cols
        team_stats = games_df[all_cols].copy()
        
        # Renombrar columnas
        new_col_names = ['GAME_DATE', 'TEAM_ID', 'PTS', 'FG_PCT', 'FG3_PCT', 'REB', 'AST', 'TOV']
        if f'{prefix}_STL' in games_df.columns:
            new_col_names.append('STL')
        if f'{prefix}_BLK' in games_df.columns:
            new_col_names.append('BLK')
        
        team_stats.columns = new_col_names
        
        return team_stats.sort_values(['TEAM_ID', 'GAME_DATE'])
    
    def add_rest_days(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Añade días de descanso entre partidos para cada equipo."""
        games_df = games_df.copy()
        games_df = games_df.sort_values('GAME_DATE').reset_index(drop=True)
        
        games_df['HOME_REST_DAYS'] = 0
        games_df['AWAY_REST_DAYS'] = 0
        
        # Calcular días de descanso
        for team_id in games_df['HOME_TEAM_ID'].unique():
            # Partidos de este equipo (local o visitante)
            home_mask = games_df['HOME_TEAM_ID'] == team_id
            away_mask = games_df['AWAY_TEAM_ID'] == team_id
            team_games = games_df[home_mask | away_mask].copy()
            
            if len(team_games) > 1:
                team_games = team_games.sort_values('GAME_DATE')
                rest_days = team_games['GAME_DATE'].diff().dt.days.fillna(3)
                
                # Asignar a los partidos correspondientes
                for idx, (game_idx, rest) in enumerate(zip(team_games.index, rest_days)):
                    if games_df.loc[game_idx, 'HOME_TEAM_ID'] == team_id:
                        games_df.at[game_idx, 'HOME_REST_DAYS'] = rest
                    else:
                        games_df.at[game_idx, 'AWAY_REST_DAYS'] = rest
        
        # Back-to-back indicator (menos de 2 días de descanso)
        games_df['HOME_BACK_TO_BACK'] = (games_df['HOME_REST_DAYS'] < 2).astype(int)
        games_df['AWAY_BACK_TO_BACK'] = (games_df['AWAY_REST_DAYS'] < 2).astype(int)
        
        return games_df
    
    def add_win_streak(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Añade rachas de victorias/derrotas actuales."""
        games_df = games_df.copy()
        games_df['HOME_WIN_STREAK'] = 0
        games_df['AWAY_WIN_STREAK'] = 0
        
        team_streaks = {}
        
        for idx, game in games_df.iterrows():
            home_id = game['HOME_TEAM_ID']
            away_id = game['AWAY_TEAM_ID']
            
            # Obtener racha actual antes del partido
            games_df.at[idx, 'HOME_WIN_STREAK'] = team_streaks.get(home_id, 0)
            games_df.at[idx, 'AWAY_WIN_STREAK'] = team_streaks.get(away_id, 0)
            
            # Actualizar rachas después del partido
            if game['HOME_WL'] == 1:
                team_streaks[home_id] = max(0, team_streaks.get(home_id, 0)) + 1
                team_streaks[away_id] = min(0, team_streaks.get(away_id, 0)) - 1
            else:
                team_streaks[home_id] = min(0, team_streaks.get(home_id, 0)) - 1
                team_streaks[away_id] = max(0, team_streaks.get(away_id, 0)) + 1
        
        return games_df
    
    def add_season_stats(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Añade estadísticas acumuladas de la temporada hasta el momento."""
        games_df = games_df.copy()
        
        # Wins y losses acumulados
        games_df['HOME_SEASON_WINS'] = games_df.groupby(['SEASON', 'HOME_TEAM_ID'])['HOME_WL'].cumsum()
        games_df['HOME_SEASON_GAMES'] = games_df.groupby(['SEASON', 'HOME_TEAM_ID']).cumcount() + 1
        games_df['HOME_WIN_PCT'] = games_df['HOME_SEASON_WINS'] / games_df['HOME_SEASON_GAMES']
        
        # Similar para visitante (invertir resultado) - fix para Pandas 2.x
        away_wins = games_df.groupby(['SEASON', 'AWAY_TEAM_ID'])['HOME_WL'].transform(
            lambda x: (1 - x).cumsum()
        )
        games_df['AWAY_SEASON_WINS'] = away_wins
        games_df['AWAY_SEASON_GAMES'] = games_df.groupby(['SEASON', 'AWAY_TEAM_ID']).cumcount() + 1
        games_df['AWAY_WIN_PCT'] = games_df['AWAY_SEASON_WINS'] / games_df['AWAY_SEASON_GAMES']
        
        return games_df
    
    def create_all_features(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo: genera todas las features.
        
        Args:
            games_df: DataFrame con datos crudos de partidos
            
        Returns:
            DataFrame con todas las features añadidas
        """
        print("🔧 Generando features...")
        
        # Asegurar que esté ordenado por fecha
        games_df = games_df.sort_values('GAME_DATE').reset_index(drop=True)
        
        # 1. ELO ratings
        print("  - Calculando ELO ratings...")
        games_df = self.calculate_elo_ratings(games_df)
        
        # 2. Rolling statistics
        print("  - Agregando rolling statistics...")
        games_df = self.add_rolling_stats(games_df, windows=[5, 10, 20])
        
        # 3. Rest days y back-to-back
        print("  - Calculando días de descanso...")
        games_df = self.add_rest_days(games_df)
        
        # 4. Win streaks
        print("  - Calculando rachas de victorias...")
        games_df = self.add_win_streak(games_df)
        
        # 5. Season stats
        print("  - Agregando estadísticas de temporada...")
        games_df = self.add_season_stats(games_df)
        
        print("✅ Features generadas exitosamente!")
        
        return games_df


if __name__ == "__main__":
    # Ejemplo de uso
    from data_loader import NBADataLoader
    
    loader = NBADataLoader()
    games_df = loader.load_local_data("games_all_seasons.csv")
    
    if not games_df.empty:
        engineer = NBAFeatureEngineer()
        games_with_features = engineer.create_all_features(games_df)
        
        print(f"\n📊 Features creadas: {games_with_features.shape[1]} columnas")
        print("\nColumnas disponibles:")
        print(games_with_features.columns.tolist())
        
        # Guardar
        output_path = Path("data/processed/games_with_features.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        games_with_features.to_parquet(output_path)
        print(f"\n💾 Datos guardados en: {output_path}")
