# Changelog

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
