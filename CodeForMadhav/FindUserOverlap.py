import os
import json
from collections import defaultdict
import csv
from datetime import datetime

def extract_user_comments(comments_folder_path):
    """Extract all user comment data from JSON files"""
    
    user_data = defaultdict(lambda: {
        'comments': [],
        'channels': set(),
        'total_likes': 0,
        'total_comments': 0,
        'usernames': set()
    })
    
    print(f" Processing comments from {comments_folder_path}...")
    
    # Walk through all videos and JSON files
    for country_folder in os.listdir(comments_folder_path):
        country_path = os.path.join(comments_folder_path, country_folder)
        
        if not os.path.isdir(country_path):
            continue
        
        print(f"\n Country: {country_folder}")
        
        # Map folder name to channel
        if 'india' in country_folder.lower():
            channel_name = 'India'
        elif 'pakistan' in country_folder.lower():
            channel_name = 'Pakistan'
        elif 'bangladesh' in country_folder.lower():
            channel_name = 'Bangladesh'
        else:
            channel_name = country_folder
        
        video_count = 0
        
        # Process each video folder
        for video_id in os.listdir(country_path):
            video_path = os.path.join(country_path, video_id)
            
            if not os.path.isdir(video_path):
                continue
            
            video_count += 1
            
            if video_count % 100 == 0:
                print(f"  Processed {video_count} videos...")
            
            # Process each JSON file (pagination)
            for json_file in os.listdir(video_path):
                if not json_file.endswith('.json'):
                    continue
                
                json_path = os.path.join(video_path, json_file)
                
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract comments
                    for item in data.get('items', []):
                        snippet = item.get('snippet', {})
                        top_comment = snippet.get('topLevelComment', {})
                        comment_snippet = top_comment.get('snippet', {})
                        
                        # Extract user info
                        author_channel_id = comment_snippet.get('authorChannelId', {}).get('value')
                        author_name = comment_snippet.get('authorDisplayName', 'Unknown')
                        
                        if not author_channel_id:
                            continue
                        
                        # Store comment data
                        user_data[author_channel_id]['comments'].append({
                            'video_id': comment_snippet.get('videoId'),
                            'comment_id': top_comment.get('id'),
                            'text': comment_snippet.get('textDisplay'),
                            'channel': channel_name,
                            'likes': comment_snippet.get('likeCount', 0),
                            'published_at': comment_snippet.get('publishedAt'),
                            'author_name': author_name
                        })
                        
                        user_data[author_channel_id]['channels'].add(channel_name)
                        user_data[author_channel_id]['total_likes'] += comment_snippet.get('likeCount', 0)
                        user_data[author_channel_id]['total_comments'] += 1
                        user_data[author_channel_id]['usernames'].add(author_name)
                
                except json.JSONDecodeError as e:
                    print(f"    Error reading {json_file}: {e}")
        
        print(f"  Processed {video_count} videos")
    
    return user_data

def find_overlap_users(user_data, min_channels=2):
    """Find users who commented on multiple channels"""
    
    overlap_users = {}
    
    for user_id, data in user_data.items():
        num_channels = len(data['channels'])
        
        if num_channels >= min_channels:
            overlap_users[user_id] = data
    
    return overlap_users

def create_overlap_report(user_data):
    """Create detailed overlap analysis"""
    
    print("\n" + "="*80)
    print("USER OVERLAP ANALYSIS")
    print("="*80)
    print()
    
    # Categorize by number of channels
    single_channel = {uid: data for uid, data in user_data.items() if len(data['channels']) == 1}
    dual_channel = {uid: data for uid, data in user_data.items() if len(data['channels']) == 2}
    triple_channel = {uid: data for uid, data in user_data.items() if len(data['channels']) == 3}
    
    print(f"OVERLAP STATISTICS")
    print(f"{'─'*80}")
    print(f"Users on 1 channel only:   {len(single_channel):,}")
    print(f"Users on 2 channels:       {len(dual_channel):,}")
    print(f"Users on ALL 3 channels:   {len(triple_channel):,} ")
    print(f"Total unique users:        {len(user_data):,}")
    print()
    
    # Single channel breakdown
    if single_channel:
        print(f"SINGLE-CHANNEL USERS")
        print(f"{'─'*80}")
        
        channel_breakdown = defaultdict(int)
        for data in single_channel.values():
            channel = list(data['channels'])[0]
            channel_breakdown[channel] += 1
        
        for channel, count in sorted(channel_breakdown.items()):
            print(f"  {channel:15s}: {count:,} users")
        print()
    
    # Dual channel breakdown
    if dual_channel:
        print(f"DUAL-CHANNEL USERS (Commented on 2 Channels)")
        print(f"{'─'*80}")
        
        total_comments_dual = sum(data['total_comments'] for data in dual_channel.values())
        total_likes_dual = sum(data['total_likes'] for data in dual_channel.values())
        
        print(f"Count: {len(dual_channel):,}")
        print(f"Total comments: {total_comments_dual:,}")
        print(f"Total likes received: {total_likes_dual:,}")
        
        # Channel combinations
        channel_combos = defaultdict(int)
        for data in dual_channel.values():
            channels_tuple = tuple(sorted(data['channels']))
            channel_combos[channels_tuple] += 1
        
        print(f"\nChannel Combinations:")
        for combo, count in sorted(channel_combos.items(), key=lambda x: x[1], reverse=True):
            print(f"  {' + '.join(combo):30s}: {count:,} users")
        print()
    
    # Triple channel stats
    if triple_channel:
        print(f"USERS COMMENTED ON ALL 3 CHANNELS")
        print(f"{'─'*80}")
        
        total_comments_triple = sum(data['total_comments'] for data in triple_channel.values())
        total_likes_triple = sum(data['total_likes'] for data in triple_channel.values())
        avg_comments = total_comments_triple / len(triple_channel)
        avg_likes = total_likes_triple / len(triple_channel)
        
        print(f"Count: {len(triple_channel):,}")
        print(f"Total comments: {total_comments_triple:,}")
        print(f"Total likes received: {total_likes_triple:,}")
        print(f"Avg comments per user: {avg_comments:.1f}")
        print(f"Avg likes per user: {avg_likes:.1f}")
        print()
        
        # Top users by engagement
        print(f" Top 10 USERS by Engagement")
        print(f"{'─'*80}")
        
        sorted_users = sorted(
            triple_channel.items(),
            key=lambda x: x[1]['total_likes'],
            reverse=True
        )
        
        for rank, (user_id, data) in enumerate(sorted_users[:10], 1):
            username = list(data['usernames'])[0] if data['usernames'] else 'Unknown'
            print(f"{rank:2d}. {username:30s} | Comments: {data['total_comments']:3d} | Likes: {data['total_likes']:4d}")
    
    print()

def export_users_by_channel_count(user_data, channel_count, output_file):
    """Export users who commented on specific number of channels"""
    
    filtered_users = {uid: data for uid, data in user_data.items() if len(data['channels']) == channel_count}
    
    if not filtered_users:
        print(f" No users with {channel_count} channel(s)")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        header = [
            'User_ID',
            'Username',
            'Total_Comments',
            'Total_Likes',
            'Channels',
            'Comment_Count_Per_Channel',
            'Likes_Per_Channel'
        ]
        writer.writerow(header)
        
        # Write data
        for user_id, data in sorted(
            filtered_users.items(),
            key=lambda x: x[1]['total_likes'],
            reverse=True
        ):
            username = list(data['usernames'])[0] if data['usernames'] else 'Unknown'
            channels = ','.join(sorted(data['channels']))
            
            # Count per channel
            channel_counts = defaultdict(int)
            channel_likes = defaultdict(int)
            
            for comment in data['comments']:
                channel_counts[comment['channel']] += 1
                channel_likes[comment['channel']] += comment['likes']
            
            counts_str = '|'.join([
                f"{channel}:{channel_counts[channel]}"
                for channel in sorted(channel_counts.keys())
            ])
            
            likes_str = '|'.join([
                f"{channel}:{channel_likes[channel]}"
                for channel in sorted(channel_likes.keys())
            ])
            
            writer.writerow([
                user_id,
                username,
                data['total_comments'],
                data['total_likes'],
                channels,
                counts_str,
                likes_str
            ])
    
    print(f"Exported {len(filtered_users):,} users to {output_file}")

def export_detailed_comments(user_data, channel_count, output_file):
    """Export detailed comment data for users with specific channel count"""
    
    filtered_users = {uid: data for uid, data in user_data.items() if len(data['channels']) == channel_count}
    
    if not filtered_users:
        print(f"No users with {channel_count} channel(s)")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'User_ID',
            'Username',
            'Video_ID',
            'Comment_ID',
            'Comment_Text',
            'Channel',
            'Like_Count',
            'Published_At'
        ])
        
        for user_id, data in filtered_users.items():
            username = list(data['usernames'])[0] if data['usernames'] else 'Unknown'
            
            for comment in data['comments']:
                writer.writerow([
                    user_id,
                    username,
                    comment['video_id'],
                    comment['comment_id'],
                    comment['text'],
                    comment['channel'],
                    comment['likes'],
                    comment['published_at']
                ])
    
    print(f"Exported detailed comments to {output_file}")

if __name__ == '__main__':
    
    print("="*80)
    print(" FINDING USER OVERLAP ACROSS COKE STUDIO CHANNELS")
    print("="*80)
    print()
    
    # Path to comments folder
    comments_folder = "VideoComments"
    
    if not os.path.exists(comments_folder):
        print(f"Folder not found: {comments_folder}")
        print("Expected folder structure:")
        print("  VideoComments/")
        print("    IndiaComments/")
        print("    PakistanComments/")
        print("    BangladeshComments/")
        exit(1)
    
    # Extract all user data
    print("Step 1: Extracting all user comment data...")
    user_data = extract_user_comments(comments_folder)
    
    print(f"\nTotal unique users: {len(user_data):,}")
    
    # Create report
    print("\nStep 2: Analyzing engagement...")
    create_overlap_report(user_data)
    
    # Export data for all categories
    print("\nStep 3: Exporting data...")
    print()
    
    # Single channel users
    print("Exporting single-channel users...")
    export_users_by_channel_count(user_data, 1, 'single_channel_users.csv')
    export_detailed_comments(user_data, 1, 'single_channel_users_detailed.csv')
    print()
    
    # Dual channel users
    print("Exporting dual-channel users...")
    export_users_by_channel_count(user_data, 2, 'dual_channel_users.csv')
    export_detailed_comments(user_data, 2, 'dual_channel_users_detailed.csv')
    print()
    
    # Triple channel users
    print("Exporting triple-channel users...")
    export_users_by_channel_count(user_data, 3, 'triple_channel_users.csv')
    export_detailed_comments(user_data, 3, 'triple_channel_users_detailed.csv')
    print()
    
    print("="*80)
    print("USER OVERLAP ANALYSIS COMPLETE!")
    print("="*80)
    print("\n Generated files:")
    print("\n  Summary Files:")
    print("    • single_channel_users.csv")
    print("    • dual_channel_users.csv")
    print("    • triple_channel_users.csv")
    print("\n  Detailed Comment Files:")
    print("    • single_channel_users_detailed.csv")
    print("    • dual_channel_users_detailed.csv")
    print("    • triple_channel_users_detailed.csv")
    print()
