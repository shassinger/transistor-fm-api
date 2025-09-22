#!/usr/bin/env python3
"""Test raw API endpoints to identify the pagination issue"""

import requests
import json

def test_raw_endpoints():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    base_url = "https://api.transistor.fm/v1"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    show_id = "31926"
    
    print("=== RAW API ENDPOINT TEST ===\n")
    
    # Test different episode endpoints
    endpoints_to_test = [
        f"shows/{show_id}/episodes",
        f"episodes?show_id={show_id}",
        f"episodes",
        f"analytics/{show_id}/episodes",
        f"analytics/{show_id}"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"Testing: {endpoint}")
        try:
            url = f"{base_url}/{endpoint}"
            response = requests.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.ok:
                data = response.json()
                if 'data' in data:
                    count = len(data['data'])
                    print(f"   ✓ Success: {count} items")
                    
                    # Show structure
                    if data['data'] and isinstance(data['data'], list):
                        first_item = data['data'][0]
                        if 'attributes' in first_item:
                            title = first_item['attributes'].get('title', 'No title')
                            print(f"     First item: {title}")
                    
                    # Check for pagination metadata
                    if 'meta' in data:
                        print(f"     Meta: {data['meta']}")
                    if 'links' in data:
                        print(f"     Links: {data['links']}")
                else:
                    print(f"   ✓ Success: {list(data.keys())}")
            else:
                print(f"   ✗ Error: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Exception: {e}")
        
        print()
    
    # Test pagination on working endpoint
    print("Testing pagination on analytics endpoint:")
    try:
        url = f"{base_url}/analytics/{show_id}/episodes"
        
        # Test with pagination params
        params_to_test = [
            {},
            {'page': 1},
            {'page': 2},
            {'per_page': 2},
            {'page': 1, 'per_page': 2}
        ]
        
        for params in params_to_test:
            response = requests.get(url, headers=headers, params=params)
            if response.ok:
                data = response.json()
                count = len(data.get('data', []))
                print(f"   Params {params}: {count} episodes")
            else:
                print(f"   Params {params}: Error {response.status_code}")
                
    except Exception as e:
        print(f"   Pagination test error: {e}")

if __name__ == "__main__":
    test_raw_endpoints()
