import json
import streamlit as st
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def create_url():
    

    credentials = {
    "web": {
        "client_id": st.secrets["CLIENT_ID"],
        "project_id": st.secrets["PROJECT_ID"], 
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": st.secrets["CLIENT_SECRET"],
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }

    # Convert dictionary to JSON string
    json_string = json.dumps(credentials, indent=4)

    # Save JSON string to a file
    with open('client_secrets.json', 'w') as json_file:
        json_file.write(json_string)

    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', 
        st.session_state.SCOPES, 
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    
    # Tell the user to go to the authorization URL.
    auth_url, _ = flow.authorization_url(prompt='consent')

    st.session_state.auth_url = auth_url
    st.session_state.flow = flow

def create_creds(code):
    try: 
        flow = st.session_state.flow
        flow.fetch_token(code=code)

        session = flow.authorized_session()

        creds = flow.credentials

        # Save the credentials
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

        return creds

    except Exception as e:
        st.error(f"An error occurred: {e}")


def authenticate(code):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', st.session_state.SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            create_url()

            if st.session_state.auth_url:
                with st.sidebar:
                    st.write('Please go to this URL: ', st.session_state.auth_url)
                    code = st.text_input('Enter the authorization code: ', None)
                if code:
                    creds = create_creds(code)

    if creds and creds.valid:
        service = build('drive', 'v3', credentials=creds)

        with st.sidebar:
            st.success("Google Drive authentication was successful.")
        st.session_state.authcomplete = True
 


    # try: 
    #     flow = st.session_state.flow
    #     flow.fetch_token(code=code)

    #     session = flow.authorized_session()

    #     creds = flow.credentials

    #     # Save the credentials
    #     with open('token.json', 'w') as token_file:
    #         token_file.write(creds.to_json())
            
    #     service = build('drive', 'v3', credentials=creds)

    #     with st.sidebar:
    #         st.success("Google Drive authentication was successful.")
    #     st.session_state.authcomplete = True

    # except Exception as e:
    #     st.error(f"An error occurred: {e}")


        
