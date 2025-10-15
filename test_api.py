#!/usr/bin/env python3
"""
Script de test pour l'API Music Streaming
"""
import requests
import json
import time

# Configuration
BASE_URL = "https://doz-api-production.up.railway.app"
VIDEO_ID = "6PS8zLqvQtU"  # Jeady Jay & Emma'a - Dis-moi que tu m'aimes

def test_endpoint(endpoint, method="GET", data=None):
    """Teste un endpoint et affiche le résultat"""
    print(f"\n🔍 Test: {method} {endpoint}")
    print("-" * 50)
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            
            # Affichage adapté selon l'endpoint
            if "search" in endpoint:
                print(f"Résultats trouvés: {len(result.get('results', []))}")
                if result.get('results'):
                    first = result['results'][0]
                    print(f"Premier résultat: {first.get('title', 'N/A')}")
            
            elif "stream" in endpoint:
                print(f"Titre: {result.get('title', 'N/A')}")
                print(f"Durée: {result.get('duration', 'N/A')}s")
                print(f"Qualité: {result.get('quality', 'N/A')}")
                print(f"Stratégie: {result.get('strategy', 'N/A')}")
                print(f"En cache: {result.get('cached', False)}")
                print(f"URL audio: {result.get('audio_url', 'N/A')[:100]}...")
            
            elif "cache" in endpoint:
                print(f"Entrées en cache: {result.get('total_entries', 0)}")
            
            else:
                # Affichage générique
                if isinstance(result, dict) and len(str(result)) < 200:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print("Réponse reçue (trop longue pour affichage)")
        
        else:
            print(f"❌ Erreur: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Serveur non accessible. Lancez d'abord 'python streaming_main.py'")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    print("🎵 Test de l'API Music Streaming")
    print("=" * 50)
    
    # Test des endpoints principaux
    test_endpoint("/")
    test_endpoint("/cache/stats")
    test_endpoint(f"/stream/{VIDEO_ID}")
    test_endpoint("/search", "POST", {"query": "Jeady Jay Emma", "limit": 5})
    test_endpoint(f"/song/{VIDEO_ID}")
    test_endpoint("/cache/stats")  # Vérifier que le cache a été mis à jour
    
    print("\n🎯 Tests terminés!")
    print("Pour lancer le serveur: python streaming_main.py")

if __name__ == "__main__":
    main()