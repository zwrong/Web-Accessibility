"""
URL Handler Module for Focus Order Tester

Handles URL parsing, validation, and reading from files.
"""
from urllib.parse import urlparse
from pathlib import Path
from typing import List, Optional


class URLValidationError(Exception):
    """Raised when URL validation fails"""
    pass


def validate_url(url: Optional[str]) -> bool:
    """
    Validate if a string is a proper URL.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    if url is None or url == "":
        return False
    
    try:
        result = urlparse(url)
        # Must have scheme (http, https, file) and netloc (for http/https) or path (for file)
        if result.scheme in ('http', 'https'):
            return bool(result.netloc)
        elif result.scheme == 'file':
            return bool(result.path)
        else:
            return False
    except Exception:
        return False


def parse_urls(url_string: str) -> List[str]:
    """
    Parse a string containing one or more URLs.
    
    URLs can be comma-separated. Invalid URLs are filtered out.
    
    Args:
        url_string: A string containing one or more URLs
        
    Returns:
        List of valid URLs
    """
    if not url_string or not url_string.strip():
        return []
    
    # Split by comma and clean up
    raw_urls = [u.strip() for u in url_string.split(',')]
    
    # Filter to only valid URLs
    valid_urls = [u for u in raw_urls if validate_url(u)]
    
    return valid_urls


def read_urls_from_file(file_path: str) -> List[str]:
    """
    Read URLs from a file, one per line.
    
    Lines starting with # are treated as comments and skipped.
    Empty lines are skipped.
    Invalid URLs are filtered out.
    
    Args:
        file_path: Path to the file containing URLs
        
    Returns:
        List of valid URLs
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"URL file not found: {file_path}")
    
    valid_urls = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Validate and add
            if validate_url(line):
                valid_urls.append(line)
    
    return valid_urls
