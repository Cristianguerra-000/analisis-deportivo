"""Módulo para cargar datos de la NBA usando nba_api."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import time
from pathlib import Path

try:
    from nba_api.stats.endpoints import leaguegamefinder, teamgamelog
    from nba_api.stats.static import teams
except ImportError:
    print("⚠️  nba_api no está instalado. Ejecuta: pip install nba_api")
    teams = None


class NBADataLoader:
    """Carga y procesa datos de partidos de la NBA."""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_season_string(self, year: int) -> str:
        """Convierte año a formato de temporada NBA (ej: 2023 -> '2023-24')."""
        next_year = str(year + 1)[-2:]
        return f"{year}-{next_year}"
    
    def download_season_games(
        self, 
        season: str = "2024-25",
        save: bool = True
    ) -> pd.DataFrame:
        """
        Descarga todos los partidos de una temporada.
        
        Args:
            season: Temporada en formato "YYYY-YY" (ej: "2024-25")
            save: Si True, guarda los datos en CSV
            
        Returns:
            DataFrame con información de partidos
        """
        if teams is None:
            raise ImportError("nba_api no está disponible")
        
        print(f"📥 Descargando datos de la temporada {season}...")
        
        try:
            # Buscar todos los partidos de la temporada
            gamefinder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                league_id_nullable='00'
            )
            
            games_df = gamefinder.get_data_frames()[0]
            
            # Cada partido aparece 2 veces (una por equipo)
            # Agrupar por GAME_ID para obtener un registro por partido
            games_df = self._process_game_data(games_df)
            
            print(f"✅ Descargados {len(games_df)} partidos de la temporada {season}")
            
            if save:
                filename = self.data_dir / f"games_{season.replace('-', '_')}.csv"
                games_df.to_csv(filename, index=False)
                print(f"💾 Datos guardados en: {filename}")
            
            # Rate limiting para evitar bloqueos de la API
            time.sleep(1)
            
            return games_df
            
        except Exception as e:
            print(f"❌ Error descargando temporada {season}: {e}")
            return pd.DataFrame()
    
    def _process_game_data(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Procesa datos crudos para tener un registro por partido."""
        # Ordenar por fecha y game_id
        games_df = games_df.sort_values(['GAME_DATE', 'GAME_ID']).reset_index(drop=True)
        
        # Crear pares de equipos por partido
        processed_games = []
        
        for game_id in games_df['GAME_ID'].unique():
            game_data = games_df[games_df['GAME_ID'] == game_id]
            
            if len(game_data) != 2:
                continue  # Skip si no hay exactamente 2 equipos
            
            # Determinar equipo local (matchup contiene '@' o 'vs.')
            home_idx = game_data['MATCHUP'].str.contains('vs.').idxmax()
            away_idx = game_data.index[game_data.index != home_idx][0]
            
            home = game_data.loc[home_idx]
            away = game_data.loc[away_idx]
            
            processed_game = {
                'GAME_ID': game_id,
                'GAME_DATE': pd.to_datetime(home['GAME_DATE']),
                'SEASON': home['SEASON_ID'],
                
                # Equipo local
                'HOME_TEAM_ID': home['TEAM_ID'],
                'HOME_TEAM_NAME': home['TEAM_NAME'],
                'HOME_PTS': home['PTS'],
                'HOME_FGM': home['FGM'],
                'HOME_FGA': home['FGA'],
                'HOME_FG_PCT': home['FG_PCT'],
                'HOME_FG3M': home['FG3M'],
                'HOME_FG3A': home['FG3A'],
                'HOME_FG3_PCT': home['FG3_PCT'],
                'HOME_FTM': home['FTM'],
                'HOME_FTA': home['FTA'],
                'HOME_FT_PCT': home['FT_PCT'],
                'HOME_OREB': home['OREB'],
                'HOME_DREB': home['DREB'],
                'HOME_REB': home['REB'],
                'HOME_AST': home['AST'],
                'HOME_STL': home['STL'],
                'HOME_BLK': home['BLK'],
                'HOME_TOV': home['TOV'],
                'HOME_PF': home['PF'],
                
                # Equipo visitante
                'AWAY_TEAM_ID': away['TEAM_ID'],
                'AWAY_TEAM_NAME': away['TEAM_NAME'],
                'AWAY_PTS': away['PTS'],
                'AWAY_FGM': away['FGM'],
                'AWAY_FGA': away['FGA'],
                'AWAY_FG_PCT': away['FG_PCT'],
                'AWAY_FG3M': away['FG3M'],
                'AWAY_FG3A': away['FG3A'],
                'AWAY_FG3_PCT': away['FG3_PCT'],
                'AWAY_FTM': away['FTM'],
                'AWAY_FTA': away['FTA'],
                'AWAY_FT_PCT': away['FT_PCT'],
                'AWAY_OREB': away['OREB'],
                'AWAY_DREB': away['DREB'],
                'AWAY_REB': away['REB'],
                'AWAY_AST': away['AST'],
                'AWAY_STL': away['STL'],
                'AWAY_BLK': away['BLK'],
                'AWAY_TOV': away['TOV'],
                'AWAY_PF': away['PF'],
                
                # Resultado
                'HOME_WL': 1 if home['WL'] == 'W' else 0,
                'TOTAL_PTS': home['PTS'] + away['PTS'],
                'POINT_DIFF': home['PTS'] - away['PTS'],
            }
            
            processed_games.append(processed_game)
        
        return pd.DataFrame(processed_games)
    
    def download_multiple_seasons(
        self, 
        seasons: List[str],
        save: bool = True
    ) -> pd.DataFrame:
        """
        Descarga múltiples temporadas.
        
        Args:
            seasons: Lista de temporadas (ej: ["2022-23", "2023-24"])
            save: Si True, guarda cada temporada individualmente
            
        Returns:
            DataFrame combinado con todas las temporadas
        """
        all_games = []
        
        for season in seasons:
            games_df = self.download_season_games(season, save=save)
            if not games_df.empty:
                all_games.append(games_df)
            time.sleep(2)  # Pausa entre temporadas
        
        if all_games:
            combined = pd.concat(all_games, ignore_index=True)
            combined = combined.sort_values('GAME_DATE').reset_index(drop=True)
            
            if save:
                filename = self.data_dir / "games_all_seasons.csv"
                combined.to_csv(filename, index=False)
                print(f"💾 Datos combinados guardados en: {filename}")
            
            return combined
        
        return pd.DataFrame()
    
    def load_local_data(self, filename: str) -> pd.DataFrame:
        """Carga datos guardados localmente."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"❌ Archivo no encontrado: {filepath}")
            return pd.DataFrame()
        
        df = pd.read_csv(filepath)
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        
        print(f"✅ Cargados {len(df)} partidos desde {filepath}")
        return df
    
    def get_team_list(self) -> pd.DataFrame:
        """Obtiene lista de todos los equipos NBA."""
        if teams is None:
            raise ImportError("nba_api no está disponible")
        
        nba_teams = teams.get_teams()
        return pd.DataFrame(nba_teams)


if __name__ == "__main__":
    # Ejemplo de uso
    loader = NBADataLoader()
    
    # Descargar temporadas recientes
    seasons = ["2022-23", "2023-24", "2024-25"]
    df = loader.download_multiple_seasons(seasons)
    
    print(f"\n📊 Resumen de datos:")
    print(f"Total de partidos: {len(df)}")
    print(f"Rango de fechas: {df['GAME_DATE'].min()} a {df['GAME_DATE'].max()}")
    print(f"\nPrimeros partidos:")
    print(df.head())
