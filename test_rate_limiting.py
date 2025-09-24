#!/usr/bin/env python3
"""Test automatic rate limiting"""

import sys
import time
sys.path.insert(0, '/home/ec2-user/transistor-fm-api')

from transistor.client import TransistorClient

def test_rate_limiting():
    api_key = "YYhADUpAtKgHp9bdFa_tjA"
    
    print("=== RATE LIMITING TEST ===\n")
    
    # Test with rate limiting enabled (default)
    print("1. Testing with auto_rate_limit=True (default):")
    client = TransistorClient(api_key)
    
    start_time = time.time()
    
    # Make 12 requests (should trigger rate limiting after 10)
    for i in range(12):
        try:
            account = client.get_account()
            elapsed = time.time() - start_time
            print(f"   Request {i+1}: Success ({elapsed:.1f}s elapsed)")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
    
    total_time = time.time() - start_time
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Expected: ~10s (rate limiting should kick in)")
    
    # Test with rate limiting disabled
    print(f"\n2. Testing with auto_rate_limit=False:")
    client_no_limit = TransistorClient(api_key, auto_rate_limit=False)
    
    start_time = time.time()
    
    # Make 3 quick requests
    for i in range(3):
        try:
            account = client_no_limit.get_account()
            elapsed = time.time() - start_time
            print(f"   Request {i+1}: Success ({elapsed:.1f}s elapsed)")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
    
    total_time = time.time() - start_time
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Expected: <1s (no rate limiting)")

if __name__ == "__main__":
    test_rate_limiting()
