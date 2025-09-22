#!/usr/bin/env python3
"""Diagnostic test to check API endpoints and permissions"""

import sys
sys.path.insert(0, '/home/ec2-user/transistor-fm-api')

from transistor.client import TransistorClient

def diagnose_api():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    client = TransistorClient(api_key)
    
    print("=== API DIAGNOSTIC TEST ===\n")
    
    # Test 1: Account access
    print("1. Testing account access...")
    try:
        account = client.get_account()
        print(f"   ✓ Account ID: {account['data']['id']}")
        print(f"   ✓ Account type: {account['data']['type']}")
    except Exception as e:
        print(f"   ✗ Account error: {e}")
        return
    
    # Test 2: Shows access
    print("\n2. Testing shows access...")
    try:
        shows = client.list_shows()
        print(f"   ✓ Shows found: {len(shows['data'])}")
        
        if shows['data']:
            show = shows['data'][0]
            show_id = show['id']
            show_title = show['attributes']['title']
            print(f"   ✓ First show: {show_title} (ID: {show_id})")
            
            # Test 3: Episodes access with different methods
            print(f"\n3. Testing episodes for show {show_id}...")
            
            # Method 1: Direct episodes endpoint
            try:
                episodes = client.list_episodes(show_id)
                print(f"   ✓ list_episodes(): {len(episodes['data'])} episodes")
                if episodes['data']:
                    print(f"     First episode: {episodes['data'][0]['attributes']['title']}")
            except Exception as e:
                print(f"   ✗ list_episodes() error: {e}")
            
            # Method 2: Analytics endpoint (known to work)
            try:
                analytics = client.get_all_episodes_analytics(show_id)
                print(f"   ✓ Analytics: {len(analytics['data'])} episodes")
                if analytics['data']:
                    print(f"     First in analytics: {analytics['data'][0]['attributes']['title']}")
            except Exception as e:
                print(f"   ✗ Analytics error: {e}")
            
            # Method 3: Try different pagination parameters
            print(f"\n4. Testing pagination parameters...")
            
            test_params = [
                {'page': 1},
                {'page': 2}, 
                {'per_page': 50},
                {'page': 1, 'per_page': 50},
                {'offset': 0, 'limit': 50}
            ]
            
            for params in test_params:
                try:
                    result = client.list_episodes(show_id, **params)
                    count = len(result['data'])
                    print(f"   ✓ Params {params}: {count} episodes")
                except Exception as e:
                    print(f"   ✗ Params {params}: {e}")
        
    except Exception as e:
        print(f"   ✗ Shows error: {e}")

if __name__ == "__main__":
    diagnose_api()
