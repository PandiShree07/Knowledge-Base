
import os
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict

from dotenv import load_dotenv
from google import genai
from langgraph.graph import END, START, StateGraph

from app.db import execute_readonly_query, get_database_schema
from app.knowledge import load_knowledge, retrieve_documents

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "").strip()
BASE_DIR = Path(__file__).resolve().parent.parent

TRANSIENT_ERROR_CODES = ("429", "500", "502", "503", "504")


class AssistantState(TypedDict, total=False):
    question: str
    route: str
    route_note: str
    knowledge: list[dict]
    doc_hits: list[dict]
    schema: str
    sql: str
    sql_rows: list[dict]
    evidence: str
    answer: str


def _is_transient_error(exc: Exception) -> bool:
    message = str(exc).lower()

    return (
        any(code in message for code in TRANSIENT_ERROR_CODES)
        or "unavailable" in message
        or "resource_exhausted" in message
        or "rate limit" in message
        or "timed out" in message
        or "timeout" in message
    )


def _generate_with_model(
    client: genai.Client,
    model: str,
    prompt: str,
) -> str:
    start_time = time.perf_counter()
    print(f"[TIMING] Gemini request started. Model: {model}")

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        answer = response.text

        if not answer or not answer.strip():
            raise RuntimeError(f"Model {model} returned an empty response.")

        return answer.strip()
    finally:
        elapsed = time.perf_counter() - start_time
        print(
            f"[TIMING] Gemini request finished in {elapsed:.2f} seconds. "
            f"Model: {model}"
        )


def gemini_text(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "put_your_gemini_api_key_here":
        raise RuntimeError("Set GEMINI_API_KEY in your .env file.")

    if not GEMINI_MODEL:
        raise RuntimeError("Set GEMINI_MODEL in your .env file.")

    client = genai.Client(api_key=api_key)
    primary_error = None

    for attempt in range(2):
        try:
            return _generate_with_model(client, GEMINI_MODEL, prompt)
        except Exception as exc:
            primary_error = exc

            if not _is_transient_error(exc):
                break

            if attempt == 0:
                delay = 1
                print(
                    f"[RETRY] Primary model temporarily unavailable. "
                    f"Retrying in {delay} second."
                )
                time.sleep(delay)

    if GEMINI_FALLBACK_MODEL and GEMINI_FALLBACK_MODEL != GEMINI_MODEL:
        print(
            f"[FALLBACK] Trying configured fallback model: "
            f"{GEMINI_FALLBACK_MODEL}"
        )

        try:
            return _generate_with_model(
                client,
                GEMINI_FALLBACK_MODEL,
                prompt,
            )
        except Exception as fallback_error:
            raise RuntimeError(
                "Both Gemini models failed. "
                f"Primary model ({GEMINI_MODEL}): {primary_error}. "
                f"Fallback model ({GEMINI_FALLBACK_MODEL}): {fallback_error}"
            ) from fallback_error

    raise RuntimeError(
        f"Gemini model {GEMINI_MODEL} failed: {primary_error}. "
        "Configure GEMINI_FALLBACK_MODEL in .env to enable fallback."
    ) from primary_error


@lru_cache(maxsize=1)
def get_cached_knowledge():
    return load_knowledge()


@lru_cache(maxsize=1)
def get_cached_schema() -> str:
    return get_database_schema()


def local_route(question: str) -> str:
    q = question.lower()

    sql_terms = (
        "employee",
        "employees",
        "department",
        "attendance",
        "leave",
        "project",
        "projects",
        "task",
        "tasks",
        "database",
        "records",
        "salary",
        "salaries",
        "count",
        "how many",
        "total",
        "average",
        "sum",
        "list",
        "show",
        "compare",
        "highest",
        "lowest",
        "top",
        "pending",
        "absent",
        "in progress",
        "in_progress",
    )

    doc_terms = (
        "policy",
        "policies",
        "explain",
        "guideline",
        "guidelines",
        "rule",
        "rules",
        "process",
        "procedure",
        "faq",
        "remote work",
        "security",
        "leave entitlement",
        "what does",
        "how do i",
    )

    asks_sql = any(term in q for term in sql_terms)
    asks_docs = any(term in q for term in doc_terms)

    if asks_sql and asks_docs:
        return "both"

    if asks_sql:
        return "sql"

    return "documents"


def route_node(state: AssistantState) -> AssistantState:
    question = state["question"].strip()
    route = local_route(question)

    return {
        "route": route,
        "route_note": "Local keyword router selected the knowledge source.",
        "knowledge": get_cached_knowledge(),
        "schema": get_cached_schema(),
    }


def document_node(state: AssistantState) -> AssistantState:
    start_time = time.perf_counter()

    hits = retrieve_documents(
        state["question"],
        state["knowledge"],
        limit=5,
    )

    print(
        "[TIMING] Document retrieval completed in "
        f"{time.perf_counter() - start_time:.2f} seconds."
    )

    return {"doc_hits": hits}


def _extract_sql(response: str) -> str:
    sql = response.strip()

    fenced = re.fullmatch(
        r"```(?:mysql|sql)?\s*(.*?)\s*```",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if fenced:
        sql = fenced.group(1).strip()

    return sql


def sql_node(state: AssistantState) -> AssistantState:
    prompt = f"""You are a MySQL 8 read-only SQL generation system.

Convert the user's natural-language question into exactly one SQL query.

Requirements:
- Return only one SQL SELECT query, optionally using WITH and CTEs.
- Use only the tables and columns listed in the schema below.
- Do not return explanations, Markdown fences, or comments.
- Never generate INSERT, UPDATE, DELETE, REPLACE, DDL, stored procedures,
  multiple statements, file operations, or locking queries.
- Use explicit column names where practical.
- Use JOINs when the question requires related tables.
- For list queries, limit results to at most 100 rows.
- Do not invent table names, column names, or data values.
- Match status values using the values supported by the schema and question.
- If the question cannot be answered using this schema, return:
  SELECT 'INSUFFICIENT_SCHEMA' AS error

DATABASE SCHEMA:
{state['schema']}

USER QUESTION:
{state['question']}

SQL:
"""

    last_error = None

    for attempt in range(2):
        generated_sql = gemini_text(prompt)
        sql = _extract_sql(generated_sql)

        try:
            rows = execute_readonly_query(sql, max_rows=200)

            return {
                "sql": sql.rstrip(";"),
                "sql_rows": rows,
            }

        except ValueError as exc:
            last_error = exc

            if attempt == 0:
                print(
                    "[SQL VALIDATION] Generated query was rejected. "
                    "Requesting a corrected query."
                )
                prompt += (
                    "\nThe previous query was rejected by the SQL validator. "
                    f"Validation error: {exc}\n"
                    "Generate a corrected query that follows every requirement."
                )
                continue

            raise RuntimeError(
                f"Generated SQL did not pass read-only validation: {exc}"
            ) from exc

    raise RuntimeError(f"Unable to generate valid SQL: {last_error}")


def _format_value(value: Any) -> str:
    if value is None:
        return "NULL"

    value_text = str(value)
    value_text = value_text.replace("\r", " ").replace("\n", " ")

    if len(value_text) > 500:
        value_text = value_text[:497] + "..."

    return value_text.replace("|", "\\|")


def _format_sql_results(rows: list[dict]) -> str:
    if not rows:
        return "No matching records were found."

    columns = list(rows[0].keys())

    if not columns:
        return f"The query returned {len(rows)} record(s)."

    lines = [
        f"Query returned {len(rows)} record(s).",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]

    for row in rows:
        lines.append(
            "| " + " | ".join(
                _format_value(row.get(column))
                for column in columns
            ) + " |"
        )

    return "\n".join(lines)


def answer_node(state: AssistantState) -> AssistantState:
    route = state.get("route")
    sql_rows = state.get("sql_rows")

    if route == "sql" and sql_rows is not None:
        answer = _format_sql_results(sql_rows)

        return {
            "answer": answer,
            "evidence": str(sql_rows),
        }

    evidence_parts = []

    for item in state.get("doc_hits", []):
        evidence_parts.append(
            f"Source: {item['path'].relative_to(BASE_DIR)}\n"
            f"Title: {item['metadata'].get('title', '')}\n"
            f"{item['body']}"
        )

    if evidence_parts:
        evidence_parts.insert(0, "DOCUMENT EVIDENCE:")

    if sql_rows is not None:
        evidence_parts.append(
            f"MYSQL QUERY:\n{state.get('sql', '')}\n\n"
            f"MYSQL RESULTS:\n{sql_rows}"
        )

    if not evidence_parts:
        evidence_parts.append("No evidence was retrieved.")

    evidence = "\n\n---\n\n".join(evidence_parts)

    prompt = f"""You are a careful knowledge assistant.

Answer the user's question using only the supplied evidence.
Do not invent database records or policy details.
Cite document source paths when using document evidence.
Explain SQL results clearly and mention if results may be limited.
If evidence is insufficient, clearly state what is missing.

USER QUESTION:
{state['question']}

SELECTED ROUTE:
{route}

EVIDENCE:
{evidence}

ANSWER:
"""

    return {
        "answer": gemini_text(prompt),
        "evidence": evidence,
    }


def build_graph():
    graph = StateGraph(AssistantState)

    graph.add_node("route", route_node)
    graph.add_node("documents", document_node)
    graph.add_node("sql", sql_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "route")

    graph.add_conditional_edges(
        "route",
        lambda state: state["route"],
        {
            "documents": "documents",
            "sql": "sql",
            "both": "documents",
        },
    )

    graph.add_conditional_edges(
        "documents",
        lambda state: "sql" if state.get("route") == "both" else "answer",
        {
            "sql": "sql",
            "answer": "answer",
        },
    )

    graph.add_edge("sql", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


_graph = None


def answer_question(question: str) -> dict[str, Any]:
    global _graph

    question = question.strip()

    if not question:
        raise ValueError("Please enter a question.")

    start_time = time.perf_counter()

    if _graph is None:
        print("[TIMING] Compiling LangGraph for the first time.")
        _graph = build_graph()

    result = _graph.invoke({"question": question})

    print(
        "[TIMING] Total graph execution time: "
        f"{time.perf_counter() - start_time:.2f} seconds."
    )

    return {
        "answer": result.get("answer", "No answer generated."),
        "route": result.get("route"),
        "route_note": result.get("route_note"),
        "document_sources": [
            str(item["path"].relative_to(BASE_DIR))
            for item in result.get("doc_hits", [])
        ],
        "sql": result.get("sql"),
        "sql_rows": result.get("sql_rows"),
    }
