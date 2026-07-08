
#!/usr/bin/env python3
"""
AI-Powered Query Monitoring (Hackweek 2025)
Monitors Snowflake queries, scores them for correctness, and sends alerts via Slack.
"""

import os
import pandas as pd
import snowflake.connector
import openai
import re
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------------------
# GPT Model Configuration
# ----------------------------------------
# Using GPT-5 for maximum capability
GPT_MODEL = "gpt-5-chat-latest"  # Working GPT-5 model for all AI operations
# Alternative GPT-5 models if needed:
# GPT_MODEL = "gpt-5"  # Base GPT-5 (returns empty responses)
# GPT_MODEL = "gpt-5-nano"  # GPT-5 nano (returns empty responses)
# GPT_MODEL = "gpt-5-mini"  # GPT-5 mini (returns empty responses)
# Fallback to GPT-4 if needed:
# GPT_MODEL = "gpt-4"  # GPT-4 for maximum accuracy

# ----------------------------------------
# Configuration from Environment
# ----------------------------------------
SNOWFLAKE_CONFIG = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'authenticator': 'externalbrowser',
    'autocommit': True,
    'database': os.getenv('SNOWFLAKE_DATABASE'),
    'timezone': os.getenv('SNOWFLAKE_TIMEZONE'),
    'role': os.getenv('SNOWFLAKE_ROLE'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'multi_statement': True,
    'abort_detached_query': True,
    'network_timeout': 900,
    'login_timeout': 24 * 3600,
}

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_TARGET_EMAIL = os.getenv('SLACK_TARGET_EMAIL')

# ----------------------------------------
# Initialize Clients
# ----------------------------------------
def init_clients():
    """Initialize OpenAI and Slack clients."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment")
    if not SLACK_BOT_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN not set in environment")
    
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    slack_client = WebClient(token=SLACK_BOT_TOKEN)
    
    return openai_client, slack_client

# ----------------------------------------
# Snowflake Connection
# ----------------------------------------
def get_snowflake_connection():
    """Create and return Snowflake connection."""
    return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

def fetch_query_to_df(query, conn):
    """Execute query and return results as pandas DataFrame."""
    cur = conn.cursor()
    try:
        cur.execute(query)
        return cur.fetch_pandas_all()
    finally:
        cur.close()

# ----------------------------------------
# AI Functions
# ----------------------------------------
def _response_text(r):
    """Extract text from OpenAI response object."""
    if getattr(r, "output_text", None):
        return r.output_text
    
    # Responses API structure fallback
    try:
        parts = []
        for item in getattr(r, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                t = getattr(c, "text", None)
                if t:
                    parts.append(t)
        if parts:
            return " ".join(parts)
    except Exception:
        pass
    
    # Chat Completions-style fallback
    if hasattr(r, "choices") and r.choices:
        return r.choices[0].message.content or ""
    return ""

def ai_sql_incorrectness_score(sql: str, openai_client, model=GPT_MODEL) -> int:
    """Score SQL query critical issues (0-100, higher = more critical).
    Uses GPT-5 for maximum accuracy in scoring. Only scores 80+ for truly problematic queries."""
    prompt = (
        'Return ONLY JSON like {"score": <0-100 integer>} for SQL CRITICAL ISSUES. '
        'Score based on: '
        '0-20=excellent/optimal queries, '
        '21-40=good with minor inefficiencies (SELECT *, missing indexes), '
        '41-60=moderate issues (inefficient joins, suboptimal filters), '
        '61-80=significant problems (performance risks, potential data issues), '
        '81-100=CRITICAL issues ONLY (broken logic, security risks, major performance problems that WILL cause failures). '
        'IMPORTANT: Only score 80+ for queries that NEED IMMEDIATE ATTENTION and will cause serious problems. '
        'Queries with just inefficiencies should score 60 or below. '
        'Be conservative with high scores. No extra text.\nSQL:\n' + sql
    )
    
    try:
        r = openai_client.responses.create(
            model=model,
            input=[{"role": "user", "content": prompt}],
            max_output_tokens=16384  # GPT-5-chat-latest limit
        )
        text = _response_text(r).strip()
        
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
        
        try:
            score = int(json.loads(text)["score"])
        except Exception:
            m = re.search(r"\b(100|[1-9]?\d)\b", text)
            score = int(m.group(1)) if m else 0
        
        return max(0, min(100, score))
    except Exception as e:
        print(f"Error scoring SQL: {e}")
        return 0

def ai_sql_restructure_query(query_text: str, openai_client, model=GPT_MODEL) -> str:
    """Rewrite SQL query to fix mistakes and improve performance."""
    prompt = (
        "You are a Snowflake SQL expert. Rewrite the following SQL query to fix any mistakes and improve performance. "
        "If the query is correct, return the same query, don't over optimize it. "
        "Output only the corrected or optimized query, nothing else.\nSQL:\n" + query_text
    )
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful SQL rewriter."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=16384  # GPT-5-chat-latest limit
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def ai_sql_review(query_text: str, openai_client, model: str = GPT_MODEL) -> str:
    """Review SQL query for correctness risks and inefficiencies."""
    prompt = (
        "You are a Snowflake SQL expert. Briefly review the query for correctness risks "
        "(missing joins, wrong filters, alias issues) and major inefficiencies. "
        "Return 3–6 short bullet points.\nSQL:\n" + query_text
    )
    
    try:
        resp = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise Snowflake SQL reviewer."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=16384,  # GPT-5-chat-latest limit
        )
        result = resp.choices[0].message.content.strip()
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# ----------------------------------------
# Main Monitoring Logic
# ----------------------------------------
def fetch_long_running_queries(conn):
    """Fetch queries running longer than 5 minutes."""
    query = '''
    SELECT
        QUERY_ID,
        USER_NAME,
        WAREHOUSE_NAME,
        START_TIME,
        EXECUTION_STATUS,
        TOTAL_ELAPSED_TIME,
        QUERY_TEXT
    FROM TABLE(SNOWFLAKE.INFORMATION_SCHEMA.QUERY_HISTORY(result_limit=> 10000))
    WHERE EXECUTION_STATUS = 'RUNNING'
        AND QUERY_TYPE = 'SELECT'
        AND datediff('millisecond', start_time, current_timestamp()) > 300000
    '''
    
    return fetch_query_to_df(query, conn)

def process_and_score_queries(df, openai_client):
    """Process queries and score them for correctness."""
    results = []
    
    for i, row in df.iterrows():
        query_id = row["QUERY_ID"]
        user = row["USER_NAME"]
        wh = row["WAREHOUSE_NAME"]
        start_time = row["START_TIME"]
        elapsed = row["TOTAL_ELAPSED_TIME"]
        sql_text = row["QUERY_TEXT"]

        print(f"Processing query {i+1}/{len(df)}: {query_id}")
        score = ai_sql_incorrectness_score(sql_text, openai_client)

        results.append({
            "QUERY_ID": query_id,
            "USER_NAME": user,
            "WAREHOUSE_NAME": wh,
            "START_TIME": start_time,
            "ELAPSED_MS": elapsed,
            "INCORRECTNESS_SCORE": score,
            "QUERY_TEXT": sql_text,
        })

    return pd.DataFrame(results)

def process_high_risk_queries(bad_results_df, openai_client):
    """Process high-risk queries (score > 70) with AI review and restructuring."""
    results_restructured = []
    
    for i, row in bad_results_df.iterrows():
        query_id = row["QUERY_ID"]
        user = row["USER_NAME"]
        warehouse = row["WAREHOUSE_NAME"]
        start_time = row["START_TIME"]
        elapsed_ms = row.get("ELAPSED_MS")
        sql_text = row["QUERY_TEXT"]

        print(f"\n--- Processing High-Risk Query {i+1}/{len(bad_results_df)} ---")
        print(f"QUERY_ID: {query_id}")
        print(f"USER: {user}")
        print(f"WAREHOUSE: {warehouse}")
        print(f"START_TIME: {start_time}")
        print(f"Elapsed (ms): {elapsed_ms}")

        ai_review = ai_sql_review(sql_text, openai_client)
        restructured_query = ai_sql_restructure_query(sql_text, openai_client)

        results_restructured.append({
            "QUERY_ID": query_id,
            "USER_NAME": user,
            "WAREHOUSE_NAME": warehouse,
            "START_TIME": start_time,
            "ELAPSED_MS": elapsed_ms,
            "AI_REVIEW": ai_review,
            "QUERY_TEXT": sql_text,
            "RESTRUCTURED_QUERY": restructured_query
        })

    return pd.DataFrame(results_restructured)

def send_slack_alerts(results_df, slack_client):
    """Send Slack DM alerts for high-risk queries."""
    if not SLACK_TARGET_EMAIL:
        print("SLACK_TARGET_EMAIL not set, skipping Slack alerts")
        return
    
    try:
        # Look up user by email
        u = slack_client.users_lookupByEmail(email=SLACK_TARGET_EMAIL)
        user_id = u["user"]["id"]

        # Open DM channel
        dm = slack_client.conversations_open(users=user_id)
        channel_id = dm["channel"]["id"]

        # Send alerts for each high-risk query
        rows = results_df.to_dict("records")
        
        for r in rows:
            ai_review = str(r.get("AI_REVIEW") or "")
            restructured = str(r.get("RESTRUCTURED_QUERY") or "")
            start_ts = r.get("START_TIME")
            start_ts_str = start_ts.isoformat() if hasattr(start_ts, "isoformat") else str(start_ts)

            msg = (
                f"*Query Alert*\n"
                f"*QUERY_ID*: `{r['QUERY_ID']}`\n"
                f"*USER*: {r.get('USER_NAME')}\n"
                f"*WAREHOUSE*: {r.get('WAREHOUSE_NAME')}\n"
                f"*START_TIME*: {start_ts_str}\n"
                f"*ELAPSED_MS*: {r.get('ELAPSED_MS')}\n\n"
                f"*AI Review:*\n{ai_review}\n\n"
                f"*Restructured Query:*\n```{restructured}```"
            )

            slack_client.chat_postMessage(channel=channel_id, text=msg)
            print(f"Sent Slack alert for query {r['QUERY_ID']}")
            
    except SlackApiError as e:
        print(f"Slack API error: {e.response.get('error')}")
    except Exception as e:
        print(f"Error sending Slack alerts: {e}")

# ----------------------------------------
# Main Execution
# ----------------------------------------
def main():
    """Main execution function."""
    print("Starting AI-Powered Query Monitoring...")
    
    try:
        # Initialize clients
        openai_client, slack_client = init_clients()
        
        # Connect to Snowflake
        print("Connecting to Snowflake...")
        conn = get_snowflake_connection()
        
        # Fetch long-running queries
        print("Fetching long-running queries...")
        df = fetch_long_running_queries(conn)
        print(f"Found {len(df)} running queries over 5 minutes.")
        
        if len(df) == 0:
            print("No long-running queries found.")
            return
        
        # Score queries for correctness
        print("Scoring queries for correctness...")
        results_df = process_and_score_queries(df, openai_client)
        
        # Filter high-risk queries (score > 80) - only truly problematic queries
        bad_results_df = results_df[results_df["INCORRECTNESS_SCORE"] > 80]
        print(f"Found {len(bad_results_df)} high-risk queries (score > 80).")
        
        if len(bad_results_df) == 0:
            print("No high-risk queries found.")
            return
        
        # Process high-risk queries with AI
        print("Processing high-risk queries with AI...")
        results_restructured_df = process_high_risk_queries(bad_results_df, openai_client)
        
        # Send Slack alerts
        print("Sending Slack alerts...")
        send_slack_alerts(results_restructured_df, slack_client)
        
        print("Monitoring complete!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
