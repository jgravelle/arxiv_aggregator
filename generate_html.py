import os
from datetime import datetime

# Path to base template (HTML boilerplate with CSS placeholders)
TEMPLATE_PATH = os.path.join('templates', 'base_template.html')
ML_TEMPLATE_PATH = os.path.join('templates', 'ml_template.html')
CV_TEMPLATE_PATH = os.path.join('templates', 'cv_template.html')
CR_TEMPLATE_PATH = os.path.join('templates', 'cr_template.html')
RO_TEMPLATE_PATH = os.path.join('templates', 'ro_template.html')
HC_TEMPLATE_PATH = os.path.join('templates', 'hc_template.html')


def load_template(category="AI Research"):
    """Read the appropriate HTML template into a string based on category."""
    if category == "Machine Learning":
        template_path = ML_TEMPLATE_PATH
    elif category == "Computer Vision":
        template_path = CV_TEMPLATE_PATH
    elif category == "Security/Cryptography":
        template_path = CR_TEMPLATE_PATH
    elif category == "Robotics":
        template_path = RO_TEMPLATE_PATH
    elif category == "Human-Computer Interaction":
        template_path = HC_TEMPLATE_PATH
    else:
        template_path = TEMPLATE_PATH
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def clean_headline(title):
    """Remove trailing periods from headlines as they shouldn't end with periods."""
    return title.rstrip('.')

def convert_to_pdf_url(url):
    """Convert arXiv abstract URL to PDF URL by replacing /abs/ with /pdf/"""
    return url.replace('/abs/', '/pdf/')

def generate_html(articles, category="AI Research"):
    """Generate a complete HTML page given a list of article dicts.

    Each article dict should have:
      - id: unique arXiv ID (string)
      - title: rewritten headline
      - blurb: rewritten summary
      - url: link to the arXiv abstract
      - featured: optional bool
    
    Args:
      - category: The category name to display (e.g., "AI Research", "Machine Learning")
    """
    template = load_template(category)

    # Separate featured article (only one) and others
    featured = None
    others = []
    for art in articles:
        if art.get('featured'):
            featured = art
        else:
            others.append(art)
    # If no article explicitly featured, default to first
    if featured is None and articles:
        featured = articles[0]
        others = articles[1:]

    # Split others into main content and sidebar articles
    # Move last 3 articles to sidebar, keep the rest in main content
    if len(others) > 3:
        main_articles = others[:-3]  # All but last 3
        sidebar_articles = others[-3:]  # Last 3
    else:
        main_articles = []
        sidebar_articles = others  # All remaining articles go to sidebar

    # Build HTML segments for main content
    html_segments = ""
    
    # Featured article section
    if featured:
        image_html = ""
        if featured.get('image'):
            img = featured['image']
            credit_html = ""
            if img.get('credit'):
                # Unsplash requires attribution to both photographer and Unsplash with UTM parameters
                credit_html = f'''<div class="photo-credit">
                    <a href="{img.get("credit_link", "#")}" target="_blank">{img["credit"]}</a> •
                    <a href="{img.get("unsplash_link", "https://unsplash.com/?utm_source=arxiv_aggregator&utm_medium=referral")}" target="_blank">Unsplash</a>
                </div>'''
            image_html = f"""
        <div class="featured-image">
          <img src="{img['path']}" alt="{img['alt_text']}" class="article-img" />
          {credit_html}
        </div>"""
        
        html_segments += f"""
      <article class="featured-article">
        <div class="category-tag">FEATURED {category.upper()}</div>
        <h1>{clean_headline(featured['title'])}</h1>
        <div class="byline">From arXiv • Latest Research</div>{image_html}
        <p class="summary">{featured['blurb']}</p>
        <a href="{convert_to_pdf_url(featured['url'])}" target="_blank" class="read-more">Read Full Paper →</a>
      </article>
"""

    # Regular articles grid (main content)
    if main_articles:
        html_segments += '\n      <div class="articles-grid">\n'
        for art in main_articles:
            image_html = ""
            if art.get('image'):
                img = art['image']
                credit_html = ""
                if img.get('credit'):
                    # Unsplash requires attribution to both photographer and Unsplash with UTM parameters
                    credit_html = f'''<div class="photo-credit-small">
                        <a href="{img.get("credit_link", "#")}" target="_blank">{img["credit"]}</a> •
                        <a href="{img.get("unsplash_link", "https://unsplash.com/?utm_source=arxiv_aggregator&utm_medium=referral")}" target="_blank">Unsplash</a>
                    </div>'''
                image_html = f"""
          <div class="article-thumbnail">
            <img src="{img['path']}" alt="{img['alt_text']}" class="thumbnail-img" />
            {credit_html}
          </div>"""
            
            html_segments += f"""        <article class="article">
          {image_html}
          <h2>{clean_headline(art['title'])}</h2>
          <p class="summary">{art['blurb']}</p>
          <a href="{convert_to_pdf_url(art['url'])}" target="_blank" class="read-more">Read Paper →</a>
        </article>
"""
        html_segments += '      </div>\n'

    # Build sidebar articles HTML
    sidebar_html = ""
    if sidebar_articles:
        for art in sidebar_articles:
            sidebar_html += f"""        <article class="sidebar-article">
          <h3><a href="{convert_to_pdf_url(art['url'])}" target="_blank">{clean_headline(art['title'])}</a></h3>
          <p class="summary">{art['blurb']}</p>
          <a href="{convert_to_pdf_url(art['url'])}" target="_blank" class="read-more">Read Paper →</a>
        </article>
"""

    # Replace placeholders
    html = template.replace("<!--ARTICLES_PLACEHOLDER-->", html_segments)
    html = html.replace("<!--SIDEBAR_ARTICLES_PLACEHOLDER-->", sidebar_html)

    # Insert current date
    today = datetime.now().strftime("%B %d, %Y")
    html = html.replace('{date}', today)
    return html
