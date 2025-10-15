#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Flask
"""
import os
from app import create_app
from app.config import Config

# Créer l'application
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    print("🎵 Démarrage de Music Streaming API (Flask)")
    print(f"🌍 Mode: {os.getenv('FLASK_ENV', 'development')}")
    print(f"📡 URL: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 Endpoints: http://{Config.HOST}:{Config.PORT}/api/")
    print(f"📁 Fichiers audio: {Config.AUDIO_DIR}")
    print("⏹️ Ctrl+C pour arrêter")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )