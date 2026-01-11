"""
Tests for Main Batch Processor Module
TDD Phase 5 - RED: These tests should FAIL initially

Tests cover:
- Command line argument parsing
- Batch URL processing
- Report output
- Error handling
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Import the module we're testing (doesn't exist yet - will fail)
from focus_order_tester.main import (
    parse_args,
    process_urls,
    main
)


class TestParseArgs:
    """Test command line argument parsing"""
    
    def test_parse_single_url(self):
        """Should parse a single URL argument"""
        args = parse_args(["https://example.com"])
        assert args.urls == ["https://example.com"]
    
    def test_parse_multiple_urls(self):
        """Should parse multiple URL arguments"""
        args = parse_args(["https://a.com", "https://b.com"])
        assert len(args.urls) == 2
    
    def test_parse_file_option(self):
        """Should parse --file option"""
        args = parse_args(["--file", "urls.txt"])
        assert args.file == "urls.txt"
    
    def test_parse_output_option(self):
        """Should parse --output option"""
        args = parse_args(["https://example.com", "--output", "report.json"])
        assert args.output == "report.json"
    
    def test_parse_format_option(self):
        """Should parse --format option (json or html)"""
        args = parse_args(["https://example.com", "--format", "html"])
        assert args.format == "html"
    
    def test_default_format_is_json(self):
        """Should default to json format"""
        args = parse_args(["https://example.com"])
        assert args.format == "json"
    
    def test_parse_headless_option(self):
        """Should parse --no-headless option"""
        args = parse_args(["https://example.com", "--no-headless"])
        assert args.headless == False


class TestProcessUrls:
    """Test batch URL processing"""
    
    @pytest.mark.asyncio
    async def test_process_single_url(self):
        """Should process a single URL and return results"""
        with patch('focus_order_tester.main.AxeRunner') as MockRunner:
            mock_instance = AsyncMock()
            mock_instance.analyze.return_value = []
            MockRunner.return_value.__aenter__.return_value = mock_instance
            
            results = await process_urls(["https://example.com"])
            assert len(results) == 1
            assert "url" in results[0]
    
    @pytest.mark.asyncio
    async def test_process_multiple_urls(self):
        """Should process multiple URLs"""
        with patch('focus_order_tester.main.AxeRunner') as MockRunner:
            mock_instance = AsyncMock()
            mock_instance.analyze.return_value = []
            MockRunner.return_value.__aenter__.return_value = mock_instance
            
            results = await process_urls(["https://a.com", "https://b.com"])
            assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_process_handles_errors(self):
        """Should handle errors gracefully and continue"""
        with patch('focus_order_tester.main.AxeRunner') as MockRunner:
            mock_instance = AsyncMock()
            mock_instance.analyze.side_effect = [Exception("Error"), []]
            MockRunner.return_value.__aenter__.return_value = mock_instance
            
            results = await process_urls(["https://error.com", "https://ok.com"])
            # Should have results for both, one with error
            assert len(results) == 2


class TestMain:
    """Test main entry point"""
    
    @pytest.mark.asyncio
    async def test_main_with_urls(self):
        """Should run successfully with URL arguments"""
        with patch('focus_order_tester.main.process_urls') as mock_process:
            mock_process.return_value = [{"url": "https://example.com", "violations": []}]
            with patch('focus_order_tester.main.generate_json_report') as mock_report:
                mock_report.return_value = "{}"
                
                # Should not raise
                await main(["https://example.com"])
    
    @pytest.mark.asyncio
    async def test_main_writes_output_file(self):
        """Should write report to output file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            with patch('focus_order_tester.main.process_urls') as mock_process:
                mock_process.return_value = [{"url": "https://example.com", "violations": []}]
                
                await main(["https://example.com", "--output", output_path])
                assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestTraceFocusIntegration:
    """Test --trace-focus flag integration (TDD Red Phase)"""
    
    @pytest.mark.asyncio
    async def test_process_urls_calls_trace_focus_when_flag_set(self):
        """Should call trace_focus_path when trace_focus=True"""
        with patch('focus_order_tester.main.AxeRunner') as MockRunner:
            mock_instance = AsyncMock()
            mock_instance.analyze.return_value = []
            MockRunner.return_value.__aenter__.return_value = mock_instance
            
            with patch('focus_order_tester.main.trace_focus_path') as mock_trace:
                mock_trace.return_value = {
                    "url": "https://example.com",
                    "focus_path": [{"position": 0, "tag_name": "button"}],
                    "element_count": 1
                }
                
                results = await process_urls(
                    ["https://example.com"],
                    trace_focus=True
                )
                
                # trace_focus_path should be called
                mock_trace.assert_called_once()
                # Result should include focus_path
                assert "focus_path" in results[0]
    
    @pytest.mark.asyncio
    async def test_process_urls_skips_trace_when_flag_false(self):
        """Should NOT call trace_focus_path when trace_focus=False"""
        with patch('focus_order_tester.main.AxeRunner') as MockRunner:
            mock_instance = AsyncMock()
            mock_instance.analyze.return_value = []
            MockRunner.return_value.__aenter__.return_value = mock_instance
            
            with patch('focus_order_tester.main.trace_focus_path') as mock_trace:
                results = await process_urls(
                    ["https://example.com"],
                    trace_focus=False
                )
                
                # trace_focus_path should NOT be called
                mock_trace.assert_not_called()
                # Result should NOT include focus_path
                assert "focus_path" not in results[0]
    
    @pytest.mark.asyncio
    async def test_focus_path_included_in_result(self):
        """Focus path data should be properly structured in result"""
        with patch('focus_order_tester.main.AxeRunner') as MockRunner:
            mock_instance = AsyncMock()
            mock_instance.analyze.return_value = []
            MockRunner.return_value.__aenter__.return_value = mock_instance
            
            with patch('focus_order_tester.main.trace_focus_path') as mock_trace:
                mock_trace.return_value = {
                    "url": "https://example.com",
                    "focus_path": [
                        {"position": 0, "tag_name": "button", "selector": "#btn1"},
                        {"position": 1, "tag_name": "a", "selector": "#link1"}
                    ],
                    "element_count": 2
                }
                
                results = await process_urls(
                    ["https://example.com"],
                    trace_focus=True
                )
                
                assert results[0]["focus_path"] == mock_trace.return_value["focus_path"]
                assert results[0]["focus_element_count"] == 2
