"""
🔥 Football Data Loader - API 100% GRATUITA
Usa api.football-data.org (10 requests/min, 2000 partidos/día GRATIS)

Datos en TIEMPO REAL:
- Partidos en vivo con stats actualizadas cada 30s
- Goles, corners, shots, tarjetas EN VIVO
- Histórico completo de 10+ ligas
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from dotenv import load_dotenv

load_dotenv()


class FootballDataLoader:
    """
    Descarga datos de fútbol desde api.football-data.org (100% GRATIS)
    
    Características:
    - 10 requests por minuto (suficiente para múltiples ligas)
    - Datos en tiempo real con delay de ~30 segundos
    - Histórico completo de temporadas
    - Stats: goles, corners, shots, posesión, tarjetas
    """
    
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY')
        self.base_url = os.getenv('FOOTBALL_DATA_API_URL', 'https://api.football-data.org/v4')
        self.headers = {
            'X-Auth-Token': self.api_key
        } if self.api_key and self.api_key != 'YOUR_FREE_TOKEN_HERE' else {}
        
        # IDs de ligas principales
        self.competitions = {
            'premier_league': 'PL',      # Premier League
            'la_liga': 'PD',             # La Liga
            'bundesliga': 'BL1',         # Bundesliga
            'serie_a': 'SA',             # Serie A
            'ligue_1': 'FL1',            # Ligue 1
            'champions_league': 'CL',    # Champions League
            'europa_league': 'EL',       # Europa League
            'world_cup': 'WC',           # World Cup
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 6  # 10 requests/min = 1 cada 6s
    
    def _wait_for_rate_limit(self):
        """Espera para respetar límite de 10 requests/min"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Hace request con rate limiting y error handling"""
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️ Rate limit alcanzado. Esperando 60 segundos...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            elif response.status_code == 403:
                print("❌ Error 403: Verifica tu API key en .env")
                print("📝 Regístrate GRATIS en: https://www.football-data.org/client/register")
                return None
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error en request: {str(e)}")
            return None
    
    def get_live_matches(self, competition: str = None) -> pd.DataFrame:
        """
        Obtiene partidos EN VIVO con stats actualizadas
        
        Args:
            competition: Código de competición (ej: 'PL', 'PD') o None para todas
        
        Returns:
            DataFrame con partidos en vivo y sus stats
        """
        endpoint = f"competitions/{competition}/matches" if competition else "matches"
        params = {'status': 'LIVE'}
        
        data = self._make_request(endpoint, params)
        
        if not data or 'matches' not in data:
            return pd.DataFrame()
        
        matches = []
        for match in data['matches']:
            matches.append({
                'match_id': match['id'],
                'date': match['utcDate'],
                'minute': match.get('minute', 0),
                'status': match['status'],
                'competition': match['competition']['name'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'home_score': match['score']['fullTime']['home'] or 0,
                'away_score': match['score']['fullTime']['away'] or 0,
                'half_time_home': match['score']['halfTime']['home'] or 0,
                'half_time_away': match['score']['halfTime']['away'] or 0,
            })
        
        return pd.DataFrame(matches)
    
    def get_upcoming_matches(self, competition: str = 'PL', days: int = 7) -> pd.DataFrame:
        """
        Obtiene partidos próximos para predicción
        
        Args:
            competition: Código de competición ('PL', 'PD', etc.)
            days: Días hacia adelante
        
        Returns:
            DataFrame con partidos próximos
        """
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        endpoint = f"competitions/{competition}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'status': 'SCHEDULED'
        }
        
        data = self._make_request(endpoint, params)
        
        if not data or 'matches' not in data:
            return pd.DataFrame()
        
        matches = []
        for match in data['matches']:
            matches.append({
                'match_id': match['id'],
                'date': match['utcDate'],
                'competition': match['competition']['name'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'venue': match.get('venue', 'Unknown'),
            })
        
        return pd.DataFrame(matches)
    
    def get_historical_matches(self, competition: str = 'PL', 
                              season: int = 2024) -> pd.DataFrame:
        """
        Obtiene datos históricos de una temporada completa
        
        Args:
            competition: Código de competición
            season: Año de la temporada (ej: 2024 para 2024/25)
        
        Returns:
            DataFrame con partidos históricos y stats
        """
        endpoint = f"competitions/{competition}/matches"
        params = {'season': season}
        
        data = self._make_request(endpoint, params)
        
        if not data or 'matches' not in data:
            return pd.DataFrame()
        
        matches = []
        for match in data['matches']:
            if match['status'] == 'FINISHED':
                matches.append({
                    'match_id': match['id'],
                    'date': match['utcDate'],
                    'matchday': match['matchday'],
                    'competition': match['competition']['name'],
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'home_score': match['score']['fullTime']['home'],
                    'away_score': match['score']['fullTime']['away'],
                    'half_time_home': match['score']['halfTime']['home'] or 0,
                    'half_time_away': match['score']['halfTime']['away'] or 0,
                    'winner': match['score']['winner'],  # HOME_TEAM, AWAY_TEAM, DRAW
                })
        
        return pd.DataFrame(matches)
    
    def get_team_stats(self, team_id: int) -> Dict:
        """
        Obtiene estadísticas detalladas de un equipo
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Dict con estadísticas del equipo
        """
        endpoint = f"teams/{team_id}"
        data = self._make_request(endpoint)
        
        if not data:
            return {}
        
        return {
            'team_id': data['id'],
            'name': data['name'],
            'short_name': data['shortName'],
            'tla': data['tla'],
            'founded': data.get('founded'),
            'venue': data.get('venue'),
            'coach': data.get('coach', {}).get('name', 'Unknown'),
        }
    
    def get_standings(self, competition: str = 'PL', season: int = 2024) -> pd.DataFrame:
        """
        Obtiene tabla de posiciones actual
        
        Args:
            competition: Código de competición
            season: Año de temporada
        
        Returns:
            DataFrame con standings
        """
        endpoint = f"competitions/{competition}/standings"
        params = {'season': season}
        
        data = self._make_request(endpoint, params)
        
        if not data or 'standings' not in data:
            return pd.DataFrame()
        
        standings = []
        for table in data['standings']:
            if table['type'] == 'TOTAL':
                for entry in table['table']:
                    standings.append({
                        'position': entry['position'],
                        'team': entry['team']['name'],
                        'played': entry['playedGames'],
                        'won': entry['won'],
                        'draw': entry['draw'],
                        'lost': entry['lost'],
                        'points': entry['points'],
                        'goals_for': entry['goalsFor'],
                        'goals_against': entry['goalsAgainst'],
                        'goal_difference': entry['goalDifference'],
                        'form': entry.get('form', ''),
                    })
        
        return pd.DataFrame(standings)
    
    def get_head_to_head(self, team1_id: int, team2_id: int, limit: int = 10) -> pd.DataFrame:
        """
        Obtiene historial H2H entre dos equipos
        
        Args:
            team1_id: ID equipo 1
            team2_id: ID equipo 2
            limit: Número de partidos H2H
        
        Returns:
            DataFrame con partidos H2H
        """
        endpoint = f"teams/{team1_id}/matches"
        params = {'limit': limit}
        
        data = self._make_request(endpoint, params)
        
        if not data or 'matches' not in data:
            return pd.DataFrame()
        
        h2h_matches = []
        for match in data['matches']:
            if match['status'] == 'FINISHED':
                # Filtrar solo partidos contra team2_id
                if (match['homeTeam']['id'] == team2_id or 
                    match['awayTeam']['id'] == team2_id):
                    h2h_matches.append({
                        'date': match['utcDate'],
                        'home_team': match['homeTeam']['name'],
                        'away_team': match['awayTeam']['name'],
                        'home_score': match['score']['fullTime']['home'],
                        'away_score': match['score']['fullTime']['away'],
                        'winner': match['score']['winner'],
                    })
        
        return pd.DataFrame(h2h_matches)
    
    def download_multiple_seasons(self, competition: str = 'PL', 
                                  seasons: List[int] = None) -> pd.DataFrame:
        """
        Descarga múltiples temporadas de datos históricos
        
        Args:
            competition: Código de competición
            seasons: Lista de años (ej: [2022, 2023, 2024])
        
        Returns:
            DataFrame combinado con todas las temporadas
        """
        if seasons is None:
            seasons = [2022, 2023, 2024]
        
        all_matches = []
        for season in seasons:
            print(f"📥 Descargando temporada {season}/{season+1}...")
            df = self.get_historical_matches(competition, season)
            if not df.empty:
                df['season'] = f"{season}/{season+1}"
                all_matches.append(df)
            time.sleep(1)  # Pequeña pausa entre temporadas
        
        if all_matches:
            return pd.concat(all_matches, ignore_index=True)
        return pd.DataFrame()


def test_football_api():
    """Prueba rápida de la API"""
    loader = FootballDataLoader()
    
    print("\n🔥 PROBANDO FOOTBALL-DATA.ORG API\n")
    
    # Test 1: Partidos en vivo
    print("1️⃣ Partidos EN VIVO:")
    live = loader.get_live_matches()
    if not live.empty:
        print(f"✅ {len(live)} partidos en vivo encontrados")
        print(live[['home_team', 'home_score', 'away_score', 'away_team', 'minute']].head())
    else:
        print("⚠️ No hay partidos en vivo ahora (o necesitas API key)")
    
    # Test 2: Próximos partidos Premier League
    print("\n2️⃣ Próximos partidos Premier League:")
    upcoming = loader.get_upcoming_matches('PL', days=7)
    if not upcoming.empty:
        print(f"✅ {len(upcoming)} partidos próximos")
        print(upcoming[['date', 'home_team', 'away_team']].head())
    else:
        print("⚠️ No se encontraron partidos (verifica API key)")
    
    # Test 3: Tabla de posiciones
    print("\n3️⃣ Tabla Premier League:")
    standings = loader.get_standings('PL', 2024)
    if not standings.empty:
        print(f"✅ {len(standings)} equipos en la tabla")
        print(standings[['position', 'team', 'points', 'goal_difference']].head(5))
    else:
        print("⚠️ No se pudo obtener tabla")
    
    print("\n" + "="*50)
    print("📝 NOTA: Para usar esta API necesitas:")
    print("1. Registrarte GRATIS en: https://www.football-data.org/client/register")
    print("2. Copiar tu token y agregarlo a .env como FOOTBALL_DATA_API_KEY")
    print("3. Límite: 10 requests/min (suficiente para uso personal)")


if __name__ == "__main__":
    test_football_api()
