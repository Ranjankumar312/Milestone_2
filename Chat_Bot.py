import streamlit as st
import pandas as pd
import requests
import json

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Chatbot with Dataset (Ollama)", layout="wide")

DATA_PATH = "bengaluru_house_prices.csv" 
OLLAMA_URL = "http://localhost:11434/api/generate"  
OLLAMA_MODEL = "llama3.2:1b" 
# ------------------- SESSION STATE -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "df" not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(DATA_PATH)
        st.success(f"✅ Loaded dataset `{DATA_PATH}` with shape {st.session_state.df.shape}")
    except Exception as e:
        st.error(f"❌ Failed to load dataset: {e}")
        st.stop()

# ------------------- HELPER FUNCTION -------------------
def get_ollama_response(user_input, df_sample):
    """Send user query + dataset context to Ollama and return the reply"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"You are a helpful assistant. Here is some dataset context:\n{df_sample}\n\nUser: {user_input}\nAssistant:"
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
        output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        output += data["response"]
                except Exception:
                    continue
        return output if output else "⚠️ No response from Ollama"
    except Exception as e:
        return f"⚠️ Request failed: {e}"

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("### ⚡ Chat_bot")

    if st.button("📝 New chat"):
        if st.session_state.messages:
            st.session_state.chat_history.append(st.session_state.messages)
        st.session_state.messages = []
        st.experimental_rerun()

    st.button("🔍 Search chats")
    st.button("⚙️ Settings ")

    st.markdown("---")
    st.subheader("Chats")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history):
            if st.button(f"💬 Chat {i+1}", key=f"history_{i}"):
                st.session_state.messages = chat
                st.experimental_rerun()
    else:
        st.caption("No chats yet...")

# ------------------- MAIN CHAT WINDOW -------------------
st.title("💬 Chatbot (with Dataset & Ollama)")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------- CHAT INPUT -------------------
if prompt := st.chat_input("Type your question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ------------------- BOT RESPONSE -------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Take a small dataset sample for context
            df_sample = st.session_state.df.head(5).to_string()

            reply = get_ollama_response(prompt, df_sample)
            st.markdown(reply)

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": reply})
