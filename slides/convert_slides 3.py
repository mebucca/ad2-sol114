#!/usr/bin/env python3
"""Convert xaringan Rmd presentations to Quarto RevealJS qmd."""

import re
import sys
import os
from pathlib import Path

# Colors per class: title_bg = title slide bg, inverse_bg = inverse slide bg
CLASS_COLORS = {
    'class_0':  {'title_bg': '#972D15',   'inverse_bg': '#1f2026'},
    'class_1':  {'title_bg': '#01647F',   'inverse_bg': '#FF4500'},
    'class_2':  {'title_bg': '#a57688',   'inverse_bg': '#6fbbca'},
    'class_3':  {'title_bg': '#719379',   'inverse_bg': '#c3aef2'},
    'class_4':  {'title_bg': '#F57C6C',   'inverse_bg': '#6A8EAE'},
    'class_5':  {'title_bg': '#ff7377',   'inverse_bg': '#ffec73'},
    'class_6':  {'title_bg': '#4953A6',   'inverse_bg': '#FFD58D'},
    'class_7':  {'title_bg': '#D18229',   'inverse_bg': '#4E5354'},
    'class_8':  {'title_bg': '#003366',   'inverse_bg': '#FFFFF0'},
    'class_9':  {'title_bg': '#4B6F44',   'inverse_bg': '#F4C430'},
    'class_10': {'title_bg': '#4B6F44',   'inverse_bg': '#F4C430'},
    'class_11': {'title_bg': '#D32F2F',   'inverse_bg': '#FAD9A1'},
    'class_12': {'title_bg': '#1F3C88',   'inverse_bg': '#DAA996'},
    'class_13': {'title_bg': '#A67C52',   'inverse_bg': '#FAF3E0'},
    'class_14': {'title_bg': '#228B22',   'inverse_bg': '#4B0082'},
    'class_15': {'title_bg': '#744B22',   'inverse_bg': '#3B4082'},
    'class_16': {'title_bg': '#D6523C',   'inverse_bg': '#34B334'},
    'class_17': {'title_bg': '#008C45',   'inverse_bg': '#3949AB'},
    'class_18': {'title_bg': '#A0522D',   'inverse_bg': '#ADD8E6'},
    'class_19': {'title_bg': '#A0522D',   'inverse_bg': '#ADD8E6'},
    'class_20': {'title_bg': '#6CABDD',   'inverse_bg': '#1C2C5B'},
    'class_21': {'title_bg': '#A51C30',   'inverse_bg': '#000000'},
    'class_22': {'title_bg': '#C80815',   'inverse_bg': '#007FFF'},
    'class_23': {'title_bg': '#1D1D1F',   'inverse_bg': '#50B2BE'},
    'class_24': {'title_bg': '#4682B4',   'inverse_bg': '#CD5C5C'},
    'class_25': {'title_bg': '#00634E',   'inverse_bg': '#003E30'},
}

REVEALJS_CSS_ADDON = """
/* ============================================================
 * Quarto RevealJS compatibility
 * ============================================================ */

/* Base font/color applied via reveal root */
.reveal {
  font-family: var(--text-font-family), var(--text-font-family-fallback), var(--text-font-base);
  font-size: var(--base-font-size);
  color: var(--text-color);
  background-color: var(--background-color);
}

.reveal .slides section {
  padding: 16px 64px 16px 64px;
  box-sizing: border-box;
  text-align: left;
}

/* Headings */
.reveal h1, .reveal h2, .reveal h3,
.reveal h4, .reveal h5, .reveal h6 {
  font-family: var(--header-font-family), var(--header-font-family-fallback);
  font-weight: 600;
  color: var(--header-color);
  text-transform: none;
  letter-spacing: normal;
}

.reveal h1 { font-size: var(--header-h1-font-size); }
.reveal h2 { font-size: var(--header-h2-font-size); }
.reveal h3 { font-size: var(--header-h3-font-size); }

/* Section-title slides: make h2 as large as h1 */
.reveal section.section-title h2 {
  font-size: var(--header-h1-font-size);
}

/* Middle vertical centering */
.reveal section.middle {
  display: flex !important;
  flex-direction: column;
  justify-content: center;
  align-items: normal;
}

/* Code blocks */
.reveal pre {
  width: 100%;
  box-shadow: none;
}

.reveal pre code,
.reveal .sourceCode code {
  font-family: var(--code-font-family), Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace;
  font-size: var(--code-font-size);
  max-height: none;
}

/* Inline code */
.reveal p code, .reveal li code, .reveal td code, .reveal th code {
  font-family: var(--code-font-family), Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace;
  font-size: var(--code-inline-font-size);
  color: var(--secondary);
  background-color: #F5F5F5;
  border-radius: 3px;
  padding: 2px 4px;
}

/* Slide number */
.reveal .slide-number {
  background-color: transparent;
  color: var(--header-color);
  font-size: 0.9rem;
  opacity: 1;
}

/* Bold and links */
.reveal strong {
  color: var(--text-bold-color);
}

.reveal a, .reveal a > code {
  color: var(--link-color);
  text-decoration: none;
}

/* Inverse (section break) slides */
.reveal section.inverse {
  background-color: var(--inverse-background-color) !important;
  color: var(--inverse-text-color);
}

.reveal section.inverse h1,
.reveal section.inverse h2,
.reveal section.inverse h3 {
  color: var(--inverse-header-color);
}

.reveal section.inverse a,
.reveal section.inverse a > code {
  color: var(--inverse-link-color);
}

.reveal section.inverse .slide-number {
  display: none;
}

/* Center alignment for slides */
.reveal section.center {
  text-align: center;
}

/* Title slide */
#title-slide {
  background-color: var(--title-slide-background-color);
  text-align: center;
}

#title-slide h1, #title-slide h2, #title-slide h3,
#title-slide .subtitle, #title-slide .author, #title-slide .date {
  color: var(--title-slide-text-color);
}

/* Tables */
.reveal table {
  margin: auto;
  border-top: 1px solid #666;
  border-bottom: 1px solid #666;
}

.reveal table thead th {
  border-bottom: 1px solid #ddd;
}

.reveal table:not(.table-unshaded) thead,
.reveal table:not(.table-unshaded) tfoot,
.reveal table:not(.table-unshaded) tr:nth-child(even) {
  background: #D2D2D3;
}

/* Blockquote */
.reveal blockquote {
  border-left: solid 5px var(--secondary, #1f202680);
  padding-left: 1em;
  background: transparent;
  box-shadow: none;
  font-style: normal;
  width: 100%;
}

/* Column layout: use float (matches existing .pull-left/.pull-right CSS) */
.reveal .pull-left {
  float: left;
  width: 47%;
}

.reveal .pull-right {
  float: right;
  width: 47%;
}

.reveal .pull-right + * {
  clear: both;
}

/* Code-plot layout */
.reveal .left-code {
  float: left;
  width: 38%;
  height: 92%;
}

.reveal .right-plot {
  float: right;
  width: 60%;
}

/* Content boxes - ensure display */
.reveal .content-box-primary,
.reveal .content-box-secondary,
.reveal .content-box-blue,
.reveal .content-box-gray,
.reveal .content-box-grey,
.reveal .content-box-green,
.reveal .content-box-purple,
.reveal .content-box-red,
.reveal .content-box-yellow {
  border-radius: 0;
  padding: 15px 20px;
  margin: 0 0 15px;
  display: block;
}

/* Full width wrapper */
.reveal .full-width {
  display: block;
  width: 100%;
}
"""

GENTLE_R_CSS_ADDON = """
/* ============================================================
 * Quarto RevealJS compatibility
 * ============================================================ */

.reveal .slides section {
  font-size: 20px;
}

.reveal pre code {
  font-size: 0.9em;
}

.reveal .footnote {
  position: absolute;
  bottom: 60px;
  padding-right: 4em;
  font-size: 60%;
}
"""


def find_matching_bracket(text, start):
    """Find closing ] matching [ at position start."""
    assert text[start] == '[', f"Expected '[' at position {start}, got '{text[start]}'"
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def convert_class_markup(text):
    """Convert .class[content] patterns to Quarto syntax."""
    result = []
    i = 0

    while i < len(text):
        # Skip fenced code blocks ```...```
        if text[i:i+3] == '```':
            end = text.find('\n```', i + 3)
            if end >= 0:
                result.append(text[i:end + 4])
                i = end + 4
                continue
            else:
                result.append(text[i:])
                break

        # Skip inline backtick code
        if text[i] == '`' and (i == 0 or text[i-1] != '`'):
            end = text.find('`', i + 1)
            if end >= 0 and text[end-1] != '\\':
                result.append(text[i:end + 1])
                i = end + 1
                continue

        # Look for .classname[ pattern
        # Must be preceded by space, newline, (, [ or start of string
        if text[i] == '.':
            m = re.match(r'\.([a-zA-Z][a-zA-Z0-9_-]*)\[', text[i:])
            if m and (i == 0 or text[i-1] in ' \t\n([{'):
                class_name = m.group(1)
                bracket_start = i + len(m.group(0)) - 1  # position of [
                bracket_end = find_matching_bracket(text, bracket_start)

                if bracket_end >= 0:
                    content = text[bracket_start + 1:bracket_end]
                    # Recursively convert nested markup
                    converted_content = convert_class_markup(content)

                    # Decide: span (inline) or div (block)
                    is_block = (
                        '\n' in content.strip() or
                        re.search(r'!\[', content) or
                        re.search(r'\$\$', content) or   # display math
                        re.search(r'\\begin\{', content) or  # LaTeX environments
                        class_name in ('pull-left', 'pull-right', 'pull-rigth',
                                       'left-code', 'right-plot', 'center',
                                       'full-width', 'figure-right', 'img-right',
                                       'plot-callout')
                    )

                    if is_block:
                        stripped = converted_content.strip()
                        result.append(f'\n::: {{.{class_name}}}\n{stripped}\n:::\n')
                    else:
                        result.append(f'[{converted_content}]{{.{class_name}}}')

                    i = bracket_end + 1
                    continue

        result.append(text[i])
        i += 1

    return ''.join(result)


def convert_incremental(text):
    """Convert xaringan -- incremental reveals to Quarto . . ."""
    # A line with only -- (possibly with trailing whitespace)
    text = re.sub(r'\n--[ \t]*\n', '\n\n. . .\n\n', text)
    text = re.sub(r'^--[ \t]*\n', '. . .\n\n', text)
    return text


def extract_slide_classes(slide_text):
    """Extract and remove class: ... line from slide text."""
    lines = slide_text.split('\n')
    classes = None
    new_lines = []
    found = False

    for line in lines:
        m = re.match(r'^class:\s*(.+)', line.strip())
        if m and not found:
            class_str = m.group(1)
            classes = [c.strip() for c in class_str.split(',')]
            found = True
        else:
            new_lines.append(line)

    return classes, '\n'.join(new_lines)


def normalize_headings(text):
    """Fix headings that lack the required space (##Title → ## Title)."""
    return re.sub(r'^(#{1,6})(?=[^ \t#\n])', r'\1 ', text, flags=re.MULTILINE)


def convert_slide(slide_text, is_first=False):
    """Convert a single slide from xaringan to Quarto RevealJS syntax."""
    if is_first:
        # First "slide" is pre-YAML content (setup chunk etc.) — remove it
        return ''

    # Extract slide-level classes
    classes, slide_text = extract_slide_classes(slide_text)

    # Fix headings that lack the space (##Title → ## Title)
    slide_text = normalize_headings(slide_text)

    # Strip leading/trailing blank lines
    slide_text = slide_text.strip()

    if not slide_text and not classes:
        return ''

    # Convert incremental reveals
    slide_text = convert_incremental(slide_text)

    # Convert .class[content] markup
    slide_text = convert_class_markup(slide_text)

    # Clean up extra blank lines (max 2 consecutive)
    slide_text = re.sub(r'\n{3,}', '\n\n', slide_text)

    # Find the first heading in the slide (must have space after #)
    heading_match = re.search(r'^(#{1,6}) (.+?)$', slide_text, re.MULTILINE)

    if classes:
        classes_attr = ' '.join(f'.{c}' for c in classes)

        if heading_match and heading_match.start() == 0:
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            # Remove existing {} if any
            heading_text = re.sub(r'\s*\{[^}]*\}\s*$', '', heading_text).strip()

            if heading_level == 1:
                # # Title on inverse/section slide → ## Title {.classes .section-title}
                new_heading = f'## {heading_text} {{{classes_attr} .section-title}}'
                slide_text = new_heading + slide_text[heading_match.end():]
            elif heading_level == 2:
                # ## Title → ## Title {.classes}
                new_heading = f'## {heading_text} {{{classes_attr}}}'
                slide_text = new_heading + slide_text[heading_match.end():]
            else:
                # ### or lower → wrap with ## {.classes}
                slide_text = f'## {{{classes_attr}}}\n\n{slide_text}'
        else:
            # No heading at start → wrap with ## {.classes}
            slide_text = f'## {{{classes_attr}}}\n\n{slide_text}'
    else:
        # No classes — keep content as-is
        # If first line is ## heading, it will serve as slide separator in Quarto
        # Otherwise, we need --- separator
        if not (heading_match and
                len(heading_match.group(1)) == 2 and
                heading_match.start() == 0):
            slide_text = f'---\n\n{slide_text}'

    return slide_text.strip()


def split_slides(body):
    """Split document body into slides on --- separators (not inside code blocks)."""
    parts = []
    current = []
    lines = body.split('\n')
    in_code_block = False

    for line in lines:
        # Track fenced code blocks
        if re.match(r'^```', line):
            in_code_block = not in_code_block

        if not in_code_block and re.match(r'^---+\s*$', line):
            parts.append('\n'.join(current))
            current = []
        else:
            current.append(line)

    if current:
        parts.append('\n'.join(current))

    return parts


def remove_setup_chunks(text):
    """Remove xaringan-themer setup code chunks."""
    # Remove named chunk {r xaringan-themer, ...}
    text = re.sub(
        r'```\{r\s+xaringan-themer[^}]*\}.*?```',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    return text.strip()


def convert_yaml(yaml_str, title_bg_color):
    """Convert xaringan YAML header to Quarto RevealJS format."""
    lines = yaml_str.split('\n')
    result = []
    skip = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if skip:
            # Still inside an indented block — check if we're done
            if line and not line[0] in ' \t':
                skip = False
                # Fall through to process this line
            else:
                i += 1
                continue

        if re.match(r'^output\s*:', stripped):
            skip = True
            result.extend([
                'format:',
                '  revealjs:',
                '    css: ["gentle-r.css","xaringan-themer.css"]',
                '    slide-number: true',
                '    theme: default',
                '    highlight-style: github',
                '    width: 1600',
                '    height: 900',
                '    title-slide-attributes:',
                f'      data-background-color: "{title_bg_color}"',
            ])
        elif re.match(r'^editor_options\s*:', stripped):
            skip = True  # Skip editor_options block
        elif re.match(r'^date\s*:', stripped):
            result.append('date: today')
        else:
            result.append(line)

        i += 1

    return '\n'.join(result)


def convert_rmd_to_qmd(rmd_content, title_bg_color):
    """Convert full Rmd content to Quarto qmd content."""
    # Extract YAML front matter
    if not rmd_content.startswith('---'):
        return rmd_content

    yaml_end = rmd_content.find('\n---', 3)
    if yaml_end < 0:
        return rmd_content

    yaml_str = rmd_content[3:yaml_end].strip()
    body = rmd_content[yaml_end + 4:]  # Skip \n---\n

    # Convert YAML
    new_yaml = convert_yaml(yaml_str, title_bg_color)

    # Split body into slides
    slides = split_slides(body)

    # Convert each slide
    converted_slides = []
    for idx, slide in enumerate(slides):
        if idx == 0:
            # First part: pre-first-separator content (setup chunks, etc.)
            cleaned = remove_setup_chunks(slide)
            # Check if there's meaningful content (other than blank lines)
            if cleaned.strip():
                # Treat this as a regular slide (some Rmd files put first slide here)
                converted = convert_slide(cleaned, is_first=False)
                if converted:
                    converted_slides.append(converted)
        else:
            converted = convert_slide(slide)
            if converted:
                converted_slides.append(converted)

    # Join slides
    body_result = '\n\n'.join(converted_slides)

    return f'---\n{new_yaml}\n---\n\n{body_result}\n'


def _replace_or_append_addon(css_path, addon):
    """Replace existing addon block or append it."""
    with open(css_path, 'r') as f:
        content = f.read()

    marker = '/* ============================================================\n * Quarto RevealJS compatibility'
    idx = content.find(marker)
    if idx >= 0:
        # Replace from marker to end of file
        content = content[:idx].rstrip() + '\n' + addon
    else:
        content = content.rstrip() + '\n' + addon

    with open(css_path, 'w') as f:
        f.write(content)

    print(f"  Updated {css_path}")


def update_gentle_r_css(css_path):
    """Add/update RevealJS compatibility rules in gentle-r.css."""
    _replace_or_append_addon(css_path, GENTLE_R_CSS_ADDON)


def update_xaringan_themer_css(css_path):
    """Add/update RevealJS compatibility rules in xaringan-themer.css."""
    _replace_or_append_addon(css_path, REVEALJS_CSS_ADDON)


def process_class(class_dir):
    """Process a single class directory."""
    class_name = class_dir.name
    colors = CLASS_COLORS.get(class_name)

    if not colors:
        print(f"  WARNING: No color data for {class_name}, skipping")
        return

    title_bg = colors['title_bg']

    # Find Rmd file
    rmd_files = list(class_dir.glob('class_*.Rmd'))
    if not rmd_files:
        print(f"  No Rmd file found in {class_name}")
        return

    rmd_file = rmd_files[0]
    qmd_file = rmd_file.with_suffix('.qmd')

    print(f"\nProcessing {class_name}...")
    print(f"  Converting {rmd_file.name} -> {qmd_file.name}")

    # Read and convert Rmd
    with open(rmd_file, 'r', encoding='utf-8') as f:
        rmd_content = f.read()

    qmd_content = convert_rmd_to_qmd(rmd_content, title_bg)

    with open(qmd_file, 'w', encoding='utf-8') as f:
        f.write(qmd_content)

    # Update CSS files
    gentle_css = class_dir / 'gentle-r.css'
    if gentle_css.exists():
        update_gentle_r_css(gentle_css)

    themer_css = class_dir / 'xaringan-themer.css'
    if themer_css.exists():
        update_xaringan_themer_css(themer_css)

    print(f"  Done: {qmd_file}")
    return qmd_file


def main():
    slides_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        # Process specific classes
        class_names = sys.argv[1:]
        class_dirs = [slides_dir / name for name in class_names]
    else:
        # Process all classes
        class_dirs = sorted(slides_dir.glob('class_*'))

    for class_dir in class_dirs:
        if class_dir.is_dir():
            process_class(class_dir)


if __name__ == '__main__':
    main()
