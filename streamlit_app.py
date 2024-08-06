import os
import streamlit as st
import json


from googleapiclient.discovery import build

from google_auth_oauthlib.flow import InstalledAppFlow




def main():

    if 'authcomplete' not in st.session_state:
        st.session_state.authcomplete = False
    if 'auth_url' not in st.session_state:
        st.session_state.auth_url = None
    if 'flow' not in st.session_state:
        st.session_state.flow = None


    def create_url():
        SCOPES = ['https://www.googleapis.com/auth/drive']
    
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
            SCOPES, 
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        
        # Tell the user to go to the authorization URL.
        auth_url, _ = flow.authorization_url(prompt='consent')

        st.session_state.auth_url = auth_url
        st.session_state.flow = flow
  

    if st.button('Authorize Google Drive'):
        create_url()

    if st.session_state.auth_url:
        st.write('Please go to this URL: ', st.session_state.auth_url)
        code = st.text_input('Enter the authorization code: ', None)

        if code:
            try: 
                flow = st.session_state.flow
                flow.fetch_token(code=code)

                session = flow.authorized_session()

                creds = flow.credentials

                # Save the credentials
                with open('token.json', 'w') as token_file:
                    token_file.write(creds.to_json())
                    
                service = build('drive', 'v3', credentials=creds)

                st.success("Google Drive authentication was successful.")
                st.session_state.authcomplete = True
            except Exception as e:
                st.error(f"An error occurred: {e}")

    st.write("Google Drive authentication was succesfull: ", st.session_state.authcomplete)
            
if __name__ == "__main__":

    main() # Or: answer_mode='base_model' 


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
 
