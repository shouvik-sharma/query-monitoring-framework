# sqlaudit vs LLM-Based Approach Comparison Report

## Executive Summary

- **Total queries analyzed:** 91
- **sqlaudit Accuracy (WARNING+):** 45.1%
- **sqlaudit Precision (WARNING+):** 0.0%
- **sqlaudit Recall (WARNING+):** 0.0%
- **sqlaudit F1 Score (WARNING+):** 0.0%
- **sqlaudit False Positive Rate (WARNING+):** 0.0%

- **sqlaudit Accuracy (any finding):** 84.6%
- **sqlaudit Precision (any finding):** 82.1%
- **sqlaudit Recall (any finding):** 92.0%
- **sqlaudit F1 Score (any finding):** 86.8%
- **sqlaudit False Positive Rate (any finding):** 24.4%

## Confusion Matrix (WARNING+ severity as flag)

| | sqlaudit Flags | sqlaudit Accepts |
|---|---|---|
| **Inefficient (GT)** | TP=0 | FN=50 |
| **Baseline (GT)** | FP=0 | TN=41 |

## Confusion Matrix (any finding as flag)

| | sqlaudit Flags | sqlaudit Accepts |
|---|---|---|
| **Inefficient (GT)** | TP=46 | FN=4 |
| **Baseline (GT)** | FP=10 | TN=31 |

## Per-Pattern Detection Comparison

| Anti-Pattern Type | Total | sqlaudit Detected (WARNING+) | Detection Rate (WARNING+) | sqlaudit Detected (any) | Detection Rate (any) |
|---|---|---|---|---|---|
| cross_join | 4 | 0 | 0.0% | 4 | 100.0% |
| distinct_group | 4 | 0 | 0.0% | 4 | 100.0% |
| implicit_coercion | 4 | 0 | 0.0% | 4 | 100.0% |
| like_prefix | 4 | 0 | 0.0% | 4 | 100.0% |
| missing_group_col | 4 | 0 | 0.0% | 0 | 0.0% |
| missing_limit | 3 | 0 | 0.0% | 3 | 100.0% |
| missing_predicate | 4 | 0 | 0.0% | 4 | 100.0% |
| non_sargable | 5 | 0 | 0.0% | 5 | 100.0% |
| or_vs_in | 4 | 0 | 0.0% | 4 | 100.0% |
| redundant_subquery | 5 | 0 | 0.0% | 5 | 100.0% |
| select_star | 5 | 0 | 0.0% | 5 | 100.0% |
| union_all | 4 | 0 | 0.0% | 4 | 100.0% |

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

### USGS - Magnitude distribution
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### USGS - Deep earthquakes
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### USGS - Recent earthquakes by location
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P008: Function NOW() used in WHERE  --  may prevent index usage

### USGS - Earthquake frequency by month
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### USGS - High magnitude earthquakes
- **Dataset:** usgs
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - Temperature range by station
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - High humidity days
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - Pressure variation
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - Recent weather readings
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P008: Function NOW() used in WHERE  --  may prevent index usage

### NOAA - Temperature trends
- **Dataset:** noaa
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Signal strength distribution
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Device activity by class
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 98/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### AWID - Strong signal attacks
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - MAC prefix analysis
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Signal strength by class
- **Dataset:** awid
- **Ground Truth:** Baseline
- **sqlaudit Score:** 98/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Products - Category statistics
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 98/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Products - High value items
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Products - Stock levels
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 98/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Products - Price distribution
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 98/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Products - Recent inventory
- **Dataset:** products
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Customer order frequency
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Revenue by status
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 98/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Orders - High value customers
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Monthly order count
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### Orders - Average order value
- **Dataset:** orders
- **Ground Truth:** Baseline
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### NOAA - SELECT * variant
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Unnecessary column selection
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### AWID - SELECT * with filter
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Unnecessary column selection
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Orders - SELECT * variant
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Unnecessary column selection
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### NOAA - Missing predicate (full scan)
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Full table scan without filters
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### AWID - Missing predicate (full scan)
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Full table scan without filters
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Products - Missing predicate (full scan)
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** Full table scan without filters
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### USGS - Cross join variant
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Unintended Cartesian product
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Products - Cross join variant
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** Unintended Cartesian product
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Orders - Cross join variant
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Unintended Cartesian product
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### USGS - Redundant subquery variant
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Redundant nested query
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly

### NOAA - Redundant subquery variant
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Redundant nested query
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly

### Orders - Redundant subquery variant
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Redundant nested query
- **sqlaudit Score:** 95/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P001: SELECT * found  --  specify columns explicitly

### NOAA - Non-sargable MONTH() predicate
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Function on indexed column prevents index seek
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [warning] P008: Function MONTH() used in WHERE  --  may prevent index usage

### AWID - Non-sargable SUBSTR() predicate
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Function on indexed column prevents index seek
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Orders - Non-sargable YEAR() predicate
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Function on indexed column prevents index seek
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [warning] P008: Function YEAR() used in WHERE  --  may prevent index usage

### AWID - Missing LIMIT on ordered query
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Unbounded result set from missing LIMIT
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### USGS - OR instead of IN
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Multiple OR conditions instead of IN list
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P006: Multiple OR conditions on same column  --  use IN (...) instead
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### NOAA - OR instead of IN
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** Multiple OR conditions instead of IN list
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P006: Multiple OR conditions on same column  --  use IN (...) instead
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Products - OR instead of IN
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** Multiple OR conditions instead of IN list
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [info] P006: Multiple OR conditions on same column  --  use IN (...) instead
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### USGS - LIKE with leading wildcard
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Leading wildcard prevents index usage
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P003: Leading wildcard in LIKE pattern: '%CA%'
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Products - LIKE with leading wildcard
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** Leading wildcard prevents index usage
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P003: Leading wildcard in LIKE pattern: '%Widget%'
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Orders - LIKE with leading wildcard
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Leading wildcard prevents index usage
- **sqlaudit Score:** 94/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [warning] P003: Leading wildcard in LIKE pattern: '%pending%'
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### USGS - Implicit type coercion
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** Type mismatch forces implicit conversion
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### AWID - Implicit type coercion
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** Type mismatch forces implicit conversion
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Orders - Implicit type coercion
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** Type mismatch forces implicit conversion
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### NOAA - DISTINCT instead of GROUP BY
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** DISTINCT used where GROUP BY is more appropriate
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Products - DISTINCT instead of GROUP BY
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** DISTINCT used where GROUP BY is more appropriate
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### Orders - DISTINCT instead of GROUP BY
- **Dataset:** orders
- **Ground Truth:** Inefficient
- **Expected Issue:** DISTINCT used where GROUP BY is more appropriate
- **sqlaudit Score:** 97/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results
  - [info] P010: ORDER BY without LIMIT sorts entire result set

### USGS - UNION instead of UNION ALL
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** UNION instead of UNION ALL (no duplicate removal needed)
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### NOAA - UNION instead of UNION ALL
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** UNION instead of UNION ALL (no duplicate removal needed)
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### Products - UNION instead of UNION ALL
- **Dataset:** products
- **Ground Truth:** Inefficient
- **Expected Issue:** UNION instead of UNION ALL (no duplicate removal needed)
- **sqlaudit Score:** 99/100
- **sqlaudit Flags:** Yes
- **sqlaudit Findings:**
  - [hint] P007: SELECT without LIMIT  --  consider adding LIMIT for bounded results

### USGS - Missing GROUP BY column
- **Dataset:** usgs
- **Ground Truth:** Inefficient
- **Expected Issue:** GROUP BY does not include all non-aggregate columns
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### NOAA - Missing GROUP BY column
- **Dataset:** noaa
- **Ground Truth:** Inefficient
- **Expected Issue:** GROUP BY does not include all non-aggregate columns
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

### AWID - Missing GROUP BY column
- **Dataset:** awid
- **Ground Truth:** Inefficient
- **Expected Issue:** GROUP BY does not include all non-aggregate columns
- **sqlaudit Score:** 100/100
- **sqlaudit Flags:** No

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