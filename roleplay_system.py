"""
Main roleplay system coordinator.
"""

from typing import List, Optional
from pathlib import Path
import json

from data_models import CharacterPersona, Character
from data_models import Character
from managers.turn_manager import TurnManager
from managers.sceneManager import NarratorManager
from config import Config
from managers.messageManager import MessageManager
from managers.sceneManager import SceneManager


class RoleplaySystem:
    """Main coordinator for the multi-character roleplay system."""
    
    def __init__(
        self,
        player_name: str,
        characters: List[CharacterPersona],
        model_name: str = None,
        chat_storage_dir: str = None,
        story_manager = None,
        narrator_manager = None
    ):
        """
        Initialize the roleplay system.
        
        Args:
            player_name: Name of the human player
            characters: List of character personas for AI characters
            model_name: Gemini model to use for all characters (defaults to Config.DEFAULT_MODEL)
            chat_storage_dir: Directory to store chat logs (defaults to Config.CHAT_STORAGE_DIR)
            story_manager: Optional StoryManager for narrative progression
            narrator_manager: Optional NarratorManager for scene transitions
            
        Raises:
            ValueError: If OPENROUTER_API_KEY is not set
        """
        # Configure API with key from Config
        api_key = Config.OPENROUTER_API_KEY
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set in environment. "
                "Please set it in your .env file or environment variables."
            )
        
        self.player_name = player_name
        self.model_name = model_name or Config.DEFAULT_MODEL
        
        # Create AI characters
        self.ai_characters = [
            Character(persona=persona)
            for persona in characters
        ]
        
        # Create or use provided narrator manager
        self.narrator_manager = narrator_manager or NarratorManager(model_name=self.model_name)
        
        # Create turn manager with narrator
        self.turn_manager = TurnManager(
            characters=self.ai_characters,
            player_name=player_name,
            story_manager=story_manager,
            narrator_manager=self.narrator_manager
        )
        
        # Get references to managers for direct access
        self.message_manager = self.turn_manager.message_manager
        self.scene_manager = self.turn_manager.scene_manager
        self.scene = self.turn_manager.scene
        
        # Setup storage
        self.chat_storage_dir = Path(chat_storage_dir or Config.CHAT_STORAGE_DIR)
        self.chat_storage_dir.mkdir(exist_ok=True)
        
        # Try to load existing conversation
        self._load_conversation_if_exists()
    
    def _load_conversation_if_exists(self) -> bool:
        """
        Load existing conversation from file if it exists.
        
        Returns:
            True if conversation was loaded, False otherwise
        """
        filepath = self.get_conversation_file_path()
        
        if not filepath.exists():
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore the scene from saved data
            self.scene = self.scene_manager.from_dict(data)
            self.turn_manager.scene = self.scene
            
            print("\n" + "="*70)
            print("📂 LOADED EXISTING CONVERSATION")
            print("="*70)
            print(f"Restored {len(self.scene.messages)} previous messages")
            print(f"Continuing from where you left off...")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n⚠️  Could not load previous conversation: {e}")
            print("Starting fresh conversation instead.\n")
            return False
    
    def _save_conversation(self) -> None:
        """Save the current conversation to a JSON file."""
        filename = "group_chat.json"
        filepath = self.chat_storage_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Use mode='json' to properly serialize datetime objects
            json.dump(self.scene_manager.to_dict(), f, indent=2, ensure_ascii=False, default=str)
    
    def _add_player_message(self, content: str) -> None:
        """Add a player message to the conversation."""
        # Extract action description from brackets if present
        import re
        action_desc = None
        dialogue = content
        
        bracket_match = re.search(r'\[([^\]]+)\]', content)
        if bracket_match:
            action_desc = bracket_match.group(1).strip()
            # Remove brackets from the dialogue
            dialogue = re.sub(r'\[([^\]]+)\]', '', content).strip()
        
        message = self.message_manager.create_message(
            speaker=self.player_name,
            content=dialogue,
            action_description=action_desc
        )
        self.message_manager.add_message(self.scene, message)
        
        # Broadcast player message to all characters' perceived messages
        # Each character now has this in their own perspective
        self.character_manager.broadcast_message_to_characters(self.characters, message)
        self._save_conversation()
    
    def _add_ai_message(self, character: Character, content: str) -> None:
        """Add an AI character message to the conversation."""
        message = self.message_manager.create_message(
            speaker=character.persona.name,
            content=content
        )
        self.message_manager.add_message(self.scene, message)
        self._save_conversation()
    
    def get_conversation_file_path(self) -> Path:
        """Get the file path where the conversation is saved."""
        return self.chat_storage_dir / "group_chat.json"
    
    def reset_conversation(self) -> None:
        """
        Reset the conversation to start fresh.
        Deletes the saved file and clears current messages.
        """
        filepath = self.get_conversation_file_path()
        
        # Delete saved file if it exists
        if filepath.exists():
            filepath.unlink()
        
        # Clear current scene messages
        self.scene.messages.clear()
        
        print("\n" + "="*70)
        print("🔄 CONVERSATION RESET")
        print("="*70)
        print("All previous messages have been cleared.")
        print("Starting fresh conversation...")
        print("="*70 + "\n")
    
    def display_welcome(self) -> None:
        """Display welcome message with character information."""
        char_names = ", ".join([char.persona.name for char in self.ai_characters])
        
        welcome = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                      🎭 ROLEREALM SYSTEM 🎭                         ║
║                                                                      ║
║                  Interactive AI-Powered Roleplay                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

You are playing as {self.player_name.upper()}, joined by {char_names}.

The conversation will flow naturally - AI characters will respond when they
have something to say, creating an organic, dynamic storytelling experience!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📜 COMMANDS:
   • Just type naturally to speak as {self.player_name}
   • 'skip' - Let AI characters continue talking without you
   • 'info' - See character details
   • 'quit' or 'exit' - End the roleplay session

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(welcome)
    
    def display_character_info(self) -> None:
        """Display information about all AI characters."""
        print("\n📖 CHARACTER INFORMATION:\n")
        for character in self.ai_characters:
            persona = character.persona
            print(f"🎭 {persona.name}")
            print(f"   Traits: {', '.join(persona.traits[:3])}...")
            print(f"   Style: {persona.speaking_style[:60]}...")
            print()
    
    def _send_initial_greeting(self) -> None:
        """Send initial greeting message from player."""
        print(f"\n💬 {self.player_name}: Hello everyone!")
        self._add_player_message("Hello everyone!")
        
        # Let AI characters respond (messages are printed inside process_ai_responses)
        ai_responses = self.turn_manager.process_ai_responses()
    
    def _handle_player_input(self, user_input: str) -> bool:
        """
        Handle player input and return whether to continue.
        
        Args:
            user_input: The player's input string
            
        Returns:
            True to continue the conversation, False to exit
        """
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'end', 'goodbye']:
            print("\n👋 Ending roleplay session...")
            print(f"💾 Chat saved to: {self.get_conversation_file_path()}")
            return False
        
        # Check for skip command
        if user_input.lower() == 'skip':
            print("\n⏭️  Letting AI characters continue...")
            ai_responses = self.turn_manager.process_ai_responses(max_turns=5)
            return True
        
        # Check for info command
        if user_input.lower() in ['info', 'characters', 'help']:
            self.display_character_info()
            return True
        
        # Skip empty inputs
        if not user_input:
            return True
        
        # Add player message and let AI respond (messages are printed inside process_ai_responses)
        self._add_player_message(user_input)
        ai_responses = self.turn_manager.process_ai_responses()
        
        return True
    
    def run(self, show_char_info: bool = False) -> None:
        """
        Run the interactive roleplay session.
        
        Args:
            show_char_info: Whether to display character information at start
        """
        self.display_welcome()
        
        if show_char_info:
            self.display_character_info()
        
        # Send initial greeting
        self._send_initial_greeting()
        
        # Main conversation loop
        while True:
            try:
                # Get player input
                user_input = input(f"\n⚡ {self.player_name}: ").strip()
                
                # Handle input and check if should continue
                should_continue = self._handle_player_input(user_input)
                if not should_continue:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted! Ending roleplay...")
                print(f"💾 Chat saved to: {self.get_conversation_file_path()}")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the current session.
        
        Returns:
            Dictionary containing session statistics
        """
        return {
            "player_name": self.player_name,
            "ai_characters": [char.persona.name for char in self.ai_characters],
            "total_messages": self.message_manager.get_message_count(self.scene),
            "total_turns": self.turn_manager.turn_count
        }
    
    def __repr__(self) -> str:
        return (f"RoleplaySystem(player='{self.player_name}', "
                f"characters={len(self.ai_characters)}, "
                f"messages={self.message_manager.get_message_count(self.scene)})")
