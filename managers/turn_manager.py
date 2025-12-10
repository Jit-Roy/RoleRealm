"""
Turn management system for natural conversation flow.
Handles ONLY turn decision logic - determines who should speak next.
All timeline operations are delegated to TimelineManager.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
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
        priority_randomness: float = None,
        save_callback: Optional[callable] = None
    ):
        """
        Initialize the turn manager.
        
        Args:
            characters: List of AI characters in the conversation
            timeline: TimelineHistory instance containing all events and participants
            story_manager: Optional story manager for narrative progression
            max_consecutive_ai_turns: Maximum number of consecutive AI turns (defaults to Config.MAX_CONSECUTIVE_AI_TURNS)
            priority_randomness: Random factor to add to priority for naturalness (defaults to Config.PRIORITY_RANDOMNESS)
            save_callback: Optional callback function to save conversation after AI responses
        """
        self.characters = characters
        self.timeline = timeline
        self.story_manager = story_manager
        self.max_consecutive_ai_turns = max_consecutive_ai_turns or Config.MAX_CONSECUTIVE_AI_TURNS
        self.priority_randomness = priority_randomness or Config.PRIORITY_RANDOMNESS
        self.save_callback = save_callback
        
        # Initialize managers
        self.timeline_manager = TimelineManager()
        self.character_manager = CharacterManager()
        
        self.turn_count = 0
        self.consecutive_silence_rounds = 0
    
    def _collect_speaking_decisions(self) -> List[Tuple[Character, Tuple[str, float, str, Optional[str], Optional[str]]]]:
        """
        Collect response decisions from all AI characters using parallel execution.
        
        Returns:
            List of tuples containing (character, decision_tuple) for characters that want to respond (speak or act)
        """
        decisions = []
        quota_exceeded = False
        
        # Get story context if available
        story_context = self.story_manager.get_story_context() if self.story_manager else None
        
        # Define worker function for parallel execution
        def get_character_decision(character):
            return character, self.character_manager.decide_turn_response(
                character,
                story_context=story_context
            )
        
        # Execute all character decisions in parallel
        with ThreadPoolExecutor(max_workers=len(self.characters)) as executor:
            # Submit all tasks
            futures = {executor.submit(get_character_decision, char): char for char in self.characters}
            
            # Process results as they complete
            for future in as_completed(futures):
                try:
                    character, (response_type, priority, reasoning, dialogue, action) = future.result()
                    
                    # Check for quota exceeded error
                    if reasoning == "API_QUOTA_EXCEEDED":
                        quota_exceeded = True
                        continue
                    
                    if response_type in ["speak", "act"]:
                        decisions.append((character, (response_type, priority, reasoning, dialogue, action)))
                        emoji = "💭" if response_type == "speak" else "👤"
                        type_label = "Speech" if response_type == "speak" else "Action"
                        print(f"{emoji} {character.persona.name}: Priority {priority:.2f} ({type_label}) - {reasoning}")
                    else:
                        # Debug: Show why they don't want to respond
                        print(f"🤐 {character.persona.name}: {reasoning}")
                        
                except Exception as e:
                    character = futures[future]
                    print(f"⚠️  Error getting decision from {character.persona.name}: {e}")
        
        if quota_exceeded:
            print("⚠️  API QUOTA EXCEEDED")
        
        return decisions
    
    def _select_speaker_from_decisions(
        self, 
        decisions: List[Tuple[Character, Tuple[str, float, str, Optional[str], Optional[str]]]]
    ) -> Optional[Tuple[Character, str, Optional[str], Optional[str]]]:
        """
        Select which character should respond (speak or act) based on priorities.
        
        Args:
            decisions: List of (character, decision_tuple) tuples
            
        Returns:
            Tuple of (character, response_type, dialogue, action) for the selected character, or None
            - For "speak": dialogue=spoken words, action=body language
            - For "act": dialogue=None, action=physical action
        """
        if not decisions:
            return None
        
        # Sort by priority with small random factor for naturalness
        decisions_with_adjusted_priority = [
            (char, decision_tuple, decision_tuple[1] + random.uniform(-self.priority_randomness, self.priority_randomness))
            for char, decision_tuple in decisions
        ]
        
        decisions_with_adjusted_priority.sort(key=lambda x: x[2], reverse=True)
        
        # Return the highest priority character with their response type and content
        selected_character, decision_tuple, _ = decisions_with_adjusted_priority[0]
        response_type = decision_tuple[0]
        dialogue = decision_tuple[3]  # spoken words (for speak) or None (for act)
        action = decision_tuple[4]  # body_language (for speak) or physical action (for act)
        return (selected_character, response_type, dialogue, action)
    
    def select_next_speaker(self) -> Optional[Tuple[Character, str, Optional[str], Optional[str]]]:
        """
        Select which AI character should respond next (speak or act).
        
        Returns:
            Tuple of (character, response_type, dialogue, action) for the selected character, or None
            - For "speak": dialogue=spoken words, action=body language
            - For "act": dialogue=physical action, action=None
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
        """Process AI responses ONE AT A TIME until no one wants to speak or max turns reached.
        Each character sees the updated conversation including previous AI responses.
        Returns the list of (character, message) tuples for the caller to handle.
        
        Args:
            max_turns: Maximum number of consecutive AI turns (uses default if None)
            
        Returns:
            List of (character, message) tuples for AI turns that want to speak """
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
                print(f"🔕 Silence round {self.consecutive_silence_rounds}/2")
                
                # Generate scene event when conversation stalls
                if self.consecutive_silence_rounds >= 2:
                    self._generate_scene_event()
                    # Reset silence counter after scene event
                    self.consecutive_silence_rounds = 0
                
                break
            
            # Reset silence counter when someone responds
            self.consecutive_silence_rounds = 0
            
            character, response_type, dialogue, action = result
            
            # Prevent the same character from responding twice in a row
            if last_speaker == character.persona.name:
                print(f"   ⏭️  {character.persona.name} already responded, giving others a chance...")
                continue  # Continue to next iteration instead of breaking, let other characters respond
            
            # Validate that we have content before processing
            if response_type == "speak" and not dialogue:
                print(f"   ⚠️  {character.persona.name} chose to speak but provided no dialogue, skipping...")
                continue
            elif response_type == "act" and not action:
                print(f"   ⚠️  {character.persona.name} chose to act but provided no action, skipping...")
                continue
            
            # Handle different response types
            if response_type == "speak":
                # For speak: dialogue = spoken words, action = body language
                body_language = action
                
                # Create and add the message to the timeline
                message_obj = self.timeline_manager.create_message(
                    speaker=character.persona.name,
                    content=dialogue,
                    action_description=body_language or "speaks"
                )
                self.timeline_manager.add_event(self.timeline, message_obj)
                
                # Broadcast this TimelineEvent to all characters
                self.character_manager.broadcast_event_to_characters(self.characters, message_obj)
                
                # Print with body language in cyan color if available
                print(f"\n💬 {character.persona.name}:", end="")
                if body_language:
                    print(f" {Fore.CYAN}*{body_language}*{Style.RESET_ALL}")
                    print(f"   \"{dialogue}\"")
                else:
                    print(f" {dialogue}")
                
                responses.append((character, dialogue))
                
            elif response_type == "act":
                # For act: dialogue is None, action contains the physical action
                physical_action = action
                
                # Create and add the action to the timeline
                from data_models import Action
                action_obj = self.timeline_manager.create_action(
                    character=character.persona.name,
                    description=physical_action
                )
                self.timeline_manager.add_event(self.timeline, action_obj)
                
                # Broadcast this TimelineEvent to all characters
                self.character_manager.broadcast_event_to_characters(self.characters, action_obj)
                
                # Print action without dialogue
                print(f"\n👤 {character.persona.name}: {Fore.CYAN}*{physical_action}*{Style.RESET_ALL}")
                
                responses.append((character, f"[ACTION: {physical_action}]"))
            
            last_speaker = character.persona.name
            consecutive_count += 1
            
            # Small delay for readability and to let next character see the context
            time.sleep(2)
        
        # After all character responses, check if a scene event should be generated
        scene_decision = self.timeline_manager.should_generate_scene(self.timeline, recent_event_count=15)
        if scene_decision:
            print("\n" + "─"*70)
            print("🌅 SCENE EVENT")
            print("─"*70)
            
            # Create and add scene event
            scene = self.timeline_manager.create_scene(
                location=scene_decision['location'],
                description=scene_decision['event_description']
            )
            self.timeline_manager.add_event(self.timeline, scene)
            
            # Broadcast scene to all characters
            self.character_manager.broadcast_event_to_characters(self.characters, scene)
            
            print(f"\n📍 Location: {scene.location}")
            print(f"{scene.description}\n")
            print("─"*70)
        
        # Save conversation after AI responses if callback is provided
        if responses and self.save_callback:
            self.save_callback()
        
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
            
            # Add scene to timeline
            self.timeline_manager.add_event(self.timeline, scene)
            
            # Broadcast scene event to all characters so they're aware of it
            self.character_manager.broadcast_event_to_characters(self.characters, scene)
            
            # Save conversation after scene event if callback is provided
            if self.save_callback:
                self.save_callback()
            
            time.sleep(2)
            
        except Exception as e:
            print(f"\nError generating scene event: {e}\n")
            print("─"*70)