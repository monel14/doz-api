from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ytmusicapi import YTMusic
from pydantic import BaseModel
from typing import List, Optional
import logging
import asyncio
import aiofiles
import os
import tempfile
import time
import json
from audio_extractor import extract_audio_url

app = FastAPI(title="Music Streaming API - Version Complète", version="2.0.0")

# Configuration CORS pour React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation de YTMusic
ytmusic = YTMusic()

# Cache simple en mémoire pour les URLs audio
audio_cache = {}
CACHE_DURATION = 1800  # 30 minutes

# Configuration yt-dlp optimisée
ydl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'extractaudio': True,
    'audioformat': 'm4a',
    'outtmpl': '%(id)s.%(ext)s',
}

# Modèles Pydantic
class SearchRequest(BaseModel):
    query: str
    filter: Optional[str] = "songs"
    limit: Optional[int] = 20

class PlaylistRequest(BaseModel):
    playlist_id: str

def is_cache_valid(timestamp):
    return time.time() - timestamp < CACHE_DURATION

def cleanup_cache():
    """Nettoie les entrées expirées du cache"""
    expired_keys = [
        key for key, value in audio_cache.items()
        if not is_cache_valid(value['timestamp'])
    ]
    for key in expired_keys:
        del audio_cache[key]

@app.get("/")
async def root():
    return {"message": "Music Streaming API - Version Complète avec yt-dlp"}

@app.post("/search")
async def search_music(request: SearchRequest):
    try:
        results = ytmusic.search(request.query, filter=request.filter, limit=request.limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/song/{video_id}")
async def get_song_info(video_id: str):
    try:
        song_info = ytmusic.get_song(video_id)
        return song_info
    except Exception as e:
        raise HTTPException(status_code=404, detail="Song not found")

@app.get("/stream/{video_id}")
async def stream_audio(video_id: str):
    """Extrait l'URL audio réelle avec yt-dlp"""
    try:
        # Nettoyer le cache périodiquement
        cleanup_cache()
        
        # Vérifier le cache d'abord
        if video_id in audio_cache:
            cache_entry = audio_cache[video_id]
            if is_cache_valid(cache_entry['timestamp']):
                return {
                    "audio_url": cache_entry['url'],
                    "title": cache_entry['title'],
                    "cached": True,
                    "expires_in": CACHE_DURATION - (time.time() - cache_entry['timestamp'])
                }
        
        # Extraire l'URL audio avec notre extracteur amélioré
        result = extract_audio_url(video_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('error', 'Extraction failed'))
        
        # Mettre en cache l'URL
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
            "strategy": result.get('strategy', 'unknown'),
            "duration": result.get('duration', 0)
        }
            
    except Exception as e:
        logging.error(f"Erreur streaming pour {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts")
async def get_charts():
    try:
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
    """Statistiques du cache"""
    cleanup_cache()
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
    """Vider le cache"""
    global audio_cache
    count = len(audio_cache)
    audio_cache = {}
    return {"message": f"Cache vidé, {count} entrées supprimées"}

if __name__ == "__main__":
    import uvicorn
    print("🎵 Démarrage du serveur API Music Streaming (Version Complète)...")
    print("📡 API disponible sur: http://localhost:8000")
    print("📡 API disponible sur: http://192.168.1.134:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🎧 Streaming audio réel activé avec yt-dlp")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)