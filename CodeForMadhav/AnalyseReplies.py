import os
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the base directory
base_dir = "/Users/sreejareddybobbili/Documents/CodeForMadhav/VideoComments/BangladeshComments/"

# Collect all reply counts
reply_counts = []

# Walk through all subdirectories and JSON files
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract reply counts from all comment threads
                if 'items' in data:
                    for item in data['items']:
                        if 'snippet' in item:
                            reply_count = item['snippet'].get('totalReplyCount', 0)
                            reply_counts.append(reply_count)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Create DataFrame for analysis
df = pd.DataFrame({'reply_count': reply_counts})

# Print statistics
print(f"Total comments processed: {len(reply_counts)}")
print(f"\nReply Count Statistics:")
print(f"  Mean: {df['reply_count'].mean():.2f}")
print(f"  Median: {df['reply_count'].median():.2f}")
print(f"  Std Dev: {df['reply_count'].std():.2f}")
print(f"  Min: {df['reply_count'].min()}")
print(f"  Max: {df['reply_count'].max()}")
print(f"\nReply Count Distribution:")
print(df['reply_count'].value_counts().sort_index())

# Save statistics to CSV
stats_df = pd.DataFrame({
    'reply_count': sorted(set(reply_counts)),
    'frequency': [reply_counts.count(x) for x in sorted(set(reply_counts))]
})
stats_df.to_csv('reply_counts_statistics.csv', index=False)
print("✓ Statistics saved as 'reply_counts_statistics.cs")