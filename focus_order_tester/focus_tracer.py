"""
Focus Tracer Module for Focus Order Tester

Traces the actual focus path through a page by simulating Tab key navigation.
"""
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page


@dataclass
class FocusElement:
    """Represents an element that received focus during tracing"""
    tag_name: str
    selector: str
    text_content: str
    tab_index: int
    position: int
    role: Optional[str] = None
    aria_label: Optional[str] = None


class FocusTracer:
    """
    Traces focus path through a page by simulating Tab key navigation.
    
    Usage:
        async with FocusTracer() as tracer:
            focus_path = await tracer.trace("https://example.com")
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
    
    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
    
    async def trace(self, url: str, max_elements: int = 100) -> List[FocusElement]:
        """
        Trace focus path by simulating Tab key presses.
        
        Args:
            url: The URL to trace
            max_elements: Maximum elements to trace (prevents infinite loops)
            
        Returns:
            List of FocusElement in focus order
        """
        if not self._browser:
            raise RuntimeError("FocusTracer must be used as async context manager")
        
        page = await self._browser.new_page()
        focus_path = []
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            
            # Start from body to ensure clean state
            await page.evaluate("document.body.focus()")
            
            seen_selectors = set()
            position = 0
            
            for _ in range(max_elements):
                # Press Tab
                await page.keyboard.press("Tab")
                await asyncio.sleep(0.05)  # Small delay for focus to settle
                
                # Get currently focused element info
                element_info = await page.evaluate("""
                    (index) => {
                        const el = document.activeElement;
                        if (!el || el === document.body) return null;
                        
                        // Generate a unique selector using index
                        let selector = el.tagName.toLowerCase();
                        if (el.id) selector = '#' + el.id;
                        else selector = el.tagName.toLowerCase() + '_' + index;
                        
                        return {
                            tagName: el.tagName.toLowerCase(),
                            selector: selector,
                            textContent: (el.textContent || '').trim().slice(0, 100),
                            tabIndex: el.tabIndex,
                            role: el.getAttribute('role'),
                            ariaLabel: el.getAttribute('aria-label')
                        };
                    }
                """, position)
                
                if not element_info:
                    break
                
                # Check if we've cycled back to start
                if element_info["selector"] in seen_selectors:
                    break
                
                seen_selectors.add(element_info["selector"])
                
                focus_path.append(FocusElement(
                    tag_name=element_info["tagName"],
                    selector=element_info["selector"],
                    text_content=element_info["textContent"],
                    tab_index=element_info["tabIndex"],
                    position=position,
                    role=element_info.get("role"),
                    aria_label=element_info.get("ariaLabel")
                ))
                
                position += 1
            
            return focus_path
            
        finally:
            await page.close()


async def trace_focus_path(url: str, headless: bool = True, max_elements: int = 100) -> Dict[str, Any]:
    """
    Convenience function to trace focus path on a single URL.
    
    Args:
        url: The URL to trace
        headless: Whether to run browser in headless mode
        max_elements: Maximum elements to trace
        
    Returns:
        Dict with url, focus_path, and element_count
    """
    async with FocusTracer(headless=headless) as tracer:
        focus_path = await tracer.trace(url, max_elements=max_elements)
        
        return {
            "url": url,
            "focus_path": [
                {
                    "position": e.position,
                    "tag_name": e.tag_name,
                    "selector": e.selector,
                    "text_content": e.text_content,
                    "tab_index": e.tab_index,
                    "role": e.role
                }
                for e in focus_path
            ],
            "element_count": len(focus_path)
        }


def compare_dom_vs_focus_order(dom_order: List[str], focus_order: List[str]) -> Dict[str, Any]:
    """
    Compare DOM order with actual focus order.
    
    Args:
        dom_order: List of selectors in DOM order
        focus_order: List of selectors in focus order
        
    Returns:
        Dict with matches (bool) and discrepancies list
    """
    discrepancies = []
    
    for i, (dom_sel, focus_sel) in enumerate(zip(dom_order, focus_order)):
        if dom_sel != focus_sel:
            discrepancies.append({
                "position": i,
                "dom_selector": dom_sel,
                "focus_selector": focus_sel
            })
    
    # Check for length differences
    if len(dom_order) != len(focus_order):
        discrepancies.append({
            "type": "length_mismatch",
            "dom_count": len(dom_order),
            "focus_count": len(focus_order)
        })
    
    return {
        "matches": len(discrepancies) == 0,
        "discrepancies": discrepancies
    }
