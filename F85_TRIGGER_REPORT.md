# WCAG 2.4.3 Focus Order Test Report

**Generated:** 2026-01-11 22:13:06

## Summary

| Metric | Value |
|--------|-------|
| Total Pages | 1 |
| Pages with Violations | 1 |
| Pages Passed | 0 |
| Total Violations | 1 |

---

## ❌ file:///Users/vinen/Documents/Vscode_Kiro/Web-Accessibility/tests/fixtures/f85_dialog_position.html

**Violations Found:** 1

### 🔴 wcag243-f85-dialog-position (serious)

Focus Order Failure (F85): Dialog '#dialog' is not adjacent to trigger '#open-dialog' in focus order.

📖 [Learn more](https://www.w3.org/WAI/WCAG21/Techniques/failures/F85)

**Affected Elements:**

- ``
  ```html
  <button>Open Dialog</button> ... <dialog>...
  ```

### 🔘 Trigger Click Analysis

Analysis of focus behavior after clicking interactive elements (F85 check).

| Trigger | Dialog | Distance | Status |
|---------|--------|----------|--------|
| `#open-dialog` | `#dialog` | 7 | ❌ **VIOLATION (F85)** |

---
