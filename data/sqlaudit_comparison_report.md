# sqlaudit vs LLM-Based Approach Comparison Report

## Executive Summary

- **Total queries analyzed:** 32
- **sqlaudit Accuracy (WARNING+):** 50.0%
- **sqlaudit Precision (WARNING+):** 0.0%
- **sqlaudit Recall (WARNING+):** 0.0%
- **sqlaudit F1 Score (WARNING+):** 0.0%
- **sqlaudit False Positive Rate (WARNING+):** 0.0%

- **sqlaudit Accuracy (any finding):** 93.8%
- **sqlaudit Precision (any finding):** 93.8%
- **sqlaudit Recall (any finding):** 93.8%
- **sqlaudit F1 Score (any finding):** 93.8%
- **sqlaudit False Positive Rate (any finding):** 6.2%

## Confusion Matrix (WARNING+ severity as flag)

| | sqlaudit Flags | sqlaudit Accepts |
|---|---|---|
| **Inefficient (GT)** | TP=0 | FN=16 |
| **Baseline (GT)** | FP=0 | TN=16 |

## Confusion Matrix (any finding as flag)

| | sqlaudit Flags | sqlaudit Accepts |
|---|---|---|
| **Inefficient (GT)** | TP=15 | FN=1 |
| **Baseline (GT)** | FP=1 | TN=15 |

## Per-Pattern Detection Comparison

| Anti-Pattern Type | Total | sqlaudit Detected (WARNING+) | Detection Rate (WARNING+) | sqlaudit Detected (any) | Detection Rate (any) |
|---|---|---|---|---|---|
| cross_join | 1 | 0 | 0.0% | 1 | 100.0% |
| distinct_group | 1 | 0 | 0.0% | 1 | 100.0% |
| implicit_coercion | 1 | 0 | 0.0% | 1 | 100.0% |
| like_prefix | 1 | 0 | 0.0% | 1 | 100.0% |
| missing_group_col | 1 | 0 | 0.0% | 0 | 0.0% |
| missing_limit | 2 | 0 | 0.0% | 2 | 100.0% |
| missing_predicate | 1 | 0 | 0.0% | 1 | 100.0% |
| non_sargable | 2 | 0 | 0.0% | 2 | 100.0% |
| or_vs_in | 1 | 0 | 0.0% | 1 | 100.0% |
| redundant_subquery | 2 | 0 | 0.0% | 2 | 100.0% |
| select_star | 2 | 0 | 0.0% | 2 | 100.0% |
| union_all | 1 | 0 | 0.0% | 1 | 100.0% |

## Detailed Findings by Query

### USGS - Large earthquakes by magnitude
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### USGS - Recent California earthquakes
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P003: Leading wildcard in LIKE pattern: '%CA%'

### USGS - Shallow earthquake count by region
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - High temperature stations
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - Average temperature by station
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - Days with large pressure drops
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Strong signal devices
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Normal traffic by MAC prefix
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Attack signal distribution
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Products - Top-selling items
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Products - Average price by category
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Products - Low stock alerts
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - High-value recent orders
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Monthly revenue summary
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Top customers by spend
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Pending high-value orders
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### USGS - SELECT * variant
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Unnecessary column selection
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### USGS - Missing predicate (full scan)
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Full table scan without filters
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### USGS - Non-sargable YEAR() predicate
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Function on indexed column prevents index seek
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P008: Function YEAR() used in WHERE  --  may prevent index usage

### USGS - DISTINCT instead of GROUP BY
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** DISTINCT used where GROUP BY is more appropriate
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### NOAA - Cross join variant
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Unintended Cartesian product
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### NOAA - Missing LIMIT on ordered query
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Unbounded result set from missing LIMIT
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### NOAA - Implicit type coercion
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Type mismatch forces implicit conversion
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### AWID - Nested subquery variant
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Redundant nested query
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly

### AWID - OR instead of IN
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Multiple OR conditions instead of IN list
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P006: Multiple OR conditions on same column  --  use IN (...) instead
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### AWID - LIKE with leading wildcard
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Leading wildcard prevents index usage
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P003: Leading wildcard in LIKE pattern: '%:ff'
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Products - SELECT * with full scan
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** Unnecessary column selection
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Products - Missing GROUP BY column
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** GROUP BY does not include all non-aggregate columns
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Products - Non-sargable string function
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** Function on indexed column prevents index seek
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P008: Function LOWER() used in WHERE  --  may prevent index usage

### Orders - UNION instead of UNION ALL
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** UNION instead of UNION ALL (no duplicate removal needed)
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] S006: UNION after string literal  --  possible injection pattern

### Orders - Redundant subquery wrapping
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Redundant nested query
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly

### Orders - Missing LIMIT with ORDER BY
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Unbounded result set from missing LIMIT
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

## Key Insights

### What sqlaudit Catches Well
- SELECT * patterns (P001)
- Missing LIMIT clauses (P007, P010)
- Function on indexed columns (P008)
- Multiple OR conditions (P006)

### What sqlaudit Misses
- Semantic issues requiring context understanding
- Cross joins without explicit join syntax
- Implicit type coercion
- Missing predicates (full scans)
- UNION vs UNION ALL distinction

### Limitations of Rule-Based Approach
1. **No context understanding:** sqlaudit cannot distinguish between intentional full scans and accidental ones
2. **No rewrite generation:** It identifies issues but doesn't propose fixes
3. **No execution validation:** Cannot verify if rewrites preserve semantics
4. **Fixed rule set:** Cannot adapt to domain-specific patterns