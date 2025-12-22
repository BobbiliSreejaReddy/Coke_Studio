import pandas as pd

# Load the CSV file
df = pd.read_csv('triple_channel_users_detailed.csv')

# Filter to keep only User_ID and Comment_Text
filtered_df = df[['User_ID', 'Comment_Text']]

# Save to CSV
filtered_df.to_csv('filtered_comments.csv', index=False)

print(f"Filtered dataset created with {len(filtered_df)} records")
print("\nFirst 10 rows:")
print(filtered_df.head(10))
print(f"\nFile saved as 'filtered_comments.csv'")
