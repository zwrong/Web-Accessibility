"""
Tests for URL Handler Module
TDD Phase 1 - RED: These tests should FAIL initially

Tests cover:
- Single URL parsing and validation
- Reading URLs from a file
- Handling invalid/empty inputs
"""
import pytest
from pathlib import Path
import tempfile
import os

# Import the module we're testing (doesn't exist yet - will fail)
from focus_order_tester.url_handler import (
    validate_url,
    parse_urls,
    read_urls_from_file,
    URLValidationError
)


class TestValidateUrl:
    """Test URL validation functionality"""
    
    def test_valid_http_url(self):
        """Should accept valid HTTP URLs"""
        assert validate_url("http://example.com") == True
    
    def test_valid_https_url(self):
        """Should accept valid HTTPS URLs"""
        assert validate_url("https://www.amazon.com") == True
    
    def test_valid_url_with_path(self):
        """Should accept URLs with paths"""
        assert validate_url("https://www.w3.org/WAI/WCAG21/Techniques/failures/F44") == True
    
    def test_invalid_url_no_scheme(self):
        """Should reject URLs without scheme"""
        assert validate_url("example.com") == False
    
    def test_invalid_url_empty(self):
        """Should reject empty strings"""
        assert validate_url("") == False
    
    def test_invalid_url_none(self):
        """Should reject None"""
        assert validate_url(None) == False
    
    def test_local_file_url(self):
        """Should accept file:// URLs for local testing"""
        assert validate_url("file:///path/to/test.html") == True


class TestParseUrls:
    """Test URL list parsing"""
    
    def test_single_url_string(self):
        """Should parse a single URL string into a list"""
        result = parse_urls("https://example.com")
        assert result == ["https://example.com"]
    
    def test_multiple_urls_comma_separated(self):
        """Should parse comma-separated URLs"""
        result = parse_urls("https://a.com,https://b.com")
        assert result == ["https://a.com", "https://b.com"]
    
    def test_multiple_urls_with_spaces(self):
        """Should handle spaces around commas"""
        result = parse_urls("https://a.com, https://b.com")
        assert result == ["https://a.com", "https://b.com"]
    
    def test_empty_string_returns_empty_list(self):
        """Should return empty list for empty input"""
        result = parse_urls("")
        assert result == []
    
    def test_filters_invalid_urls(self):
        """Should filter out invalid URLs from the list"""
        result = parse_urls("https://valid.com,invalid,https://also-valid.com")
        assert result == ["https://valid.com", "https://also-valid.com"]


class TestReadUrlsFromFile:
    """Test reading URLs from file"""
    
    def test_read_urls_one_per_line(self):
        """Should read URLs from file, one per line"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("https://example1.com\n")
            f.write("https://example2.com\n")
            f.write("https://example3.com\n")
            f.flush()
            
            try:
                result = read_urls_from_file(f.name)
                assert result == [
                    "https://example1.com",
                    "https://example2.com", 
                    "https://example3.com"
                ]
            finally:
                os.unlink(f.name)
    
    def test_skip_empty_lines(self):
        """Should skip empty lines in file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("https://example1.com\n")
            f.write("\n")
            f.write("https://example2.com\n")
            f.flush()
            
            try:
                result = read_urls_from_file(f.name)
                assert result == ["https://example1.com", "https://example2.com"]
            finally:
                os.unlink(f.name)
    
    def test_skip_comment_lines(self):
        """Should skip lines starting with #"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("https://example.com\n")
            f.flush()
            
            try:
                result = read_urls_from_file(f.name)
                assert result == ["https://example.com"]
            finally:
                os.unlink(f.name)
    
    def test_file_not_found_raises_error(self):
        """Should raise FileNotFoundError for missing file"""
        with pytest.raises(FileNotFoundError):
            read_urls_from_file("/nonexistent/path/urls.txt")
    
    def test_filter_invalid_urls_in_file(self):
        """Should filter out invalid URLs from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("https://valid.com\n")
            f.write("not-a-valid-url\n")
            f.write("https://also-valid.com\n")
            f.flush()
            
            try:
                result = read_urls_from_file(f.name)
                assert result == ["https://valid.com", "https://also-valid.com"]
            finally:
                os.unlink(f.name)
