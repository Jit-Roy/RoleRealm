# RoleRealm

An interactive AI-powered roleplay system that brings characters to life through dynamic conversations and story-driven experiences, powered by Google's Gemini API.

## Features

- 🎭 **Dynamic Character Interactions** - Create and interact with multiple AI characters, each with unique personalities and speaking styles
- 💬 **Natural Conversations** - Advanced conversation management with full context awareness
- 📖 **Story Progression System** - Structure your narratives with story arcs, scenes, and objectives
- 💾 **Persistent Sessions** - Automatic chat history and story state saving
- 🔄 **Context Awareness** - Characters remember past interactions across sessions
- 👥 **Multi-Character Support** - Seamlessly manage conversations with multiple AI characters

## Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Jit-Roy/RoleRealm.git
cd RoleRealm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### Running RoleRealm

Simply run the main script:
```bash
python main.py
```

## Project Structure

```
RoleRealm/
├── main.py                 # Main entry point
├── characters/             # Character definition JSON files
├── stories/                # Story arc JSON files
├── managers/               # Core system managers
│   ├── characterManager.py
│   ├── messageManager.py
│   ├── sceneManager.py
│   ├── storyManager.py
│   └── turn_manager.py
├── chat_logs/              # Saved conversation histories
└── config.py               # Configuration settings
```

## Customization

### Creating Characters

Define characters in JSON format in the `characters/` folder. Each character should include:
- Name and traits
- Speaking style
- Background and relationships
- Goals and knowledge base

### Creating Stories

Design story arcs in JSON format in the `stories/` folder with:
- Story beats and scenes
- Objectives and progression logic
- Scene descriptions

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.
