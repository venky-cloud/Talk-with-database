"""
MongoDB Injection Detection & Safety Validation
Similar to SQL injection detection but for MongoDB queries
"""

import re
import json
from typing import Dict, Any, List

# MongoDB Injection Patterns (NoSQL Injection)
MONGODB_INJECTION_PATTERNS = [
    # JavaScript injection in $where
    (r'\$where.*function\s*\(', 'JavaScript injection in $where operator detected'),
    (r'\$where.*\beval\b', 'eval() in $where detected (code injection)'),
    (r'\$where.*process\.', 'Process access in $where detected'),
    (r'\$where.*require\(', 'require() in $where detected'),
    
    # Command injection operators
    (r'\$ne\s*:\s*1', 'Always-true $ne injection (similar to OR 1=1)'),
    (r'\$ne\s*:\s*null', 'Always-true $ne:null injection'),
    (r'\$gt\s*:\s*""', 'Always-true $gt injection'),
    (r'\$regex\s*:\s*".*"', 'Regex injection pattern detected'),
    
    # NoSQL operator injection
    (r'\$or\s*:\s*\[\s*\{\s*\}\s*\]', 'Empty $or injection (bypass authentication)'),
    (r'\$ne\s*:\s*\{\s*\}', 'Empty object $ne injection'),
    
    # MongoDB system commands
    (r'db\..*\.drop\(', 'DROP collection command detected'),
    (r'db\.dropDatabase\(', 'DROP database command detected'),
    (r'db\..*\.remove\(.*\{\s*\}\s*\)', 'REMOVE all documents detected'),
    (r'db\..*\.deleteMany\(.*\{\s*\}\s*\)', 'DELETE all documents detected'),
    
    # mapReduce injection
    (r'db\..*\.mapReduce\(', 'mapReduce operation detected (potential injection)'),
    (r'\$function\s*:', '$function operator detected (code execution)'),
    (r'\$accumulator\s*:', '$accumulator operator detected (code execution)'),
    
    # Authentication bypass patterns
    (r'\[\s*\$ne\s*\]', 'Query parameter injection [$ne]'),
    (r'\[\s*\$gt\s*\]', 'Query parameter injection [$gt]'),
    (r'\[\s*\$regex\s*\]', 'Query parameter injection [$regex]'),
    
    # Blind NoSQL injection
    (r'sleep\s*\(', 'sleep() detected (time-based injection)'),
    (r'benchmark\s*\(', 'benchmark() detected (time-based injection)'),
    
    # Server-side JavaScript
    (r'db\.eval\(', 'db.eval() detected (deprecated, code execution)'),
    (r'db\..*\.group\(', 'group() operation detected (potential injection)'),
    
    # Type coercion attacks
    (r'\$type\s*:\s*2', '$type operator manipulation detected'),
    (r'\$expr\s*:', '$expr operator detected (potential injection)'),
]

def detect_mongodb_injection(query_str: str) -> Dict[str, Any]:
    """
    Detect MongoDB injection attempts in query strings.
    Returns {"detected": bool, "threats": list, "severity": str}
    """
    detected_issues = []
    
    # Convert to string if it's a dict
    if isinstance(query_str, dict):
        query_str = json.dumps(query_str)
    
    for pattern, reason in MONGODB_INJECTION_PATTERNS:
        if re.search(pattern, query_str, re.IGNORECASE | re.DOTALL):
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

def validate_mongodb_query(query: Dict[str, Any], operation: str = "find") -> Dict[str, Any]:
    """
    Validate MongoDB query for safety.
    Similar to SQL validation but for MongoDB operations.
    """
    safety = {"valid": False, "blocked": False, "reasons": []}
    
    query_str = json.dumps(query)
    
    # 1. MongoDB Injection Detection
    injection_result = detect_mongodb_injection(query_str)
    if injection_result["detected"]:
        safety["blocked"] = True
        safety["reasons"].extend([f"MONGODB_INJECTION: {r}" for r in injection_result["threats"]])
        safety["injection_severity"] = injection_result["severity"]
        return safety
    
    # Add warnings for suspicious patterns
    if injection_result["threats"]:
        safety["reasons"].extend([f"SUSPICIOUS: {r}" for r in injection_result["threats"]])
    
    # 2. Check for dangerous operations
    dangerous_ops = []
    
    # Check for empty delete/update queries (delete/update all)
    if operation in ["delete", "deleteMany", "remove"]:
        if not query or query == {}:
            dangerous_ops.append("DELETE without filter (deletes all documents)")
    
    if operation in ["update", "updateMany"]:
        if not query or query == {}:
            dangerous_ops.append("UPDATE without filter (updates all documents)")
    
    # Check for dangerous operators
    if "$where" in query_str:
        dangerous_ops.append("$where operator (allows JavaScript execution)")
    
    if "$function" in query_str:
        dangerous_ops.append("$function operator (allows code execution)")
    
    if "mapReduce" in query_str:
        dangerous_ops.append("mapReduce operation (potential security risk)")
    
    if "db.eval" in query_str:
        dangerous_ops.append("db.eval() (deprecated, code execution risk)")
    
    # Block if dangerous operations found
    if dangerous_ops:
        safety["blocked"] = True
        safety["reasons"].extend([f"DANGEROUS_OP: {op}" for op in dangerous_ops])
        return safety
    
    # 3. Check query structure
    try:
        # Ensure query is valid JSON
        if isinstance(query, dict):
            safety["valid"] = True
        else:
            safety["blocked"] = True
            safety["reasons"].append("INVALID: Query must be a valid dictionary/object")
            return safety
    except Exception as e:
        safety["blocked"] = True
        safety["reasons"].append(f"PARSE_ERROR: {str(e)}")
        return safety
    
    # 4. Check for authentication bypass patterns
    auth_bypass = []
    
    # Pattern: {username: {$ne: null}} - bypass authentication
    if "$ne" in query_str and ("null" in query_str or '""' in query_str):
        auth_bypass.append("Potential authentication bypass using $ne")
    
    # Pattern: {$or: [{}]} - always true
    if "$or" in query_str and "{}" in query_str:
        auth_bypass.append("Potential authentication bypass using empty $or")
    
    if auth_bypass:
        safety["blocked"] = True
        safety["reasons"].extend([f"AUTH_BYPASS: {p}" for p in auth_bypass])
        return safety
    
    # If we made it here, query is safe
    safety["valid"] = True
    return safety

def sanitize_mongodb_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize MongoDB query by removing dangerous operators.
    """
    sanitized = {}
    
    dangerous_operators = [
        "$where", "$function", "$accumulator", "$expr"
    ]
    
    for key, value in query.items():
        if key in dangerous_operators:
            continue  # Skip dangerous operators
        
        if isinstance(value, dict):
            sanitized[key] = sanitize_mongodb_query(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_mongodb_query(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

def get_safe_mongodb_options():
    """
    Return safe MongoDB query options.
    """
    return {
        "max_documents": 1000,  # Limit results
        "timeout_ms": 5000,  # Query timeout
        "allow_disk_use": False,  # Prevent disk-heavy operations
        "disable_where": True,  # Disable $where operator
        "disable_function": True,  # Disable $function operator
    }
