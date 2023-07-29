import argparse

from dotenv import load_dotenv

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import (
    RetrievalQA,
)
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import (
    Tool,
    ZeroShotAgent,
    AgentExecutor,
)
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

import gradio

load_dotenv()

db = Chroma(
    persist_directory="./chroma",
    embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
)
print(db.similarity_search("What is lang chain?")[0])
llm = OpenAI(temperature=0)
webscrape_qa = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", retriever=db.as_retriever()
)

tools = [
    Tool(
        name="LangChain API QA System",
        func=webscrape_qa.run,
        description="useful for when you need to answer questions about the LangChain API documentation. Input should be a fully formed question. You should always attempt to query this first.",
    )
]

memory = ConversationBufferMemory(memory_key="chat_history")

prefix = """You are an agent assisting a human with queries about the LangChain API. The LangChain API is a python based framework for developing applications powered by large language models. You have access to the following tools:"""
suffix = """Begin!

Chat history: {chat_history}
Question: {input}
{agent_scratchpad}"""
prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)

llm_chain = LLMChain(
    llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0), prompt=prompt
)

agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True, memory=memory
)


def predict(message, history):
    response = agent_chain(message)
    print(response)
    return response["output"]


gradio.ChatInterface(predict).launch()
