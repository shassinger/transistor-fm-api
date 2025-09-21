#!/usr/bin/env python3
"""
Analytics-focused examples for Transistor API client

Demonstrates comprehensive analytics functionality including:
- Show-level analytics
- Episode-level analytics  
- All episodes analytics
- Date range filtering
- Error handling
"""

import os
from datetime import datetime, timedelta
from transistor import TransistorClient, TransistorAPIError, RateLimitError

def analytics_examples():
    """Demonstrate comprehensive analytics functionality"""
    
    # Get API key from environment
    api_key = os.getenv('TRANSISTOR_API_KEY')
    if not api_key:
        print("Error: Set TRANSISTOR_API_KEY environment variable")
        print("Get your API key from: https://dashboard.transistor.fm/account")
        return
    
    client = TransistorClient(api_key)
    
    try:
        # Get shows first to get analytics IDs
        print("=== Getting Shows for Analytics ===")
        shows = client.list_shows()
        
        if not shows.get('data'):
            print("No shows found. Create a show first.")
            return
            
        show = shows['data'][0]
        show_id = show['id']
        show_title = show['attributes']['title']
        print(f"Using show: {show_title} (ID: {show_id})")
        
        # 1. Show Analytics
        print(f"\n=== Show Analytics (Last 14 days) ===")
        show_analytics = client.get_show_analytics(show_id)
        
        downloads = show_analytics['data']['attributes']['downloads']
        total_downloads = sum(day['downloads'] for day in downloads)
        print(f"Total downloads: {total_downloads:,}")
        print(f"Date range: {show_analytics['data']['attributes']['start_date']} to {show_analytics['data']['attributes']['end_date']}")
        
        # 2. Show Analytics with Custom Date Range
        print(f"\n=== Show Analytics (Last 30 days) ===")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        show_analytics_30d = client.get_show_analytics(
            show_id,
            start_date=start_date.strftime('%d-%m-%Y'),
            end_date=end_date.strftime('%d-%m-%Y')
        )
        
        downloads_30d = show_analytics_30d['data']['attributes']['downloads']
        total_downloads_30d = sum(day['downloads'] for day in downloads_30d)
        print(f"Total downloads (30 days): {total_downloads_30d:,}")
        
        # 3. All Episodes Analytics
        print(f"\n=== All Episodes Analytics ===")
        all_episodes_analytics = client.get_all_episodes_analytics(show_id)
        
        episodes = all_episodes_analytics['data']['attributes']['episodes']
        print(f"Episodes with analytics: {len(episodes)}")
        
        # Show top 5 episodes by downloads
        episode_totals = []
        for episode in episodes:
            total = sum(day['downloads'] for day in episode['downloads'])
            episode_totals.append((episode['title'], total))
        
        episode_totals.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 5 Episodes (last 7 days):")
        for i, (title, downloads) in enumerate(episode_totals[:5], 1):
            print(f"{i}. {title[:50]}... - {downloads:,} downloads")
        
        # 4. Individual Episode Analytics
        if episodes:
            print(f"\n=== Individual Episode Analytics ===")
            episode = episodes[0]  # Get first episode
            episode_id = episode['id']
            episode_title = episode['title']
            
            print(f"Getting analytics for: {episode_title}")
            
            episode_analytics = client.get_episode_analytics(episode_id)
            
            ep_downloads = episode_analytics['data']['attributes']['downloads']
            ep_total = sum(day['downloads'] for day in ep_downloads)
            print(f"Total downloads: {ep_total:,}")
            
            # Show daily breakdown
            print("Daily breakdown:")
            for day in ep_downloads[-7:]:  # Last 7 days
                print(f"  {day['date']}: {day['downloads']:,} downloads")
        
        # 5. Historical Analytics (from oldest available data)
        print(f"\n=== Historical Analytics (from Jan 1, 2022) ===")
        historical_analytics = client.get_show_analytics(
            show_id,
            start_date='01-01-2022',
            end_date=datetime.now().strftime('%d-%m-%Y')
        )
        
        historical_downloads = historical_analytics['data']['attributes']['downloads']
        historical_total = sum(day['downloads'] for day in historical_downloads)
        print(f"Total historical downloads: {historical_total:,}")
        print(f"Data available from: {historical_analytics['data']['attributes']['start_date']}")
        
    except RateLimitError:
        print("Rate limit exceeded. Wait 10 seconds and try again.")
    except TransistorAPIError as e:
        print(f"API Error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status Code: {e.status_code}")

def analytics_summary_report():
    """Generate a comprehensive analytics summary report"""
    
    api_key = os.getenv('TRANSISTOR_API_KEY')
    if not api_key:
        print("Set TRANSISTOR_API_KEY environment variable")
        return
    
    client = TransistorClient(api_key)
    
    try:
        shows = client.list_shows()
        
        for show in shows['data']:
            show_id = show['id']
            show_title = show['attributes']['title']
            
            print(f"\n{'='*60}")
            print(f"ANALYTICS REPORT: {show_title}")
            print(f"{'='*60}")
            
            # Get all episodes analytics for comprehensive view
            all_episodes = client.get_all_episodes_analytics(show_id)
            episodes = all_episodes['data']['attributes']['episodes']
            
            # Calculate totals
            total_downloads = 0
            episodes_with_downloads = 0
            
            for episode in episodes:
                ep_downloads = sum(day['downloads'] for day in episode['downloads'])
                total_downloads += ep_downloads
                if ep_downloads > 0:
                    episodes_with_downloads += 1
            
            print(f"Total Episodes: {len(episodes)}")
            print(f"Episodes with Downloads: {episodes_with_downloads}")
            print(f"Total Downloads (last 7 days): {total_downloads:,}")
            print(f"Average Downloads per Episode: {total_downloads / len(episodes) if episodes else 0:.1f}")
            
            # Show date range
            date_range = all_episodes['data']['attributes']
            print(f"Date Range: {date_range['start_date']} to {date_range['end_date']}")
            
    except TransistorAPIError as e:
        print(f"Error generating report: {e}")

if __name__ == '__main__':
    print("Transistor.fm Analytics Examples")
    print("================================")
    
    # Run comprehensive analytics examples
    analytics_examples()
    
    # Generate summary report
    print("\n" + "="*60)
    analytics_summary_report()
