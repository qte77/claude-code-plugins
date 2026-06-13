# WCAG 2.2 AA Quick Reference

Condensed checklist for auditing against WCAG 2.2 Level A and AA success
criteria. Organized by principle (POUR). WCAG 2.2 adds the criteria marked
"new in 2.2" below and removes 4.1.1 Parsing (now obsolete).

## 1. Perceivable

### Text Alternatives (1.1)

- **1.1.1 Non-text Content** (A) — All images, icons, and controls have
  meaningful alt text. Decorative images use `alt=""`.

### Time-based Media (1.2)

- **1.2.1 Audio/Video (prerecorded)** (A) — Captions or transcript provided
- **1.2.2 Captions (prerecorded)** (A) — Synchronized captions for video
- **1.2.3 Audio Description** (A) — Description for prerecorded video
- **1.2.4 Captions (live)** (AA) — Live captions for live video
- **1.2.5 Audio Description (prerecorded)** (AA) — Audio description track

### Adaptable (1.3)

- **1.3.1 Info and Relationships** (A) — Structure conveyed through semantic
  HTML (`<h1>`-`<h6>`, `<nav>`, `<main>`, `<table>`, `<label>`)
- **1.3.2 Meaningful Sequence** (A) — DOM order matches visual order
- **1.3.3 Sensory Characteristics** (A) — Instructions don't rely solely on
  shape, size, position, or color
- **1.3.4 Orientation** (AA) — Content not restricted to single orientation
- **1.3.5 Identify Input Purpose** (AA) — Input fields use `autocomplete`
  attributes for common personal data

### Distinguishable (1.4)

- **1.4.1 Use of Color** (A) — Color is not the only visual means of
  conveying information
- **1.4.2 Audio Control** (A) — Auto-playing audio can be paused/stopped
- **1.4.3 Contrast (Minimum)** (AA) — Text: 4.5:1, Large text: 3:1
- **1.4.4 Resize Text** (AA) — Text resizable to 200% without loss
- **1.4.5 Images of Text** (AA) — Real text used instead of images of text
- **1.4.10 Reflow** (AA) — No horizontal scroll at 320px width
- **1.4.11 Non-text Contrast** (AA) — UI components and graphics: 3:1
- **1.4.12 Text Spacing** (AA) — Content readable with increased spacing
- **1.4.13 Content on Hover/Focus** (AA) — Hover/focus popups dismissible,
  hoverable, and persistent

## 2. Operable

### Keyboard (2.1)

- **2.1.1 Keyboard** (A) — All functionality via keyboard
- **2.1.2 No Keyboard Trap** (A) — Focus can always be moved away
- **2.1.4 Character Key Shortcuts** (A) — Single-key shortcuts can be
  remapped or disabled

### Enough Time (2.2)

- **2.2.1 Timing Adjustable** (A) — Time limits can be extended or disabled
- **2.2.2 Pause, Stop, Hide** (A) — Moving/auto-updating content controllable

### Seizures (2.3)

- **2.3.1 Three Flashes** (A) — No content flashes more than 3 times/second

### Navigable (2.4)

- **2.4.1 Bypass Blocks** (A) — Skip navigation link present
- **2.4.2 Page Titled** (A) — Descriptive `<title>` on each page
- **2.4.3 Focus Order** (A) — Tab order logical and predictable
- **2.4.4 Link Purpose (In Context)** (A) — Link text meaningful in context
- **2.4.5 Multiple Ways** (AA) — Multiple paths to pages (nav, search, sitemap)
- **2.4.6 Headings and Labels** (AA) — Headings and labels are descriptive
- **2.4.7 Focus Visible** (AA) — Keyboard focus indicator is visible
- **2.4.11 Focus Not Obscured (Minimum)** (AA, new in 2.2) — Focused element
  not entirely hidden by sticky headers/footers

### Input Modalities (2.5)

- **2.5.1 Pointer Gestures** (A) — Multipoint gestures have single-pointer
  alternatives
- **2.5.2 Pointer Cancellation** (A) — Actions fire on up-event, can be
  aborted
- **2.5.3 Label in Name** (A) — Accessible name contains visible label text
- **2.5.4 Motion Actuation** (A) — Motion-triggered actions have UI
  alternatives
- **2.5.7 Dragging Movements** (AA, new in 2.2) — Drag actions have a
  single-pointer alternative
- **2.5.8 Target Size (Minimum)** (AA, new in 2.2) — Targets at least
  24x24 CSS px, or have adequate spacing

## 3. Understandable

### Readable (3.1)

- **3.1.1 Language of Page** (A) — `lang` attribute on `<html>`
- **3.1.2 Language of Parts** (AA) — `lang` attribute on foreign-language
  passages

### Predictable (3.2)

- **3.2.1 On Focus** (A) — Focus doesn't trigger unexpected context change
- **3.2.2 On Input** (A) — Input doesn't trigger unexpected context change
- **3.2.3 Consistent Navigation** (AA) — Navigation consistent across pages
- **3.2.4 Consistent Identification** (AA) — Same function = same label
- **3.2.6 Consistent Help** (A, new in 2.2) — Help mechanisms appear in a
  consistent order across pages

### Input Assistance (3.3)

- **3.3.1 Error Identification** (A) — Errors described in text
- **3.3.2 Labels or Instructions** (A) — Labels provided for input
- **3.3.3 Error Suggestion** (AA) — Suggested corrections for errors
- **3.3.4 Error Prevention (Legal/Financial)** (AA) — Submissions
  reversible, checked, or confirmed
- **3.3.7 Redundant Entry** (A, new in 2.2) — Don't ask for the same
  information twice in a process
- **3.3.8 Accessible Authentication (Minimum)** (AA, new in 2.2) — No
  cognitive-function test without an alternative

## 4. Robust

### Compatible (4.1)

- **4.1.1 Parsing** (A) — Valid HTML (no duplicate IDs, proper nesting)
- **4.1.2 Name, Role, Value** (A) — Custom components expose name, role,
  value via ARIA
- **4.1.3 Status Messages** (AA) — Status messages announced via
  `role="status"` or `aria-live`

## Contrast Ratio Cheat Sheet

| Element | Minimum Ratio |
|---------|---------------|
| Normal text (<18pt / <14pt bold) | 4.5:1 |
| Large text (>=18pt / >=14pt bold) | 3:1 |
| UI components and graphics | 3:1 |
| Inactive controls, decorative | No requirement |

## Common Fix Patterns

- **Missing alt**: `<img alt="Description of content">`
- **Missing lang**: `<html lang="en">`
- **Missing skip link**: `<a href="#main" class="skip-link">Skip to content</a>`
- **Low contrast**: Adjust foreground/background to meet ratio
- **Missing label**: `<label for="input-id">` or `aria-label="..."`
- **Focus trap**: Ensure `keydown` handlers don't prevent Tab
- **Missing live region**: `<div role="status" aria-live="polite">`
