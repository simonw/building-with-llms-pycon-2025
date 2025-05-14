#!/usr/bin/env python3
import json
import sqlite_utils
import llm
from pathlib import Path

def main():
    # 1. locate the SQLite DB
    db_path = Path(llm.user_dir()) / "logs.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path!r}")
    db = sqlite_utils.Database(db_path)

    # 2. pick your model
    model = llm.get_model("gpt-4.1-mini")

    # 3. wrap execute_sql into a tool the LLM can call
    def execute_sql(sql: str):
        """
        Tool for the LLM: run arbitrary SQL against our SQLite DB
        and return the rows as a list of dicts.
        """
        try:
            return list(db.query(sql))
        except Exception as e:
            return {"error": str(e)}

    # 4. Prepare a system prompt with the schema
    system_prompt = f"""You are a helpful assistant for a SQLite database.
Here is the schema of the database you have access to:

{db.schema}

When given a user question, think about the SQL you need,
then call the execute_sql(sql: str) tool with exactly that SQL.
Finally return only the JSON result of that tool call (no markdown)."""

    print(f"Connected to {db_path}")
    print("ASK A QUESTION (Ctrl-D to exit)")
    while True:
        try:
            question = input(">> ").strip()
        except EOFError:
            print("\nGoodbye.")
            break
        if not question:
            continue

        # 5. call the model with our tool
        chain_response = model.chain(
            question,
            system=system_prompt,
            tools=[execute_sql],
            stream=False
        )

        # 6. drill into the tool call result if we can
        result = None
        if hasattr(chain_response, "tool_calls") and chain_response.tool_calls:
            # take the last tool result
            result = chain_response.tool_calls[-1].result
        else:
            # fallback: try parsing the raw assistant text as JSON
            text = chain_response.text().strip()
            try:
                result = json.loads(text)
            except Exception:
                # last resort: just show whatever the assistant said
                print(text)
                continue

        # 7. pretty-print JSON
        print(json.dumps(result, indent=2, default=str))
        print()

if __name__ == "__main__":
    main()

