# Building a text to SQL tool

We're going to build something *genuinely useful*. Weirdly enough, this is a "hello world" exercise for prompt engineering.

Ask a question of your database in English, get a response from a custom SQL query written by the LLM.

## Prototyping against the logs database

We're going to use the LLM logs database itself, and prototype against it using the `sqlite-utils` CLI tool:

```bash
sqlite-utils schema "$(llm logs path)"
```
Let's write that to a file:

```bash
sqlite-utils schema "$(llm logs path)" > schema.sql
```

Now we can feed it to LLM and write our first query:

```bash
llm -f schema.sql \
  -s "reply with sqlite SQL" \
  "how many conversations are there?"
```

I got back this:

````
```sql
SELECT COUNT(*) AS conversation_count FROM conversations;
```
````
As you can see, the LLM decided to wrap it in a fenced code block.

We could ask it not to, but we can also use the `--extract` flag to extract the SQL from the response:

```bash
llm -f schema.sql \
  -s "reply with sqlite SQL" \
  --extract \
  "how many conversations are there?"
```
Let's run that query in the most diabolical way possible:

```bash
sqlite-utils "$(llm logs path)" "$(llm -f schema.sql \
  -s 'reply with sqlite SQL' \
  --extract \
  'how many conversations are there?')"
```

## Turning that into a Python function

Let's upgrade our hacky CLI prototype into a Python function.

```python
import sqlite_utils
import llm

model = llm.get_model("gpt-4.1-mini")

def text_to_sql(db: sqlite_utils.Database, question: str) -> str:
    """Convert a prompt to SQL using the LLM."""
    prompt = "Schema:\n\n{}\n\nQuestion:\n\n{}".format(
        db.schema, question
    )
    return model.prompt(
        prompt,
        system="reply with SQLite SQL, not in markdown, just the SQL",
    ).text()

db = sqlite_utils.Database(llm.user_dir() / "logs.db")

sql = text_to_sql(db, "how many conversations are there?")

print(sql)

# Now execute it
result = db.query(sql)
print(list(result))
```

## Upgrading that to a CLI tool

Now that we have this working, let's turn it into a small CLI tool using `argparse` from the Python standard library:

```python
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
```

Here's a fun note: the above block just said "FILL ME" and then I ran this command:

```bash
llm -m o4-mini -f text-to-sql.md -s 'Write the code for the FILL ME bit'
```

## Ways to make this better

This is the most basic version of this, but it works pretty well!

Some ways we could make this better:

- **Examples**. The single most powerful prompt engineering trick is to give the LLM illustrative examples of what you are trying to achieve. A small number of carefully selected examples of questions and the expected SQL answer can radically improve the results.
- **Column values**. A common failure case for text to SQL is when the question is e.g. "How many schools are in California?" and the model queries for `where state = 'California'` when it should have queried for `where state = 'CA'`. Feeding in some example value from each column can be all the model needs to get it right.
- **Data documentation**. Just like a real data analyst, the more information you can feed the model the better.
- **Loop on errors**. If the SQL query fails to run, feed the error back to the LLM and have it try again. You can use `EXPLAIN ...` for a cheap validation of the query without running the whole thing.
