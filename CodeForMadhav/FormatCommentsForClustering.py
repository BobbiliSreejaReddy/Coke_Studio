import json
import os
import re

def decode_unicode(text):
    """Decode unicode escaped sequences"""
    if isinstance(text, str):
        return text.encode('utf-8').decode('unicode-escape')
    return text

def clean_comment(text):
    """Clean comment text - normalize whitespace, lowercase, remove punctuation, keep all Unicode letters/numbers"""
    # Normalize whitespace
    text = ' '.join(text.split())
    # Convert to lowercase (handles all scripts reasonably for case where applicable)
    text = text.lower()
    # Remove punctuation and special symbols, but keep Unicode letters, numbers, and spaces
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    # Normalize whitespace again
    text = ' '.join(text.split())
    return text


def extract_comments_from_file(json_file):
    """Extract comments from a single JSON file. Returns tuple (kept_comments, removed_comments)"""
    kept_comments = []
    removed_comments = []
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        items = data.get('items', [])

        for item in items:
            if 'snippet' in item:
                snippet = item['snippet']

                if 'topLevelComment' in snippet:
                    comment = snippet['topLevelComment']['snippet']
                else:
                    comment = snippet

                text = comment.get('textDisplay', '')

                if text:
                    cleaned_text = clean_comment(text)
                    if len(cleaned_text.split()) >= 5:
                        kept_comments.append(cleaned_text)
                    else:
                        removed_comments.append(cleaned_text)

    except Exception as e:
        print(f"Error reading {json_file}: {e}")

    return kept_comments, removed_comments

def format_comments_from_folder(comments_folder, output_file, removed_file, country=''):
    """Format all comments from a country folder into a single text file and save removed comments separately"""

    print(f"\n{'='*70}")
    print(f"FORMATTING COMMENTS: {country}")
    print(f"{'='*70}")

    if not os.path.exists(comments_folder):
        print(f"Folder not found: {comments_folder}")
        return 0

    all_comments = []
    removed_comments = []
    video_count = 0
    file_count = 0

    for video_id in sorted(os.listdir(comments_folder)):
        video_path = os.path.join(comments_folder, video_id)

        if os.path.isdir(video_path):
            video_count += 1
            print(f"\n[{video_count}] Processing video: {video_id}")

            video_comments = 0
            for json_file in sorted(os.listdir(video_path)):
                if json_file.endswith('.json'):
                    file_count += 1
                    filepath = os.path.join(video_path, json_file)

                    kept, removed = extract_comments_from_file(filepath)
                    video_comments += len(kept)
                    all_comments.extend(kept)
                    removed_comments.extend(removed)

                    print(f"  ✓ {json_file}: {len(kept)} comments kept, {len(removed)} removed")

            print(f"  Total for video: {video_comments} comments kept")

    print(f"\n{'='*70}")
    print(f"Writing {len(all_comments):,} comments to {output_file}")
    print(f"Writing {len(removed_comments):,} removed comments to {removed_file}")
    print(f"{'='*70}")

    with open(output_file, 'w', encoding='utf-8') as f:
        for comment in all_comments:
            f.write(comment + '\n')

    with open(removed_file, 'w', encoding='utf-8') as f:
        for comment in removed_comments:
            f.write(comment + '\n')

    print(f"   Videos processed: {video_count}")
    print(f"   JSON files: {file_count}")
    print(f"   Total comments kept: {len(all_comments):,}")
    print(f"   Total comments removed: {len(removed_comments):,}")

    return len(all_comments)

if __name__ == '__main__':

    print("="*70)
    print("COMMENT FORMATTER FOR CLUSTERING")
    print("="*70)

    countries = {
        'India': 'VideoComments/IndiaComments',
        'Pakistan': 'VideoComments/PakistanComments',
        'Bangladesh': 'VideoComments/BangladeshComments'
    }

    grand_total = 0

    for country, folder in countries.items():
        output_file = f"{country}_Comments_Formatted.txt"
        removed_file = f"{country}_removed_comments.txt"
        count = format_comments_from_folder(folder, output_file, removed_file, country)
        grand_total += count

    print(f"Total comments across all countries: {grand_total:,}")
    print(f"\nGenerated files:")
    for country in countries.keys():
        print(f"  - {country}_Comments_Formatted.txt")
        print(f"  - {country}_removed_comments.txt")
