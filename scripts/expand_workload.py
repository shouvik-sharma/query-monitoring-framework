"""Expand the query workload to 100+ queries for comprehensive evaluation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKLOAD_PATH = ROOT / 'data' / 'query_workload.json'
EXPANDED_WORKLOAD_PATH = ROOT / 'data' / 'expanded_query_workload.json'

def load_existing_workload():
    """Load the existing 32-query workload."""
    with open(WORKLOAD_PATH, 'r') as f:
        return json.load(f)

def generate_additional_baseline_queries():
    """Generate additional baseline queries to reach 50+ baseline queries."""
    queries = []
    
    # Additional USGS queries (5 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - Magnitude distribution',
        'query': 'SELECT mag, COUNT(*) AS cnt FROM earthquakes GROUP BY mag ORDER BY cnt DESC LIMIT 10',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'usgs', 'label': 'USGS - Deep earthquakes',
        'query': 'SELECT place, mag, depth FROM earthquakes WHERE depth > 300 ORDER BY depth DESC LIMIT 15',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'usgs', 'label': 'USGS - Recent earthquakes by location',
        'query': 'SELECT latitude, longitude, mag FROM earthquakes WHERE time > DATE_SUB(NOW(), INTERVAL 7 DAY) LIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'usgs', 'label': 'USGS - Earthquake frequency by month',
        'query': "SELECT STRFTIME('%Y-%m', time) AS month, COUNT(*) AS cnt FROM earthquakes GROUP BY month ORDER BY month DESC LIMIT 12",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'usgs', 'label': 'USGS - High magnitude earthquakes',
        'query': 'SELECT place, mag, time FROM earthquakes WHERE mag > 6.0 ORDER BY mag DESC LIMIT 10',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    # Additional NOAA queries (5 more)
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Temperature range by station',
        'query': 'SELECT STATION, MAX(TMP) - MIN(TMP) AS temp_range FROM weather GROUP BY STATION ORDER BY temp_range DESC LIMIT 10',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - High humidity days',
        'query': 'SELECT STATION, DATE, DEW FROM weather WHERE DEW > 25.0 ORDER BY DEW DESC LIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Pressure variation',
        'query': 'SELECT STATION, AVG(SLP) AS avg_pressure, STDDEV(SLP) AS pressure_std FROM weather GROUP BY STATION ORDER BY pressure_std DESC LIMIT 10',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Recent weather readings',
        'query': 'SELECT STATION, DATE, TMP, DEW, SLP FROM weather WHERE DATE > DATE_SUB(NOW(), INTERVAL 30 DAY) LIMIT 25',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Temperature trends',
        'query': "SELECT STRFTIME('%Y-%m', DATE) AS month, AVG(TMP) AS avg_temp FROM weather GROUP BY month ORDER BY month DESC LIMIT 12",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    # Additional AWID queries (5 more)
    queries.append({'dataset': 'awid', 'label': 'AWID - Signal strength distribution',
        'query': 'SELECT radiotap_dbm_antsignal, COUNT(*) AS cnt FROM wifi_network GROUP BY radiotap_dbm_antsignal ORDER BY cnt DESC LIMIT 15',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Device activity by class',
        'query': 'SELECT class, COUNT(DISTINCT wlan_sa) AS device_count FROM wifi_network GROUP BY class ORDER BY device_count DESC',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Strong signal attacks',
        'query': "SELECT wlan_sa, radiotap_dbm_antsignal FROM wifi_network WHERE class = 'attack' AND radiotap_dbm_antsignal > -60 ORDER BY radiotap_dbm_antsignal DESC LIMIT 10",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - MAC prefix analysis',
        'query': 'SELECT SUBSTR(wlan_sa, 1, 8) AS prefix, COUNT(*) AS cnt FROM wifi_network GROUP BY prefix ORDER BY cnt DESC LIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Signal strength by class',
        'query': 'SELECT class, AVG(radiotap_dbm_antsignal) AS avg_signal FROM wifi_network GROUP BY class ORDER BY avg_signal DESC',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    # Additional Products queries (5 more)
    queries.append({'dataset': 'products', 'label': 'Products - Category statistics',
        'query': 'SELECT category, COUNT(*) AS cnt, AVG(price) AS avg_price, SUM(stock_qty) AS total_stock FROM products GROUP BY category ORDER BY cnt DESC',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'products', 'label': 'Products - High value items',
        'query': 'SELECT product_name, category, price FROM products WHERE price > 1000 ORDER BY price DESC LIMIT 15',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'products', 'label': 'Products - Stock levels',
        'query': 'SELECT category, SUM(stock_qty) AS total_stock FROM products GROUP BY category ORDER BY total_stock DESC',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'products', 'label': 'Products - Price distribution',
        'query': 'SELECT CASE WHEN price < 50 THEN \'Low\' WHEN price < 200 THEN \'Medium\' ELSE \'High\' END AS price_range, COUNT(*) AS cnt FROM products GROUP BY price_range ORDER BY cnt DESC',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'products', 'label': 'Products - Recent inventory',
        'query': 'SELECT product_name, category, stock_qty, price FROM products WHERE stock_qty > 0 ORDER BY stock_qty DESC LIMIT 30',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    # Additional Orders queries (5 more)
    queries.append({'dataset': 'orders', 'label': 'Orders - Customer order frequency',
        'query': 'SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id HAVING COUNT(*) > 5 ORDER BY order_count DESC LIMIT 20',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Revenue by status',
        'query': 'SELECT status, COUNT(*) AS order_count, SUM(total_amount) AS total_revenue FROM orders GROUP BY status ORDER BY total_revenue DESC',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - High value customers',
        'query': 'SELECT customer_id, SUM(total_amount) AS total_spend FROM orders GROUP BY customer_id HAVING SUM(total_amount) > 1000 ORDER BY total_spend DESC LIMIT 15',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Monthly order count',
        'query': "SELECT STRFTIME('%Y-%m', order_date) AS month, COUNT(*) AS order_count FROM orders GROUP BY month ORDER BY month DESC LIMIT 12",
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Average order value',
        'query': 'SELECT AVG(total_amount) AS avg_order_value, MIN(total_amount) AS min_order, MAX(total_amount) AS max_order FROM orders',
        'is_baseline': True, 'inefficiency_type': None, 'expected_issue': ''})
    
    return queries

def generate_additional_inefficient_queries():
    """Generate additional inefficient queries to reach 50+ inefficient queries."""
    queries = []
    
    # Additional SELECT * variants (3 more)
    queries.append({'dataset': 'noaa', 'label': 'NOAA - SELECT * variant',
        'query': 'SELECT * FROM weather WHERE TMP > 30',
        'is_baseline': False, 'inefficiency_type': 'select_star',
        'expected_issue': 'Unnecessary column selection'})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - SELECT * with filter',
        'query': 'SELECT * FROM wifi_network WHERE class = \'attack\'',
        'is_baseline': False, 'inefficiency_type': 'select_star',
        'expected_issue': 'Unnecessary column selection'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - SELECT * variant',
        'query': 'SELECT * FROM orders WHERE total_amount > 1000',
        'is_baseline': False, 'inefficiency_type': 'select_star',
        'expected_issue': 'Unnecessary column selection'})
    
    # Additional missing predicate variants (3 more)
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Missing predicate (full scan)',
        'query': 'SELECT STATION, TMP FROM weather ORDER BY TMP DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_predicate',
        'expected_issue': 'Full table scan without filters'})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Missing predicate (full scan)',
        'query': 'SELECT wlan_sa, class FROM wifi_network ORDER BY radiotap_dbm_antsignal',
        'is_baseline': False, 'inefficiency_type': 'missing_predicate',
        'expected_issue': 'Full table scan without filters'})
    
    queries.append({'dataset': 'products', 'label': 'Products - Missing predicate (full scan)',
        'query': 'SELECT product_name, price FROM products ORDER BY price DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_predicate',
        'expected_issue': 'Full table scan without filters'})
    
    # Additional cross join variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - Cross join variant',
        'query': 'SELECT e1.place, e1.mag, e2.place, e2.mag FROM earthquakes e1, earthquakes e2 WHERE e1.mag > 5',
        'is_baseline': False, 'inefficiency_type': 'cross_join',
        'expected_issue': 'Unintended Cartesian product'})
    
    queries.append({'dataset': 'products', 'label': 'Products - Cross join variant',
        'query': 'SELECT p.product_name, c.category FROM products p, products c WHERE p.price > 100',
        'is_baseline': False, 'inefficiency_type': 'cross_join',
        'expected_issue': 'Unintended Cartesian product'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Cross join variant',
        'query': 'SELECT o1.order_id, o2.order_id FROM orders o1, orders o2 WHERE o1.total_amount > 500',
        'is_baseline': False, 'inefficiency_type': 'cross_join',
        'expected_issue': 'Unintended Cartesian product'})
    
    # Additional redundant subquery variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - Redundant subquery variant',
        'query': 'SELECT * FROM (SELECT * FROM earthquakes WHERE mag > 4) AS sub WHERE sub.depth < 20',
        'is_baseline': False, 'inefficiency_type': 'redundant_subquery',
        'expected_issue': 'Redundant nested query'})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Redundant subquery variant',
        'query': 'SELECT * FROM (SELECT * FROM weather WHERE TMP > 25) AS sub WHERE sub.SLP < 1010',
        'is_baseline': False, 'inefficiency_type': 'redundant_subquery',
        'expected_issue': 'Redundant nested query'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Redundant subquery variant',
        'query': 'SELECT * FROM (SELECT * FROM orders WHERE total_amount > 500) AS sub WHERE sub.status = \'pending\'',
        'is_baseline': False, 'inefficiency_type': 'redundant_subquery',
        'expected_issue': 'Redundant nested query'})
    
    # Additional non-sargable variants (3 more)
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Non-sargable MONTH() predicate',
        'query': 'SELECT STATION, DATE, TMP FROM weather WHERE MONTH(DATE) = 6',
        'is_baseline': False, 'inefficiency_type': 'non_sargable',
        'expected_issue': 'Function on indexed column prevents index seek'})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Non-sargable SUBSTR() predicate',
        'query': "SELECT wlan_sa, class FROM wifi_network WHERE SUBSTR(wlan_sa, 1, 5) = '00:11:22'",
        'is_baseline': False, 'inefficiency_type': 'non_sargable',
        'expected_issue': 'Function on indexed column prevents index seek'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Non-sargable YEAR() predicate',
        'query': "SELECT order_id, total_amount FROM orders WHERE YEAR(order_date) = 2024",
        'is_baseline': False, 'inefficiency_type': 'non_sargable',
        'expected_issue': 'Function on indexed column prevents index seek'})
    
    # Additional missing limit variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - Missing LIMIT on ordered query',
        'query': 'SELECT place, mag, time FROM earthquakes ORDER BY mag DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_limit',
        'expected_issue': 'Unbounded result set from missing LIMIT'})
    
    queries.append({'dataset': 'products', 'label': 'Products - Missing LIMIT on ordered query',
        'query': 'SELECT product_name, price FROM products ORDER BY price DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_limit',
        'expected_issue': 'Unbounded result set from missing LIMIT'})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Missing LIMIT on ordered query',
        'query': 'SELECT wlan_sa, radiotap_dbm_antsignal FROM wifi_network ORDER BY radiotap_dbm_antsignal DESC',
        'is_baseline': False, 'inefficiency_type': 'missing_limit',
        'expected_issue': 'Unbounded result set from missing LIMIT'})
    
    # Additional or_vs_in variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - OR instead of IN',
        'query': "SELECT place, mag FROM earthquakes WHERE place = 'California' OR place = 'Nevada' OR place = 'Oregon'",
        'is_baseline': False, 'inefficiency_type': 'or_vs_in',
        'expected_issue': 'Multiple OR conditions instead of IN list'})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - OR instead of IN',
        'query': "SELECT STATION, TMP FROM weather WHERE STATION = '01001099999' OR STATION = '01002099999'",
        'is_baseline': False, 'inefficiency_type': 'or_vs_in',
        'expected_issue': 'Multiple OR conditions instead of IN list'})
    
    queries.append({'dataset': 'products', 'label': 'Products - OR instead of IN',
        'query': "SELECT product_name, category FROM products WHERE category = 'Electronics' OR category = 'Clothing'",
        'is_baseline': False, 'inefficiency_type': 'or_vs_in',
        'expected_issue': 'Multiple OR conditions instead of IN list'})
    
    # Additional like_prefix variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - LIKE with leading wildcard',
        'query': "SELECT place, mag FROM earthquakes WHERE place LIKE '%CA%'",
        'is_baseline': False, 'inefficiency_type': 'like_prefix',
        'expected_issue': 'Leading wildcard prevents index usage'})
    
    queries.append({'dataset': 'products', 'label': 'Products - LIKE with leading wildcard',
        'query': "SELECT product_name, price FROM products WHERE product_name LIKE '%Widget%'",
        'is_baseline': False, 'inefficiency_type': 'like_prefix',
        'expected_issue': 'Leading wildcard prevents index usage'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - LIKE with leading wildcard',
        'query': "SELECT order_id, customer_id FROM orders WHERE status LIKE '%pending%'",
        'is_baseline': False, 'inefficiency_type': 'like_prefix',
        'expected_issue': 'Leading wildcard prevents index usage'})
    
    # Additional implicit_coercion variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - Implicit type coercion',
        'query': 'SELECT place, mag FROM earthquakes WHERE mag > 5',
        'is_baseline': False, 'inefficiency_type': 'implicit_coercion',
        'expected_issue': 'Type mismatch forces implicit conversion'})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Implicit type coercion',
        'query': 'SELECT wlan_sa, class FROM wifi_network WHERE radiotap_dbm_antsignal > -50',
        'is_baseline': False, 'inefficiency_type': 'implicit_coercion',
        'expected_issue': 'Type mismatch forces implicit conversion'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - Implicit type coercion',
        'query': 'SELECT order_id, total_amount FROM orders WHERE total_amount > 1000',
        'is_baseline': False, 'inefficiency_type': 'implicit_coercion',
        'expected_issue': 'Type mismatch forces implicit conversion'})
    
    # Additional distinct_group variants (3 more)
    queries.append({'dataset': 'noaa', 'label': 'NOAA - DISTINCT instead of GROUP BY',
        'query': 'SELECT DISTINCT STATION, TMP FROM weather ORDER BY TMP DESC',
        'is_baseline': False, 'inefficiency_type': 'distinct_group',
        'expected_issue': 'DISTINCT used where GROUP BY is more appropriate'})
    
    queries.append({'dataset': 'products', 'label': 'Products - DISTINCT instead of GROUP BY',
        'query': 'SELECT DISTINCT category, price FROM products ORDER BY price DESC',
        'is_baseline': False, 'inefficiency_type': 'distinct_group',
        'expected_issue': 'DISTINCT used where GROUP BY is more appropriate'})
    
    queries.append({'dataset': 'orders', 'label': 'Orders - DISTINCT instead of GROUP BY',
        'query': 'SELECT DISTINCT customer_id, total_amount FROM orders ORDER BY total_amount DESC',
        'is_baseline': False, 'inefficiency_type': 'distinct_group',
        'expected_issue': 'DISTINCT used where GROUP BY is more appropriate'})
    
    # Additional union_all variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - UNION instead of UNION ALL',
        'query': "SELECT place, mag FROM earthquakes WHERE mag > 6 UNION SELECT place, mag FROM earthquakes WHERE depth < 10",
        'is_baseline': False, 'inefficiency_type': 'union_all',
        'expected_issue': 'UNION instead of UNION ALL (no duplicate removal needed)'})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - UNION instead of UNION ALL',
        'query': "SELECT STATION, TMP FROM weather WHERE TMP > 35 UNION SELECT STATION, TMP FROM weather WHERE TMP < 0",
        'is_baseline': False, 'inefficiency_type': 'union_all',
        'expected_issue': 'UNION instead of UNION ALL (no duplicate removal needed)'})
    
    queries.append({'dataset': 'products', 'label': 'Products - UNION instead of UNION ALL',
        'query': "SELECT product_name, price FROM products WHERE price > 1000 UNION SELECT product_name, price FROM products WHERE price < 10",
        'is_baseline': False, 'inefficiency_type': 'union_all',
        'expected_issue': 'UNION instead of UNION ALL (no duplicate removal needed)'})
    
    # Additional missing_group_col variants (3 more)
    queries.append({'dataset': 'usgs', 'label': 'USGS - Missing GROUP BY column',
        'query': 'SELECT place, mag, COUNT(*) FROM earthquakes GROUP BY place',
        'is_baseline': False, 'inefficiency_type': 'missing_group_col',
        'expected_issue': 'GROUP BY does not include all non-aggregate columns'})
    
    queries.append({'dataset': 'noaa', 'label': 'NOAA - Missing GROUP BY column',
        'query': 'SELECT STATION, TMP, COUNT(*) FROM weather GROUP BY STATION',
        'is_baseline': False, 'inefficiency_type': 'missing_group_col',
        'expected_issue': 'GROUP BY does not include all non-aggregate columns'})
    
    queries.append({'dataset': 'awid', 'label': 'AWID - Missing GROUP BY column',
        'query': 'SELECT class, radiotap_dbm_antsignal, COUNT(*) FROM wifi_network GROUP BY class',
        'is_baseline': False, 'inefficiency_type': 'missing_group_col',
        'expected_issue': 'GROUP BY does not include all non-aggregate columns'})
    
    return queries

def main():
    """Main function to expand the workload."""
    print("Loading existing workload...")
    existing_workload = load_existing_workload()
    
    print(f"Existing workload: {len(existing_workload)} queries")
    
    print("Generating additional baseline queries...")
    additional_baseline = generate_additional_baseline_queries()
    
    print("Generating additional inefficient queries...")
    additional_inefficient = generate_additional_inefficient_queries()
    
    # Combine all queries
    expanded_workload = existing_workload + additional_baseline + additional_inefficient
    
    # Remove duplicates based on query text
    seen_queries = set()
    unique_workload = []
    for q in expanded_workload:
        query_text = q['query'].strip()
        if query_text not in seen_queries:
            seen_queries.add(query_text)
            unique_workload.append(q)
    
    print(f"Expanded workload: {len(unique_workload)} queries")
    print(f"  - Baseline: {sum(1 for q in unique_workload if q['is_baseline'])}")
    print(f"  - Inefficient: {sum(1 for q in unique_workload if not q['is_baseline'])}")
    
    # Save expanded workload
    with open(EXPANDED_WORKLOAD_PATH, 'w') as f:
        json.dump(unique_workload, f, indent=2)
    
    print(f"Expanded workload saved to: {EXPANDED_WORKLOAD_PATH}")
    
    # Print summary of anti-pattern types
    inefficient_queries = [q for q in unique_workload if not q['is_baseline']]
    pattern_counts = {}
    for q in inefficient_queries:
        pattern = q['inefficiency_type']
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    print("\nAnti-pattern distribution:")
    for pattern, count in sorted(pattern_counts.items()):
        print(f"  - {pattern}: {count}")

if __name__ == '__main__':
    main()