"""
Transistor.fm API Client - Fixed Version with Proper Pagination

This is an improved version of the client that addresses pagination issues.
"""

import requests
from typing import Dict, List, Optional, Any
from .exceptions import TransistorAPIError, RateLimitError, AuthenticationError, NotFoundError, ValidationError


class TransistorClientFixed:
    """
    Improved Transistor.fm API client with proper pagination support
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
    
    def list_episodes(self, show_id: str = None, page: int = 1, per_page: int = 20, **params) -> Dict[str, Any]:
        """
        List episodes with proper pagination support
        
        Args:
            show_id: Optional show ID to filter episodes
            page: Page number (default: 1)
            per_page: Episodes per page (default: 20, max recommended: 100)
            **params: Additional query parameters
            
        Returns:
            Dict containing episodes array with pagination metadata
            
        Example:
            >>> # Get first page (20 episodes)
            >>> episodes = client.list_episodes('show_id')
            >>> 
            >>> # Get second page
            >>> episodes_page2 = client.list_episodes('show_id', page=2)
            >>> 
            >>> # Get more episodes per page
            >>> episodes_large = client.list_episodes('show_id', per_page=50)
        """
        # Build pagination parameters
        pagination_params = {
            'page': page,
            'per_page': min(per_page, 100)  # Cap at 100 to avoid API limits
        }
        pagination_params.update(params)
        
        endpoint = f"shows/{show_id}/episodes" if show_id else "episodes"
        response = self._request("GET", endpoint, params=pagination_params)
        
        # Add pagination metadata if not present
        if 'meta' not in response:
            response['meta'] = {
                'current_page': page,
                'per_page': per_page,
                'returned_count': len(response.get('data', []))
            }
        
        return response
    
    def get_all_episodes(self, show_id: str, batch_size: int = 100) -> Dict[str, Any]:
        """
        Get ALL episodes for a show by automatically handling pagination
        
        Args:
            show_id: The show ID
            batch_size: Episodes to fetch per API call (default: 100)
            
        Returns:
            Dict containing all episodes for the show with total count
            
        Example:
            >>> # Get all episodes at once
            >>> all_episodes = client.get_all_episodes('show_id')
            >>> print(f"Total episodes: {len(all_episodes['data'])}")
        """
        all_episodes = []
        page = 1
        
        while True:
            try:
                response = self.list_episodes(show_id, page=page, per_page=batch_size)
                episodes = response.get('data', [])
                
                if not episodes:
                    break
                    
                all_episodes.extend(episodes)
                
                # If we got fewer episodes than requested, we're on the last page
                if len(episodes) < batch_size:
                    break
                    
                page += 1
                
            except (NotFoundError, TransistorAPIError) as e:
                # If we get an error on page > 1, we've likely reached the end
                if page > 1:
                    break
                else:
                    raise e
        
        return {
            'data': all_episodes,
            'meta': {
                'total_count': len(all_episodes),
                'pages_fetched': page,
                'batch_size': batch_size
            }
        }
    
    def list_episodes_iterator(self, show_id: str = None, per_page: int = 20):
        """
        Iterator that yields episodes page by page
        
        Args:
            show_id: Optional show ID to filter episodes
            per_page: Episodes per page
            
        Yields:
            Individual episode dictionaries
            
        Example:
            >>> # Process episodes one by one without loading all into memory
            >>> for episode in client.list_episodes_iterator('show_id'):
            ...     print(f"Episode: {episode['attributes']['title']}")
        """
        page = 1
        
        while True:
            response = self.list_episodes(show_id, page=page, per_page=per_page)
            episodes = response.get('data', [])
            
            if not episodes:
                break
                
            for episode in episodes:
                yield episode
                
            if len(episodes) < per_page:
                break
                
            page += 1
    
    # Include all other methods from original client
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
    
    def create_episode(self, show_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new episode for a show"""
        return self._request("POST", f"shows/{show_id}/episodes", json=data)
    
    def update_episode(self, episode_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing episode"""
        return self._request("PATCH", f"episodes/{episode_id}", json=data)
    
    def delete_episode(self, episode_id: str) -> Dict[str, Any]:
        """Delete an episode"""
        return self._request("DELETE", f"episodes/{episode_id}")
