import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
import random
import time

# Load system prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: LLM Mode + Dice Roller
with st.sidebar:
    llm_mode = st.selectbox(
        "Choose LLM Mode:",
        options=["Narrative", "Combat", "Puzzle", "Dialogue", "Exploration"],
        index=0
    )
    st.markdown(f"**Current LLM Mode:** `{llm_mode}`")
    st.markdown("## 🎲 Dice Roller")
    st.markdown("Click below to roll a 20-sided dice.")

    if st.button("🎯 Roll d20"):
        with st.spinner("Rolling the dice..."):
            roll_placeholder = st.empty()

            for _ in range(15):
                temp_roll = random.randint(1, 20)
                roll_placeholder.markdown(f"### Rolling... **{temp_roll}**")
                time.sleep(0.05)

            final_roll = random.randint(1, 20)
            time.sleep(0.3)

        # Display result
        roll_placeholder.markdown(f"### You rolled: **{final_roll}**")

        # Narrative feedback
        if final_roll == 20:
            st.success("💥 What a Roll!")
        elif final_roll == 1:
            st.error("😵 Better luck next time!")
        elif final_roll >= 15:
            st.info("Solid roll!")
        elif final_roll <= 5:
            st.warning("Hmm...That was rough...")
        else:
            st.write("Not bad, not great.")

        # Log dice roll to messages
        roll_message = f"The player rolled a d20 and got {final_roll}."
        st.session_state.messages.append({"role": "user", "content": roll_message})

     
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        font-family: 'Arial', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 2.5em;
        color: #333;
        margin-bottom: 20px;
    }
    .chat-box {
        background-color: #fff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        color: #000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>Dungeons & Dragons - LLM Dungeon Master</div>", unsafe_allow_html=True)

# Function to get LLM response
def get_llm_response(chat_history):
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for chat_msg in chat_history:
        if chat_msg["role"] == "user":
            messages.append(HumanMessage(content=chat_msg["content"]))
        elif chat_msg["role"] == "bot":
            messages.append(AIMessage(content=chat_msg["content"]))

    llm = ChatOllama(
        model=os.environ.get("LLAMA_MODEL", "llama3.1"),
        api_key=os.environ.get("LLAMA_API_KEY"),
        streaming=True
    )
    response = llm.stream(messages)
    for chunk in response:
        yield chunk

# Main user input box
user_input = st.text_input("You:", "")

if user_input:
    # Optional: inject LLM mode into user input
    # user_input = f"[Mode: {llm_mode}]\n{user_input}"

    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response_stream = get_llm_response(st.session_state.messages)

    streamed_response = ""
    response_placeholder = st.empty()

    for word in bot_response_stream:
        streamed_response += word.content
        response_placeholder.markdown(
            f"<div class='chat-box'><strong>Bot:</strong> {streamed_response}</div>",
            unsafe_allow_html=True
        )

    st.session_state.messages.append({"role": "bot", "content": streamed_response.strip()})

# Clear Chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
