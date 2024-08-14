# AI Bot Conversation Generator

## Overview

**AI Bot Conversation Generator** is a Streamlit-based application that allows users to create and manage AI-powered bots that interact with each other. The application supports multiple AI models, including OpenAI's GPT-4 and GPT-3.5, as well as Claude 3.5. Each bot can be customized with a unique prompt and personality, leading to engaging and dynamic conversations.

## Features

- **Bot Creation & Management**: Create, edit, or delete up to 5 AI bots with custom prompts and models.
- **Multi-Bot Conversations**: Generate conversations between multiple bots with the ability to iterate through multiple rounds of dialogue.
- **Real-Time Interaction**: View the conversation in real-time with color-coded messages for each bot.
- **Chat History**: Save, load, and manage previous conversations.
- **Customization**: Customize the bots' prompts and personalities to guide the conversation.

## Installation

To get started with the AI Bot Conversation Generator, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-bot-conversation-generator.git
cd ai-bot-conversation-generator
```

### 2. Install Dependencies

Make sure you have Python 3.7 or higher installed. Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys

You'll need API keys for OpenAI and Anthropic. Store them in Streamlit's secrets management by creating a file named `.streamlit/secrets.toml` in the project directory with the following content:

```toml
[secrets]
OPENAI_API_KEY = "your-openai-api-key"
ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

### 4. Run the Application

You can start the Streamlit application by running:

```bash
streamlit run app.py
```

## Usage

1. **Add Bots**: Use the left sidebar to create and customize AI bots.
2. **Generate Conversations**: Enter an initial message and set the number of iterations to generate a conversation.
3. **View Conversations**: Real-time display of conversations in the main content area.
4. **Manage History**: Save, load, and clear chat histories using the right sidebar.

## Example

![image](https://github.com/user-attachments/assets/96a98152-a004-4bb2-8304-72efd3f8e62a)


## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://www.streamlit.io/) for the awesome framework.
- [OpenAI](https://www.openai.com/) and [Anthropic](https://www.anthropic.com/) for their powerful language models.

