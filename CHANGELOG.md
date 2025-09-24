# Changelog

## [1.2.0] - 2025-09-24

### Added
- **Automatic Rate Limiting** - Built-in rate limiting (10 req/10s) enabled by default
- Optional `auto_rate_limit=False` parameter to disable automatic rate limiting
- Intelligent request tracking and automatic sleep when approaching limits

### Changed
- `TransistorClient()` constructor now accepts `auto_rate_limit` parameter
- All API calls now automatically respect rate limits without user intervention
- Improved user experience - no more manual rate limit handling required

### Technical Details
- Uses sliding window approach to track last 10 requests
- Automatically sleeps when rate limit would be exceeded
- Zero-configuration rate limiting for better developer experience

## [1.1.0] - 2025-09-22

### Fixed
- **CRITICAL**: Fixed `list_episodes()` endpoint format causing 404 errors
  - Changed from `shows/{show_id}/episodes` to `episodes?show_id={show_id}`
  - Episodes are now accessible instead of returning "Resource not found"

### Added
- `get_all_episode_ids()` method - Retrieves all episode IDs using analytics endpoint workaround
- `get_all_episodes_full_data()` method - Fetches complete data for all episodes with rate limiting
- Comprehensive pagination issue documentation and workarounds

### Changed
- Updated `list_episodes()` documentation to clarify API limitations
- Added warnings about Transistor.fm API's 20-episode limit despite pagination metadata

### API Limitations Documented
- Transistor.fm API only returns first 20 episodes via `list_episodes()`
- API shows `totalPages` and `totalCount` metadata but rejects pagination parameters
- Workaround methods provided for accessing all episodes

## [1.0.0] - 2025-09-21
- Initial release with complete API coverage
- CLI with interactive mode
- Analytics support and error handling
