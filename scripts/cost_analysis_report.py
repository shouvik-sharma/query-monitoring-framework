"""Wrapper to generate and print the cost-improvement report."""

import sys
from pathlib import Path
from generate_report import generate_markdown_report

if __name__ == '__main__':
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')

    # Generate the report
    generate_markdown_report()
    
    # Print the report to console
    report_path = Path(__file__).resolve().parent.parent / 'data' / 'cost_analysis_report.md'
    with open(report_path, 'r', encoding='utf-8') as f:
        print(f.read())
