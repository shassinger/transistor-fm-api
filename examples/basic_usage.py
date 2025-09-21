#!/usr/bin/env python3
"""
Basic usage examples for Transistor API client
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
        # Get account info
        print("=== Account Info ===")
        account = client.get_account()
        print(f"Account: {account}")
        
        # List shows
        print("\n=== Shows ===")
        shows = client.list_shows()
        print(f"Shows: {shows}")
        
        # List episodes
        print("\n=== Episodes ===")
        episodes = client.list_episodes()
        print(f"Episodes: {episodes}")
        
        # Example: Create a show
        print("\n=== Creating Show ===")
        show_data = {
            "data": {
                "type": "show",
                "attributes": {
                    "title": "My Test Podcast",
                    "description": "A test podcast created via API"
                }
            }
        }
        # Uncomment to create:
        # new_show = client.create_show(show_data)
        # print(f"Created show: {new_show}")
        
    except TransistorAPIError as e:
        print(f"API Error: {e}")

if __name__ == '__main__':
    main()
