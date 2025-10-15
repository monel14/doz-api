"""
Application Flask pour Music Streaming API
"""
import logging
from flask import Flask
from flask_cors import CORS
from .config import config


def create_app(config_name='default'):
    """Factory pour créer l'application Flask"""
    
    # Créer l'application Flask
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configurer CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configurer les logs
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enregistrer les blueprints
    from .routes.music_routes import music_bp
    from .routes.audio_routes import audio_bp
    
    app.register_blueprint(music_bp)
    app.register_blueprint(audio_bp)
    
    # Route de base
    @app.route('/')
    def index():
        return {
            'message': 'Music Streaming API - Flask Version',
            'version': '2.0.0',
            'endpoints': {
                'music': '/api/music',
                'audio': '/api/audio'
            },
            'features': [
                'YouTube Music search',
                'Audio streaming with geo-bypass',
                'File management',
                'Multi-region support'
            ]
        }
    
    # Route de santé
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'music-streaming-api',
            'version': '2.0.0'
        }
    
    return app