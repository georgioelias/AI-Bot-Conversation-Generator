import streamlit as st
import random
import datetime
from openai import OpenAI
import anthropic
import requests
import time

BOT_COLORS = ["#FF5733", "#33FF57", "#3357FF", "#FF33F1", "#33FFF1"]

# Set your API keys
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
claude_client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Set page config
st.set_page_config(layout="wide", page_title="AI Bot Conversation Generator", page_icon="🤖")

# Initialize session state
if 'bots' not in st.session_state:
    st.session_state.bots = []
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'colored_conversation' not in st.session_state:
    st.session_state.colored_conversation = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'initial_message' not in st.session_state:
    st.session_state.initial_message = "start"

def return_claudeformat(my_list, separator=", "):
    temp=separator.join(map(str, my_list))

    # Strip the 'TextBlock(text="' prefix and the trailing part
    text = temp[len('TextBlock(text="'):-len('",type="text")')]

    # Replace the escaped newline characters with actual newlines
    formatted_text = text.replace('\\n\\n', '\n\n').replace('\\n', '\n')
    
    return formatted_text

def chat_with_ai(messages, model="gpt-4o-mini",bot_name="", bot_color=""):
    try:
        if model == "claude-3-5-sonnet-20240620":
            system_message = None
            formatted_messages = []
            last_role = None

            for m in messages:
                if m['role'] == 'system':
                    system_message = m['content']
                else:
                    role = m['role']
                    if role not in ['assistant', 'user']:
                        role = 'user'  # Default to 'user' for custom roles
                    
                    # Ensure alternating user and assistant messages
                    if role == last_role == 'user':
                        formatted_messages[-1]['content'] += "\n\n" + m['content']
                    else:
                        formatted_messages.append({"role": role, "content": m['content']})
                        last_role = role

            # Ensure the last message is from the user
            if formatted_messages[-1]['role'] != 'user':
                formatted_messages.append({"role": "user", "content": "Please continue the conversation."})

            response = claude_client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_message,
                messages=formatted_messages
            )
            yield f'<span style="font-size: 18px; font-weight: bold; color: {bot_color};">{bot_name}:</span> {return_claudeformat(response.content)}'
        else:
            # OpenAI code remains unchanged
            response = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            collected_messages = []
            for chunk in response:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message is not None:
                    collected_messages.append(chunk_message)
                    full_response = ''.join(collected_messages)
                    yield f'<span style="font-size: 18px; font-weight: bold; color: {bot_color};">{bot_name}:</span> {full_response}'
    except Exception as e:
        yield f"An error occurred: {e}"

def add_bot(name, model, user_prompt):
    color = BOT_COLORS[len(st.session_state.bots) % len(BOT_COLORS)]
    FIXED_SYSTEM_PROMPT = f"""You are an AI assistant named {name} participating in a multi-bot conversation. Your specific role and personality are as follows:

        {user_prompt}

        Respond to the previous messages in the conversation, staying in character and adhering to your defined role. Keep your responses short and relevant to the ongoing discussion.
    
        DON'T UNDER ANY CIRCUMSTANCES START YOUR MESSAGE WITH "bot name:", REPLY WITH THE ANSWER DIRECTLY
        
        You can refer to many speakers message at once also you can ask questions to other participants in the chat to get more insights"""

    st.session_state.bots.append({
        "name": name,
        "model": model,
        "user_prompt": user_prompt,
        "color": color,
        "history": [
            {"role": "system", "content": FIXED_SYSTEM_PROMPT}
        ]
    })

def run_conversation(iterations=3):
    full_history = []
    conversation = []
    colored_conversation = []

    
    for i in range(iterations):
        for idx, bot in enumerate(st.session_state.bots):
            # Create a formatted history with speaker names
            formatted_history = [
                {"role": "system", "content": bot['history'][0]['content']}
            ]
            for entry in full_history:
                formatted_history.append({
                    "role": "user",
                    "content": f"{entry['speaker']}: {entry['content']}"
                })
            
            user_input = st.session_state.initial_message if idx == 0 and i == 0 else full_history[-1]['content'] if full_history else st.session_state.initial_message
            
            formatted_history.append({"role": "user", "content": f"Previous message: {user_input}"})
            
            message_placeholder = st.empty()
            
            full_response = ""
            for response in chat_with_ai(formatted_history, model=bot['model'], bot_name=bot['name'], bot_color=bot['color']):
                full_response = response
                message_placeholder.markdown(full_response, unsafe_allow_html=True)
                time.sleep(0.05)
            
            # Extract content without HTML tags
            content = full_response.split('</span> ', 1)[1] if '</span>' in full_response else full_response
            
            full_history.append({
                "speaker": bot['name'],
                "content": content
            })
            
            conversation.append(f"{bot['name']}: {content}")
            colored_conversation.append({
                "name": bot['name'],
                "content": content,
                "color": bot['color']
            })
    
    return conversation, colored_conversation

# Create a three-column layout
left_sidebar, main_content, right_sidebar = st.columns([1, 3, 1])

# Left sidebar for bot management
with left_sidebar:
    st.sidebar.title("Bot Management")

    # Bot creation
    st.sidebar.subheader("Create a New Bot")
    if len(st.session_state.bots) < 5:
        new_bot_name = st.sidebar.text_input("Bot Name", key="new_bot_name")
        new_bot_model = st.sidebar.selectbox("Choose Model", ["gpt-4","gpt-4o-mini", "gpt-3.5-turbo", "claude-3-5-sonnet-20240620"], key="new_bot_model")
        new_bot_prompt = st.sidebar.text_area("Enter Bot Prompt", key="new_bot_prompt")

        if st.sidebar.button("Add Bot", key="add_bot"):
            if new_bot_name and new_bot_prompt:
                add_bot(new_bot_name, new_bot_model, new_bot_prompt)
                st.sidebar.success(f"Bot '{new_bot_name}' added successfully!")
            else:
                st.sidebar.error("Please provide a name and prompt for the bot.")
    else:
        st.sidebar.warning("Maximum number of bots (5) reached. Delete a bot to add a new one.")

    # Bot list, editing, and deletion
# Bot list, editing, and deletion
    st.sidebar.subheader("Available Bots")
    for i, bot in enumerate(st.session_state.bots):
        with st.sidebar.expander(f"{bot['name']}"):
            st.write(f"**Model:** {bot['model']}")
            new_prompt = st.text_area(f"Edit Prompt for {bot['name']}", value=bot['user_prompt'])
            if st.button(f"Save Changes for {bot['name']}", key=f"save_{i}"):
                bot['user_prompt'] = new_prompt
                bot['history'][0]['content'] = bot['history'][0]['content'].replace(
                    bot['user_prompt'], new_prompt
                )
                st.success(f"Prompt updated for {bot['name']}")
            if st.button(f"Delete {bot['name']}", key=f"delete_{i}"):
                st.session_state.bots.pop(i)
                st.success(f"{bot['name']} deleted successfully!")
                st.experimental_rerun()

    # Clear all bots
    if st.sidebar.button("Clear All Bots", key="clear_bots"):
        st.session_state.bots = []
        st.success("All bots have been removed.")
        st.session_state.conversation = []

# Main content area
with main_content:
    st.title("AI Bot Conversation Generator")

    # Initial message input
    st.session_state.initial_message = st.text_input("Enter the initial message for the conversation:", value=st.session_state.initial_message)

    # Number of messages to generate
    num_messages = st.number_input("Number of iterations", min_value=1, value=3)

    # Generate conversation
    if st.button("Generate Conversation", key="generate"):
        if len(st.session_state.bots) < 2:
            st.warning("Please add at least two bots before generating a conversation.")
        else:
            st.session_state.conversation, st.session_state.colored_conversation = run_conversation(iterations=num_messages)
            
            # Save to chat history
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_history.append((timestamp, st.session_state.conversation.copy()))
            
            st.success("Conversation generated and saved to history!")

# Display conversation
if st.session_state.colored_conversation:
    st.subheader("Current Conversation:")
    for message in st.session_state.colored_conversation:
        styled_message = f'<p><span style="font-size: 18px; font-weight: bold; color: {message["color"]};">{message["name"]}:</span> {message["content"]}</p>'
        st.markdown(styled_message, unsafe_allow_html=True)

    # Generate additional messages
    if st.session_state.colored_conversation:
        additional_messages = st.number_input("Number of additional messages", min_value=1, value=1)
        if st.button("Generate Additional Messages"):
            new_messages, new_colored_messages = run_conversation(iterations=additional_messages)
            st.session_state.conversation.extend(new_messages)
            st.session_state.colored_conversation.extend(new_colored_messages)
            for message in new_colored_messages:
                styled_message = f'<p><span style="font-size: 18px; font-weight: bold; color: {message["color"]};">{message["name"]}:</span> {message["content"]}</p>'
                st.markdown(styled_message, unsafe_allow_html=True)

    # Clear conversation
    if st.button("Clear Current Conversation", key="clear_conversation"):
        st.session_state.conversation = []
        st.session_state.colored_conversation = []
        st.success("Current conversation cleared.")

# Right sidebar for chat history
with right_sidebar:
    st.sidebar.title("Chat History")
    
    for i, (timestamp, conversation) in enumerate(reversed(st.session_state.chat_history)):
        with st.sidebar.expander(f"Chat {len(st.session_state.chat_history)-i} - {timestamp}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Load This Chat", key=f"load_{i}"):
                    try:
                        st.session_state.conversation = conversation.copy()  # Make a copy to avoid reference issues
                        st.session_state.colored_conversation = []
                        for msg in conversation:
                            name, content = msg.split(": ", 1)  # Split only on the first ":"
                            color = next((bot['color'] for bot in st.session_state.bots if bot['name'] == name), "#000000")
                            st.session_state.colored_conversation.append({
                                "name": name,
                                "content": content,
                                "color": color
                            })
                        st.success("Chat loaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading chat: {str(e)}")
            # ... (delete button and message display)
            with col2:
                if st.button("🗑", key=f"delete_chat_{i}"):
                    st.session_state.chat_history.pop(-(i+1))
                    st.success(f"Chat {len(st.session_state.chat_history)-i} deleted.")
                    st.rerun()
            for message in conversation:
                st.text(message)


    # Clear all history
    if st.sidebar.button("Clear All History", key="clear_history"):
        st.session_state.chat_history = []
        st.success("All chat history has been cleared.")
        st.rerun()
