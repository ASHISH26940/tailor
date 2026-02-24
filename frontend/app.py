import streamlit as st
import requests
import json
from urllib.parse import urljoin

BACKEND_URL = "https://tailor-mcju.onrender.com"

st.set_page_config(page_title="Titanic Dataset Chatbot", page_icon="🚢", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #FDF0D5;
    }

    .app-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .app-header h1 {
        color: #003049;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .app-header p {
        color: #669BBC;
        font-size: 1.1rem;
    }

    .stChatMessage {
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #e8dcc0 !important;
        border-left: 3px solid #669BBC;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #f5e8c8 !important;
        border-left: 3px solid #C1121F;
    }

    .stChatInput, .stChatInput > div,
    .stChatInput [data-testid="stChatInputContainer"],
    .stChatInput [data-testid="stBottom"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #003049 !important;
        border: 1.5px solid #669BBC !important;
        border-radius: 10px !important;
        padding: 0.6rem !important;
    }
    .stChatInput textarea:focus {
        border-color: #003049 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    [data-testid="stBottom"] {
        background-color: #FDF0D5 !important;
    }
    [data-testid="stBottom"] > div {
        background-color: transparent !important;
    }

    .stButton > button {
        background-color: #C1121F;
        color: #FDF0D5;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #780000;
        color: #FDF0D5;
    }

    a { color: #003049 !important; }
    hr { border-color: #669BBC33; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #FDF0D5; }
    ::-webkit-scrollbar-thumb { background: #669BBC; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h1>🚢 Titanic Dataset Explorer</h1>
    <p>Ask questions about the Titanic dataset — get answers, charts & insights</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "images" in message:
            for img_path in message["images"]:
                full_image_url = urljoin(BACKEND_URL, img_path)
                st.image(full_image_url)

if prompt := st.chat_input("E.g., What was the survival rate by gender?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/chat", json={"query": prompt})
            response.raise_for_status()
            
            data = response.json()
            reply_text = data.get("text", "Sorry, I didn't get a response.")
            reply_images = data.get("images", [])
            
            message_placeholder.markdown(reply_text)
            
            for img_path in reply_images:
                full_image_url = urljoin(BACKEND_URL, img_path)
                st.image(full_image_url)
                
            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply_text,
                "images": reply_images
            })
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Failed to connect to backend API at {BACKEND_URL}. Is it running?"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
