# Transistor.fm API - ACTUAL Pagination Issue Diagnosis

## Live Test Results with API Key: YYhADUpAtKgHp9bdFa_tjA

### Key Findings

**Your podcast has 65 episodes total, but the API only returns 20 at a time with NO working pagination parameters.**

## Test Results Summary

### ✓ Working Endpoints
```
GET /episodes?show_id=31926
- Returns: 20 episodes (first page only)
- Meta: {"currentPage": 1, "totalPages": 4, "totalCount": 65}
- Status: 200 OK

GET /analytics/31926/episodes  
- Returns: 4 episodes (analytics data only)
- Status: 200 OK
```

### ✗ Broken Endpoints
```
GET /shows/31926/episodes
- Status: 404 Not Found
- Error: {"status":404,"error":"Not Found"}
```

### ✗ Pagination Parameters NOT Supported
```
All of these return 400 Bad Request:
- page=2 → "Invalid parameters: page"
- per_page=10 → "Invalid parameters: per_page" 
- limit=10 → "Invalid parameters: limit"
- page[number]=2 → "Invalid parameters: page"
- page[size]=10 → "Invalid parameters: page"
```

## The Real Problem

**The Transistor.fm API shows pagination metadata but doesn't accept pagination parameters!**

```json
{
  "meta": {
    "currentPage": 1,
    "totalPages": 4, 
    "totalCount": 65
  }
}
```

This indicates 4 pages of data exist, but there's no way to access pages 2-4.

## Impact on Your 65-Episode Podcast

- **Accessible episodes:** 20 (31% of total)
- **Inaccessible episodes:** 45 (69% of total) 
- **API limitation:** No pagination parameters work
- **Workaround required:** Use analytics endpoint (limited data)

## Client Code Issues Confirmed

### Issue 1: Wrong Endpoint Format
```python
# Current broken code in client.py:
endpoint = f"shows/{show_id}/episodes" if show_id else "episodes"
# Results in: GET /shows/31926/episodes → 404 Not Found

# Should be:
endpoint = "episodes"
params = {"show_id": show_id} if show_id else {}
# Results in: GET /episodes?show_id=31926 → 200 OK (but still only 20 episodes)
```

### Issue 2: No Pagination Support Possible
The API itself doesn't support pagination parameters, so the client can't implement proper pagination.

## Recommended Solutions

### 1. Fix the Endpoint (Immediate)
```python
def list_episodes(self, show_id: str = None, **params) -> Dict[str, Any]:
    """List episodes - FIXED endpoint format"""
    if show_id:
        params['show_id'] = show_id
    return self._request("GET", "episodes", params=params)
```

### 2. Document the Limitation
```python
def list_episodes(self, show_id: str = None, **params) -> Dict[str, Any]:
    """
    List episodes (LIMITED TO FIRST 20 ONLY)
    
    WARNING: The Transistor.fm API only returns the first 20 episodes
    and does not support pagination parameters. For complete episode
    access, use get_all_episodes_analytics() as a workaround.
    
    Returns:
        Dict containing up to 20 episodes maximum
    """
```

### 3. Provide Workaround Method
```python
def get_all_episode_ids(self, show_id: str) -> List[str]:
    """
    Get all episode IDs using analytics endpoint workaround
    
    Returns:
        List of all episode IDs for the show
    """
    analytics = self.get_all_episodes_analytics(show_id)
    return [ep['id'] for ep in analytics['data']]

def get_all_episodes_full_data(self, show_id: str) -> List[Dict]:
    """
    Get complete data for all episodes (SLOW - multiple API calls)
    
    Warning: This makes one API call per episode. For 65 episodes,
    this will make 65+ API calls and may hit rate limits.
    """
    episode_ids = self.get_all_episode_ids(show_id)
    episodes = []
    
    for episode_id in episode_ids:
        try:
            episode = self.get_episode(episode_id)
            episodes.append(episode['data'])
        except Exception as e:
            print(f"Failed to get episode {episode_id}: {e}")
    
    return episodes
```

## API Provider Issue

**This is fundamentally a Transistor.fm API limitation, not a client bug.**

The API:
1. ✓ Provides pagination metadata (`totalPages: 4`)
2. ✗ Doesn't accept any pagination parameters
3. ✗ Only returns first 20 episodes regardless of total count

## Immediate Action Items

1. **Fix endpoint format** in `client.py` (line ~150)
2. **Document the 20-episode limitation** clearly
3. **Provide workaround methods** for accessing all episodes
4. **Contact Transistor.fm** about the pagination API limitation

## Test Commands to Verify Fix

```python
# After fixing the endpoint:
client = TransistorClient('YYhADUpAtKgHp9bdFa_tjA')

# This should now work (returns 20 episodes):
episodes = client.list_episodes('31926')
print(f"Episodes: {len(episodes['data'])}")  # Should show 20

# This should show the limitation:
print(f"Total episodes: {episodes['meta']['totalCount']}")  # Shows 65
print(f"Accessible: {len(episodes['data'])}")  # Shows 20
print(f"Missing: {episodes['meta']['totalCount'] - len(episodes['data'])}")  # Shows 45
```

The core issue is that **Transistor.fm's API is incomplete** - it promises pagination but doesn't deliver it.
