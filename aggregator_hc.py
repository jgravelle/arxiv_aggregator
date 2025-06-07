# aggregator_hc.py - arXiv aggregator for Human-Computer Interaction research
import os
import json
import feedparser
import requests
import ftplib
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from config import (
    SEEN_IDS_FILE,
    FTP_HOST,
    FTP_USER,
    FTP_PASS,
    FTP_REMOTE_DIR,
    UNSPLASH_ACCESS_KEY,
    UNSPLASH_API_URL,
)
from generate_html import generate_html
from content_utils import log, rewrite_title, rewrite_blurb, generate_search_keywords
from featured_tracker import select_featured_article

# ArXiv API URL for fetching recent cs.HC papers (Human-Computer Interaction)
ARXIV_HC_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.HC&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending"

# During development, limit number of articles fetched
MAX_ARTICLES = 8


def load_seen_ids():
    try:
        with open(SEEN_IDS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen_ids(seen_ids):
    with open(SEEN_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(seen_ids), f)


def fetch_recent_arxiv():
    log("Fetching recent arXiv cs.HC entries...")
    feed = feedparser.parse(ARXIV_HC_URL)
    articles = []
    for idx, entry in enumerate(feed.entries):
        if idx >= MAX_ARTICLES:
            break
        articles.append({
            'id': entry.id,
            'title': entry.title.strip(),
            'summary': entry.summary.strip(),
            'published': entry.published,
        })
    log(f"Fetched {len(articles)} entries from arXiv cs.HC.")
    return articles


def search_unsplash_photo(query, is_featured=False):
    """Search for a photo on Unsplash and return photo data."""
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
    }
    
    # Search for photos
    search_url = f"{UNSPLASH_API_URL}/search/photos"
    params = {
        'query': query,
        'per_page': 1,
        'orientation': 'landscape' if is_featured else 'squarish'
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            photo = data['results'][0]
            
            # Add UTM parameters to user profile link as required by Unsplash guidelines
            user_link_with_utm = f"{photo['user']['links']['html']}?utm_source=arxiv_aggregator&utm_medium=referral"
            
            return {
                'id': photo['id'],
                'url': photo['urls']['small'] if not is_featured else photo['urls']['regular'],
                'download_url': photo['links']['download_location'],
                'alt_description': photo.get('alt_description', ''),
                'user': photo['user']['name'],
                'user_link': user_link_with_utm,
                'unsplash_link': f"https://unsplash.com/?utm_source=arxiv_aggregator&utm_medium=referral"
            }
    except requests.RequestException as e:
        log(f"Error searching Unsplash: {e}")
    
    return None


def download_unsplash_photo(photo_data, filename, is_featured=False):
    """Download a photo from Unsplash and save it locally."""
    try:
        # REQUIRED: Trigger download endpoint as per Unsplash API guidelines
        # This is mandatory when using images in a way similar to downloading
        headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
        download_response = requests.get(photo_data['download_url'], headers=headers)
        download_response.raise_for_status()
        log(f"Triggered Unsplash download endpoint for photo {photo_data['id']}")
        
        # Download the actual image using the hotlinked URL as required
        response = requests.get(photo_data['url'])
        response.raise_for_status()
        
        # Save the image
        os.makedirs('output/images', exist_ok=True)
        image_path = os.path.join('output', 'images', filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        # Resize if needed
        if not is_featured:
            # Resize thumbnail images to consistent size
            with Image.open(image_path) as img:
                img.thumbnail((120, 80), Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=85)
        else:
            # Resize featured images
            with Image.open(image_path) as img:
                img.thumbnail((300, 200), Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=90)
        
        log(f"Downloaded and saved image: {filename}")
        return True
        
    except Exception as e:
        log(f"Error downloading image: {e}")
        return False


def generate_article_image(title, summary, is_featured=False):
    """Get an image from Unsplash for an article."""
    # Generate search keywords
    search_query = generate_search_keywords(title, summary)
    log(f"Searching Unsplash for: {search_query}")
    
    # Search for photo
    photo_data = search_unsplash_photo(search_query, is_featured)
    
    if not photo_data:
        log(f"No photo found for query: {search_query}")
        return None
    
    # Create filename based on title hash
    title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
    filename = f"article_{title_hash}.jpg"
    
    # Download the photo
    if download_unsplash_photo(photo_data, filename, is_featured):
        return {
            'filename': filename,
            'path': f"images/{filename}",
            'alt_text': photo_data.get('alt_description', f"Photo related to: {title}"),
            'credit': f"Photo by {photo_data['user']} on Unsplash",
            'credit_link': photo_data['user_link'],
            'unsplash_link': photo_data['unsplash_link']
        }
    
    return None


def upload_via_ftp(local_dir):
    log("Uploading to FTP...")
    with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
        ftp.encoding = 'utf-8'
        ftp.cwd(FTP_REMOTE_DIR)
        
        # Upload files in root directory
        for filename in os.listdir(local_dir):
            filepath = os.path.join(local_dir, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    ftp.storbinary(f'STOR {filename}', f)
                    log(f"Uploaded {filename}")
        
        # Upload images directory if it exists
        images_dir = os.path.join(local_dir, 'images')
        if os.path.exists(images_dir) and os.path.isdir(images_dir):
            # Create images directory on FTP server if it doesn't exist
            try:
                ftp.mkd('images')
                log("Created 'images' directory on FTP server")
            except ftplib.error_perm:
                # Directory might already exist
                pass
            
            # Change to images directory on FTP server
            ftp.cwd('images')
            
            # Upload all image files
            for filename in os.listdir(images_dir):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    with open(filepath, 'rb') as f:
                        ftp.storbinary(f'STOR {filename}', f)
                        log(f"Uploaded images/{filename}")
            
            # Go back to root directory
            ftp.cwd('..')


def main():
    seen_ids = load_seen_ids()
    all_articles = fetch_recent_arxiv()
    new_articles = [a for a in all_articles if a['id'] not in seen_ids]

    if not new_articles:
        log("No new articles (or all have been seen). Exiting.")
        return

    # Select featured article (avoiding already-featured ones)
    featured_article, remaining_articles = select_featured_article(new_articles)
    
    if not featured_article:
        log("No suitable featured article found. Exiting.")
        return

    processed = []
    
    # Process featured article first
    log(f"Processing featured article: {featured_article['title']}")
    new_summary = rewrite_blurb(featured_article['title'], featured_article['summary'], "human-computer interaction")
    new_headline = rewrite_title(featured_article['title'], "human-computer interaction", featured_article['summary'], new_summary)
    
    # Generate featured image
    log("Generating featured image")
    image_data = generate_article_image(new_headline, new_summary, is_featured=True)
    
    featured_data = {
        'id': featured_article['id'].split('/')[-1],
        'title': new_headline,
        'blurb': new_summary,
        'url': featured_article['id'],
        'featured': True
    }
    
    if image_data:
        featured_data['image'] = image_data
        
    processed.append(featured_data)
    seen_ids.add(featured_article['id'])
    
    # Process remaining articles
    for idx, art in enumerate(remaining_articles, start=2):
        log(f"Processing article {idx}/{len(new_articles)}: {art['title']}")
        new_summary = rewrite_blurb(art['title'], art['summary'], "human-computer interaction")
        new_headline = rewrite_title(art['title'], "human-computer interaction", art['summary'], new_summary)
        
        # Generate thumbnail for every third article (articles 4, 7, 10, etc.)
        image_data = None
        if (idx - 1) % 3 == 0 and idx > 1:
            log(f"Generating thumbnail for article {idx}")
            image_data = generate_article_image(new_headline, new_summary, is_featured=False)
        
        article_data = {
            'id': art['id'].split('/')[-1],
            'title': new_headline,
            'blurb': new_summary,
            'url': art['id'],
        }
        
        if image_data:
            article_data['image'] = image_data
            
        processed.append(article_data)
        seen_ids.add(art['id'])

    save_seen_ids(seen_ids)
    html_content = generate_html(processed, category="Human-Computer Interaction")

    os.makedirs('output', exist_ok=True)
    output_path = os.path.join('output', 'hc.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    log(f"Generated HTML at {output_path}")

    upload_via_ftp('output')
    log(f"Finished processing {len(new_articles)} articles at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()