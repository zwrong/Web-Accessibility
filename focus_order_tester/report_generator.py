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
