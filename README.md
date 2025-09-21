# Transistor.fm API Python Client

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete Python client library for the [Transistor.fm](https://transistor.fm) podcast hosting API. Provides full access to shows, episodes, analytics, subscribers, and file uploads with both programmatic and command-line interfaces.

## Features

- ✅ **Complete API Coverage** - All Transistor.fm API endpoints
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

# List episodes
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

### Interactive Mode

The CLI includes an interactive mode for easy API exploration:

```bash
$ transistor interactive
Transistor API Interactive Mode
Type 'help' for commands, 'quit' to exit

transistor> help
Available commands:
  account              - Get account info
  shows                - List shows
  episodes             - List episodes
  show <id>            - Get show details
  episode <id>         - Get episode details
  analytics <id>       - Get analytics by ID
  show-analytics <id>  - Get show analytics
  episode-analytics <id> - Get episode analytics
  all-episodes <id>    - Get all episodes analytics
  quit                 - Exit

transistor> shows
ID         Title                          Status    
----------------------------------------------------
31926      The New Quantum Era           published

transistor> show-analytics 31926
Analytics for last 7 days...

transistor> quit
```

## API Reference

### Authentication

Get your API key from [dashboard.transistor.fm/account](https://dashboard.transistor.fm/account).

```python
client = TransistorClient('your_api_key')
```

### Account Operations

```python
# Get account details
account = client.get_account()
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

### Episode Operations

```python
# List episodes (paginated - returns first 20)
episodes = client.list_episodes()

# List episodes for specific show
episodes = client.list_episodes('show_id')

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

**Analytics Data Structure:**
```python
{
    "data": {
        "attributes": {
            "downloads": [
                {"date": "21-09-2025", "downloads": 150},
                {"date": "20-09-2025", "downloads": 200}
            ],
            "start_date": "15-09-2025",
            "end_date": "21-09-2025"
        }
    }
}
```

### Private Subscriber Operations

```python
# List private subscribers
subscribers = client.list_subscribers('show_id')

# Create private subscriber
subscriber_data = {
    "data": {
        "type": "private_subscriber",
        "attributes": {
            "email": "subscriber@example.com"
        }
    }
}
subscriber = client.create_subscriber('show_id', subscriber_data)

# Delete subscriber
client.delete_subscriber('show_id', 'subscriber_id')
```

### File Upload Operations

```python
# Upload audio file
upload_result = client.upload_audio('/path/to/audio.mp3')
print(f"Upload URL: {upload_result['data']['attributes']['upload_url']}")
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

### Exception Types

- `TransistorAPIError` - Base exception for all API errors
- `RateLimitError` - Rate limit exceeded (429) - wait 10 seconds
- `AuthenticationError` - Invalid API key (401)
- `NotFoundError` - Resource not found (404)
- `ValidationError` - Request validation failed (422)

## Rate Limiting

The Transistor API is limited to **10 requests per 10 seconds**. The client automatically detects rate limit errors and raises `RateLimitError` when limits are exceeded.

```python
import time
from transistor import RateLimitError

try:
    result = client.get_show_analytics('show_id')
except RateLimitError:
    print("Rate limited - waiting 10 seconds...")
    time.sleep(10)
    result = client.get_show_analytics('show_id')  # Retry
```

## Analytics Data Availability

Analytics data is available from **January 1, 2022** onwards:

- ✅ **Complete data:** Jan 1, 2022 to present (nearly 4 years)
- ✅ **Daily breakdown:** Downloads per day for each episode
- ✅ **Date filtering:** Custom date ranges in dd-mm-yyyy format
- ✅ **All episodes:** Use `get_all_episodes_analytics()` to get all episodes in one request (not paginated)

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

### v1.0.0
- Initial release
- Complete API coverage for all endpoints
- CLI with interactive mode
- Comprehensive analytics support
- Full error handling and rate limiting
- Type hints and documentation
