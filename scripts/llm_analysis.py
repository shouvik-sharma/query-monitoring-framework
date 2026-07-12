"""Analyze queries using LLM, generate optimized rewrites, store results in query_history.db."""

import os
import sqlite3
import json
import time
import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'data' / 'query_history.db'
DATASETS_DIR = ROOT / 'data' / 'raw'

# Try to import OpenAI safely
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Sample data setup for DuckDB to execute rewritten queries
datasets = {
    'usgs': {
        'table': 'earthquakes',
        'data': [
            ('2023-01-01 12:00:00', 34.123, -118.456, 5.5, 'Los Angeles, CA'),
            ('2023-01-02 15:30:00', 37.7749, -122.4194, 6.1, 'San Francisco, CA'),
            ('2023-01-03 09:15:00', 40.7128, -74.0060, 4.8, 'New York, NY')
        ]
    },
    'noaa': {
        'table': 'weather',
        'data': [
            ('01001099999', '2023-01-01 12:00:00', 22.5, 15.2, 1013.2),
            ('01001099999', '2023-01-02 12:00:00', 25.1, 16.3, 1011.8),
            ('01001099999', '2023-01-03 12:00:00', 28.3, 18.2, 1009.5)
        ]
    },
    'awid': {
        'table': 'wifi_network',
        'data': [
            ('2023-01-01 10:00:00', '00:11:22:33:44:55', -45, 'normal'),
            ('2023-01-01 10:01:00', 'aa:bb:cc:dd:ee:ff', -65, 'normal'),
            ('2023-01-01 10:02:00', '11:22:33:44:55:66', -30, 'normal')
        ]
    }
}

def setup_duckdb():
    """Load sample datasets into DuckDB memory tables"""
    conn = duckdb.connect()
    
    # Earthquakes
    conn.execute("CREATE TABLE earthquakes (time TIMESTAMP, latitude FLOAT, longitude FLOAT, mag FLOAT, place VARCHAR)")
    conn.executemany("INSERT INTO earthquakes VALUES (?, ?, ?, ?, ?)", datasets['usgs']['data'])
    
    # Weather
    conn.execute("CREATE TABLE weather (STATION VARCHAR, DATE TIMESTAMP, TMP FLOAT, DEW FLOAT, SLP FLOAT)")
    conn.executemany("INSERT INTO weather VALUES (?, ?, ?, ?, ?)", datasets['noaa']['data'])
    
    # Wi-Fi
    conn.execute("CREATE TABLE wifi_network (frame_time_epoch TIMESTAMP, wlan_sa VARCHAR, radiotap_dbm_antsignal INTEGER, class VARCHAR)")
    conn.executemany("INSERT INTO wifi_network VALUES (?, ?, ?, ?)", datasets['awid']['data'])
    
    return conn

def execute_sql(duckdb_conn, sql):
    """Execute SQL against DuckDB and measure metrics"""
    start = time.time()
    try:
        res = duckdb_conn.execute(sql).fetchall()
        runtime_ms = (time.time() - start) * 1000
        return {
            'status': 'success',
            'runtime_ms': runtime_ms,
            'rows_returned': len(res),
            'error_message': None
        }
    except Exception as e:
        runtime_ms = (time.time() - start) * 1000
        return {
            'status': 'error',
            'runtime_ms': runtime_ms,
            'rows_returned': 0,
            'error_message': str(e)
        }

def analyze_query_with_llm(query_text, query_label, inefficiency_type):
    """Analyze query using OpenAI if available, or simulate if not"""
    if HAS_OPENAI and OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            prompt = f"""
            Analyze the following SQL query for correctness and optimization opportunities.
            
            Output in this strict JSON format:
            {{
                "score": <0-100 integer score where 0 is perfect and 100 has critical anti-patterns>,
                "issues_found": [<list of specific string issues>],
                "recommendation": "<complete rewritten optimized SQL query text>",
                "improvement_reason": "<explanation of improvements>",
                "expected_category": "<runtime, readability, or correctness>"
            }}
            
            SQL Query:
            {query_text}
            """
            start_llm = time.time()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            latency_ms = int((time.time() - start_llm) * 1000)
            data = json.loads(response.choices[0].message.content)
            
            return {
                'score': data.get('score', 0),
                'score_reason': data.get('improvement_reason', 'Analysis completed successfully.'),
                'issues_found': json.dumps(data.get('issues_found', [])),
                'recommended_query': data.get('recommendation', query_text),
                'improvement_reason': data.get('improvement_reason', ''),
                'expected_category': data.get('expected_category', 'readability'),
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'llm_cost_usd': (response.usage.prompt_tokens * 0.15 + response.usage.completion_tokens * 0.6) / 1000000.0,
                'latency_ms': latency_ms,
                'error': None
            }
        except Exception as e:
            return {'error': str(e)}

    # Fallback simulation
    latency_ms = 450 + int(hash(query_label) % 300)
    input_tokens = 150 + int(hash(query_text) % 50)
    output_tokens = 200 + int(hash(query_label) % 100)
    # Estimate standard mini API costs: $0.15/1M input, $0.60/1M output
    llm_cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1000000.0

    if inefficiency_type is None:
        # Optimal query
        return {
            'score': 15,
            'score_reason': "Query is well-structured, uses specific column projection, and includes necessary filters.",
            'issues_found': json.dumps([]),
            'recommended_query': query_text,
            'improvement_reason': "No restructuring required.",
            'expected_category': "readability",
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'llm_cost_usd': llm_cost,
            'latency_ms': latency_ms,
            'error': None
        }
    
    # Inefficient query simulation
    if inefficiency_type == 'select_star':
        rec_query = query_text.replace("SELECT *", "SELECT place, mag, time")
        return {
            'score': 65,
            'score_reason': "Using SELECT * pulls all column metadata and increases memory footprint. Specific projection should be used instead.",
            'issues_found': json.dumps(["Unnecessary column selection", "Over-fetching database columns"]),
            'recommended_query': rec_query,
            'improvement_reason': "Replaced wildcard projection with explicit place, mag, and time columns.",
            'expected_category': "runtime",
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'llm_cost_usd': llm_cost,
            'latency_ms': latency_ms,
            'error': None
        }
    elif inefficiency_type == 'missing_predicate':
        rec_query = query_text.replace("FROM earthquakes", "FROM earthquakes WHERE mag > 4.0")
        return {
            'score': 75,
            'score_reason': "Table scan performed without predicate filter. Suggest adding specific filter criteria.",
            'issues_found': json.dumps(["Full table scan", "Missing WHERE clause filters"]),
            'recommended_query': rec_query,
            'improvement_reason': "Added mag predicate to filter records early in the execution plan.",
            'expected_category': "runtime",
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'llm_cost_usd': llm_cost,
            'latency_ms': latency_ms,
            'error': None
        }
    elif inefficiency_type == 'cross_join':
        rec_query = "SELECT w1.STATION, w1.TMP, w2.TMP AS TMP2\nFROM weather w1 JOIN weather w2 ON w1.STATION = w2.STATION AND w1.DATE = w2.DATE"
        return {
            'score': 90,
            'score_reason': "Unintended Cartesian product due to missing join conditions. Will cause exponential row growth.",
            'issues_found': json.dumps(["Cross join detected", "Exponential performance degradation danger"]),
            'recommended_query': rec_query,
            'improvement_reason': "Converted implicit cross join to explicit inner join on STATION and DATE variables.",
            'expected_category': "runtime",
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'llm_cost_usd': llm_cost,
            'latency_ms': latency_ms,
            'error': None
        }
    elif inefficiency_type == 'redundant_subquery':
        rec_query = """SELECT frame_time_epoch, wlan_sa, radiotap_dbm_antsignal, class FROM wifi_network WHERE radiotap_dbm_antsignal > -60"""
        return {
            'score': 55,
            'score_reason': "Redundant subquery wrapping. Suggest flattening query and combining filters.",
            'issues_found': json.dumps(["Redundant subquery projection", "Layered nested projection overhead"]),
            'recommended_query': rec_query,
            'improvement_reason': "Flattened the nested query structure and merged predicate logic.",
            'expected_category': "readability",
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'llm_cost_usd': llm_cost,
            'latency_ms': latency_ms,
            'error': None
        }
    
    return {
        'score': 50,
        'score_reason': "Analysis complete.",
        'issues_found': json.dumps([]),
        'recommended_query': query_text,
        'improvement_reason': "",
        'expected_category': "readability",
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'llm_cost_usd': llm_cost,
        'latency_ms': latency_ms,
        'error': None
    }

def main():
    if not (HAS_OPENAI and OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-")):
        print("WARNING: No valid OPENAI_API_KEY found. Running in SIMULATION mode.")
        print("         Results will be deterministic defaults, not real LLM calls.")
        print("         Set OPENAI_API_KEY to reproduce measured paper results.\n")
    print("Starting LLM query analysis pipeline...")
    duckdb_conn = setup_duckdb()
    sqlite_conn = sqlite3.connect(DB_PATH)
    cursor = sqlite_conn.cursor()
    
    # Clear previous analysis entries for a clean run
    cursor.execute("DELETE FROM cost_comparisons")
    cursor.execute("DELETE FROM recommendations")
    cursor.execute("DELETE FROM llm_analyses")
    sqlite_conn.commit()
    
    # Read all executed queries
    cursor.execute("""
        SELECT q.id, q.query_text, q.query_label, q.inefficiency_type, q.is_baseline, qe.id
        FROM queries q
        JOIN query_executions qe ON q.id = qe.query_id
        WHERE qe.execution_label = 'original'
    """)
    rows = cursor.fetchall()
    print(f"Loaded {len(rows)} executions to analyze.")
    
    for query_id, query_text, query_label, inefficiency_type, is_baseline, orig_exec_id in rows:
        print(f"\nAnalyzing: {query_label}")
        
        # Call analysis
        analysis = analyze_query_with_llm(query_text, query_label, inefficiency_type)
        if analysis.get('error'):
            print(f"  Error: {analysis['error']}")
            continue
            
        # Store in llm_analyses table
        cursor.execute("""
            INSERT INTO llm_analyses (
                query_id, model, prompt_version, score, score_reason, 
                issues_found, input_tokens, output_tokens, llm_cost_usd, latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query_id, 
            "gpt-4o-mini" if (HAS_OPENAI and OPENAI_API_KEY) else "simulated-gpt-4o-mini",
            "v1.0-reproducible",
            analysis['score'],
            analysis['score_reason'],
            analysis['issues_found'],
            analysis['input_tokens'],
            analysis['output_tokens'],
            analysis['llm_cost_usd'],
            analysis['latency_ms']
        ))
        analysis_id = cursor.lastrowid
        print(f"  Risk Score: {analysis['score']}")
        
        # If query has potential optimizations, generate recommendation and test it
        if analysis['score'] >= 40:
            print("  Generating recommendation...")
            cursor.execute("""
                INSERT INTO recommendations (
                    query_id, llm_analysis_id, recommended_query, 
                    improvement_reason, expected_improvement_category, improvement_suggestion
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                query_id,
                analysis_id,
                analysis['recommended_query'],
                analysis['improvement_reason'],
                analysis['expected_category'],
                f"Issues found: {analysis['issues_found']}"
            ))
            rec_id = cursor.lastrowid
            
            # Execute rewritten query against DuckDB
            print("  Executing rewritten query...")
            rewritten_exec = execute_sql(duckdb_conn, analysis['recommended_query'])
            
            cursor.execute("""
                INSERT INTO query_executions (
                    query_id, execution_label, engine, status, runtime_ms, 
                    rows_returned, explain_plan, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query_id,
                'rewritten',
                'duckdb',
                rewritten_exec['status'],
                rewritten_exec['runtime_ms'],
                rewritten_exec['rows_returned'],
                '',
                rewritten_exec['error_message']
            ))
            rewritten_exec_id = cursor.lastrowid
            print(f"    Rewritten Runtime: {rewritten_exec['runtime_ms']:.2f}ms")
            
             # Get original execution stats
            cursor.execute("SELECT runtime_ms, rows_returned, result_checksum FROM query_executions WHERE id = ?", (orig_exec_id,))
            orig_runtime, orig_rows, orig_checksum = cursor.fetchone()
            
            # Calculate cost comparisons
            # Note: with <10-row datasets, sub-millisecond runtimes are noisy.
            # Negative values indicate the rewritten query ran slower in this tiny test.
            runtime_improvement_pct = 0.0
            if orig_runtime > 0:
                runtime_improvement_pct = ((orig_runtime - rewritten_exec['runtime_ms']) / orig_runtime) * 100

            rows_match = int(orig_rows == rewritten_exec['rows_returned'])
            checksum_match = int(orig_checksum == rewritten_exec.get('result_checksum', ''))
            semantic_match = int(checksum_match and rewritten_exec['status'] == 'success')
            
            cursor.execute("""
                INSERT INTO cost_comparisons (
                    query_id, recommendation_id, original_execution_id, rewritten_execution_id,
                    original_runtime_ms, rewritten_runtime_ms, runtime_improvement_pct,
                    original_rows, rewritten_rows, rows_match, checksum_match, semantic_match,
                    validation_status, llm_total_cost_usd, net_cost_improvement, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query_id,
                rec_id,
                orig_exec_id,
                rewritten_exec_id,
                int(orig_runtime),
                int(rewritten_exec['runtime_ms']),
                round(runtime_improvement_pct, 2),
                orig_rows,
                rewritten_exec['rows_returned'],
                rows_match,
                semantic_match, # checksum match
                semantic_match,
                'match' if semantic_match else 'mismatch',
                analysis['llm_cost_usd'],
                f"Saved {round(runtime_improvement_pct, 2)}% runtime",
                "Recreated from external metadata benchmark."
            ))
            
    sqlite_conn.commit()
    duckdb_conn.close()
    sqlite_conn.close()
    print("\nLLM query analysis and recommendation execution pipeline complete!")

if __name__ == '__main__':
    main()