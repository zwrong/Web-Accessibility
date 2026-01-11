"""
Tests for Report Generator Module
TDD Phase 4 - RED: These tests should FAIL initially

Tests cover:
- Generating JSON reports
- Generating HTML reports
- Handling multiple page results
- Statistics and summary
"""
import pytest
import json
import os
import tempfile
from pathlib import Path

# Import the module we're testing (doesn't exist yet - will fail)
from focus_order_tester.report_generator import (
    ReportGenerator,
    generate_json_report,
    generate_html_report
)


class TestReportGenerator:
    """Test ReportGenerator class"""
    
    def test_create_report_generator(self):
        """Should create a report generator with results"""
        results = [{"url": "https://example.com", "violations": []}]
        generator = ReportGenerator(results)
        assert len(generator.results) == 1
    
    def test_add_result(self):
        """Should allow adding results incrementally"""
        generator = ReportGenerator()
        generator.add_result({"url": "https://a.com", "violations": []})
        generator.add_result({"url": "https://b.com", "violations": []})
        assert len(generator.results) == 2
    
    def test_get_summary(self):
        """Should return summary statistics"""
        results = [
            {"url": "https://a.com", "violations": [{"rule_id": "tabindex"}]},
            {"url": "https://b.com", "violations": []},
        ]
        generator = ReportGenerator(results)
        summary = generator.get_summary()
        assert summary["total_pages"] == 2
        assert summary["pages_with_violations"] == 1
        assert summary["total_violations"] == 1


class TestGenerateJsonReport:
    """Test JSON report generation"""
    
    def test_generate_json_report_returns_string(self):
        """Should return valid JSON string"""
        results = [{"url": "https://example.com", "violations": []}]
        json_str = generate_json_report(results)
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "results" in parsed
    
    def test_json_report_includes_metadata(self):
        """Should include generation timestamp"""
        results = [{"url": "https://example.com", "violations": []}]
        json_str = generate_json_report(results)
        parsed = json.loads(json_str)
        assert "generated_at" in parsed
        assert "total_pages" in parsed
    
    def test_write_json_to_file(self):
        """Should write JSON report to file"""
        results = [{"url": "https://example.com", "violations": []}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            generate_json_report(results, output_path=filepath)
            assert os.path.exists(filepath)
            with open(filepath) as f:
                content = json.load(f)
            assert "results" in content
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestGenerateHtmlReport:
    """Test HTML report generation"""
    
    def test_generate_html_report_returns_string(self):
        """Should return HTML string"""
        results = [{"url": "https://example.com", "violations": []}]
        html = generate_html_report(results)
        assert "<html" in html.lower()  # Check for html tag (may have attributes)
        assert "</html>" in html.lower()
    
    def test_html_report_contains_violations(self):
        """Should display violation details"""
        results = [{
            "url": "https://example.com",
            "violations": [{
                "rule_id": "tabindex",
                "description": "Elements should not have tabindex greater than zero",
                "impact": "serious",
                "nodes": [{"html": "<p tabindex='1'>", "target": ["#test"]}]
            }]
        }]
        html = generate_html_report(results)
        assert "tabindex" in html
        assert "serious" in html
    
    def test_html_report_shows_pass_for_no_violations(self):
        """Should show pass status when no violations"""
        results = [{"url": "https://example.com", "violations": []}]
        html = generate_html_report(results)
        # Should indicate pass or no issues
        assert "pass" in html.lower() or "0 violation" in html.lower()
    
    def test_write_html_to_file(self):
        """Should write HTML report to file"""
        results = [{"url": "https://example.com", "violations": []}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            filepath = f.name
        
        try:
            generate_html_report(results, output_path=filepath)
            assert os.path.exists(filepath)
            with open(filepath) as f:
                content = f.read()
            assert "<html" in content.lower()  # Check for html tag (may have attributes)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
