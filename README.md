# langchain-webscraper-demo

This is a small demo project illustrating how to create a chatbot that can query a scraped website. It uses LangChain to manage the chatbot's framework, Gradio for a user friendly interface, OpenAI's `gpt-3.5-turbo` LLM model, and ChromaDB for as a vector store. 

This project accompanies a blog post on my website, and can be read here.

## Getting started

This project supports both `pip` and `pipenv`. I recommend using `pipenv` for the best (and least error prone) experience.

### Installation

#### Pip
Run 

```bash
pip install -r requirements.txt
```

if using `pip`.

#### Pipenv

Run

```bash
pipenv install
```

if using `pipenv`, followed by `pipenv shell` to start a shell with the installed packages.

### Environment variables

You need to create a new `.env` file from the `.env.example` file with your `OPENAI_API_KEY`. You can create one of these on OpenAI's [platform](https://platform.openai.com/account/api-keys). This will require an OpenAI developer account.

### Web scraping

To scrape a site, run 

```
python scrape.py --site <site_url> --depth <int>
```

This will scrape a url and all links found at that url recursively up to the specified `depth`. This will only scrape sites with the same origin as the given `<site_url>`, so for example scraping `https://python.langchain.com/docs` will only scrape sites at `https://python.langchain.com`.

The data will be stored in a new `scrape/` directory.

### Data embeddings

To generate and persist the embeddings and create a vector store, run

```bash
python embed.py
```

A new persisted vector store will be created in the `chroma/` directory.

### Launching the chatbot

To launch the chatbot, you can run

```bash
python main.py
```

This will start a Gradio server at http://127.0.0.1:7860, allowing you to chat to the scraped website and data store.

NOTE: you must both first scrape a site and persist a vector store in order for this to work.