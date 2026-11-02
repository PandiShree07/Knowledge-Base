from sqlalchemy import inspect, text

from app.db import engine, get_database_schema, test_connection

print("Connection:", test_connection())
print("\nSchema:\n", get_database_schema())
with engine.connect() as conn:
    for table in inspect(engine).get_table_names():
        count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar_one()
        print(f"{table}: {count:,} rows")
