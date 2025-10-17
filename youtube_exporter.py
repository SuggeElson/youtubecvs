import os
import time
import csv
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeExporter:
    def __init__(self, api_key: str):
        """Initialize YouTube API client"""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
    def get_channel_id_from_username(self, username: str) -> Optional[str]:
        """Get channel ID from username or handle"""
        try:
            # Remove @ symbol if present
            username = username.lstrip('@')
            
            # Try to get channel by username
            search_response = self.youtube.channels().list(
                part='id',
                forUsername=username
            ).execute()
            
            if 'items' in search_response and search_response['items']:
                return search_response['items'][0]['id']
            
            # If username search fails, try search API
            search_response = self.youtube.search().list(
                part='snippet',
                q=username,
                type='channel',
                maxResults=1
            ).execute()
            
            if 'items' in search_response and search_response['items']:
                return search_response['items'][0]['snippet']['channelId']
                
        except HttpError as e:
            st.error(f"Error finding channel: {e}")
            
        return None
    
    def get_channel_info(self, channel_id: str) -> Dict:
        """Get basic channel information"""
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
            
            if 'items' in response and response['items']:
                channel = response['items'][0]
                return {
                    'title': channel['snippet']['title'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', '0'),
                    'video_count': channel['statistics'].get('videoCount', '0'),
                    'view_count': channel['statistics'].get('viewCount', '0')
                }
            else:
                st.error(f"No channel found with ID: {channel_id}")
        except HttpError as e:
            st.error(f"Error getting channel info: {e}")
            
        return {}
    
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[str]:
        """Get list of video IDs from channel"""
        video_ids = []
        next_page_token = None
        
        try:
            while len(video_ids) < max_results:
                # Calculate how many videos to fetch in this request
                remaining = max_results - len(video_ids)
                request_max = min(50, remaining)  # YouTube API max is 50 per request
                
                # Get videos from channel
                search_response = self.youtube.search().list(
                    part='id',
                    channelId=channel_id,
                    type='video',
                    order='date',  # Get newest videos first
                    maxResults=request_max,
                    pageToken=next_page_token
                ).execute()
                
                # Extract video IDs
                if 'items' in search_response and search_response['items']:
                    for item in search_response['items']:
                        video_ids.append(item['id']['videoId'])
                else:
                    st.warning(f"No videos found for channel {channel_id}")
                    break
                
                # Check if there are more pages
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except HttpError as e:
            st.error(f"Error getting channel videos: {e}")
            
        return video_ids[:max_results]
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get detailed information for a list of videos"""
        videos_data = []
        
        # Process videos in batches of 50 (YouTube API limit)
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            try:
                # Get video details
                videos_response = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch_ids)
                ).execute()
                
                if 'items' in videos_response and videos_response['items']:
                    for video in videos_response['items']:
                        video_data = self._process_video_data(video)
                        videos_data.append(video_data)
                else:
                    st.warning(f"No video details found for batch: {batch_ids}")
                    
            except HttpError as e:
                st.error(f"Error getting video details: {e}")
                
        return videos_data
    
    def _process_video_data(self, video: Dict) -> Dict:
        """Process individual video data to match CSV format"""
        snippet = video['snippet']
        statistics = video['statistics']
        content_details = video['contentDetails']
        
        # Parse duration (ISO 8601 format)
        duration = self._parse_duration(content_details['duration'])
        
        # Format publish date
        publish_date = snippet['publishedAt'][:10]  # YYYY-MM-DD format
        
        # Get tags
        tags = ','.join(snippet.get('tags', [])) if snippet.get('tags') else ''
        
        # Clean description and transcript (they're the same in this case)
        description = snippet.get('description', '').replace('\n', ' ')
        transcript = description  # Using description as transcript
        
        return {
            'title': snippet['title'],
            'video_id': video['id'],
            'url': f"https://www.youtube.com/watch?v={video['id']}",
            'view_count': statistics.get('viewCount', '0'),
            'like_count': statistics.get('likeCount', '0'),
            'comment_count': statistics.get('commentCount', '0'),
            'publish_date': publish_date,
            'duration_seconds': duration,
            'description': description,
            'tags': tags,
            'transcript': transcript,
            'content': description  # Using description as content
        }
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        # Remove PT prefix
        duration = duration.replace('PT', '')
        
        total_seconds = 0
        
        # Parse hours
        if 'H' in duration:
            hours = int(re.search(r'(\d+)H', duration).group(1))
            total_seconds += hours * 3600
            
        # Parse minutes
        if 'M' in duration:
            minutes = int(re.search(r'(\d+)M', duration).group(1))
            total_seconds += minutes * 60
            
        # Parse seconds
        if 'S' in duration:
            seconds = int(re.search(r'(\d+)S', duration).group(1))
            total_seconds += seconds
            
        return total_seconds
    
    def test_api_connection(self) -> bool:
        """Test if the API key works by making a simple request"""
        try:
            # Try to search for a popular term to test API
            test_response = self.youtube.search().list(
                part='snippet',
                q='test',
                type='video',
                maxResults=1
            ).execute()
            
            if 'items' in test_response:
                return True
            else:
                st.error("API test failed: No items in response")
                return False
                
        except HttpError as e:
            if e.resp.status == 403:
                st.error("❌ API Key Error: The provided API key is invalid or has insufficient permissions.")
                st.info("💡 Please check your API key and ensure YouTube Data API v3 is enabled.")
            elif e.resp.status == 400:
                st.error("❌ API Error: Bad request. Please check your input.")
            else:
                st.error(f"❌ API Error: {e}")
            return False
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return False

    def export_to_csv(self, videos_data: List[Dict], filename: str = None) -> str:
        """Export videos data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_export_{timestamp}.csv"
        
        # Define CSV columns in the same order as the reference file
        fieldnames = [
            'title', 'video_id', 'url', 'view_count', 'like_count', 
            'comment_count', 'publish_date', 'duration_seconds', 
            'description', 'tags', 'transcript', 'content'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(videos_data)
        
        return filename

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="YouTube Channel Exporter",
        page_icon="📺",
        layout="wide"
    )
    
    st.title("📺 YouTube Channel Exporter")
    st.markdown("Export channel statistics and video data using the YouTube Data API")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "YouTube API Key",
        value=os.getenv('YOUTUBE_API_KEY', ''),
        type="password",
        help="Get your API key from Google Cloud Console"
    )
    
    if not api_key:
        st.warning("⚠️ Please enter your YouTube API key in the sidebar")
        st.markdown("""
        ### How to get your YouTube API Key:
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Enable YouTube Data API v3
        4. Create credentials (API Key)
        5. Copy the API key and paste it above
        """)
        return
    
    # Initialize exporter
    exporter = YouTubeExporter(api_key)
    
    # Test API connection
    if st.sidebar.button("🔧 Test API Connection"):
        with st.spinner("Testing API connection..."):
            if exporter.test_api_connection():
                st.sidebar.success("✅ API connection successful!")
            else:
                st.sidebar.error("❌ API connection failed!")
    
    # Channel input
    st.header("Channel Configuration")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        channel_input = st.text_input(
            "Channel (Username, Handle, or Channel ID)",
            placeholder="e.g., @username, username, or UCxxxxxxxxxxxxxxxxxxxxxx",
            help="Enter channel username (with or without @), handle, or full channel ID"
        )
    
    with col2:
        max_videos = st.number_input(
            "Number of Videos",
            min_value=1,
            max_value=1000,
            value=50,
            help="Maximum number of recent videos to export"
        )
    
    # Rate limiting configuration
    st.header("Rate Limiting")
    col1, col2 = st.columns(2)
    
    with col1:
        delay_between_calls = st.number_input(
            "Delay between API calls (seconds)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Pause between API requests to respect rate limits"
        )
    
    with col2:
        batch_size = st.number_input(
            "Batch size for video details",
            min_value=1,
            max_value=50,
            value=50,
            help="Number of videos to process in each batch"
        )
    
    # Export button
    if st.button("🚀 Export Channel Data", type="primary"):
        if not channel_input:
            st.error("Please enter a channel name or ID")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Find channel ID
            status_text.text("🔍 Finding channel...")
            progress_bar.progress(10)
            
            # Check if input is already a channel ID
            if channel_input.startswith('UC') and len(channel_input) == 24:
                channel_id = channel_input
                st.info(f"Using provided channel ID: {channel_id}")
            else:
                st.info(f"Searching for channel: {channel_input}")
                channel_id = exporter.get_channel_id_from_username(channel_input)
            
            if not channel_id:
                st.error("❌ Channel not found. Please check the channel name or ID.")
                st.info("💡 Try using the full channel ID (starts with UC) or check if the channel is public.")
                return
            
            st.success(f"✅ Found channel ID: {channel_id}")
            
            # Step 2: Get channel info
            status_text.text("📊 Getting channel information...")
            progress_bar.progress(20)
            
            channel_info = exporter.get_channel_info(channel_id)
            
            if channel_info:
                st.success(f"✅ Found channel: **{channel_info['title']}**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Subscribers", f"{int(channel_info['subscriber_count']):,}")
                with col2:
                    st.metric("Videos", f"{int(channel_info['video_count']):,}")
                with col3:
                    st.metric("Total Views", f"{int(channel_info['view_count']):,}")
                with col4:
                    st.metric("Exporting", f"{min(max_videos, int(channel_info['video_count'])):,}")
            
            # Step 3: Get video list
            status_text.text("📹 Getting video list...")
            progress_bar.progress(30)
            
            video_ids = exporter.get_channel_videos(channel_id, max_videos)
            
            if not video_ids:
                st.error("❌ No videos found for this channel")
                return
            
            st.info(f"📹 Found {len(video_ids)} videos to process")
            
            # Step 4: Get video details in batches
            status_text.text("🔍 Getting video details...")
            progress_bar.progress(40)
            
            all_videos_data = []
            total_batches = (len(video_ids) + batch_size - 1) // batch_size
            
            for i in range(0, len(video_ids), batch_size):
                batch_video_ids = video_ids[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                status_text.text(f"🔍 Processing batch {batch_num}/{total_batches}...")
                
                batch_data = exporter.get_video_details(batch_video_ids)
                all_videos_data.extend(batch_data)
                
                # Update progress
                progress = 40 + (batch_num / total_batches) * 50
                progress_bar.progress(int(progress))
                
                # Delay between batches
                if i + batch_size < len(video_ids):
                    time.sleep(delay_between_calls)
            
            # Step 5: Export to CSV
            status_text.text("💾 Exporting to CSV...")
            progress_bar.progress(90)
            
            filename = exporter.export_to_csv(all_videos_data)
            
            progress_bar.progress(100)
            status_text.text("✅ Export completed!")
            
            # Display results
            st.success(f"🎉 Successfully exported {len(all_videos_data)} videos to **{filename}**")
            
            # Show preview
            st.header("📊 Data Preview")
            df = pd.DataFrame(all_videos_data)
            st.dataframe(df[['title', 'view_count', 'like_count', 'publish_date', 'duration_seconds']], use_container_width=True)
            
            # Download button
            with open(filename, 'rb') as file:
                st.download_button(
                    label="📥 Download CSV File",
                    data=file.read(),
                    file_name=filename,
                    mime="text/csv"
                )
            
        except Exception as e:
            st.error(f"❌ Error during export: {str(e)}")
            status_text.text("❌ Export failed")

if __name__ == "__main__":
    main()
