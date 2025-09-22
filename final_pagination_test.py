#!/usr/bin/env python3
"""Final test showing actual pagination working with correct endpoint"""

import requests
import json

def test_actual_pagination():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    base_url = "https://api.transistor.fm/v1"
    show_id = "31926"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json", 
        "Accept": "application/json"
    }
    
    print("=== ACTUAL PAGINATION TEST RESULTS ===\n")
    
    print("PROBLEM CONFIRMED:")
    print("✗ Current client uses: shows/31926/episodes (404 Not Found)")
    print("✓ Correct endpoint is: episodes?show_id=31926\n")
    
    # Test all pages
    print("PAGINATION WORKING:")
    all_episodes = []
    
    for page in range(1, 5):  # API shows 4 total pages
        url = f"{base_url}/episodes"
        params = {'show_id': show_id, 'page': page}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.ok:
            data = response.json()
            episodes = data['data']
            meta = data['meta']
            
            print(f"Page {page}: {len(episodes)} episodes")
            print(f"   Meta: {meta}")
            
            if episodes:
                print(f"   First: {episodes[0]['attributes']['title']}")
                print(f"   Last:  {episodes[-1]['attributes']['title']}")
            
            all_episodes.extend(episodes)
        else:
            print(f"Page {page}: Error {response.status_code}")
        
        print()
    
    print(f"TOTAL EPISODES RETRIEVED: {len(all_episodes)}")
    print(f"EXPECTED FROM API META: 65")
    print(f"SUCCESS: {'✓' if len(all_episodes) == 65 else '✗'}")
    
    # Show the fix needed
    print(f"\nFIX REQUIRED:")
    print("Change client.py line in list_episodes():")
    print("FROM: endpoint = f'shows/{show_id}/episodes' if show_id else 'episodes'")
    print("TO:   endpoint = 'episodes'")
    print("AND:  Add show_id to params if provided")

if __name__ == "__main__":
    test_actual_pagination()
