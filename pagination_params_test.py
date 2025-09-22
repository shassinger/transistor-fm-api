#!/usr/bin/env python3
"""Test pagination parameters systematically"""

import requests
import json

def test_pagination_params():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    base_url = "https://api.transistor.fm/v1"
    show_id = "31926"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("=== PAGINATION PARAMETERS TEST ===\n")
    
    # First, get the working baseline
    print("1. Baseline (no params):")
    url = f"{base_url}/episodes"
    response = requests.get(url, headers=headers, params={'show_id': show_id})
    
    if response.ok:
        data = response.json()
        print(f"   ✓ Episodes: {len(data['data'])}")
        print(f"   ✓ Meta: {data['meta']}")
        baseline_meta = data['meta']
    else:
        print(f"   ✗ Error: {response.status_code} - {response.text}")
        return
    
    # Test different pagination parameter formats
    print(f"\n2. Testing pagination formats:")
    
    param_tests = [
        # Standard pagination
        {'show_id': show_id, 'page': 2},
        {'show_id': show_id, 'page[number]': 2},
        {'show_id': show_id, 'page[offset]': 20},
        
        # Per-page controls
        {'show_id': show_id, 'per_page': 10},
        {'show_id': show_id, 'page[size]': 10},
        {'show_id': show_id, 'limit': 10},
        
        # Combined
        {'show_id': show_id, 'page': 2, 'per_page': 10},
        {'show_id': show_id, 'page[number]': 2, 'page[size]': 10},
    ]
    
    for params in param_tests:
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.ok:
                data = response.json()
                count = len(data['data'])
                meta = data.get('meta', {})
                print(f"   ✓ {params}: {count} episodes, meta: {meta}")
                
                # Show first episode title to verify different data
                if data['data']:
                    title = data['data'][0]['attributes']['title']
                    print(f"     First: {title[:50]}...")
                    
            else:
                error_data = response.text
                print(f"   ✗ {params}: {response.status_code} - {error_data}")
                
        except Exception as e:
            print(f"   ✗ {params}: Exception - {e}")
    
    # Test if we can get all episodes by iterating
    print(f"\n3. Attempting to get all {baseline_meta.get('totalCount', 'unknown')} episodes:")
    
    if 'totalPages' in baseline_meta:
        total_pages = baseline_meta['totalPages']
        all_episodes = []
        
        for page_num in range(1, total_pages + 1):
            params = {'show_id': show_id, 'page': page_num}
            response = requests.get(url, headers=headers, params=params)
            
            if response.ok:
                data = response.json()
                episodes = data['data']
                print(f"   Page {page_num}: {len(episodes)} episodes")
                all_episodes.extend(episodes)
            else:
                print(f"   Page {page_num}: Error {response.status_code}")
        
        print(f"\n   TOTAL COLLECTED: {len(all_episodes)} episodes")
        print(f"   EXPECTED: {baseline_meta.get('totalCount')} episodes")

if __name__ == "__main__":
    test_pagination_params()
