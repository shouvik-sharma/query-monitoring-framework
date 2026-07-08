"""Create baseline and intentionally inefficient query workloads for the research framework."""

import csv
from pathlib import Path

# Directory setup
ROOT = Path(__file__).resolve().parents[1]

# Dataset paths
DATASETS = {
    'usgs': {
        'path': ROOT / 'data' / 'raw' / 'usgs' / 'all_month.csv',
        'columns': ['time', 'latitude', 'longitude', 'depth', 'mag', 'place'],
        'description': 'USGS earthquake data'
    },
    'noaa': {
        'path': ROOT / 'data' / 'raw' / 'noaa' / '01001099999.csv',
        'columns': ['STATION', 'DATE', 'TMP', 'DEW', 'SLP'],
        'description': 'NOAA hourly weather data'
    },
    'awid': {
        'path': ROOT / 'data' / 'raw' / 'kaggle_wifi' / 'extracted' / 'AWID.csv',
        'columns': ['frame.time_epoch', 'wlan.sa', 'radiotap.dbm_antsignal', 'class'],
        'description': 'Wi-Fi network traffic data'
    }
}

def read_csv_header(filepath):
    """Read first row to get column names"""
    with open(filepath, 'r') as f:
        return next(csv.reader(f))

def generate_baseline_queries():
    """Create efficient baseline queries for each dataset"""
    queries = []
    
    # USGS Earthquake queries
    queries.append({
        'dataset': 'usgs',
        'label': 'USGS - Earthquakes > 5.0 magnitude',
        'query': """SELECT place, mag, time
FROM earthquakes
WHERE mag > 5.0
ORDER BY time DESC
LIMIT 20""",
        'is_baseline': True,
        'inefficiency_type': None
    })
    
    queries.append({
        'dataset': 'usgs',
        'label': 'USGS - Recent earthquakes in California',
        'query': """SELECT place, mag, time
FROM earthquakes
WHERE place LIKE '%CA%' AND time > '2023-01-01'
ORDER BY mag DESC
LIMIT 10""",
        'is_baseline': True,
        'inefficiency_type': None
    })
    
    # NOAA Weather queries
    queries.append({
        'dataset': 'noaa',
        'label': 'NOAA - High temperature stations',
        'query': """SELECT STATION, DATE, TMP
FROM weather
WHERE TMP > 25.0
ORDER BY TMP DESC
LIMIT 15""",
        'is_baseline': True,
        'inefficiency_type': None
    })
    
    # AWID Wi-Fi queries
    queries.append({
        'dataset': 'awid',
        'label': 'AWID - Strong signal devices',
        'query': """SELECT wlan_sa, radiotap_dbm_antsignal
FROM wifi_network
WHERE radiotap_dbm_antsignal > -50
ORDER BY radiotap_dbm_antsignal DESC
LIMIT 10""",
        'is_baseline': True,
        'inefficiency_type': None
    })
    
    return queries

def generate_inefficient_queries():
    """Create intentionally inefficient query variants"""
    queries = []
    
    # USGS Inefficient variants
    queries.append({
        'dataset': 'usgs', 
        'label': 'USGS - SELECT * variant',
        'query': """SELECT * FROM earthquakes""",
        'is_baseline': False,
        'inefficiency_type': 'select_star',
        'expected_issue': 'Unnecessary column selection'
    })
    
    queries.append({
        'dataset': 'usgs',
        'label': 'USGS - No filter variant',
        'query': """SELECT place, mag, time FROM earthquakes ORDER BY mag DESC""",
        'is_baseline': False,
        'inefficiency_type': 'missing_predicate',
        'expected_issue': 'Full table scan without filters'
    })
    
    # NOAA Inefficient variants
    queries.append({
        'dataset': 'noaa',
        'label': 'NOAA - Cross join variant',
        'query': """SELECT w1.STATION, w1.TMP, w2.TMP AS TMP2
FROM weather w1, weather w2""",
        'is_baseline': False,
        'inefficiency_type': 'cross_join',
        'expected_issue': 'Unintended cross join'
    })
    
    # AWID Inefficient variants
    queries.append({
        'dataset': 'awid',
        'label': 'AWID - Nested subquery variant',
        'query': """SELECT * FROM (
            SELECT * FROM wifi_network WHERE radiotap_dbm_antsignal > -70
        ) AS t WHERE radiotap_dbm_antsignal > -60""",
        'is_baseline': False,
        'inefficiency_type': 'redundant_subquery',
        'expected_issue': 'Redundant filtering'
    })
    
    return queries

def save_queries_to_file(queries, filename):
    """Save queries to a JSON file"""
    import json
    
    # Convert to dictionary
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
    
    # Write to file
    filepath = ROOT / 'data' / filename
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved {len(output)} queries to {filepath}")

def main():
    print("Generating query workload...")
    
    # Generate queries
    baseline_queries = generate_baseline_queries()
    inefficient_queries = generate_inefficient_queries()
    
    # Save to files
    save_queries_to_file(baseline_queries, 'baseline_queries.json')
    save_queries_to_file(inefficient_queries, 'inefficient_queries.json')
    
    # Combined query workload
    all_queries = baseline_queries + inefficient_queries
    save_queries_to_file(all_queries, 'query_workload.json')
    
    print("Query workload generation complete!")

if __name__ == "__main__":
    main()