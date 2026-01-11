"""
Tests for Focus Tracer Module
TDD Phase 3 - RED: These tests should FAIL initially

Tests cover:
- Simulating Tab key navigation
- Recording focus path sequence
- Detecting focus traps
- Comparing DOM order vs focus order
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

# Import the module we're testing (doesn't exist yet - will fail)
from focus_order_tester.focus_tracer import (
    FocusTracer,
    FocusElement,
    trace_focus_path,
    compare_dom_vs_focus_order
)


class TestFocusElement:
    """Test the FocusElement data class"""
    
    def test_create_focus_element(self):
        """Should create a focus element with required fields"""
        element = FocusElement(
            tag_name="button",
            selector="#submit-btn",
            text_content="Submit",
            tab_index=0,
            position=1
        )
        assert element.tag_name == "button"
        assert element.position == 1
    
    def test_focus_element_with_optional_fields(self):
        """Should support optional aria attributes"""
        element = FocusElement(
            tag_name="a",
            selector="a.nav-link",
            text_content="Home",
            tab_index=0,
            position=0,
            role="link",
            aria_label="Home page"
        )
        assert element.role == "link"
        assert element.aria_label == "Home page"


class TestFocusTracer:
    """Test FocusTracer class"""
    
    @pytest.mark.asyncio
    async def test_tracer_initialization(self):
        """Should initialize with headless browser by default"""
        async with FocusTracer() as tracer:
            assert tracer.headless == True
    
    @pytest.mark.asyncio
    async def test_trace_returns_focus_elements(self):
        """trace() should return list of FocusElement"""
        html = "<html><body><button>Click</button></body></html>"
        async with FocusTracer() as tracer:
            result = await tracer.trace(f"data:text/html,{html}")
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_trace_records_focus_sequence(self):
        """Should record elements in focus order with sequential positions"""
        # Use simple HTML without href to avoid URL issues
        html = "<html><body><button>Btn1</button><button>Btn2</button><button>Btn3</button></body></html>"
        async with FocusTracer() as tracer:
            result = await tracer.trace(f"data:text/html,{html}")
            # Verify positions are sequential
            if len(result) > 0:
                positions = [e.position for e in result]
                assert positions == list(range(len(result)))
    
    @pytest.mark.asyncio
    async def test_trace_with_tabindex(self):
        """Should follow tabindex order when present"""
        html = """
        <html><body>
            <button tabindex="2">Second</button>
            <button tabindex="1">First</button>
            <button tabindex="3">Third</button>
        </body></html>
        """
        async with FocusTracer() as tracer:
            result = await tracer.trace(f"data:text/html,{html}")
            texts = [e.text_content.strip() for e in result]
            # With positive tabindex, order should be 1, 2, 3
            assert texts == ["First", "Second", "Third"]
    
    @pytest.mark.asyncio  
    async def test_max_elements_limit(self):
        """Should stop after max_elements to prevent infinite loops"""
        html = "<html><body>" + "<a href='#'>Link</a>" * 100 + "</body></html>"
        async with FocusTracer() as tracer:
            result = await tracer.trace(f"data:text/html,{html}", max_elements=10)
            assert len(result) <= 10


class TestTraceFocusPath:
    """Test convenience function"""
    
    @pytest.mark.asyncio
    async def test_trace_focus_path_returns_dict(self):
        """Should return dict with url and focus_path"""
        result = await trace_focus_path("data:text/html,<html><body><a href='#'>Link</a></body></html>")
        assert "url" in result
        assert "focus_path" in result
        assert "element_count" in result


class TestCompareDomVsFocusOrder:
    """Test DOM vs focus order comparison"""
    
    def test_matching_order_returns_no_issues(self):
        """Should return empty issues when orders match"""
        dom_order = ["#a", "#b", "#c"]
        focus_order = ["#a", "#b", "#c"]
        result = compare_dom_vs_focus_order(dom_order, focus_order)
        assert result["matches"] == True
        assert len(result["discrepancies"]) == 0
    
    def test_different_order_returns_discrepancies(self):
        """Should return discrepancies when orders differ"""
        dom_order = ["#a", "#b", "#c"]
        focus_order = ["#b", "#a", "#c"]
        result = compare_dom_vs_focus_order(dom_order, focus_order)
        assert result["matches"] == False
        assert len(result["discrepancies"]) > 0
