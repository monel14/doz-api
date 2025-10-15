#!/usr/bin/env python3
"""
Extracteur audio avec gestion des cookies et fallbacks
"""

import yt_dlp
import logging
import os
from typing import Optional, Dict

class AudioExtractor:
    def __init__(self):
        # Configuration yt-dlp avec cookies du navigateur
        self.ydl_opts_with_cookies = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'cookiesfrombrowser': ('chrome',),  # Utilise les cookies de Chrome
        }
        
        # Configuration fallback sans cookies
        self.ydl_opts_basic = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        # Configuration avec user-agent personnalisé
        self.ydl_opts_ua = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
    
    def extract_audio_url(self, video_id: str) -> Optional[Dict]:
        """Extrait l'URL audio avec plusieurs stratégies de fallback"""
        
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Stratégies à essayer dans l'ordre
        strategies = [
            ("avec cookies Chrome", self.ydl_opts_with_cookies),
            ("avec User-Agent personnalisé", self.ydl_opts_ua),
            ("basique", self.ydl_opts_basic),
        ]
        
        for strategy_name, opts in strategies:
            try:
                logging.info(f"Tentative d'extraction {strategy_name} pour {video_id}")
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    
                    # Chercher les formats audio
                    formats = info.get('formats', [])
                    audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                    
                    if audio_formats:
                        best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                        audio_url = best_audio.get('url')
                        
                        if audio_url:
                            logging.info(f"✅ Extraction réussie {strategy_name}")
                            return {
                                'success': True,
                                'audio_url': audio_url,
                                'title': title,
                                'duration': duration,
                                'quality': best_audio.get('abr', 'unknown'),
                                'format': best_audio.get('format_note', 'audio'),
                                'strategy': strategy_name
                            }
                    
                    # Fallback: chercher n'importe quel format avec audio
                    for format_info in formats:
                        if format_info.get('acodec') != 'none':
                            audio_url = format_info.get('url')
                            if audio_url:
                                logging.info(f"✅ Extraction réussie {strategy_name} (format mixte)")
                                return {
                                    'success': True,
                                    'audio_url': audio_url,
                                    'title': title,
                                    'duration': duration,
                                    'quality': format_info.get('abr', 'unknown'),
                                    'format': 'mixed',
                                    'strategy': strategy_name
                                }
                            
            except Exception as e:
                logging.warning(f"❌ Échec {strategy_name}: {e}")
                continue
        
        # Toutes les stratégies ont échoué
        return {
            'success': False,
            'error': 'Toutes les stratégies d\'extraction ont échoué'
        }

# Instance globale
audio_extractor = AudioExtractor()

def extract_audio_url(video_id: str) -> Optional[Dict]:
    """Fonction helper pour extraire l'URL audio"""
    return audio_extractor.extract_audio_url(video_id)