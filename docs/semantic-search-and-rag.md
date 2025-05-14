# Semantic search and RAG

One of the most popular applications of LLMs is to build "ask questions of my own documents" systems.

You do **not** need to fine-tune a model for this. Instead, you can use a pattern called **retrieval-augmented generation** (RAG).

The key trick to RAG is simple: try to figure out the most relevant documents for the user's question and *stuff as many of them as possible into the prompt*.

Long context models make this even more effective. "Reasoning" models may actually be *less* effective here.

## Semantic search

If somebody asks "can my pup eat brassicas", how can we ensure we pull in documents that talk about dogs eating sprouts?

One solution is to build **semantic search** on top of **vector embeddings**.

I wrote about those in [Embeddings: What they are and why they matter](https://simonwillison.net/2023/Oct/23/embeddings/).

## Generating embeddings with LLM

LLM includes [a suite of tools](https://llm.datasette.io/en/latest/embeddings/index.html) for working with embeddings, plus various plugins that add new embedding models.

We'll start with the OpenAI hosted embedding model.

```bash
llm embed -m text-embedding-3-small-512 -c "can my pup eat brassicas?"
```
This returns a 256 long vector of floats.

More useful is if we store some information first. Let's embed all the PEPs that start with a `3`:
```bash
git clone https://github.com/python/peps
cd peps

llm embed-multi peps \
  -m text-embedding-3-small-512 \
  --files peps 'pep-3*.rst' \
  -d peps.db \
  --store
```
There's a lot going on there. We're using the 512 long `text-embedding-3-small-512` model, saving embeddings to a `peps.db` SQLite database in a `peps` collection, scanning for `peps/pep-3*.rst` files. and storing the full documents along with their vectors.

I tried this... and it failed, because the documents were too long. Let's create truncated documents first, like this:

```bash
llm install llm-cmd

llm cmd create a new folder peps-truncated which has every .rst file from peps/ in it but truncated to first 8000 characters
```
Which ran
```bash
mkdir -p peps-truncated && find peps/ -name '*.rst' -exec sh -c 'head -c 8000 "$1" > "peps-truncated/$(basename "$1")"' _ {} \;
```
Then I ran this:
```bash
llm embed-multi peps \
  -m text-embedding-3-small-512 \
  --files peps-truncated 'pep-3*.rst' \
  -d peps.db \
  --store
```
Confirmed with:
```bash
llm collections -d peps.db
```
And now we can search that collection for items similar to a term using:
```bash
llm similar -c 'string concatenation' -d peps.db peps | jq
```
Here's a SQLite database with ALL of the PEPs, so that our workshop doesn't burn through my API credits with everyone embedding the same data!

[https://static.simonwillison.net/static/2025/peps.db](https://static.simonwillison.net/static/2025/peps.db) (6MB)

## Answering questions against those PEPs

This time we'll build a bash script:

```bash
llm '
Build me a bash script like this:

./pep-qa.sh "What do string templates look like?"

It should first run:

llm similar -c $question -d peps.db peps

Then it should pipe the output from that to:

llm -s "Answer the question: $question" -m gpt-4.1-mini

That last command should run so the output is visible as it runs.
' -x > pep-qa.sh

chmod +x pep-qa.sh
./pep-qa.sh "What do string templates look like?"
```
I [got this](https://gist.github.com/simonw/d51086c71515d00130d076e97f2234be).

(Running code that an LLM has generated without first reviewing it generally a *terrible* idea!)

If you want to port the above to Python you should consult the [Working with collections](https://llm.datasette.io/en/latest/embeddings/python-api.html#working-with-collections) section of LLM's Python API documentation.

## RAG does not have to use semantic search!

Many people associate RAG with embedding-based semantic search, but it's not actually a requirement for the pattern.

A lot of the most successful RAG systems out there use traditional keyword search instead. Models are very good at taking a user's question and turning it into one or more search queries.

Don't get hung up on embeddings!

## RAG is dead?

Every time a new long-context model comes out, someone will declare the death of RAG.

I think classic RAG is dead for a different reason: it turns out arming an LLM with search tools is a much better way to achieve the same goal.

Which brings us to our next topic: {ref}`tools`.