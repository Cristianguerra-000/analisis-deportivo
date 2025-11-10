"""
🔥 DEMO: TU IA ANALIZANDO DATOS EN TIEMPO REAL

Este script muestra cómo tu IA puede usar los datos de Tenis AHORA MISMO
para hacer análisis y predicciones.

Sin necesidad de API keys, sin límites, 100% funcional.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.data.tennis_data_loader import TennisDataLoader
import pandas as pd
from datetime import datetime


def demo_analisis_tiempo_real():
    """
    Simula cómo tu IA analizará partidos en tiempo real
    """
    print("\n" + "🔥"*35)
    print("🔥  DEMO: IA ANALIZANDO TENIS EN TIEMPO REAL  🔥")
    print("🔥"*35 + "\n")
    
    loader = TennisDataLoader()
    
    # ===== PASO 1: DESCARGAR DATOS =====
    print("📥 PASO 1: Descargando datos históricos...")
    atp_2024 = loader.get_atp_matches(2024)
    print(f"✅ {len(atp_2024)} partidos ATP 2024 descargados\n")
    
    # ===== PASO 2: ANÁLISIS DE JUGADOR =====
    print("🎾 PASO 2: Análisis de jugador (Ejemplo: Djokovic)")
    print("-" * 60)
    
    stats_djokovic = loader.get_player_stats('Djokovic', atp_2024)
    if stats_djokovic:
        print(f"Jugador: {stats_djokovic['player_name']}")
        print(f"Partidos jugados: {stats_djokovic['total_matches']}")
        print(f"Balance: {stats_djokovic['wins']}W - {stats_djokovic['losses']}L")
        print(f"Win %: {stats_djokovic['win_pct']:.1f}%")
        print(f"\nRendimiento por superficie:")
        for surface, s_stats in stats_djokovic.get('surface_stats', {}).items():
            print(f"  {surface:8s}: {s_stats['wins']:2d}W - {s_stats['matches']-s_stats['wins']:2d}L ({s_stats['win_pct']:5.1f}%)")
    
    # ===== PASO 3: H2H ANALYSIS =====
    print("\n\n🔍 PASO 3: Head-to-Head Analysis")
    print("-" * 60)
    
    h2h = loader.get_head_to_head('Djokovic', 'Alcaraz', atp_2024)
    if not h2h.empty:
        print(f"Partidos H2H encontrados: {len(h2h)}")
        print("\nÚltimos enfrentamientos:")
        for _, match in h2h.head(3).iterrows():
            print(f"  {match['tourney_name']:25s} ({match['surface']:8s}): {match['winner_name']}")
    else:
        print("No hay enfrentamientos en 2024")
    
    # ===== PASO 4: FORMA RECIENTE =====
    print("\n\n📈 PASO 4: Forma Reciente (últimos 10 partidos)")
    print("-" * 60)
    
    form = loader.get_recent_form('Djokovic', atp_2024, last_n=10)
    if form:
        print(f"Últimos {form['last_n_matches']} partidos:")
        print(f"  Balance: {form['wins']}W - {form['losses']}L")
        print(f"  Win %: {form['win_pct']:.1f}%")
        print(f"  Último torneo: {form['last_tournament']}")
    
    # ===== PASO 5: CÁLCULO ELO =====
    print("\n\n⚡ PASO 5: ELO por superficie (Top 10 jugadores)")
    print("-" * 60)
    
    print("Calculando ELO de todos los jugadores...")
    elo_df = loader.calculate_surface_specific_elo(atp_2024, k_factor=32)
    
    if not elo_df.empty:
        # Top 10 en Hard
        print("\n🏆 Top 10 ELO en Hard Court:")
        top_hard = elo_df[elo_df['surface'] == 'Hard'].nlargest(10, 'elo')
        for i, (_, row) in enumerate(top_hard.iterrows(), 1):
            print(f"  {i:2d}. {row['player']:25s} - ELO: {row['elo']:.0f}")
    
    # ===== PASO 6: SIMULACIÓN PREDICCIÓN =====
    print("\n\n🧠 PASO 6: SIMULACIÓN DE PREDICCIÓN")
    print("-" * 60)
    print("Partido hipotético: Djokovic vs Alcaraz (Hard Court)")
    print("\nDatos de entrada para tu IA:")
    
    # Stats Djokovic
    djoko_hard = stats_djokovic['surface_stats'].get('Hard', {})
    print(f"\nDjokovic (Hard):")
    print(f"  - Win %: {djoko_hard.get('win_pct', 0):.1f}%")
    print(f"  - Partidos: {djoko_hard.get('matches', 0)}")
    
    # Stats Alcaraz
    stats_alcaraz = loader.get_player_stats('Alcaraz', atp_2024)
    if stats_alcaraz:
        alcaraz_hard = stats_alcaraz['surface_stats'].get('Hard', {})
        print(f"\nAlcaraz (Hard):")
        print(f"  - Win %: {alcaraz_hard.get('win_pct', 0):.1f}%")
        print(f"  - Partidos: {alcaraz_hard.get('matches', 0)}")
    
    # ELO
    djoko_elo = elo_df[(elo_df['player'].str.contains('Djokovic')) & 
                       (elo_df['surface'] == 'Hard')]['elo'].values
    alcaraz_elo = elo_df[(elo_df['player'].str.contains('Alcaraz')) & 
                         (elo_df['surface'] == 'Hard')]['elo'].values
    
    if len(djoko_elo) > 0 and len(alcaraz_elo) > 0:
        print(f"\nELO Comparison:")
        print(f"  - Djokovic ELO: {djoko_elo[0]:.0f}")
        print(f"  - Alcaraz ELO: {alcaraz_elo[0]:.0f}")
        
        # Calcular probabilidad básica con ELO
        expected_djoko = 1 / (1 + 10 ** ((alcaraz_elo[0] - djoko_elo[0]) / 400))
        print(f"\n🎯 PREDICCIÓN SIMPLE (basada en ELO):")
        print(f"  - Djokovic: {expected_djoko:.1%}")
        print(f"  - Alcaraz: {1-expected_djoko:.1%}")
    
    # ===== RESUMEN =====
    print("\n\n" + "="*60)
    print("📊 RESUMEN: LO QUE TU IA PUEDE HACER")
    print("="*60)
    print("""
✅ Análisis de jugadores:
   - Win rate general y por superficie
   - Torneos jugados, forma reciente
   
✅ Head-to-Head histórico:
   - Partidos directos entre 2 jugadores
   - Resultados por superficie
   
✅ Sistema ELO por superficie:
   - Rankings específicos Clay/Hard/Grass
   - Predicción probabilística basada en ELO
   
✅ Forma reciente:
   - Últimos N partidos
   - Tendencias de victorias/derrotas
   
🔥 TODO ESTO FUNCIONA AHORA MISMO
   Sin API keys, sin límites, 100% gratis
   
🚀 PRÓXIMO PASO:
   Entrenar modelos ML con estos datos:
   - Regresión logística para ganador
   - XGBoost para total de games
   - Features: ELO + surface + H2H + forma
    """)
    
    # ===== ESTADÍSTICAS FINALES =====
    print("\n📈 DATOS DISPONIBLES PARA ENTRENAR:")
    print(f"   - Partidos ATP 2024: {len(atp_2024):,}")
    
    # Descargar más años
    print("\n   Descargando más datos...")
    historical = loader.get_historical_data('ATP', [2022, 2023, 2024])
    if not historical.empty:
        print(f"   - Partidos 2022-2024: {len(historical):,}")
        print(f"   - Jugadores únicos: {pd.concat([historical['winner_name'], historical['loser_name']]).nunique():,}")
        print(f"   - Torneos: {historical['tourney_name'].nunique()}")
        print(f"   - Superficies: {', '.join(historical['surface'].dropna().unique())}")
    
    print("\n✅ SISTEMA LISTO PARA ENTRENAR MODELOS ML")


if __name__ == "__main__":
    demo_analisis_tiempo_real()
