# WCAG 2.4.3 Focus Order Test Report

**Generated:** 2026-01-11 22:35:26

## Summary

| Metric                | Value |
| --------------------- | ----- |
| Total Pages           | 2     |
| Pages with Violations | 1     |
| Pages Passed          | 1     |
| Total Violations      | 1     |

---

## ❌ https://broken-workshop.dequelabs.com/

**Violations Found:** 1

### 🔴 focus-order-semantics (minor)

Ensures elements in the focus order have a role appropriate for interactive content

📖 [Learn more](https://dequeuniversity.com/rules/axe/4.8/focus-order-semantics?application=axeAPI)

**Affected Elements:**

- `div[data-testid="chocolate-cake"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="moms-spaghetti"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="filet-mignon"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="mega-burger"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="grilled-cheese"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="lemon-squares"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="kale-salad"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```
- `div[data-testid="trail-mix"] > .Recipes__card-head > div`
  ```html
  <div tabindex="0"><img src="/pencil.e81f7a41.png" class="edit" alt="Edit" data-testid="edit-button"></div>
  ```

---

## ✅ https://www.w3.org/

> ⚠️ **Error:** Trigger tracking failed: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("button").first
    - locator resolved to <button type="button" aria-expanded="true" data-trigger="mobile-nav" class="button button--ghost with-icon--after with-icon--larger">…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
      - waiting 100ms
    59 × waiting for element to be visible, enabled and stable
       - element is not visible
     - retrying click action
       - waiting 500ms


**Status:** Pass - No violations detected

---
