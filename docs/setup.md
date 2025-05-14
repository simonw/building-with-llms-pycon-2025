# Setup

If you are using Codespaces, go and create one here:

[https://github.com/pamelafox/python-3.13-playground](https://github.com/pamelafox/python-3.13-playground)

It can take a few minutes to start the first time, so click the button now!

If you're not using Codespaces you'll need a Python 3.9+ environment that you can install packages into. You'll likely want a virtual environment to avoid conflicts with other projects.

## Installing the packages

```bash
git clone https://github.com/simonw/building-with-llms-pycon-2025

# Optional if you want a virtual environment (no need to do this on Codespaces):
python -m venv venv
source venv/bin/activate

# Install the project requirements
pip install -r requirements.txt
```

Run this command to see if the packages installed correctly:

```bash
llm --version
```
You should see this:
```
llm, version 0.26a0
```

## Configuring the OpenAI API key

You'll need an OpenAI API key for this workshop. You can either get your own here:

[https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

Or you can use a shared one I created for the workshop. You'll need the password that is distributed in the workshop:

**[Get the workshop API key (password required)](https://tools.simonwillison.net/encrypt#s4zfXxKzT7Qy6dYfQYIq5w0VvGeOLnvuOn3+MM9pHUuMyvwCLhNo6i/q4tqUVYhPQA1kVO55c1QUqn/8jZpMR1IOoOJphKbbjtVD82gIGekmisiYNa4UVNPt88cKddI+zK3TBljHOjTwIqPxQSvWkgRJGETORa26d6d1NahdcKUeUmHuTrjNciqgt9iowD1zkAIejsBq84+A0aRrxWLEfMWfi2lhiW3Rd0hJu0lJpuV3AVR3K/PuywlrGhx91Ns8hmWpQ/ImSXKkAcIUY4/ZjNWY/g==)**

This shared key is restricted to the following models: `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-nano`, `gpt-4.1-mini`, `o4-mini`.

Key obtained, you can configure it for LLM like this:

```bash
llm keys set openai
# Paste your key here
```

## Testing that it worked

Test that the keys works like this:
```bash
llm 'five fun facts about pelicans'

The key will be saved to a JSON file. You can see the location of that file by running:
```bash
llm keys path
```

A useful trick is that `llm keys get openai` will print the key out again. You can use this pattern to use that key with other tools that require an environment variable:

```bash
export OPENAI_API_KEY="$(llm keys get openai)"
```