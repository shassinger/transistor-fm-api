#!/usr/bin/env python3
"""Add automatic rate limiting to the Transistor client"""

def add_rate_limiting():
    with open('/home/ec2-user/transistor-fm-api/transistor/client.py', 'r') as f:
        content = f.read()
    
    # Add imports
    old_imports = 'import requests\nfrom typing import Dict, List, Optional, Any'
    new_imports = 'import requests\nimport time\nfrom collections import deque\nfrom typing import Dict, List, Optional, Any'
    content = content.replace(old_imports, new_imports)
    
    # Add rate limiting to __init__
    old_init = '''    def __init__(self, api_key: str):
        """Initialize the client with API key"""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })'''
    
    new_init = '''    def __init__(self, api_key: str, auto_rate_limit: bool = True):
        """Initialize the client with API key and optional rate limiting"""
        self.api_key = api_key
        self.auto_rate_limit = auto_rate_limit
        self.request_times = deque(maxlen=10)  # Track last 10 requests
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })'''
    
    content = content.replace(old_init, new_init)
    
    # Replace _request method with rate limiting
    old_request_start = '''    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make authenticated API request with comprehensive error handling
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Dict containing the JSON response
            
        Raises:
            RateLimitError: When rate limit (10 req/10s) is exceeded
            AuthenticationError: When API key is invalid
            NotFoundError: When resource is not found
            ValidationError: When request validation fails
            TransistorAPIError: For other API errors
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:'''
    
    new_request_start = '''    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make authenticated API request with automatic rate limiting
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Dict containing the JSON response
            
        Note:
            Automatically handles rate limiting (10 req/10s) when auto_rate_limit=True
        """
        # Automatic rate limiting
        if self.auto_rate_limit:
            self._enforce_rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:'''
    
    content = content.replace(old_request_start, new_request_start)
    
    # Add rate limiting method before _request
    rate_limit_method = '''    def _enforce_rate_limit(self):
        """Enforce 10 requests per 10 seconds rate limit"""
        now = time.time()
        
        # Remove requests older than 10 seconds
        while self.request_times and now - self.request_times[0] > 10:
            self.request_times.popleft()
        
        # If we have 10 requests in the last 10 seconds, wait
        if len(self.request_times) >= 10:
            sleep_time = 10 - (now - self.request_times[0]) + 0.1  # Small buffer
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Record this request
        self.request_times.append(now)

'''
    
    # Insert before _request method
    content = content.replace('    def _request(', rate_limit_method + '    def _request(')
    
    with open('/home/ec2-user/transistor-fm-api/transistor/client.py', 'w') as f:
        f.write(content)
    
    print("✅ Added automatic rate limiting to client")
    print("✅ Rate limiting: 10 requests per 10 seconds")
    print("✅ Optional disable with auto_rate_limit=False")

if __name__ == "__main__":
    add_rate_limiting()
