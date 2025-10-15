"""
Service pour la gestion de l'audio (téléchargement et streaming)
"""
import os
import logging
from typing import Dict, Optional, List
from pathlib import Path
import yt_dlp
from ..config import Config

logger = logging.getLogger(__name__)


class AudioService:
    """Service pour gérer l'audio avec yt-dlp"""
    
    def __init__(self):
        self.audio_dir = Config.AUDIO_DIR
        self.audio_dir.mkdir(exist_ok=True)
    
    def get_streaming_url(self, video_id: str) -> Optional[Dict]:
        """Obtenir l'URL de streaming pour une vidéo"""
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Configurations de contournement géographique
        bypass_configs = self._get_bypass_configs()
        
        for i, config in enumerate(bypass_configs):
            try:
                country = config.get('geo_bypass_country', 'default')
                logger.info(f"Tentative extraction URL {i+1}/{len(bypass_configs)} avec pays: {country}")
                
                with yt_dlp.YoutubeDL(config) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    
                    # Trouver le meilleur format audio
                    audio_url = None
                    for format_info in info.get('formats', []):
                        if format_info.get('acodec') != 'none':
                            audio_url = format_info.get('url')
                            break
                    
                    if audio_url:
                        logger.info(f"✅ URL extraite avec succès avec pays: {country}")
                        return {
                            'audio_url': audio_url,
                            'title': info.get('title', 'Unknown'),
                            'duration': info.get('duration', 0),
                            'quality': format_info.get('abr', 'unknown'),
                            'format': format_info.get('ext', 'unknown'),
                            'country_used': country
                        }
                        
            except Exception as e:
                logger.warning(f"❌ Échec extraction avec {country}: {str(e)[:100]}")
                continue
        
        logger.error(f"Impossible d'extraire l'URL pour {video_id}")
        return None
    
    def download_audio(self, video_id: str) -> Optional[Dict]:
        """Télécharger un fichier audio"""
        # Vérifier si le fichier existe déjà
        existing_file = self.get_local_file(video_id)
        if existing_file:
            logger.info(f"Fichier existant trouvé: {existing_file['filename']}")
            return existing_file
        
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        output_path = self.audio_dir / f"{video_id}.%(ext)s"
        
        # Configurations de téléchargement
        download_configs = self._get_download_configs(str(output_path))
        
        for i, config in enumerate(download_configs):
            try:
                country = config.get('geo_bypass_country', 'default')
                logger.info(f"Tentative téléchargement {i+1}/{len(download_configs)} avec pays: {country}")
                
                with yt_dlp.YoutubeDL(config) as ydl:
                    ydl.download([youtube_url])
                
                # Trouver le fichier téléchargé
                downloaded_files = [f for f in os.listdir(self.audio_dir) if f.startswith(video_id)]
                if downloaded_files:
                    filename = downloaded_files[0]
                    file_path = self.audio_dir / filename
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    logger.info(f"✅ Téléchargement réussi: {filename} ({size_mb:.2f} MB)")
                    return {
                        'video_id': video_id,
                        'filename': filename,
                        'file_path': str(file_path),
                        'size_mb': round(size_mb, 2),
                        'country_used': country
                    }
                    
            except Exception as e:
                logger.warning(f"❌ Échec téléchargement avec {country}: {str(e)[:100]}")
                continue
        
        logger.error(f"Impossible de télécharger {video_id}")
        return None
    
    def get_local_file(self, video_id: str) -> Optional[Dict]:
        """Obtenir un fichier local s'il existe"""
        try:
            files = [f for f in os.listdir(self.audio_dir) if f.startswith(video_id)]
            if files:
                filename = files[0]
                file_path = self.audio_dir / filename
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    return {
                        'video_id': video_id,
                        'filename': filename,
                        'file_path': str(file_path),
                        'size_mb': round(size_mb, 2),
                        'exists': True
                    }
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du fichier local {video_id}: {e}")
            return None
    
    def list_files(self) -> List[Dict]:
        """Lister tous les fichiers audio"""
        try:
            files = []
            for file_path in self.audio_dir.iterdir():
                if file_path.is_file():
                    video_id = file_path.stem.split('.')[0]
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    created_at = file_path.stat().st_ctime
                    
                    files.append({
                        'video_id': video_id,
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'size_mb': round(size_mb, 2),
                        'created_at': created_at
                    })
            
            logger.info(f"Listage de {len(files)} fichiers")
            return files
        except Exception as e:
            logger.error(f"Erreur lors du listage des fichiers: {e}")
            return []
    
    def delete_file(self, video_id: str) -> bool:
        """Supprimer un fichier audio"""
        try:
            files = [f for f in os.listdir(self.audio_dir) if f.startswith(video_id)]
            deleted_count = 0
            
            for filename in files:
                file_path = self.audio_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Fichier supprimé: {filename}")
            
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier {video_id}: {e}")
            return False
    
    def clear_all_files(self) -> int:
        """Supprimer tous les fichiers audio"""
        try:
            deleted_count = 0
            for file_path in self.audio_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"Suppression de {deleted_count} fichiers")
            return deleted_count
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de tous les fichiers: {e}")
            return 0
    
    def _get_bypass_configs(self) -> List[Dict]:
        """Obtenir les configurations de contournement pour streaming"""
        countries = ['US', 'GB', 'FR', 'CA', 'AU', 'DE', 'NL']
        configs = []
        
        for country in countries:
            config = {
                **Config.YT_DLP_OPTIONS,
                'geo_bypass_country': country
            }
            configs.append(config)
        
        # Configuration sans contournement en dernier recours
        configs.append({
            **Config.YT_DLP_OPTIONS,
            'geo_bypass': False
        })
        
        return configs
    
    def _get_download_configs(self, output_path: str) -> List[Dict]:
        """Obtenir les configurations de téléchargement"""
        countries = ['US', 'GB', 'FR', 'CA', 'AU']
        configs = []
        
        for country in countries:
            config = {
                **Config.YT_DLP_OPTIONS,
                'geo_bypass_country': country,
                'outtmpl': output_path
            }
            configs.append(config)
        
        return configs