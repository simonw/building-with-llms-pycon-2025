# Prompting from Python

LLM is also [a Python library](https://llm.datasette.io/en/latest/python-api.html). Let's run a prompt from Python:

```python
import llm
model = llm.get_model("gpt-4.1-mini")
response = model.prompt(
    "A joke about a walrus who lost his shoes"
)
print(response.text())
```
LLM defaults to picking up keys you have already configured. You can pass an explicit API key using the `key=` argument like this:

```python
response = model.prompt("Say hi", key="sk-...")
```

## Streaming

You can stream responses in Python like this:

```python
for chunk in model.prompt(
    "A joke about a pelican who rides a bicycle",
    stream=True
):
    print(chunk, end="", flush=True)
```

## Using attachments

Use `llm.Attachment` to attach files to your prompt:

```python
response = model.prompt(
    "Describe this image",
    attachments=[
        llm.Attachment(
            url="https://static.simonwillison.net/static/2025/two-pelicans.jpg",
        )
    ]
)
print(response.text())
```
## Using system prompts

System prompts become particularly important once you start building applications on top of LLMs.

Let's write a function to translate English to Spanish:

```python
def translate_to_spanish(text):
    model = llm.get_model("gpt-4.1-mini")
    response = model.prompt(
        text,
        system="Translate this to Spanish"
    )
    return response.text()

# And try it out:
print(translate_to_spanish("What is the best thing about a pelican?"))
```

We're writing software with LLMs!

## Async support

LLM offers [async support](https://llm.datasette.io/en/latest/python-api.html#async-models) as well. We won't discuss that in detail here, but this is a quick taster:

```python
import asyncio
import llm

model = llm.get_async_model("gpt-4.1-mini")
async def main():
    response = model.prompt(
        "A joke about a walrus who lost his shoes"
    )
    async for chunk in response:
        print(chunk, end="", flush=True)
    # Or just print(await response.text())

asyncio.run(main())
```
