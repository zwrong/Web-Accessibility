"""
Main Entry Point for Focus Order Tester

Batch processor for WCAG SC 2.4.3 Focus Order testing.

Usage:
    python -m focus_order_tester.main https://example.com
    python -m focus_order_tester.main --file urls.txt --output report.json
"""
import argparse
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

from .url_handler import parse_urls, read_urls_from_file, validate_url
from .axe_runner import AxeRunner, run_axe_analysis
from .focus_tracer import trace_focus_path
from .trigger_tracker import TriggerTracker
from .report_generator import generate_json_report, generate_html_report, generate_md_report


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: List of arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="WCAG SC 2.4.3 Focus Order Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s https://example.com
    %(prog)s https://a.com https://b.com --output report.json
    %(prog)s --file urls.txt --format html --output report.html
        """
    )
    
    parser.add_argument(
        "urls",
        nargs="*",
        default=[],
        help="URLs to test"
    )
    
    parser.add_argument(
        "--file", "-f",
        dest="file",
        help="File containing URLs (one per line)"
    )
    
    parser.add_argument(
        "--output", "-o",
        dest="output",
        help="Output file path for the report"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "html", "md"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        default=True,
        help="Run browser in visible mode"
    )
    
    parser.add_argument(
        "--trace-focus",
        action="store_true",
        help="Include focus path tracing in the report"
    )
    
    parser.add_argument(
        "--trace-triggers",
        action="store_true",
        help="Trace focus after clicking trigger elements (for F85 detection)"
    )
    
    return parser.parse_args(args)


async def process_urls(
    urls: List[str],
    headless: bool = True,
    trace_focus: bool = False,
    trace_triggers: bool = False
) -> List[Dict[str, Any]]:
    """
    Process multiple URLs for focus order testing.
    
    Args:
        urls: List of URLs to test
        headless: Whether to run browser in headless mode
        urls: List of URLs to test
        headless: Whether to run browser in headless mode
        trace_focus: Whether to include focus path tracing
        trace_triggers: Whether to include click trigger tracking (F85)
        
    Returns:
        List of results for each URL
    """
    results = []
    
    async with AxeRunner(headless=headless) as runner:
        for url in urls:
            result = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "violations": [],
                "violation_count": 0,
                "error": None
            }
            
            # Axe Analysis
            try:
                violations = await runner.analyze(url)
                result["violations"] = [
                    {
                        "rule_id": v.rule_id,
                        "description": v.description,
                        "impact": v.impact,
                        "help_url": v.help_url,
                        "nodes": v.nodes
                    }
                    for v in violations
                ]
                result["violation_count"] += len(violations)
            except Exception as e:
                # Capture Axe error but continue to other checks
                error_msg = f"Axe analysis failed: {str(e)}"
                result["error"] = error_msg if not result["error"] else f"{result['error']}; {error_msg}"
                print(f"⚠️ {error_msg}")

            # Focus path tracing verification
            if trace_focus:
                try:
                    trace_result = await trace_focus_path(url, headless=headless)
                    result["focus_path"] = trace_result.get("focus_path", [])
                    result["focus_element_count"] = trace_result.get("element_count", 0)
                except Exception as e:
                     error_msg = f"Focus tracing failed: {str(e)}"
                     result["error"] = error_msg if not result["error"] else f"{result['error']}; {error_msg}"
                     print(f"⚠️ {error_msg}")
            
            # Trigger tracking (F85)
            if trace_triggers:
                try:
                    async with TriggerTracker(headless=headless) as tracker:
                        trigger_results = await tracker.analyze_f85(url)
                        result["trigger_results"] = [
                            {
                                "trigger": r.trigger_selector,
                                "trigger_text": r.trigger_text,
                                "dialog": r.dialog_selector,
                                "distance": r.distance,
                                "is_adjacent": r.is_adjacent,
                                "f85_violation": r.f85_violation,
                                "focus_path": [
                                    {"tag": e.tag_name, "text": e.text_content} 
                                    for e in r.focus_path_after_click
                                ]
                            }
                            for r in trigger_results
                        ]
                        
                        # Add specific F85 violation if detected
                        for r in trigger_results:
                            if r.f85_violation:
                                result["violations"].append({
                                    "rule_id": "wcag243-f85-dialog-position",
                                    "impact": "serious",
                                    "description": f"Focus Order Failure (F85): Dialog '{r.dialog_selector}' is not adjacent to trigger '{r.trigger_selector}' in focus order.",
                                    "help_url": "https://www.w3.org/WAI/WCAG21/Techniques/failures/F85",
                                    "nodes": [{"html": f"<button>{r.trigger_text}</button> ... <dialog>..."}]
                                })
                                result["violation_count"] += 1
                except Exception as e:
                     error_msg = f"Trigger tracking failed: {str(e)}"
                     result["error"] = error_msg if not result["error"] else f"{result['error']}; {error_msg}"
                     print(f"⚠️ {error_msg}")

            results.append(result)
            print(f"✓ Processed: {url} ({result.get('violation_count', 0)} violations)")
    
    return results



async def main(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the focus order tester.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
    """
    parsed = parse_args(args)
    
    # Collect URLs
    urls = list(parsed.urls)
    
    if parsed.file:
        try:
            file_urls = read_urls_from_file(parsed.file)
            urls.extend(file_urls)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    if not urls:
        print("Error: No URLs provided. Use positional arguments or --file option.", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n🔍 Testing {len(urls)} URL(s) for WCAG SC 2.4.3 Focus Order...\n")
    
    # Process URLs
    results = await process_urls(
        urls,
        headless=parsed.headless,
        trace_focus=getattr(parsed, 'trace_focus', False),
        trace_triggers=getattr(parsed, 'trace_triggers', False)
    )
    
    # Generate report
    if parsed.format == "html":
        report = generate_html_report(results, output_path=parsed.output)
    elif parsed.format == "md":
        report = generate_md_report(results, output_path=parsed.output)
    else:
        report = generate_json_report(results, output_path=parsed.output)
    
    # Print summary
    violations_count = sum(r.get("violation_count", 0) for r in results)
    pages_with_issues = sum(1 for r in results if r.get("violation_count", 0) > 0)
    
    print(f"\n📊 Summary:")
    print(f"   Total pages: {len(results)}")
    print(f"   Pages with violations: {pages_with_issues}")
    print(f"   Total violations: {violations_count}")
    
    if parsed.output:
        print(f"\n📄 Report saved to: {parsed.output}")
    else:
        print(f"\n{report}")


def run():
    """Entry point for console script"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
