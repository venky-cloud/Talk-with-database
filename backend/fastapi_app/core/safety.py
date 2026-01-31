from __future__ import annotations
from typing import Dict, Any
import re
from sqlglot import parse_one, exp
from .config import settings

BLOCKED = {"DROP", "TRUNCATE", "ALTER"}

# SQL Injection Detection Patterns (OWASP-based)
SQL_INJECTION_PATTERNS = [
    # Union-based injection
    (r'UNION\s+(ALL\s+)?SELECT', 'UNION SELECT injection detected'),
    # Boolean-based injection
    (r'(OR|AND)\s+[\'"]?\d+[\'"]?\s*=\s*[\'"]?\d+[\'"]?', 'Boolean-based injection (OR 1=1) detected'),
    (r'(OR|AND)\s+[\'"]?[a-zA-Z]+[\'"]?\s*=\s*[\'"]?[a-zA-Z]+[\'"]?', 'Boolean-based injection detected'),
    # Time-based injection
    (r'(SLEEP|BENCHMARK|WAITFOR\s+DELAY)', 'Time-based injection detected'),
    # Stacked queries
    (r';\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER)', 'Stacked query injection detected'),
    # Comment-based evasion
    (r'/\*.*?\*/', 'SQL comment detected (potential evasion)'),
    (r'--\s', 'SQL comment detected (potential injection)'),
    (r'#', 'MySQL comment detected'),
    # String concatenation attacks
    (r'CONCAT\s*\(.*SELECT', 'CONCAT with subquery (data exfiltration)'),
    (r'\|\|.*SELECT', 'Concatenation with subquery detected'),
    # Information schema access
    (r'information_schema\.', 'Information schema access detected'),
    (r'sys\.(tables|columns)', 'System catalog access detected'),
    # Hex/ASCII encoding
    (r'0x[0-9a-fA-F]+', 'Hexadecimal encoding detected'),
    (r'CHAR\s*\(', 'CHAR encoding detected'),
    # File operations
    (r'LOAD_FILE\s*\(', 'LOAD_FILE detected (file read attempt)'),
    (r'INTO\s+OUTFILE', 'INTO OUTFILE detected (file write attempt)'),
    # Command execution
    (r'xp_cmdshell', 'xp_cmdshell detected (command execution)'),
    (r'EXEC\s+', 'EXEC detected (potential command execution)'),
    # Nested queries (excessive depth)
    (r'\(\s*SELECT.*SELECT.*SELECT', 'Excessive query nesting detected'),
]


def detect_sql_injection(query: str) -> Dict[str, Any]:
    """
    Detect SQL injection attempts using regex patterns.
    Returns {"detected": bool, "threats": list, "severity": str}
    """
    detected_issues = []
    query_upper = query.upper()
    
    for pattern, reason in SQL_INJECTION_PATTERNS:
        if re.search(pattern, query_upper, re.IGNORECASE | re.DOTALL):
            detected_issues.append(reason)
    
    # Severity based on number of patterns matched
    if len(detected_issues) >= 3:
        severity = "CRITICAL"
        is_detected = True
    elif len(detected_issues) >= 2:
        severity = "HIGH"
        is_detected = True
    elif len(detected_issues) == 1:
        severity = "MEDIUM"
        is_detected = True
    else:
        severity = "LOW"
        is_detected = False
    
    return {
        "detected": is_detected,
        "threats": detected_issues,
        "severity": severity,
        "threat_count": len(detected_issues)
    }


def validate_query(query: str, db_type: str = "mysql") -> Dict[str, Any]:
    safety = {"valid_syntax": False, "blocked": False, "reasons": []}
    
    # 1. SQL Injection Detection (Advanced)
    injection_result = detect_sql_injection(query)
    if injection_result["detected"]:
        safety["blocked"] = True
        safety["reasons"].extend([f"SQL_INJECTION: {r}" for r in injection_result["threats"]])
        safety["injection_severity"] = injection_result["severity"]
        return safety
    
    # Add warnings for suspicious patterns even if not blocked
    if injection_result["threats"]:
        safety["reasons"].extend([f"SUSPICIOUS: {r}" for r in injection_result["threats"]])
    
    # 2. Check for escaped underscores or backslashes in identifiers
    if "\\" in query:
        # Look for backslash followed by underscore outside of quotes
        if re.search(r'\\_', query):
            safety["blocked"] = True
            safety["reasons"].append("Query contains escaped underscores (\\_). Use plain identifiers (e.g., customer_id not customer\\_id)")
            return safety
    
    try:
        tree = parse_one(query, read=db_type)
        safety["valid_syntax"] = True
        # Block DDL
        if isinstance(tree, (exp.Drop, exp.Truncate, exp.Alter)):
            safety["blocked"] = True
            safety["reasons"].append("DDL is blocked")
        # Block DELETE/UPDATE without WHERE
        if isinstance(tree, exp.Delete) and not tree.args.get("where"):
            safety["blocked"] = True
            safety["reasons"].append("DELETE without WHERE is blocked")
        if isinstance(tree, exp.Update) and not tree.args.get("where"):
            safety["blocked"] = True
            safety["reasons"].append("UPDATE without WHERE is blocked")
        # Enforce LIMIT on SELECT
        if isinstance(tree, exp.Select):
            limit = tree.args.get("limit")
            if not limit:
                safety["reasons"].append("SELECT missing LIMIT; will cap at runtime")
    except Exception as e:
        safety["reasons"].append(f"parse_error: {e}")
    # Simple injection heuristics
    lower = query.lower()
    if "--" in lower:
        safety["reasons"].append("inline comment detected")
    # Allow single semicolon at end, but block multiple statements
    if query.count(";") > 1 or (query.count(";") == 1 and not query.rstrip().endswith(";")):
        safety["blocked"] = True
        safety["reasons"].append("multi-statement queries are blocked")
    return safety
