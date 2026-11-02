
import time

from app.db import test_connection
from app.graph import answer_question


def main():
    print("\nUnified Knowledge Assistant — LangGraph + OKF documents + MySQL")
    print("Type 'exit' to quit. The app uses the separate uka_demo database by default.\n")

    try:
        details = test_connection()
        print(
            f"Connected to database: {details['database_name']} "
            f"(MySQL {details['mysql_version']})"
        )
    except Exception as exc:
        print(f"Database connection failed: {exc}")
        print("Check .env and follow README.md before asking questions.\n")
        return

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            start_time = time.perf_counter()
            print("\nProcessing your question...")

            result = answer_question(question)

            elapsed = time.perf_counter() - start_time

            print(f"\nRoute: {result['route']} — {result['route_note']}")
            print(f"\nAssistant: {result['answer']}")
            print(f"\nProcessing time: {elapsed:.2f} seconds")

            if result.get("document_sources"):
                print("\nDocument sources:")
                for source in result["document_sources"]:
                    print(f" - {source}")

            if result.get("sql"):
                print(f"\nGenerated read-only SQL: {result['sql']}")

        except Exception as exc:
            print(f"\nCould not answer this question: {exc}")
            print("Check GEMINI_API_KEY, MySQL connection, and the demo database seed.")


if __name__ == "__main__":
    main()
