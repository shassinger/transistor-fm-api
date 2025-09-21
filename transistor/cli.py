"""
Transistor.fm API Command Line Interface

Provides both command-line tools and an interactive mode for working
with the Transistor.fm API. Supports all major operations including
show management, episode operations, analytics, and file uploads.
"""

import click
import json
import os
from .client import TransistorClient
from .exceptions import TransistorAPIError


@click.group()
@click.option('--api-key', envvar='TRANSISTOR_API_KEY', help='Transistor API key')
@click.pass_context
def main(ctx, api_key):
    """
    Transistor.fm API CLI
    
    Command-line interface for the Transistor.fm podcast hosting API.
    Requires an API key from dashboard.transistor.fm/account
    
    Set your API key via environment variable:
        export TRANSISTOR_API_KEY=your_api_key
    
    Or pass it directly:
        transistor --api-key your_api_key command
    """
    if not api_key:
        click.echo("Error: API key required. Set TRANSISTOR_API_KEY env var or use --api-key")
        ctx.exit(1)
    
    ctx.ensure_object(dict)
    ctx.obj['client'] = TransistorClient(api_key)


@main.command()
@click.pass_context
def account(ctx):
    """Get account information"""
    try:
        result = ctx.obj['client'].get_account()
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@main.group()
def shows():
    """Show management commands"""
    pass


@shows.command('list')
@click.pass_context
def list_shows(ctx):
    """List all shows"""
    try:
        result = ctx.obj['client'].list_shows()
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@shows.command('get')
@click.argument('show_id')
@click.pass_context
def get_show(ctx, show_id):
    """Get show details"""
    try:
        result = ctx.obj['client'].get_show(show_id)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@shows.command('create')
@click.option('--title', required=True, help='Show title')
@click.option('--description', help='Show description')
@click.pass_context
def create_show(ctx, title, description):
    """Create new show"""
    data = {"data": {"type": "show", "attributes": {"title": title}}}
    if description:
        data["data"]["attributes"]["description"] = description
    
    try:
        result = ctx.obj['client'].create_show(data)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@main.group()
def episodes():
    """Episode management commands"""
    pass


@episodes.command('list')
@click.option('--show-id', help='Filter by show ID')
@click.pass_context
def list_episodes(ctx, show_id):
    """List episodes"""
    try:
        result = ctx.obj['client'].list_episodes(show_id)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@episodes.command('get')
@click.argument('episode_id')
@click.pass_context
def get_episode(ctx, episode_id):
    """Get episode details"""
    try:
        result = ctx.obj['client'].get_episode(episode_id)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@episodes.command('create')
@click.argument('show_id')
@click.option('--title', required=True, help='Episode title')
@click.option('--description', help='Episode description')
@click.option('--audio-url', help='Audio file URL')
@click.pass_context
def create_episode(ctx, show_id, title, description, audio_url):
    """Create new episode"""
    data = {"data": {"type": "episode", "attributes": {"title": title}}}
    if description:
        data["data"]["attributes"]["description"] = description
    if audio_url:
        data["data"]["attributes"]["media_url"] = audio_url
    
    try:
        result = ctx.obj['client'].create_episode(show_id, data)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@episodes.command('publish')
@click.argument('episode_id')
@click.pass_context
def publish_episode(ctx, episode_id):
    """Publish episode"""
    try:
        result = ctx.obj['client'].publish_episode(episode_id)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@main.group()
def analytics():
    """Analytics commands"""
    pass


@analytics.command('get')
@click.argument('analytics_id')
@click.option('--start-date', help='Start date (dd-mm-yyyy)')
@click.option('--end-date', help='End date (dd-mm-yyyy)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='json')
@click.pass_context
def get_analytics(ctx, analytics_id, start_date, end_date, output_format):
    """Get analytics data"""
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    try:
        result = ctx.obj['client'].get_analytics(analytics_id, **params)
        if output_format == 'table':
            _display_analytics_table(result)
        else:
            click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@analytics.command('show')
@click.argument('show_id')
@click.option('--start-date', help='Start date (dd-mm-yyyy)')
@click.option('--end-date', help='End date (dd-mm-yyyy)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table')
@click.pass_context
def show_analytics(ctx, show_id, start_date, end_date, output_format):
    """Get show analytics"""
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    try:
        result = ctx.obj['client'].get_show_analytics(show_id, **params)
        if output_format == 'table':
            _display_analytics_table(result)
        else:
            click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@analytics.command('episode')
@click.argument('episode_id')
@click.option('--start-date', help='Start date (dd-mm-yyyy)')
@click.option('--end-date', help='End date (dd-mm-yyyy)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table')
@click.pass_context
def episode_analytics(ctx, episode_id, start_date, end_date, output_format):
    """Get episode analytics"""
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    try:
        result = ctx.obj['client'].get_episode_analytics(episode_id, **params)
        if output_format == 'table':
            _display_analytics_table(result)
        else:
            click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@analytics.command('all-episodes')
@click.argument('show_id')
@click.option('--start-date', help='Start date (dd-mm-yyyy)')
@click.option('--end-date', help='End date (dd-mm-yyyy)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table')
@click.pass_context
def all_episodes_analytics(ctx, show_id, start_date, end_date, output_format):
    """Get analytics for all episodes of a show"""
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    try:
        result = ctx.obj['client'].get_all_episodes_analytics(show_id, **params)
        if output_format == 'table':
            _display_episodes_analytics_table(result)
        else:
            click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


def _display_analytics_table(data):
    """Display analytics in table format"""
    if 'data' in data:
        analytics = data['data']
        if isinstance(analytics, list):
            for item in analytics:
                _print_analytics_item(item)
        else:
            _print_analytics_item(analytics)
    else:
        click.echo("No analytics data found")


def _display_episodes_analytics_table(data):
    """Display all episodes analytics in table format"""
    if 'data' in data and 'attributes' in data['data'] and 'episodes' in data['data']['attributes']:
        episodes = data['data']['attributes']['episodes']
        
        click.echo(f"{'Episode':<50} {'Total Downloads':<15}")
        click.echo("-" * 65)
        
        for episode in episodes:
            title = episode.get('title', 'Unknown')[:47] + "..." if len(episode.get('title', '')) > 47 else episode.get('title', 'Unknown')
            total_downloads = sum(day['downloads'] for day in episode.get('downloads', []))
            click.echo(f"{title:<50} {total_downloads:<15}")
    else:
        click.echo("No episodes analytics data found")


def _print_analytics_item(item):
    """Print single analytics item"""
    attrs = item.get('attributes', {})
    click.echo(f"Analytics ID: {item.get('id', 'N/A')}")
    click.echo(f"Downloads: {attrs.get('downloads', 'N/A')}")
    click.echo(f"Date: {attrs.get('date', 'N/A')}")
    if 'country' in attrs:
        click.echo(f"Country: {attrs['country']}")
    if 'app' in attrs:
        click.echo(f"App: {attrs['app']}")
    click.echo("---")


@main.command()
@click.argument('file_path')
@click.pass_context
def upload(ctx, file_path):
    """Upload audio file"""
    if not os.path.exists(file_path):
        click.echo(f"Error: File {file_path} not found", err=True)
        return
    
    try:
        result = ctx.obj['client'].upload_audio(file_path)
        click.echo(json.dumps(result, indent=2))
    except TransistorAPIError as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.pass_context
def interactive(ctx):
    """
    Interactive mode for exploring the API
    
    Provides a command-line interface for testing API endpoints
    with simplified commands and table-formatted output.
    """
    client = ctx.obj['client']
    click.echo("Transistor API Interactive Mode")
    click.echo("Type 'help' for commands, 'quit' to exit")
    
    while True:
        try:
            cmd = click.prompt("transistor>", type=str).strip()
            
            if cmd == 'quit':
                break
            elif cmd == 'help':
                click.echo("""
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
                """)
            elif cmd == 'account':
                result = client.get_account()
                click.echo(json.dumps(result, indent=2))
            elif cmd == 'shows':
                result = client.list_shows()
                _display_shows_table(result)
            elif cmd == 'episodes':
                result = client.list_episodes()
                _display_episodes_table(result)
            elif cmd.startswith('show '):
                show_id = cmd.split(' ', 1)[1]
                result = client.get_show(show_id)
                click.echo(json.dumps(result, indent=2))
            elif cmd.startswith('episode '):
                episode_id = cmd.split(' ', 1)[1]
                result = client.get_episode(episode_id)
                click.echo(json.dumps(result, indent=2))
            elif cmd.startswith('analytics '):
                analytics_id = cmd.split(' ', 1)[1]
                result = client.get_analytics(analytics_id)
                _display_analytics_table(result)
            elif cmd.startswith('show-analytics '):
                show_id = cmd.split(' ', 1)[1]
                result = client.get_show_analytics(show_id)
                _display_analytics_table(result)
            elif cmd.startswith('episode-analytics '):
                episode_id = cmd.split(' ', 1)[1]
                result = client.get_episode_analytics(episode_id)
                _display_analytics_table(result)
            elif cmd.startswith('all-episodes '):
                show_id = cmd.split(' ', 1)[1]
                result = client.get_all_episodes_analytics(show_id)
                _display_episodes_analytics_table(result)
            else:
                click.echo("Unknown command. Type 'help' for available commands.")
                
        except TransistorAPIError as e:
            click.echo(f"Error: {e}", err=True)
        except KeyboardInterrupt:
            break
        except EOFError:
            break


def _display_shows_table(data):
    """Display shows in table format"""
    if 'data' in data:
        shows = data['data']
        click.echo(f"{'ID':<10} {'Title':<30} {'Status':<10}")
        click.echo("-" * 52)
        for show in shows:
            attrs = show.get('attributes', {})
            click.echo(f"{show.get('id', ''):<10} {attrs.get('title', ''):<30} {attrs.get('status', ''):<10}")


def _display_episodes_table(data):
    """Display episodes in table format"""
    if 'data' in data:
        episodes = data['data']
        click.echo(f"{'ID':<10} {'Title':<30} {'Status':<10}")
        click.echo("-" * 52)
        for episode in episodes:
            attrs = episode.get('attributes', {})
            click.echo(f"{episode.get('id', ''):<10} {attrs.get('title', ''):<30} {attrs.get('status', ''):<10}")


if __name__ == '__main__':
    main()
