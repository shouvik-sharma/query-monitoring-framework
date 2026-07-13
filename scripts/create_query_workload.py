"""Create baseline and intentionally inefficient query workloads for the research framework."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def generate_baseline_queries():
    queries = []

    # ── USGS Earthquakes (3 baseline) ──
    queries.append({'dataset': 'usgs', 'label': 'USGS - Large earthquakes by magnitude',
        'query': 'SELECT place, mag, time, latitude, longitude\nFROM earthquakes\nWHERE mag > 4.5\nORDER BY mag DESC\nLIMIT 25',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'usgs', 'label': 'USGS - Recent California earthquakes',
        'query': "SELECT place, mag, time\nFROM earthquakes\nWHERE place LIKE '%CA%' AND time > '2023-01-01'\nORDER BY time DESC\nLIMIT 20",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'usgs', 'label': 'USGS - Shallow earthquake count by region',
        'query': "SELECT place, COUNT(*) AS cnt\nFROM earthquakes\nWHERE depth < 10.0\nGROUP BY place\nORDER BY cnt DESC\nLIMIT 15",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    # ── NOAA Weather (3 baseline) ──
    queries.append({'dataset': 'noaa', 'label': 'NOAA - High temperature stations',
        'query': 'SELECT STATION, DATE, TMP, DEW\nFROM weather\nWHERE TMP > 30.0\nORDER BY TMP DESC\nLIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'noaa', 'label': 'NOAA - Average temperature by station',
        'query': 'SELECT STATION, AVG(TMP) AS avg_temp, MIN(TMP) AS min_temp, MAX(TMP) AS max_temp\nFROM weather\nGROUP BY STATION\nORDER BY avg_temp DESC\nLIMIT 15',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'noaa', 'label': 'NOAA - Days with large pressure drops',
        'query': 'SELECT STATION, DATE, SLP\nFROM weather\nWHERE SLP < 1005.0\nORDER BY SLP ASC\nLIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    # ── AWID Wi-Fi (3 baseline) ──
    queries.append({'dataset': 'awid', 'label': 'AWID - Strong signal devices',
        'query': 'SELECT wlan_sa, radiotap_dbm_antsignal, class\nFROM wifi_network\nWHERE radiotap_dbm_antsignal > -50\nORDER BY radiotap_dbm_antsignal DESC\nLIMIT 25',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'awid', 'label': 'AWID - Normal traffic by MAC prefix',
        "query": "SELECT SUBSTR(wlan_sa, 1, 8) AS mac_prefix, COUNT(*) AS cnt\nFROM wifi_network\nWHERE class = 'normal'\nGROUP BY mac_prefix\nORDER BY cnt DESC\nLIMIT 15",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'awid', 'label': 'AWID - Attack signal distribution',
        "query": "SELECT radiotap_dbm_antsignal, COUNT(*) AS cnt\nFROM wifi_network\nWHERE class = 'attack'\nGROUP BY radiotap_dbm_antsignal\nORDER BY cnt DESC\nLIMIT 20",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    # ── Products (3 baseline) ──
    queries.append({'dataset': 'products', 'label': 'Products - Top-selling items',
        'query': 'SELECT category, product_name, price, stock_qty\nFROM products\nWHERE stock_qty > 0\nORDER BY price DESC\nLIMIT 30',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'products', 'label': 'Products - Average price by category',
        'query': 'SELECT category, AVG(price) AS avg_price, COUNT(*) AS product_count\nFROM products\nGROUP BY category\nORDER BY avg_price DESC\nLIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'products', 'label': 'Products - Low stock alerts',
        'query': 'SELECT product_name, category, stock_qty\nFROM products\nWHERE stock_qty < 10\nORDER BY stock_qty ASC\nLIMIT 25',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    # ── Orders (4 baseline) ──
    queries.append({'dataset': 'orders', 'label': 'Orders - High-value recent orders',
        'query': 'SELECT order_id, customer_id, total_amount, order_date\nFROM orders\nWHERE total_amount > 500.0\nORDER BY order_date DESC\nLIMIT 30',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'orders', 'label': 'Orders - Monthly revenue summary',
        'query': "SELECT STRFTIME('%Y-%m', order_date) AS month, SUM(total_amount) AS revenue, COUNT(*) AS order_count\nFROM orders\nGROUP BY month\nORDER BY month DESC\nLIMIT 24",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'orders', 'label': 'Orders - Top customers by spend',
        'query': 'SELECT customer_id, COUNT(*) AS order_count, SUM(total_amount) AS total_spend\nFROM orders\nGROUP BY customer_id\nORDER BY total_spend DESC\nLIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    queries.append({'dataset': 'orders', 'label': 'Orders - Pending high-value orders',
        "query": "SELECT order_id, customer_id, total_amount\nFROM orders\nWHERE status = 'pending' AND total_amount > 200.0\nORDER BY total_amount DESC\nLIMIT 20",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})

    return queries


ANTI_PATTERN_MAP = {
    'select_star':          'Unnecessary column selection',
    'missing_predicate':    'Full table scan without filters',
    'cross_join':           'Unintended Cartesian product',
    'redundant_subquery':   'Redundant nested query',
    'non_sargable':         'Function on indexed column prevents index seek',
    'missing_group_col':    'GROUP BY does not include all non-aggregate columns',
    'implicit_coercion':    'Type mismatch forces implicit conversion',
    'missing_limit':        'Unbounded result set from missing LIMIT',
    'or_vs_in':             'Multiple OR conditions instead of IN list',
    'union_all':            'UNION instead of UNION ALL (no duplicate removal needed)',
    'like_prefix':          'Leading wildcard prevents index usage',
    'distinct_group':       'DISTINCT used where GROUP BY is more appropriate',
}

def generate_inefficient_queries():
    queries = []

    # ── USGS (4 inefficient) ──
    queries.append({'dataset': 'usgs', 'label': 'USGS - SELECT * variant',
        'query': 'SELECT * FROM earthquakes WHERE mag > 4.0',
        'is_baseline': False, 'inefficiency_type': 'select_star',
        'expected_issue': ANTI_PATTERN_MAP['select_star']})

    queries.append({'dataset': 'usgs', 'label': 'USGS - Missing predicate (full scan)',
        'query': 'SELECT place, mag, time FROM earthquakes ORDER BY mag DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_predicate',
        'expected_issue': ANTI_PATTERN_MAP['missing_predicate']})

    queries.append({'dataset': 'usgs', 'label': 'USGS - Non-sargable YEAR() predicate',
        "query": 'SELECT place, mag, time FROM earthquakes WHERE YEAR(time) = 2024 ORDER BY mag DESC LIMIT 20',
        'is_baseline': False, 'inefficiency_type': 'non_sargable',
        'expected_issue': ANTI_PATTERN_MAP['non_sargable']})

    queries.append({'dataset': 'usgs', 'label': 'USGS - DISTINCT instead of GROUP BY',
        'query': 'SELECT DISTINCT place, mag FROM earthquakes ORDER BY mag DESC',
        'is_baseline': False, 'inefficiency_type': 'distinct_group',
        'expected_issue': ANTI_PATTERN_MAP['distinct_group']})

    # ── NOAA (3 inefficient) ──
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Cross join variant',
        'query': 'SELECT w1.STATION, w1.TMP, w2.TMP AS TMP2\nFROM weather w1, weather w2',
        'is_baseline': False, 'inefficiency_type': 'cross_join',
        'expected_issue': ANTI_PATTERN_MAP['cross_join']})

    queries.append({'dataset': 'noaa', 'label': 'NOAA - Missing LIMIT on ordered query',
        'query': 'SELECT STATION, DATE, TMP FROM weather WHERE TMP > 25.0 ORDER BY TMP DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_limit',
        'expected_issue': ANTI_PATTERN_MAP['missing_limit']})

    queries.append({'dataset': 'noaa', 'label': 'NOAA - Implicit type coercion',
        'query': "SELECT STATION, DATE, TMP FROM weather WHERE STATION = 10010099999 AND TMP > 25.0",
        'is_baseline': False, 'inefficiency_type': 'implicit_coercion',
        'expected_issue': ANTI_PATTERN_MAP['implicit_coercion']})

    # ── AWID (3 inefficient) ──
    queries.append({'dataset': 'awid', 'label': 'AWID - Nested subquery variant',
        'query': 'SELECT * FROM (\n    SELECT * FROM wifi_network WHERE radiotap_dbm_antsignal > -70\n) AS t WHERE radiotap_dbm_antsignal > -60',
        'is_baseline': False, 'inefficiency_type': 'redundant_subquery',
        'expected_issue': ANTI_PATTERN_MAP['redundant_subquery']})

    queries.append({'dataset': 'awid', 'label': 'AWID - OR instead of IN',
        "query": "SELECT wlan_sa, class, radiotap_dbm_antsignal\nFROM wifi_network\nWHERE class = 'normal' OR class = 'attack' OR class = 'unknown'\nORDER BY radiotap_dbm_antsignal",
        'is_baseline': False, 'inefficiency_type': 'or_vs_in',
        'expected_issue': ANTI_PATTERN_MAP['or_vs_in']})

    queries.append({'dataset': 'awid', 'label': 'AWID - LIKE with leading wildcard',
        "query": "SELECT wlan_sa, class FROM wifi_network WHERE wlan_sa LIKE '%:ff'",
        'is_baseline': False, 'inefficiency_type': 'like_prefix',
        'expected_issue': ANTI_PATTERN_MAP['like_prefix']})

    # ── Products (3 inefficient) ──
    queries.append({'dataset': 'products', 'label': 'Products - SELECT * with full scan',
        'query': 'SELECT * FROM products',
        'is_baseline': False, 'inefficiency_type': 'select_star',
        'expected_issue': ANTI_PATTERN_MAP['select_star']})

    queries.append({'dataset': 'products', 'label': 'Products - Missing GROUP BY column',
        'query': 'SELECT product_name, category, COUNT(*) AS cnt FROM products GROUP BY category',
        'is_baseline': False, 'inefficiency_type': 'missing_group_col',
        'expected_issue': ANTI_PATTERN_MAP['missing_group_col']})

    queries.append({'dataset': 'products', 'label': 'Products - Non-sargable string function',
        'query': "SELECT product_name, price, category FROM products WHERE LOWER(category) = 'electronics' ORDER BY price DESC LIMIT 20",
        'is_baseline': False, 'inefficiency_type': 'non_sargable',
        'expected_issue': ANTI_PATTERN_MAP['non_sargable']})

    # ── Orders (3 inefficient) ──
    queries.append({'dataset': 'orders', 'label': 'Orders - UNION instead of UNION ALL',
        'query': "SELECT order_id, total_amount FROM orders WHERE status = 'pending'\nUNION\nSELECT order_id, total_amount FROM orders WHERE status = 'shipped'\nORDER BY total_amount DESC LIMIT 30",
        'is_baseline': False, 'inefficiency_type': 'union_all',
        'expected_issue': ANTI_PATTERN_MAP['union_all']})

    queries.append({'dataset': 'orders', 'label': 'Orders - Redundant subquery wrapping',
        'query': 'SELECT * FROM (\n    SELECT order_id, customer_id, total_amount, order_date\n    FROM orders WHERE total_amount > 100.0\n) AS t WHERE total_amount > 200.0',
        'is_baseline': False, 'inefficiency_type': 'redundant_subquery',
        'expected_issue': ANTI_PATTERN_MAP['redundant_subquery']})

    queries.append({'dataset': 'orders', 'label': 'Orders - Missing LIMIT with ORDER BY',
        'query': 'SELECT order_id, customer_id, total_amount FROM orders ORDER BY total_amount DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_limit',
        'expected_issue': ANTI_PATTERN_MAP['missing_limit']})

    return queries


def save_queries_to_file(queries, filename):
    output = []
    for q in queries:
        output.append({
            'dataset': q['dataset'],
            'label': q['label'],
            'query': q['query'],
            'is_baseline': q['is_baseline'],
            'inefficiency_type': q.get('inefficiency_type'),
            'expected_issue': q.get('expected_issue', '')
        })
    filepath = ROOT / 'data' / filename
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved {len(output)} queries to {filepath}")


def main():
    print("Generating query workload...")
    baseline_queries = generate_baseline_queries()
    inefficient_queries = generate_inefficient_queries()

    save_queries_to_file(baseline_queries, 'baseline_queries.json')
    save_queries_to_file(inefficient_queries, 'inefficient_queries.json')

    all_queries = baseline_queries + inefficient_queries
    save_queries_to_file(all_queries, 'query_workload.json')

    baseline_types = set()
    inefficient_types = {}
    for q in inefficient_queries:
        t = q['inefficiency_type']
        inefficient_types[t] = inefficient_types.get(t, 0) + 1
    print(f"\nTotal: {len(all_queries)} queries ({len(baseline_queries)} baseline + {len(inefficient_queries)} inefficient)")
    print(f"Anti-pattern coverage: {len(inefficient_types)} types")
    for t, c in sorted(inefficient_types.items()):
        print(f"  {t}: {c}x")
    print("Query workload generation complete!")


if __name__ == "__main__":
    main()
