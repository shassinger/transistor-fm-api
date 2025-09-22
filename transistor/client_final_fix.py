"""
Transistor.fm API Client - FINAL FIX with correct analytics parsing
"""

import requests
from typing import Dict, List, Optional, Any
from .exceptions import TransistorAPIError, RateLimitError, AuthenticationError, NotFoundError, ValidationError


class TransistorClientFinalFix:
    """
    Final fixed Transistor.fm API client with correct endpoint and analytics parsing
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
        
        WARNING: Only returns first 20 episodes due to API limitation
        """
        if show_id:
            params = params.copy() if params else {}
            params['show_id'] = show_id
        
        return self._request("GET", "episodes", params=params)
    
    def get_all_episode_ids(self, show_id: str) -> List[str]:
        """
        Get all episode IDs using analytics endpoint - FIXED parsing
        """
        analytics = self.get_all_episodes_analytics(show_id)
        
        # FIXED: Analytics structure is data.attributes.episodes, not data array
        if 'data' in analytics and 'attributes' in analytics['data']:
            episodes = analytics['data']['attributes'].get('episodes', [])
            return [str(ep['id']) for ep in episodes]
        
        return []
    
    def get_all_episodes_full_data(self, show_id: str) -> Dict[str, Any]:
        """
        Get complete data for ALL episodes using individual API calls
        """
        episode_ids = self.get_all_episode_ids(show_id)
        episodes = []
        failed_episodes = []
        
        print(f"Fetching full data for {len(episode_ids)} episodes...")
        
        for i, episode_id in enumerate(episode_ids):
            try:
                episode = self.get_episode(episode_id)
                episodes.append(episode['data'])
                print(f"  {i+1}/{len(episode_ids)}: {episode['data']['attributes']['title']}")
                
                # Rate limiting: pause every 9 requests
                if (i + 1) % 9 == 0 and i + 1 < len(episode_ids):
                    print("  Pausing to avoid rate limits...")
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                failed_episodes.append({'id': episode_id, 'error': str(e)})
                print(f"  {i+1}/{len(episode_ids)}: FAILED - {e}")
        
        return {
            'data': episodes,
            'meta': {
                'total_requested': len(episode_ids),
                'successful': len(episodes),
                'failed': len(failed_episodes),
                'failed_episodes': failed_episodes
            }
        }
    
    # Essential methods
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
