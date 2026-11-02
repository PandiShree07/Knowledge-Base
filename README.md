# Unified Knowledge Assistant — Large Demo Dataset

A single LangGraph-based assistant that answers questions from **OKF-style Markdown knowledge documents** and a **separate MySQL demo database**. It does not implement external document upload.

## What is included

- LangGraph flow: route → documents / MySQL / both → final answer.
- 40+ curated Markdown knowledge documents covering HR policies, security, engineering, product information, FAQs, and operating procedures.
- MySQL demo seed generator targeting approximately **1,000 employees, 5,000 attendance records, 2,500 leave records, 1,000 projects, and 3,000 tasks** (12,500 rows total).
- Safe seeding: the script is restricted to database name `uka_demo`, does not delete rows, and inserts only missing IDs.
- Runtime connection uses a separate SELECT-only account. Do not use the runtime account for seeding.
- SQL result output is capped at 200 rows.

> The bundled documents and rows are synthetic learning data. Do not use them as real HR or company records.

## 1. Requirements

- Python 3.10+
- Local MySQL 8.x server running
- Gemini API key

## 2. Create a separate demo database (Windows)

1. Extract this ZIP and open PowerShell in the `unified_knowledge_assistant_large_data` folder.
2. Open MySQL Workbench or the MySQL command-line client as an administrator.
3. Run the SQL in `sql/01_create_demo_database.sql`. It creates only `uka_demo` and two dedicated accounts. It does **not** alter your other databases.
4. Change the example passwords in that SQL script to strong passwords, and use the same values in `.env`.
5. Create and activate the Python environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

6. Edit `.env`:
   - `GEMINI_API_KEY`: your Gemini API key
   - `DB_*`: `uka_demo_reader` account details
   - `SEED_DB_*`: `uka_demo_seed` account details

The sample database name is deliberately fixed to `uka_demo` in the seed script. Do not change it to your real database name.

## 3. Seed the synthetic data

```powershell
python scripts/seed_demo_data.py
```

The script creates the tables and inserts missing synthetic records. Running it again is safe: it will not delete existing rows or overwrite records with the same IDs. Expected target counts after a fresh seed:

| Table | Rows |
|---|---:|
| employees | 1,000 |
| attendance | 5,000 |
| leave_records | 2,500 |
| projects | 1,000 |
| tasks | 3,000 |
| **Total** | **12,500** |

Check the connection and counts:

```powershell
python scripts/check_db.py
```

## 4. Run the assistant

```powershell
python app.py
```

Example questions:

- What is our annual leave policy?
- How many employees are in Engineering?
- Count attendance records marked absent by department.
- Which projects are in progress?
- Explain the remote work policy and list the most common work modes in attendance.
- What is the security incident reporting process?
- How many pending leave requests are there?
- Summarize the task statuses and explain the project delivery guidelines.

## 5. How documents work

The documents live under `knowledge/documents/`. Each file uses YAML frontmatter with `type`, `title`, `description`, and `tags`, followed by Markdown text. The current retriever uses lexical term overlap, which is simple and local. It is **not embedding-based vector RAG** yet. You do not need to convert other files or upload external documents for this version.

## 6. Database safety

- The app defaults to `uka_demo`, not your existing database.
- Run `sql/01_create_demo_database.sql` as an administrator to create a separate demo DB and accounts.
- Runtime credentials should have only `SELECT`/`SHOW VIEW` permissions.
- Seed credentials are separate and scoped to `uka_demo`.
- The seed script has a safety check requiring `SEED_DB_NAME=uka_demo` and never issues DELETE/TRUNCATE statements.
- Generated SQL is restricted to one SELECT/CTE and results are limited. SQL text checks are defense-in-depth; the read-only database account is the main protection.
- Never point the seed script at production or a real database.

## Troubleshooting

- **Access denied:** verify the usernames, host entries, passwords, and grants in the SQL setup file.
- **Unknown database:** run `sql/01_create_demo_database.sql` first.
- **Connection refused:** make sure MySQL is running and `DB_PORT` is correct (default `3306`).
- **Gemini API error:** check `GEMINI_API_KEY` and the model name in `.env`.
- **PowerShell blocks activation:** run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate the venv.


## Comments To Run 

- pip install -r requirements.txt
- copy .env.example .env
- python scripts/seed_demo_data.py
- python scripts/check_db.py
- python app.py