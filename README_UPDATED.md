# Transistor.fm API Python Client

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete Python client library for the [Transistor.fm](https://transistor.fm) podcast hosting API. Provides full access to shows, episodes, analytics, subscribers, and file uploads with both programmatic and command-line interfaces.

## ⚠️ Important: Episode Pagination Limitation

**The Transistor.fm API has a limitation where `list_episodes()` only returns the first 20 episodes**, regardless of your podcast's total episode count. This client provides workaround methods to access all episodes.

## Features

- ✅ **Complete API Coverage** - All Transistor.fm API endpoints
- ✅ **Episode Pagination Workarounds** - Access all episodes despite API limitations
- ✅ **Analytics Support** - Comprehensive download analytics with date filtering  
- ✅ **CLI Tools** - Command-line interface with interactive mode
- ✅ **Error Handling** - Specific exceptions for different error types
- ✅ **Rate Limiting** - Built-in awareness of API rate limits (10 req/10s)
- ✅ **JSON:API Compliant** - Proper data formatting and sparse fieldsets
- ✅ **Type Hints** - Full type annotations for better IDE support
- ✅ **File Uploads** - Audio file upload support

## Installation

```bash
pip install transistor-api
```

## Quick Start

### Episode Access (Important!)

```python
from transistor import TransistorClient

client = TransistorClient('your_api_key_here')

# ⚠️ This only returns first 20 episodes (API limitation)
episodes = client.list_episodes('show_id')
print(f"Episodes: {len(episodes['data'])}")  # Max 20

# ✅ Get all episode IDs (recommended)
all_episode_ids = client.get_all_episode_ids('show_id')
print(f"Total episodes: {len(all_episode_ids)}")  # All episodes

# ✅ Get complete data for all episodes (slower)
all_episodes = client.get_all_episodes_full_data('show_id')
print(f"Complete episodes: {len(all_episodes['data'])}")  # All episodes with full data
```

### Python Library

```python
from transistor import TransistorClient

# Initialize client with your API key
client = TransistorClient('your_api_key_here')

# Get account information
account = client.get_account()
print(f"Account ID: {account['data']['id']}")

# List all shows
shows = client.list_shows()
for show in shows['data']:
    print(f"Show: {show['attributes']['title']}")

# Get analytics for all episodes (last 30 days)
analytics = client.get_all_episodes_analytics('show_id',
    start_date='22-08-2025', 
    end_date='21-09-2025'
)

# Create a new episode
episode_data = {
    "data": {
        "type": "episode",
        "attributes": {
            "title": "My New Episode",
            "description": "Episode description here"
        }
    }
}
episode = client.create_episode('show_id', episode_data)
```

### Command Line Interface

Set your API key as an environment variable:

```bash
export TRANSISTOR_API_KEY=your_api_key_here
```

Basic CLI usage:

```bash
# Get account info
transistor account

# List all shows
transistor shows list

# Get show details
transistor shows get SHOW_ID

# Create a new show
transistor shows create --title "My Podcast" --description "A great podcast"

# List episodes (⚠️ only shows first 20)
transistor episodes list

# Create episode
transistor episodes create SHOW_ID --title "Episode 1" --description "First episode"

# Get show analytics (table format)
transistor analytics show SHOW_ID --format table

# Get analytics for all episodes
transistor analytics all-episodes SHOW_ID --start-date 01-08-2025 --end-date 21-09-2025

# Upload audio file
transistor upload /path/to/audio.mp3

# Interactive mode
transistor interactive
```

## API Reference

### Episode Operations (Updated)

```python
# ⚠️ Limited episode listing (first 20 only)
episodes = client.list_episodes('show_id')

# ✅ Get all episode IDs using analytics workaround
all_ids = client.get_all_episode_ids('show_id')

# ✅ Get complete data for all episodes
all_episodes = client.get_all_episodes_full_data('show_id')

# Get specific episode
episode = client.get_episode('episode_id')

# Create episode
episode_data = {
    "data": {
        "type": "episode",
        "attributes": {
            "title": "Episode Title",
            "description": "Episode description"
        }
    }
}
episode = client.create_episode('show_id', episode_data)

# Update episode
client.update_episode('episode_id', updated_data)

# Publish/unpublish episode
client.publish_episode('episode_id')
client.unpublish_episode('episode_id')

# Delete episode
client.delete_episode('episode_id')
```

### New Workaround Methods

```python
def get_all_episode_ids(self, show_id: str) -> List[str]:
    """
    Get all episode IDs using analytics endpoint workaround
    
    Returns:
        List of all episode IDs for the show
        
    Note:
        This bypasses the 20-episode limitation by using the analytics
        endpoint which returns all episodes.
    """

def get_all_episodes_full_data(self, show_id: str) -> Dict[str, Any]:
    """
    Get complete data for ALL episodes using individual API calls
    
    Returns:
        Dict containing all episodes with full data
        
    Warning:
        Makes one API call per episode. For large podcasts, this may
        hit rate limits. Built-in rate limiting protection included.
    """
```

### Show Operations

```python
# List all shows
shows = client.list_shows()

# Get specific show
show = client.get_show('show_id')

# Create show
show_data = {
    "data": {
        "type": "show",
        "attributes": {
            "title": "My Podcast",
            "description": "Podcast description"
        }
    }
}
show = client.create_show(show_data)

# Update show
client.update_show('show_id', updated_data)

# Delete show
client.delete_show('show_id')
```

### Analytics Operations

The analytics system provides comprehensive download data from **January 1, 2022** onwards (nearly 4 years of historical data).

```python
# Get show analytics (defaults to last 14 days)
analytics = client.get_show_analytics('show_id')

# Get show analytics with date range
analytics = client.get_show_analytics('show_id',
    start_date='01-01-2024',  # dd-mm-yyyy format
    end_date='31-12-2024'
)

# Get analytics for ALL episodes (not paginated!)
all_episodes = client.get_all_episodes_analytics('show_id')

# Get analytics for specific episode
episode_analytics = client.get_episode_analytics('episode_id',
    start_date='01-08-2025',
    end_date='21-09-2025'
)

# Get analytics by analytics ID
analytics = client.get_analytics('analytics_id')
```

## Episode Pagination Workaround

Due to Transistor.fm API limitations, use these patterns:

### For Episode Counts
```python
# Get total episode count
all_ids = client.get_all_episode_ids('show_id')
total_episodes = len(all_ids)
print(f"Podcast has {total_episodes} episodes")
```

### For Episode Processing
```python
# Process all episodes efficiently
all_ids = client.get_all_episode_ids('show_id')

for episode_id in all_ids:
    episode = client.get_episode(episode_id)
    title = episode['data']['attributes']['title']
    print(f"Processing: {title}")
    
    # Add rate limiting for large podcasts
    if len(all_ids) > 50:
        import time
        time.sleep(0.1)  # Brief pause
```

### For Complete Episode Data
```python
# Get all episodes with full data (handles rate limiting automatically)
all_episodes = client.get_all_episodes_full_data('show_id')

print(f"Retrieved {len(all_episodes['data'])} episodes")
print(f"Failed: {all_episodes['meta']['failed']} episodes")

for episode in all_episodes['data']:
    print(f"Episode: {episode['attributes']['title']}")
```

## Error Handling

The library provides specific exceptions for different error types:

```python
from transistor import TransistorClient, TransistorAPIError, RateLimitError, AuthenticationError

try:
    client = TransistorClient('invalid_key')
    account = client.get_account()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded - wait 10 seconds")
except TransistorAPIError as e:
    print(f"API error: {e}")
```

## Rate Limiting

The Transistor API is limited to **10 requests per 10 seconds**. The workaround methods include automatic rate limiting protection.

```python
import time
from transistor import RateLimitError

try:
    # This method includes built-in rate limiting
    all_episodes = client.get_all_episodes_full_data('show_id')
except RateLimitError:
    print("Rate limited - waiting 10 seconds...")
    time.sleep(10)
```

## Known API Limitations

### Episode Pagination
- ❌ `list_episodes()` only returns first 20 episodes
- ❌ API rejects pagination parameters (`page`, `per_page`, etc.)
- ❌ API shows `totalPages` metadata but provides no way to access additional pages
- ✅ Workaround methods provided for complete episode access

### Analytics vs Episodes
- ✅ Analytics endpoints return all episodes
- ❌ Episode endpoints are paginated without working pagination
- ✅ Individual episode access works for any episode ID

## Development

### Setting up for development:

```bash
git clone https://github.com/your-username/transistor-api.git
cd transistor-api
pip install -e ".[dev]"
```

### Running tests:

```bash
pytest
```

### Code formatting:

```bash
black transistor/
flake8 transistor/
```

## Examples

See the `examples/` directory for complete usage examples:

- `examples/basic_usage.py` - Basic library usage
- `examples/analytics_usage.py` - Analytics-focused examples
- `examples/episode_workarounds.py` - Episode pagination workarounds

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Transistor.fm](https://transistor.fm) - Podcast hosting platform
- [API Documentation](https://developers.transistor.fm/) - Official API docs
- [Dashboard](https://dashboard.transistor.fm/account) - Get your API key
- [PyPI Package](https://pypi.org/project/transistor-api/) - Install via pip

## Changelog

### v1.1.0 - Episode Pagination Fixes
- Fixed `list_episodes()` endpoint format (404 → 200)
- Added `get_all_episode_ids()` workaround method
- Added `get_all_episodes_full_data()` with rate limiting
- Documented API limitations and workarounds

### v1.0.0 - Initial Release
- Complete API coverage for all endpoints
- CLI with interactive mode
- Comprehensive analytics support
- Full error handling and rate limiting
- Type hints and documentation
