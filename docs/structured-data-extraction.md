# Structured data extraction

One of the most clearly valuable applications of LLMs is for **structured data extraction** - turning unstructured text (and images and PDFs and even video or audio) into structured data.

They are *really good at this*.

Many models allow you to specify a JSON schema that should be used to control their output. LLM calls this [schemas](https://llm.datasette.io/en/latest/schemas.html).

## Using simple schemas

You can define a schema as a JSON schema, but that's pretty verbose and hard to type. LLM has its own mini-DSL for creating simple schemas.

Let's invent a cool pelican:
```bash
llm --schema 'name, age int, one_sentence_bio' 'invent a cool pelican'
```

I got back this:
```json
{
    "name": "Zephyr the Pelican",
    "age": 5,
    "one_sentence_bio": "Zephyr is a sleek silver-feathered pelican with an iridescent blue beak who gracefully soars the skies, known for his clever fishing techniques and playful spirit."
}
```
Pass `--schema-multi` to get back a JSON array of objects:
```bash
llm --schema-multi 'name, age int, one_sentence_bio' 'invent 3 cool pelicans'
```
You can retrieve just the data from `llm logs` using `--data` like this:
```bash
llm logs -c --data
```
I often pipe it through `jq`:
```bash
llm logs -c --data | jq
```
## Something a bit more impressive

FEMA's [Daily Operation Briefing PDF](https://www.disastercenter.com/FEMA%20Daily%20Operation%20Brief.pdf) is a *fascinating* document.

Let's extract the "Declaration Requests" from it:
```bash
llm \
  -a https://www.disastercenter.com/FEMA%20Daily%20Operation%20Brief.pdf \
  --schema-multi '
state_or_tribe_or_territory
incident_description
incident_type
IA bool
PA bool
HM bool
requested str: YYYY-MM-DD, current year is 2025' \
  -s 'extract all the declaration requests'
```
Here we're using the multi-line format of the schema DSL, and including both type information (the `bool` notes) and hints following a `:` for one of the fields.

Pretty-print it like this:

```bash
llm logs -c --data | jq
```
Crucially, **did it get everything right?** We used a very inexpensive model for this. Spot-checking is crucial. We may find we need to upgrade to something a little more expensive to get better results.

My favorite models for this kind of thing are Google's Gemini series. They can handle video and audio in addition to images and PDFs!

## Structured data extraction in Python with Pydantic

When using LLM as a Python library you can set `schema=` to a Pydantic model class.

```python
import llm, json
from pydantic import BaseModel

class Pelican(BaseModel):
    name: str
    age: int
    short_bio: str
    beak_capacity_ml: float

model = llm.get_model("gpt-4o-mini")
response = model.prompt("Describe a spectacular pelican", schema=Pelican)
pelican = json.loads(response.text())
print(pelican)
```
