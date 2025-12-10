"""
Turn management system for natural conversation flow.
Handles ONLY turn decision logic - determines who should speak next.
All timeline operations are delegated to TimelineManager.
"""

import random
import time
from typing import List, Optional, Tuple
from colorama import Fore, Style

from data_models import Message, TimelineHistory, Character, Scene
from managers.timelineManager import TimelineManager
from managers.characterManager import CharacterManager
from managers.storyManager import StoryManager
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
        timeline: TimelineHistory,
        story_manager: Optional[StoryManager] = None,
        max_consecutive_ai_turns: int = None,
        priority_randomness: float = None
    ):
        """
        Initialize the turn manager.
        
        Args:
            characters: List of AI characters in the conversation
            timeline: TimelineHistory instance containing all events and participants
            story_manager: Optional story manager for narrative progression
            max_consecutive_ai_turns: Maximum number of consecutive AI turns (defaults to Config.MAX_CONSECUTIVE_AI_TURNS)
            priority_randomness: Random factor to add to priority for naturalness (defaults to Config.PRIORITY_RANDOMNESS)
        """
        self.characters = characters
        self.timeline = timeline
        self.story_manager = story_manager
        self.max_consecutive_ai_turns = max_consecutive_ai_turns or Config.MAX_CONSECUTIVE_AI_TURNS
        self.priority_randomness = priority_randomness or Config.PRIORITY_RANDOMNESS
        
        # Initialize managers
        self.timeline_manager = TimelineManager()
        self.character_manager = CharacterManager()
        
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
        story_context = self.story_manager.get_story_context() if self.story_manager else None
        
        for character in self.characters:
            wants_to_speak, priority, reasoning, action_desc, message = self.character_manager.decide_to_speak(
                character,
                story_context=story_context
            )
            
            # Check for quota exceeded error
            if reasoning == "API_QUOTA_EXCEEDED":
                quota_exceeded = True
                continue
            
            if wants_to_speak:
                decisions.append((character, (wants_to_speak, priority, reasoning, action_desc, message)))
                print(f"💭 {character.persona.name}: Priority {priority:.2f} - {reasoning}")
            else:
                # Debug: Show why they don't want to speak
                print(f"🤐 {character.persona.name}: {reasoning}")
        
        if quota_exceeded:
            print("⚠️  API QUOTA EXCEEDED")
        
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
        action_desc = decision_tuple[3]  
        message = decision_tuple[4]  
        return (selected_character, action_desc, message)
    
    def select_next_speaker(self) -> Optional[Tuple[Character, Optional[str], str]]:
        """
        Select which AI character should speak next.
        
        Returns:
            Tuple of (character, action_description, message) for the selected speaker, or None
        """
        # Check if there are any events in the timeline
        recent_events = self.timeline_manager.get_recent_events(timeline=self.timeline)
        if not recent_events:
            return None
        
        print("\n🤔 AI characters are thinking...")
        
        # Collect decisions from all characters
        decisions = self._collect_speaking_decisions()
        
        if not decisions:
            print("💤 No one wants to speak right now.")
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
            if self.story_manager and consecutive_count >= 2:
                recent_events = self.timeline_manager.get_recent_events(self.timeline)
                event_count = len(recent_events)
                event = self.story_manager.check_for_story_event(
                    silence_duration=consecutive_count,
                    message_count=event_count,
                    recent_messages=recent_events[-3:] if len(recent_events) >= 3 else recent_events
                )
                if event:
                    self.story_manager.display_story_event(event)
                    current_location = self.timeline_manager.get_current_location(self.timeline)
                    self.timeline_manager.add_event(
                        self.timeline,
                        event=Scene(
                            location=current_location or "Unknown",
                            description=f"[{event['title']}] {event['description']}"
                        )
                    )
                    break
            
            # Ask ONE character at a time (sequentially, not in parallel)
            # Note: select_next_speaker() prints its own "thinking" and "no one speaks" messages
            result = self.select_next_speaker()
            
            if result is None:
                # No one wants to speak - increment silence counter
                self.consecutive_silence_rounds += 1
                
                # Generate scene event when conversation stalls
                if self.consecutive_silence_rounds >= 2:
                    self._generate_scene_event()
                    # Reset silence counter after scene event
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
            
            # Create and add the message to the timeline
            message_obj = self.timeline_manager.create_message(
                speaker=character.persona.name,
                content=message,
                action_description=action_desc
            )
            self.timeline_manager.add_event(self.timeline, message_obj)
            
            # Broadcast this TimelineEvent to all characters
            # Each character now has this in their own perspective
            self.character_manager.broadcast_event_to_characters(self.characters, message_obj)
            
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
    
    def _generate_scene_event(self) -> None:
        """Generate a dramatic scene event when conversation stalls."""
        print("\n" + "─"*70)
        print("🌅 SCENE EVENT")
        print("─"*70)
        
        # Generate scene event
        try:
            scene = self.timeline_manager.generate_scene_event(
                timeline=self.timeline,
                recent_event_count=15
            )
            
            print(f"\n{scene.description}\n")
            print("─"*70)
            time.sleep(2)
            
        except Exception as e:
            print(f"\nError generating scene event: {e}\n")
            print("─"*70)