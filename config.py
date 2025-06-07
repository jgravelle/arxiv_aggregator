# config.py - Configuration settings for arXiv aggregator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ArXiv API URL for fetching recent cs.AI papers (Atom feed)
ARXIV_API_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=lastUpdatedDate&sortOrder=descending&max_results=8&start=0"
ARXIV_ML_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.LG&&sortBy=lastUpdatedDate&sortOrder=descending&max_results=8&start=0"
ARXIV_CV_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.CV&sortBy=lastUpdatedDate&sortOrder=descending&max_results=8&start=0"
ARXIV_RO_URL = "https://export.arxiv.org/api/query?search_query=cat:cs.RO&sortBy=lastUpdatedDate&sortOrder=descending&max_results=8&start=0"
ARXIV_CR_URL = "https://export.arxiv.org/api/query?search_query=cat:cs.CR&pysortBy=lastUpdatedDate&sortOrder=descending&max_results=8&start=0"

# Local JSON file to track which arXiv IDs have already been processed
SEEN_IDS_FILE = "seen_arxiv_ids.json"

# Ollama configuration (loaded from environment variables with fallbacks)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:latest")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_CHAT_API_URL = os.getenv("OLLAMA_CHAT_API_URL", "http://localhost:11434/api/chat")

# FTP server configuration (loaded from environment variables)
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_REMOTE_DIR = os.getenv("FTP_REMOTE_DIR", ".")

# Unsplash API configuration (loaded from environment variables)
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_SECRET_KEY = os.getenv("UNSPLASH_SECRET_KEY")
UNSPLASH_APPLICATION_ID = os.getenv("UNSPLASH_APPLICATION_ID")
UNSPLASH_API_URL = "https://api.unsplash.com"

# Validation: Ensure required environment variables are set
required_env_vars = [
    "FTP_HOST", "FTP_USER", "FTP_PASS",
    "UNSPLASH_ACCESS_KEY", "UNSPLASH_SECRET_KEY", "UNSPLASH_APPLICATION_ID"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. "
                     f"Please check your .env file and ensure all required variables are set.")
