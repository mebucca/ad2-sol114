#!/usr/bin/env python3
"""Fix issues in all Quarto RevealJS presentations:
1. Math rendering: switch to KaTeX (fixes underbrace/mathbb font issues)
2. Section slide backgrounds: add data-background-color to .inverse slides
3. Slide number: remove slide index from side
4. Image captions: hide figcaption labels shown by markdown ![label](link)
5. Scientific notation: restore options(scipen=999) for classes that had it
"""

import re
from pathlib import Path

BASE = Path("/Users/mebucca/Library/Mobile Documents/com~apple~CloudDocs/Teaching/ISUC/2026_1_pie/repo/slides")

# Classes whose original Rmd had options(scipen=999)
SCIPEN_CLASSES = {'class_18', 'class_19', 'class_20', 'class_21',
                  'class_22', 'class_23', 'class_24', 'class_25'}

# CSS rule to hide image labels (figcaption from markdown images)
FIGCAPTION_CSS = """
/* Hide image labels from markdown ![label](path) syntax */
.reveal figure figcaption {
  display: none !important;
}
"""


def get_inverse_colors(themer_css_path):
    """Read inverse background and text color from xaringan-themer.css."""
    default_bg = '#F4C430'
    default_text = '#000000'
    if not themer_css_path.exists():
        return default_bg, default_text
    css = themer_css_path.read_text()
    bg_m = re.search(r'--inverse-background-color:\s*(#[0-9A-Fa-f]+)', css)
    tx_m = re.search(r'--inverse-text-color:\s*(#[0-9A-Fa-f]+)', css)
    inv_bg = bg_m.group(1) if bg_m else default_bg
    inv_text = tx_m.group(1) if tx_m else default_text
    return inv_bg, inv_text


def fix_qmd(qmd_path, inv_bg, inv_text, class_name):
    """Apply all fixes to a single QMD file."""
    qmd = qmd_path.read_text(encoding='utf-8')
    changes = []

    # ── Fix 1: switch to KaTeX ────────────────────────────────────────────
    if 'html-math-method' not in qmd:
        # Insert after "height: 900"
        qmd = qmd.replace(
            '    height: 900\n',
            '    height: 900\n    html-math-method: katex\n'
        )
        changes.append('add html-math-method: katex')

    # ── Fix 2: remove slide number ────────────────────────────────────────
    if 'slide-number: true' in qmd:
        qmd = qmd.replace('slide-number: true', 'slide-number: false')
        changes.append('slide-number: false')

    # ── Fix 3: add background-color to .inverse slide headers ─────────────
    # Patterns:
    #   ## Title {.inverse .center .middle .section-title}
    #   ## Hasta la próxima clase. Gracias! {.inverse .center .middle}
    #   ## {.inverse .center .middle}
    def add_bg(m):
        prefix = m.group(1)   # e.g. "## Title " or "## "
        attrs  = m.group(2)   # e.g. ".inverse .center .middle .section-title"
        if 'background-color=' in attrs:
            return m.group(0)  # already fixed
        return f'{prefix}{{background-color="{inv_bg}" {attrs}}}'

    new_qmd = re.sub(
        r'^(## [^{\n]*)\{([^}\n]*\.inverse[^}\n]*)\}',
        add_bg,
        qmd,
        flags=re.MULTILINE
    )
    if new_qmd != qmd:
        changes.append('add background-color to .inverse slides')
        qmd = new_qmd

    # ── Fix 4: ensure text colors are visible on .inverse slides ──────────
    # Add !important to inverse text/header color rules in the CSS string
    # (handled in CSS fix below, not in QMD)

    # ── Fix 5: restore options(scipen=999) for scientific notation ─────────
    if class_name in SCIPEN_CLASSES and 'scipen' not in qmd:
        # Try common setup chunk patterns
        for pattern in [
            'knitr::opts_chunk$set(eval = T, echo = T)',
            'knitr::opts_chunk$set(eval = TRUE, echo = TRUE)',
            'knitr::opts_chunk$set(',
        ]:
            if pattern in qmd:
                qmd = qmd.replace(pattern, 'options(scipen=999)\n' + pattern, 1)
                changes.append('add options(scipen=999)')
                break
        else:
            # If no setup chunk found, add one after the first ```{r
            # setup chunk with include=FALSE
            setup_chunk = '```{r setup, include=FALSE}\noptions(scipen=999)\nknitr::opts_chunk$set(eval = T, echo = T)\n```'
            # Find the first code chunk
            first_chunk = qmd.find('```{r')
            if first_chunk >= 0:
                # Insert before first chunk
                qmd = qmd[:first_chunk] + setup_chunk + '\n\n' + qmd[first_chunk:]
                changes.append('insert setup chunk with options(scipen=999)')

    if changes:
        qmd_path.write_text(qmd, encoding='utf-8')
        print(f"  [{class_name}] QMD: {', '.join(changes)}")
    else:
        print(f"  [{class_name}] QMD: no changes needed")

    return qmd


def fix_gentle_css(css_path, class_name):
    """Add figcaption hide rule to gentle-r.css."""
    if not css_path.exists():
        return
    gcss = css_path.read_text(encoding='utf-8')
    if 'figcaption' not in gcss:
        gcss = gcss.rstrip() + '\n' + FIGCAPTION_CSS
        css_path.write_text(gcss, encoding='utf-8')
        print(f"  [{class_name}] gentle-r.css: added figcaption rule")


def fix_themer_css(css_path, class_name):
    """Strengthen inverse text color rules with !important."""
    if not css_path.exists():
        return
    css = css_path.read_text(encoding='utf-8')
    changed = False

    # Make inverse text color use !important (so Quarto default theme can't override)
    # Pattern 1: color: var(--inverse-text-color); without !important inside .inverse block
    # Pattern 2: inverse h1/h2/h3 color without !important

    # Fix inverse section text color
    old1 = '  color: var(--inverse-text-color);\n}'
    new1 = '  color: var(--inverse-text-color) !important;\n}'
    if old1 in css and 'color: var(--inverse-text-color) !important' not in css:
        css = css.replace(old1, new1, 1)
        changed = True

    # Fix inverse h1/h2/h3 color
    old2 = '  color: var(--inverse-header-color);\n}'
    new2 = '  color: var(--inverse-header-color) !important;\n}'
    if old2 in css and 'color: var(--inverse-header-color) !important' not in css:
        css = css.replace(old2, new2, 1)
        changed = True

    # Remove height: 100% from inverse section (not needed when using data-background-color)
    # Keep it as it doesn't cause harm

    if changed:
        css_path.write_text(css, encoding='utf-8')
        print(f"  [{class_name}] xaringan-themer.css: strengthened inverse text color rules")


def process_class(class_n):
    """Process a single class directory."""
    class_name = f'class_{class_n}'
    class_dir = BASE / class_name
    qmd_file = class_dir / f'{class_name}.qmd'
    themer_css = class_dir / 'xaringan-themer.css'
    gentle_css = class_dir / 'gentle-r.css'

    if not qmd_file.exists():
        print(f"  [{class_name}] Skipping: no QMD file found")
        return

    inv_bg, inv_text = get_inverse_colors(themer_css)
    fix_qmd(qmd_file, inv_bg, inv_text, class_name)
    fix_gentle_css(gentle_css, class_name)
    fix_themer_css(themer_css, class_name)


def main():
    print("Fixing Quarto RevealJS presentations...\n")
    for n in range(0, 26):
        process_class(n)
    print("\nDone!")


if __name__ == '__main__':
    main()
