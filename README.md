# YouTube Channel Exporter

A Python application that exports YouTube channel statistics and video data using the official YouTube Data API v3. The app allows you to export channel information, video details, and statistics to CSV format.

## Features

- 🔍 **Channel Discovery**: Find channels by username, handle, or channel ID
- 📊 **Comprehensive Data Export**: Export video titles, view counts, likes, comments, publish dates, duration, descriptions, and tags
- ⚡ **Rate Limiting**: Configurable delays between API calls to respect YouTube's rate limits
- 📈 **Progress Tracking**: Real-time progress updates during export
- 🎯 **Batch Processing**: Efficiently process large numbers of videos
- 📁 **CSV Export**: Export data in the same format as your reference file
- 🖥️ **User-Friendly Interface**: Clean Streamlit web interface

## Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get YouTube API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create credentials (API Key)
   - Copy your API key

4. **Configure environment** (optional):
   - Copy `config.env.example` to `.env`
   - Add your API key to the `.env` file

## Usage

### Option 1: Streamlit Web Interface (Recommended)

1. **Run the Streamlit app**:
   ```bash
   streamlit run youtube_exporter.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Configure the export**:
   - Enter your YouTube API key in the sidebar
   - Enter the channel name, username, or channel ID
   - Set the number of videos to export (1-1000)
   - Configure rate limiting settings
   - Click "Export Channel Data"

### Option 2: Command Line Usage

You can also use the `YouTubeExporter` class directly in your Python scripts:

```python
from youtube_exporter import YouTubeExporter

# Initialize with your API key
exporter = YouTubeExporter("your_api_key_here")

# Get channel ID from username
channel_id = exporter.get_channel_id_from_username("username")

# Get video list
video_ids = exporter.get_channel_videos(channel_id, max_results=50)

# Get video details
videos_data = exporter.get_video_details(video_ids)

# Export to CSV
filename = exporter.export_to_csv(videos_data)
```

## Data Format

The exported CSV includes the following columns (matching your reference format):

- `title`: Video title
- `video_id`: YouTube video ID
- `url`: Full YouTube URL
- `view_count`: Number of views
- `like_count`: Number of likes
- `comment_count`: Number of comments
- `publish_date`: Publication date (YYYY-MM-DD)
- `duration_seconds`: Video duration in seconds
- `description`: Video description
- `tags`: Video tags (comma-separated)
- `transcript`: Video transcript (same as description)
- `content`: Video content (same as description)

## Rate Limiting

The app includes built-in rate limiting to respect YouTube's API quotas:

- **Default delay**: 1 second between API calls
- **Configurable**: Adjust delay from 0.1 to 10 seconds
- **Batch processing**: Process videos in batches of up to 50
- **Progress tracking**: Real-time updates on export progress

## API Quotas

YouTube Data API v3 has the following quotas:
- **Free tier**: 10,000 units per day
- **Each video search**: 100 units
- **Each video details request**: 1 unit per video
- **Each channel request**: 1 unit

For example, exporting 100 videos costs approximately 200 units (100 for search + 100 for details).

## Troubleshooting

### Common Issues

1. **"Channel not found"**:
   - Verify the channel name or ID is correct
   - Try using the full channel ID instead of username
   - Check if the channel is public

2. **"API key invalid"**:
   - Verify your API key is correct
   - Ensure YouTube Data API v3 is enabled in Google Cloud Console
   - Check if your API key has the necessary permissions

3. **"Quota exceeded"**:
   - Wait for your quota to reset (daily)
   - Reduce the number of videos to export
   - Increase the delay between API calls

### Getting Channel IDs

If you need to find a channel ID:
1. Go to the YouTube channel
2. Look at the URL: `youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx`
3. The part after `/channel/` is the channel ID

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## Disclaimer

This tool is for educational and research purposes. Please respect YouTube's Terms of Service and API usage policies when using this application.
