"""
Routes pour la gestion de la musique
"""
import logging
from flask import Blueprint, request, jsonify
from ..services.music_service import MusicService

logger = logging.getLogger(__name__)

# Créer le blueprint
music_bp = Blueprint('music', __name__, url_prefix='/api/music')

# Initialiser le service
music_service = MusicService()


@music_bp.route('/search', methods=['POST'])
def search_music():
    """Rechercher de la musique"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        limit = data.get('limit', 20)
        
        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        result = music_service.search_songs(query, limit)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@music_bp.route('/song/<video_id>', methods=['GET'])
def get_song_info(video_id):
    """Obtenir les informations d'une chanson"""
    try:
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        song_info = music_service.get_song_info(video_id)
        
        if song_info:
            return jsonify(song_info), 200
        else:
            return jsonify({'error': 'Song not found'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos pour {video_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@music_bp.route('/playlist/<playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Obtenir une playlist"""
    try:
        if not playlist_id:
            return jsonify({'error': 'Playlist ID is required'}), 400
        
        playlist = music_service.get_playlist(playlist_id)
        
        if playlist:
            return jsonify(playlist), 200
        else:
            return jsonify({'error': 'Playlist not found'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la playlist {playlist_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@music_bp.route('/charts', methods=['GET'])
def get_charts():
    """Obtenir les charts"""
    try:
        charts = music_service.get_charts()
        
        if charts:
            return jsonify(charts), 200
        else:
            return jsonify({'error': 'Charts not available'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des charts: {e}")
        return jsonify({'error': 'Internal server error'}), 500