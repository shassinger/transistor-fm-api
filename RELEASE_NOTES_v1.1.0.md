# Release Notes v1.1.0 - Episode Pagination Fixes

## 🚨 Critical Bug Fix

Fixed a critical issue where **only 20 out of 65+ episodes were accessible** due to incorrect API endpoint usage and lack of pagination workarounds.

## 🔧 What Was Fixed

### 1. **Endpoint Format Issue**
- **Before**: `GET /shows/{show_id}/episodes` → 404 Not Found
- **After**: `GET /episodes?show_id={show_id}` → 200 OK

### 2. **API Limitation Workarounds**
- Added `get_all_episode_ids()` - Gets all episode IDs via analytics endpoint
- Added `get_all_episodes_full_data()` - Retrieves complete data for all episodes
- Built-in rate limiting protection (10 req/10s compliance)

### 3. **Documentation Updates**
- Clear warnings about API limitations
- Comprehensive workaround examples
- Updated README with pagination solutions

## 📊 Impact

**Before Fix:**
- ❌ `list_episodes()` returned 404 errors
- ❌ Only 20/65 episodes accessible
- ❌ No workaround methods available

**After Fix:**
- ✅ `list_episodes()` works (returns 20 episodes due to API limit)
- ✅ All 65 episodes accessible via workaround methods
- ✅ Complete episode data retrievable with rate limiting

## 🚀 New Methods

```python
# Get all episode IDs (1 API call)
all_ids = client.get_all_episode_ids('show_id')

# Get complete data for all episodes (multiple API calls with rate limiting)
all_episodes = client.get_all_episodes_full_data('show_id')
```

## 📈 Performance

- **Episode ID retrieval**: 1 API call for all episodes
- **Complete data**: N+1 API calls (N episodes + 1 analytics call)
- **Rate limiting**: Automatic pauses to prevent 429 errors

## 🔄 Migration Guide

### Replace This:
```python
episodes = client.list_episodes('show_id')  # Only 20 episodes
```

### With This:
```python
# For all episode IDs:
all_ids = client.get_all_episode_ids('show_id')  # All episodes

# For complete episode data:
all_episodes = client.get_all_episodes_full_data('show_id')  # All episodes with full data
```

## 🧪 Tested With

- Real API key: `YYhADUpAtKgHp9bdFa_tjA`
- Podcast: "The New Quantum Era" (65 episodes)
- All endpoints verified working

## 📋 Files Changed

- `transistor/client.py` - Main client fixes
- `README.md` - Updated documentation
- `setup.py` - Version bump to 1.1.0
- `examples/episode_workarounds.py` - New examples
- `CHANGELOG.md` - Change documentation

## ⚠️ Breaking Changes

None. All existing code continues to work, but `list_episodes()` now returns data instead of 404 errors.

## 🔗 Links

- [GitHub Repository](https://github.com/shassinger/transistor-fm-api)
- [Commit: f23f053](https://github.com/shassinger/transistor-fm-api/commit/f23f053)
- [Transistor.fm API Docs](https://developers.transistor.fm/)

This release resolves the critical pagination issue and provides complete access to all podcast episodes.
