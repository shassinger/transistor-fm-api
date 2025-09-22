#!/usr/bin/env python3
"""Live test of pagination issues with actual API key"""

import sys
sys.path.insert(0, '/home/ec2-user/transistor-fm-api')

from transistor.client import TransistorClient
from transistor.client_fixed import TransistorClientFixed

def test_with_real_api():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    
    print("=== LIVE PAGINATION TEST ===\n")
    
    # Test original client
    print("1. ORIGINAL CLIENT TEST:")
    try:
        client = TransistorClient(api_key)
        
        # Get shows first
        shows = client.list_shows()
        if not shows['data']:
            print("   No shows found")
            return
        
        show_id = shows['data'][0]['id']
        show_title = shows['data'][0]['attributes']['title']
        print(f"   Testing show: {show_title} (ID: {show_id})")
        
        # Test original list_episodes
        episodes = client.list_episodes(show_id)
        episode_count = len(episodes['data'])
        print(f"   Original list_episodes(): {episode_count} episodes")
        
        # Test analytics for comparison
        analytics = client.get_all_episodes_analytics(show_id)
        analytics_count = len(analytics['data'])
        print(f"   Analytics shows: {analytics_count} episodes")
        print(f"   MISSING: {analytics_count - episode_count} episodes\n")
        
    except Exception as e:
        print(f"   ERROR: {e}\n")
    
    # Test fixed client
    print("2. FIXED CLIENT TEST:")
    try:
        fixed_client = TransistorClientFixed(api_key)
        
        # Test get_all_episodes
        all_episodes = fixed_client.get_all_episodes(show_id)
        all_count = len(all_episodes['data'])
        print(f"   Fixed get_all_episodes(): {all_count} episodes")
        
        # Test pagination
        page1 = fixed_client.list_episodes(show_id, page=1, per_page=20)
        page2 = fixed_client.list_episodes(show_id, page=2, per_page=20)
        page3 = fixed_client.list_episodes(show_id, page=3, per_page=20)
        
        print(f"   Page 1: {len(page1['data'])} episodes")
        print(f"   Page 2: {len(page2['data'])} episodes") 
        print(f"   Page 3: {len(page3['data'])} episodes")
        
        total_paginated = len(page1['data']) + len(page2['data']) + len(page3['data'])
        print(f"   Total via pagination: {total_paginated} episodes")
        
        # Show episode titles from different pages
        if page1['data']:
            print(f"   First episode: {page1['data'][0]['attributes']['title']}")
        if page2['data']:
            print(f"   Page 2 first: {page2['data'][0]['attributes']['title']}")
            
    except Exception as e:
        print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_with_real_api()
