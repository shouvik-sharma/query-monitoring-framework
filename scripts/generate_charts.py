"""Generate visual charts for the research paper from query_history.db."""

import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'data' / 'query_history.db'
FIGURES_DIR = ROOT / 'figures'

sns.set_style("whitegrid")
COLORS = sns.color_palette("muted")


def plot_detection_accuracy():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT q.query_label, la.score, q.is_baseline
        FROM llm_analyses la
        JOIN queries q ON la.query_id = q.id
        ORDER BY q.id
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = [r[0] for r in rows]
    scores = [r[1] for r in rows]
    is_baseline = [r[2] for r in rows]

    colors = ['#2ecc71' if b else '#e74c3c' for b in is_baseline]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels, scores, color=colors, edgecolor='white', linewidth=0.5)

    ax.axvline(x=40, color='orange', linestyle='--', linewidth=1.5, label='Threshold (τ = 40)')
    ax.set_xlabel('LLM Risk Score (0–100)', fontsize=12)
    ax.set_title('Query Risk Scores: Baseline vs. Inefficient Queries', fontsize=14, fontweight='bold')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='Baseline (correct)'),
        Patch(facecolor='#e74c3c', label='Inefficient (anti-pattern)'),
        plt.Line2D([0], [0], color='orange', linestyle='--', label='Threshold τ = 40')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{score}/100', va='center', fontsize=9, fontweight='bold')

    ax.set_xlim(0, 110)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'detection_accuracy.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved figures/detection_accuracy.png")


def plot_semantic_validation():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT q.query_label, cc.validation_status
        FROM cost_comparisons cc
        JOIN queries q ON cc.query_id = q.id
        ORDER BY q.id
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = [r[0] for r in rows]
    statuses = [r[1] for r in rows]

    colors = ['#2ecc71' if s == 'match' else '#e74c3c' for s in statuses]
    status_labels = ['Match' if s == 'match' else 'Mismatch' for s in statuses]

    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.barh(labels, [1] * len(labels), color=colors, edgecolor='white', linewidth=0.5)

    for i, (bar, sl) in enumerate(zip(bars, status_labels)):
        ax.text(0.5, bar.get_y() + bar.get_height()/2, sl,
                va='center', ha='center', fontsize=10, fontweight='bold', color='white')

    match_count = sum(1 for s in statuses if s == 'match')
    total = len(statuses)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title(f'Semantic Validation Results ({match_count}/{total} matches)', fontsize=14, fontweight='bold')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='Semantic Match'),
        Patch(facecolor='#e74c3c', label='Semantic Mismatch')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'semantic_validation.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved figures/semantic_validation.png")


def plot_llm_cost_breakdown():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT q.query_label, la.llm_cost_usd
        FROM llm_analyses la
        JOIN queries q ON la.query_id = q.id
        ORDER BY q.id
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = [r[0] for r in rows]
    costs = [r[1] * 1000000 for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(labels)), costs, color=sns.color_palette("Blues", len(labels)),
                  edgecolor='white', linewidth=0.5)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=9)
    ax.set_ylabel('LLM API Cost (micro-USD)', fontsize=12)
    ax.set_title('Per-Query LLM API Cost', fontsize=14, fontweight='bold')

    for bar, cost in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'${cost/1000000:.6f}', ha='center', va='bottom', fontsize=8, rotation=0)

    total_cost_usd = sum(costs) / 1000000
    ax.axhline(y=sum(costs)/len(costs), color='red', linestyle=':', linewidth=1,
               label=f'Mean: ${total_cost_usd/len(costs):.6f}')
    ax.legend(fontsize=10)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'llm_cost_breakdown.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved figures/llm_cost_breakdown.png")


def plot_score_distribution():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT la.score, q.is_baseline
        FROM llm_analyses la
        JOIN queries q ON la.query_id = q.id
    """)
    rows = cursor.fetchall()
    conn.close()

    baseline_scores = [r[0] for r in rows if r[1] == 1]
    inefficient_scores = [r[0] for r in rows if r[1] == 0]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot([baseline_scores, inefficient_scores],
                    patch_artist=True, widths=0.4)
    ax.set_xticklabels(['Baseline Queries', 'Inefficient Queries'])

    bp['boxes'][0].set_facecolor('#2ecc71')
    bp['boxes'][1].set_facecolor('#e74c3c')

    for i, scores in enumerate([baseline_scores, inefficient_scores]):
        jitter = np.random.normal(0, 0.04, size=len(scores))
        ax.scatter(np.ones(len(scores)) * (i + 1) + jitter, scores,
                   alpha=0.6, color='black', s=60, zorder=5)

    ax.set_ylabel('LLM Risk Score (0–100)', fontsize=12)
    ax.set_title('Score Distribution: Baseline vs. Inefficient Queries', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)

    mean_b = np.mean(baseline_scores) if baseline_scores else 0
    mean_i = np.mean(inefficient_scores) if inefficient_scores else 0
    ax.text(1, mean_b + 2, f'Mean: {mean_b:.0f}', ha='center', fontsize=10, fontweight='bold', color='#2ecc71')
    ax.text(2, mean_i + 2, f'Mean: {mean_i:.0f}', ha='center', fontsize=10, fontweight='bold', color='#e74c3c')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'score_distribution.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved figures/score_distribution.png")


def plot_runtime_comparison():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT q.query_label,
               qe1.runtime_ms AS original,
               qe2.runtime_ms AS rewritten
        FROM cost_comparisons cc
        JOIN queries q ON cc.query_id = q.id
        JOIN query_executions qe1 ON cc.original_execution_id = qe1.id
        JOIN query_executions qe2 ON cc.rewritten_execution_id = qe2.id
        ORDER BY q.id
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = [r[0] for r in rows]
    orig = [r[1] for r in rows]
    rew = [r[2] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    w = 0.35

    bars1 = ax.bar(x - w/2, orig, w, label='Original', color='#3498db', edgecolor='white')
    bars2 = ax.bar(x + w/2, rew, w, label='Rewritten', color='#e67e22', edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=9)
    ax.set_ylabel('Runtime (ms)', fontsize=12)
    ax.set_title('Original vs. Rewritten Query Runtime', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)

    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.02, f'{h:.2f}',
                ha='center', va='bottom', fontsize=8)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.02, f'{h:.2f}',
                ha='center', va='bottom', fontsize=8)

    ax.set_ylim(0, max(max(orig), max(rew)) * 1.3)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'runtime_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved figures/runtime_comparison.png")


if __name__ == '__main__':
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_detection_accuracy()
    plot_semantic_validation()
    plot_llm_cost_breakdown()
    plot_score_distribution()
    plot_runtime_comparison()
    print("\nAll charts generated successfully.")
