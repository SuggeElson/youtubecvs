"""
Example usage of the YouTube Channel Exporter
Demonstrates different ways to use the exporter programmatically
"""

from youtube_exporter import YouTubeExporter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def example_basic_export():
    """Basic example of exporting a channel's data"""
    print("=== Basic Export Example ===")
    
    # Initialize exporter with API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Please set YOUTUBE_API_KEY in your .env file")
        return
    
    exporter = YouTubeExporter(api_key)
    
    # Example channel (replace with actual channel)
    channel_username = "mkbhd"  # Marques Brownlee's channel
    
    # Get channel ID
    channel_id = exporter.get_channel_id_from_username(channel_username)
    if not channel_id:
        print(f"Channel '{channel_username}' not found")
        return
    
    # Get channel info
    channel_info = exporter.get_channel_info(channel_id)
    print(f"Channel: {channel_info.get('title', 'Unknown')}")
    print(f"Subscribers: {channel_info.get('subscriber_count', '0')}")
    
    # Get latest 10 videos
    video_ids = exporter.get_channel_videos(channel_id, max_results=10)
    print(f"Found {len(video_ids)} videos")
    
    # Get video details
    videos_data = exporter.get_video_details(video_ids)
    
    # Export to CSV
    filename = exporter.export_to_csv(videos_data, "example_export.csv")
    print(f"Exported to: {filename}")

def example_custom_processing():
    """Example of custom data processing before export"""
    print("\n=== Custom Processing Example ===")
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Please set YOUTUBE_API_KEY in your .env file")
        return
    
    exporter = YouTubeExporter(api_key)
    
    # Get videos from a channel
    channel_id = exporter.get_channel_id_from_username("mkbhd")
    if not channel_id:
        return
    
    video_ids = exporter.get_channel_videos(channel_id, max_results=20)
    videos_data = exporter.get_video_details(video_ids)
    
    # Custom filtering: Only videos with more than 1M views
    high_view_videos = [
        video for video in videos_data 
        if int(video['view_count']) > 1000000
    ]
    
    print(f"Found {len(high_view_videos)} videos with >1M views")
    
    # Export filtered data
    filename = exporter.export_to_csv(high_view_videos, "high_view_videos.csv")
    print(f"Exported filtered data to: {filename}")

def example_channel_comparison():
    """Example of comparing multiple channels"""
    print("\n=== Channel Comparison Example ===")
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Please set YOUTUBE_API_KEY in your .env file")
        return
    
    exporter = YouTubeExporter(api_key)
    
    channels = ["mkbhd", "linustechtips", "davidpakman"]
    all_data = []
    
    for channel_name in channels:
        print(f"Processing channel: {channel_name}")
        
        channel_id = exporter.get_channel_id_from_username(channel_name)
        if not channel_id:
            print(f"  Channel '{channel_name}' not found, skipping...")
            continue
        
        channel_info = exporter.get_channel_info(channel_id)
        video_ids = exporter.get_channel_videos(channel_id, max_results=5)
        videos_data = exporter.get_video_details(video_ids)
        
        # Add channel name to each video
        for video in videos_data:
            video['channel_name'] = channel_name
        
        all_data.extend(videos_data)
        print(f"  Added {len(videos_data)} videos")
    
    # Export combined data
    filename = exporter.export_to_csv(all_data, "multi_channel_comparison.csv")
    print(f"Exported {len(all_data)} videos from {len(channels)} channels to: {filename}")

if __name__ == "__main__":
    # Run examples (uncomment the ones you want to test)
    
    # Basic export example
    # example_basic_export()
    
    # Custom processing example
    # example_custom_processing()
    
    # Multi-channel comparison example
    # example_channel_comparison()
    
    print("Examples completed. Uncomment the function calls in the script to run them.")
    print("Make sure to set YOUTUBE_API_KEY in your .env file first.")
