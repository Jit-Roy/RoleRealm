"""
Manager for story progression and narrative flow with sequential objective system.
"""

from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
import json
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_models import Story, Character, TimelineEvent
from config import Config
from openrouter_client import GenerativeModel


class StoryManager:
    """Manager for sequential story objectives and character objective assignment."""
    
    def __init__(self, story: Optional[Story] = None):
        """
        Initialize StoryManager.
        
        Args:
            story: The story to manage
        """
        self.story = story
        self.model = GenerativeModel(Config.DEFAULT_MODEL)
    
    def set_story_arc(self, story: Story) -> None:
        """Set the story arc."""
        self.story = story
    
    def get_current_objective(self) -> Optional[str]:
        """Get the current story objective."""
        if self.story and self.story.current_objective_index < len(self.story.objectives):
            return self.story.objectives[self.story.current_objective_index]
        return None
    
    def is_story_complete(self) -> bool:
        """Check if all story objectives are complete."""
        if not self.story:
            return True
        return self.story.current_objective_index >= len(self.story.objectives)
    
    def get_progress_percentage(self) -> float:
        """Get the percentage of story completion."""
        if not self.story or len(self.story.objectives) == 0:
            return 100.0
        return (self.story.current_objective_index / len(self.story.objectives)) * 100
    
    def get_story_context(self) -> str:
        """Get the current story context for AI characters."""
        if not self.story:
            return "No story defined."
        
        current_objective = self.get_current_objective()
        if not current_objective:
            return "Story completed! All objectives achieved."
        
        progress = self.get_progress_percentage()
        
        context = f"""
        STORY: {self.story.title}
        Progress: {progress:.0f}% ({self.story.current_objective_index + 1} of {len(self.story.objectives)} objectives)

        CURRENT STORY OBJECTIVE:
        {current_objective}

        OVERALL STORY CONTEXT:
        {self.story.description}

        Remember: Work naturally toward accomplishing the current objective through your character's unique perspective and abilities.
        """
        return context
    
    def assign_initial_objectives(
        self,
        active_characters: List[Character],
        timeline_context: str
    ) -> Dict[str, str]:
        """
        Assign initial character objectives at story start or when objective advances.
        
        Args:
            active_characters: List of currently active characters
            timeline_context: Recent timeline context
            
        Returns:
            Dictionary mapping character names to their new objectives
        """
        if not self.story or self.is_story_complete():
            return {char.persona.name: None for char in active_characters}
        
        current_objective = self.get_current_objective()
        
        # Build character descriptions
        char_descriptions = []
        for char in active_characters:
            traits = ", ".join(char.persona.traits)
            char_descriptions.append(
                f"- {char.persona.name}: {traits}. Speaking style: {char.persona.speaking_style}"
            )
        
        prompt = f"""You are assigning objectives to characters in an interactive roleplay story.
        STORY: {self.story.title}
        {self.story.description}
        CURRENT STORY OBJECTIVE (what needs to be achieved):
        {current_objective}
        ACTIVE CHARACTERS:
        {chr(10).join(char_descriptions)}
        RECENT CONTEXT:
        {timeline_context}
        TASK: Assign ONE specific objective to EACH character that helps achieve the current story objective.

        Guidelines:
        - Make objectives specific enough to guide the character, but flexible enough to allow creativity
        - Consider each character's unique abilities and personality
        - Objectives should be complementary (characters working together from different angles)
        - Objectives should be achievable through conversation/action in 3-10 turns
        - Don't assign the exact same objective to multiple characters

        Respond ONLY with valid JSON in this format:
        {{
        "character_objectives": {{
            "CharacterName1": "specific objective for this character",
            "CharacterName2": "specific objective for this character"
        }}
        }}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result.get("character_objectives", {})
            
        except Exception as e:
            print(f"⚠️ Error assigning initial objectives: {e}")
            # Fallback: generic objectives
            return {
                char.persona.name: f"Help achieve: {current_objective}"
                for char in active_characters
            }
    
    def evaluate_and_assign_objectives(
        self,
        active_characters: List[Character],
        recent_timeline_events: List[TimelineEvent]
    ) -> Dict[str, Any]:
        """
        Unified LLM call that handles both initial assignment and ongoing evaluation.
        
        If characters don't have objectives (first turn or after story advances):
            - Assigns initial objectives
        
        If characters have objectives:
            - Evaluates completion
            - Assigns new objectives to those who completed
            - Checks story objective completion
        
        Args:
            active_characters: List of currently active characters
            recent_timeline_events: Recent timeline events for context
            
        Returns:
            Dictionary with evaluation results:
            {
                "character_updates": {
                    "CharacterName": {
                        "objective": "current or new objective",
                        "status": "assigned|completed|continuing",
                        "reasoning": "explanation"
                    }
                },
                "story_objective_complete": bool,
                "reasoning": "story completion reasoning"
            }
        """
        if not self.story or self.is_story_complete():
            return {
                "character_updates": {},
                "story_objective_complete": True,
                "reasoning": "Story is complete"
            }
        
        current_story_objective = self.get_current_objective()
        
        # Check if this is first turn (characters have no objectives)
        is_first_turn = all(
            not char.state.current_objective 
            for char in active_characters
        )
        
        # Build timeline summary
        timeline_summary = []
        for event in recent_timeline_events[-15:]:
            if hasattr(event, 'character') and hasattr(event, 'dialouge'):
                timeline_summary.append(f"{event.character}: {event.dialouge}")
            elif hasattr(event, 'character') and hasattr(event, 'description') and hasattr(event, '__class__'):
                event_type = event.__class__.__name__
                if event_type == "Action":
                    timeline_summary.append(f"[ACTION] {event.character}: {event.description}")
                elif event_type == "CharacterEntry":
                    timeline_summary.append(f"[ENTRY] {event.character} entered: {event.description}")
                elif event_type == "CharacterExit":
                    timeline_summary.append(f"[EXIT] {event.character} left: {event.description}")
                elif event_type == "Scene":
                    timeline_summary.append(f"[SCENE at {event.location}]: {event.description}")
        
        timeline_text = "\n".join(timeline_summary) if timeline_summary else "No recent events"
        
        # Build character info
        char_info = []
        for char in active_characters:
            traits = ", ".join(char.persona.traits)
            current_obj = char.state.current_objective if char.state.current_objective else "None"
            char_info.append(
                f"- {char.persona.name}: Traits: {traits}. Current Objective: {current_obj}"
            )
        
        char_info_text = "\n".join(char_info)
        
        if is_first_turn:
            # First turn: Assign initial objectives
            prompt = f"""You are assigning objectives to characters in an interactive roleplay story.

STORY: {self.story.title}
{self.story.description}

CURRENT STORY OBJECTIVE (what needs to be achieved):
{current_story_objective}

ACTIVE CHARACTERS:
{char_info_text}

RECENT CONTEXT:
{timeline_text}

TASK: Assign ONE specific objective to EACH character that helps achieve the current story objective.

Guidelines:
- Make objectives specific but flexible
- Consider each character's unique abilities and personality
- Objectives should complement each other
- Achievable through conversation/action in 3-10 turns

Respond ONLY with valid JSON:
{{
  "character_updates": {{
    "CharacterName1": {{
      "objective": "specific objective for this character",
      "status": "assigned",
      "reasoning": "why this objective fits them"
    }}
  }},
  "story_objective_complete": false,
  "reasoning": "Story just started, objective not yet complete"
}}"""
        else:
            # Ongoing: Evaluate and reassign
            prompt = f"""You are evaluating story progression in an interactive roleplay.

CURRENT STORY OBJECTIVE (Overall goal):
{current_story_objective}

ACTIVE CHARACTERS AND CURRENT OBJECTIVES:
{char_info_text}

RECENT CONVERSATION (Last 15 events):
{timeline_text}

EVALUATE AND UPDATE:

1. For EACH character:
   - If objective completed: Provide NEW objective toward current story goal, status="completed"
   - If ongoing: Keep same objective, status="continuing"

2. For STORY OBJECTIVE:
   - Is it achieved? (Even if some character objectives incomplete)

Respond ONLY with valid JSON:
{{
  "character_updates": {{
    "CharacterName1": {{
      "objective": "new objective if completed, otherwise same as current",
      "status": "completed|continuing",
      "reasoning": "brief explanation"
    }}
  }},
  "story_objective_complete": true/false,
  "reasoning": "story objective status explanation"
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            print(f"⚠️ Error in objective evaluation: {e}")
            # Fallback
            fallback_updates = {}
            for char in active_characters:
                if is_first_turn:
                    fallback_updates[char.persona.name] = {
                        "objective": f"Help achieve: {current_story_objective}",
                        "status": "assigned",
                        "reasoning": "Fallback objective"
                    }
                else:
                    fallback_updates[char.persona.name] = {
                        "objective": char.state.current_objective or f"Help achieve: {current_story_objective}",
                        "status": "continuing",
                        "reasoning": "Evaluation error"
                    }
            
            return {
                "character_updates": fallback_updates,
                "story_objective_complete": False,
                "reasoning": f"Error during evaluation: {e}"
            }
    
    def advance_story_objective(self) -> bool:
        """
        Advance to the next story objective.
        
        Returns:
            True if advanced successfully, False if story is complete
        """
        if not self.story:
            return False
        
        if self.story.current_objective_index < len(self.story.objectives) - 1:
            self.story.current_objective_index += 1
            return True
        else:
            # Story complete
            self.story.current_objective_index = len(self.story.objectives)
            return False
    
    def get_progress_summary(self) -> str:
        """Get a summary of story progress."""
        if not self.story:
            return "No story active."
        
        if self.is_story_complete():
            return f"""
            📖 Story Complete: {self.story.title}
            ✅ All {len(self.story.objectives)} objectives achieved!
            """
        
        current_objective = self.get_current_objective()
        progress = self.get_progress_percentage()
        
        return f"""
        📖 Story: {self.story.title}
        📊 Progress: {progress:.0f}% 
        🎯 Objective {self.story.current_objective_index + 1} of {len(self.story.objectives)}
        "{current_objective}"
        """