"""
Configuration de l'application Flask
"""
import os
from pathlib import Path

class Config:
    """Configuration de base"""
    
    # Dossiers
    BASE_DIR = Path(__file__).parent.parent
    AUDIO_DIR = BASE_DIR / "audio_files"
    
    # API
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # YouTube/Music
    YT_DLP_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'extractor_retries': 3,
        'fragment_retries': 3,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
    }
    
    # Régions pour contournement géographique
    BYPASS_REGIONS = [
        {'language': 'en', 'location': 'US'},
        {'language': 'en', 'location': 'GB'},
        {'language': 'fr', 'location': 'FR'},
        {'language': 'en', 'location': 'CA'},
        {'language': 'en', 'location': 'AU'},
        None  # Fallback
    ]
    
    # Cache
    CACHE_TTL = 3600  # 1 heure
    STREAM_CACHE_TTL = 1800  # 30 minutes
    
    @classmethod
    def init_app(cls, app):
        """Initialiser la configuration pour l'app"""
        # Créer le dossier audio s'il n'existe pas
        cls.AUDIO_DIR.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False


# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}