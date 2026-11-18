import re

DISALLOWED_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "CALL",
    "MERGE",
    "UPSERT",
    "LOCK",
    "VACUUM",
    "REINDEX",
    "COMMENT",
    "COPY",
}

COMMENT_PATTERNS = [
    re.compile(r"--.*$", re.MULTILINE),
    re.compile(r"/\*.*?\*/", re.DOTALL),
]


class SQLValidationError(ValueError):
    """Raised when a SQL query violates security or read-only constraints."""
    pass


def validate_read_only_sql(sql: str) -> str:
    """
    Validates that a SQL string is strictly a single, read-only SELECT query.
    
    Raises SQLValidationError if:
    - Query is empty or whitespace only.
    - Query contains comments (-- or /* */).
    - Query contains multiple statements (semicolons separating queries).
    - Query does not start with SELECT or WITH (for CTEs).
    - Query contains any forbidden DDL/DML keywords as whole words.
    """
    if not sql or not sql.strip():
        raise SQLValidationError("SQL query cannot be empty.")

    cleaned_sql = sql.strip()

    # Reject comments that could be used for injection evasion
    for pattern in COMMENT_PATTERNS:
        if pattern.search(cleaned_sql):
            raise SQLValidationError("SQL comments are not permitted in queries.")

    # Remove trailing semicolon if present
    normalized_sql = cleaned_sql.rstrip(";").strip()

    # Check for multiple statements
    if ";" in normalized_sql:
        raise SQLValidationError("Multiple SQL statements in a single execution are forbidden.")

    # Ensure query begins with SELECT or WITH (Common Table Expression)
    first_token_match = re.match(r"^\s*([a-zA-Z]+)", normalized_sql)
    if not first_token_match:
        raise SQLValidationError("Invalid SQL syntax: missing leading command.")

    first_token = first_token_match.group(1).upper()
    if first_token not in {"SELECT", "WITH"}:
        raise SQLValidationError(
            f"Only read-only SELECT queries are allowed. Query began with '{first_token}'."
        )

    # Tokenize words to inspect disallowed keywords
    tokens = set(re.findall(r"\b[A-Z]+\b", normalized_sql.upper()))
    disallowed_found = tokens.intersection(DISALLOWED_KEYWORDS)
    if disallowed_found:
        raise SQLValidationError(
            f"Query contains forbidden modification keywords: {', '.join(sorted(disallowed_found))}."
        )

    return normalized_sql
