"""
Manager for message-related operations.
"""

from typing import List, Dict, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_models import Message, MessageHistory
from config import Config
from openrouter_client import GenerativeModel
from helpers.response_parser import parse_json_response


class MessageManager:
    """Manager for message-related operations."""
    
    def __init__(self):
        """Initialize MessageManager."""
        self.model = GenerativeModel(Config.DEFAULT_MODEL)
    
    def create_message(
        self, 
        speaker: str, 
        content: str, 
        action_description: str
    ) -> Message:
        """Create a new message instance."""
        return Message(
            speaker=speaker, 
            content=content, 
            action_description=action_description
        )
    
    def add_message(
        self,
        message_history: MessageHistory,
        message: Message
    ) -> Message:
        """
        Add a message to the message_history and update participants.
        
        Args:
            message_history: MessageHistory instance to add message to
            message: Message instance to add
            
        Returns:
            The added Message
        """
        message_history.messages.append(message)
        
        if message.speaker not in message_history.participants:
            message_history.participants.append(message.speaker)
        
        return message
    
    def get_recent_messages(self, message_history: MessageHistory, n: int = 10) -> List[Message]:
        """
        Get the n most recent messages from history.
        
        Args:
            message_history: MessageHistory instance to retrieve from
            n: Number of recent messages
            
        Returns:
            List of recent messages
        """
        return message_history.messages[-n:] if len(message_history.messages) > n else message_history.messages
    
    def create_message_history(
        self,
        title: Optional[str] = None,
        scene_description: Optional[str] = None,
        participants: Optional[List[str]] = None,
        visible_to_user: bool = True,
        location: Optional[str] = None
    ) -> MessageHistory:
        """
        Create a new message history.
        
        Args:
            title: Optional conversation title (e.g., 'Midnight Planning')
            scene_description: Optional description of the scene or context
            location: Optional location where conversation took place
            participants: Optional initial participants list
            visible_to_user: Whether user can view this conversation (default True)
            
        Returns:
            New MessageHistory instance
        """
        
        return MessageHistory(
            title=title,
            scene_description=scene_description,
            location=location,
            participants=participants,
            visible_to_user=visible_to_user,
            location = location
        )
    
    def summarize_conversation(self, message_history: MessageHistory) -> str:
        """
        Generate a brief AI-powered summary of the conversation.
        
        Args:
            message_history: MessageHistory instance to summarize
            
        Returns:
            Summary string
        """
        if not message_history.messages:
            return "No conversation to summarize."
        
        # Build conversation text for summarization
        conversation_text = []
        for msg in message_history.messages:
            conversation_text.append(f"{msg.speaker}: *{msg.action_description}* {msg.content}")
        
        conversation_str = "\n".join(conversation_text)
        
        # Build context
        context_parts = []
        if message_history.title:
            context_parts.append(f"Title: {message_history.title}")
        if message_history.scene_description:
            context_parts.append(f"Scene: {message_history.scene_description}")
        if message_history.location:
            context_parts.append(f"Location: {message_history.location}")
        
        context_str = "\n".join(context_parts) if context_parts else ""
        
        prompt = f"""You are summarizing a roleplay conversation between characters.
        {context_str}
        CONVERSATION:
        {conversation_str}
        TASK: Generate a concise summary (2-4 sentences) of this conversation covering:
        - What the main topics discussed were
        - Any important decisions or revelations
        - The overall mood or tone
        - Key character interactions or conflicts

        OUTPUT FORMAT (strict JSON):
        {{
        "summary": "Your 2-4 sentence summary here"
        }}
        Keep it brief but capture the essence of what happened."""
        try:
            response = self.model.generate_content(prompt, temperature=0.7)
            summary_data = parse_json_response(response.text)
            summary = summary_data.get("summary", "Unable to generate summary.")
            message_history.conversation_summary = summary
            return summary
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {e}")