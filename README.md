# Focus Order Tester

A batch testing tool for **WCAG 2.1 Success Criterion 2.4.3 (Focus Order)** compliance using axe-core and Playwright.

## Features

- 🔍 Detects focus order violations using axe-core rules
- 📊 Generates reports in JSON, HTML, or Markdown format
- 🚀 Batch processing of multiple URLs
- 🧪 66 unit tests with TDD methodology

## Detected Rules

| Rule                    | Impact  | Description                                           |
| ----------------------- | ------- | ----------------------------------------------------- |
| `tabindex`              | serious | tabindex > 0 creates non-natural focus order          |
| `focus-order-semantics` | minor   | Elements in focus order should have interactive roles |
| `nested-interactive`    | serious | Nested interactive controls cause focus issues        |
| `aria-hidden-focus`     | serious | aria-hidden elements shouldn't be focusable           |

## Installation

```bash
# Clone the repository
git clone https://github.com/zwrong/Web-Accessibility.git
cd Web-Accessibility

# Create and activate conda environment
conda create -n webAccess python=3.11 -y
conda activate webAccess

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Usage

### Basic Usage

```bash
# Test a single URL
python -m focus_order_tester.main https://example.com

# Test multiple URLs
python -m focus_order_tester.main https://a.com https://b.com
```

### Output Options

```bash
# Save as JSON (default)
python -m focus_order_tester.main https://example.com -o report.json

# Save as HTML
python -m focus_order_tester.main https://example.com --format html -o report.html

# Save as Markdown
python -m focus_order_tester.main https://example.com --format md -o report.md
```

### Batch Testing from File

```bash
# Create a file with URLs (one per line)
echo "https://example1.com
https://example2.com
https://example3.com" > urls.txt

# Run batch test
python -m focus_order_tester.main --file urls.txt -o batch_report.md --format md
```

### Local HTML Files

```bash
# Test local HTML files
python -m focus_order_tester.main "file:///path/to/your/page.html"
```

## CLI Options

| Option          | Short | Description                            |
| --------------- | ----- | -------------------------------------- |
| `--file`        | `-f`  | File containing URLs (one per line)    |
| `--output`      | `-o`  | Output file path for the report        |
| `--format`      |       | Output format: `json`, `html`, or `md` |
| `--no-headless` |       | Run browser in visible mode            |
| `--trace-focus` |       | Include focus path tracing             |

## Running Tests

```bash
conda activate webAccess
pytest tests/ -v
```

## Project Structure

```
focus_order_tester/
├── __init__.py
├── url_handler.py      # URL parsing and validation
├── axe_runner.py       # axe-core integration
├── focus_tracer.py     # Tab key simulation
├── report_generator.py # JSON/HTML/MD reports
└── main.py             # CLI entry point

tests/
├── fixtures/           # Test HTML files (F44, F85)
├── test_url_handler.py
├── test_axe_runner.py
├── test_focus_tracer.py
├── test_report_generator.py
└── test_main.py
```

## Test Fixtures

Based on W3C WCAG failure techniques:

- `f44_bad_tabindex.html` - Elements with tabindex > 0
- `f85_dialog_position.html` - Dialog not adjacent to trigger
- `pass_example.html` - Correct focus order (no violations)

## Example Output

```markdown
# WCAG 2.4.3 Focus Order Test Report

## Summary

| Metric                | Value |
| --------------------- | ----- |
| Total Pages           | 3     |
| Pages with Violations | 1     |
| Pages Passed          | 2     |

## ❌ https://example.com

**Violations Found:** 1

### 🔴 tabindex (serious)

Elements should not have tabindex greater than 0

**Affected Elements:**
- `li:nth-child(1) > a`
  ```html
  <a href="#" tabindex="1">Homepage</a>
  ```


## License

MIT
