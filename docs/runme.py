import argparse
from pathlib import Path

import sqlite_utils
import llm

# pick your model
model = llm.get_model("gpt-4.1-mini")

def text_to_sql(db: sqlite_utils.Database, question: str) -> str:
    """Convert an English question into a SQLite SQL statement."""
    prompt = "Schema:\n\n{}\n\nQuestion:\n\n{}".format(db.schema, question)
    resp = model.prompt(
        prompt,
        system="reply with SQLite SQL, not in markdown, just the SQL",
    )
    return resp.text().strip()

def main():
    parser = argparse.ArgumentParser(
        description="Turn a natural-language question into SQL (and optionally run it)."
    )
    parser.add_argument(
        "question",
        help="The question to ask of your SQLite database, in plain English.",
    )
    parser.add_argument(
        "--db",
        "-d",
        default=str(llm.user_dir() / "logs.db"),
        help="Path to the SQLite database file.  [default: %(default)s]",
    )
    parser.add_argument(
        "--execute",
        "-x",
        action="store_true",
        help="Execute the generated SQL and print the results instead of just showing the SQL.",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        parser.error(f"Database file not found: {db_path!r}")

    db = sqlite_utils.Database(db_path)
    sql = text_to_sql(db, args.question)

    if args.execute:
        try:
            rows = list(db.query(sql))
        except Exception as e:
            print("ERROR running SQL:", e)
            print("SQL was:", sql)
            raise SystemExit(1)
        # print rows as simple CSV
        for row in rows:
            print(row)
    else:
        print(sql)

if __name__ == "__main__":
    main()
