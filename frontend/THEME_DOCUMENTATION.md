# ITS Frontend - Theme & Styling Documentation

This document tracks all styling and theming decisions made during the UI/UX modernization.

---

## Theme Mode

**Decision: Dark Mode** - The application will maintain a dark theme.

---

## Color Palette

Angular Material's `mat-blue-grey` palette will be used as the primary color.

### Primary Colors (Blue-Grey)
| Color Name | Hue | Hex Code | Usage |
|------------|-----|----------|-------|
| Primary    | 500 | #607D8B  | Main brand color, buttons, links |
| Primary Light | 300 | #90A4AE | Hover states, backgrounds |
| Primary Dark  | 700 | #455A64 | Active states, emphasis |
| Primary Lighter | 100 | #CFD8DC | Subtle backgrounds |
| Primary Darker | 900 | #263238 | Deep emphasis |

### Secondary/Accent Colors (Teal - Darker Tone)
| Color Name | Hue | Hex Code | Usage |
|------------|-----|----------|-------|
| Accent     | 700 | #00796B  | Secondary actions, FABs, links |
| Accent Light | 500 | #009688 | Hover states |
| Accent Dark  | 900 | #004D40 | Active states |
| Accent Lighter | 300 | #4DB6AC | Subtle highlights |

### Semantic Colors
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Success    | TBD      | Positive feedback, confirmations |
| Warning    | TBD      | Caution messages |
| Error      | TBD      | Error states, destructive actions |
| Info       | TBD      | Informational messages |

### Background & Surface Colors (Dark Theme)
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Background | #121212  | Page background (Material dark) |
| Surface    | #1E1E1E  | Cards, panels, dialogs |
| Surface Variant | #2D2D2D | Elevated surfaces |

### Text Colors
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Text Primary   | #FFFFFF  | Main text content |
| Text Secondary | rgba(255,255,255,0.7) | Secondary text, captions |
| Text Disabled  | rgba(255,255,255,0.5) | Disabled state text |

---

## Typography

### Font Stack
- **Primary Font:** TBD
- **Monospace Font:** TBD (for code)

### Type Scale
| Level   | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| H1      | TBD  | TBD    | TBD         | Page titles |
| H2      | TBD  | TBD    | TBD         | Section headers |
| H3      | TBD  | TBD    | TBD         | Subsections |
| H4      | TBD  | TBD    | TBD         | Card titles |
| H5      | TBD  | TBD    | TBD         | Small headers |
| H6      | TBD  | TBD    | TBD         | Tiny headers |
| Body 1  | TBD  | TBD    | TBD         | Main content |
| Body 2  | TBD  | TBD    | TBD         | Secondary content |
| Caption | TBD  | TBD    | TBD         | Captions, hints |
| Button  | TBD  | TBD    | TBD         | Button text |

---

## Spacing

### Spacing Scale
| Token | Value | Usage |
|-------|-------|-------|
| xs    | TBD   | Tight spacing |
| sm    | TBD   | Small gaps |
| md    | TBD   | Standard gaps |
| lg    | TBD   | Section spacing |
| xl    | TBD   | Large gaps |
| xxl   | TBD   | Page margins |

---

## Components

### Buttons
- **Primary Button:** TBD
- **Secondary Button:** TBD
- **Icon Button:** TBD
- **FAB:** TBD

### Cards
- **Elevation:** TBD
- **Border Radius:** TBD
- **Padding:** TBD

### Inputs
- **Text Field:** TBD
- **Select:** TBD
- **Checkbox:** TBD
- **Radio:** TBD

### Navigation
- **Top Bar:** TBD
- **Side Panel:** TBD
- **Tabs:** TBD

---

## Elevation & Shadows

| Level | Box Shadow | Usage |
|-------|------------|-------|
| 0     | TBD        | Flat surfaces |
| 1     | TBD        | Cards, raised elements |
| 2     | TBD        | Dropdowns, menus |
| 3     | TBD        | Dialogs, modals |
| 4     | TBD        | Floating elements |

---

## Border Radius

| Token    | Value | Usage |
|----------|-------|-------|
| none     | TBD   | Sharp corners |
| sm       | TBD   | Small radius |
| md       | TBD   | Standard radius |
| lg       | TBD   | Large radius |
| full     | TBD   | Pills, circles |

---

## Dark Mode Support

- **Status:** Confirmed - Dark mode is the default and only theme
- **Implementation:** Angular Material dark theme with `mat-blue-grey` primary
- **Color Mapping:** Material Design dark theme guidelines (#121212 background)

---

## Animation & Transitions

| Type       | Duration | Easing | Usage |
|------------|----------|--------|-------|
| Fast       | TBD      | TBD    | Hover, focus |
| Standard   | TBD      | TBD    | Page transitions |
| Slow       | TBD      | TBD    | Complex animations |

---

## Component Migration Checklist

Components to update with new theme:

- [ ] Navigation bar
- [x] Auth/Login components
- [ ] Course selection panel
- [ ] Course settings
- [x] Task panel
- [x] Action panel
- [x] Code panel (editor, multiple choice)
- [x] Feedback panel
- [x] Profile
- [ ] Skill overview
- [ ] Admin settings
- [ ] Shared components (partially - markdown-panel done)

---

## Implementation Notes

### Theme File Location
- SCSS theme: `its_ui/src/styles/_theme.scss`
- Global styles: `its_ui/src/styles.scss`

### Angular Material Customization
Theme will be customized using Angular Material's theming API:
```scss
@use '@angular/material' as mat;

$my-primary: mat.define-palette(mat.$blue-grey-palette);
$my-accent: mat.define-palette(mat.$teal-palette, 700); // Darker teal for dark theme
$my-warn: mat.define-palette(mat.$deep-orange-palette);

$my-theme: mat.define-dark-theme((
  color: (
    primary: $my-primary,
    accent: $my-accent,
    warn: $my-warn,
  ),
  typography: /* TBD */,
  density: /* TBD */,
));
```

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-04 | Dark mode confirmed | Aligns with code editor aesthetic, reduces eye strain |
| 2026-03-04 | Primary: Blue-Grey palette | Professional, neutral tone; native Angular Material support |
| 2026-03-04 | Accent: Teal (hue 700) | Darker tone works better on dark backgrounds; provides contrast without harshness |
| 2026-03-04 | Surface color (#1E1E1E) for all panels | Tutoring view panels use Surface instead of Surface Variant for a darker, more cohesive look; Monaco editor theme also updated to match |

---

## Resources

- [Angular Material Theming Guide](https://material.angular.io/guide/theming)
- [Material Design 3 Guidelines](https://m3.material.io/)
- [Material Design Color System](https://m3.material.io/styles/color/overview)
