"""
Narrator Manager for autonomous scene transitions and environmental storytelling.
Handles time progression, environmental changes, and narrative events.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from config import Config
from data_models import Message
from openrouter_client import GenerativeModel


class NarratorManager:
    """Manages narrative transitions, time progression, and environmental storytelling."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the Narrator Manager.
        
        Args:
            model_name: Gemini model to use (defaults to Config.DEFAULT_MODEL)
        """
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.model = None
        self.current_time_of_day = "evening"  # evening, night, late_night, dawn, morning, afternoon
        self.environment_state = {
            "fire": "crackling warmly",
            "lighting": "warm and golden",
            "temperature": "comfortable",
            "sounds": ["fire crackling", "wind outside"],
            "time_passed_hours": 0
        }
        self.previous_descriptions = []  # Track previous environmental descriptions to avoid repetition
        
    def get_or_create_model(self) -> Any:
        """Get or create the generative model."""
        if self.model is None:
            self.model = GenerativeModel(self.model_name)
        return self.model
    
    def advance_time(self, hours: float = 1.0) -> str:
        """
        Advance time and update environment accordingly.
        
        Args:
            hours: Number of hours to advance
            
        Returns:
            Description of time change
        """
        self.environment_state["time_passed_hours"] += hours
        
        # Update time of day
        if self.current_time_of_day == "evening" and hours >= 2:
            self.current_time_of_day = "night"
            return "evening → night"
        elif self.current_time_of_day == "night" and hours >= 3:
            self.current_time_of_day = "late_night"
            return "night → late night"
        elif self.current_time_of_day == "late_night" and hours >= 2:
            self.current_time_of_day = "dawn"
            return "late night → dawn"
        elif self.current_time_of_day == "dawn" and hours >= 1:
            self.current_time_of_day = "morning"
            return "dawn → morning"
        
        return f"time passes ({hours} hours)"
    
    def update_environment_for_time(self):
        """Update environmental details based on current time."""
        if self.current_time_of_day == "evening":
            self.environment_state.update({
                "fire": "crackling warmly",
                "lighting": "warm and golden from firelight",
                "sounds": ["fire crackling", "distant voices", "wind outside"]
            })
        elif self.current_time_of_day == "night":
            self.environment_state.update({
                "fire": "burning steadily, flames dancing",
                "lighting": "dimmer, shadows lengthening",
                "sounds": ["fire popping", "wind howling outside", "building settling"]
            })
        elif self.current_time_of_day == "late_night":
            self.environment_state.update({
                "fire": "dying down to embers, glowing faintly",
                "lighting": "very dim, mostly darkness",
                "sounds": ["embers crackling softly", "silence", "distant owl hooting"]
            })
        elif self.current_time_of_day == "dawn":
            self.environment_state.update({
                "fire": "reduced to ashes with faint wisps of smoke",
                "lighting": "pale grey light filtering through windows",
                "sounds": ["birds chirping faintly", "castle waking up", "footsteps in distance"]
            })
        elif self.current_time_of_day == "morning":
            self.environment_state.update({
                "fire": "cold ashes in the hearth",
                "lighting": "bright morning sunlight streaming through windows",
                "sounds": ["students chattering", "footsteps", "breakfast smells wafting up"]
            })
    
    def detect_conversation_stagnation(
        self,
        silence_rounds: int,
        recent_messages: List[Message],
        player_name: str
    ) -> bool:
        """
        Detect if conversation has stagnated and needs narrative intervention.
        
        Args:
            silence_rounds: Number of consecutive rounds with no speakers
            recent_messages: Recent conversation messages
            player_name: Name of the player character
            
        Returns:
            True if narrator should intervene
        """
        # Intervene after 1 round of silence for environmental descriptions
        if silence_rounds >= 1:
            return True
        
        return False
    
    def generate_transition_narrative(
        self,
        current_scene: str,
        recent_messages: List[Message],
        silence_rounds: int,
        player_name: str
    ) -> str:
        """
        Generate a narrative transition to move the story forward.
        
        Args:
            current_scene: Current scene description
            recent_messages: Recent conversation messages
            silence_rounds: How many silent rounds
            player_name: Name of the player character
            
        Returns:
            Narrative transition text
        """
        try:
            # Update environment based on time (shorter intervals for environmental descriptions)
            time_change = self.advance_time(hours=0.5)  # Small time passage for environmental moments
            self.update_environment_for_time()
            
            # Build context from recent conversation
            conversation_summary = ""
            if recent_messages:
                last_few = recent_messages[-3:]
                conversation_summary = "\n".join([f"{msg.speaker}: {msg.content[:100]}" for msg in last_few])
            
            # Check if player is absent using the withdrawal detector
            from helpers.withdrawal_detector import WithdrawalDetector
            
            player_absent = False
            if recent_messages:
                last_msg = recent_messages[-1]
                # Check if the last message was from player with a leaving action
                if last_msg.speaker == player_name and last_msg.action_description:
                    # Use withdrawal detector to verify if this is actually a leaving action
                    detector = WithdrawalDetector()
                    is_leaving = detector.is_leaving_action(last_msg.action_description)
                    if is_leaving:
                        player_absent = True
            
            # Build history context to avoid repetition
            history_context = ""
            if self.previous_descriptions:
                recent_descs = self.previous_descriptions[-3:]  # Last 3 descriptions
                history_context = "\n\nPREVIOUS DESCRIPTIONS (DO NOT REPEAT THESE):\n" + "\n".join([f"- {desc[:100]}" for desc in recent_descs])
            
            prompt = f"""You are a narrator for an interactive Harry Potter roleplay story.

CURRENT ENVIRONMENT:
- Time of day: {self.current_time_of_day}
- Fire state: {self.environment_state['fire']}
- Lighting: {self.environment_state['lighting']}
- Location: Gryffindor Common Room
- Sounds: {', '.join(self.environment_state['sounds'])}
- Player ({player_name}) status: {"sleeping/resting" if player_absent else "present"}

RECENT CONVERSATION:
{conversation_summary}

CONTEXT:
A moment of silence has fallen. The conversation paused naturally.{history_context}

TASK:
Write a BRIEF environmental description (1-2 sentences) that:
1. Describes the CURRENT moment in the room (NOT time passage, NOT transitions)
2. Focuses on sensory details: fire crackling, shadows, warmth, sounds, atmosphere
3. Captures the mood and ambiance of THIS specific moment
4. Makes the scene feel alive and immersive
5. MUST be completely different from any previous descriptions above

CRITICAL RULES:
- DO NOT describe time passing or transitions
- DO NOT repeat details from previous descriptions
- Focus on NEW sensory details each time
- Vary your observations: if you described the fire before, now describe the windows, shadows, sounds, temperature, etc.
- Keep it brief: 1-2 sentences maximum
- Present tense, atmospheric, Harry Potter tone

EXAMPLES OF VARIETY:
- First time: "The fire crackles softly in the hearth, casting warm shadows across the room."
- Second time: "Outside, wind rattles the windows while the common room settles into comfortable quiet."
- Third time: "The scent of old parchment and wood smoke hangs in the air, familiar and soothing."
- Fourth time: "Portraits on the walls doze peacefully, their soft snores barely audible."

OUTPUT:
Just the environmental description, no quotes or labels. Write as the narrator.
"""
            
            model = self.get_or_create_model()
            response = model.generate_content(prompt)
            
            description = response.text.strip()
            
            # Store this description in history
            self.previous_descriptions.append(description)
            # Keep only last 5 descriptions
            if len(self.previous_descriptions) > 5:
                self.previous_descriptions.pop(0)
            
            return description
            
        except Exception as e:
            # Fallback to template-based transition
            return self._generate_fallback_transition(player_absent)
    
    def _generate_fallback_transition(self, player_sleeping: bool = False) -> str:
        """Generate a simple fallback transition if AI fails."""
        transitions = {
            "evening": "The evening deepens. The fire crackles lower, casting dancing shadows on the walls. The common room grows quieter as more students head to bed.",
            "night": "Hours pass. The fire burns down to glowing embers, its light dimming. The common room is silent now, save for the occasional pop of a coal and the wind outside.",
            "late_night": "The night wears on. The fire has nearly died, leaving only faint embers. Darkness fills the room, broken only by pale moonlight through the windows.",
            "dawn": "Dawn breaks. Grey light filters through the tall windows as the first birds begin to chirp. The fire is cold ashes now. A new day is beginning.",
            "morning": "Morning arrives in full. Bright sunlight streams through the windows, warming the room. The sounds of the castle waking up echo through the halls."
        }
        
        transition = transitions.get(self.current_time_of_day, transitions["evening"])
        
        if player_sleeping and self.current_time_of_day == "morning":
            transition += " It's time to wake up."
        
        return transition
    
    def generate_wakeup_event(
        self,
        player_name: str,
        other_characters: List[str]
    ) -> Optional[str]:
        """
        Generate a wakeup event when it's time to resume the story.
        
        Args:
            player_name: Name of sleeping player
            other_characters: Names of other characters present
            
        Returns:
            Description of wakeup event, or None
        """
        if self.current_time_of_day not in ["dawn", "morning"]:
            return None
        
        try:
            prompt = f"""You are narrating a Harry Potter story. {player_name} fell asleep in the common room last night. 
It's now {self.current_time_of_day}. 

Write a brief (1-2 sentences) description of {player_name} waking up naturally or being woken by one of their friends ({', '.join(other_characters)}).

Be specific about WHO wakes them and HOW (gentle shake, calling their name, etc.).
Write in present tense, vivid and atmospheric.
Just the narrative description, no character dialogue."""
            
            model = self.get_or_create_model()
            response = model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            # Fallback
            if other_characters:
                return f"Morning light wakes {player_name}. {other_characters[0]} is already awake, watching with concern."
            return f"{player_name} stirs awake as morning sunlight streams through the windows."
    
    def should_trigger_wakeup(self) -> bool:
        """Check if it's time to trigger a wakeup event."""
        return self.current_time_of_day in ["dawn", "morning"]
    
    def reset_time(self, time_of_day: str = "evening"):
        """Reset time to a specific point."""
        self.current_time_of_day = time_of_day
        self.environment_state["time_passed_hours"] = 0
        self.update_environment_for_time()
