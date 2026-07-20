"""Run sqlaudit baseline on the query workload and compare with LLM-based approach."""

import json
import sqlite3
from pathlib import Path
from sqlaudit import Analyzer

ROOT = Path(__file__).resolve().parent.parent
WORKLOAD_PATH = ROOT / 'data' / 'query_workload.json'
EXPANDED_WORKLOAD_PATH = ROOT / 'data' / 'expanded_query_workload.json'
DB_PATH = ROOT / 'data' / 'query_history.db'
REPORT_PATH = ROOT / 'data' / 'sqlaudit_comparison_report.md'
EXPANDED_REPORT_PATH = ROOT / 'data' / 'sqlaudit_expanded_comparison_report.md'

# Map sqlaudit findings to our anti-pattern types
SQLAUDIT_TO_OUR_MAPPING = {
    'P001': 'select_star',           # SELECT * retrieves all columns
    'P003': 'like_prefix',           # Leading wildcard in LIKE
    'P006': 'or_vs_in',              # Multiple OR on same column
    'P007': 'missing_limit',         # SELECT without LIMIT
    'P008': 'non_sargable',          # Function on column in WHERE
    'P009': 'distinct_group',        # SELECT DISTINCT with JOINs
    'P010': 'missing_limit',         # ORDER BY without LIMIT
    'C002': 'select_star',           # SELECT * with GROUP BY
    'B004': 'redundant_subquery',    # Deeply nested subqueries
}

def load_workload():
    """Load the query workload from JSON."""
    with open(WORKLOAD_PATH, 'r') as f:
        return json.load(f)

def run_sqlaudit_baseline(workload):
    """Run sqlaudit on each query and collect findings."""
    analyzer = Analyzer()
    results = []
    
    for query in workload:
        sql = query['query']
        label = query['label']
        dataset = query['dataset']
        is_baseline = query['is_baseline']
        inefficiency_type = query.get('inefficiency_type', None)
        expected_issue = query.get('expected_issue', '')
        
        # Run sqlaudit
        report = analyzer.analyze(sql)
        
        # Extract findings
        findings = []
        for q in report.queries:
            for finding in q.findings:
                findings.append({
                    'rule_id': finding.rule_id,
                    'severity': finding.severity.value,
                    'message': finding.message,
                    'suggestion': finding.suggestion
                })
        
        # Determine if sqlaudit flags this query (any finding at WARNING level or higher)
        # Note: INFO and HINT are lower severity, but we include them for comparison
        has_any_finding = len(findings) > 0
        has_warning_or_higher = any(f['severity'] in ['ERROR', 'WARNING'] for f in findings)
        
        # Map to our anti-pattern types
        detected_types = set()
        for finding in findings:
            if finding['rule_id'] in SQLAUDIT_TO_OUR_MAPPING:
                detected_types.add(SQLAUDIT_TO_OUR_MAPPING[finding['rule_id']])
        
        results.append({
            'label': label,
            'dataset': dataset,
            'is_baseline': is_baseline,
            'inefficiency_type': inefficiency_type,
            'expected_issue': expected_issue,
            'sqlaudit_score': report.score,
            'sqlaudit_findings': findings,
            'sqlaudit_flags': has_warning_or_higher,
            'sqlaudit_any_finding': has_any_finding,
            'detected_types': list(detected_types)
        })
    
    return results

def compute_metrics(results):
    """Compute comparison metrics between sqlaudit and our ground truth."""
    tp = 0  # Inefficient queries correctly flagged
    fp = 0  # Baselines incorrectly flagged
    tn = 0  # Baselines correctly accepted
    fn = 0  # Inefficient queries missed
    
    per_pattern_stats = {}
    
    for r in results:
        is_inefficient = not r['is_baseline']
        sqlaudit_flagged = r['sqlaudit_flags']
        
        if is_inefficient and sqlaudit_flagged:
            tp += 1
        elif is_inefficient and not sqlaudit_flagged:
            fn += 1
        elif not is_inefficient and sqlaudit_flagged:
            fp += 1
        else:
            tn += 1
        
        # Per-pattern statistics
        if is_inefficient:
            pattern = r['inefficiency_type']
            if pattern not in per_pattern_stats:
                per_pattern_stats[pattern] = {'detected': 0, 'total': 0, 'examples': []}
            per_pattern_stats[pattern]['total'] += 1
            if sqlaudit_flagged:
                per_pattern_stats[pattern]['detected'] += 1
            per_pattern_stats[pattern]['examples'].append({
                'label': r['label'],
                'expected': r['expected_issue'],
                'sqlaudit_detected': sqlaudit_flagged,
                'sqlaudit_findings': r['sqlaudit_findings']
            })
    
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'fpr': fpr,
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn,
        'per_pattern_stats': per_pattern_stats
    }

def generate_comparison_report(results, metrics_strict, metrics_any):
    """Generate a markdown comparison report."""
    report = []
    report.append("# sqlaudit vs LLM-Based Approach Comparison Report")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append(f"- **Total queries analyzed:** {len(results)}")
    report.append(f"- **sqlaudit Accuracy (WARNING+):** {metrics_strict['accuracy']:.1%}")
    report.append(f"- **sqlaudit Precision (WARNING+):** {metrics_strict['precision']:.1%}")
    report.append(f"- **sqlaudit Recall (WARNING+):** {metrics_strict['recall']:.1%}")
    report.append(f"- **sqlaudit F1 Score (WARNING+):** {metrics_strict['f1']:.1%}")
    report.append(f"- **sqlaudit False Positive Rate (WARNING+):** {metrics_strict['fpr']:.1%}")
    report.append("")
    report.append(f"- **sqlaudit Accuracy (any finding):** {metrics_any['accuracy']:.1%}")
    report.append(f"- **sqlaudit Precision (any finding):** {metrics_any['precision']:.1%}")
    report.append(f"- **sqlaudit Recall (any finding):** {metrics_any['recall']:.1%}")
    report.append(f"- **sqlaudit F1 Score (any finding):** {metrics_any['f1']:.1%}")
    report.append(f"- **sqlaudit False Positive Rate (any finding):** {metrics_any['fpr']:.1%}")
    report.append("")
    report.append("## Confusion Matrix (WARNING+ severity as flag)")
    report.append("")
    report.append("| | sqlaudit Flags | sqlaudit Accepts |")
    report.append("|---|---|---|")
    report.append(f"| **Inefficient (GT)** | TP={metrics_strict['tp']} | FN={metrics_strict['fn']} |")
    report.append(f"| **Baseline (GT)** | FP={metrics_strict['fp']} | TN={metrics_strict['tn']} |")
    report.append("")
    report.append("## Confusion Matrix (any finding as flag)")
    report.append("")
    report.append("| | sqlaudit Flags | sqlaudit Accepts |")
    report.append("|---|---|---|")
    report.append(f"| **Inefficient (GT)** | TP={metrics_any['tp']} | FN={metrics_any['fn']} |")
    report.append(f"| **Baseline (GT)** | FP={metrics_any['fp']} | TN={metrics_any['tn']} |")
    report.append("")
    
    report.append("## Per-Pattern Detection Comparison")
    report.append("")
    report.append("| Anti-Pattern Type | Total | sqlaudit Detected (WARNING+) | Detection Rate (WARNING+) | sqlaudit Detected (any) | Detection Rate (any) |")
    report.append("|---|---|---|---|---|---|")
    
    for pattern in sorted(metrics_strict['per_pattern_stats'].keys()):
        stats_strict = metrics_strict['per_pattern_stats'][pattern]
        stats_any = metrics_any['per_pattern_stats'][pattern]
        rate_strict = stats_strict['detected'] / stats_strict['total'] if stats_strict['total'] > 0 else 0
        rate_any = stats_any['detected'] / stats_any['total'] if stats_any['total'] > 0 else 0
        report.append(f"| {pattern} | {stats_strict['total']} | {stats_strict['detected']} | {rate_strict:.1%} | {stats_any['detected']} | {rate_any:.1%} |")
    
    report.append("")
    report.append("## Detailed Findings by Query")
    report.append("")
    
    for r in results:
        report.append(f"### {r['label']}")
        report.append(f"- **Dataset:** {r['dataset']}")
        report.append(f"- **Ground Truth:** {'Inefficient' if not r['is_baseline'] else 'Baseline'}")
        if not r['is_baseline']:
            report.append(f"- **Expected Issue:** {r['expected_issue']}")
        report.append(f"- **sqlaudit Score:** {r['sqlaudit_score']}/100")
        report.append(f"- **sqlaudit Flags:** {'Yes' if r['sqlaudit_flags'] else 'No'}")
        
        if r['sqlaudit_findings']:
            report.append(f"- **sqlaudit Findings:**")
            for f in r['sqlaudit_findings']:
                report.append(f"  - [{f['severity']}] {f['rule_id']}: {f['message']}")
        
        report.append("")
    
    report.append("## Key Insights")
    report.append("")
    report.append("### What sqlaudit Catches Well")
    report.append("- SELECT * patterns (P001)")
    report.append("- Missing LIMIT clauses (P007, P010)")
    report.append("- Function on indexed columns (P008)")
    report.append("- Multiple OR conditions (P006)")
    report.append("")
    report.append("### What sqlaudit Misses")
    report.append("- Semantic issues requiring context understanding")
    report.append("- Cross joins without explicit join syntax")
    report.append("- Implicit type coercion")
    report.append("- Missing predicates (full scans)")
    report.append("- UNION vs UNION ALL distinction")
    report.append("")
    report.append("### Limitations of Rule-Based Approach")
    report.append("1. **No context understanding:** sqlaudit cannot distinguish between intentional full scans and accidental ones")
    report.append("2. **No rewrite generation:** It identifies issues but doesn't propose fixes")
    report.append("3. **No execution validation:** Cannot verify if rewrites preserve semantics")
    report.append("4. **Fixed rule set:** Cannot adapt to domain-specific patterns")
    
    return "\n".join(report)

def load_expanded_workload():
    """Load the expanded query workload from JSON."""
    with open(EXPANDED_WORKLOAD_PATH, 'r') as f:
        return json.load(f)

def run_sqlaudit_baseline(workload):
    """Run sqlaudit on each query and collect findings."""
    analyzer = Analyzer()
    results = []
    
    for query in workload:
        sql = query['query']
        label = query['label']
        dataset = query['dataset']
        is_baseline = query['is_baseline']
        inefficiency_type = query.get('inefficiency_type', None)
        expected_issue = query.get('expected_issue', '')
        
        # Run sqlaudit
        report = analyzer.analyze(sql)
        
        # Extract findings
        findings = []
        for q in report.queries:
            for finding in q.findings:
                findings.append({
                    'rule_id': finding.rule_id,
                    'severity': finding.severity.value,
                    'message': finding.message,
                    'suggestion': finding.suggestion
                })
        
        # Determine if sqlaudit flags this query (any finding at WARNING level or higher)
        # Note: INFO and HINT are lower severity, but we include them for comparison
        has_any_finding = len(findings) > 0
        has_warning_or_higher = any(f['severity'] in ['ERROR', 'WARNING'] for f in findings)
        
        # Map to our anti-pattern types
        detected_types = set()
        for finding in findings:
            if finding['rule_id'] in SQLAUDIT_TO_OUR_MAPPING:
                detected_types.add(SQLAUDIT_TO_OUR_MAPPING[finding['rule_id']])
        
        results.append({
            'label': label,
            'dataset': dataset,
            'is_baseline': is_baseline,
            'inefficiency_type': inefficiency_type,
            'expected_issue': expected_issue,
            'sqlaudit_score': report.score,
            'sqlaudit_findings': findings,
            'sqlaudit_flags': has_warning_or_higher,
            'sqlaudit_any_finding': has_any_finding,
            'detected_types': list(detected_types)
        })
    
    return results

def main():
    """Main function to run sqlaudit baseline comparison on both workloads."""
    # Run on original workload
    print("Loading original query workload...")
    workload = load_workload()
    
    print(f"Running sqlaudit on {len(workload)} queries (original)...")
    results = run_sqlaudit_baseline(workload)
    
    print("Computing comparison metrics...")
    metrics_strict = compute_metrics(results)  # Using WARNING+ as flags
    
    # Also compute with any finding as flag
    for r in results:
        r['sqlaudit_flags'] = r['sqlaudit_any_finding']
    metrics_any = compute_metrics(results)
    
    print("Generating comparison report...")
    report = generate_comparison_report(results, metrics_strict, metrics_any)
    
    # Save report
    with open(REPORT_PATH, 'w') as f:
        f.write(report)
    
    # Also save raw results as JSON for further analysis
    json_path = ROOT / 'data' / 'sqlaudit_results.json'
    with open(json_path, 'w') as f:
        json.dump({
            'results': results,
            'metrics_strict': {
                'accuracy': metrics_strict['accuracy'],
                'precision': metrics_strict['precision'],
                'recall': metrics_strict['recall'],
                'f1': metrics_strict['f1'],
                'fpr': metrics_strict['fpr'],
                'tp': metrics_strict['tp'],
                'fp': metrics_strict['fp'],
                'tn': metrics_strict['tn'],
                'fn': metrics_strict['fn']
            },
            'metrics_any': {
                'accuracy': metrics_any['accuracy'],
                'precision': metrics_any['precision'],
                'recall': metrics_any['recall'],
                'f1': metrics_any['f1'],
                'fpr': metrics_any['fpr'],
                'tp': metrics_any['tp'],
                'fp': metrics_any['fp'],
                'tn': metrics_any['tn'],
                'fn': metrics_any['fn']
            }
        }, f, indent=2)
    
    print(f"\nOriginal workload results saved to:")
    print(f"  - Report: {REPORT_PATH}")
    print(f"  - JSON: {json_path}")
    print(f"\nKey Metrics (WARNING+ severity as flag):")
    print(f"  Accuracy: {metrics_strict['accuracy']:.1%}")
    print(f"  Precision: {metrics_strict['precision']:.1%}")
    print(f"  Recall: {metrics_strict['recall']:.1%}")
    print(f"  F1 Score: {metrics_strict['f1']:.1%}")
    print(f"  False Positive Rate: {metrics_strict['fpr']:.1%}")
    print(f"\nKey Metrics (any finding as flag):")
    print(f"  Accuracy: {metrics_any['accuracy']:.1%}")
    print(f"  Precision: {metrics_any['precision']:.1%}")
    print(f"  Recall: {metrics_any['recall']:.1%}")
    print(f"  F1 Score: {metrics_any['f1']:.1%}")
    print(f"  False Positive Rate: {metrics_any['fpr']:.1%}")
    
    # Run on expanded workload
    print("\n" + "="*80)
    print("Loading expanded query workload...")
    expanded_workload = load_expanded_workload()
    
    print(f"Running sqlaudit on {len(expanded_workload)} queries (expanded)...")
    expanded_results = run_sqlaudit_baseline(expanded_workload)
    
    print("Computing comparison metrics...")
    expanded_metrics_strict = compute_metrics(expanded_results)
    
    # Also compute with any finding as flag
    for r in expanded_results:
        r['sqlaudit_flags'] = r['sqlaudit_any_finding']
    expanded_metrics_any = compute_metrics(expanded_results)
    
    print("Generating comparison report...")
    expanded_report = generate_comparison_report(expanded_results, expanded_metrics_strict, expanded_metrics_any)
    
    # Save expanded report
    with open(EXPANDED_REPORT_PATH, 'w') as f:
        f.write(expanded_report)
    
    # Also save raw results as JSON for further analysis
    expanded_json_path = ROOT / 'data' / 'sqlaudit_expanded_results.json'
    with open(expanded_json_path, 'w') as f:
        json.dump({
            'results': expanded_results,
            'metrics_strict': {
                'accuracy': expanded_metrics_strict['accuracy'],
                'precision': expanded_metrics_strict['precision'],
                'recall': expanded_metrics_strict['recall'],
                'f1': expanded_metrics_strict['f1'],
                'fpr': expanded_metrics_strict['fpr'],
                'tp': expanded_metrics_strict['tp'],
                'fp': expanded_metrics_strict['fp'],
                'tn': expanded_metrics_strict['tn'],
                'fn': expanded_metrics_strict['fn']
            },
            'metrics_any': {
                'accuracy': expanded_metrics_any['accuracy'],
                'precision': expanded_metrics_any['precision'],
                'recall': expanded_metrics_any['recall'],
                'f1': expanded_metrics_any['f1'],
                'fpr': expanded_metrics_any['fpr'],
                'tp': expanded_metrics_any['tp'],
                'fp': expanded_metrics_any['fp'],
                'tn': expanded_metrics_any['tn'],
                'fn': expanded_metrics_any['fn']
            }
        }, f, indent=2)
    
    print(f"\nExpanded workload results saved to:")
    print(f"  - Report: {EXPANDED_REPORT_PATH}")
    print(f"  - JSON: {expanded_json_path}")
    print(f"\nKey Metrics (WARNING+ severity as flag):")
    print(f"  Accuracy: {expanded_metrics_strict['accuracy']:.1%}")
    print(f"  Precision: {expanded_metrics_strict['precision']:.1%}")
    print(f"  Recall: {expanded_metrics_strict['recall']:.1%}")
    print(f"  F1 Score: {expanded_metrics_strict['f1']:.1%}")
    print(f"  False Positive Rate: {expanded_metrics_strict['fpr']:.1%}")
    print(f"\nKey Metrics (any finding as flag):")
    print(f"  Accuracy: {expanded_metrics_any['accuracy']:.1%}")
    print(f"  Precision: {expanded_metrics_any['precision']:.1%}")
    print(f"  Recall: {expanded_metrics_any['recall']:.1%}")
    print(f"  F1 Score: {expanded_metrics_any['f1']:.1%}")
    print(f"  False Positive Rate: {expanded_metrics_any['fpr']:.1%}")

if __name__ == '__main__':
    main()