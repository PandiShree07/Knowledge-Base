"""Seed deterministic sample records into the separate uka_demo database.
Safe to rerun: it never deletes rows and inserts only IDs that do not already exist.
"""
import os
import random
from datetime import date, timedelta
from pathlib import Path
import sys
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, MetaData, Table, Column, Integer, String, Date, ForeignKey, Text, inspect, select

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

host = os.getenv("SEED_DB_HOST", "127.0.0.1")
port = int(os.getenv("SEED_DB_PORT", "3306"))
db_name = os.getenv("SEED_DB_NAME", "uka_demo")
user = os.getenv("SEED_DB_USER", "systemroot")
password = os.getenv("SEED_DB_PASSWORD", "")
if db_name.lower() != "uka_demo":
    raise SystemExit("Safety stop: SEED_DB_NAME must be 'uka_demo'. This seed script is intentionally restricted to the demo database.")
if not password or password.startswith("change_me"):
    raise SystemExit("Set SEED_DB_PASSWORD in .env before running this script.")

engine = create_engine(URL.create("mysql+pymysql", username=user, password=password, host=host, port=port, database=db_name, query={"charset":"utf8mb4"}), pool_pre_ping=True)
meta = MetaData()
employees = Table("employees", meta,
    Column("id", Integer, primary_key=True), Column("full_name", String(120), nullable=False),
    Column("email", String(180), nullable=False, unique=True), Column("department", String(80), nullable=False),
    Column("job_title", String(100), nullable=False), Column("manager_name", String(120), nullable=False),
    Column("location", String(80), nullable=False), Column("hire_date", Date, nullable=False),
    Column("salary_band", String(30), nullable=False), Column("employment_status", String(30), nullable=False))
attendance = Table("attendance", meta,
    Column("id", Integer, primary_key=True), Column("employee_id", Integer, ForeignKey("employees.id"), nullable=False),
    Column("attendance_date", Date, nullable=False), Column("status", String(30), nullable=False),
    Column("hours_worked", Integer, nullable=False), Column("work_mode", String(30), nullable=False))
leave_records = Table("leave_records", meta,
    Column("id", Integer, primary_key=True), Column("employee_id", Integer, ForeignKey("employees.id"), nullable=False),
    Column("leave_type", String(40), nullable=False), Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=False), Column("days", Integer, nullable=False),
    Column("status", String(30), nullable=False), Column("reason", String(180), nullable=False))
projects = Table("projects", meta,
    Column("id", Integer, primary_key=True), Column("project_name", String(140), nullable=False),
    Column("department", String(80), nullable=False), Column("owner_employee_id", Integer, ForeignKey("employees.id"), nullable=False),
    Column("status", String(30), nullable=False), Column("priority", String(20), nullable=False),
    Column("start_date", Date, nullable=False), Column("target_date", Date, nullable=False), Column("budget_band", String(30), nullable=False))
tasks = Table("tasks", meta,
    Column("id", Integer, primary_key=True), Column("project_id", Integer, ForeignKey("projects.id"), nullable=False),
    Column("assignee_employee_id", Integer, ForeignKey("employees.id"), nullable=False), Column("title", String(180), nullable=False),
    Column("status", String(30), nullable=False), Column("priority", String(20), nullable=False),
    Column("estimated_hours", Integer, nullable=False), Column("created_date", Date, nullable=False), Column("due_date", Date, nullable=False))

first_names = ["Aarav", "Aditi", "Akash", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya", "Kiran", "Meera", "Nisha", "Pranav", "Priya", "Rahul", "Riya", "Rohan", "Sanjay", "Sneha", "Varun", "Vikram", "Yamini", "Dev", "Lakshmi", "Manoj", "Pooja", "Shreya", "Surya", "Tanvi", "Vijay", "Zoya"]
last_names = ["Kumar", "Sharma", "Nair", "Reddy", "Iyer", "Patel", "Das", "Menon", "Singh", "Rao", "Pillai", "Gupta", "Joseph", "Fernandes", "Mishra", "Bose", "Verma", "Khan", "Thomas", "Roy"]
departments = ["Engineering", "Sales", "Human Resources", "Finance", "Operations", "Customer Support", "Marketing", "Data", "Security", "Product"]
roles = ["Software Engineer", "Senior Engineer", "Analyst", "Team Lead", "Project Manager", "Support Specialist", "Data Engineer", "QA Engineer", "HR Executive", "Account Manager"]
locations = ["Chennai", "Bengaluru", "Hyderabad", "Mumbai", "Pune", "Delhi", "Coimbatore", "Remote"]
leave_types = ["annual", "sick", "casual", "parental", "unpaid"]
statuses = ["approved", "pending", "rejected"]
project_statuses = ["planning", "in_progress", "completed", "on_hold"]
task_statuses = ["todo", "in_progress", "blocked", "completed"]

def chunks(seq, size=500):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def insert_missing(conn, table, rows):
    if not rows:
        return 0
    existing_ids = set(conn.execute(select(table.c.id)).scalars().all())
    missing = [row for row in rows if row["id"] not in existing_ids]
    for batch in chunks(missing):
        conn.execute(table.insert(), batch)
    return len(missing)

rng = random.Random(20261017)
today = date(2026, 10, 17)
with engine.begin() as conn:
    meta.create_all(conn)
    existing = inspect(conn).get_table_names()
    expected = {"employees", "attendance", "leave_records", "projects", "tasks"}
    if not expected.issubset(set(existing)):
        raise SystemExit("Expected demo tables could not be created.")

    employee_rows = []
    for i in range(1, 1001):
        first = first_names[(i * 7) % len(first_names)]
        last = last_names[(i * 11) % len(last_names)]
        employee_rows.append({
            "id": i, "full_name": f"{first} {last} {i:04d}", "email": f"employee{i:04d}@example.test",
            "department": departments[(i * 3) % len(departments)], "job_title": roles[(i * 5) % len(roles)],
            "manager_name": f"{first_names[(i + 4) % len(first_names)]} {last_names[(i + 2) % len(last_names)]}",
            "location": locations[(i * 2) % len(locations)], "hire_date": date(2016, 1, 1) + timedelta(days=(i * 13) % 3900),
            "salary_band": ["B1", "B2", "B3", "B4", "B5"][(i * 7) % 5],
            "employment_status": "active" if i % 23 else "on_leave",
        })
    inserted_employees = insert_missing(conn, employees, employee_rows)

    attendance_rows = []
    for i in range(1, 5001):
        emp = ((i * 37) % 1000) + 1
        day = today - timedelta(days=(i * 3) % 365)
        attendance_rows.append({"id": i, "employee_id": emp, "attendance_date": day,
            "status": ["present", "present", "present", "remote", "absent", "half_day", "leave"][(i * 5) % 7],
            "hours_worked": [0, 4, 6, 7, 8, 9][(i * 3) % 6], "work_mode": ["office", "remote", "hybrid"][(i * 11) % 3]})
    inserted_attendance = insert_missing(conn, attendance, attendance_rows)

    leave_rows = []
    for i in range(1, 2501):
        emp = ((i * 19) % 1000) + 1
        start = today - timedelta(days=(i * 7) % 700)
        days = 1 + (i % 5)
        leave_rows.append({"id": i, "employee_id": emp, "leave_type": leave_types[(i * 3) % len(leave_types)],
            "start_date": start, "end_date": start + timedelta(days=days - 1), "days": days,
            "status": statuses[(i * 7) % len(statuses)],
            "reason": ["Personal appointment", "Family commitment", "Medical rest", "Vacation", "Personal work"][(i * 13) % 5]})
    inserted_leaves = insert_missing(conn, leave_records, leave_rows)

    project_rows = []
    for i in range(1, 1001):
        start = today - timedelta(days=(i * 17) % 900)
        project_rows.append({"id": i, "project_name": f"{departments[(i * 3) % len(departments)]} Initiative {i:04d}",
            "department": departments[(i * 3) % len(departments)], "owner_employee_id": ((i * 23) % 1000) + 1,
            "status": project_statuses[(i * 5) % len(project_statuses)], "priority": ["low", "medium", "high", "critical"][(i * 7) % 4],
            "start_date": start, "target_date": start + timedelta(days=30 + (i % 180)), "budget_band": ["under_10k", "10k_50k", "50k_100k", "over_100k"][(i * 3) % 4]})
    inserted_projects = insert_missing(conn, projects, project_rows)

    task_rows = []
    for i in range(1, 3001):
        created = today - timedelta(days=(i * 5) % 500)
        task_rows.append({"id": i, "project_id": ((i * 13) % 1000) + 1, "assignee_employee_id": ((i * 29) % 1000) + 1,
            "title": f"Work item {i:04d}: {['review requirements', 'implement feature', 'validate data', 'write tests', 'prepare release notes'][(i * 7) % 5]}",
            "status": task_statuses[(i * 11) % len(task_statuses)], "priority": ["low", "medium", "high", "critical"][(i * 3) % 4],
            "estimated_hours": 1 + (i * 7) % 40, "created_date": created, "due_date": created + timedelta(days=1 + (i % 45))})
    inserted_tasks = insert_missing(conn, tasks, task_rows)

    counts = {table.name: conn.execute(select(__import__('sqlalchemy').func.count()).select_from(table)).scalar_one() for table in [employees, attendance, leave_records, projects, tasks]}

print("Seed complete. No existing rows were deleted or overwritten.")
print(f"Database: {db_name}")
print(f"New rows inserted: employees={inserted_employees}, attendance={inserted_attendance}, leave_records={inserted_leaves}, projects={inserted_projects}, tasks={inserted_tasks}")
print("Current row counts:")
for name, count in counts.items():
    print(f"  {name}: {count:,}")
