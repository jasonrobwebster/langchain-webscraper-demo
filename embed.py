import os
import argparse
from langchain.document_loaders import (
    BSHTMLLoader,
    DirectoryLoader,
    UnstructuredHTMLLoader,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.vectorstores import Chroma

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    if os.path.exists("./chroma"):
        print("already embedded")
        exit(0)

    loader = DirectoryLoader(
        "./scrape",
        glob="*.html",
        loader_cls=BSHTMLLoader,
        show_progress=True,
        loader_kwargs={"get_text_separator": " "},
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    data = loader.load()
    documents = text_splitter.split_documents(data)
    print(len(documents))
    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    db = Chroma.from_documents(documents, embedding_model, persist_directory="./chroma")
    db.persist()
