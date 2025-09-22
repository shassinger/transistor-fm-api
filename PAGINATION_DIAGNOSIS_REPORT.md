# Transistor.fm API Pagination Issues - Diagnosis Report

## Executive Summary

The Transistor.fm API client has a **critical pagination issue** where `list_episodes()` only returns the first 20 episodes by default, with no built-in mechanism to retrieve additional pages. For podcasts with 65+ episodes, this means **45+ episodes are inaccessible** through the standard listing method.

## Issues Identified

### 1. **Missing Pagination Parameters**

The `list_episodes()` method accepts `**params` but provides no documentation or implementation for pagination parameters.

**Current Implementation:**
```python
def list_episodes(self, show_id: str = None, **params) -> Dict[str, Any]:
    """
    List episodes, optionally filtered by show
    
    Note:
        Returns first 20 episodes by default. Use pagination parameters
        or get_all_episodes_analytics() for complete episode data.
    """
    endpoint = f"shows/{show_id}/episodes" if show_id else "episodes"
    return self._request("GET", endpoint, params=params)
```

**Problem:** No guidance on what pagination parameters to use.

### 2. **Inconsistent API Coverage**

The client provides `get_all_episodes_analytics()` which returns ALL episodes, but no equivalent `get_all_episodes()` method.

**Working Method (Analytics):**
```python
def get_all_episodes_analytics(self, show_id: str, **params) -> Dict[str, Any]:
    """Get analytics for ALL episodes of a show in one request"""
    return self._request("GET", f"analytics/{show_id}/episodes", params=params)
```

**Missing Method:**
```python
# This method doesn't exist but should
def get_all_episodes(self, show_id: str) -> Dict[str, Any]:
    """Get ALL episodes for a show (not paginated)"""
```

### 3. **CLI Pagination Gaps**

The CLI has no pagination support for episode listing:

```python
def list_episodes(ctx, show_id):
    """List episodes"""
    try:
        result = ctx.obj['client'].list_episodes(show_id)  # Only gets first 20
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}")
```

## Code Examples Demonstrating Issues

### Issue 1: Limited Episode Access
```python
from transistor import TransistorClient

client = TransistorClient('your_api_key')

# This only returns 20 episodes maximum
episodes = client.list_episodes('show_id')
print(f"Episodes found: {len(episodes['data'])}")  # Will show 20 max

# But analytics shows all episodes exist
analytics = client.get_all_episodes_analytics('show_id')
print(f"Episodes in analytics: {len(analytics['data'])}")  # Shows all 65
```

### Issue 2: Unknown Pagination Parameters
```python
# These might work but are undocumented:
episodes_page2 = client.list_episodes('show_id', page=2)
episodes_large = client.list_episodes('show_id', per_page=100)
episodes_offset = client.list_episodes('show_id', offset=20, limit=50)

# No way to know which parameters the API accepts
```

### Issue 3: Workaround Required
```python
# Current workaround: Use analytics to get episode IDs, then fetch individually
analytics = client.get_all_episodes_analytics('show_id')
all_episode_ids = [ep['id'] for ep in analytics['data']]

# Fetch each episode individually (inefficient)
all_episodes = []
for episode_id in all_episode_ids:
    episode = client.get_episode(episode_id)
    all_episodes.append(episode['data'])
```

## Proposed Solutions

### 1. **Add Pagination Support to list_episodes()**

```python
def list_episodes(self, show_id: str = None, page: int = 1, per_page: int = 20, **params) -> Dict[str, Any]:
    """
    List episodes with pagination support
    
    Args:
        show_id: Optional show ID to filter episodes
        page: Page number (default: 1)
        per_page: Episodes per page (default: 20, max: 100)
        **params: Additional query parameters
    """
    pagination_params = {'page': page, 'per_page': per_page}
    pagination_params.update(params)
    
    endpoint = f"shows/{show_id}/episodes" if show_id else "episodes"
    return self._request("GET", endpoint, params=pagination_params)
```

### 2. **Add get_all_episodes() Method**

```python
def get_all_episodes(self, show_id: str) -> Dict[str, Any]:
    """
    Get ALL episodes for a show (not paginated)
    
    Args:
        show_id: The show ID
        
    Returns:
        Dict containing all episodes for the show
    """
    all_episodes = []
    page = 1
    
    while True:
        response = self.list_episodes(show_id, page=page, per_page=100)
        episodes = response['data']
        
        if not episodes:
            break
            
        all_episodes.extend(episodes)
        
        # Check if we have more pages
        if len(episodes) < 100:
            break
            
        page += 1
    
    return {
        'data': all_episodes,
        'meta': {'total_count': len(all_episodes)}
    }
```

### 3. **Add CLI Pagination Support**

```python
@click.command()
@click.option('--show-id', help='Filter by show ID')
@click.option('--page', default=1, help='Page number')
@click.option('--per-page', default=20, help='Episodes per page')
@click.option('--all', is_flag=True, help='Get all episodes')
@click.pass_context
def list_episodes(ctx, show_id, page, per_page, all):
    """List episodes with pagination"""
    try:
        if all:
            result = ctx.obj['client'].get_all_episodes(show_id)
        else:
            result = ctx.obj['client'].list_episodes(show_id, page=page, per_page=per_page)
        
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}")
```

## Testing the Fixes

### Test Script for Pagination
```python
#!/usr/bin/env python3
"""Test pagination fixes"""

def test_pagination_fixes():
    client = TransistorClient('your_api_key')
    show_id = 'your_show_id'
    
    # Test 1: Paginated access
    page1 = client.list_episodes(show_id, page=1, per_page=20)
    page2 = client.list_episodes(show_id, page=2, per_page=20)
    
    print(f"Page 1: {len(page1['data'])} episodes")
    print(f"Page 2: {len(page2['data'])} episodes")
    
    # Test 2: Get all episodes
    all_episodes = client.get_all_episodes(show_id)
    print(f"All episodes: {len(all_episodes['data'])} episodes")
    
    # Test 3: Verify no duplicates
    page1_ids = {ep['id'] for ep in page1['data']}
    page2_ids = {ep['id'] for ep in page2['data']}
    overlap = page1_ids & page2_ids
    
    print(f"Overlap between pages: {len(overlap)} (should be 0)")
```

## Impact Assessment

### Current Impact
- **Data Loss:** 45+ episodes inaccessible via standard API calls
- **User Experience:** CLI users can't see their full episode catalog
- **Workarounds Required:** Users must use analytics endpoints or individual episode fetching

### Post-Fix Benefits
- **Complete Data Access:** All episodes accessible through proper pagination
- **Improved Performance:** Efficient batch retrieval options
- **Better UX:** CLI users can navigate through all episodes
- **API Consistency:** Matches expected REST API pagination patterns

## Recommended Implementation Priority

1. **High Priority:** Add pagination parameters to `list_episodes()`
2. **Medium Priority:** Add `get_all_episodes()` convenience method  
3. **Medium Priority:** Update CLI with pagination support
4. **Low Priority:** Add pagination metadata to responses

## API Documentation Needed

The Transistor.fm API documentation should clarify:
- Supported pagination parameters (`page`, `per_page`, `offset`, `limit`)
- Maximum `per_page` values
- Response metadata format for pagination info
- Rate limiting considerations for large requests

This pagination issue significantly impacts the usability of the API client and should be addressed as a high-priority bug fix.
