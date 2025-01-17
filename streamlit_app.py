import os
import streamlit as st
import json

from audio_recorder_streamlit import audio_recorder
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from streamlit_float import *
import hmac


from drive_connection import authenticate, create_creds
from create_vectorstore import run_vs
from helpers import speech_to_text
from generate_answer import base_model_chatbot


def main(answer_mode='base_model'):

    float_init()

    # Run the sidebar 
    if 'authcomplete' not in st.session_state:
        st.session_state.authcomplete = False
    if 'auth_url' not in st.session_state:
        st.session_state.auth_url = None
    if 'flow' not in st.session_state:
        st.session_state.flow = None
    if 'SCOPES' not in st.session_state:
        st.session_state.SCOPES =  ['https://www.googleapis.com/auth/drive']
    if "FOLDER_ID" not in st.session_state:
        st.session_state.FOLDER_ID = None

    if st.sidebar.button('Authorize Google Drive'):
        authenticate()

    # If token.json file was not yet present or did not work, first establish 
    if not st.session_state.authcomplete:
        if st.session_state.auth_url:
            with st.sidebar:
                st.write("Please authenticate Google via this [link](%s)" % st.session_state.auth_url)
                code = st.text_input('Enter the authorization code: ', None)
            if code:
                create_creds(code)
                authenticate()
            
    with st.sidebar:
        st.write("Google Drive authentication was succesfull: ", st.session_state.authcomplete)

    with st.sidebar:
        st.session_state.FOLDER_ID = st.text_input('Enter the folder id to be loaded: ', None)


    if (st.session_state.authcomplete) and (st.session_state.FOLDER_ID is not None):
        if st.sidebar.button('Update Vectorstore'):
            run_vs()

    if os.path.exists('token.json'):
        if st.sidebar.button('Delete Authentication File'):
            try:
                if os.path.exists('token.json'):
                    os.remove('token.json')
                    st.success("token.json file deleted successfully.")
                else:
                    st.warning("token.json file does not exist.")
            except Exception as e:
                st.error(f"An error occurred while deleting the token.json file: {e}")

    

    # Create chatbot
    def initialize_session_state():
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! How may I assist you today?"}
            ]

    initialize_session_state()

    st.title("Proposal Writer")

    # Create footer container for the microphone
    footer_container = st.container()
    with footer_container:
        col1, col2 = st.columns([1,3], vertical_alignment="bottom")
        with col1: 
            audio_bytes = audio_recorder()
        with col2:
            user_input = st.chat_input("Say something")


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if audio_bytes:
        # Write the audio bytes to a file
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.mp3"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)

            transcript = speech_to_text(webm_file_path)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)
                os.remove(webm_file_path)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

    
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking🤔..."):

                if 'rag_chain' not in st.session_state.keys():
                    print("adding chain to session state")
                    st.session_state.rag_chain = base_model_chatbot()

                response = st.session_state.rag_chain.invoke({"input": st.session_state.messages[-1]["content"], 
                                                              "chat_history":  st.session_state.messages})
                
                # st.write(response)
                final_response = response['answer']

            st.write(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})

    # Float the footer container and provide CSS to target it with
    footer_container.float("bottom: 0.5rem;")
            
if __name__ == "__main__":

    def check_password():
        """Returns `True` if the user had the correct password."""

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the password.
            else:
                st.session_state["password_correct"] = False

        # Return True if the password is validated.
        if st.session_state.get("password_correct", False):
            return True

        # Show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        if "password_correct" in st.session_state:
            st.error("😕 Password incorrect")

        return False

    if not check_password():
        st.stop()  # Do not continue if check_password is not True.

    main(answer_mode='base_model') 


# def main(answer_mode: str):
#     # Float feature initialization
#     float_init()

#     def reset_auth():
#         st.session_state.show_button = False

#     if "show_button" not in st.session_state:
#         reset_auth()

#     def load_docs():
#         # st.session_state.docs = load_googledrivedocs()
#         load_googledrivedocs()

#     st.button(
#         "Load Docs", key="reload", on_click=load_docs(), type="primary"
#     )


#     st.button(
#         "Reset Authorization", key="reset", on_click=reset_auth(), type="primary"
#     )

#     def initialize_session_state():
#         if "messages" not in st.session_state:
#             st.session_state.messages = [
#                 {"role": "assistant", "content": "Hi! How may I assist you today?"}
#             ]

#     initialize_session_state()

#     st.title("Proposal Writer")

#     # Create footer container for the microphone
#     footer_container = st.container()
#     with footer_container:
#         col1, col2 = st.columns([1,3], vertical_alignment="bottom")
#         with col1: 
#             audio_bytes = audio_recorder()
#         with col2:
#              user_input = st.chat_input("Say something")


#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.write(message["content"])

#     if audio_bytes:
#         # Write the audio bytes to a file
#         with st.spinner("Transcribing..."):
#             webm_file_path = "temp_audio.mp3"
#             with open(webm_file_path, "wb") as f:
#                 f.write(audio_bytes)

#             transcript = speech_to_text(webm_file_path)
#             if transcript:
#                 st.session_state.messages.append({"role": "user", "content": transcript})
#                 with st.chat_message("user"):
#                     st.write(transcript)
#                 os.remove(webm_file_path)

#     if user_input:
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.write(user_input)

#     if st.session_state.messages[-1]["role"] != "assistant":
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking🤔..."):

#                 if answer_mode == 'base_model':
#                     if 'llm_chain' not in st.session_state.keys():
#                         print("adding chain to session state")
#                         st.session_state.llm_chain = base_model_chatbot()

#                     response = st.session_state.llm_chain.invoke({"input": st.session_state.messages[-1]["content"]})
#                     final_response = response['response']

#                 elif answer_mode == 'pdf_chat':
#                     print('--------->', st.session_state.messages)
#                     final_response = with_pdf_chatbot(st.session_state.messages)

#             st.write(final_response)
#             st.session_state.messages.append({"role": "assistant", "content": final_response})

#     # Float the footer container and provide CSS to target it with
#     footer_container.float("bottom: 0.5rem;")
 
