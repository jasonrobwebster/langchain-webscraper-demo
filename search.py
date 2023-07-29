import argparse
import os

from dotenv import load_dotenv

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("search_string", type=str)

if __name__ == "__main__":
    if not os.path.exists("./chroma"):
        print("No chroma persisted, run `python embed.py` to create one")
        exit(0)
    args = parser.parse_args()
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    db = Chroma(persist_directory="./chroma", embedding_function=embeddings)
    docs = db.similarity_search(args.search_string)
    for doc in docs[0:5]:
        print(doc)
        print("\n")
