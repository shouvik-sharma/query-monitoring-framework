"""Execute query workload and store results in query_history.db"""

import sqlite3
import duckdb
import json
import time
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'query_history.db'
QUERY_WORKLOAD_PATH = ROOT / 'data' / 'query_workload.json'
DATASETS_DIR = ROOT / 'data' / 'raw'

SEED = 42
N_ROWS = 500


def seeded_random():
    rng = random.Random(SEED)
    return rng


def generate_data():
    """Generate 500 rows for each of 5 tables using seeded random."""
    rng = seeded_random()

    # USGS Earthquakes
    places = ['Los Angeles, CA', 'San Francisco, CA', 'New York, NY', 'Tokyo, Japan',
              'Mexico City, Mexico', 'Anchorage, AK', 'Seattle, WA', 'Portland, OR',
              'Reno, NV', 'Salt Lake City, UT', 'Phoenix, AZ', 'Denver, CO',
              'Chicago, IL', 'Miami, FL', 'Honolulu, HI']
    usgs = []
    for i in range(N_ROWS):
        ts = f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d} {rng.randint(0,23):02d}:{rng.randint(0,59):02d}:00"
        lat = round(rng.uniform(20.0, 50.0), 4)
        lon = round(rng.uniform(-125.0, -65.0), 4)
        mag = round(rng.uniform(2.0, 7.5), 1)
        depth = round(rng.uniform(1.0, 50.0), 1)
        place = rng.choice(places)
        usgs.append((ts, lat, lon, depth, mag, place))

    # NOAA Weather (2 stations)
    stations = ['01001099999', '01002099999']
    noaa = []
    for i in range(N_ROWS):
        st = rng.choice(stations)
        ts = f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d} {rng.randint(0,23):02d}:{rng.randint(0,59):02d}:00"
        tmp = round(rng.uniform(5.0, 40.0), 1)
        dew = round(tmp - rng.uniform(2.0, 10.0), 1)
        slp = round(rng.uniform(995.0, 1025.0), 1)
        noaa.append((st, ts, tmp, dew, slp))

    # AWID Wi-Fi
    mac_prefixes = ['00:11:22', 'aa:bb:cc', '11:22:33', '44:55:66', '77:88:99']
    classes = ['normal', 'normal', 'normal', 'attack', 'unknown']
    awid = []
    for i in range(N_ROWS):
        ts = f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d} {rng.randint(0,23):02d}:{rng.randint(0,59):02d}:00"
        mac = f"{rng.choice(mac_prefixes)}:{rng.randint(10,99):02d}:{rng.randint(10,99):02d}:{rng.randint(10,99):02d}"
        sig = rng.randint(-95, -20)
        cls = rng.choice(classes)
        awid.append((ts, mac, sig, cls))

    # Products
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Food']
    product_adjectives = ['Premium', 'Basic', 'Pro', 'Ultra', 'Eco', 'Smart', 'Classic']
    product_nouns = ['Widget', 'Gadget', 'Tool', 'Kit', 'Set', 'Pack', 'Device']
    products = []
    for i in range(N_ROWS):
        cat = rng.choice(categories)
        adj = rng.choice(product_adjectives)
        noun = rng.choice(product_nouns)
        name = f"{adj} {noun} {rng.randint(100,999)}"
        price = round(rng.uniform(5.0, 2000.0), 2)
        stock = rng.randint(0, 200)
        products.append((name, cat, price, stock))

    # Orders
    statuses = ['pending', 'shipped', 'delivered', 'cancelled']
    orders = []
    for i in range(N_ROWS):
        cid = rng.randint(1, 100)
        ts = f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
        amt = round(rng.uniform(10.0, 2000.0), 2)
        st = rng.choice(statuses)
        orders.append((i + 1, cid, ts, amt, st))

    return usgs, noaa, awid, products, orders


def setup_duckdb():
    conn = duckdb.connect()
    rng = seeded_random()

    usgs, noaa, awid, products, orders = generate_data()

    # Earthquakes
    conn.execute("CREATE TABLE earthquakes (time TIMESTAMP, latitude FLOAT, longitude FLOAT, depth FLOAT, mag FLOAT, place VARCHAR)")
    conn.executemany("INSERT INTO earthquakes VALUES (?, ?, ?, ?, ?, ?)", usgs)

    # Weather
    conn.execute("CREATE TABLE weather (STATION VARCHAR, DATE TIMESTAMP, TMP FLOAT, DEW FLOAT, SLP FLOAT)")
    conn.executemany("INSERT INTO weather VALUES (?, ?, ?, ?, ?)", noaa)

    # Wi-Fi
    conn.execute("CREATE TABLE wifi_network (frame_time_epoch TIMESTAMP, wlan_sa VARCHAR, radiotap_dbm_antsignal INTEGER, class VARCHAR)")
    conn.executemany("INSERT INTO wifi_network VALUES (?, ?, ?, ?)", awid)

    # Products
    conn.execute("CREATE TABLE products (product_name VARCHAR, category VARCHAR, price FLOAT, stock_qty INTEGER)")
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

    # Orders
    conn.execute("CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, order_date DATE, total_amount FLOAT, status VARCHAR)")
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

    for table, n in [('earthquakes', len(usgs)), ('weather', len(noaa)), ('wifi_network', len(awid)),
                     ('products', len(products)), ('orders', len(orders))]:
        print(f"  Loaded {n} rows into {table}")

    return conn


def compute_checksum(rows):
    row_str = str(sorted([tuple(row) for row in rows]))
    return hashlib.sha256(row_str.encode()).hexdigest()


def execute_query(duckdb_conn, query, dataset):
    start_time = time.time()
    try:
        result = duckdb_conn.execute(query).fetchall()
        runtime_ms = (time.time() - start_time) * 1000
        rows_returned = len(result)
        result_checksum = compute_checksum(result)
        try:
            explain_plan = duckdb_conn.execute(f"EXPLAIN {query}").fetchone()[0]
        except Exception:
            explain_plan = ""
        status = 'success'
        error_message = None
    except Exception as e:
        runtime_ms = (time.time() - start_time) * 1000
        rows_returned = 0
        result_checksum = ""
        explain_plan = ""
        status = 'error'
        error_message = str(e)
        result = []

    return {
        'status': status, 'runtime_ms': runtime_ms, 'rows_returned': rows_returned,
        'result_checksum': result_checksum, 'explain_plan': explain_plan,
        'error_message': error_message, 'result': result
    }


def store_execution(sqlite_conn, query_data, execution):
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id FROM datasets WHERE name = ?", (query_data['dataset'],))
    dataset_row = cursor.fetchone()
    if not dataset_row:
        cursor.execute("INSERT INTO datasets (name, source_url, local_path, description) VALUES (?, ?, ?, ?)",
                       (query_data['dataset'], '', '', ''))
        dataset_id = cursor.lastrowid
    else:
        dataset_id = dataset_row[0]

    cursor.execute("""INSERT INTO queries (dataset_id, query_text, query_label, inefficiency_type, expected_issue, is_baseline)
                      VALUES (?, ?, ?, ?, ?, ?)""",
                   (dataset_id, query_data['query'], query_data['label'],
                    query_data.get('inefficiency_type'), query_data.get('expected_issue', ''),
                    query_data['is_baseline']))
    query_id = cursor.lastrowid

    cursor.execute("""INSERT INTO query_executions (query_id, execution_label, engine, status, runtime_ms, 
                      rows_returned, result_checksum, explain_plan, error_message)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (query_id, 'original', 'duckdb', execution['status'], execution['runtime_ms'],
                    execution['rows_returned'], execution['result_checksum'], execution['explain_plan'],
                    execution['error_message']))

    sqlite_conn.commit()
    return query_id


def main():
    with open(QUERY_WORKLOAD_PATH, 'r') as f:
        queries = json.load(f)

    print(f"Loading {N_ROWS} rows per table into DuckDB...")
    duckdb_conn = setup_duckdb()
    sqlite_conn = sqlite3.connect(DB_PATH)

    cursor = sqlite_conn.cursor()
    cursor.execute("DELETE FROM cost_comparisons")
    cursor.execute("DELETE FROM recommendations")
    cursor.execute("DELETE FROM llm_analyses")
    cursor.execute("DELETE FROM query_executions")
    cursor.execute("DELETE FROM queries")
    cursor.execute("DELETE FROM datasets")
    cursor.execute("DELETE FROM workloads")
    sqlite_conn.commit()

    cursor.execute("INSERT INTO workloads (name, description, engine) VALUES (?, ?, ?)",
                   ("default_workload", "Default external-data workload run", "duckdb"))
    workload_id = cursor.lastrowid

    print(f"\nExecuting {len(queries)} queries...")
    for query_data in queries:
        print(f"  [{query_data['dataset']:12s}] {query_data['label'][:55]:55s} ...", end=' ', flush=True)
        execution = execute_query(duckdb_conn, query_data['query'], query_data['dataset'])
        store_execution(sqlite_conn, query_data, execution)
        print(f" {execution['status']:7s}  {execution['rows_returned']:4d} rows  {execution['runtime_ms']:8.2f}ms")

    duckdb_conn.close()
    sqlite_conn.close()
    print(f"\nQuery workload execution complete! {len(queries)} queries executed.")


if __name__ == "__main__":
    main()
