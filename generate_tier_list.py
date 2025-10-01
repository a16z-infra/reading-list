#!/usr/bin/env python3
"""
Generate a tier list graphic from the reading list entries
Split A tier into Classics and Very Good
"""

import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import yaml
import glob
import ssl
import urllib3
import random
from tqdm import tqdm

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define tier mappings - keeping classics and very_good separate
TIER_MAPPING = {
    'must_read': 'S',
    'classic': 'A_CLASSIC',
    'very_good': 'A_VERY_GOOD',
    'also_worth_reading': 'B',
    'fantasy': 'C',
    'comic': 'C',
    'non_fiction': 'C'
}

# Tier colors
TIER_COLORS = {
    'S': '#FF7F7F',  # Red
    'A_CLASSIC': '#FFBF7F',  # Orange
    'A_VERY_GOOD': '#FFBF7F',  # Orange (same as classics)
    'B': '#FFFF7F',  # Yellow
    'C': '#7FFF7F',  # Green
}

# Tier display names
TIER_NAMES = {
    'S': 'S',
    'A_CLASSIC': 'A',
    'A_VERY_GOOD': 'A',
    'B': 'B',
    'C': 'C'
}

# Tier subtitles
TIER_SUBTITLES = {
    'S': 'Must Reads',
    'A_CLASSIC': 'Classics',
    'A_VERY_GOOD': 'Very Good',
    'B': 'Worth Reading',
    'C': 'More Great Reads'
}

# Book spine colors for placeholders
BOOK_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#393b79', '#637939', '#8c6d31', '#843c39', '#7b4173',
    '#5254a3', '#6b6ecf', '#9c9ede', '#8ca252', '#b5cf6b'
]

def load_entries(entries_dir):
    """Load all entry files and organize by tier"""
    entries_by_tier = {'S': [], 'A_CLASSIC': [], 'A_VERY_GOOD': [], 'B': [], 'C': []}
    
    for entry_file in glob.glob(os.path.join(entries_dir, '*.md')):
        with open(entry_file, 'r') as f:
            content = f.read()
            
        # Parse YAML front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                    category = metadata.get('category', '')
                    tier = TIER_MAPPING.get(category, 'C')
                    
                    # Extract base filename (without extension) for cover caching
                    base_filename = os.path.splitext(os.path.basename(entry_file))[0]
                    
                    # Determine display title: book_title, then series_title (+ postfix), then author
                    book_title = metadata.get('book_title')
                    series_title = metadata.get('series_title')
                    series_postfix = metadata.get('series_postfix')
                    
                    if book_title:
                        display_title = book_title
                    elif series_title:
                        if series_postfix:
                            display_title = series_title + " " + series_postfix
                        else:
                            display_title = series_title
                    else:
                        display_title = metadata.get('author', 'Unknown')
                    
                    entry = {
                        'title': display_title,
                        'author': metadata.get('author', 'Unknown'),
                        'cover_url': metadata.get('cover_url', ''),
                        'order': metadata.get('order', 999),
                        'category': category,
                        'base_filename': base_filename
                    }
                    
                    entries_by_tier[tier].append(entry)
                except yaml.YAMLError as e:
                    print(f"Error parsing {entry_file}: {e}")
    
    # Sort entries within each tier by order
    for tier in entries_by_tier:
        entries_by_tier[tier].sort(key=lambda x: x['order'])
    
    return entries_by_tier

def create_placeholder_cover(title, author, size=(100, 150)):
    """Create a book-like placeholder image"""
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Pick a random book color
    book_color = random.choice(BOOK_COLORS)
    
    # Draw book spine and cover
    draw.rectangle([(0, 0), size], fill=book_color)
    draw.rectangle([(5, 5), (size[0]-5, size[1]-5)], fill='white')
    draw.rectangle([(10, 10), (size[0]-10, size[1]-10)], fill=book_color)
    
    # Try to load a font
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        author_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
    except:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
    
    # Write title (wrapped)
    title_lines = []
    words = title.split()
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        if bbox[2] - bbox[0] > size[0] - 25:
            if current_line:
                title_lines.append(current_line)
                current_line = word
            else:
                title_lines.append(word)
        else:
            current_line = test_line
    if current_line:
        title_lines.append(current_line)
    
    # Draw title
    y_offset = 20
    for line in title_lines[:3]:  # Max 3 lines
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        draw.text((x, y_offset), line, fill='white', font=title_font)
        y_offset += 20
    
    # Draw author at bottom
    if author and author != 'Unknown':
        author_text = author.split()[-1]  # Last name only
        bbox = draw.textbbox((0, 0), author_text, font=author_font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        draw.text((x, size[1] - 30), author_text, fill='white', font=author_font)
    
    return img

def get_extension_from_url(url):
    """Extract file extension from URL"""
    if not url:
        return '.png'  # Default extension
    # Get the path component and extract extension
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path
    # Get extension from the path
    _, ext = os.path.splitext(path)
    # If no extension found or it's not an image extension, default to .png
    if not ext or ext.lower() not in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']:
        return '.png'
    return ext.lower()

def download_cover(url, title, author, base_filename, size=(100, 150), covers_dir='_entries/covers'):
    """Download and resize book cover, with fallback to placeholder. Uses local cache if available."""
    # Create covers directory if it doesn't exist
    os.makedirs(covers_dir, exist_ok=True)
    
    # Get the expected extension from the URL
    extension = get_extension_from_url(url)
    local_cover_path = os.path.join(covers_dir, base_filename + extension)
    
    # Check if we already have a local cover
    if os.path.exists(local_cover_path):
        try:
            img = Image.open(local_cover_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail(size, Image.Resampling.LANCZOS)
            print(f"✓ Using cached cover for: {title}")
            return img
        except Exception as e:
            print(f"✗ Failed to load cached cover for {title}: {str(e)[:50]}... Re-downloading.")
    
    # Download the cover
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Try to download with proper headers and SSL handling, using streaming
        response = requests.get(url, headers=headers, timeout=10, verify=False, stream=True)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress bar
        downloaded_data = BytesIO()
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"⬇ {title[:30]}", leave=False) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded_data.write(chunk)
                    pbar.update(len(chunk))
        
        # Load and save the image
        downloaded_data.seek(0)
        img = Image.open(downloaded_data)
        
        # Save the original image to cache using the extension from the URL
        img.save(local_cover_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img.thumbnail(size, Image.Resampling.LANCZOS)
        print(f"✓ Downloaded and cached cover for: {title}")
        return img
    except Exception as e:
        print(f"✗ Failed to download cover for {title}: {str(e)[:50]}... Using placeholder.")
        return create_placeholder_cover(title, author, size)

def create_tier_list(entries_by_tier, output_file='tier_list.png'):
    """Create the tier list graphic"""
    # Configuration
    img_width = 1400
    tier_height = 200
    tier_label_width = 140
    cover_width = 100
    cover_height = 150
    padding = 10
    
    # Calculate image height
    num_tiers = len([tier for tier in entries_by_tier if entries_by_tier[tier]])
    img_height = num_tiers * tier_height + 100  # Extra space for title
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load a font (fallback to default if not available)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        tier_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        title_font = ImageFont.load_default()
        tier_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        book_font = ImageFont.load_default()
    
    # Draw title
    title = "a16z Infra Reading List - Tier List"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_width) // 2, 20), title, fill='black', font=title_font)
    
    # Draw tiers
    y_offset = 100
    for tier in ['S', 'A_CLASSIC', 'A_VERY_GOOD', 'B', 'C']:
        if not entries_by_tier[tier]:
            continue
            
        # Draw tier background
        draw.rectangle(
            [(0, y_offset), (img_width, y_offset + tier_height)],
            fill=TIER_COLORS[tier]
        )
        
        # Draw tier label with black background
        draw.rectangle(
            [(0, y_offset), (tier_label_width, y_offset + tier_height)],
            fill='black'
        )
        
        # Draw tier letter
        tier_label = TIER_NAMES[tier]
        tier_label_bbox = draw.textbbox((0, 0), tier_label, font=tier_font)
        tier_label_height = tier_label_bbox[3] - tier_label_bbox[1]
        tier_label_width_text = tier_label_bbox[2] - tier_label_bbox[0]
        draw.text(
            ((tier_label_width - tier_label_width_text) // 2, y_offset + 40),
            tier_label,
            fill='white',
            font=tier_font
        )
        
        # Draw tier subtitle
        subtitle = TIER_SUBTITLES[tier]
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(
            ((tier_label_width - subtitle_width) // 2, y_offset + 120),
            subtitle,
            fill='white',
            font=subtitle_font
        )
        
        # Draw vertical line after tier label
        draw.line(
            [(tier_label_width, y_offset), (tier_label_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        # Draw book covers and titles
        x_offset = tier_label_width + padding
        for entry in entries_by_tier[tier]:
            if x_offset + cover_width > img_width - padding:
                break  # No more room in this tier
                
            # Download and place cover
            cover = download_cover(
                entry['cover_url'], 
                entry['title'] or 'Unknown', 
                entry['author'],
                entry['base_filename'],
                (cover_width, cover_height)
            )
            cover_y = y_offset + (tier_height - cover_height) // 2
            img.paste(cover, (x_offset, cover_y))
            
            # Draw book title below cover (truncated if needed)
            title_text = entry['title'] or 'Unknown'
            if len(title_text) > 15:
                title_text = title_text[:12] + '...'
            
            text_y = y_offset + tier_height - 25
            # Add semi-transparent background for text
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + 15)],
                fill=(255, 255, 255, 200)
            )
            draw.text((x_offset, text_y), title_text, fill='black', font=book_font)
            
            x_offset += cover_width + padding
        
        # Draw horizontal line below tier
        draw.line(
            [(0, y_offset + tier_height), (img_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        y_offset += tier_height
    
    # Save image
    img.save(output_file, 'PNG')
    print(f"\nTier list saved to {output_file}")

def create_text_tier_list(entries_by_tier, output_file='tier_list.txt'):
    """Create a text version of the tier list"""
    with open(output_file, 'w') as f:
        f.write("=== a16z Infra Reading List - Tier List ===\n\n")
        
        tier_names = {
            'S': 'S Tier (Must Reads)',
            'A_CLASSIC': 'A Tier (Classics)',
            'A_VERY_GOOD': 'A Tier (Very Good)',
            'B': 'B Tier (Also Worth Reading)',
            'C': 'C Tier (Fantasy, Comics, Non-Fiction)'
        }
        
        for tier in ['S', 'A_CLASSIC', 'A_VERY_GOOD', 'B', 'C']:
            if not entries_by_tier[tier]:
                continue
                
            f.write(f"{tier_names[tier]}\n")
            f.write("=" * len(tier_names[tier]) + "\n")
            
            for entry in entries_by_tier[tier]:
                title = entry['title'] or 'Unknown'
                author = entry['author'] or 'Unknown'
                f.write(f"- {title} by {author}\n")
            
            f.write("\n")

def create_scifi_tier_list(entries_by_tier, output_file='tier_list_scifi.png'):
    """Create the sci-fi tier list graphic with full titles"""
    # Configuration
    img_width = 1400
    tier_height = 200
    tier_label_width = 200
    cover_width = 100
    cover_height = 150
    padding = 10
    
    # Only include sci-fi tiers
    scifi_tiers = ['S', 'A_CLASSIC', 'A_VERY_GOOD', 'B']
    num_tiers = len([tier for tier in scifi_tiers if entries_by_tier[tier]])
    img_height = num_tiers * tier_height + 100
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        tier_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        title_font = ImageFont.load_default()
        tier_font = ImageFont.load_default()
        book_font = ImageFont.load_default()
    
    # Full tier names for sci-fi
    tier_full_names = {
        'S': 'Must Reads',
        'A_CLASSIC': 'Classics',
        'A_VERY_GOOD': 'Very Good Books',
        'B': 'Also Worth Reading'
    }
    
    # Draw title
    title = "a16z Infra Reading List - Sci-Fi"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_width) // 2, 20), title, fill='black', font=title_font)
    
    # Draw tiers
    y_offset = 100
    for tier in scifi_tiers:
        if not entries_by_tier[tier]:
            continue
            
        # Draw tier background
        draw.rectangle(
            [(0, y_offset), (img_width, y_offset + tier_height)],
            fill=TIER_COLORS[tier]
        )
        
        # Draw tier label with black background
        draw.rectangle(
            [(0, y_offset), (tier_label_width, y_offset + tier_height)],
            fill='black'
        )
        
        # Draw tier full name (centered vertically)
        tier_name = tier_full_names[tier]
        tier_bbox = draw.textbbox((0, 0), tier_name, font=tier_font)
        tier_height_text = tier_bbox[3] - tier_bbox[1]
        tier_width_text = tier_bbox[2] - tier_bbox[0]
        draw.text(
            ((tier_label_width - tier_width_text) // 2, y_offset + (tier_height - tier_height_text) // 2),
            tier_name,
            fill='white',
            font=tier_font
        )
        
        # Draw vertical line after tier label
        draw.line(
            [(tier_label_width, y_offset), (tier_label_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        # Draw book covers
        x_offset = tier_label_width + padding
        for entry in entries_by_tier[tier]:
            if x_offset + cover_width > img_width - padding:
                break
                
            cover = download_cover(
                entry['cover_url'], 
                entry['title'] or 'Unknown', 
                entry['author'],
                entry['base_filename'],
                (cover_width, cover_height)
            )
            cover_y = y_offset + (tier_height - cover_height) // 2
            img.paste(cover, (x_offset, cover_y))
            
            # Draw book title
            title_text = entry['title'] or 'Unknown'
            if len(title_text) > 15:
                title_text = title_text[:12] + '...'
            
            text_y = y_offset + tier_height - 25
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + 15)],
                fill=(255, 255, 255, 200)
            )
            draw.text((x_offset, text_y), title_text, fill='black', font=book_font)
            
            x_offset += cover_width + padding
        
        # Draw horizontal line below tier
        draw.line(
            [(0, y_offset + tier_height), (img_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        y_offset += tier_height
    
    img.save(output_file, 'PNG')
    print(f"Sci-Fi tier list saved to {output_file}")

def create_other_categories_list(entries_by_tier, output_file='tier_list_other.png'):
    """Create the other categories list (Fantasy, Comics, Non-fiction)"""
    # Configuration
    img_width = 1400
    tier_height = 200
    tier_label_width = 200
    cover_width = 100
    cover_height = 150
    padding = 10
    
    # Category colors (red, orange, yellow)
    category_colors = {
        'fantasy': '#FF7F7F',     # Red
        'comic': '#FFBF7F',       # Orange
        'non_fiction': '#FFFF7F'  # Yellow
    }
    
    category_names = {
        'fantasy': 'Fantasy',
        'comic': 'Comic Books',
        'non_fiction': 'Non-Fiction'
    }
    
    # Organize entries by original category
    entries_by_category = {
        'fantasy': [],
        'comic': [],
        'non_fiction': []
    }
    
    for entry in entries_by_tier['C']:
        cat = entry['category']
        if cat in entries_by_category:
            entries_by_category[cat].append(entry)
    
    num_categories = len([cat for cat in entries_by_category if entries_by_category[cat]])
    img_height = num_categories * tier_height + 100
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        category_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        title_font = ImageFont.load_default()
        category_font = ImageFont.load_default()
        book_font = ImageFont.load_default()
    
    # Draw title
    title = "a16z Infra Reading List - Other Categories"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_width) // 2, 20), title, fill='black', font=title_font)
    
    # Draw categories
    y_offset = 100
    for category in ['fantasy', 'comic', 'non_fiction']:
        if not entries_by_category[category]:
            continue
            
        # Draw category background
        draw.rectangle(
            [(0, y_offset), (img_width, y_offset + tier_height)],
            fill=category_colors[category]
        )
        
        # Draw category label with black background
        draw.rectangle(
            [(0, y_offset), (tier_label_width, y_offset + tier_height)],
            fill='black'
        )
        
        # Draw category name (centered vertically)
        cat_name = category_names[category]
        cat_bbox = draw.textbbox((0, 0), cat_name, font=category_font)
        cat_height_text = cat_bbox[3] - cat_bbox[1]
        cat_width_text = cat_bbox[2] - cat_bbox[0]
        draw.text(
            ((tier_label_width - cat_width_text) // 2, y_offset + (tier_height - cat_height_text) // 2),
            cat_name,
            fill='white',
            font=category_font
        )
        
        # Draw vertical line after category label
        draw.line(
            [(tier_label_width, y_offset), (tier_label_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        # Draw book covers
        x_offset = tier_label_width + padding
        for entry in entries_by_category[category]:
            if x_offset + cover_width > img_width - padding:
                break
                
            cover = download_cover(
                entry['cover_url'], 
                entry['title'] or 'Unknown', 
                entry['author'],
                entry['base_filename'],
                (cover_width, cover_height)
            )
            cover_y = y_offset + (tier_height - cover_height) // 2
            img.paste(cover, (x_offset, cover_y))
            
            # Draw book title
            title_text = entry['title'] or 'Unknown'
            if len(title_text) > 15:
                title_text = title_text[:12] + '...'
            
            text_y = y_offset + tier_height - 25
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + 15)],
                fill=(255, 255, 255, 200)
            )
            draw.text((x_offset, text_y), title_text, fill='black', font=book_font)
            
            x_offset += cover_width + padding
        
        # Draw horizontal line below category
        draw.line(
            [(0, y_offset + tier_height), (img_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        y_offset += tier_height
    
    img.save(output_file, 'PNG')
    print(f"Other categories list saved to {output_file}")

if __name__ == '__main__':
    print("Generating tier lists...\n")
    
    # Load entries
    entries_dir = '_entries'
    entries_by_tier = load_entries(entries_dir)
    
    # Print summary
    print("\nBooks by category:")
    print(f"  S Tier (Must Reads): {len(entries_by_tier['S'])} books")
    print(f"  A Tier (Classics): {len(entries_by_tier['A_CLASSIC'])} books")
    print(f"  A Tier (Very Good): {len(entries_by_tier['A_VERY_GOOD'])} books")
    print(f"  B Tier (Also Worth Reading): {len(entries_by_tier['B'])} books")
    
    # Count by original category for C tier
    fantasy_count = sum(1 for e in entries_by_tier['C'] if e['category'] == 'fantasy')
    comic_count = sum(1 for e in entries_by_tier['C'] if e['category'] == 'comic')
    nonfiction_count = sum(1 for e in entries_by_tier['C'] if e['category'] == 'non_fiction')
    print(f"  Fantasy: {fantasy_count} books")
    print(f"  Comics: {comic_count} books")
    print(f"  Non-Fiction: {nonfiction_count} books")
    
    print("\nDownloading covers and creating tier lists...")
    
    # Create sci-fi tier list
    print("\n1. Creating Sci-Fi tier list...")
    create_scifi_tier_list(entries_by_tier, 'tier_list_scifi.png')
    
    # Create other categories list
    print("\n2. Creating Other Categories list...")
    create_other_categories_list(entries_by_tier, 'tier_list_other.png')
