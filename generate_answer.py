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
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

try:
    api_key = os.getenv("OPENAI_API_KEY")
except:
    os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"]

openai.api_key = api_key

def base_model_chatbot():


    # SET UP LLM & RETRIEVER
    llm = OpenAI(temperature=0.0)

    embeddings = OpenAIEmbeddings()

    index_name = "googledriveindex"
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    retriever = vectorstore.as_retriever()

    # CREATE QUESTION
    contextualize_q_system_prompt = """Given a chat history and the latest user input \
    which might reference context in the chat history, formulate a standalone user input \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    ##############################
    ### Answer question ###
    qa_system_prompt = """
        You are an assistant that helps a human to write a proposal from the input given by the human in 
        addition to the context provided to you. 
        You will output the following:

        First, you give a short summary, that can function as a case description. 
        Second, you state which actions should be taken. 
        Last, you state which oustanding questions there still are. 

        If you do not know the answer to the question, simply respond with "I do not have enough 
        information to write a proposal, can you give me more information?" If possible, be specific 
        in which information you are missing. If the context provided to you, does not seem an addition
        to the proposal, do not use it. Keep the proposal concise.


        {context}
        """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain

