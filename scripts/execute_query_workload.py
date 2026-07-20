"""Execute query workload and store results in query_history.db"""

import csv
import sqlite3
import duckdb
import json
import time
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'query_history.db'
QUERY_WORKLOAD_PATH = ROOT / 'data' / 'query_workload.json'
DATASETS_DIR = ROOT / 'data' / 'raw'

N_ROWS = 500


def read_csv_sample(csv_path: Path, n_rows: int) -> list[tuple]:
    """Read up to n_rows from a CSV file, returning list of tuples."""
    rows = []
    with csv_path.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for i, row in enumerate(reader):
            if i >= n_rows:
                break
            rows.append(tuple(row))
    return rows


def setup_duckdb():
    conn = duckdb.connect()

    # USGS Earthquakes from CSV (columns: time=0, latitude=1, longitude=2, depth=3, mag=4, place=13)
    usgs_path = DATASETS_DIR / 'usgs' / 'all_month.csv'
    if usgs_path.exists():
        print(f"  Loading USGS data from {usgs_path.name}...")
        raw = read_csv_sample(usgs_path, N_ROWS)
        conn.execute("CREATE TABLE earthquakes (time TIMESTAMP, latitude FLOAT, longitude FLOAT, depth FLOAT, mag FLOAT, place VARCHAR)")
        for row in raw:
            try:
                ts = row[0].replace("T", " ").replace("Z", "") if len(row) > 0 else ""
                lat = float(row[1]) if len(row) > 1 and row[1] else 0.0
                lon = float(row[2]) if len(row) > 2 and row[2] else 0.0
                depth = float(row[3]) if len(row) > 3 and row[3] else 0.0
                mag = float(row[4]) if len(row) > 4 and row[4] else 0.0
                place = row[13] if len(row) > 13 else ""
                conn.execute("INSERT INTO earthquakes VALUES (?, ?, ?, ?, ?, ?)", (ts, lat, lon, depth, mag, place))
            except (ValueError, IndexError):
                continue
        n_usgs = conn.execute("SELECT COUNT(*) FROM earthquakes").fetchone()[0]
    else:
        print("  USGS CSV not found, creating empty table")
        conn.execute("CREATE TABLE earthquakes (time TIMESTAMP, latitude FLOAT, longitude FLOAT, depth FLOAT, mag FLOAT, place VARCHAR)")
        n_usgs = 0

    # NOAA Weather from CSV (columns: STATION=0, DATE=1, TMP=13, DEW=14, SLP=15)
    noaa_path = DATASETS_DIR / 'noaa' / '01001099999.csv'
    if noaa_path.exists():
        print(f"  Loading NOAA data from {noaa_path.name}...")
        raw = read_csv_sample(noaa_path, N_ROWS)
        conn.execute("CREATE TABLE weather (STATION VARCHAR, DATE VARCHAR, TMP FLOAT, DEW FLOAT, SLP FLOAT)")
        for row in raw:
            try:
                station = row[0] if len(row) > 0 else ""
                date_val = row[1] if len(row) > 1 else ""
                tmp_str = row[13] if len(row) > 13 else ""
                dew_str = row[14] if len(row) > 14 else ""
                slp_str = row[15] if len(row) > 15 else ""
                # NOAA uses format like "55.0,1" where first part is value
                tmp = float(tmp_str.split(",")[0]) if tmp_str and "," in tmp_str else (float(tmp_str) if tmp_str else 0.0)
                dew = float(dew_str.split(",")[0]) if dew_str and "," in dew_str else (float(dew_str) if dew_str else 0.0)
                slp = float(slp_str.split(",")[0]) if slp_str and "," in slp_str else (float(slp_str) if slp_str else 0.0)
                conn.execute("INSERT INTO weather VALUES (?, ?, ?, ?, ?)", (station, date_val, tmp, dew, slp))
            except (ValueError, IndexError):
                continue
        n_noaa = conn.execute("SELECT COUNT(*) FROM weather").fetchone()[0]
    else:
        print("  NOAA CSV not found, creating empty table")
        conn.execute("CREATE TABLE weather (STATION VARCHAR, DATE VARCHAR, TMP FLOAT, DEW FLOAT, SLP FLOAT)")
        n_noaa = 0

    # AWID Wi-Fi from CSV (columns: frame.time_epoch=3, wlan.sa=78, radiotap.dbm_antsignal=60, class=83)
    awid_path = DATASETS_DIR / 'kaggle_wifi' / 'extracted' / 'AWID.csv'
    if awid_path.exists():
        print(f"  Loading AWID data from {awid_path.name}...")
        raw = read_csv_sample(awid_path, N_ROWS)
        conn.execute("CREATE TABLE wifi_network (frame_time_epoch VARCHAR, wlan_sa VARCHAR, radiotap_dbm_antsignal INTEGER, class VARCHAR)")
        for row in raw:
            try:
                ts = row[3] if len(row) > 3 else ""
                mac = row[78] if len(row) > 78 else ""
                sig_str = row[60] if len(row) > 60 else "0"
                sig = int(float(sig_str)) if sig_str else 0
                cls = row[83] if len(row) > 83 else "normal"
                conn.execute("INSERT INTO wifi_network VALUES (?, ?, ?, ?)", (ts, mac, sig, cls))
            except (ValueError, IndexError):
                continue
        n_awid = conn.execute("SELECT COUNT(*) FROM wifi_network").fetchone()[0]
    else:
        print("  AWID CSV not found, creating empty table")
        conn.execute("CREATE TABLE wifi_network (frame_time_epoch VARCHAR, wlan_sa VARCHAR, radiotap_dbm_antsignal INTEGER, class VARCHAR)")
        n_awid = 0

    # Products from derived CSV
    products_path = DATASETS_DIR / 'uci_online_retail' / 'products.csv'
    if products_path.exists():
        print(f"  Loading products data from {products_path.name}...")
        raw = read_csv_sample(products_path, N_ROWS)
        conn.execute("CREATE TABLE products (product_name VARCHAR, category VARCHAR, price FLOAT, stock_qty INTEGER)")
        for row in raw:
            try:
                pname = row[1] if len(row) > 1 else ""
                cat = row[2] if len(row) > 2 else "General"
                price = float(row[3]) if len(row) > 3 and row[3] else 0.0
                stock = int(float(row[4])) if len(row) > 4 and row[4] else 0
                conn.execute("INSERT INTO products VALUES (?, ?, ?, ?)", (pname, cat, price, stock))
            except (ValueError, IndexError):
                continue
        n_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    else:
        print("  Products CSV not found, creating empty table")
        conn.execute("CREATE TABLE products (product_name VARCHAR, category VARCHAR, price FLOAT, stock_qty INTEGER)")
        n_products = 0

    # Orders from derived CSV
    orders_path = DATASETS_DIR / 'uci_online_retail' / 'orders.csv'
    if orders_path.exists():
        print(f"  Loading orders data from {orders_path.name}...")
        raw = read_csv_sample(orders_path, N_ROWS)
        conn.execute("CREATE TABLE orders (order_id VARCHAR, customer_id VARCHAR, total_amount FLOAT, order_date DATE, status VARCHAR)")
        for row in raw:
            try:
                oid = row[0] if len(row) > 0 else ""
                cid = row[1] if len(row) > 1 else "0"
                amt = float(row[2]) if len(row) > 2 and row[2] else 0.0
                odate = row[3][:10] if len(row) > 3 else "2011-01-01"
                status = row[4] if len(row) > 4 else "completed"
                conn.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", (oid, cid, amt, odate, status))
            except (ValueError, IndexError):
                continue
        n_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    else:
        print("  Orders CSV not found, creating empty table")
        conn.execute("CREATE TABLE orders (order_id VARCHAR, customer_id VARCHAR, total_amount FLOAT, order_date DATE, status VARCHAR)")
        n_orders = 0

    for table, n in [('earthquakes', n_usgs), ('weather', n_noaa), ('wifi_network', n_awid),
                     ('products', n_products), ('orders', n_orders)]:
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
