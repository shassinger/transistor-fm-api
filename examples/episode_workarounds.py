#!/usr/bin/env python3
"""
Episode pagination workaround examples for Transistor API client
"""

import os
from transistor import TransistorClient, TransistorAPIError

def main():
    # Initialize client
    api_key = os.getenv('TRANSISTOR_API_KEY')
    if not api_key:
        print("Set TRANSISTOR_API_KEY environment variable")
        return
    
    client = TransistorClient(api_key)
    
    try:
        # Get shows first
        shows = client.list_shows()
        if not shows['data']:
            print("No shows found")
            return
        
        show_id = shows['data'][0]['id']
        show_title = shows['data'][0]['attributes']['title']
        print(f"Working with show: {show_title}")
        
        # Example 1: Demonstrate the limitation
        print("\n=== Episode Limitation Demo ===")
        episodes = client.list_episodes(show_id)
        print(f"list_episodes() returns: {len(episodes['data'])} episodes")
        print(f"Total episodes in podcast: {episodes['meta']['totalCount']}")
        print(f"Missing episodes: {episodes['meta']['totalCount'] - len(episodes['data'])}")
        
        # Example 2: Get all episode IDs
        print("\n=== Get All Episode IDs ===")
        all_ids = client.get_all_episode_ids(show_id)
        print(f"All episode IDs found: {len(all_ids)}")
        print(f"Sample IDs: {all_ids[:3]}")
        
        # Example 3: Process episodes efficiently
        print("\n=== Process Episodes Efficiently ===")
        for i, episode_id in enumerate(all_ids[:5]):  # First 5 only for demo
            episode = client.get_episode(episode_id)
            title = episode['data']['attributes']['title']
            print(f"{i+1}. {title}")
        
        # Example 4: Get complete data for all episodes
        print(f"\n=== Get Complete Data (Demo: first 3 episodes) ===")
        # Note: Using slice for demo to avoid long execution
        demo_ids = all_ids[:3]
        
        complete_episodes = []
        for episode_id in demo_ids:
            episode = client.get_episode(episode_id)
            complete_episodes.append(episode['data'])
        
        print(f"Retrieved complete data for {len(complete_episodes)} episodes")
        for episode in complete_episodes:
            title = episode['attributes']['title']
            status = episode['attributes']['status']
            print(f"- {title} (Status: {status})")
        
        # Example 5: Using the full data method (commented for demo)
        print(f"\n=== Full Data Method (commented for demo) ===")
        print("# Uncomment to get ALL episodes with full data:")
        print("# all_episodes = client.get_all_episodes_full_data(show_id)")
        print("# print(f'Total episodes: {len(all_episodes[\"data\"])}')")
        
    except TransistorAPIError as e:
        print(f"API Error: {e}")

if __name__ == '__main__':
    main()
