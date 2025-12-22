import csv
import sys

try:
    print("Reading CSV...")
    
    # Read with UTF-16 encoding
    with open('Djokovic.CSV', 'r', encoding='utf-16') as csvfile:
        reader = csv.reader(csvfile)
        
        # Write video IDs to a new file
        with open('VideoIDs.txt', 'w') as outfile:
            for i, row in enumerate(reader):
                # Skip empty rows
                if not row or len(row) < 2:
                    print(f"Skipping row {i}: {row}")
                    continue
                
                url_path = row[1].strip()  # Get URL path and remove whitespace
                
                video_id = None
                
                # Check for regular video format: /watch?v=VIDEO_ID
                if 'v=' in url_path:
                    try:
                        video_id = url_path.split('v=')[1]  # Get part after 'v='
                        video_id = video_id.split('&')[0]   # Remove parameters after &
                    except Exception as e:
                        print(f"✗ Row {i}: Error extracting regular video ID - {e}")
                
                # Check for YouTube Shorts format: /shorts/VIDEO_ID
                elif '/shorts/' in url_path:
                    try:
                        video_id = url_path.split('/shorts/')[1]  # Get part after '/shorts/'
                        video_id = video_id.split('&')[0]         # Remove parameters after &
                    except Exception as e:
                        print(f"✗ Row {i}: Error extracting shorts ID - {e}")
                
                else:
                    print(f"✗ Row {i}: Unknown URL format: {url_path}")
                    continue
                
                # Write the video ID if we extracted one
                if video_id:
                    outfile.write(video_id + '\n')
                    print(f"✓ Extracted: {video_id}")
                else:
                    print(f"✗ Row {i}: Video ID is empty")

    print("\n✅ Video IDs extracted to VideoIDs.txt")

except FileNotFoundError:
    print("❌ Error: CSV not found!")
    print("Make sure you ran Step 1 first (DownloadVideoURLsFromSearchQuery.py)")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
