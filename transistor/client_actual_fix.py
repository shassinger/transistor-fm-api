"""
Transistor.fm API Client - ACTUAL FIX for endpoint issue

This fixes the real problem: wrong endpoint format causing 404 errors.
"""

import requests
from typing import Dict, List, Optional, Any
from .exceptions import TransistorAPIError, RateLimitError, AuthenticationError, NotFoundError, ValidationError


class TransistorClientActualFix:
    """
    Fixed Transistor.fm API client that uses correct endpoints
    """
    
    BASE_URL = "https://api.transistor.fm/v1"
    
    def __init__(self, api_key: str):
        """Initialize the client with API key"""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request with comprehensive error handling"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Wait 10 seconds.", 429, response)
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key", 401, response)
            elif response.status_code == 404:
                raise NotFoundError("Resource not found", 404, response)
            elif response.status_code == 422:
                raise ValidationError("Validation error", 422, response)
            elif not response.ok:
                raise TransistorAPIError(f"API error: {response.text}", response.status_code, response)
            
            return response.json() if response.content else {}
            
        except requests.RequestException as e:
            raise TransistorAPIError(f"Request failed: {str(e)}")
    
    def list_episodes(self, show_id: str = None, **params) -> Dict[str, Any]:
        """
        List episodes - FIXED to use correct endpoint
        
        Args:
            show_id: Optional show ID to filter episodes
            **params: Optional query parameters (NOTE: pagination not supported by API)
            
        Returns:
            Dict containing episodes array (LIMITED TO FIRST 20 EPISODES ONLY)
            
        WARNING:
            The Transistor.fm API only returns the first 20 episodes and does not
            support pagination parameters. The API shows totalCount and totalPages
            in metadata but provides no way to access additional pages.
            
            For your 65-episode podcast, this method will only return 20 episodes.
            Use get_all_episode_ids() and individual get_episode() calls as workaround.
        """
        # FIXED: Use correct endpoint format
        if show_id:
            params = params.copy() if params else {}
            params['show_id'] = show_id
        
        return self._request("GET", "episodes", params=params)
    
    def get_all_episode_ids(self, show_id: str) -> List[str]:
        """
        Get all episode IDs using analytics endpoint workaround
        
        Args:
            show_id: The show ID
            
        Returns:
            List of all episode IDs for the show
            
        Note:
            This uses the analytics endpoint which returns all episodes,
            but only provides limited data per episode.
        """
        analytics = self.get_all_episodes_analytics(show_id)
        return [ep['id'] for ep in analytics['data']]
    
    def get_all_episodes_full_data(self, show_id: str) -> Dict[str, Any]:
        """
        Get complete data for ALL episodes (SLOW - makes multiple API calls)
        
        Args:
            show_id: The show ID
            
        Returns:
            Dict containing all episodes with full data
            
        WARNING:
            This makes one API call per episode. For 65 episodes, this will
            make 65+ API calls and may hit rate limits (10 req/10s).
            Use with caution and implement delays if needed.
        """
        episode_ids = self.get_all_episode_ids(show_id)
        episodes = []
        failed_episodes = []
        
        for i, episode_id in enumerate(episode_ids):
            try:
                episode = self.get_episode(episode_id)
                episodes.append(episode['data'])
                
                # Rate limiting: pause every 9 requests
                if (i + 1) % 9 == 0:
                    import time
                    time.sleep(1)  # Brief pause to avoid rate limits
                    
            except Exception as e:
                failed_episodes.append({'id': episode_id, 'error': str(e)})
        
        return {
            'data': episodes,
            'meta': {
                'total_requested': len(episode_ids),
                'successful': len(episodes),
                'failed': len(failed_episodes),
                'failed_episodes': failed_episodes
            }
        }
    
    # Include essential methods from original client
    def get_account(self) -> Dict[str, Any]:
        """Get authenticated user account details"""
        return self._request("GET", "")
    
    def list_shows(self, **params) -> Dict[str, Any]:
        """List all shows accessible to the authenticated user"""
        return self._request("GET", "shows", params=params)
    
    def get_show(self, show_id: str, **params) -> Dict[str, Any]:
        """Get details for a specific show"""
        return self._request("GET", f"shows/{show_id}", params=params)
    
    def get_episode(self, episode_id: str, **params) -> Dict[str, Any]:
        """Get details for a specific episode"""
        return self._request("GET", f"episodes/{episode_id}", params=params)
    
    def get_all_episodes_analytics(self, show_id: str, **params) -> Dict[str, Any]:
        """Get analytics for ALL episodes of a show in one request"""
        return self._request("GET", f"analytics/{show_id}/episodes", params=params)
