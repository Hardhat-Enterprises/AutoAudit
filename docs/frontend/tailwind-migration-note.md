# TailwindCSS Migration Research Note (AutoAudit Frontend)

## Purpose

This note documents the justification behind moving from vanilla CSS to TailwindCSS and consolidating multiple CSS files into a single global stylesheet.

## Scope
- Frontend and UI only

## Motivation for Migration

### 1. **Reduced CSS File Complexity**
- **Before**: Multiple CSS files scattered across the project (components, layouts, utilities, etc.)
- **After**: Single consolidated global stylesheet with Tailwind utilities
- **Benefit**: Eliminates CSS file fragmentation, reduces import chains, and simplifies maintenance

### 2. **Utility-First Approach**
- Tailwind's utility-first methodology eliminates the need to create custom CSS classes
- Developers can compose styles directly in HTML/JSX markup
- Reduces context switching between template and CSS files

### 3. **Consistency & Design System**
- Enforces consistent spacing, colors, typography, and breakpoints across the entire project
- Configuration-driven design system ensures no arbitrary values
- Easier to maintain brand consistency

### 4. **Smaller Bundle Size**
- Tailwind's purging removes unused styles at build time
- Eliminates dead CSS code that accumulated in multiple files
- Better performance for end users

### 5. **Developer Productivity**
- Faster development with instant visual feedback
- No naming conventions to worry about (BEM, OOCSS, etc.)
- IntelliSense/autocomplete for utility classes

### 6. **Maintainability**
- Single source of truth for global styles
- Easier onboarding for new developers
- Simplified refactoring and design updates

## Implementation Details

- Single Global CSS file: `index.css` serves as the primary source stylesheet
  - Includes all CSS variables
  - Includes TailwindCSS directives: `@tailwind`, `@apply`, `@theme`

## Notes

- To make it easier to maintain, please use globalised CSS colour variables in TailwindCSS
- The version is TailwindCSS v4, while a lot of AI models are still trained on v3 primarily. Mitigations:
  - Include TailwindCSS v4 in the prompt
  - Install VSCode or Cursor extensions to easily migrate from TailwindCSS v3 to v4
- (Optional) To make TailwindCSS classes sort in order without affecting spacing (which Prettier may affect), RustyWind is an option:
  - https://github.com/avencera/rustywind
  - Installed globally
    ```
    cd frontend
    npm install -g rustywind
    rustywind . --write
    ```