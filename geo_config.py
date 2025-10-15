#!/usr/bin/env python3
"""
Configuration géographique optimisée pour l'Afrique
"""

# Configuration yt-dlp optimisée pour l'Afrique
AFRICA_YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'geo_bypass': True,
    'geo_bypass_country': 'US',  # Simuler USA
    'extractor_retries': 3,
    'fragment_retries': 3,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
}

# Régions à essayer en priorité pour l'Afrique
AFRICA_REGIONS = [
    {'language': 'en', 'location': 'US'},   # USA souvent accessible
    {'language': 'en', 'location': 'GB'},   # UK
    {'language': 'fr', 'location': 'FR'},   # France (langue commune)
    {'language': 'en', 'location': 'CA'},   # Canada
    {'language': 'en', 'location': 'AU'},   # Australie
    {'language': 'pt', 'location': 'BR'},   # Brésil
    None  # Fallback
]

# Pays de contournement pour yt-dlp
BYPASS_COUNTRIES = ['US', 'GB', 'FR', 'CA', 'AU', 'DE', 'NL', 'BR']

def get_africa_optimized_config():
    """Retourne la configuration optimisée pour l'Afrique"""
    return AFRICA_YDL_OPTS

def get_bypass_configs():
    """Génère différentes configurations de contournement"""
    configs = []
    
    for country in BYPASS_COUNTRIES:
        config = {
            **AFRICA_YDL_OPTS,
            'geo_bypass_country': country
        }
        configs.append(config)
    
    # Configuration sans contournement en dernier recours
    configs.append({
        **AFRICA_YDL_OPTS,
        'geo_bypass': False
    })
    
    return configs