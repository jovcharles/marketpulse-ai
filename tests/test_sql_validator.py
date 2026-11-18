import pytest
from backend.app.services.sql_validator import SQLValidationError, validate_read_only_sql


def test_validate_valid_select_query():
    sql = "SELECT symbol, close FROM prices WHERE symbol = %s LIMIT 10;"
    result = validate_read_only_sql(sql)
    assert result == "SELECT symbol, close FROM prices WHERE symbol = %s LIMIT 10"


def test_validate_valid_with_cte():
    sql = """
        WITH cte AS (
            SELECT symbol, close FROM prices WHERE symbol = %s
        )
        SELECT * FROM cte;
    """
    result = validate_read_only_sql(sql)
    assert result.startswith("WITH cte AS")


def test_validate_rejects_empty():
    with pytest.raises(SQLValidationError, match="cannot be empty"):
        validate_read_only_sql("")

    with pytest.raises(SQLValidationError, match="cannot be empty"):
        validate_read_only_sql("   ")


def test_validate_rejects_dml_statements():
    bad_queries = [
        "DELETE FROM prices WHERE symbol = 'BTC-USD';",
        "INSERT INTO prices (symbol) VALUES ('BTC-USD');",
        "UPDATE prices SET close = 0;",
        "DROP TABLE prices;",
        "ALTER TABLE prices ADD COLUMN test INT;",
        "TRUNCATE TABLE prices;",
        "CREATE TABLE test (id INT);",
        "GRANT ALL ON prices TO public;",
    ]
    for q in bad_queries:
        with pytest.raises(SQLValidationError):
            validate_read_only_sql(q)


def test_validate_rejects_embedded_forbidden_keywords():
    injection = "SELECT * FROM prices; DROP TABLE prices;"
    with pytest.raises(SQLValidationError, match="Multiple SQL statements"):
        validate_read_only_sql(injection)


def test_validate_rejects_sql_comments():
    with pytest.raises(SQLValidationError, match="SQL comments are not permitted"):
        validate_read_only_sql("SELECT * FROM prices -- comment here")

    with pytest.raises(SQLValidationError, match="SQL comments are not permitted"):
        validate_read_only_sql("SELECT * /* block comment */ FROM prices")
