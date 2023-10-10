import os
import json
import chardet  # Importing chardet for encoding detection
import logging  # Importing logging for error logging

from langchain.document_loaders import (
    BSHTMLLoader,
    DirectoryLoader,
)

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from dotenv import load_dotenv
from bs4 import BeautifulSoup  # Importing BeautifulSoup

# Setup logging
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_file_content(file_path):
    with open(file_path, "rb") as f:  # Reading as bytes
        byte_content = f.read()
        # Detect encoding
        encoding = chardet.detect(byte_content)["encoding"]
        # Decode using detected encoding
        content = byte_content.decode(encoding or "utf-8", errors="replace")
    return content

# Custom BSHTMLLoader to handle different encodings
class CustomBSHTMLLoader(BSHTMLLoader):
    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)  # Calling the parent class's initializer
        self.path = path  # Storing path as an instance attribute

    def _extract_text(self, soup):
        return soup.get_text(separator=' ', strip=True)

    
    def load(self):
        content = load_file_content(self.path)
        soup = BeautifulSoup(content, **self.bs_kwargs)
        return self._extract_text(soup)


if __name__ == "__main__":
    load_dotenv()
    if os.path.exists("./chroma"):
        print("already embedded")
        exit(0)

    loader = DirectoryLoader(
        "./scrape",
        glob="*.html",
        loader_cls=CustomBSHTMLLoader,  # Using the custom loader
        show_progress=True,
        loader_kwargs={"get_text_separator": " "}
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    data = loader.load()
    documents = text_splitter.split_documents(data)

    # map sources from file directory to web source
    with open("./scrape/sitemap.json", "r") as f:
        sitemap = json.loads(f.read())

    for document in documents:
        document.metadata["source"] = sitemap[
            document.metadata["source"].replace(".html", "").replace("scrape/", "")
        ]

    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    db = Chroma.from_documents(documents, embedding_model, persist_directory="./chroma")
    db.persist()
