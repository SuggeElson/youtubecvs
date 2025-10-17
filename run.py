#!/usr/bin/env python3
"""
YouTube Channel Exporter - Command Line Runner
Simple command line interface for the YouTube exporter
"""

import argparse
import sys
from youtube_exporter import YouTubeExporter

def main():
    parser = argparse.ArgumentParser(description='Export YouTube channel data to CSV')
    parser.add_argument('--api-key', required=True, help='YouTube API key')
    parser.add_argument('--channel', required=True, help='Channel username, handle, or ID')
    parser.add_argument('--max-videos', type=int, default=50, help='Maximum number of videos to export (default: 50)')
    parser.add_argument('--output', help='Output CSV filename (default: auto-generated)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between API calls in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    print("🚀 Starting YouTube Channel Export...")
    print(f"Channel: {args.channel}")
    print(f"Max videos: {args.max_videos}")
    print(f"API delay: {args.delay}s")
    print()
    
    try:
        # Initialize exporter
        exporter = YouTubeExporter(args.api_key)
        
        # Find channel ID
        print("🔍 Finding channel...")
        if args.channel.startswith('UC') and len(args.channel) == 24:
            channel_id = args.channel
        else:
            channel_id = exporter.get_channel_id_from_username(args.channel)
        
        if not channel_id:
            print("❌ Channel not found!")
            sys.exit(1)
        
        # Get channel info
        print("📊 Getting channel information...")
        channel_info = exporter.get_channel_info(channel_id)
        if channel_info:
            print(f"✅ Found: {channel_info['title']}")
            print(f"   Subscribers: {int(channel_info['subscriber_count']):,}")
            print(f"   Videos: {int(channel_info['video_count']):,}")
            print(f"   Views: {int(channel_info['view_count']):,}")
        
        # Get videos
        print("📹 Getting video list...")
        video_ids = exporter.get_channel_videos(channel_id, args.max_videos)
        print(f"📹 Found {len(video_ids)} videos")
        
        # Get video details
        print("🔍 Getting video details...")
        videos_data = exporter.get_video_details(video_ids)
        
        # Export to CSV
        print("💾 Exporting to CSV...")
        filename = exporter.export_to_csv(videos_data, args.output)
        
        print(f"✅ Export completed! Saved to: {filename}")
        print(f"📊 Exported {len(videos_data)} videos")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
