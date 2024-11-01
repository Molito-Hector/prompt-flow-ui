import streamlit as st
import urllib.request
import json
import os
import ssl

# Load environment variable from Streamlit's secrets
AZURE_ENDPOINT_KEY = os.getenv('AZURE_ENDPOINT_KEY')

def allowSelfSignedHttps(allowed):
    # Bypass server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def main():
    # Allow self-signed HTTPS certificates
    allowSelfSignedHttps(True)

    st.title("Azure Prompt Flow Chat Interface")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for interaction in st.session_state.chat_history:
        if interaction["inputs"]["chat_input"]:
            with st.chat_message("user"):
                st.write(interaction["inputs"]["chat_input"])
        if interaction["outputs"]["answer"]:
            with st.chat_message("assistant"):
                st.write(interaction["outputs"]["answer"])

    # React to user input
    if user_input := st.chat_input("Ask me anything..."):

        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        # Query API
        data = {"chat_history": st.session_state.chat_history, 'chat_input': user_input}
        body = json.dumps(data).encode('utf-8')
        url = 'https://gyt-chat.eastus.inference.ml.azure.com/score'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AZURE_ENDPOINT_KEY}'
        }
        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            response_data = json.loads(response.read().decode('utf-8'))

            # Render response
            with st.chat_message("assistant"):
                st.markdown(response_data['chat_output'])

            # Add user input and assistant response to chat history
            st.session_state.chat_history.append(
                {"inputs": {"chat_input": user_input},
                 "outputs": {"answer": response_data['chat_output']}}
            )

        except urllib.error.HTTPError as error:
            st.error(f"The request failed with status code: {error.code}")
            st.text(error.read().decode("utf8", 'ignore'))

if __name__ == "__main__":
    main()
