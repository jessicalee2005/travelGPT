from chains.information_extractor import Information_Extractor
from chains.summarizer import Summarizer 
import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from chains.tagger import Tagger
from utils.logger import logger

_ = load_dotenv(find_dotenv())  # read local .env file (load enviornmental vars)

st.title("Travel Destination Assistant - AI Agent") #sets up srtreamlit app title
logger.propagate = False

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [] #allows prev chats to be displayed on reruns

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input(
    "Ask me anything about travel destinations!"
):
    try:
        summarizer = Summarizer(os.getenv("OPENAI_API_KEY"))  

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            st.markdown("Let me check that for you...")
        
        
        user_intent = Tagger(os.getenv("OPENAI_API_KEY")).extract_information(prompt)
        information = Information_Extractor(os.getenv("OPENAI_API_KEY")).get_information(user_intent)
        summary = summarizer.summarize(information, prompt)
        

        with st.chat_message("assistant"):
            st.markdown(summary)
        st.session_state.messages.append({"role": "assistant", "content": summary})
    except Exception as e:
        logger.debug(f"Error: {e}")
        message = "I was not able to process the request. Please try again."
        st.markdown(message)
        st.session_state.messages.append({"role": "assistant", "content": message})
