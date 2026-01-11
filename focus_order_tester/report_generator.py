"""
Report Generator Module for Focus Order Tester

Generates JSON and HTML reports from accessibility test results.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ReportGenerator:
    """
    Generates reports from accessibility test results.
    
    Usage:
        generator = ReportGenerator(results)
        summary = generator.get_summary()
    """
    
    def __init__(self, results: Optional[List[Dict[str, Any]]] = None):
        self.results = results or []
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """Add a single result to the collection"""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all results"""
        total_violations = 0
        pages_with_violations = 0
        
        for result in self.results:
            violations = result.get("violations", [])
            if violations:
                pages_with_violations += 1
                total_violations += len(violations)
        
        return {
            "total_pages": len(self.results),
            "pages_with_violations": pages_with_violations,
            "total_violations": total_violations,
            "pages_passed": len(self.results) - pages_with_violations
        }


def generate_json_report(
    results: List[Dict[str, Any]], 
    output_path: Optional[str] = None
) -> str:
    """
    Generate a JSON report from test results.
    
    Args:
        results: List of test results
        output_path: Optional path to write the report
        
    Returns:
        JSON string of the report
    """
    generator = ReportGenerator(results)
    summary = generator.get_summary()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_pages": summary["total_pages"],
        "pages_with_violations": summary["pages_with_violations"],
        "total_violations": summary["total_violations"],
        "results": results
    }
    
    json_str = json.dumps(report, indent=2, ensure_ascii=False)
    
    if output_path:
        Path(output_path).write_text(json_str, encoding='utf-8')
    
    return json_str


def generate_html_report(
    results: List[Dict[str, Any]], 
    output_path: Optional[str] = None
) -> str:
    """
    Generate an HTML report from test results.
    
    Args:
        results: List of test results
        output_path: Optional path to write the report
        
    Returns:
        HTML string of the report
    """
    generator = ReportGenerator(results)
    summary = generator.get_summary()
    
    # Build HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <title>WCAG 2.4.3 Focus Order Test Report</title>",
        "  <style>",
        "    body { font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }",
        "    .summary { background: #f0f0f0; padding: 20px; border-radius: 8px; margin-bottom: 20px; }",
        "    .pass { color: #22c55e; }",
        "    .fail { color: #ef4444; }",
        "    .page { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }",
        "    .violation { background: #fef2f2; padding: 10px; margin: 5px 0; border-left: 4px solid #ef4444; }",
        "    .impact-serious { border-color: #f97316; }",
        "    .impact-critical { border-color: #ef4444; }",
        "    code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>WCAG 2.4.3 Focus Order Test Report</h1>",
        f"  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        "  <div class='summary'>",
        f"    <h2>Summary</h2>",
        f"    <p>Total Pages: {summary['total_pages']}</p>",
        f"    <p>Pages with Violations: <span class='fail'>{summary['pages_with_violations']}</span></p>",
        f"    <p>Pages Passed: <span class='pass'>{summary['pages_passed']}</span></p>",
        f"    <p>Total Violations: {summary['total_violations']}</p>",
        "  </div>",
    ]
    
    # Add each page result
    for result in results:
        url = result.get("url", "Unknown")
        violations = result.get("violations", [])
        status = "fail" if violations else "pass"
        status_text = f"{len(violations)} violation(s)" if violations else "Pass - 0 violations"
        
        html_parts.append(f"  <div class='page'>")
        html_parts.append(f"    <h3>{url}</h3>")
        html_parts.append(f"    <p class='{status}'>{status_text}</p>")
        
        for v in violations:
            impact = v.get("impact", "minor")
            html_parts.append(f"    <div class='violation impact-{impact}'>")
            html_parts.append(f"      <strong>{v.get('rule_id', 'Unknown Rule')}</strong> ({impact})")
            html_parts.append(f"      <p>{v.get('description', '')}</p>")
            
            for node in v.get("nodes", []):
                html = node.get("html", "")
                html_parts.append(f"      <code>{html}</code>")
            
            html_parts.append("    </div>")
        
        html_parts.append("  </div>")
    
    html_parts.extend(["</body>", "</html>"])
    
    html = "\n".join(html_parts)
    
    if output_path:
        Path(output_path).write_text(html, encoding='utf-8')
    
    return html


def generate_md_report(
    results: List[Dict[str, Any]], 
    output_path: Optional[str] = None
) -> str:
    """
    Generate a Markdown report from test results.
    
    Args:
        results: List of test results
        output_path: Optional path to write the report
        
    Returns:
        Markdown string of the report
    """
    generator = ReportGenerator(results)
    summary = generator.get_summary()
    
    md_parts = [
        "# WCAG 2.4.3 Focus Order Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Pages | {summary['total_pages']} |",
        f"| Pages with Violations | {summary['pages_with_violations']} |",
        f"| Pages Passed | {summary['pages_passed']} |",
        f"| Total Violations | {summary['total_violations']} |",
        "",
        "---",
        "",
    ]
    
    for result in results:
        url = result.get("url", "Unknown")
        violations = result.get("violations", [])
        error = result.get("error")
        
        status = "❌" if violations else "✅"
        md_parts.append(f"## {status} {url}")
        md_parts.append("")
        
        if error:
            md_parts.append(f"> ⚠️ **Error:** {error}")
            md_parts.append("")
            continue
        
        if not violations:
            md_parts.append("**Status:** Pass - No violations detected")
            md_parts.append("")
        else:
            md_parts.append(f"**Violations Found:** {len(violations)}")
            md_parts.append("")
            
            for v in violations:
                rule_id = v.get("rule_id", "Unknown")
                impact = v.get("impact", "minor")
                description = v.get("description", "")
                help_url = v.get("help_url", "")
                
                md_parts.append(f"### 🔴 {rule_id} ({impact})")
                md_parts.append("")
                md_parts.append(f"{description}")
                md_parts.append("")
                
                if help_url:
                    md_parts.append(f"📖 [Learn more]({help_url})")
                    md_parts.append("")
                
                nodes = v.get("nodes", [])
                if nodes:
                    md_parts.append("**Affected Elements:**")
                    md_parts.append("")
                    for node in nodes:
                        html = node.get("html", "").replace("`", "'")
                        target = node.get("target", [])
                        target_str = " > ".join(target) if target else ""
                        md_parts.append(f"- `{target_str}`")
                        md_parts.append(f"  ```html")
                        md_parts.append(f"  {html}")
                        md_parts.append(f"  ```")
                    md_parts.append("")
        
        # Focus path section
        focus_path = result.get("focus_path", [])
        if focus_path:
            md_parts.append("### 🔍 Focus Path Trace")
            md_parts.append("")
            md_parts.append(f"**Total focusable elements:** {len(focus_path)}")
            md_parts.append("")
            md_parts.append("| # | Tag | Selector | Text |")
            md_parts.append("|---|-----|----------|------|")
            for item in focus_path:
                pos = item.get("position", 0)
                tag = item.get("tag_name", "")
                selector = item.get("selector", "")
                text = item.get("text_content", "")[:30]  # Truncate long text
                md_parts.append(f"| {pos} | `{tag}` | `{selector}` | {text} |")
            md_parts.append("")
        
        # Trigger analysis section
        trigger_results = result.get("trigger_results", [])
        if trigger_results:
            md_parts.append("### 🔘 Trigger Click Analysis")
            md_parts.append("")
            md_parts.append("Analysis of focus behavior after clicking interactive elements (F85 check).")
            md_parts.append("")
            md_parts.append("| Trigger | Dialog | Distance | Status |")
            md_parts.append("|---------|--------|----------|--------|")
            
            for res in trigger_results:
                trigger = f"`{res.get('trigger', '')}`"
                dialog = f"`{res.get('dialog', 'None')}`" if res.get('dialog') else "None"
                distance = res.get('distance', -1)
                
                status = "✅ Pass"
                if res.get('f85_violation'):
                    status = "❌ **VIOLATION (F85)**"
                elif not res.get('dialog'):
                    status = "⚠️ No Dialog Opened"
                elif distance > 1:
                     # Warn if distance is high but not strictly marked as violation yet (though logic says it is)
                     status = f"⚠️ Distance: {distance}"
                
                md_parts.append(f"| {trigger} | {dialog} | {distance} | {status} |")
            md_parts.append("")
        
        md_parts.append("---")
        md_parts.append("")
    
    md = "\n".join(md_parts)
    
    if output_path:
        Path(output_path).write_text(md, encoding='utf-8')
    
    return md
