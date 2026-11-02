
import os
import re
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, Engine
from sqlglot import exp, parse
from sqlglot.errors import ParseError

load_dotenv()

_REQUIRED_SETTINGS = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
_missing = [
    key for key in _REQUIRED_SETTINGS
    if not os.getenv(key)
]

if _missing:
    raise RuntimeError(
        "Missing MySQL settings in .env: " + ", ".join(_missing)
    )

_database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME"),
    query={"charset": "utf8mb4"},
)

engine: Engine = create_engine(
    _database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=5,
    connect_args={"connect_timeout": 10},
)


def test_connection() -> dict[str, Any]:
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT DATABASE() AS database_name, VERSION() AS mysql_version")
        ).mappings().one()

    return dict(row)


def get_database_schema() -> str:
    inspector = inspect(engine)
    table_names = sorted(inspector.get_table_names())

    if not table_names:
        return "No tables were found in the configured database."

    sections = []

    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        lines = [f"Table: {table_name}", "Columns:"]

        for column in columns:
            nullable = "NULL" if column.get("nullable", True) else "NOT NULL"
            lines.append(
                f"  - {column['name']}: {column['type']} {nullable}"
            )

        foreign_keys = inspector.get_foreign_keys(table_name)

        for foreign_key in foreign_keys:
            constrained = ", ".join(
                foreign_key.get("constrained_columns") or []
            )
            referred_table = foreign_key.get("referred_table")
            referred_columns = ", ".join(
                foreign_key.get("referred_columns") or []
            )

            if referred_table:
                lines.append(
                    f"Foreign key: ({constrained}) -> "
                    f"{referred_table}({referred_columns})"
                )

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def validate_readonly_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise ValueError("The generated SQL is empty.")

    candidate = sql.strip()

    if len(candidate) > 20000:
        raise ValueError("The generated SQL exceeds the allowed length.")

    if "\x00" in candidate:
        raise ValueError("The SQL contains an invalid null character.")

    if re.search(r"/\*|--|#", candidate):
        raise ValueError("SQL comments are not permitted.")

    candidate = candidate.rstrip()

    if candidate.endswith(";"):
        candidate = candidate[:-1].rstrip()

    if ";" in candidate:
        raise ValueError("Only one SQL statement is allowed.")

    if re.search(
        r"\b(INSERT|UPDATE|DELETE|REPLACE|DROP|ALTER|CREATE|TRUNCATE|"
        r"GRANT|REVOKE|CALL|EXECUTE|PREPARE|DEALLOCATE|SET|"
        r"COMMIT|ROLLBACK|START\s+TRANSACTION|LOCK|UNLOCK)\b",
        candidate,
        flags=re.IGNORECASE,
    ):
        raise ValueError("The SQL contains a prohibited operation.")

    if re.search(
        r"\b(INTO\s+(OUTFILE|DUMPFILE)|FOR\s+UPDATE|"
        r"LOCK\s+IN\s+SHARE\s+MODE)\b",
        candidate,
        flags=re.IGNORECASE,
    ):
        raise ValueError("File output and locking queries are not allowed.")

    if re.search(
        r"\b(SLEEP|BENCHMARK|LOAD_FILE|GET_LOCK|RELEASE_LOCK)\s*\(",
        candidate,
        flags=re.IGNORECASE,
    ):
        raise ValueError("A prohibited SQL function was detected.")

    try:
        statements = parse(candidate, read="mysql")
    except ParseError as exc:
        raise ValueError(f"Could not parse generated MySQL SQL: {exc}") from exc

    statements = [statement for statement in statements if statement is not None]

    if len(statements) != 1:
        raise ValueError("Exactly one SQL statement is required.")

    statement = statements[0]

    if not isinstance(statement, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        raise ValueError("Only read-only SELECT queries are permitted.")

    forbidden_nodes = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Command,
        exp.Into,
    )

    for node_type in forbidden_nodes:
        if any(statement.find_all(node_type)):
            raise ValueError(
                f"The generated SQL contains a prohibited {node_type.__name__} operation."
            )

    cte_names = set()

    with_clause = statement.args.get("with") or statement.args.get("with_")

    if with_clause:
        for cte in with_clause.expressions:
            cte_names.add(cte.alias_or_name.lower())

    allowed_tables = {
        name.lower()
        for name in inspect(engine).get_table_names()
    }

    for table in statement.find_all(exp.Table):
        table_name = table.name.lower()
        database_name = table.db

        if table_name in cte_names:
            continue

        if database_name and database_name.lower() != (
            os.getenv("DB_NAME", "").lower()
        ):
            raise ValueError(
                f"Cross-database access is not allowed: {database_name}"
            )

        if table_name not in allowed_tables:
            raise ValueError(
                f"Table '{table.name}' is not available in the configured database."
            )

    return candidate


def execute_readonly_query(
    sql: str,
    max_rows: int = 200,
) -> list[dict[str, Any]]:
    if max_rows < 1 or max_rows > 1000:
        raise ValueError("max_rows must be between 1 and 1000.")

    safe_sql = validate_readonly_sql(sql)

    with engine.connect() as connection:
        result = connection.execute(text(safe_sql))
        rows = result.mappings().fetchmany(max_rows + 1)

    if len(rows) > max_rows:
        rows = rows[:max_rows]

    return [dict(row) for row in rows]
