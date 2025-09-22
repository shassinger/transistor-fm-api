#!/usr/bin/env python3
"""Debug analytics endpoint structure"""

import sys
sys.path.insert(0, '/home/ec2-user/transistor-fm-api')

from transistor.client import TransistorClient
import json

def debug_analytics():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    show_id = "31926"
    
    client = TransistorClient(api_key)
    
    print("=== ANALYTICS STRUCTURE DEBUG ===\n")
    
    try:
        analytics = client.get_all_episodes_analytics(show_id)
        print("Analytics response structure:")
        print(json.dumps(analytics, indent=2)[:1000] + "...")
        
        print(f"\nTop-level keys: {list(analytics.keys())}")
        
        if 'data' in analytics:
            print(f"Data type: {type(analytics['data'])}")
            print(f"Data length: {len(analytics['data'])}")
            
            if analytics['data'] and isinstance(analytics['data'], list):
                first_item = analytics['data'][0]
                print(f"First item keys: {list(first_item.keys())}")
                print(f"First item: {json.dumps(first_item, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_analytics()
