(tools)=

# Tool usage

This feature of LLM is *so new* that I haven't even formally announced it yet. I got the alpha together just in time for the conference.

LLM systems can be expanded by giving them the ability to **execute tools**.

Ever heard the complaints about how LLMs are computers that can'd do math, and language tools that can't count the number of Rs in the word strawberry?

Tools can solve those problems, and so many more.

LLM can treat any Python function as a tool. It can grant tool access to a range of models - currently models from OpenAI, Anthropic and Gemini are supported by their relevant alpha plugins.

## Passing Python functions to an LLM

Let's solve the hardest problem in LLMs:

```bash
llm --functions '
def count_char_in_string(char: str, string: str) -> int:
    """Count the number of times a character appears in a string."""
    return string.lower().count(char.lower())
' 'Count the number of Rs in the word strawberry' --td
```
The `--td` stands for `--tools-debug` - it shows you what's going on.

Use `--ta/--tools-approve` to manually approve every tool call.

Run `llm logs -c` to see how tool calls are logged.

## Multiple tools can run in a row

Here's a simple example of that:
```bash
llm --functions '
def lookup_population(country: str) -> int:
    "Returns the current population of the specified fictional country"
    return 123124
def can_have_dragons(population: int) -> bool:
    "Returns True if the specified population can have dragons, False otherwise"
    return population > 10000
' 'Can the country of Crumpet have dragons?' --td
```

## Tools in Python

In Python code  an array of functions can be passed to the `tools=` argument of the `chain` method of a model:

```python
model = llm.get_model("gpt-4.1-mini")

def lookup_population(country: str) -> int:
    "Returns the current population of the specified fictional country"
    return 123124

def can_have_dragons(population: int) -> bool:
    "Returns True if the specified population can have dragons, False otherwise"
    return population > 10000

chain_response = model.chain(
    "Can the country of Crumpet have dragons? Answer with only YES or NO",
    tools=[lookup_population, can_have_dragons],
    stream=False,
    key=API_KEY,
)
print(chain_response.text())
```
The `chain()` method handles running multiple prompts in a row to pass the tool results on to th e next prompt.


## Running calculations with simpleeval

We can do mathematics using [danthedeckie/simpleeval](https://github.com/danthedeckie/simpleeval):

```bash
llm install simpleeval # Puts it in the right environment
llm --functions 'from simpleeval import simple_eval' \
  'Calculate 42342 * 21123' --td
```

## Let's build some tools!

Open exercise: who can come up with the most interesting tool?

`httpx` is already available in LLM's environment.

## Chat with your database, implemented using tools

```bash
llm -f prompting.md -f text-to-sql.md -f tools.md -m o4-mini -o reasoning_effort high -s 'Based on this documentation implement a short Python script for the "chat with your database" example, it should take input from the user a line at a time and execute a new execute_sql() tool to try and answer their questions, displaying the results as pretty-printed JSON to them'
```
[Here's the transcript](https://gist.github.com/simonw/b0bacce9b495b81921c25c2581507f54), and the [chat_with_db.py script](https://gist.github.com/simonw/cc303e503baa8ae263ad5e0c11750c25) it wrote.

It's not quite right but amazingly it does kind-of-work!
