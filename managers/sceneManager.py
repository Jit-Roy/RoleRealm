"""
Scene Manager for autonomous scene transitions and environmental storytelling.
Handles dynamic environment changes and narrative events.
"""

from typing import List, Optional, Dict, Any
from config import Config
from data_models import Message
from openrouter_client import GenerativeModel
from helpers.response_parser import parse_json_response


class SceneManager:
    """Manages narrative transitions and environmental storytelling with dynamic, LLM-generated content."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the Scene Manager.
        """
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.model = GenerativeModel(self.model_name)
        self.environment_history = []
        self.scene_context = {
            "location": "Gryffindor Common Room",
            "atmosphere": "warm and comfortable",
            "notable_features": ["fireplace", "armchairs", "portraits", "windows"]
        }
        self.conversation_rounds = 0  # Track conversation progression
    
    def update_scene_context(self, location: Optional[str] = None, atmosphere: Optional[str] = None):
        """
        Update scene context dynamically.
        
        Args:
            location: New location description
            atmosphere: New atmosphere description
        """
        if location:
            self.scene_context["location"] = location
        if atmosphere:
            self.scene_context["atmosphere"] = atmosphere
    
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
            True if scene should intervene
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
        Generate a dynamic narrative transition using LLM.
        
        Args:
            current_scene: Current scene description
            recent_messages: Recent conversation messages
            silence_rounds: How many silent rounds
            player_name: Name of the player character
            
        Returns:
            Narrative transition text
        """
        try:
            self.conversation_rounds += 1
            
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
                if last_msg.speaker == player_name and last_msg.action_description:
                    detector = WithdrawalDetector()
                    is_leaving = detector.is_leaving_action(last_msg.action_description)
                    if is_leaving:
                        player_absent = True
            
            # Build history context to avoid repetition
            history_context = ""
            if self.environment_history:
                recent_envs = self.environment_history[-3:]
                history_context = "\n\nPREVIOUS ENVIRONMENTAL DESCRIPTIONS (DO NOT REPEAT):\n" + "\n".join([f"- {desc[:100]}" for desc in recent_envs])
            
            prompt = f"""You are a narrator for an interactive Harry Potter roleplay story.

CURRENT SCENE CONTEXT:
- Location: {self.scene_context['location']}
- Atmosphere: {self.scene_context['atmosphere']}
- Conversation rounds: {self.conversation_rounds}
- Player ({player_name}) status: {"away/resting" if player_absent else "present"}

RECENT CONVERSATION:
{conversation_summary}

SITUATION:
A moment of silence has fallen. The conversation naturally paused.{history_context}

TASK:
Generate a BRIEF environmental description (1-2 sentences) that brings the scene to life.

The description should:
1. Focus on SENSORY DETAILS (sights, sounds, smells, textures, temperature)
2. Capture the MOOD and atmosphere of this specific moment
3. Be COMPLETELY DIFFERENT from any previous descriptions above
4. Vary what you observe each time (if you described fire before, now describe windows/portraits/sounds/smells/etc.)
5. Allow time to naturally progress through environmental cues (firelight dimming, shadows lengthening, sounds changing, etc.)
6. Be subtle and immersive - let the environment tell its own story

OUTPUT FORMAT (strict JSON):
{{
  "description": "Your 1-2 sentence environmental description",
  "time_progression": "subtle hint about time (e.g., 'time feels later', 'night deepening', 'hours passing', 'dawn approaching') or null if no time change"
}}

EXAMPLES OF VARIETY:
- "The fire crackles softly in the hearth, casting warm dancing shadows across the stone walls."
- "Outside, wind rattles the ancient windows while the common room settles into comfortable quiet."
- "The scent of old parchment and wood smoke hangs in the air, familiar and soothing."
- "Portraits on the walls doze peacefully, their soft snores barely audible in the stillness."
- "The fire has burned lower now, embers glowing faintly as darkness gathers in the corners of the room."

CRITICAL: 
- Present tense, atmospheric, Harry Potter tone
- Each description must observe something NEW
- Let time pass naturally through environmental details
- No quotes or labels in output"""
            
            response = self.model.generate_content(prompt, temperature=0.8)
            result = parse_json_response(response.text)
            
            description = result.get("description", "").strip()
            time_hint = result.get("time_progression")
            
            # Store in history
            self.environment_history.append(description)
            if len(self.environment_history) > 5:
                self.environment_history.pop(0)
            
            return description
            
        except Exception as e:
            # Fallback to simple atmospheric description
            return self._generate_fallback_description()
    
    def _generate_fallback_description(self) -> str:
        """Generate a simple fallback description if AI fails."""
        fallbacks = [
            "The fire crackles softly, filling the common room with warmth and flickering light.",
            "Shadows dance across the walls as the firelight flickers and shifts.",
            "The room settles into a comfortable quiet, broken only by the occasional pop of a coal in the hearth.",
            "Outside, wind whispers against the windows while the common room remains cozy and warm.",
            "The familiar scent of old books and wood smoke fills the air."
        ]
        import random
        return random.choice(fallbacks)
    
    def generate_scene_change(
        self,
        new_location: str,
        context: str,
        characters_present: List[str]
    ) -> str:
        """
        Generate a scene transition to a new location.
        
        Args:
            new_location: The new location to transition to
            context: Context about why the scene is changing
            characters_present: List of character names present
            
        Returns:
            Scene transition description
        """
        try:
            prompt = f"""You are narrating a Harry Potter story. Generate a brief scene transition.

TRANSITION:
- From: {self.scene_context['location']}
- To: {new_location}
- Characters: {', '.join(characters_present)}
- Context: {context}

Write a vivid 2-3 sentence description of the characters moving to the new location.
Include sensory details and atmosphere. Present tense, Harry Potter tone.

OUTPUT FORMAT (strict JSON):
{{
  "transition": "Your scene transition description"
}}"""
            
            response = self.model.generate_content(prompt, temperature=0.8)
            result = parse_json_response(response.text)
            
            transition = result.get("transition", "").strip()
            
            # Update scene context
            self.scene_context["location"] = new_location
            
            return transition
            
        except Exception as e:
            return f"The group makes their way to {new_location}."
