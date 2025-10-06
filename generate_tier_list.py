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
    'S': 'Must Reads\n(S tier)',
    'A_CLASSIC': 'Classics\n(A tier)',
    'A_VERY_GOOD': 'Very Good\n(A tier)',
    'B': 'Worth Reading\n(B tier)',
    'C': 'More Great Reads\n(C tier)'
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
                    
                    # Determine display title: book_title, then series_title, then author
                    book_title = metadata.get('book_title')
                    series_title = metadata.get('series_title')
                    series_postfix = metadata.get('series_postfix')
                    author = metadata.get('author', 'Unknown')
                    
                    if book_title:
                        display_title = book_title
                        title_prefix = ""
                    elif series_title:
                        display_title = "Series: " + series_title
                        title_prefix = "Series: "
                    else:
                        display_title = "Author: " + author
                        title_prefix = "Author: "
                    
                    entry = {
                        'title': display_title,
                        'author': author,
                        'series_title': series_title,
                        'series_postfix': series_postfix,
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

def create_placeholder_cover(title, author, size=(250, 375)):
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

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width, returning list of lines"""
    # First split by explicit newlines
    paragraphs = text.split('\n')
    lines = []
    
    for paragraph in paragraphs:
        words = paragraph.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            # Create a temporary image to measure text
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
    
    return lines

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

def download_cover(url, title, author, base_filename, size=(250, 375), covers_dir='_entries/covers'):
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
            
            # Scale to fill the target size while maintaining aspect ratio
            img_ratio = img.width / img.height
            target_ratio = size[0] / size[1]
            
            if img_ratio > target_ratio:
                # Image is wider, scale to match height
                new_height = size[1]
                new_width = int(new_height * img_ratio)
            else:
                # Image is taller, scale to match width
                new_width = size[0]
                new_height = int(new_width / img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop to exact size if needed
            if img.width > size[0] or img.height > size[1]:
                left = (img.width - size[0]) // 2
                top = (img.height - size[1]) // 2
                img = img.crop((left, top, left + size[0], top + size[1]))
            
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
        
        # Scale to fill the target size while maintaining aspect ratio
        img_ratio = img.width / img.height
        target_ratio = size[0] / size[1]
        
        if img_ratio > target_ratio:
            # Image is wider, scale to match height
            new_height = size[1]
            new_width = int(new_height * img_ratio)
        else:
            # Image is taller, scale to match width
            new_width = size[0]
            new_height = int(new_width / img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop to exact size if needed
        if img.width > size[0] or img.height > size[1]:
            left = (img.width - size[0]) // 2
            top = (img.height - size[1]) // 2
            img = img.crop((left, top, left + size[0], top + size[1]))
        
        print(f"✓ Downloaded and cached cover for: {title}")
        return img
    except Exception as e:
        print(f"✗ Failed to download cover for {title}: {str(e)[:50]}... Using placeholder.")
        return create_placeholder_cover(title, author, size)

def create_tier_list(entries_by_tier, output_file='tier_list.png'):
    """Create the tier list graphic"""
    # Configuration
    tier_height = 420
    tier_label_width = 180
    cover_width = 250
    cover_height = 375
    padding = 15
    
    # Calculate image dimensions based on content
    num_tiers = len([tier for tier in entries_by_tier if entries_by_tier[tier]])
    img_height = num_tiers * tier_height + 100  # Extra space for title
    
    # Calculate width based on the tier with the most books
    max_books_in_tier = max(len(entries_by_tier[tier]) for tier in entries_by_tier if entries_by_tier[tier])
    img_width = tier_label_width + (max_books_in_tier * (cover_width + padding)) + padding
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load a font (fallback to default if not available)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
        tier_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
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
        
        # Draw tier subtitle with word wrapping
        subtitle = TIER_SUBTITLES[tier]
        wrapped_subtitle_lines = wrap_text(subtitle, subtitle_font, tier_label_width - 20)
        
        # Draw each line centered horizontally
        subtitle_y = y_offset + 160
        for line in wrapped_subtitle_lines:
            line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text(
                ((tier_label_width - line_width) // 2, subtitle_y),
                line,
                fill='white',
                font=subtitle_font
            )
            subtitle_y += 30
        
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
            
            # Draw book title below cover with word wrapping
            title_text = entry['title'] or 'Unknown'
            wrapped_lines = wrap_text(title_text, book_font, cover_width - 4)
            
            # Limit to 2 lines max
            if len(wrapped_lines) > 2:
                wrapped_lines = wrapped_lines[:2]
                # Add ellipsis to last line if truncated
                wrapped_lines[1] = wrapped_lines[1][:20] + '...' if len(wrapped_lines[1]) > 20 else wrapped_lines[1]
            
            # Calculate text background height
            line_height = 24
            text_bg_height = len(wrapped_lines) * line_height + 6
            text_y = y_offset + tier_height - text_bg_height
            
            # Add semi-transparent background for text
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + text_bg_height)],
                fill=(255, 255, 255, 200)
            )
            
            # Draw each line
            current_y = text_y
            for line in wrapped_lines:
                draw.text((x_offset, current_y), line, fill='black', font=book_font)
                current_y += line_height
            
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
    tier_height = 420
    tier_label_width = 240
    cover_width = 250
    cover_height = 375
    padding = 15
    
    # Only include sci-fi tiers
    scifi_tiers = ['S', 'A_CLASSIC', 'A_VERY_GOOD', 'B']
    num_tiers = len([tier for tier in scifi_tiers if entries_by_tier[tier]])
    img_height = num_tiers * tier_height + 100
    
    # Calculate width based on the tier with the most books
    max_books_in_tier = max(len(entries_by_tier[tier]) for tier in scifi_tiers if entries_by_tier[tier])
    img_width = tier_label_width + (max_books_in_tier * (cover_width + padding)) + padding
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
        tier_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        title_font = ImageFont.load_default()
        tier_font = ImageFont.load_default()
        book_font = ImageFont.load_default()
    
    # Full tier names for sci-fi
    tier_full_names = {
        'S': 'Must Reads\n(S tier)',
        'A_CLASSIC': 'Classics\n(A tier)',
        'A_VERY_GOOD': 'Very Good\n(A tier)',
        'B': 'Also Worth Reading\n(B tier)'
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
        
        # Draw tier full name with word wrapping (centered vertically)
        tier_name = tier_full_names[tier]
        wrapped_tier_lines = wrap_text(tier_name, tier_font, tier_label_width - 20)
        
        # Calculate total height of wrapped text
        line_height = 42
        total_text_height = len(wrapped_tier_lines) * line_height
        start_y = y_offset + (tier_height - total_text_height) // 2
        
        # Draw each line centered horizontally
        current_y = start_y
        for line in wrapped_tier_lines:
            line_bbox = draw.textbbox((0, 0), line, font=tier_font)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text(
                ((tier_label_width - line_width) // 2, current_y),
                line,
                fill='white',
                font=tier_font
            )
            current_y += line_height
        
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
            
            # Draw book title with word wrapping
            title_text = entry['title'] or 'Unknown'
            wrapped_lines = wrap_text(title_text, book_font, cover_width - 4)
            
            # Limit to 2 lines max
            if len(wrapped_lines) > 2:
                wrapped_lines = wrapped_lines[:2]
                # Add ellipsis to last line if truncated
                wrapped_lines[1] = wrapped_lines[1][:20] + '...' if len(wrapped_lines[1]) > 20 else wrapped_lines[1]
            
            # Calculate text background height
            line_height = 24
            text_bg_height = len(wrapped_lines) * line_height + 6
            text_y = y_offset + tier_height - text_bg_height
            
            # Add semi-transparent background for text
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + text_bg_height)],
                fill=(255, 255, 255, 200)
            )
            
            # Draw each line
            current_y = text_y
            for line in wrapped_lines:
                draw.text((x_offset, current_y), line, fill='black', font=book_font)
                current_y += line_height
            
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
    tier_height = 420
    tier_label_width = 240
    cover_width = 250
    cover_height = 375
    padding = 15
    
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
    
    # Calculate width based on the category with the most books
    max_books_in_category = max(len(entries_by_category[cat]) for cat in entries_by_category if entries_by_category[cat])
    img_width = tier_label_width + (max_books_in_category * (cover_width + padding)) + padding
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
        category_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
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
        
        # Draw category name with word wrapping (centered vertically)
        cat_name = category_names[category]
        wrapped_cat_lines = wrap_text(cat_name, category_font, tier_label_width - 20)
        
        # Calculate total height of wrapped text
        line_height = 42
        total_text_height = len(wrapped_cat_lines) * line_height
        start_y = y_offset + (tier_height - total_text_height) // 2
        
        # Draw each line centered horizontally
        current_y = start_y
        for line in wrapped_cat_lines:
            line_bbox = draw.textbbox((0, 0), line, font=category_font)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text(
                ((tier_label_width - line_width) // 2, current_y),
                line,
                fill='white',
                font=category_font
            )
            current_y += line_height
        
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
            
            # Draw book title with word wrapping
            title_text = entry['title'] or 'Unknown'
            wrapped_lines = wrap_text(title_text, book_font, cover_width - 4)
            
            # Limit to 2 lines max
            if len(wrapped_lines) > 2:
                wrapped_lines = wrapped_lines[:2]
                # Add ellipsis to last line if truncated
                wrapped_lines[1] = wrapped_lines[1][:20] + '...' if len(wrapped_lines[1]) > 20 else wrapped_lines[1]
            
            # Calculate text background height
            line_height = 24
            text_bg_height = len(wrapped_lines) * line_height + 6
            text_y = y_offset + tier_height - text_bg_height
            
            # Add semi-transparent background for text
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + text_bg_height)],
                fill=(255, 255, 255, 200)
            )
            
            # Draw each line
            current_y = text_y
            for line in wrapped_lines:
                draw.text((x_offset, current_y), line, fill='black', font=book_font)
                current_y += line_height
            
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

def create_authors_tier_list(entries_by_tier, output_file='tier_list_authors.png'):
    """Create an authors-only tier list (no series/book titles)"""
    # Configuration
    tier_height = 480
    tier_label_width = 240
    cover_width = 250
    cover_height = 375
    padding = 15
    
    # Only include sci-fi tiers
    scifi_tiers = ['S', 'A_CLASSIC', 'A_VERY_GOOD', 'B']
    num_tiers = len([tier for tier in scifi_tiers if entries_by_tier[tier]])
    img_height = num_tiers * tier_height + 100
    
    # Calculate width based on the tier with the most books
    max_books_in_tier = max(len(entries_by_tier[tier]) for tier in scifi_tiers if entries_by_tier[tier])
    img_width = tier_label_width + (max_books_in_tier * (cover_width + padding)) + padding
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
        tier_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        book_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        title_font = ImageFont.load_default()
        tier_font = ImageFont.load_default()
        book_font = ImageFont.load_default()
    
    # Full tier names for sci-fi
    tier_full_names = {
        'S': 'Must Reads\n(S tier)',
        'A_CLASSIC': 'Classics\n(A tier)',
        'A_VERY_GOOD': 'Very Good\n(A tier)',
        'B': 'Also Worth Reading\n(B tier)'
    }
    
    # Draw title
    title = "a16z Infra Reading List - Authors"
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
        
        # Draw tier full name with word wrapping (centered vertically)
        tier_name = tier_full_names[tier]
        wrapped_tier_lines = wrap_text(tier_name, tier_font, tier_label_width - 20)
        
        # Calculate total height of wrapped text
        line_height = 42
        total_text_height = len(wrapped_tier_lines) * line_height
        start_y = y_offset + (tier_height - total_text_height) // 2
        
        # Draw each line centered horizontally
        current_y = start_y
        for line in wrapped_tier_lines:
            line_bbox = draw.textbbox((0, 0), line, font=tier_font)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text(
                ((tier_label_width - line_width) // 2, current_y),
                line,
                fill='white',
                font=tier_font
            )
            current_y += line_height
        
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
            # Top-align all covers in the tier row
            gap = 5
            vertical_padding = 20  # Space from top of tier row
            cover_y = y_offset + vertical_padding
            
            img.paste(cover, (x_offset, cover_y))
            
            # Draw author name and series (if available)
            author_text = entry['author'] or 'Unknown'
            series_title = entry.get('series_title')
            series_postfix = entry.get('series_postfix')
            
            # Build list of text elements to draw
            text_elements = []
            
            # Add author name
            author_lines = wrap_text(author_text, book_font, cover_width - 4)
            # Limit author to 1 line
            if len(author_lines) > 1:
                author_lines = author_lines[:1]
            for line in author_lines:
                text_elements.append({'text': line, 'font': book_font, 'height': 24})
            
            # Add series name if present (same font as author)
            if series_title:
                series_text = series_title
                if series_postfix:
                    series_text += " " + series_postfix
                series_lines = wrap_text(series_text, book_font, cover_width - 4)
                # Allow up to 2 lines for series (total of 3 lines with author)
                remaining_lines = 3 - len(text_elements)
                if len(series_lines) > remaining_lines:
                    series_lines = series_lines[:remaining_lines]
                    # Add ellipsis to last line if truncated
                    if series_lines and len(series_lines[-1]) > 20:
                        series_lines[-1] = series_lines[-1][:20] + '...'
                for line in series_lines:
                    text_elements.append({'text': line, 'font': book_font, 'height': 24})
            
            # Top-align all captions at the same position below covers
            text_bg_height = sum(elem['height'] for elem in text_elements) + 6
            text_y = cover_y + cover_height + gap
            
            # Add semi-transparent background for text
            draw.rectangle(
                [(x_offset - 2, text_y - 2), (x_offset + cover_width + 2, text_y + text_bg_height)],
                fill=(255, 255, 255, 200)
            )
            
            # Draw each line
            current_y = text_y
            for elem in text_elements:
                draw.text((x_offset, current_y), elem['text'], fill='black', font=elem['font'])
                current_y += elem['height']
            
            x_offset += cover_width + padding
        
        # Draw horizontal line below tier
        draw.line(
            [(0, y_offset + tier_height), (img_width, y_offset + tier_height)],
            fill='black',
            width=3
        )
        
        y_offset += tier_height
    
    img.save(output_file, 'PNG')
    print(f"Authors tier list saved to {output_file}")

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
    
    # Create authors tier list
    print("\n3. Creating Authors tier list...")
    create_authors_tier_list(entries_by_tier, 'tier_list_authors.png')
