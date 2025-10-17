from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
from pydantic import BaseModel
from typing import List, Optional
import logging
import json
import time

app = FastAPI(title="Music Streaming API", version="1.0.0")

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

# Cache simple en mémoire
audio_cache = {}
CACHE_DURATION = 3600  # 1 heure

# Modèles Pydantic
class SearchRequest(BaseModel):
    query: str
    filter: Optional[str] = "songs"
    limit: Optional[int] = 20

class PlaylistRequest(BaseModel):
    playlist_id: str

def is_cache_valid(timestamp):
    return time.time() - timestamp < CACHE_DURATION

@app.get("/")
async def root():
    return {"message": "Music Streaming API - Version Simple"}

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

@app.get("/stream/{video_id}")
async def stream_audio(video_id: str):
    """Version simplifiée du streaming - retourne une URL YouTube directe"""
    try:
        # Vérifier le cache
        if video_id in audio_cache:
            cache_entry = audio_cache[video_id]
            if is_cache_valid(cache_entry['timestamp']):
                return {
                    "audio_url": cache_entry['url'],
                    "title": cache_entry['title'],
                    "cached": True
                }
        
        # Obtenir les infos de la chanson
        song_info = ytmusic.get_song(video_id)
        
        # Pour cette version simplifiée, on retourne l'URL YouTube directe
        # Note: Ceci ne fonctionnera pas pour la lecture audio réelle
        # mais permet de tester l'interface
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Mettre en cache
        audio_cache[video_id] = {
            'url': youtube_url,
            'title': song_info.get('videoDetails', {}).get('title', 'Unknown'),
            'timestamp': time.time()
        }
        
        return {
            "audio_url": youtube_url,
            "title": song_info.get('videoDetails', {}).get('title', 'Unknown'),
            "cached": False,
            "note": "Version simplifiée - URL YouTube directe"
        }
        
    except Exception as e:
        logging.error(f"Erreur streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "cache_entries": len(audio_cache),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    print("🎵 Démarrage du serveur API Music Streaming (Version Simple)...")
    print("📡 API disponible sur: http://localhost:8001")
    print("📡 API disponible sur: http://192.168.1.134:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("⚠️  Version simplifiée sans yt-dlp")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)