import json
import os
from pathlib import Path

def count_comments_in_file(json_file):
    """Count comments in a single JSON file"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            items = data.get('items', [])
            return len(items)
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return 0

def count_comments_in_video(video_folder):
    """Count total comments for a video (may span multiple JSON files)"""
    total = 0
    if os.path.isdir(video_folder):
        for json_file in os.listdir(video_folder):
            if json_file.endswith('.json'):
                filepath = os.path.join(video_folder, json_file)
                total += count_comments_in_file(filepath)
    return total

def count_comments_in_folder(comments_folder):
    """Count all comments in a country's comments folder"""
    total_comments = 0
    total_videos = 0
    video_stats = []
    
    if not os.path.exists(comments_folder):
        print(f"Folder not found: {comments_folder}")
        return 0, 0, []
    
    # Iterate through each video folder
    for video_id in os.listdir(comments_folder):
        video_path = os.path.join(comments_folder, video_id)
        
        if os.path.isdir(video_path):
            comment_count = count_comments_in_video(video_path)
            total_comments += comment_count
            total_videos += 1
            
            video_stats.append({
                'video_id': video_id,
                'comments': comment_count
            })
    
    return total_comments, total_videos, video_stats

if __name__ == '__main__':
    
    print("="*70)
    print("COMMENT COUNT ANALYZER")
    print("="*70)
    print()
    
    # Define countries and their comment folders
    countries = {
        'India': 'VideoComments/IndiaComments',
        'Pakistan': 'VideoComments/PakistanComments',
        'Bangladesh': 'VideoComments/BangladeshComments'
    }
    
    grand_total_comments = 0
    grand_total_videos = 0
    
    summary_data = []
    
    for country, folder in countries.items():
        print(f"🇮 {country}")
        print("-" * 70)
        
        total_comments, total_videos, video_stats = count_comments_in_folder(folder)
        
        grand_total_comments += total_comments
        grand_total_videos += total_videos
        
        if total_videos > 0:
            avg_comments = total_comments / total_videos
            print(f"  Videos with comments: {total_videos}")
            print(f"  Total comments: {total_comments:,}")
            print(f"  Average comments per video: {avg_comments:.1f}")
            
            # Find video with most comments
            if video_stats:
                max_video = max(video_stats, key=lambda x: x['comments'])
                min_video = min(video_stats, key=lambda x: x['comments'])
                
                print(f"  Max comments in one video: {max_video['comments']:,} ({max_video['video_id']})")
                print(f"  Min comments in one video: {min_video['comments']:,} ({min_video['video_id']})")
            
            summary_data.append({
                'country': country,
                'videos': total_videos,
                'comments': total_comments,
                'avg': avg_comments
            })
        else:
            print(f"  No comments downloaded yet")
            summary_data.append({
                'country': country,
                'videos': 0,
                'comments': 0,
                'avg': 0
            })
        
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()
    print(f"{'Country':<15} {'Videos':<10} {'Comments':<15} {'Avg Comments':<15}")
    print("-"*70)
    
    for data in summary_data:
        print(f"{data['country']:<15} {data['videos']:<10} {data['comments']:<15,} {data['avg']:<15.1f}")
    
    print("-"*70)
    if grand_total_videos > 0:
        grand_avg = grand_total_comments / grand_total_videos
        print(f"{'TOTAL':<15} {grand_total_videos:<10} {grand_total_comments:<15,} {grand_avg:<15.1f}")
    print()
    
    print("="*70)
