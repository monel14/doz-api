from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
from pydantic import BaseModel
from typing import List, Optional
import logging
import time
import yt_dlp
import random
import asyncio

app = FastAPI(title="Music Streaming API - Improved", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ytmusic = YTMusic()
audio_cache = {}
CACHE_DURATION = 300  # 5 minutes au lieu de 30

# User agents rotatifs pour éviter la détection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
]

class SearchRequest(BaseModel):
    query: str
    filter: Optional[str] = "songs"
    limit: Optional[int] = 20

class PlaylistRequest(BaseModel):
    playlist_id: str

def is_cache_valid(timestamp):
    return time.time() - timestamp < CACHE_DURATION

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def extract_audio_improved(video_id: str):
    """Version améliorée avec multiples stratégies anti-détection"""
    
    strategies = [
        # Stratégie 1: Configuration légère
        {
            'name': 'lightweight',
            'opts': {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'http_headers': {
                    'User-Agent': get_random_user_agent(),
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            }
        },
        
        # Stratégie 2: Avec proxy simulation
        {
            'name': 'proxy_simulation',
            'opts': {
                'format': 'worst[ext=m4a]/worst/bestaudio',  # Format moins suspect
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': get_random_user_agent(),
                    'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                }
            }
        },
        
        # Stratégie 3: Mobile simulation
        {
            'name': 'mobile',
            'opts': {
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
            }
        },
        
        # Stratégie 4: Fallback simple
        {
            'name': 'simple',
            'opts': {
                'format': 'bestaudio',
                'quiet': True,
                'no_warnings': True,
            }
        }
    ]
    
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    for strategy in strategies:
        try:
            logging.info(f"Tentative stratégie: {strategy['name']}")
            
            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(0.5, 2.0))
            
            with yt_dlp.YoutubeDL(strategy['opts']) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                # Chercher les formats audio
                formats = info.get('formats', [])
                
                # Priorité aux formats audio purs
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                
                if audio_formats:
                    # Trier par qualité mais pas forcément prendre le meilleur (moins suspect)
                    audio_formats.sort(key=lambda x: x.get('abr', 0) or 0)
                    best_audio = audio_formats[len(audio_formats)//2]  # Prendre le format moyen
                    
                    audio_url = best_audio.get('url')
                    if audio_url:
                        logging.info(f"✅ Succès avec stratégie: {strategy['name']}")
                        return {
                            'success': True,
                            'audio_url': audio_url,
                            'title': title,
                            'duration': duration,
                            'quality': best_audio.get('abr', 'unknown'),
                            'format': best_audio.get('format_note', 'audio'),
                            'strategy': strategy['name']
                        }
                
                # Fallback: format mixte
                for fmt in formats:
                    if fmt.get('acodec') != 'none' and fmt.get('url'):
                        logging.info(f"✅ Succès fallback avec stratégie: {strategy['name']}")
                        return {
                            'success': True,
                            'audio_url': fmt.get('url'),
                            'title': title,
                            'duration': duration,
                            'quality': fmt.get('abr', 'unknown'),
                            'format': 'mixed',
                            'strategy': f"{strategy['name']}_fallback"
                        }
                        
        except Exception as e:
            logging.warning(f"❌ Échec stratégie {strategy['name']}: {str(e)[:100]}")
            continue
    
    # Toutes les stratégies ont échoué - retourner une URL YouTube directe
    logging.info("Toutes les extractions ont échoué, retour URL YouTube directe")
    return {
        'success': True,
        'audio_url': youtube_url,
        'title': 'Titre non disponible',
        'duration': 0,
        'quality': 'youtube_direct',
        'format': 'youtube_fallback',
        'strategy': 'youtube_direct',
        'note': 'URL YouTube directe - extraction impossible'
    }

@app.get("/")
async def root():
    return {"message": "Music Streaming API - Improved Anti-Detection", "version": "2.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/search")
async def search_music(request: SearchRequest):
    try:
        results = ytmusic.search(request.query, filter=request.filter, limit=request.limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/{video_id}")
async def stream_audio(video_id: str):
    try:
        # Vérifier le cache (mais avec une durée plus courte)
        if video_id in audio_cache:
            cache_entry = audio_cache[video_id]
            if is_cache_valid(cache_entry['timestamp']):
                return {
                    "audio_url": cache_entry['url'],
                    "title": cache_entry['title'],
                    "cached": True,
                    "expires_in": CACHE_DURATION - (time.time() - cache_entry['timestamp'])
                }
            else:
                # Cache expiré, le supprimer
                del audio_cache[video_id]
        
        # Extraire l'URL audio
        result = extract_audio_improved(video_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('error', 'Extraction failed'))
        
        # Mettre en cache avec timestamp actuel
        audio_cache[video_id] = {
            'url': result['audio_url'],
            'title': result['title'],
            'timestamp': time.time()
        }
        
        return {
            "audio_url": result['audio_url'],
            "title": result['title'],
            "cached": False,
            "format": result.get('format', 'audio'),
            "quality": result.get('quality', 'unknown'),
            "duration": result.get('duration', 0),
            "strategy": result.get('strategy', 'unknown'),
            "note": result.get('note', ''),
            "cache_duration": CACHE_DURATION
        }
            
    except Exception as e:
        logging.error(f"Streaming error for {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/song/{video_id}")
async def get_song_info(video_id: str):
    try:
        song_info = ytmusic.get_song(video_id)
        return song_info
    except Exception as e:
        raise HTTPException(status_code=404, detail="Song not found")

@app.get("/charts")
async def get_charts():
    try:
        # Récupérer les charts populaires
        charts = ytmusic.get_charts()
        return charts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/playlist")
async def get_playlist(request: PlaylistRequest):
    try:
        playlist = ytmusic.get_playlist(request.playlist_id)
        return playlist
    except Exception as e:
        raise HTTPException(status_code=404, detail="Playlist not found")

@app.get("/cache/stats")
async def get_cache_stats():
    return {
        "total_entries": len(audio_cache),
        "cache_duration_seconds": CACHE_DURATION,
        "entries": [
            {
                "video_id": vid,
                "title": data["title"],
                "age_seconds": time.time() - data["timestamp"]
            }
            for vid, data in audio_cache.items()
        ]
    }

@app.delete("/cache/clear")
async def clear_cache():
    global audio_cache
    count = len(audio_cache)
    audio_cache = {}
    return {"message": f"Cache vidé, {count} entrées supprimées"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)