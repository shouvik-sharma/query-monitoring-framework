"""Convert RESEARCH_PAPER.md to PDF using markdown + playwright with MathJax."""

import markdown
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / 'RESEARCH_PAPER.md'
PDF_PATH = ROOT / 'RESEARCH_PAPER.pdf'
HTML_PATH = ROOT / 'temp_paper.html'

with open(MD_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

html = markdown.markdown(
    text,
    extensions=['extra', 'codehilite', 'tables', 'fenced_code']
)

CURRENT_DIR = ROOT.as_posix()

html_with_style = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<base href="file:///{CURRENT_DIR}/">
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true
  }},
  svg: {{ fontCache: 'global' }},
  options: {{
    enableMenu: false,
    ignoreHtmlClass: 'tex2jax_ignore',
    processHtmlClass: 'tex2jax_process'
  }}
}};
</script>
<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
</script>
<style>
@page {{ margin: 2cm; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 2cm; font-size: 11pt; line-height: 1.5; color: #000; }}
h1 {{ font-size: 20pt; text-align: center; margin-top: 0; page-break-before: avoid; }}
h2 {{ font-size: 14pt; margin-top: 28pt; border-bottom: 1px solid #ddd; padding-bottom: 4pt; }}
h3 {{ font-size: 12pt; margin-top: 20pt; }}
img {{ max-width: 100%; height: auto; display: block; margin: 12pt auto; }}
code {{ background: #f0f0f0; padding: 1px 4px; font-size: 9pt; border-radius: 2px; }}
pre {{ background: #f0f0f0; padding: 8pt; font-size: 8.5pt; border-left: 3px solid #333; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }}
table {{ border-collapse: collapse; width: 100%; margin: 12pt 0; page-break-inside: avoid; }}
th, td {{ border: 1px solid #ccc; padding: 6pt; font-size: 10pt; text-align: left; }}
th {{ background: #eee; }}
blockquote {{ border-left: 3px solid #999; padding-left: 12pt; color: #555; margin: 12pt 0; }}
p {{ margin: 8pt 0; text-align: justify; }}
</style>
</head><body>
{html}
</body></html>'''

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html_with_style)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto(HTML_PATH.as_uri(), wait_until='networkidle')

    try:
        page.wait_for_function(
            '() => window.MathJax && MathJax.startup && MathJax.startup.document && MathJax.startup.document.state() === "processed"',
            timeout=60000
        )
        print("MathJax rendering complete")
    except Exception as e:
        print(f"MathJax wait warning: {e}")
        svg_count = page.evaluate('() => document.querySelectorAll("svg").length')
        print(f"SVG elements in page: {svg_count}")

    page.wait_for_timeout(3000)

    page.pdf(
        path=str(PDF_PATH),
        format='A4',
        print_background=True,
        margin={'top': '2cm', 'bottom': '2cm', 'left': '2cm', 'right': '2cm'}
    )
    browser.close()

if HTML_PATH.exists():
    HTML_PATH.unlink()

print(f'PDF generated: {PDF_PATH}')
