"""
Transistor.fm API Client

A complete Python client for the Transistor.fm podcast hosting API.
Supports all endpoints including shows, episodes, analytics, subscribers, and uploads.
"""

import requests
from typing import Dict, List, Optional, Any
from .exceptions import TransistorAPIError, RateLimitError, AuthenticationError, NotFoundError, ValidationError


class TransistorClient:
    """
    Complete Transistor.fm API client
    
    Provides access to all Transistor.fm API endpoints with proper error handling,
    rate limiting awareness, and JSON:API compliance.
    
    Args:
        api_key (str): Your Transistor.fm API key from dashboard.transistor.fm/account
        
    Example:
        >>> client = TransistorClient('your_api_key')
        >>> account = client.get_account()
        >>> shows = client.list_shows()
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
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle specific HTTP status codes
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
    
    # Account Operations
    def get_account(self) -> Dict[str, Any]:
        """
        Get authenticated user account details
        
        Returns:
            Dict containing account information including user ID and attributes
        """
        return self._request("GET", "")
    
    # Show Operations
    def list_shows(self, **params) -> Dict[str, Any]:
        """
        List all shows accessible to the authenticated user
        
        Args:
            **params: Optional query parameters (fields, include, etc.)
            
        Returns:
            Dict containing array of show resources
        """
        return self._request("GET", "shows", params=params)
    
    def get_show(self, show_id: str, **params) -> Dict[str, Any]:
        """
        Get details for a specific show
        
        Args:
            show_id: The show ID
            **params: Optional query parameters
            
        Returns:
            Dict containing show resource details
        """
        return self._request("GET", f"shows/{show_id}", params=params)
    
    def create_show(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new show
        
        Args:
            data: JSON:API formatted show data with type and attributes
            
        Returns:
            Dict containing created show resource
            
        Example:
            >>> data = {
            ...     "data": {
            ...         "type": "show",
            ...         "attributes": {
            ...             "title": "My Podcast",
            ...             "description": "A great podcast"
            ...         }
            ...     }
            ... }
            >>> show = client.create_show(data)
        """
        return self._request("POST", "shows", json=data)
    
    def update_show(self, show_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing show"""
        return self._request("PATCH", f"shows/{show_id}", json=data)
    
    def delete_show(self, show_id: str) -> Dict[str, Any]:
        """Delete a show"""
        return self._request("DELETE", f"shows/{show_id}")
    
    # Episode Operations
    def list_episodes(self, show_id: str = None, **params) -> Dict[str, Any]:
        """
        List episodes, optionally filtered by show
        
        Args:
            show_id: Optional show ID to filter episodes
            **params: Optional query parameters
            
        Returns:
            Dict containing episodes array (paginated, default 20 per page)
            
        Note:
            WARNING: Only returns first 20 episodes due to Transistor.fm API limitation.
            The API does not support pagination parameters despite showing totalPages
            in metadata. Use get_all_episode_ids() workaround for complete access.
        """
        if show_id:
            params = params.copy() if params else {}
            params['show_id'] = show_id
        endpoint = "episodes"
        return self._request("GET", endpoint, params=params)
    
    def get_episode(self, episode_id: str, **params) -> Dict[str, Any]:
        """Get details for a specific episode"""
        return self._request("GET", f"episodes/{episode_id}", params=params)
    
    def create_episode(self, show_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new episode for a show
        
        Args:
            show_id: The show ID to create episode in
            data: JSON:API formatted episode data
            
        Example:
            >>> data = {
            ...     "data": {
            ...         "type": "episode",
            ...         "attributes": {
            ...             "title": "Episode 1",
            ...             "description": "First episode"
            ...         }
            ...     }
            ... }
            >>> episode = client.create_episode('show_id', data)
        """
        return self._request("POST", f"shows/{show_id}/episodes", json=data)
    
    def update_episode(self, episode_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing episode"""
        return self._request("PATCH", f"episodes/{episode_id}", json=data)
    
    def delete_episode(self, episode_id: str) -> Dict[str, Any]:
        """Delete an episode"""
        return self._request("DELETE", f"episodes/{episode_id}")
    
    def publish_episode(self, episode_id: str) -> Dict[str, Any]:
        """Publish an episode"""
        return self._request("PATCH", f"episodes/{episode_id}/publish")
    
    def unpublish_episode(self, episode_id: str) -> Dict[str, Any]:
        """Unpublish an episode"""
        return self._request("PATCH", f"episodes/{episode_id}/unpublish")
    
    
    def get_all_episode_ids(self, show_id: str) -> List[str]:
        """
        Get all episode IDs using analytics endpoint workaround
        
        Args:
            show_id: The show ID
            
        Returns:
            List of all episode IDs for the show
            
        Note:
            This uses the analytics endpoint which returns all episodes.
            The Transistor.fm API limitation prevents direct episode pagination.
        """
        analytics = self.get_all_episodes_analytics(show_id)
        
        # Analytics structure: data.attributes.episodes (not data array)
        if 'data' in analytics and 'attributes' in analytics['data']:
            episodes = analytics['data']['attributes'].get('episodes', [])
            return [str(ep['id']) for ep in episodes]
        
        return []
    
    def get_all_episodes_full_data(self, show_id: str) -> Dict[str, Any]:
        """
        Get complete data for ALL episodes using individual API calls
        
        Args:
            show_id: The show ID
            
        Returns:
            Dict containing all episodes with full data
            
        WARNING:
            This makes one API call per episode and may hit rate limits.
            For your 65-episode podcast, this makes 65+ API calls.
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
                if (i + 1) % 9 == 0 and i + 1 < len(episode_ids):
                    import time
                    time.sleep(1)
                    
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

    # Analytics Operations
    def get_analytics(self, analytics_id: str, **params) -> Dict[str, Any]:
        """
        Get analytics data by analytics ID
        
        Args:
            analytics_id: The analytics resource ID
            **params: Optional parameters (start_date, end_date in dd-mm-yyyy format)
            
        Returns:
            Dict containing analytics data with downloads per day
        """
        return self._request("GET", f"analytics/{analytics_id}", params=params)
    
    def get_show_analytics(self, show_id: str, **params) -> Dict[str, Any]:
        """
        Get download analytics for an entire show
        
        Args:
            show_id: The show ID
            **params: Optional parameters (start_date, end_date in dd-mm-yyyy format)
            
        Returns:
            Dict containing show-level analytics with daily download counts
            Defaults to last 14 days if no date range specified
            
        Example:
            >>> # Get last 30 days of show analytics
            >>> analytics = client.get_show_analytics('31926', 
            ...     start_date='22-08-2025', end_date='21-09-2025')
        """
        return self._request("GET", f"analytics/{show_id}", params=params)
    
    def get_all_episodes_analytics(self, show_id: str, **params) -> Dict[str, Any]:
        """
        Get analytics for ALL episodes of a show in one request
        
        Args:
            show_id: The show ID
            **params: Optional parameters (start_date, end_date in dd-mm-yyyy format)
            
        Returns:
            Dict containing analytics for all episodes with individual download data
            Defaults to last 7 days if no date range specified
            
        Note:
            This endpoint returns ALL episodes (not paginated like list_episodes)
            and includes download analytics for each episode in the specified period.
            
        Example:
            >>> # Get analytics for all episodes in the last 30 days
            >>> analytics = client.get_all_episodes_analytics('31926',
            ...     start_date='22-08-2025', end_date='21-09-2025')
        """
        return self._request("GET", f"analytics/{show_id}/episodes", params=params)
    
    def get_episode_analytics(self, episode_id: str, **params) -> Dict[str, Any]:
        """
        Get analytics for a specific episode
        
        Args:
            episode_id: The episode ID
            **params: Optional parameters (start_date, end_date in dd-mm-yyyy format)
            
        Returns:
            Dict containing episode analytics with daily download breakdown
            Defaults to last 14 days if no date range specified
        """
        return self._request("GET", f"analytics/episodes/{episode_id}", params=params)
    
    # Private Subscriber Operations
    def list_subscribers(self, show_id: str, **params) -> Dict[str, Any]:
        """List private subscribers for a show"""
        return self._request("GET", f"shows/{show_id}/private_subscribers", params=params)
    
    def create_subscriber(self, show_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a private subscriber for a show"""
        return self._request("POST", f"shows/{show_id}/private_subscribers", json=data)
    
    def delete_subscriber(self, show_id: str, subscriber_id: str) -> Dict[str, Any]:
        """Delete a private subscriber"""
        return self._request("DELETE", f"shows/{show_id}/private_subscribers/{subscriber_id}")
    
    # Audio Upload Operations
    def upload_audio(self, file_path: str, **params) -> Dict[str, Any]:
        """
        Upload an audio file to Transistor
        
        Args:
            file_path: Path to the audio file to upload
            **params: Optional upload parameters
            
        Returns:
            Dict containing upload response with file details
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            TransistorAPIError: If upload fails
        """
        with open(file_path, 'rb') as f:
            files = {'audio_file': f}
            # Remove Content-Type for file uploads to let requests set it
            headers = {k: v for k, v in self.session.headers.items() if k != 'Content-Type'}
            response = requests.post(
                f"{self.BASE_URL}/uploads",
                files=files,
                headers=headers,
                params=params
            )
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", 429, response)
            elif not response.ok:
                raise TransistorAPIError(f"Upload failed: {response.text}", response.status_code, response)
            
            return response.json()
