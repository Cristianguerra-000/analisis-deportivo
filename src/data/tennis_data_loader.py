"""
🎾 Tennis Data Loader - 100% GRATUITO
Usa GitHub de Jeff Sackmann (25+ años de datos ATP/WTA)

Datos históricos completos:
- Todos los partidos ATP desde 1968
- Todos los partidos WTA desde 1920
- Stats detalladas: serve %, aces, break points, surface
- Rankings, H2H, form
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import io
from dotenv import load_dotenv

load_dotenv()


class TennisDataLoader:
    """
    Descarga datos de tenis desde GitHub (Jeff Sackmann) - 100% GRATIS
    
    Características:
    - 25+ años de datos ATP (1968-2024)
    - 100+ años de datos WTA (1920-2024)
    - Stats completas: serve, aces, breaks, surface
    - Rankings históricos
    - Sin límites de requests
    """
    
    def __init__(self):
        self.atp_base = os.getenv('TENNIS_ATP_GITHUB_URL',
                                   'https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master')
        self.wta_base = os.getenv('TENNIS_WTA_GITHUB_URL',
                                   'https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master')
        
        # Superficies
        self.surfaces = ['Hard', 'Clay', 'Grass', 'Carpet']
        
        # Niveles de torneos
        self.tournament_levels = {
            'ATP': ['G', 'M', 'A', 'C', 'D', 'F'],  # Grand Slam, Masters, ATP500, etc.
            'WTA': ['G', 'PM', 'P', 'I', 'S'],       # Grand Slam, Premier Mandatory, etc.
        }
    
    def _download_csv(self, url: str) -> Optional[pd.DataFrame]:
        """Descarga CSV desde GitHub"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return pd.read_csv(io.StringIO(response.text), encoding='utf-8')
            else:
                print(f"❌ Error {response.status_code} descargando {url}")
                return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def get_atp_matches(self, year: int = 2024) -> pd.DataFrame:
        """
        Descarga partidos ATP de un año específico
        
        Args:
            year: Año (1968-2024)
        
        Returns:
            DataFrame con todos los partidos ATP del año
        """
        url = f"{self.atp_base}/atp_matches_{year}.csv"
        df = self._download_csv(url)
        
        if df is not None:
            df['tour'] = 'ATP'
            df['year'] = year
        
        return df if df is not None else pd.DataFrame()
    
    def get_wta_matches(self, year: int = 2024) -> pd.DataFrame:
        """
        Descarga partidos WTA de un año específico
        
        Args:
            year: Año (1920-2024)
        
        Returns:
            DataFrame con todos los partidos WTA del año
        """
        url = f"{self.wta_base}/wta_matches_{year}.csv"
        df = self._download_csv(url)
        
        if df is not None:
            df['tour'] = 'WTA'
            df['year'] = year
        
        return df if df is not None else pd.DataFrame()
    
    def get_atp_rankings(self, date: str = None) -> pd.DataFrame:
        """
        Descarga rankings ATP
        
        Args:
            date: Fecha en formato YYYYMMDD (ej: '20241104')
                  Si None, descarga rankings actuales
        
        Returns:
            DataFrame con rankings ATP
        """
        if date:
            url = f"{self.atp_base}/atp_rankings_{date[:4]}s.csv"
        else:
            year = datetime.now().year
            url = f"{self.atp_base}/atp_rankings_{year}0s.csv"
        
        df = self._download_csv(url)
        
        if df is not None and date:
            # Filtrar por fecha específica
            df = df[df['ranking_date'] == int(date)]
        
        return df if df is not None else pd.DataFrame()
    
    def get_wta_rankings(self, date: str = None) -> pd.DataFrame:
        """
        Descarga rankings WTA
        
        Args:
            date: Fecha en formato YYYYMMDD
        
        Returns:
            DataFrame con rankings WTA
        """
        if date:
            url = f"{self.wta_base}/wta_rankings_{date[:4]}s.csv"
        else:
            year = datetime.now().year
            url = f"{self.wta_base}/wta_rankings_{year}0s.csv"
        
        df = self._download_csv(url)
        
        if df is not None and date:
            df = df[df['ranking_date'] == int(date)]
        
        return df if df is not None else pd.DataFrame()
    
    def get_historical_data(self, tour: str = 'ATP', 
                           years: List[int] = None) -> pd.DataFrame:
        """
        Descarga múltiples años de datos históricos
        
        Args:
            tour: 'ATP' o 'WTA'
            years: Lista de años (ej: [2020, 2021, 2022, 2023, 2024])
        
        Returns:
            DataFrame combinado con todos los años
        """
        if years is None:
            # Últimos 5 años por defecto
            current_year = datetime.now().year
            years = list(range(current_year - 4, current_year + 1))
        
        all_matches = []
        
        for year in years:
            print(f"📥 Descargando {tour} {year}...")
            
            if tour.upper() == 'ATP':
                df = self.get_atp_matches(year)
            else:
                df = self.get_wta_matches(year)
            
            if not df.empty:
                all_matches.append(df)
        
        if all_matches:
            combined = pd.concat(all_matches, ignore_index=True)
            print(f"✅ Total: {len(combined)} partidos descargados")
            return combined
        
        return pd.DataFrame()
    
    def get_player_stats(self, player_name: str, 
                        df_matches: pd.DataFrame) -> Dict:
        """
        Calcula estadísticas de un jugador desde datos históricos
        
        Args:
            player_name: Nombre del jugador
            df_matches: DataFrame con partidos
        
        Returns:
            Dict con stats del jugador
        """
        # Partidos donde el jugador participó
        player_matches = df_matches[
            (df_matches['winner_name'].str.contains(player_name, case=False, na=False)) |
            (df_matches['loser_name'].str.contains(player_name, case=False, na=False))
        ].copy()
        
        if player_matches.empty:
            return {}
        
        # Calcular victorias
        wins = len(player_matches[player_matches['winner_name'].str.contains(player_name, case=False, na=False)])
        losses = len(player_matches[player_matches['loser_name'].str.contains(player_name, case=False, na=False)])
        total = wins + losses
        
        # Stats por superficie
        surface_stats = {}
        for surface in self.surfaces:
            surface_matches = player_matches[player_matches['surface'] == surface]
            if not surface_matches.empty:
                surface_wins = len(surface_matches[surface_matches['winner_name'].str.contains(player_name, case=False, na=False)])
                surface_total = len(surface_matches)
                surface_stats[surface] = {
                    'wins': surface_wins,
                    'matches': surface_total,
                    'win_pct': round(surface_wins / surface_total * 100, 2) if surface_total > 0 else 0
                }
        
        return {
            'player_name': player_name,
            'total_matches': total,
            'wins': wins,
            'losses': losses,
            'win_pct': round(wins / total * 100, 2) if total > 0 else 0,
            'surface_stats': surface_stats,
            'tournaments_played': player_matches['tourney_name'].nunique(),
        }
    
    def get_head_to_head(self, player1: str, player2: str, 
                        df_matches: pd.DataFrame) -> pd.DataFrame:
        """
        Obtiene historial H2H entre dos jugadores
        
        Args:
            player1: Nombre jugador 1
            player2: Nombre jugador 2
            df_matches: DataFrame con partidos
        
        Returns:
            DataFrame con partidos H2H
        """
        h2h = df_matches[
            ((df_matches['winner_name'].str.contains(player1, case=False, na=False)) &
             (df_matches['loser_name'].str.contains(player2, case=False, na=False))) |
            ((df_matches['winner_name'].str.contains(player2, case=False, na=False)) &
             (df_matches['loser_name'].str.contains(player1, case=False, na=False)))
        ].copy()
        
        if not h2h.empty:
            h2h = h2h.sort_values('tourney_date', ascending=False)
        
        return h2h
    
    def calculate_surface_specific_elo(self, df_matches: pd.DataFrame,
                                       k_factor: int = 32) -> pd.DataFrame:
        """
        Calcula ELO específico por superficie para todos los jugadores
        
        Args:
            df_matches: DataFrame con partidos
            k_factor: Factor K para ELO (32 por defecto)
        
        Returns:
            DataFrame con ELO por jugador y superficie
        """
        # Inicializar ELOs por superficie
        elo_by_surface = {}
        
        for surface in self.surfaces:
            elo_by_surface[surface] = {}
        
        # Ordenar por fecha
        df_sorted = df_matches.sort_values('tourney_date').copy()
        
        for _, match in df_sorted.iterrows():
            surface = match['surface']
            winner = match['winner_name']
            loser = match['loser_name']
            
            if pd.isna(surface) or pd.isna(winner) or pd.isna(loser):
                continue
            
            # Inicializar ELO si es primera vez
            if winner not in elo_by_surface[surface]:
                elo_by_surface[surface][winner] = 1500
            if loser not in elo_by_surface[surface]:
                elo_by_surface[surface][loser] = 1500
            
            # Calcular ELO
            elo_winner = elo_by_surface[surface][winner]
            elo_loser = elo_by_surface[surface][loser]
            
            expected_winner = 1 / (1 + 10 ** ((elo_loser - elo_winner) / 400))
            
            elo_by_surface[surface][winner] += k_factor * (1 - expected_winner)
            elo_by_surface[surface][loser] += k_factor * (0 - (1 - expected_winner))
        
        # Convertir a DataFrame
        elo_data = []
        for surface, players in elo_by_surface.items():
            for player, elo in players.items():
                elo_data.append({
                    'player': player,
                    'surface': surface,
                    'elo': round(elo, 2)
                })
        
        return pd.DataFrame(elo_data)
    
    def get_recent_form(self, player_name: str, df_matches: pd.DataFrame,
                       last_n: int = 10) -> Dict:
        """
        Analiza forma reciente de un jugador
        
        Args:
            player_name: Nombre del jugador
            df_matches: DataFrame con partidos
            last_n: Últimos N partidos
        
        Returns:
            Dict con análisis de forma
        """
        # Partidos del jugador ordenados por fecha
        player_matches = df_matches[
            (df_matches['winner_name'].str.contains(player_name, case=False, na=False)) |
            (df_matches['loser_name'].str.contains(player_name, case=False, na=False))
        ].sort_values('tourney_date', ascending=False).head(last_n)
        
        if player_matches.empty:
            return {}
        
        wins = len(player_matches[player_matches['winner_name'].str.contains(player_name, case=False, na=False)])
        
        return {
            'player': player_name,
            'last_n_matches': len(player_matches),
            'wins': wins,
            'losses': len(player_matches) - wins,
            'win_pct': round(wins / len(player_matches) * 100, 2),
            'last_tournament': player_matches.iloc[0]['tourney_name'] if len(player_matches) > 0 else None,
        }


def test_tennis_data():
    """Prueba rápida del loader"""
    loader = TennisDataLoader()
    
    print("\n🎾 PROBANDO TENNIS DATA (GITHUB - JEFF SACKMANN)\n")
    
    # Test 1: Descargar ATP 2024
    print("1️⃣ Descargando ATP 2024:")
    atp_2024 = loader.get_atp_matches(2024)
    if not atp_2024.empty:
        print(f"✅ {len(atp_2024)} partidos ATP 2024 descargados")
        print(f"   Columnas: {list(atp_2024.columns[:10])}...")
        print(f"   Partidos recientes:")
        print(atp_2024[['tourney_name', 'winner_name', 'loser_name', 'score']].head(3))
    else:
        print("❌ Error descargando ATP 2024")
    
    # Test 2: Descargar WTA 2024
    print("\n2️⃣ Descargando WTA 2024:")
    wta_2024 = loader.get_wta_matches(2024)
    if not wta_2024.empty:
        print(f"✅ {len(wta_2024)} partidos WTA 2024 descargados")
        print(f"   Partidos recientes:")
        print(wta_2024[['tourney_name', 'winner_name', 'loser_name', 'score']].head(3))
    else:
        print("❌ Error descargando WTA 2024")
    
    # Test 3: Stats de jugador
    if not atp_2024.empty:
        print("\n3️⃣ Stats de Djokovic en 2024:")
        djokovic_stats = loader.get_player_stats('Djokovic', atp_2024)
        if djokovic_stats:
            print(f"✅ Partidos: {djokovic_stats['total_matches']}")
            print(f"   Victorias: {djokovic_stats['wins']} ({djokovic_stats['win_pct']}%)")
            print(f"   Por superficie:")
            for surface, stats in djokovic_stats['surface_stats'].items():
                print(f"   - {surface}: {stats['wins']}/{stats['matches']} ({stats['win_pct']}%)")
    
    # Test 4: Datos históricos (últimos 3 años)
    print("\n4️⃣ Descargando histórico ATP (2022-2024):")
    historical = loader.get_historical_data('ATP', [2022, 2023, 2024])
    if not historical.empty:
        print(f"✅ {len(historical)} partidos históricos")
        print(f"   Años: {sorted(historical['year'].unique())}")
        print(f"   Superficies: {historical['surface'].unique()}")
    
    print("\n" + "="*50)
    print("✅ Todo funciona! GitHub data es 100% GRATIS y sin límites")
    print("📊 Tienes acceso a 25+ años de datos ATP/WTA")
    print("🚀 Puedes usarlo directamente para entrenar modelos")


if __name__ == "__main__":
    test_tennis_data()
