import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
import os
import random  # Import random for dice roll functionality
import time  # Import time for simulating rolling animation

# Fix encoding issue when opening the system prompt file
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Ensure session state is initialized
if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialize messages as an empty list
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

# Collapsible sidebar for Llama model selection
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
            
            # Simulate dice rolling animation
            for _ in range(15):
                temp_roll = random.randint(1, 20)
                roll_placeholder.markdown(f"### Rolling... **{temp_roll}**")
                time.sleep(0.05)
            
            final_roll = random.randint(1, 20)
            time.sleep(0.3)  # Add slight pause before showing final result

        # Show final result after spinner ends
        roll_placeholder.markdown(f"### You rolled: **{final_roll}**")

        # Add narrative feedback
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
            st.session_state.messages.append({"role": "user", "content": f"User has rolled a d20. Outcome: {str(final_roll)}"})
            
# Add a title and background color to make the UI more appealing
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
        color: #000; /* Ensure text is black for visibility */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>Dungeons & Dragons - LLM Dungeon Master</div>", unsafe_allow_html=True)

# Function to get LLM response using LangChain with selected Llama model
def get_llm_response(chat_history):
    # Convert chat history to LangChain message format
    messages = []
    for chat_msg in chat_history:  # Renamed loop variable to avoid shadowing
        if chat_msg["role"] == "user":
            messages.append(HumanMessage(content=chat_msg["content"]))
        else:
            # For bot messages, you can use AIMessage if needed
            messages.append(AIMessage(content=chat_msg["content"]))

    llm = ChatOllama(model=os.environ.get("LLAMA_MODEL", "llama3.1"), api_key=os.environ.get("LLAMA_API_KEY"),streaming=True)
    response = llm.stream(messages)
    for chunk in response:
        yield chunk
    return response

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the system prompt to the chat history
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

user_input = st.text_input("You:", "")

# Update the UI to stream the bot's response
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response_stream = get_llm_response(st.session_state.messages)

    # Initialize an empty string to collect the streamed response
    streamed_response = ""
    response_placeholder = st.empty()  # Placeholder for streaming response

    for word in bot_response_stream:
        streamed_response += word.content  # Collect the streamed content
        response_placeholder.markdown(f"<div class='chat-box'><strong>Bot:</strong> {streamed_response}</div>", unsafe_allow_html=True)

    # Append the final response to the session state
    st.session_state.messages.append({"role": "bot", "content": streamed_response.strip()})




if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()  # Refresh the app to clear the chat history

