# Prompting with LLM

Let's start by running some prompts using the LLM command-line interface.

## Setting a default model

LLM defaults to [gpt-4o-mini](https://platform.openai.com/docs/models/gpt-4o-mini). A month ago OpenAI [released the GPT-4.1 series](https://openai.com/index/gpt-4-1/). They're a big step up from GPT-4o - in particular, they have a one million token context window which means you can feed them a *lot* more data (gpt-4o-mini was limited to 128,000 tokens).

Let's switch to [gpt-4.1-mini](https://platform.openai.com/docs/models/gpt-4.1-mini) as our new default model:

```bash
llm models default gpt-4.1-mini
```

## Running a prompt

The LLM command-line tool takes a prompt as its first argument:

```bash
llm 'Ten pun names for a teashop run by a pelican and a walrus'
```

## What did that do for us?

Let's run a prompt the manual way, using `curl` and the OpenAI API:

```bash
curl https://api.openai.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $(llm keys get openai)" \
  -d '{
    "model": "gpt-4.1-mini",
    "messages": [
      {"role": "user", "content": "Ten pun names for a teashop run by a pelican and a walrus"}
    ]
  }'
```
Now try that again with `"stream": true` to see what the streaming response looks like:

```bash
curl https://api.openai.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $(llm keys get openai)" \
  -d '{
    "model": "gpt-4.1-mini",
    "stream": true,
    "messages": [
      {"role": "user", "content": "Ten pun names for a teashop run by a pelican and a walrus"}
    ]
  }'
```

Every API provider has a similar, albeit slightly different, way of doing this. LLM and its plugins provide wrappers around those APIs so you don't need to think about those differences.

## Continuing the conversation

The `llm -c` flag stands for `--continue` - it lets you continue the most previous conversation:

```bash
llm -c 'Three more with darker overtones'
```

## Seeing it in the logs

LLM logs every prompt and response to a SQLite database. You can see the location of that database by running:

```bash
llm logs path
```
The `llm logs` command shows logged conversations. Use `-c` for the most recent conversation:

```bash
llm logs -c
```
The output looks something like this:
```
# 2025-05-14T13:54:58    conversation: 01jv7h7jcf20b4hbg3jnh57syh id: 01jv7h7ens68awxrk17p2pq356

Model: **gpt-4.1-mini**

## Prompt

Ten pun names for a teashop run by a pelican and a walrus

## Response

Sure! Here are ten punny teashop name ideas featuring a pelican and a walrus:

1. **The Pelitea & Wally Brew**  
2. **Beak & Tusks Tea House**  
...
```
As you can see, the output is in Markdown format. I frequently share my conversation logs by pasting that into a [GitHub Gist](https://gist.github.com).

Add the `-u` (short for `--usage`) flag to see how many tokens were used in the conversation:

```bash
llm logs -c -u
```

You can also get output in JSON using the `--json` flag:

```bash
llm logs -c --json
```
Every conversation has an ID. If you know the ID of a conversation you can retrieve its logs using `--cid ID`.

```bash
llm logs --cid 01jv7h7jcf20b4hbg3jnh57syh
```
The `-s` option stands for `--short` and provides a more compact view, useful for finding conversation IDs:

```bash
llm logs -s
```
Add `-q` to search:

```bash
llm logs -s -q 'pelican'
```
And `-n 0` to see **every** match:

```bash
llm logs -s -q 'pelican' -n 0
```

## Browsing the logs with Datasette

[Datasette](https://datasette.io/) is my open source tool for exploring SQLite databases. Since LLM logs to SQLite you can explore that database in your web browser using Datasette like this:

```bash
datasette "$(llm logs path)"
```
This will start a local web server which you can visit at `https://localhost:8001/`

On Codespaces you should first run this command to install a plugin to make Datasette work better in that environment:

```bash
datasette install datasette-codespaces
# Then
datasette "$(llm logs path)"
```
## Using different models

Use the `-m` option to specify a different model. You can see a list of available models by running:

```bash
llm models list
```
Add the `--options` flag to learn more about them, including what options they support and what capabilities they hav:
```bash
llm models list --options
```
Let's get some pun names for a teashop from the more powerful `o4-mini`:

```bash
llm 'Ten pun names for a teashop run by a pelican and a walrus' -m o4-mini
```
[o4-mini](https://platform.openai.com/docs/models/o4-mini) is a reasoning model, so there's a delay at the start while it "thinks" about the problem.


## Piping in content

The best thing about having a command-line tool for interacting with models is you can pipe things in!

## Using system prompts

A **system prompt** is a special kind of prompt that has higher weight than the rest of the prompt. It's useful for providing instructions about *what to do* with the rest of the input.
```bash
cat requirements.txt | llm -s 'convert this to pyproject.toml'
```

## Prompting with an image

LLM supports **attachments**, which are files that you can attach to a prompt. Attachments can be specified as filepaths or as URLs.

Let's describe a photograph:

```bash
llm -a https://static.simonwillison.net/static/2025/two-pelicans.jpg 'Describe this image' -u
```
That `-u` causes the token usage to be displayed. You can paste that token line into https://www.llm-prices.com/ and select the model to get a price estimate.

## Using fragments

The `-f` option can be used to specify a **fragment** - an extra snippet of text to be added to the prompt. Like attachments, these can be filepaths or URLs.

Fragments are mainly useful as a storage optimization: the same fragment will be stored just once in the database no matter how many prompts you use it with.

Here's our `requirements.txt` example again, this time with a fragment:

```bash
llm -f requirements.txt 'convert this to pyproject.toml'
```
The `-e` option can be used with `llm logs` to expand any fragments:

```bash
llm logs -c -e
```

## Fragment plugins

The most exciting thing about fragments is that they can be customized with **plugins**.

Install the [llm-fragments-github](https://github.com/simonw/llm-fragments-github) plugin like this:

```bash
llm install llm-fragments-github
```
This adds several new fragment types, including `github:` which can be used to fetch the full contents of a repository and `issue:` which can load an issue thread.

```bash
llm -f issue:https://github.com/simonw/llm/issues/898 -s 'summarize this issue'
```
Or let's suggest some new features for that plugin:

```bash
llm -f github:simonw/llm-fragments-github -s 'Suggest new features for this plugin' -u
```

This is a good point for a digression to talk about **long context** and why it's such an important trend.

