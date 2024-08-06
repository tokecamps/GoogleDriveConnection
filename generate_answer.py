import os
from glob import glob
# import subprocess
import streamlit as st
import openai
# from openai import OpenAI
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory


load_dotenv()

try:
    api_key = os.getenv("OPENAI_API_KEY")
except:
    os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"]

openai.api_key = api_key

def base_model_chatbot():

    prompt_template = """
        You are an assistant that helps a human to write a proposal from the input given by the human. 
        You will output the following:
        First, you give a short summary, that can function as a case description. 
        Second, you state which actions should be taken. 
        Last, you state which oustanding questions there still are. 

        Ask for more information when you feel like you cannot extract the information needed to output the above, 
        but be specific in what you need.

        {chat_history}

        Human: {input}
        Chatbot:

        """

    prompt = PromptTemplate(
        input_variables=["chat_history", "input"], template=prompt_template
    )

    memory = ConversationBufferMemory(memory_key="chat_history")

    llm = OpenAI(temperature=0.0)
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    return chain


class VectorDB:
    """Class to manage document loading and vector database creation."""
    
    def __init__(self, docs_directory:str):

        self.docs_directory = docs_directory

    def create_vector_db(self):

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

        files = glob(os.path.join(self.docs_directory, "*.pdf"))

        loadPDFs = [PyPDFLoader(pdf_file) for pdf_file in files]

        pdf_docs = list()
        for loader in loadPDFs:
            pdf_docs.extend(loader.load())
        chunks = text_splitter.split_documents(pdf_docs)
            
        return Chroma.from_documents(chunks, OpenAIEmbeddings()) 
    
class ConversationalRetrievalChain:
    """Class to manage the QA chain setup."""

    def __init__(self, model_name="gpt-4o", temperature=0):
        self.model_name = model_name
        self.temperature = temperature
      
    def create_chain(self):

        model = ChatOpenAI(model_name=self.model_name,
                           temperature=self.temperature,
                           )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
            )
        vector_db = VectorDB('docs/')
        retriever = vector_db.create_vector_db().as_retriever(search_type="similarity",
                                                              search_kwargs={"k": 2},
                                                              )
        return RetrievalQA.from_chain_type(
            llm=model,
            retriever=retriever,
            memory=memory,
            )
    
def with_pdf_chatbot(messages):
    """Main function to execute the QA system."""
    query = messages[-1]['content'].strip()


    qa_chain = ConversationalRetrievalChain().create_chain()
    result = qa_chain({"query": query})
    return result['result']


# def create_VB(docs):
#     embeddings = OpenAIEmbeddings()
    
#     return FAISS.from_documents(docs, embeddings)


# def chatbot_retriever():
#     docs = load_docs()
#     vector_db = create_VB(docs)

#     model = ChatOpenAI(model_name="gpt-4o",
#                            temperature=0)

#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         return_messages=True
#         )

#     retriever = vector_db.create_vector_db().as_retriever(search_type="similarity",
#                                                             search_kwargs={"k": 2},
#                                                             )
#     return RetrievalQA.from_chain_type(
#         llm=model,
#         retriever=retriever,
#         memory=memory,
#         )

