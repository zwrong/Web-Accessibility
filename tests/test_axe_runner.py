"""
Tests for Axe Runner Module
TDD Phase 2 - RED: These tests should FAIL initially

Tests cover:
- Running axe-core on a page
- Filtering SC 2.4.3 related rules
- Parsing violation results
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

# Import the module we're testing (doesn't exist yet - will fail)
from focus_order_tester.axe_runner import (
    AxeRunner,
    FocusOrderViolation,
    SC_243_RULES,
    run_axe_analysis
)


class TestSC243Rules:
    """Test that correct rules are defined for SC 2.4.3"""
    
    def test_tabindex_rule_included(self):
        """tabindex rule should be included"""
        assert "tabindex" in SC_243_RULES
    
    def test_focus_order_semantics_included(self):
        """focus-order-semantics rule should be included"""
        assert "focus-order-semantics" in SC_243_RULES
    
    def test_nested_interactive_included(self):
        """nested-interactive rule should be included"""
        assert "nested-interactive" in SC_243_RULES
    
    def test_aria_hidden_focus_included(self):
        """aria-hidden-focus rule should be included"""
        assert "aria-hidden-focus" in SC_243_RULES


class TestFocusOrderViolation:
    """Test the FocusOrderViolation data class"""
    
    def test_create_violation(self):
        """Should create a violation object with all fields"""
        violation = FocusOrderViolation(
            rule_id="tabindex",
            description="Elements should not have tabindex greater than zero",
            impact="serious",
            help_url="https://dequeuniversity.com/rules/axe/4.11/tabindex",
            nodes=[{"html": "<p tabindex=\"1\">", "target": ["#positive"]}]
        )
        assert violation.rule_id == "tabindex"
        assert violation.impact == "serious"
        assert len(violation.nodes) == 1


class TestAxeRunner:
    """Test AxeRunner class"""
    
    @pytest.mark.asyncio
    async def test_runner_initialization(self):
        """Should initialize with headless browser by default"""
        async with AxeRunner() as runner:
            assert runner.headless == True
    
    @pytest.mark.asyncio
    async def test_runner_custom_headless(self):
        """Should accept headless parameter"""
        async with AxeRunner(headless=False) as runner:
            assert runner.headless == False
    
    @pytest.mark.asyncio
    async def test_analyze_returns_violations(self):
        """analyze() should return list of FocusOrderViolation"""
        async with AxeRunner() as runner:
            # Use a simple data URL for testing
            result = await runner.analyze("data:text/html,<html><body><p tabindex='1'>Test</p></body></html>")
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_analyze_detects_tabindex_violation(self):
        """Should detect tabindex > 0 violation"""
        html = """
        <html>
        <body>
            <p tabindex="5">Bad tabindex</p>
        </body>
        </html>
        """
        async with AxeRunner() as runner:
            result = await runner.analyze(f"data:text/html,{html}")
            rule_ids = [v.rule_id for v in result]
            assert "tabindex" in rule_ids


class TestRunAxeAnalysis:
    """Test the convenience function"""
    
    @pytest.mark.asyncio
    async def test_run_axe_analysis_single_url(self):
        """Should analyze a single URL and return results"""
        result = await run_axe_analysis("data:text/html,<html><body>Test</body></html>")
        assert "url" in result
        assert "violations" in result
    
    @pytest.mark.asyncio
    async def test_result_contains_metadata(self):
        """Result should contain timestamp and url"""
        result = await run_axe_analysis("data:text/html,<html><body>Test</body></html>")
        assert "timestamp" in result
        assert "url" in result
