"""
Axe Runner Module for Focus Order Tester

Runs axe-core accessibility analysis focusing on SC 2.4.3 (Focus Order) related rules.
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page


# Rules related to WCAG SC 2.4.3 Focus Order
SC_243_RULES = [
    "tabindex",              # tabindex > 0 creates non-natural focus order
    "focus-order-semantics", # Elements in focus order should have appropriate roles
    "nested-interactive",    # Nested interactive controls cause focus issues
    "aria-hidden-focus",     # aria-hidden elements shouldn't be focusable
]


@dataclass
class FocusOrderViolation:
    """Represents a focus order violation found by axe-core"""
    rule_id: str
    description: str
    impact: str
    help_url: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)


class AxeRunner:
    """
    Runs axe-core analysis on web pages.
    
    Usage:
        async with AxeRunner() as runner:
            violations = await runner.analyze("https://example.com")
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
    
    async def analyze(self, url: str) -> List[FocusOrderViolation]:
        """
        Analyze a page for focus order violations.
        
        Args:
            url: The URL to analyze (can be http://, https://, file://, or data:)
            
        Returns:
            List of FocusOrderViolation objects
        """
        if not self._browser:
            raise RuntimeError("AxeRunner must be used as async context manager")
        
        page = await self._browser.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            
            # Inject and run axe-core
            results = await self._run_axe(page)
            
            # Filter and parse violations
            violations = self._parse_violations(results)
            
            return violations
        finally:
            await page.close()
    
    async def _run_axe(self, page: Page) -> Dict[str, Any]:
        """Inject axe-core and run analysis"""
        # Dictionary of local paths to check
        # We check relative to current working directory
        import os
        local_axe = "lib/axe.min.js"
        
        if os.path.exists(local_axe):
            await page.add_script_tag(path=local_axe)
        else:
            # Fallback to CDN
            await page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.4/axe.min.js")
        
        # Run axe with focus order related rules
        results = await page.evaluate("""
            async () => {
                const results = await axe.run({
                    runOnly: {
                        type: 'rule',
                        values: ['tabindex', 'focus-order-semantics', 'nested-interactive', 'aria-hidden-focus']
                    }
                });
                return results;
            }
        """)
        
        return results
    
    def _parse_violations(self, results: Dict[str, Any]) -> List[FocusOrderViolation]:
        """Parse axe-core results into FocusOrderViolation objects"""
        violations = []
        
        for violation in results.get("violations", []):
            nodes = []
            for node in violation.get("nodes", []):
                nodes.append({
                    "html": node.get("html", ""),
                    "target": node.get("target", []),
                    "failureSummary": node.get("failureSummary", "")
                })
            
            violations.append(FocusOrderViolation(
                rule_id=violation.get("id", ""),
                description=violation.get("description", ""),
                impact=violation.get("impact", ""),
                help_url=violation.get("helpUrl", ""),
                nodes=nodes
            ))
        
        return violations


async def run_axe_analysis(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run axe analysis on a single URL.
    
    Args:
        url: The URL to analyze
        headless: Whether to run browser in headless mode
        
    Returns:
        Dict with url, timestamp, and violations
    """
    async with AxeRunner(headless=headless) as runner:
        violations = await runner.analyze(url)
        
        return {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "description": v.description,
                    "impact": v.impact,
                    "help_url": v.help_url,
                    "nodes": v.nodes
                }
                for v in violations
            ],
            "violation_count": len(violations)
        }
