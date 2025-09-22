#!/usr/bin/env python3
"""
Transistor.fm API Pagination Diagnosis Script

This script diagnoses pagination issues with the Transistor.fm API client
by testing various pagination scenarios and documenting the problems.
"""

import os
import json
from transistor import TransistorClient, TransistorAPIError

def test_pagination_issues():
    """Test and document pagination issues"""
    
    # Get API key from environment
    api_key = os.getenv('TRANSISTOR_API_KEY')
    if not api_key:
        print("ERROR: TRANSISTOR_API_KEY environment variable not set")
        return
    
    client = TransistorClient(api_key)
    
    print("=== TRANSISTOR.FM API PAGINATION DIAGNOSIS ===\n")
    
    try:
        # Get account and shows first
        print("1. Getting account information...")
        account = client.get_account()
        print(f"   Account ID: {account['data']['id']}")
        
        print("\n2. Getting shows...")
        shows = client.list_shows()
        if not shows['data']:
            print("   ERROR: No shows found")
            return
        
        show_id = shows['data'][0]['id']
        show_title = shows['data'][0]['attributes']['title']
        print(f"   Using show: {show_title} (ID: {show_id})")
        
        # Test 1: Default list_episodes (should show pagination issue)
        print(f"\n3. ISSUE TEST: Default list_episodes() for show {show_id}")
        episodes_default = client.list_episodes(show_id)
        episode_count = len(episodes_default['data'])
        print(f"   Episodes returned: {episode_count}")
        print(f"   Response keys: {list(episodes_default.keys())}")
        
        # Check for pagination metadata
        if 'meta' in episodes_default:
            print(f"   Meta data: {episodes_default['meta']}")
        if 'links' in episodes_default:
            print(f"   Links data: {episodes_default['links']}")
        
        # Test 2: Try with explicit pagination parameters
        print(f"\n4. ISSUE TEST: list_episodes() with pagination params")
        try:
            # Test common pagination parameter names
            pagination_tests = [
                {'page': 1, 'per_page': 50},
                {'page[number]': 1, 'page[size]': 50},
                {'offset': 0, 'limit': 50},
                {'page': 2},  # Try to get second page
            ]
            
            for i, params in enumerate(pagination_tests, 1):
                print(f"   Test {i}: params = {params}")
                try:
                    result = client.list_episodes(show_id, **params)
                    count = len(result['data'])
                    print(f"     Result: {count} episodes")
                    if 'meta' in result:
                        print(f"     Meta: {result['meta']}")
                except Exception as e:
                    print(f"     ERROR: {e}")
        
        except Exception as e:
            print(f"   ERROR in pagination tests: {e}")
        
        # Test 3: Compare with get_all_episodes_analytics
        print(f"\n5. COMPARISON: get_all_episodes_analytics() vs list_episodes()")
        try:
            all_episodes_analytics = client.get_all_episodes_analytics(show_id)
            if 'data' in all_episodes_analytics:
                analytics_count = len(all_episodes_analytics['data'])
                print(f"   get_all_episodes_analytics(): {analytics_count} episodes")
                print(f"   list_episodes(): {episode_count} episodes")
                print(f"   DISCREPANCY: {analytics_count - episode_count} episodes missing from list_episodes()")
                
                # Show some episode IDs from analytics that might be missing
                if analytics_count > episode_count:
                    analytics_ids = {ep['id'] for ep in all_episodes_analytics['data']}
                    list_ids = {ep['id'] for ep in episodes_default['data']}
                    missing_ids = analytics_ids - list_ids
                    print(f"   Missing episode IDs (sample): {list(missing_ids)[:5]}")
            else:
                print(f"   get_all_episodes_analytics() structure: {list(all_episodes_analytics.keys())}")
        
        except Exception as e:
            print(f"   ERROR in analytics comparison: {e}")
        
        # Test 4: Try to access specific episodes that might be missing
        print(f"\n6. ISSUE TEST: Accessing potentially missing episodes")
        try:
            # Get all episode IDs from analytics
            all_episodes_analytics = client.get_all_episodes_analytics(show_id)
            if 'data' in all_episodes_analytics:
                all_episode_ids = [ep['id'] for ep in all_episodes_analytics['data']]
                listed_episode_ids = [ep['id'] for ep in episodes_default['data']]
                
                # Try to access an episode that's not in the list_episodes result
                missing_ids = [eid for eid in all_episode_ids if eid not in listed_episode_ids]
                if missing_ids:
                    test_id = missing_ids[0]
                    print(f"   Testing access to missing episode ID: {test_id}")
                    episode_detail = client.get_episode(test_id)
                    print(f"   SUCCESS: Can access episode '{episode_detail['data']['attributes']['title']}'")
                    print(f"   This confirms the episode exists but is not returned by list_episodes()")
                else:
                    print("   No missing episodes found to test")
        
        except Exception as e:
            print(f"   ERROR testing missing episodes: {e}")
        
        # Test 5: Raw API call to understand the actual API response
        print(f"\n7. RAW API ANALYSIS: Direct API call")
        try:
            import requests
            url = f"https://api.transistor.fm/v1/shows/{show_id}/episodes"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Test without pagination
            response = requests.get(url, headers=headers)
            if response.ok:
                data = response.json()
                print(f"   Raw API episodes count: {len(data.get('data', []))}")
                print(f"   Response structure: {list(data.keys())}")
                if 'meta' in data:
                    print(f"   Meta information: {data['meta']}")
                if 'links' in data:
                    print(f"   Links information: {data['links']}")
            
            # Test with page parameter
            response2 = requests.get(url, headers=headers, params={'page': 2})
            if response2.ok:
                data2 = response2.json()
                print(f"   Raw API page 2 episodes: {len(data2.get('data', []))}")
        
        except Exception as e:
            print(f"   ERROR in raw API test: {e}")
    
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    test_pagination_issues()
