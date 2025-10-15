"""
Routes pour la gestion de l'audio
"""
import logging
from flask import Blueprint, jsonify, send_file
from ..services.audio_service import AudioService

logger = logging.getLogger(__name__)

# Créer le blueprint
audio_bp = Blueprint('audio', __name__, url_prefix='/api/audio')

# Initialiser le service
audio_service = AudioService()


@audio_bp.route('/stream/<video_id>', methods=['GET'])
def get_streaming_url(video_id):
    """Obtenir l'URL de streaming pour une vidéo"""
    try:
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        result = audio_service.get_streaming_url(video_id)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Streaming URL not available'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de l'URL pour {video_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@audio_bp.route('/download/<video_id>', methods=['GET'])
def download_audio(video_id):
    """Télécharger et streamer un fichier audio"""
    try:
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        # Vérifier si le fichier existe déjà
        existing_file = audio_service.get_local_file(video_id)
        if existing_file:
            file_path = existing_file['file_path']
            filename = existing_file['filename']
            
            return send_file(
                file_path,
                as_attachment=False,
                download_name=filename,
                mimetype='audio/mpeg'
            )
        
        # Télécharger le fichier
        result = audio_service.download_audio(video_id)
        
        if result:
            file_path = result['file_path']
            filename = result['filename']
            
            return send_file(
                file_path,
                as_attachment=False,
                download_name=filename,
                mimetype='audio/mpeg'
            )
        else:
            return jsonify({'error': 'Download failed'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement pour {video_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@audio_bp.route('/files', methods=['GET'])
def list_files():
    """Lister tous les fichiers audio"""
    try:
        files = audio_service.list_files()
        total_size = sum(f['size_mb'] for f in files)
        
        return jsonify({
            'files': files,
            'total_files': len(files),
            'total_size_mb': round(total_size, 2)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors du listage des fichiers: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@audio_bp.route('/files/<video_id>', methods=['DELETE'])
def delete_file(video_id):
    """Supprimer un fichier audio"""
    try:
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        success = audio_service.delete_file(video_id)
        
        if success:
            return jsonify({'message': f'File deleted for video_id: {video_id}'}), 200
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du fichier {video_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@audio_bp.route('/files/clear', methods=['DELETE'])
def clear_all_files():
    """Supprimer tous les fichiers audio"""
    try:
        count = audio_service.clear_all_files()
        
        return jsonify({
            'message': f'Deleted {count} file(s)',
            'deleted_count': count
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de tous les fichiers: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@audio_bp.route('/info/<video_id>', methods=['GET'])
def get_file_info(video_id):
    """Obtenir les informations d'un fichier local"""
    try:
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        file_info = audio_service.get_local_file(video_id)
        
        if file_info:
            return jsonify(file_info), 200
        else:
            return jsonify({'error': 'File not found locally'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos du fichier {video_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500