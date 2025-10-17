#!/usr/bin/env python3
"""
Test rapide de l'API améliorée en local
"""
import requests
import json
import time
import threading
import subprocess
import sys
import os

def start_server():
    """Lance le serveur en arrière-plan"""
    try:
        # Lancer le serveur
        process = subprocess.Popen([
            sys.executable, "streaming_improved.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(3)
        return process
    except Exception as e:
        print(f"Erreur démarrage serveur: {e}")
        return None

def test_api():
    """Test de l'API"""
    BASE_URL = "http://localhost:8001"
    
    print("🎵 Test API Améliorée en Local")
    print("=" * 40)
    
    # Test de base
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API accessible: {result.get('message', 'N/A')}")
            print(f"📦 Version: {result.get('version', 'N/A')}")
        else:
            print("❌ API non accessible")
            return
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return
    
    # Test streaming avec la vidéo problématique
    video_id = "6PS8zLqvQtU"  # Jeady Jay - Dis-moi que tu m'aimes
    print(f"\n🎧 Test streaming: {video_id}")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/stream/{video_id}", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS!")
            print(f"  📝 Titre: {result.get('title', 'N/A')}")
            print(f"  ⏱️  Durée: {result.get('duration', 'N/A')}s")
            print(f"  🎧 Qualité: {result.get('quality', 'N/A')}")
            print(f"  📦 Format: {result.get('format', 'N/A')}")
            print(f"  🔄 Stratégie: {result.get('strategy', 'N/A')}")
            print(f"  💾 En cache: {result.get('cached', False)}")
            print(f"  📝 Note: {result.get('note', 'N/A')}")
            
            audio_url = result.get('audio_url', '')
            if audio_url:
                print(f"  🔗 URL: {audio_url[:60]}...")
                
                # Test si c'est une vraie URL audio ou YouTube direct
                if 'youtube.com' in audio_url:
                    print("  ⚠️  Fallback YouTube direct")
                else:
                    print("  ✅ URL audio extraite")
        else:
            print("❌ ÉCHEC")
            try:
                error = response.json()
                print(f"  Erreur: {error.get('detail', 'Erreur inconnue')}")
            except:
                print(f"  Erreur brute: {response.text[:100]}")
                
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT (>30s)")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    # Test cache
    try:
        cache_response = requests.get(f"{BASE_URL}/cache/stats", timeout=5)
        if cache_response.status_code == 200:
            cache_data = cache_response.json()
            print(f"\n💾 Cache: {cache_data.get('total_entries', 0)} entrées")
    except:
        pass

def main():
    print("🚀 Lancement du test local")
    
    # Vérifier si le serveur tourne déjà
    try:
        response = requests.get("http://localhost:8001", timeout=2)
        print("✅ Serveur déjà en cours")
        test_api()
    except:
        print("🔄 Démarrage du serveur...")
        server_process = start_server()
        
        if server_process:
            try:
                test_api()
            finally:
                print("\n🛑 Arrêt du serveur...")
                server_process.terminate()
                server_process.wait()
        else:
            print("❌ Impossible de démarrer le serveur")

if __name__ == "__main__":
    main()