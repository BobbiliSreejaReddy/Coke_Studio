import requests
import csv
import os
import time

API_KEY_FILE = 'Key.txt'
CHANNEL_CSV = 'channel_ids.csv'

def get_api_keys():
    """Read API keys from Key.txt"""
    with open(API_KEY_FILE, 'r') as f:
        keys = [line.strip() for line in f.readlines() if line.strip()]
    if not keys:
        raise ValueError("No API keys found in Key.txt")
    return keys

def get_channel_uploads_playlist(channel_id, api_key):
    """
    Get the uploads playlist ID for a channel.
    Every YouTube channel has an 'Uploads' playlist with ID: UUxxxx (replace UC with UU)
    """
    # YouTube automatically creates uploads playlist with ID: UU + channel_id[2:]
    uploads_playlist_id = 'UU' + channel_id[2:]
    return uploads_playlist_id

def get_all_video_ids_from_playlist(playlist_id, api_key, max_results=50):
    """
    Retrieve all video IDs from a playlist using YouTube API.
    This is more complete than using Search API.
    """
    base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    
    video_ids = []
    page_token = ''
    page_count = 0
    
    while True:
        params = {
            'key': api_key,
            'playlistId': playlist_id,
            'part': 'snippet',
            'maxResults': max_results,
            'pageToken': page_token
        }
        
        try:
            response = requests.get(base_url, params=params)
            
            if response.status_code == 403:
                print(f"    API Quota exceeded")
                return video_ids, False
            
            if response.status_code != 200:
                print(f"   Error: {response.status_code}")
                return video_ids, True
            
            data = response.json()
            items = data.get('items', [])
            
            page_count += 1
            print(f"  Page {page_count}: Downloaded {len(items)} videos")
            
            for item in items:
                # Extract video ID from playlist item
                video_id = item['snippet'].get('resourceId', {}).get('videoId')
                if video_id:
                    video_ids.append(video_id)
            
            # Get next page token
            page_token = data.get('nextPageToken')
            if not page_token:
                break
            
            time.sleep(0.1)
        
        except Exception as e:
            print(f"   Exception: {e}")
            return video_ids, True
    
    return video_ids, True

def save_video_ids(video_ids, country, output_folder='ChannelVideoData'):
    """Save video IDs to file"""
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_file = os.path.join(output_folder, f'{country}_VideoIDs.txt')
    
    with open(output_file, 'w') as f:
        for vid in video_ids:
            f.write(vid + '\n')
    
    print(f"   Saved {len(video_ids)} video IDs to {output_file}\n")

def read_channel_csv(csv_file):
    """Read channel IDs from CSV"""
    channels = []
    
    try:
        # utf-8-sig removes BOM character
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                country = row.get('Country', '').strip()
                channel_id = row.get('Channel_id', '').strip()
                
                if country and channel_id:
                    channels.append((country, channel_id))
            
            return channels
    
    except Exception as e:
        print(f" Error reading CSV: {e}")
        return []

if __name__ == '__main__':
    try:
        api_keys = get_api_keys()
        print(f" Loaded {len(api_keys)} API key(s)\n")
        
        channels = read_channel_csv(CHANNEL_CSV)
        
        if not channels:
            print(" No channels found in CSV file!")
            exit(1)
        
        print(f"🔍 Found {len(channels)} channels\n")
        print("=" * 60)
        print("Using Uploads Playlist (more complete than Search API)")
        print("=" * 60)
        print()
        
        current_key_idx = 0
        
        for country, channel_id in channels:
            print(f" {country} (Channel ID: {channel_id})")
            
            # Get the uploads playlist ID
            uploads_playlist_id = get_channel_uploads_playlist(channel_id, api_keys[current_key_idx])
            print(f"  Uploads Playlist: {uploads_playlist_id}")
            
            # Fetch all videos from the uploads playlist
            video_ids, continue_flag = get_all_video_ids_from_playlist(
                uploads_playlist_id,
                api_keys[current_key_idx]
            )
            
            if not continue_flag:
                # Quota exceeded, switch API key
                if current_key_idx + 1 < len(api_keys):
                    current_key_idx += 1
                    print(f"  Switching to API key #{current_key_idx + 1}\n")
                    video_ids, _ = get_all_video_ids_from_playlist(
                        uploads_playlist_id,
                        api_keys[current_key_idx]
                    )
                else:
                    print(f"    No more API keys available\n")
                    break
            
            if video_ids:
                save_video_ids(video_ids, country)
            else:
                print(f"    No videos found\n")
        
        print("=" * 60)
        print(" All channels processed!")
        print("=" * 60)
    
    except Exception as e:
        print(f" Fatal error: {e}")
        exit(1)
