"""Verify PDF content and references."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / 'RESEARCH_PAPER.pdf'
MD_PATH = ROOT / 'RESEARCH_PAPER.md'

with open(MD_PATH, 'r', encoding='utf-8') as f:
    md = f.read()

print("Figures in figures/ directory:")
for f in sorted((ROOT / 'figures').glob('*.png')):
    size_kb = f.stat().st_size / 1024
    print(f"  {f.name} ({size_kb:.1f} KB)")

pdf_size_kb = PDF_PATH.stat().st_size / 1024
print(f"\nPDF size: {pdf_size_kb:.1f} KB")

images = re.findall(r'!\[.*?\]\((.*?)\)', md)
print(f"\nImage references in markdown: {len(images)}")
for img in images:
    exists = (ROOT / img).exists()
    print(f"  {img} -> {'EXISTS' if exists else 'MISSING'}")

display_math = len(re.findall(r'\$\$', md)) // 2
inline_math = md.count('$') // 2 - display_math
print(f"\nMath equations:")
print(f"  Display math: {display_math}")
print(f"  Inline math: approx {inline_math}")

print(f"\nSection structure:")
for line in md.split('\n'):
    if line.startswith('## ') or line.startswith('### '):
        print(f"  {line}")

print(f"\nTotal markdown size: {len(md)} chars")
print(f"Total markdown lines: {len(md.split(chr(10)))}")
