"""
Turn management system for natural conversation flow.
Handles ONLY turn decision logic - determines who should speak next.
All message operations are delegated to MessageManager.
"""

import random
import time
from typing import List, Optional, Tuple
from colorama import Fore, Style

from data_models import Message, MessageHistory, Character
from managers.messageManager import MessageManager
from managers.sceneManager import SceneManager
from managers.characterManager import CharacterManager
from managers.storyManager import StoryManager
from managers.narratorManager import NarratorManager
from config import Config


class TurnManager:
    """
    Manages conversation flow and turn selection with natural timing.
    
    Responsibilities:
    - Decide who should speak next based on context
    - Coordinate between AI characters to determine speaking order
    - Process consecutive AI responses naturally
    """
    
    def __init__(
        self,
        characters: List[Character],
        player_name: str,
        story_manager: Optional[StoryManager] = None,
        narrator_manager: Optional[NarratorManager] = None,
        max_consecutive_ai_turns: int = None,
        priority_randomness: float = None
    ):
        """
        Initialize the turn manager.
        
        Args:
            characters: List of AI characters in the conversation
            player_name: Name of the human player
            story_manager: Optional story manager for narrative progression
            narrator_manager: Optional narrator manager for scene transitions
            max_consecutive_ai_turns: Maximum number of consecutive AI turns (defaults to Config.MAX_CONSECUTIVE_AI_TURNS)
            priority_randomness: Random factor to add to priority for naturalness (defaults to Config.PRIORITY_RANDOMNESS)
        """
        self.characters = characters
        self.player_name = player_name
        self.story_manager = story_manager
        self.narrator_manager = narrator_manager or NarratorManager()
        self.max_consecutive_ai_turns = max_consecutive_ai_turns or Config.MAX_CONSECUTIVE_AI_TURNS
        self.priority_randomness = priority_randomness or Config.PRIORITY_RANDOMNESS
        
        # Initialize managers
        self.message_manager = MessageManager()
        self.scene_manager = SceneManager()
        self.character_manager = CharacterManager()
        
        # Initialize scene with all participants
        all_participants = [player_name] + [char.persona.name for char in characters]
        self.scene = self.scene_manager.create_scene(
            participants=all_participants
        )
        
        self.turn_count = 0
        self.consecutive_silence_rounds = 0
    
    def _collect_speaking_decisions(self) -> List[Tuple[Character, Tuple[bool, float, str, Optional[str]]]]:
        """
        Collect speaking decisions from all AI characters.
        
        Returns:
            List of tuples containing (character, decision_tuple) for characters that want to speak
        """
        decisions = []
        quota_exceeded = False
        
        # Get story context if available
        story_context = None
        if self.story_manager:
            story_context = self.story_manager.get_story_context()
        
        for character in self.characters:
            wants_to_speak, priority, reasoning, action_desc, message = self.character_manager.decide_to_speak(
                character,
                self.scene.messages,
                story_context=story_context
            )
            
            # Check for quota exceeded error
            if reasoning == "API_QUOTA_EXCEEDED":
                quota_exceeded = True
                continue
            
            if wants_to_speak:
                decisions.append((character, (wants_to_speak, priority, reasoning, action_desc, message)))
                print(f"   💭 {character.persona.name}: "
                      f"Priority {priority:.2f} - {reasoning}")
            else:
                # Debug: Show why they don't want to speak
                print(f"   🤐 {character.persona.name}: {reasoning}")
        
        # Display quota exceeded message if detected
        if quota_exceeded:
            print("\n" + "="*70)
            print("⚠️  API QUOTA EXCEEDED")
            print("="*70)
            print("You've reached the free tier limit for Gemini API requests.")
            print(f"Current model: {Config.DEFAULT_MODEL}")
            print("Free tier limit: ~20 requests per minute")
            print("\nOptions:")
            print("  1. Wait ~40-60 seconds and try again")
            print("  2. Check your usage at: https://ai.dev/usage?tab=rate-limit")
            print("  3. Upgrade your plan for higher limits")
            print("="*70 + "\n")
        
        return decisions
    
    def _select_speaker_from_decisions(
        self, 
        decisions: List[Tuple[Character, Tuple[bool, float, str, Optional[str], Optional[str]]]]
    ) -> Optional[Tuple[Character, Optional[str], str]]:
        """
        Select which character should speak based on priorities.
        
        Args:
            decisions: List of (character, decision_tuple) tuples
            
        Returns:
            Tuple of (character, action_description, message) or None if no valid speakers
        """
        if not decisions:
            return None
        
        # Sort by priority with small random factor for naturalness
        decisions_with_adjusted_priority = [
            (char, decision_tuple, decision_tuple[1] + random.uniform(-self.priority_randomness, self.priority_randomness))
            for char, decision_tuple in decisions
        ]
        
        decisions_with_adjusted_priority.sort(key=lambda x: x[2], reverse=True)
        
        # Return the highest priority character with their action and message
        selected_character, decision_tuple, _ = decisions_with_adjusted_priority[0]
        action_desc = decision_tuple[3]  # Extract action description
        message = decision_tuple[4]  # Extract message from tuple
        return (selected_character, action_desc, message)
    
    def select_next_speaker(self) -> Optional[Tuple[Character, Optional[str], str]]:
        """
        Select which AI character should speak next.
        
        Returns:
            Tuple of (character, action_description, message) for the selected speaker, or None
        """
        if not self.scene.messages:
            return None
        
        print("\n🤔 AI characters are thinking...")
        
        # Collect decisions from all characters
        decisions = self._collect_speaking_decisions()
        
        if not decisions:
            print("   💤 No one wants to speak right now.")
            return None
        
        # Select the speaker
        result = self._select_speaker_from_decisions(decisions)
        
        return result
    
    def process_ai_responses(self, max_turns: Optional[int] = None) -> List[Tuple[Character, str]]:
        """
        Process AI responses ONE AT A TIME until no one wants to speak or max turns reached.
        Each character sees the updated conversation including previous AI responses.
        Returns the list of (character, message) tuples for the caller to handle.
        
        Args:
            max_turns: Maximum number of consecutive AI turns (uses default if None)
            
        Returns:
            List of (character, message) tuples for AI turns that want to speak
        """
        if max_turns is None:
            max_turns = self.max_consecutive_ai_turns
        
        responses = []
        consecutive_count = 0
        last_speaker = None
        
        while consecutive_count < max_turns:
            # Check for story events ONLY after multiple AI turns (not immediately)
            # And only when conversation is flowing naturally, not at transition points
            if self.story_manager and consecutive_count >= 2:
                message_count = len(self.scene.messages)
                event = self.story_manager.check_for_story_event(
                    silence_duration=consecutive_count,
                    message_count=message_count,
                    recent_messages=self.scene.messages[-3:] if len(self.scene.messages) >= 3 else self.scene.messages
                )
                if event:
                    self.story_manager.display_story_event(event)
                    # Add event as a narrative message
                    event_msg = self.message_manager.create_message(
                        speaker="Narrator",
                        content=f"[{event['title']}] {event['description']}"
                    )
                    self.message_manager.add_message(self.scene, event_msg)
                    # Events interrupt the AI conversation flow
                    break
            
            # Ask ONE character at a time (sequentially, not in parallel)
            # Note: select_next_speaker() prints its own "thinking" and "no one speaks" messages
            result = self.select_next_speaker()
            
            if result is None:
                # No one wants to speak - increment silence counter
                self.consecutive_silence_rounds += 1
                
                # Check if narrator should intervene
                if self.narrator_manager.detect_conversation_stagnation(
                    self.consecutive_silence_rounds,
                    self.scene.messages,
                    self.player_name
                ):
                    self._trigger_narrator_intervention()
                    # Reset silence counter after intervention
                    self.consecutive_silence_rounds = 0
                
                break
            
            # Reset silence counter when someone speaks
            self.consecutive_silence_rounds = 0
            
            character, action_desc, message = result
            
            # Prevent the same character from speaking twice in a row
            if last_speaker == character.persona.name:
                print(f"   ⏭️  {character.persona.name} already spoke, giving others a chance...")
                break
            
            responses.append((character, message))
            
            # Add the message to the scene with separate action_description field
            message_obj = self.message_manager.create_message(
                speaker=character.persona.name,
                content=message,
                action_description=action_desc
            )
            self.message_manager.add_message(self.scene, message_obj)
            
            # Print with action description in cyan color if available
            print(f"\n💬 {character.persona.name}:", end="")
            if action_desc:
                print(f" {Fore.CYAN}*{action_desc}*{Style.RESET_ALL}")
                print(f"   \"{message}\"")
            else:
                print(f" {message}")
            
            last_speaker = character.persona.name
            consecutive_count += 1
            
            # Small delay for readability and to let next character see the context
            time.sleep(2)
        
        return responses
    
    def _trigger_narrator_intervention(self) -> None:
        """Trigger narrator to create an environmental description."""
        print("\n" + "─"*70)
        print("🌅 ENVIRONMENTAL MOMENT")
        print("─"*70)
        
        # Generate environmental description
        description = self.narrator_manager.generate_transition_narrative(
            current_scene=self.scene_manager.location,
            recent_messages=self.scene.messages,
            silence_rounds=self.consecutive_silence_rounds,
            player_name=self.player_name
        )
        
        print(f"\n{description}\n")
        print("─"*70)
        
        # Add narrator message to scene
        narrator_msg = self.message_manager.create_message(
            speaker="Narrator",
            content=f"[Environment] {description}"
        )
        self.message_manager.add_message(self.scene, narrator_msg)
        time.sleep(2)
        character_names = [char.persona.name for char in self.characters]
        wakeup = self.narrator_manager.generate_wakeup_event(
            self.player_name,
            character_names
        )
        if wakeup:
            print(f"\n{wakeup}\n")
            print("="*70 + "\n")
            # Add wakeup as narrator message
            wakeup_msg = self.message_manager.create_message(
                speaker="Narrator",
                content=f"[Wakeup Event] {wakeup}"
            )
            self.message_manager.add_message(self.scene, wakeup_msg)