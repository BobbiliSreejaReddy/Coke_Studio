import json
import os
import re

def decode_unicode(text):
    """Decode unicode escaped sequences"""
    if isinstance(text, str):
        return text.encode('utf-8').decode('unicode-escape')
    return text

def clean_comment(text):
    """Clean comment text - remove extra whitespace and special chars"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove emojis and special unicode
    text = re.sub(r'[^\w\s\-\.\,\!\?\'\"]', '', text, flags=re.UNICODE)
    # Remove extra spaces again
    text = ' '.join(text.split())
    return text

def extract_comments_from_file(json_file):
    """Extract comments from a single JSON file"""
    comments = []
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both formats: top-level items array or nested structure
        items = data.get('items', [])
        
        for item in items:
            # Check if it's a comment thread
            if 'snippet' in item:
                snippet = item['snippet']
                
                # Get the top-level comment
                if 'topLevelComment' in snippet:
                    comment = snippet['topLevelComment']['snippet']
                else:
                    comment = snippet
                
                # Extract text
                text = comment.get('textDisplay', '')
                
                if text: 
                    cleaned_text = clean_comment(text)
                    if cleaned_text:  # Only skip if empty after cleaning
                        comments.append(cleaned_text)
    
    except Exception as e:
        print(f" Error reading {json_file}: {e}")
    
    return comments

def format_comments_from_folder(comments_folder, output_file, country=''):
    """Format all comments from a country folder into a single text file"""
    
    print(f"\n{'='*70}")
    print(f" FORMATTING COMMENTS: {country}")
    print(f"{'='*70}")
    
    if not os.path.exists(comments_folder):
        print(f" Folder not found: {comments_folder}")
        return 0
    
    all_comments = []
    video_count = 0
    file_count = 0
    
    # Process each video folder
    for video_id in sorted(os.listdir(comments_folder)):
        video_path = os.path.join(comments_folder, video_id)
        
        if os.path.isdir(video_path):
            video_count += 1
            print(f"\n[{video_count}] Processing video: {video_id}")
            
            # Process each comment JSON file for this video
            video_comments = 0
            for json_file in sorted(os.listdir(video_path)):
                if json_file.endswith('.json'):
                    file_count += 1
                    filepath = os.path.join(video_path, json_file)
                    
                    comments = extract_comments_from_file(filepath)
                    video_comments += len(comments)
                    all_comments.extend(comments)
                    
                    print(f"  ✓ {json_file}: {len(comments)} comments")
            
            print(f"  Total for video: {video_comments} comments")
    
    # Write all comments to output file
    print(f"\n{'='*70}")
    print(f" Writing {len(all_comments):,} comments to {output_file}")
    print(f"{'='*70}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for comment in all_comments:
            f.write(comment + '\n')
    
    print(f" Done!")
    print(f"   Videos processed: {video_count}")
    print(f"   JSON files: {file_count}")
    print(f"   Total comments: {len(all_comments):,}")
    
    return len(all_comments)

if __name__ == '__main__':
    
    print("="*70)
    print(" COMMENT FORMATTER FOR CLUSTERING (No Word Filter)")
    print("="*70)
    
    countries = {
        'India': 'VideoComments/IndiaComments',
        'Pakistan': 'VideoComments/PakistanComments',
        'Bangladesh': 'VideoComments/BangladeshComments'
    }
    
    grand_total = 0
    
    for country, folder in countries.items():
        output_file = f"{country}_Comments_Formatted.txt"
        count = format_comments_from_folder(folder, output_file, country)
        grand_total += count
    
    print(f"\n{'='*70}")
    print(f" ALL COMMENTS FORMATTED!")
    print(f"{'='*70}")
    print(f"Total comments across all countries: {grand_total:,}")
    print(f"\nGenerated files:")
    for country in countries.keys():
        print(f"  - {country}_all_Comments_Formatted.txt")
    print(f"\nYou can now use these files with your clustering code:")
