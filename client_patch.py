#!/usr/bin/env python3
"""
Patch to fix the original client.py file
"""

def apply_fix():
    # Read the original client
    with open('/home/ec2-user/transistor-fm-api/transistor/client.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace the broken endpoint logic
    old_endpoint_line = 'endpoint = f"shows/{show_id}/episodes" if show_id else "episodes"'
    new_endpoint_code = '''if show_id:
            params = params.copy() if params else {}
            params['show_id'] = show_id
        endpoint = "episodes"'''
    
    content = content.replace(old_endpoint_line, new_endpoint_code)
    
    # Fix 2: Update the docstring to reflect the limitation
    old_docstring = '''        Note:
            Returns first 20 episodes by default. Use pagination parameters
            or get_all_episodes_analytics() for complete episode data.'''
    
    new_docstring = '''        Note:
            WARNING: Only returns first 20 episodes due to Transistor.fm API limitation.
            The API does not support pagination parameters despite showing totalPages
            in metadata. Use get_all_episode_ids() workaround for complete access.'''
    
    content = content.replace(old_docstring, new_docstring)
    
    # Add the workaround methods before the analytics section
    analytics_comment = "    # Analytics Operations"
    
    workaround_methods = '''    
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

    # Analytics Operations'''
    
    content = content.replace(analytics_comment, workaround_methods)
    
    # Write the fixed client
    with open('/home/ec2-user/transistor-fm-api/transistor/client_fixed_final.py', 'w') as f:
        f.write(content)
    
    print("✓ Applied fixes to create client_fixed_final.py")
    print("✓ Fixed endpoint format: episodes?show_id=X")
    print("✓ Added get_all_episode_ids() method")
    print("✓ Added get_all_episodes_full_data() method")
    print("✓ Updated documentation with API limitations")

if __name__ == "__main__":
    apply_fix()
