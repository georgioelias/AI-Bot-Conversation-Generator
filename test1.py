import streamlit as st
import datetime
from openai import OpenAI
import anthropic
import os
import time

# Set your API keys
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
claude_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

def claude_format(my_list, separator=", "):
    temp=separator.join(map(str, my_list))
    text = temp[len('TextBlock(text="'):-len('",type="text")')]
    formatted_text = text.replace('\\n\\n', '\n\n').replace('\\n', '\n')
    return formatted_text


# Set page config
st.set_page_config(layout="wide", page_title="AI Bot Conversation Generator", page_icon="🤖")

# Initialize session state
if 'bots' not in st.session_state:
    st.session_state.bots = []
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def chat_with_ai(messages, model):
    try:
        if model == "claude-3-5-sonnet-20240620":
            prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = claude_client.messages.create(
                model=model,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            yield claude_format(response.content)
        else:
            response = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=150,
                stream=True
            )
            collected_messages = []
            for chunk in response:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message is not None:
                    collected_messages.append(chunk_message)
                    yield ''.join(collected_messages)
    except Exception as e:
        yield f"An error occurred: {e}"

def add_bot(name, model, system_prompt):
    st.session_state.bots.append({
        "name": name,
        "model": model,
        "history": [
            {"role": "system", "content": system_prompt}
        ]
    })

def run_conversation(iterations=3):
    full_history = []
    conversation = []
    
    for i in range(iterations):
        for idx, bot in enumerate(st.session_state.bots):
            combined_history = full_history + bot['history']
            
            user_input = "start" if idx == 0 and i == 0 else full_history[-1]['content'] if full_history else "start"
            
            combined_history.append({"role": "user", "content": user_input})
            
            message_placeholder = st.empty()
            full_response = ""
            for response in chat_with_ai(combined_history, model=bot['model']):
                full_response = response
                message_placeholder.markdown(f"{bot['name']}: {full_response}")
                time.sleep(0.05)
            
            combined_history.append({"role": "assistant", "content": full_response})
            
            bot['history'] = combined_history.copy()
            full_history = combined_history.copy()
            
            conversation.append(f"{bot['name']}: {full_response}")
    
    return conversation

# Create a three-column layout
left_sidebar, main_content, right_sidebar = st.columns([1, 3, 1])

# Left sidebar for bot management
with left_sidebar:
    st.sidebar.title("Bot Management")

    # Bot creation
    st.sidebar.subheader("Create a New Bot")
    if len(st.session_state.bots) < 5:
        new_bot_name = st.sidebar.text_input("Bot Name", key="new_bot_name")
        new_bot_model = st.sidebar.selectbox("Choose Model", ["gpt-4o-mini", "gpt-3.5-turbo", "claude-3-5-sonnet-20240620"], key="new_bot_model")
        new_bot_prompt = st.sidebar.text_area("Enter Bot Prompt", key="new_bot_prompt")
        FIXED_SYSTEM_PROMPT = f"""You are part of a groupchat of bots. your role will be the following :{new_bot_prompt} , 
        Please STICK to this role the WHOLE conversation.
        You will have access to the whole conversation history DON'T MIXED UP WITH YOUR ROLE. 
        """

        if st.sidebar.button("Add Bot", key="add_bot"):
            if new_bot_name and new_bot_prompt:
                add_bot(new_bot_name, new_bot_model, FIXED_SYSTEM_PROMPT)
                st.sidebar.success(f"Bot '{new_bot_name}' added successfully!")
            else:
                st.sidebar.error("Please provide a name and prompt for the bot.")
    else:
        st.sidebar.warning("Maximum number of bots (5) reached. Delete a bot to add a new one.")

    # Bot list and deletion
    st.sidebar.subheader("Available Bots")
    for i, bot in enumerate(st.session_state.bots):
        with st.sidebar.expander(f"{bot['name']}"):
            st.write(f"**Model:** {bot['model']}")
            st.write(f"**Prompt:** {bot['history'][0]['content']}")
            if st.button(f"Delete {bot['name']}", key=f"delete_{i}"):
                st.session_state.bots.pop(i)
                st.sidebar.success(f"{bot['name']} deleted successfully!")
                st.experimental_rerun()

    # Clear all bots
    if st.sidebar.button("Clear All Bots", key="clear_bots"):
        st.session_state.bots = []
        st.sidebar.success("All bots have been removed.")
        st.session_state.conversation = []

# Main content area
with main_content:
    st.title("AI Bot Conversation Generator")

    # Number of messages to generate
    num_messages = st.number_input("Number of iterations", min_value=1, value=3)

    # Generate conversation
    if st.button("Generate Conversation", key="generate"):
        if len(st.session_state.bots) < 2:
            st.warning("Please add at least two bots before generating a conversation.")
        else:
            st.session_state.conversation = run_conversation(iterations=num_messages)
            
            # Save to chat history
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_history.append((timestamp, st.session_state.conversation.copy()))
            
            st.success("Conversation generated and saved to history!")

    # Display conversation
    if st.session_state.conversation:
        st.subheader("Current Conversation:")
        for message in st.session_state.conversation:
            st.text(message)

    # Generate additional messages
    if st.session_state.conversation:
        additional_messages = st.number_input("Number of additional messages", min_value=1, value=1)
        if st.button("Generate Additional Messages"):
            new_messages = run_conversation(iterations=additional_messages)
            st.session_state.conversation.extend(new_messages)
            st.experimental_rerun()

    # Clear conversation
    if st.button("Clear Current Conversation", key="clear_conversation"):
        st.session_state.conversation = []
        st.success("Current conversation cleared.")

# Right sidebar for chat history
with right_sidebar:
    st.sidebar.title("Chat History")
    
    for i, (timestamp, conversation) in enumerate(reversed(st.session_state.chat_history)):
        with st.sidebar.expander(f"Chat {len(st.session_state.chat_history)-i} - {timestamp}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Load This Chat", key=f"load_{i}"):
                    st.session_state.conversation = conversation
                    st.experimental_rerun()
            with col2:
                if st.button("🗑", key=f"delete_chat_{i}"):
                    st.session_state.chat_history.pop(-(i+1))
                    st.sidebar.success(f"Chat {len(st.session_state.chat_history)-i} deleted.")
                    st.experimental_rerun()
            for message in conversation:
                st.text(message)
    
    # Clear all history
    if st.sidebar.button("Clear All History", key="clear_history"):
        st.session_state.chat_history = []
        st.sidebar.success("All chat history has been cleared.")
        st.rerun()