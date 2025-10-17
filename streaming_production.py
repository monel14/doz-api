from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
from pydantic import BaseModel
from typing import List, Optional
import logging
import time
import yt_dlp

app = FastAPI(title="Music Streaming API - Production", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ytmusic = YTMusic()
audio_cache = {}
CACHE_DURATION = 1800

class SearchRequest(BaseModel):
    query: str
    filter: Optional[str] = "songs"
    limit: Optional[int] = 20

def is_cache_valid(timestamp):
    return time.time() - timestamp < CACHE_DURATION

def extract_audio_simple(video_id: str):
    """Version simplifiée pour la production"""
    try:
        # Configuration yt-dlp optimisée pour la production
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Chercher le meilleur format audio
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none']
            
            if audio_formats:
                # Prendre le format avec la meilleure qualité audio
                best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                audio_url = best_audio.get('url')
                
                if audio_url:
                    return {
                        'success': True,
                        'audio_url': audio_url,
                        'title': title,
                        'duration': duration,
                        'quality': best_audio.get('abr', 'unknown'),
                        'format': best_audio.get('format_note', 'audio')
                    }
            
            # Fallback: premier format avec audio
            for fmt in formats:
                if fmt.get('acodec') != 'none' and fmt.get('url'):
                    return {
                        'success': True,
                        'audio_url': fmt.get('url'),
                        'title': title,
                        'duration': duration,
                        'quality': fmt.get('abr', 'unknown'),
                        'format': 'fallback'
                    }
                    
    except Exception as e:
        logging.error(f"Extraction error: {e}")
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'No audio format found'}

@app.get("/")
async def root():
    return {"message": "Music Streaming API - Production Ready"}

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
        # Vérifier le cache
        if video_id in audio_cache:
            cache_entry = audio_cache[video_id]
            if is_cache_valid(cache_entry['timestamp']):
                return {
                    "audio_url": cache_entry['url'],
                    "title": cache_entry['title'],
                    "cached": True,
                    "expires_in": CACHE_DURATION - (time.time() - cache_entry['timestamp'])
                }
        
        # Extraire l'URL audio
        result = extract_audio_simple(video_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('error', 'Extraction failed'))
        
        # Mettre en cache
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
            "duration": result.get('duration', 0)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)