#!/usr/bin/env python3
"""
Test détaillé de l'API Railway avec plusieurs vidéos
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

# Différentes vidéos à tester
TEST_VIDEOS = [
    {"id": "6PS8zLqvQtU", "name": "Jeady Jay - Dis-moi que tu m'aimes"},
    {"id": "dQw4w9WgXcQ", "name": "Rick Astley - Never Gonna Give You Up"},
    {"id": "9bZkp7q19f0", "name": "PSY - Gangnam Style"},
    {"id": "kJQP7kiw5Fk", "name": "Luis Fonsi - Despacito"}
]

def test_streaming(video_id, video_name):
    """Test détaillé du streaming pour une vidéo"""
    print(f"\n🎵 Test streaming: {video_name}")
    print(f"📹 Video ID: {video_id}")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/stream/{video_id}", timeout=60)
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
            
            # Vérifier que l'URL audio est valide
            audio_url = result.get('audio_url', '')
            if audio_url:
                print(f"  🔗 URL audio: {audio_url[:80]}...")
                
                # Test rapide de l'URL (juste les headers)
                try:
                    head_response = requests.head(audio_url, timeout=10)
                    print(f"  ✅ URL accessible: {head_response.status_code}")
                    if 'content-length' in head_response.headers:
                        size_mb = int(head_response.headers['content-length']) / (1024*1024)
                        print(f"  📊 Taille: {size_mb:.1f} MB")
                except:
                    print("  ⚠️  URL non testable (normal pour certains formats)")
            
            return True
            
        else:
            print("❌ ÉCHEC")
            try:
                error = response.json()
                print(f"  Erreur: {error.get('detail', 'Erreur inconnue')}")
            except:
                print(f"  Erreur brute: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT (>60s)")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def test_search_and_info():
    """Test de recherche et d'infos"""
    print("\n🔍 Test recherche et infos")
    print("-" * 40)
    
    # Test recherche
    search_data = {"query": "never gonna give you up", "limit": 3}
    response = requests.post(f"{BASE_URL}/search", json=search_data)
    
    if response.status_code == 200:
        results = response.json().get('results', [])
        print(f"✅ Recherche: {len(results)} résultats")
        if results:
            first = results[0]
            print(f"  Premier: {first.get('title', 'N/A')}")
            video_id = first.get('videoId')
            
            if video_id:
                # Test info chanson
                info_response = requests.get(f"{BASE_URL}/song/{video_id}")
                if info_response.status_code == 200:
                    print("✅ Infos chanson récupérées")
                else:
                    print("❌ Échec infos chanson")
    else:
        print("❌ Échec recherche")

def main():
    print("🚀 TEST DÉTAILLÉ API RAILWAY")
    print("=" * 60)
    print(f"🌐 URL: {BASE_URL}")
    
    # Test de base
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ API accessible")
        else:
            print("❌ API non accessible")
            return
    except:
        print("❌ API non accessible")
        return
    
    # Test recherche et infos
    test_search_and_info()
    
    # Test streaming avec plusieurs vidéos
    success_count = 0
    for video in TEST_VIDEOS:
        success = test_streaming(video["id"], video["name"])
        if success:
            success_count += 1
        time.sleep(2)  # Pause entre les tests
    
    # Résumé
    print(f"\n📊 RÉSUMÉ")
    print("=" * 40)
    print(f"✅ Streaming réussi: {success_count}/{len(TEST_VIDEOS)}")
    print(f"📈 Taux de succès: {(success_count/len(TEST_VIDEOS)*100):.1f}%")
    
    # Test cache final
    cache_response = requests.get(f"{BASE_URL}/cache/stats")
    if cache_response.status_code == 200:
        cache_data = cache_response.json()
        print(f"💾 Entrées en cache: {cache_data.get('total_entries', 0)}")

if __name__ == "__main__":
    main()