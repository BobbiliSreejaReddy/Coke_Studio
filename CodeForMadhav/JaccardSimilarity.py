import os
import json
from collections import defaultdict
import csv

def extract_user_sets(comments_folder_path):
    """Extract users for each channel"""
    
    channel_users = {
        'India': set(),
        'Pakistan': set(),
        'Bangladesh': set()
    }
    
    print(f" Processing comments to extract user sets...")
    
    for country_folder in os.listdir(comments_folder_path):
        country_path = os.path.join(comments_folder_path, country_folder)
        
        if not os.path.isdir(country_path):
            continue
        
        # Map folder name to channel
        if 'india' in country_folder.lower():
            channel_name = 'India'
        elif 'pakistan' in country_folder.lower():
            channel_name = 'Pakistan'
        elif 'bangladesh' in country_folder.lower():
            channel_name = 'Bangladesh'
        else:
            continue
        
        print(f"   Processing {channel_name}...")
        
        # Process each video folder
        video_count = 0
        for video_id in os.listdir(country_path):
            video_path = os.path.join(country_path, video_id)
            
            if not os.path.isdir(video_path):
                continue
            
            video_count += 1
            
            # Process each JSON file
            for json_file in os.listdir(video_path):
                if not json_file.endswith('.json'):
                    continue
                
                json_path = os.path.join(video_path, json_file)
                
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract users
                    for item in data.get('items', []):
                        snippet = item.get('snippet', {})
                        top_comment = snippet.get('topLevelComment', {})
                        comment_snippet = top_comment.get('snippet', {})
                        
                        author_channel_id = comment_snippet.get('authorChannelId', {}).get('value')
                        
                        if author_channel_id:
                            channel_users[channel_name].add(author_channel_id)
                
                except json.JSONDecodeError:
                    pass
        
        print(f"     {channel_name}: {len(channel_users[channel_name]):,} unique users from {video_count} videos")
    
    return channel_users

def calculate_jaccard_index(set1, set2):
    """
    Calculate Jaccard Index between two sets
    
    Jaccard Index = |A ∩ B| / |A ∪ B|
    
    Where:
    - A ∩ B = intersection (users in both sets)
    - A ∪ B = union (users in either set)
    
    Range: 0 to 1
    - 0 = no overlap
    - 1 = identical sets
    """
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0
    
    return intersection / union

def calculate_all_jaccard_indices(channel_users):
    """Calculate Jaccard indices for all channel pairs"""
    
    channels = list(channel_users.keys())
    jaccard_results = {}
    
    for i in range(len(channels)):
        for j in range(i+1, len(channels)):
            ch1 = channels[i]
            ch2 = channels[j]
            
            set1 = channel_users[ch1]
            set2 = channel_users[ch2]
            
            jaccard = calculate_jaccard_index(set1, set2)
            
            pair_name = f"{ch1} vs {ch2}"
            jaccard_results[pair_name] = {
                'channel1': ch1,
                'channel2': ch2,
                'jaccard_index': jaccard,
                'users_in_ch1': len(set1),
                'users_in_ch2': len(set2),
                'intersection': len(set1 & set2),
                'union': len(set1 | set2),
                'ch1_only': len(set1 - set2),
                'ch2_only': len(set2 - set1)
            }
    
    return jaccard_results

def create_jaccard_report(channel_users, jaccard_results):
    """Create detailed Jaccard Index report"""
    
    print("\n" + "="*80)
    print(" JACCARD INDEX ANALYSIS")
    print("="*80)
    print()
    
    # Channel overview
    print(" CHANNEL OVERVIEW")
    print("─"*80)
    total_unique_users = len(set().union(*channel_users.values()))
    
    for channel, users in sorted(channel_users.items()):
        print(f"  {channel:15s}: {len(users):,} unique users ({(len(users)/total_unique_users)*100:5.2f}% of total)")
    
    print(f"  {'Total Unique':15s}: {total_unique_users:,} users")
    print()
    
    # Jaccard indices
    print(" JACCARD INDEX (J = |A ∩ B| / |A ∪ B|)")
    print("─"*80)
    print("Range: 0 = No overlap, 1 = Identical audiences")
    print()
    
    for pair_name, result in sorted(jaccard_results.items()):
        jaccard = result['jaccard_index']
        
        # Interpretation
        if jaccard < 0.02:
            interpretation = " Very Low (0-2%)"
        elif jaccard < 0.05:
            interpretation = " Low (2-5%)"
        elif jaccard < 0.10:
            interpretation = " Moderate (5-10%)"
        elif jaccard < 0.20:
            interpretation = " High (10-20%)"
        else:
            interpretation = " Very High (>20%)"
        
        print(f"{pair_name}")
        print(f"  Jaccard Index:     {jaccard:.6f} ({jaccard*100:.4f}%)")
        print(f"  Interpretation:    {interpretation}")
        print(f"  ")
        print(f"  Set Details:")
        print(f"    {result['channel1']} users:       {result['users_in_ch1']:,}")
        print(f"    {result['channel2']} users:       {result['users_in_ch2']:,}")
        print(f"    Intersection (∩):  {result['intersection']:,} users in BOTH")
        print(f"    Union (∪):         {result['union']:,} users in EITHER")
        print(f"    {result['channel1']} only:        {result['ch1_only']:,}")
        print(f"    {result['channel2']} only:        {result['ch2_only']:,}")
        print()
    
    print()

def export_jaccard_results(jaccard_results, output_file):
    """Export Jaccard results to CSV"""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Channel_Pair',
            'Channel_1',
            'Channel_2',
            'Jaccard_Index',
            'Jaccard_Percentage',
            'Users_Ch1',
            'Users_Ch2',
            'Intersection',
            'Union',
            'Ch1_Only',
            'Ch2_Only'
        ])
        
        for pair_name in sorted(jaccard_results.keys()):
            result = jaccard_results[pair_name]
            
            writer.writerow([
                pair_name,
                result['channel1'],
                result['channel2'],
                f"{result['jaccard_index']:.6f}",
                f"{result['jaccard_index']*100:.4f}%",
                result['users_in_ch1'],
                result['users_in_ch2'],
                result['intersection'],
                result['union'],
                result['ch1_only'],
                result['ch2_only']
            ])
    
    print(f" Results exported to {output_file}")

if __name__ == '__main__':
    
    print("="*80)
    print(" CALCULATING JACCARD INDEX BETWEEN CHANNELS")
    print("="*80)
    print()
    
    comments_folder = "VideoComments"
    
    if not os.path.exists(comments_folder):
        print(f" Folder not found: {comments_folder}")
        exit(1)
    
    # Extract user sets for each channel
    print("Step 1: Extracting user sets for each channel...")
    channel_users = extract_user_sets(comments_folder)
    print()
    
    # Calculate Jaccard indices
    print("Step 2: Calculating Jaccard indices...")
    jaccard_results = calculate_all_jaccard_indices(channel_users)
    print()
    
    # Create report
    print("Step 3: Creating Jaccard Index report...")
    create_jaccard_report(channel_users, jaccard_results)
    
    # Export results
    print("Step 4: Exporting results...")
    export_jaccard_results(jaccard_results, 'jaccard_index.csv')
    
    print()
    print("="*80)
    print(" JACCARD INDEX ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("    • jaccard_index.csv")
