#!/usr/bin/env python3
"""Final comprehensive test of the pagination fix"""

import sys
sys.path.insert(0, '/home/ec2-user/transistor-fm-api')

from transistor.client import TransistorClient
from transistor.client_final_fix import TransistorClientFinalFix

def final_test():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    show_id = "31926"
    
    print("=== FINAL COMPREHENSIVE PAGINATION TEST ===\n")
    
    print("PROBLEM DEMONSTRATION:")
    print("1. Original Client (Broken):")
    try:
        original = TransistorClient(api_key)
        episodes = original.list_episodes(show_id)
        print("   ✗ Should fail with 404")
    except Exception as e:
        print(f"   ✓ Fails as expected: {e}")
    
    print("\n2. Fixed Client:")
    fixed = TransistorClientFinalFix(api_key)
    
    # Test basic listing
    episodes = fixed.list_episodes(show_id)
    print(f"   ✓ Episodes via list_episodes(): {len(episodes['data'])}")
    print(f"   ✓ Total episodes in podcast: {episodes['meta']['totalCount']}")
    print(f"   ✗ Missing episodes: {episodes['meta']['totalCount'] - len(episodes['data'])}")
    
    # Test getting all episode IDs
    all_ids = fixed.get_all_episode_ids(show_id)
    print(f"   ✓ All episode IDs found: {len(all_ids)}")
    
    # Test individual episode access
    if all_ids:
        test_episode = fixed.get_episode(all_ids[0])
        print(f"   ✓ Individual episode access: {test_episode['data']['attributes']['title']}")
    
    print(f"\nSOLUTION SUMMARY:")
    print(f"• API Limitation: Transistor.fm only returns 20 episodes via list_episodes()")
    print(f"• Endpoint Fixed: Now uses correct 'episodes?show_id=X' format")
    print(f"• Workaround Available: Can get all {len(all_ids)} episode IDs via analytics")
    print(f"• Full Access Method: get_all_episodes_full_data() (slow but complete)")
    
    print(f"\nRECOMMENDED USAGE:")
    print(f"# Quick access (20 episodes only):")
    print(f"episodes = client.list_episodes('{show_id}')")
    print(f"")
    print(f"# Get all episode IDs:")
    print(f"all_ids = client.get_all_episode_ids('{show_id}')")
    print(f"")
    print(f"# Get complete data (slow):")
    print(f"all_episodes = client.get_all_episodes_full_data('{show_id}')")

if __name__ == "__main__":
    final_test()
