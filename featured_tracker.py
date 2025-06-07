#!/usr/bin/env python3
"""
Utility module for tracking featured articles across different aggregators
to prevent the same story from being featured on multiple pages.
"""

import os
import json
from typing import Set, List, Dict, Any

FEATURED_IDS_FILE = 'featured_arxiv_ids.json'

def load_featured_ids() -> Set[str]:
    """Load the set of already-featured article IDs."""
    try:
        with open(FEATURED_IDS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_featured_ids(featured_ids: Set[str]) -> None:
    """Save the set of featured article IDs."""
    with open(FEATURED_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(featured_ids), f, indent=2)

def add_featured_id(article_id: str) -> None:
    """Add a single article ID to the featured list."""
    featured_ids = load_featured_ids()
    featured_ids.add(article_id)
    save_featured_ids(featured_ids)

def clear_featured_ids() -> None:
    """Clear all featured article IDs (useful for starting a fresh batch)."""
    if os.path.exists(FEATURED_IDS_FILE):
        os.remove(FEATURED_IDS_FILE)

def select_featured_article(articles: List[Dict[str, Any]]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Select a featured article from the list, avoiding already-featured ones.
    
    Args:
        articles: List of article dictionaries with 'id' field
        
    Returns:
        Tuple of (featured_article, remaining_articles)
        If no suitable featured article found, returns (None, articles)
    """
    if not articles:
        return None, articles
    
    featured_ids = load_featured_ids()
    
    # Find the first article that hasn't been featured yet
    for i, article in enumerate(articles):
        article_id = article['id']
        if article_id not in featured_ids:
            # Mark this article as featured
            add_featured_id(article_id)
            
            # Return the featured article and the remaining articles
            remaining = articles[:i] + articles[i+1:]
            return article, remaining
    
    # If all articles have been featured, use the first one anyway
    # but log a warning
    print(f"WARNING: All {len(articles)} articles have already been featured. Using first article anyway.")
    return articles[0], articles[1:]