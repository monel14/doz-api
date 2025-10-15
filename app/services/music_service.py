"""
Service pour la gestion de la musique avec YouTube Music API
"""
import logging
from typing import List, Dict, Optional
from ytmusicapi import YTMusic
from ..config import Config

logger = logging.getLogger(__name__)


class MusicService:
    """Service pour interagir avec YouTube Music"""
    
    def __init__(self):
        self.ytmusic = None
        self._init_ytmusic()
    
    def _init_ytmusic(self):
        """Initialiser YTMusic avec gestion des régions"""
        for region in Config.BYPASS_REGIONS:
            try:
                if region:
                    self.ytmusic = YTMusic(
                        language=region['language'], 
                        location=region['location']
                    )
                    logger.info(f"YTMusic initialisé avec région: {region}")
                else:
                    self.ytmusic = YTMusic()
                    logger.info("YTMusic initialisé sans région spécifique")
                break
            except Exception as e:
                logger.warning(f"Échec initialisation YTMusic avec région {region}: {e}")
                continue
        
        if not self.ytmusic:
            raise Exception("Impossible d'initialiser YTMusic")
    
    def search_songs(self, query: str, limit: int = 20) -> Dict:
        """Rechercher des chansons"""
        try:
            # Essayer avec différentes régions si la première échoue
            for region in Config.BYPASS_REGIONS:
                try:
                    if region:
                        temp_ytmusic = YTMusic(
                            language=region['language'], 
                            location=region['location']
                        )
                    else:
                        temp_ytmusic = self.ytmusic
                    
                    results = temp_ytmusic.search(query, filter="songs", limit=limit)
                    
                    if results:
                        logger.info(f"Recherche réussie avec région {region}: {len(results)} résultats")
                        return {
                            'results': results,
                            'total_results': len(results),
                            'region_used': region,
                            'query': query
                        }
                except Exception as e:
                    logger.warning(f"Échec recherche avec région {region}: {e}")
                    continue
            
            # Si aucune région ne fonctionne
            logger.error(f"Aucune région disponible pour la recherche: {query}")
            return {
                'results': [],
                'total_results': 0,
                'region_used': None,
                'query': query,
                'error': 'Aucune région disponible'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche '{query}': {e}")
            raise
    
    def get_song_info(self, video_id: str) -> Optional[Dict]:
        """Obtenir les informations d'une chanson"""
        try:
            song_info = self.ytmusic.get_song(video_id)
            if song_info:
                logger.info(f"Infos récupérées pour: {video_id}")
                return song_info
            else:
                logger.warning(f"Aucune info trouvée pour: {video_id}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos pour {video_id}: {e}")
            raise
    
    def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Obtenir une playlist"""
        try:
            playlist = self.ytmusic.get_playlist(playlist_id)
            if playlist:
                logger.info(f"Playlist récupérée: {playlist_id}")
                return playlist
            else:
                logger.warning(f"Playlist non trouvée: {playlist_id}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la playlist {playlist_id}: {e}")
            raise
    
    def get_charts(self) -> Optional[Dict]:
        """Obtenir les charts"""
        try:
            charts = self.ytmusic.get_charts()
            if charts:
                logger.info("Charts récupérés avec succès")
                return charts
            else:
                logger.warning("Aucun chart disponible")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des charts: {e}")
            raise