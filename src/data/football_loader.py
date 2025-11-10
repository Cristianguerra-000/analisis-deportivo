"""Módulo para cargar datos de fútbol desde múltiples fuentes."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import time
from pathlib import Path
import requests
from io import StringIO
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class FootballDataLoader:
    """Carga y procesa datos de partidos de fútbol."""
    
    def __init__(self, data_dir: str = "data/football"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Datos históricos GRATUITOS (sin API key necesaria)
        self.football_data_url = "https://www.football-data.co.uk/mmz4281"
        
        # RapidAPI Configuration
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('FOOTBALL_API_HOST', 'api-football-v1.p.rapidapi.com')
        
    def download_historical_csv(self, league: str = "E0", season: str = "2324") -> pd.DataFrame:
        """
        Descarga datos históricos desde Football-Data.co.uk (GRATIS).
        
        Args:
            league: Código de liga (E0=Premier, E1=Championship, SP1=La Liga, etc.)
            season: Temporada en formato "2324" para 2023-24
            
        Returns:
            DataFrame con partidos históricos
        """
        print(f"📥 Descargando datos históricos de {league} temporada {season}...")
        
        url = f"{self.football_data_url}/{season}/{league}.csv"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Leer CSV
            df = pd.read_csv(StringIO(response.text))
            
            # Procesar datos
            df = self._process_historical_data(df, league, season)
            
            # Guardar localmente
            filename = self.data_dir / f"{league}_{season}.csv"
            df.to_csv(filename, index=False)
            
            print(f"✅ Descargados {len(df)} partidos de {league}")
            return df
            
        except Exception as e:
            print(f"❌ Error descargando {league} {season}: {e}")
            return pd.DataFrame()
    
    def _process_historical_data(self, df: pd.DataFrame, league: str, season: str) -> pd.DataFrame:
        """Procesa datos crudos de Football-Data."""
        
        # Renombrar columnas clave
        column_mapping = {
            'Date': 'GAME_DATE',
            'HomeTeam': 'HOME_TEAM',
            'AwayTeam': 'AWAY_TEAM',
            'FTHG': 'HOME_GOALS',  # Full Time Home Goals
            'FTAG': 'AWAY_GOALS',  # Full Time Away Goals
            'FTR': 'RESULT',        # Full Time Result (H/A/D)
            'HTHG': 'HT_HOME_GOALS',
            'HTAG': 'HT_AWAY_GOALS',
            'HS': 'HOME_SHOTS',
            'AS': 'AWAY_SHOTS',
            'HST': 'HOME_SHOTS_TARGET',
            'AST': 'AWAY_SHOTS_TARGET',
            'HC': 'HOME_CORNERS',
            'AC': 'AWAY_CORNERS',
            'HF': 'HOME_FOULS',
            'AF': 'AWAY_FOULS',
            'HY': 'HOME_YELLOW',
            'AY': 'AWAY_YELLOW',
            'HR': 'HOME_RED',
            'AR': 'AWAY_RED',
        }
        
        # Seleccionar y renombrar columnas existentes
        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=available_cols)
        
        # Convertir fecha
        if 'GAME_DATE' in df.columns:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%d/%m/%Y', errors='coerce')
        
        # Agregar metadata
        df['LEAGUE'] = league
        df['SEASON'] = season
        
        # Calcular features básicos
        if 'HOME_GOALS' in df.columns and 'AWAY_GOALS' in df.columns:
            df['TOTAL_GOALS'] = df['HOME_GOALS'] + df['AWAY_GOALS']
            df['GOAL_DIFF'] = df['HOME_GOALS'] - df['AWAY_GOALS']
            
            # Resultado numérico (1=Home, 0=Draw, -1=Away)
            df['RESULT_NUM'] = df['RESULT'].map({'H': 1, 'D': 0, 'A': -1})
        
        # Eliminar filas con datos faltantes críticos
        df = df.dropna(subset=['GAME_DATE', 'HOME_TEAM', 'AWAY_TEAM'])
        
        return df
    
    def download_api_fixtures(self, league_id: int = 39, season: int = 2024) -> pd.DataFrame:
        """
        Descarga fixtures desde RapidAPI Football V3.
        
        Args:
            league_id: ID de liga (39=Premier, 140=La Liga, 135=Serie A, 78=Bundesliga)
            season: Año de temporada
            
        Returns:
            DataFrame con fixtures
        """
        if not self.rapidapi_key:
            print("ℹ️  RapidAPI no configurada. Usando solo datos históricos CSV.")
            return pd.DataFrame()
        
        print(f"📥 Descargando fixtures de liga {league_id} temporada {season} desde RapidAPI...")
        
        url = f"https://{self.api_host}/v3/fixtures"
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.api_host
        }
        params = {
            'league': league_id,
            'season': season,
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('results', 0) == 0:
                print("⚠️  No se encontraron partidos")
                return pd.DataFrame()
            
            # Procesar fixtures
            fixtures = data.get('response', [])
            df = self._process_api_fixtures(fixtures)
            
            # Guardar
            filename = self.data_dir / f"api_league_{league_id}_{season}.csv"
            df.to_csv(filename, index=False)
            
            print(f"✅ Descargados {len(df)} fixtures")
            return df
            
        except Exception as e:
            print(f"❌ Error con API: {e}")
            return pd.DataFrame()
    
    def _process_api_fixtures(self, fixtures: List[Dict]) -> pd.DataFrame:
        """Procesa datos de API-Football."""
        
        processed = []
        
        for fixture in fixtures:
            try:
                # Información básica
                match_data = {
                    'FIXTURE_ID': fixture['fixture']['id'],
                    'GAME_DATE': pd.to_datetime(fixture['fixture']['date']),
                    'STATUS': fixture['fixture']['status']['short'],
                    'LEAGUE': fixture['league']['name'],
                    'SEASON': fixture['league']['season'],
                    'ROUND': fixture['league']['round'],
                    'HOME_TEAM': fixture['teams']['home']['name'],
                    'HOME_TEAM_ID': fixture['teams']['home']['id'],
                    'AWAY_TEAM': fixture['teams']['away']['name'],
                    'AWAY_TEAM_ID': fixture['teams']['away']['id'],
                }
                
                # Goles (si están disponibles)
                if fixture['goals']['home'] is not None:
                    match_data['HOME_GOALS'] = fixture['goals']['home']
                    match_data['AWAY_GOALS'] = fixture['goals']['away']
                    match_data['TOTAL_GOALS'] = match_data['HOME_GOALS'] + match_data['AWAY_GOALS']
                    
                    # Resultado
                    if match_data['HOME_GOALS'] > match_data['AWAY_GOALS']:
                        match_data['RESULT'] = 'H'
                        match_data['RESULT_NUM'] = 1
                    elif match_data['HOME_GOALS'] < match_data['AWAY_GOALS']:
                        match_data['RESULT'] = 'A'
                        match_data['RESULT_NUM'] = -1
                    else:
                        match_data['RESULT'] = 'D'
                        match_data['RESULT_NUM'] = 0
                
                processed.append(match_data)
                
            except Exception as e:
                print(f"⚠️  Error procesando fixture: {e}")
                continue
        
        return pd.DataFrame(processed)
    
    def download_multiple_leagues(
        self, 
        leagues: List[str] = ["E0", "SP1", "I1", "D1"],
        seasons: List[str] = ["2223", "2324"]
    ) -> pd.DataFrame:
        """
        Descarga múltiples ligas y temporadas.
        
        Args:
            leagues: Lista de códigos de liga
            seasons: Lista de temporadas
            
        Returns:
            DataFrame combinado
        """
        all_data = []
        
        for league in leagues:
            for season in seasons:
                df = self.download_historical_csv(league, season)
                if not df.empty:
                    all_data.append(df)
                time.sleep(1)  # Rate limiting cortés
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined = combined.sort_values('GAME_DATE').reset_index(drop=True)
            
            # Guardar combinado
            filename = self.data_dir / "all_leagues_combined.csv"
            combined.to_csv(filename, index=False)
            print(f"✅ Total de partidos combinados: {len(combined)}")
            
            return combined
        
        return pd.DataFrame()
    
    def load_local_data(self, filename: str) -> pd.DataFrame:
        """Carga datos guardados localmente."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"❌ Archivo no encontrado: {filepath}")
            return pd.DataFrame()
        
        df = pd.read_csv(filepath)
        if 'GAME_DATE' in df.columns:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        
        print(f"✅ Cargados {len(df)} partidos desde {filepath}")
        return df


if __name__ == "__main__":
    # Ejemplo de uso
    loader = FootballDataLoader()
    
    # Descargar datos históricos GRATIS
    print("\n" + "="*60)
    print("DESCARGANDO DATOS HISTÓRICOS (GRATIS)")
    print("="*60)
    
    leagues = {
        'E0': 'Premier League',
        'SP1': 'La Liga',
        'I1': 'Serie A',
        'D1': 'Bundesliga',
        'F1': 'Ligue 1'
    }
    
    for code, name in leagues.items():
        print(f"\n{name} ({code}):")
        df = loader.download_historical_csv(code, "2324")  # Temporada 2023-24
        if not df.empty:
            print(f"  - Partidos: {len(df)}")
            print(f"  - Rango: {df['GAME_DATE'].min()} a {df['GAME_DATE'].max()}")
        time.sleep(2)
    
    # Combinar todas las ligas
    print("\n" + "="*60)
    print("COMBINANDO LIGAS")
    print("="*60)
    
    combined = loader.download_multiple_leagues(
        leagues=list(leagues.keys()),
        seasons=["2223", "2324"]  # Últimas 2 temporadas
    )
    
    print(f"\n📊 Resumen final:")
    print(f"Total partidos: {len(combined)}")
    print(f"Ligas: {combined['LEAGUE'].nunique()}")
    print(f"Equipos únicos: {pd.concat([combined['HOME_TEAM'], combined['AWAY_TEAM']]).nunique()}")
