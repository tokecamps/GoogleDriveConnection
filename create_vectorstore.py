from langchain_google_community import GoogleDriveLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import streamlit as st
from pinecone import Pinecone

import os
from dotenv import load_dotenv

load_dotenv()


def load_documents():
    CLIENT_SECRET_FILE = "client_secrets.json"
    TOKEN_FILE = "token.json"
    GOOGLE_DRIVER_FOLDER_ID ="root"

    loader = GoogleDriveLoader(
        credentials_path=CLIENT_SECRET_FILE,
        token_path=TOKEN_FILE,
        folder_id=GOOGLE_DRIVER_FOLDER_ID,
        recursive=False,
        file_types=["sheet", "document", "pdf"],
    )
    return loader.load()

def add_files_to_vs(docs):
    
    os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

    embeddings = OpenAIEmbeddings()

    index_name = "googledriveindex"
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

    try:
        vectorstore.delete(delete_all=True)

    except:
        st.write("Vectorstore could not be deleted")
        

    vectorstore_from_docs = PineconeVectorStore.from_documents(
            docs,
            index_name=index_name,
            embedding=embeddings
        )
    
def check_index():
    index_name = "googledriveindex"
    pc = Pinecone()

    # connect to index
    index = pc.Index(index_name)

    # view index stats
    index_stats  = index.describe_index_stats()

    return index_stats['total_vector_count']    

def run_vs():
    docs = load_documents()
    st.write(docs)
    add_files_to_vs(docs)

    num_vectors = check_index()

    with st.sidebar:
        st.write("The vectorstore contains a number of ", str(num_vectors), " vectors")
