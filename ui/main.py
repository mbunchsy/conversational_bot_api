from ui.models import ConversationStatus
import streamlit as st
from ui.services.api_client import APIClient
from ui.config import UIConfig
from enum import Enum

st.set_page_config(
    page_title="Chat Bot Interface",
    page_icon="🤖",
    layout="wide"
)

config = UIConfig()
api_client = APIClient(config.API_URL)

st.markdown("""
    <style>
    .stChat {
        max-width: 800px;
        margin: 0 auto;
    }
    .stTextInput {
        max-width: 800px;
        margin: 0 auto;
    }
    .stButton {
        max-width: 800px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

if 'conversation' not in st.session_state:
    st.session_state.conversation = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'language' not in st.session_state:
    st.session_state.language = config.LANGUAGE

st.title("🤖 Chat Bot Interface")

with st.sidebar:
    st.header("Settings")
    
    st.session_state.language = st.selectbox(
        "Language",
        options=["es", "en", "fr", "de"],
        format_func=lambda x: {
            "es": "Spanish 🇪🇸",
            "en": "English 🇬🇧",
            "fr": "French 🇫🇷",
            "de": "German 🇩🇪"
        }[x]
    )
    
    if st.button("New Conversation"):
        conversation = api_client.create_conversation(
            config.DEFAULT_USER_ID,
            language=st.session_state.language
        )
        if conversation:
            st.session_state.conversation = conversation
            st.session_state.messages = []
            if "messages" in conversation:
                for msg in conversation["messages"]:
                    if msg.get("role") != "system":
                        st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
            st.success("New conversation started!")
        else:
            st.error("Error creating conversation")

    if st.session_state.conversation:
        st.write(f"Conversation ID: {st.session_state.conversation['id']}")

    col1, col2 = st.columns([1, 1])
    with col2:
        if st.session_state.conversation and st.button("End Conversation"):
            with st.spinner("Generating summary..."):
                try:
                    api_client.get_summary(st.session_state.conversation["id"], ConversationStatus.COMPLETED)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "🎯 Conversation ended successfully"
                    })
                    st.session_state.conversation = None
                    st.success("Conversation ended and summary generated")
                except Exception as e:
                    st.error(f"Error ending conversation: {str(e)}")

if st.session_state.conversation:
    for msg in st.session_state.messages:
        if msg.get("role") != "system":
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                st.write(msg["content"])

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        response = api_client.send_message(st.session_state.conversation["id"], prompt)
        if response:
            with st.chat_message("assistant"):
                bot_response = response["messages"][-1]["content"]
                st.write(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
        else:
            st.error("Error getting bot response")

    with st.expander("Send voice message"):
        st.write("Upload a WAV or MP3 file")
        audio_file = st.file_uploader(
            "Choose audio file",
            type=["wav", "mp3"],
            help="Only WAV and MP3 files are supported"
        )
        if audio_file:
            st.audio(audio_file)
            if st.button("Send Audio"):
                with st.spinner("Processing audio..."):
                    response = api_client.send_audio(
                        st.session_state.conversation["id"],
                        audio_file,
                        st.session_state.language
                    )
                    if response:
                        with st.chat_message("assistant"):
                            bot_response = response["messages"][-1]["content"]
                            st.write(bot_response)
                            st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    else:
                        st.error("Error processing audio")
else:
    st.info("👆 Click on 'New Conversation' to start")