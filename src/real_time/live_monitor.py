"""
🔥 SISTEMA DE TIEMPO REAL - Multi-Deporte
Actualiza predicciones automáticamente cada 30 segundos

Características:
- Polling cada 30s para Football y Tennis
- WebSocket para NBA (ya implementado)
- Actualización de probabilidades en vivo
- Notificaciones de cambios importantes
"""

import os
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv

# Importar loaders
from src.data.football_data_loader import FootballDataLoader
from src.data.tennis_data_loader import TennisDataLoader

load_dotenv()


class LiveDataMonitor:
    """
    Monitorea partidos en vivo y actualiza predicciones automáticamente
    
    Polling strategy:
    - Football: cada 30s (suficiente para goles, corners, tarjetas)
    - Tennis: cada 30s (games, sets, serve stats)
    - NBA: WebSocket en tiempo real (ya implementado)
    """
    
    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval
        self.football_loader = FootballDataLoader()
        self.tennis_loader = TennisDataLoader()
        
        # Cache de partidos en vivo
        self.live_matches = {
            'football': pd.DataFrame(),
            'tennis': pd.DataFrame(),
            'nba': pd.DataFrame(),
        }
        
        # Última actualización
        self.last_update = {
            'football': None,
            'tennis': None,
            'nba': None,
        }
        
        # Probabilidades anteriores (para detectar cambios)
        self.previous_predictions = {}
        
        self.is_running = False
    
    def update_football_live(self) -> pd.DataFrame:
        """Actualiza partidos de fútbol en vivo"""
        try:
            live_matches = self.football_loader.get_live_matches()
            
            if not live_matches.empty:
                self.live_matches['football'] = live_matches
                self.last_update['football'] = datetime.now()
                
                print(f"⚽ Football: {len(live_matches)} partidos en vivo")
                return live_matches
            else:
                print("⚽ Football: No hay partidos en vivo")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error actualizando football: {str(e)}")
            return pd.DataFrame()
    
    def update_tennis_live(self) -> pd.DataFrame:
        """
        Actualiza partidos de tenis en vivo
        
        NOTA: GitHub data es histórico, para live necesitarías:
        - Scraping de FlashScore/ESPN
        - O pagar por API de tennis en vivo
        
        Por ahora retorna próximos partidos del día
        """
        try:
            # TODO: Implementar scraping o API de tennis live
            # Por ahora retornamos DataFrame vacío
            print("🎾 Tennis: Live data pendiente (necesita scraping)")
            return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error actualizando tennis: {str(e)}")
            return pd.DataFrame()
    
    def detect_significant_changes(self, match_id: str, 
                                   new_prediction: Dict) -> bool:
        """
        Detecta cambios significativos en probabilidades
        
        Args:
            match_id: ID del partido
            new_prediction: Nueva predicción con probabilidades
        
        Returns:
            True si hay cambio significativo (>10%)
        """
        if match_id not in self.previous_predictions:
            self.previous_predictions[match_id] = new_prediction
            return False
        
        old_pred = self.previous_predictions[match_id]
        
        # Comparar probabilidades principales
        for key in ['home_win_prob', 'draw_prob', 'away_win_prob']:
            if key in old_pred and key in new_prediction:
                old_val = old_pred[key]
                new_val = new_prediction[key]
                
                # Cambio >10% es significativo
                if abs(new_val - old_val) > 0.10:
                    print(f"🚨 CAMBIO SIGNIFICATIVO: {key} {old_val:.2%} → {new_val:.2%}")
                    self.previous_predictions[match_id] = new_prediction
                    return True
        
        return False
    
    def send_notification(self, title: str, message: str):
        """
        Envía notificación de escritorio
        
        Args:
            title: Título de notificación
            message: Mensaje
        """
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                timeout=10,
            )
        except Exception as e:
            # Si falla plyer, imprimir en consola
            print(f"🔔 {title}: {message}")
    
    async def monitor_loop(self):
        """Loop principal de monitoreo"""
        print(f"\n🔥 INICIANDO MONITOREO EN TIEMPO REAL")
        print(f"⏱️  Intervalo: {self.update_interval} segundos\n")
        
        self.is_running = True
        
        while self.is_running:
            print(f"\n{'='*60}")
            print(f"🕐 Actualización: {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            # Actualizar Football
            football_live = self.update_football_live()
            
            # Actualizar Tennis
            tennis_live = self.update_tennis_live()
            
            # TODO: Aquí irían las predicciones en vivo
            # Por ahora solo mostramos los partidos
            
            # Esperar intervalo
            await asyncio.sleep(self.update_interval)
    
    def start(self):
        """Inicia el monitoreo"""
        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoreo detenido por usuario")
            self.stop()
    
    def stop(self):
        """Detiene el monitoreo"""
        self.is_running = False
        print("✅ Monitoreo finalizado")
    
    def get_status(self) -> Dict:
        """Retorna estado actual del monitor"""
        return {
            'is_running': self.is_running,
            'last_updates': self.last_update,
            'live_matches_count': {
                'football': len(self.live_matches['football']),
                'tennis': len(self.live_matches['tennis']),
                'nba': len(self.live_matches['nba']),
            }
        }


class LivePredictor:
    """
    Actualiza predicciones en vivo basándose en datos actualizados
    
    Usa modelos pre-entrenados y re-calcula probabilidades
    cada vez que los datos cambian
    """
    
    def __init__(self):
        # TODO: Cargar modelos pre-entrenados
        self.football_model = None
        self.tennis_model = None
        self.nba_model = None
    
    def predict_football_live(self, match_data: Dict) -> Dict:
        """
        Predice resultado de partido de fútbol en vivo
        
        Args:
            match_data: Datos actuales del partido (minute, score, stats)
        
        Returns:
            Dict con probabilidades actualizadas
        """
        # TODO: Implementar predicción con modelo entrenado
        
        # Por ahora retornamos ejemplo
        return {
            'match_id': match_data.get('match_id'),
            'minute': match_data.get('minute', 0),
            'home_win_prob': 0.45,
            'draw_prob': 0.25,
            'away_win_prob': 0.30,
            'over_2_5_prob': 0.65,
            'btts_prob': 0.58,
        }
    
    def predict_tennis_live(self, match_data: Dict) -> Dict:
        """
        Predice resultado de partido de tenis en vivo
        
        Args:
            match_data: Datos actuales (set, game, serve stats)
        
        Returns:
            Dict con probabilidades actualizadas
        """
        # TODO: Implementar predicción con modelo
        
        return {
            'match_id': match_data.get('match_id'),
            'set': match_data.get('set', 1),
            'player1_win_prob': 0.62,
            'player2_win_prob': 0.38,
        }


def demo_live_monitoring():
    """Demo del sistema de monitoreo en vivo"""
    monitor = LiveDataMonitor(update_interval=30)
    
    print("🚀 Iniciando monitoreo en tiempo real...")
    print("   Presiona Ctrl+C para detener\n")
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n✅ Demo finalizado")


if __name__ == "__main__":
    demo_live_monitoring()
