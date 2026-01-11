"""
Trigger Tracker Module for Focus Order Tester

Detects and tests interactive triggers (like buttons) to verify focus order behaviors
specifically for dynamic content like dialogs (F85).
"""
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, Locator

from .focus_tracer import FocusElement, FocusTracer

@dataclass
class TriggerResult:
    """Result of a trigger click analysis"""
    trigger_selector: str
    trigger_text: str
    dialog_selector: Optional[str] = None
    distance: int = -1
    is_adjacent: bool = False
    f85_violation: bool = False
    focus_path_after_click: List[FocusElement] = field(default_factory=list)


class TriggerTracker:
    """
    Tracks focus behavior after clicking trigger elements.
    Designed to detect WCAG F85 violations (dialog position).
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _ensure_page(self, url: Optional[str] = None):
        """Ensure a page is open and optionally navigate to URL"""
        if not self._browser:
            raise RuntimeError("TriggerTracker must be used as async context manager")
        
        if not self.page:
            context = await self._browser.new_context()
            self.page = await context.new_page()
        
        if url:
            await self.page.goto(url, wait_until="networkidle")

    async def detect_triggers(self) -> List[Locator]:
        """
        Detect potential trigger elements that might open dialogs.
        Looks for buttons with aria-haspopup, aria-controls, or specific text patterns.
        """
        if not self.page:
            return []

        triggers = []
        buttons = await self.page.get_by_role("button").all()
        
        for btn in buttons:
            has_popup = await btn.get_attribute("aria-haspopup")
            aria_controls = await btn.get_attribute("aria-controls")
            text = (await btn.text_content() or "").lower()
            
            # Heuristics for potential dialog triggers
            if (has_popup or 
                aria_controls or 
                "open" in text or 
                "show" in text or 
                "dialog" in text or 
                "modal" in text):
                triggers.append(btn)
                
        return triggers

    async def click_and_trace(self, trigger_selector: str) -> TriggerResult:
        """
        Click a specific trigger and trace focus path to find the dialog.
        
        Args:
            trigger_selector: CSS selector of the trigger to click
            
        Returns:
            TriggerResult containing distance and violation status
        """
        if not self.page:
            raise RuntimeError("Page not initialized")

        # Get trigger info before clicking
        trigger = self.page.locator(trigger_selector).first
        trigger_text = (await trigger.text_content() or "").strip()[:50]
        
        # Click the trigger
        await trigger.click()
        
        # Wait a bit for animations/DOM updates
        await asyncio.sleep(0.5)
        
        # Start tracing focus from current position
        # Note: We reuse logic similar to FocusTracer but here we just tab forward
        # until we hit a dialog or run out of reasonable steps
        
        focus_path = []
        dialog_found = False
        dialog_selector = None
        distance = 0
        
        # Trace up to 20 steps to find dialog
        for i in range(20):
            # Press Tab
            await self.page.keyboard.press("Tab")
            await asyncio.sleep(0.05)
            
            # Get current element
            element_info = await self.page.evaluate("""
                () => {
                    const el = document.activeElement;
                    if (!el || el === document.body) return null;
                    
                    let selector = el.tagName.toLowerCase();
                    if (el.id) selector = '#' + el.id;
                    else if (el.className) selector += '.' + el.className.split(' ').join('.');
                    
                    // Check if it looks like a dialog or is inside one
                    const dialogParent = el.closest('[role="dialog"], dialog, .modal, .dialog');
                    const isInDialog = dialogParent !== null;
                    const isDialogItself = el.getAttribute('role') === 'dialog' || el.tagName === 'DIALOG';
                     
                    return {
                        tagName: el.tagName.toLowerCase(),
                        selector: selector,
                        textContent: (el.textContent || '').trim().slice(0, 50),
                        role: el.getAttribute('role'),
                        isInDialog: isInDialog,
                        dialogSelector: dialogParent ? (dialogParent.id ? '#' + dialogParent.id : dialogParent.className) : null
                    };
                }
            """)
            
            if not element_info:
                continue

            focus_element = FocusElement(
                tag_name=element_info["tagName"],
                selector=element_info["selector"],
                text_content=element_info["textContent"],
                tab_index=0, # Simplified
                position=i + 1,
                role=element_info["role"]
            )
            focus_path.append(focus_element)
            
            # Check if we landed in a dialog
            if element_info["isInDialog"]:
                distance = i + 1
                dialog_found = True
                dialog_selector = element_info["dialogSelector"]
                break
        
        # Reset state (reload page or close dialog) - needed for next tests?
        # For now, we assume one test per page load or caller handles reset
        
        # Analyze results
        is_adjacent = distance <= 1 if dialog_found else False
        
        # F85 Violation: Dialog found but too far away (not adjacent in focus order)
        # However, if focus management moves focus TO the dialog immediately (distance 0 or 1), it's good.
        # If user has to tab many times (distance > 1), it's a violation.
        f85_violation = dialog_found and not is_adjacent
        
        return TriggerResult(
            trigger_selector=trigger_selector,
            trigger_text=trigger_text,
            dialog_selector=dialog_selector,
            distance=distance if dialog_found else -1,
            is_adjacent=is_adjacent,
            f85_violation=f85_violation,
            focus_path_after_click=focus_path
        )

    async def analyze_f85(self, url: str) -> List[TriggerResult]:
        """
        Analyze a page for F85 violations by detecting and testing triggers.
        """
        await self._ensure_page(url)
        
        results = []
        triggers = await self.detect_triggers()
        
        # Currently only test the first few relevant triggers to avoid long runtimes
        # In a real tool, might want to be more exhaustive or configurable
        for i, trigger in enumerate(triggers[:3]):
            # Get safe selector
            selector = await trigger.evaluate("""
                (el) => {
                    if (el.id) return '#' + el.id;
                    return el.tagName.toLowerCase(); // simplified
                }
            """)
            
            # We need to reload page for each trigger to ensure clean state
            if i > 0:
                await self.page.reload(wait_until="networkidle")
                
            res = await self.click_and_trace(selector)
            if res.dialog_selector: # Only keep results where we actually found a dialog interaction
                results.append(res)
                
        return results
