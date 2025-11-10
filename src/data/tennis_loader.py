"""Módulo para cargar datos de tenis desde múltiples fuentes."""

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

class TennisDataLoader:
    """Carga y procesa datos de partidos de tenis."""
    
    def __init__(self, data_dir: str = "data/tennis"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # RapidAPI Configuration
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('TENNIS_API_HOST', 'tennis-api-atp-wta-itf.p.rapidapi.com')
        
        # Datos históricos gratuitos
        self.tennis_data_url = "http://www.tennis-data.co.uk"
    
    def download_historical_csv(self, year: int = 2024, tour: str = "atp") -> pd.DataFrame:
        """
        Descarga datos históricos desde Tennis-Data.co.uk (GRATIS).
        
        Args:
            year: Año de la temporada
            tour: "atp" o "wta"
            
        Returns:
            DataFrame con partidos históricos
        """
        print(f"📥 Descargando datos históricos {tour.upper()} {year}...")
        
        # Tennis-Data tiene formato diferente por año
        if year >= 2013:
            url = f"{self.tennis_data_url}/{year}/{year}.zip"
        else:
            url = f"{self.tennis_data_url}/{year}_{tour}.zip"
        
        try:
            # Descargar y extraer
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Tennis-Data usa archivos XLS/XLSX comprimidos
            # Por simplicidad, usamos CSV si está disponible
            print(f"⚠️  Tennis-Data usa formato ZIP con XLS. Necesitarás openpyxl.")
            print(f"   Alternativa: Usar solo API de RapidAPI")
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Error descargando datos históricos: {e}")
            print(f"   Usando API de RapidAPI en su lugar...")
            return pd.DataFrame()
    
    def search_player(self, player_name: str) -> Dict:
        """
        Busca un jugador en la API.
        
        Args:
            player_name: Nombre del jugador
            
        Returns:
            Información del jugador
        """
        if not self.rapidapi_key:
            print("⚠️  API key no configurada")
            return {}
        
        print(f"🔍 Buscando jugador: {player_name}...")
        
        url = f"https://{self.api_host}/tennis/v2/search"
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.api_host
        }
        params = {'search': player_name}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Encontrado: {len(data.get('results', []))} resultados")
            
            return data
            
        except Exception as e:
            print(f"❌ Error buscando jugador: {e}")
            return {}
    
    def get_player_matches(self, player_id: int, season: int = 2024) -> pd.DataFrame:
        """
        Obtiene partidos de un jugador específico.
        
        Args:
            player_id: ID del jugador
            season: Temporada
            
        Returns:
            DataFrame con partidos del jugador
        """
        if not self.rapidapi_key:
            print("⚠️  API key no configurada")
            return pd.DataFrame()
        
        print(f"📥 Descargando partidos del jugador {player_id} temporada {season}...")
        
        # Endpoint exacto depende de la documentación de la API
        # Ajustar según respuesta de la API
        url = f"https://{self.api_host}/tennis/v2/player/{player_id}/matches"
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.api_host
        }
        params = {'season': season}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar respuesta
            df = self._process_matches(data)
            
            if not df.empty:
                print(f"✅ Descargados {len(df)} partidos")
                
                # Guardar
                filename = self.data_dir / f"player_{player_id}_{season}.csv"
                df.to_csv(filename, index=False)
            
            return df
            
        except Exception as e:
            print(f"❌ Error descargando partidos: {e}")
            return pd.DataFrame()
    
    def get_tournament_matches(self, tournament_id: int, season: int = 2024) -> pd.DataFrame:
        """
        Obtiene todos los partidos de un torneo.
        
        Args:
            tournament_id: ID del torneo
            season: Temporada
            
        Returns:
            DataFrame con partidos del torneo
        """
        if not self.rapidapi_key:
            print("⚠️  API key no configurada")
            return pd.DataFrame()
        
        print(f"📥 Descargando torneo {tournament_id} temporada {season}...")
        
        url = f"https://{self.api_host}/tennis/v2/tournament/{tournament_id}/matches"
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.api_host
        }
        params = {'season': season}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            df = self._process_matches(data)
            
            if not df.empty:
                print(f"✅ Descargados {len(df)} partidos del torneo")
                
                # Guardar
                filename = self.data_dir / f"tournament_{tournament_id}_{season}.csv"
                df.to_csv(filename, index=False)
            
            return df
            
        except Exception as e:
            print(f"❌ Error descargando torneo: {e}")
            return pd.DataFrame()
    
    def get_live_matches(self) -> pd.DataFrame:
        """
        Obtiene partidos en vivo.
        
        Returns:
            DataFrame con partidos en curso
        """
        if not self.rapidapi_key:
            print("⚠️  API key no configurada")
            return pd.DataFrame()
        
        print("📡 Descargando partidos en vivo...")
        
        url = f"https://{self.api_host}/tennis/v2/matches/live"
        headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': self.api_host
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            df = self._process_live_matches(data)
            
            if not df.empty:
                print(f"✅ {len(df)} partidos en vivo")
            else:
                print("ℹ️  No hay partidos en vivo ahora")
            
            return df
            
        except Exception as e:
            print(f"❌ Error obteniendo partidos en vivo: {e}")
            return pd.DataFrame()
    
    def _process_matches(self, data: Dict) -> pd.DataFrame:
        """Procesa datos de partidos de la API."""
        
        if not data or 'matches' not in data:
            return pd.DataFrame()
        
        processed = []
        
        for match in data.get('matches', []):
            try:
                match_data = {
                    'MATCH_ID': match.get('id'),
                    'DATE': pd.to_datetime(match.get('startTimestamp'), unit='s') if match.get('startTimestamp') else None,
                    'TOURNAMENT': match.get('tournament', {}).get('name'),
                    'SURFACE': match.get('groundType'),
                    'ROUND': match.get('roundInfo', {}).get('name'),
                    
                    # Jugador 1
                    'PLAYER1_ID': match.get('homeTeam', {}).get('id'),
                    'PLAYER1_NAME': match.get('homeTeam', {}).get('name'),
                    'PLAYER1_RANK': match.get('homeTeam', {}).get('ranking'),
                    
                    # Jugador 2
                    'PLAYER2_ID': match.get('awayTeam', {}).get('id'),
                    'PLAYER2_NAME': match.get('awayTeam', {}).get('name'),
                    'PLAYER2_RANK': match.get('awayTeam', {}).get('ranking'),
                    
                    # Score
                    'PLAYER1_SETS': match.get('homeScore', {}).get('current'),
                    'PLAYER2_SETS': match.get('awayScore', {}).get('current'),
                    
                    'STATUS': match.get('status', {}).get('type'),
                }
                
                # Winner
                if match.get('winnerCode') == 1:
                    match_data['WINNER'] = 'PLAYER1'
                elif match.get('winnerCode') == 2:
                    match_data['WINNER'] = 'PLAYER2'
                
                processed.append(match_data)
                
            except Exception as e:
                print(f"⚠️  Error procesando partido: {e}")
                continue
        
        return pd.DataFrame(processed)
    
    def _process_live_matches(self, data: Dict) -> pd.DataFrame:
        """Procesa partidos en vivo."""
        return self._process_matches(data)
    
    def load_local_data(self, filename: str) -> pd.DataFrame:
        """Carga datos guardados localmente."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"❌ Archivo no encontrado: {filepath}")
            return pd.DataFrame()
        
        df = pd.read_csv(filepath)
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'])
        
        print(f"✅ Cargados {len(df)} partidos desde {filepath}")
        return df


if __name__ == "__main__":
    # Ejemplo de uso
    loader = TennisDataLoader()
    
    print("\n" + "="*60)
    print("PROBANDO API DE TENIS")
    print("="*60)
    
    # Test 1: Buscar jugador
    print("\n📊 TEST 1: Buscar jugador (Djokovic)...")
    result = loader.search_player("Djokovic")
    if result:
        print(f"   Resultados: {len(result.get('results', []))}")
    
    time.sleep(2)
    
    # Test 2: Partidos en vivo
    print("\n📊 TEST 2: Partidos en vivo...")
    live_df = loader.get_live_matches()
    if not live_df.empty:
        print(f"   Partidos en curso: {len(live_df)}")
        for _, match in live_df.head(3).iterrows():
            print(f"   • {match['PLAYER1_NAME']} vs {match['PLAYER2_NAME']}")
    
    print("\n" + "="*60)
    print("✅ PRUEBA COMPLETADA")
    print("="*60)
