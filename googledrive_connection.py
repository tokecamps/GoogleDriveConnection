
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from langchain_google_community import GoogleDriveLoader
from langchain_community.document_loaders import UnstructuredFileIOLoader

import json

import os

import streamlit as st

from dotenv import load_dotenv

load_dotenv()

def create_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    credentials = {
        "web": {
            "client_id": st.secrets["CLIENT_ID"],
            "project_id": st.secrets["PROJECT_ID"], 
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": st.secrets["CLIENT_SECRET"],
            "redirect_uris": ["'urn:ietf:wg:oauth:2.0:oob", "http://localhost", "http://localhost:8501", "https://chatbot-proposal.streamlit.app"]
            }
        }

    # Convert dictionary to JSON string
    json_string = json.dumps(credentials, indent=4)

    # Save JSON string to a file
    with open('Creds/client_secrets.json', 'w') as json_file:
        json_file.write(json_string)

    print(json_string)

    flow = InstalledAppFlow.from_client_secrets_file('Creds/client_secrets.json', SCOPES, redirect_uri='https://chatbot-proposal.streamlit.app')

    auth_url, _ = flow.authorization_url(prompt='consent')

    st.sidebar.title("Google Drive API Authentication")

    if st.session_state.show_button == False:
        if st.sidebar.link_button("Authorize Google Drive", auth_url):
            st.session_state.show_button = True
        
    else:
        if st.sidebar.button("Fetch token"):

            flow.fetch_token()
            creds = flow.credentials

            # Save the credentials
            with open('Creds/token.json', 'w') as token_file:
                token_file.write(creds.to_json())

            st.session_state.service = build('drive', 'v3', credentials=creds)
            
        

def load_googledrivedocs():

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

    folder_id = "root"
    # try: 
    #     loader = GoogleDriveLoader(
    #         folder_id = folder_id,
    #         credentials_path = "Creds/client_secrets.json", 
    #         token_path="Creds/token.json", 
    #         recursive=True, 
    #         load_extended_metadata=True,
    #         file_loader_cls=UnstructuredFileIOLoader,
    #     )

    #     return loader.load()

    # except:
        # Renew token access


    create_service()

    # loader = GoogleDriveLoader(
    #     folder_id = folder_id,
    #     credentials_path = "Creds/client_secrets.json", 
    #     token_path="Creds/token.json", 
    #     recursive=True, 
    #     load_extended_metadata=True,
    #     file_loader_cls=UnstructuredFileIOLoader,
    # )

    #     return None
    # return loader.load()


