import os
import time
import hashlib
from typing import Optional, Dict
import logging

class AudioCacheManager:
    """Gestionnaire de cache pour les URLs audio"""
    
    def __init__(self, cache_duration: int = 3600):  # 1 heure par défaut
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = cache_duration
        
    def _is_expired(self, timestamp: float) -> bool:
        """Vérifie si un élément du cache a expiré"""
        return time.time() - timestamp > self.cache_duration
    
    def get(self, video_id: str) -> Optional[str]:
        """Récupère une URL audio du cache"""
        if video_id in self.cache:
            cache_entry = self.cache[video_id]
            if not self._is_expired(cache_entry['timestamp']):
                logging.info(f"Cache hit pour {video_id}")
                return cache_entry['url']
            else:
                # Supprimer l'entrée expirée
                del self.cache[video_id]
                logging.info(f"Cache expiré pour {video_id}")
        
        return None
    
    def set(self, video_id: str, audio_url: str) -> None:
        """Ajoute une URL audio au cache"""
        self.cache[video_id] = {
            'url': audio_url,
            'timestamp': time.time()
        }
        logging.info(f"Cache mis à jour pour {video_id}")
    
    def clear_expired(self) -> None:
        """Nettoie les entrées expirées du cache"""
        expired_keys = [
            key for key, value in self.cache.items()
            if self._is_expired(value['timestamp'])
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logging.info(f"Nettoyage du cache: {len(expired_keys)} entrées supprimées")
    
    def get_cache_stats(self) -> Dict:
        """Retourne les statistiques du cache"""
        return {
            'total_entries': len(self.cache),
            'cache_duration': self.cache_duration
        }

# Instance globale du gestionnaire de cache
audio_cache = AudioCacheManager()