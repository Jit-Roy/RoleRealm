from typing import List, Optional, Dict, Any, Tuple
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_models import CharacterPersona, Message, Character, CharacterMemory, CharacterState, TimelineEvent, Scene, Action
from config import Config
from openrouter_client import GenerativeModel
from helpers.response_parser import parse_json_response


class CharacterManager:
    """Manager for character-related operations."""
    
    def __init__(self):
        """Initialize CharacterManager."""
        self.model_name = Config.DEFAULT_MODEL
        self.model = GenerativeModel(self.model_name)
    
    def create_character(
        self, 
        persona: CharacterPersona, 
        memory: Optional[CharacterMemory] = None,
        state: Optional[CharacterState] = None
    ) -> Character:
        """
        Create a new AI character instance.
        
        Args:
            persona: CharacterPersona defining the character
            memory: Optional character memory
            state: Optional character state
            
        Returns:
            New Character instance
        """
        if memory is None:
            memory = CharacterMemory(name=persona.name)
        if state is None:
            state = CharacterState(name=persona.name)
        
        return Character(persona=persona, memory=memory, state=state)
    
    def update_character_memory(
        self,
        character: Character,
        timeline_memory: TimelineEvent
    ) -> None:
        """
        Update character's memory by adding timeline event.
        
        Args:
            character: The Character to update
            timeline_memory: The TimelineEvent to add to memory
        """
            
        if timeline_memory is not None:
            character.memory.timeline_memory.append(timeline_memory)
    
    def update_character_state(
        self,
        character: Character,
        mood: Optional[str] = None,
        focus: Optional[str] = None,
        current_action: Optional[str] = None,
        is_silent: Optional[bool] = None
    ) -> None:
        """
        Update character's current state (mood, focus, action, silence).
        
        Args:
            character: The Character to update
            mood: Update character's mood
            focus: Update character's focus
            current_action: Update character's current action
            is_silent: Update whether character is deliberately silent
        """
        if mood is not None:
            character.state.mood = mood
        if focus is not None:
            character.state.focus = focus
        if current_action is not None:
            character.state.current_action = current_action
        if is_silent is not None:
            character.state.is_silent = is_silent
        
    
    def build_persona_context(self, character: Character) -> str:
        """Build the character's personality context including traits, relationships, goals, and knowledge."""
        # Use list for efficient string building
        parts = [
            f"You are {character.persona.name}.",
            "        YOUR PERSONALITY:",
            f"        - Traits: {', '.join(character.persona.traits)}",
            f"        - Speaking Style: {character.persona.speaking_style}",
            f"        - Background: {character.persona.background}",
            "        YOUR RELATIONSHIPS:"
        ]
        
        # Add relationships
        parts.extend(f"        - {char}: {rel}" for char, rel in character.persona.relationships.items())
        
        # Add goals if available
        if character.persona.goals:
            parts.append("\n        YOUR GOALS & MOTIVATIONS:")
            parts.extend(f"        - {goal}" for goal in character.persona.goals)
        
        # Add knowledge base if available
        if character.persona.knowledge_base:
            parts.append("\n        YOUR SPECIAL KNOWLEDGE:")
            parts.extend(f"        - {key}: {value}" for key, value in character.persona.knowledge_base.items())
        
        return "\n".join(parts)
    
    def build_state_context(self, character: Character) -> str:
        """Build the character's current state context including mood, focus, and action."""
        if not character.state:
            return ""
        
        context = f"\n\nYOUR CURRENT STATE:\n- Mood: {character.state.mood}"
        if character.state.focus:
            context += f"\n- Focus: {character.state.focus}"
        if character.state.current_action:
            context += f"\n- Current Action: {character.state.current_action}"
        
        return context
    
    def build_memory_context(self, character: Character, last_n_messages: Optional[int] = None) -> str:
        """Build the memory context string with actions noted from character's perceived messages.
        
        Args:
            character: The Character whose memory to build context from
            last_n_messages: Optional number of recent messages to include. If None, includes all messages.
        
        Returns:
            Formatted memory context string
        """
        if not character.memory or not character.memory.timeline_memory:
            return ""
        
        events = character.memory.timeline_memory
        if last_n_messages is not None and len(events) > last_n_messages:
            events = events[-last_n_messages:]
        
        # Pre-allocate list with estimated size for better performance
        context_lines = []
        char_name = character.persona.name
        
        for event in events:
            if isinstance(event, Message):
                prefix = "You" if event.speaker == char_name else event.speaker
                context_lines.append(f"{prefix}: *{event.action_description}* {event.content}")
            elif isinstance(event, Scene):
                context_lines.append(f"[Scene at {event.location}]: {event.description}")
            elif isinstance(event, Action):
                prefix = "You" if event.character == char_name else event.character
                context_lines.append(f"{prefix}: *{event.description}*")
        
        return "\n".join(context_lines)
    
    def build_decision_prompt(
        self, 
        character: Character,
        story_context: Optional[str] = None
    ) -> str:
        """
        Build the prompt for deciding whether to speak FROM THIS CHARACTER'S PERSPECTIVE.
        Each character sees the conversation through their own lens.
        
        Args:
            character: The AICharacter making the decision
            story_context: Optional story context to guide the narrative
            
        Returns:
            The complete prompt string 
        """ 

        persona_context = self.build_persona_context(character)
        state_context = self.build_state_context(character)
        memory_context = self.build_memory_context(character)
        
        # Add story context if provided
        story_section = ""
        if story_context:
            story_section = f"\n{story_context}\n"
        
        prompt = f"""{persona_context}{state_context}
        {story_section}
        WHAT YOU EXPERIENCED (your perspective):
        {memory_context}
        DECISION:
        Based on YOUR experiences, YOUR traits, and YOUR current state, decide how you want to respond right now.
        
        THREE OPTIONS:
        1. **SPEAK** - Respond with dialogue (and accompanying action)
        2. **ACT** - React physically/emotionally WITHOUT speaking (silent action)
        3. **SILENT** - Do nothing, stay quiet
        
        WHEN TO SPEAK (high priority):
        1. **Someone greets the group or asks how everyone is doing** - It's natural to respond as friends!
        2. **Someone reveals important/concerning information** - React with your authentic concern!
        3. **You're directly addressed or mentioned** - Respond naturally!
        4. **There's been awkward silence** - Someone should break it!
        5. **The topic is highly relevant to YOU** - Share your unique perspective!
        6. **Someone needs help or support** - Friends respond to friends!
        
        WHEN TO ACT (medium priority):
        - You want to react but words feel forced or unnecessary
        - Showing emotion through body language is more powerful than speaking
        - High tension moment where silence + action is more dramatic
        - You're uncomfortable/unsure and just want to show physical reaction
        - Someone said something shocking and you need a moment to process
        - Physical reaction conveys your feeling better than words would

        WHEN TO STAY SILENT (stay quiet):
        - You JUST spoke in the last message (let others respond first)
        - Someone else already said exactly what you'd say
        - You've made the same point 2-3+ times already (don't be repetitive!)
        - **If others already reacted to danger/concern, you don't need to pile on with the SAME reaction**
        - Someone clearly wants to end a topic and you'd just push it again
        - Another character is better suited to respond to this specific topic
        - The conversation doesn't involve you and you have nothing unique to add
        - **Multiple people already said similar things - don't be the third person saying the same thing**

        SPECIAL SITUATIONS:
        - **RESPECT BOUNDARIES**: If someone has stated their position, accept it or change approach
        - **REACT TO DANGER/CONCERN**: If friend mentions pain/danger/threat, respond with concern ONLY if you have something UNIQUE to add beyond what others said
        - **WITHDRAWAL CONTEXT**: If someone needs rest after revealing something serious, acknowledge both parts
        - **DON'T GANG UP**: If another character already made your exact point, DON'T repeat it - offer a DIFFERENT suggestion or stay quiet
        - **BE INDEPENDENT**: Have your own opinions - don't just echo what others said with slightly different words
        - **NATURAL FLOW**: Sometimes "Alright, if you say so" or changing subjects IS the right move
        - **CHECK WHAT OTHERS SAID**: Look at the last 2-3 messages. If they already covered your concern, you don't need to repeat it

        OUTPUT FORMAT (strict JSON):
        {{
        "response_type": "speak" or "act" or "silent",
        "wants_to_speak": true or false (true if response_type is "speak", false otherwise),
        "priority": 0.0 to 1.0 (how urgent/important is your response),
        "reasoning": "brief explanation of your decision",
        "action_description": "physical actions/body language - REQUIRED for 'act' type, optional for 'speak' type",
        "message": "your actual dialogue if response_type is 'speak', otherwise null"
        }}

        IMPORTANT:
        - For "speak": Include BOTH action_description AND message
        - For "act": Only action_description (silent physical reaction), message should be null
        - For "silent": Both action_description and message should be null

        **CRITICAL - ACTION VARIETY RULES (READ THIS CAREFULLY):**
        1. **CHECK THE CONVERSATION ABOVE** - Look at your previous messages. What actions did you ALREADY do?
        2. **NEVER REPEAT ACTIONS** - If you already "leaned forward", "sat back", "crossed arms", "looked at someone" - DON'T DO IT AGAIN
        3. **PHYSICAL CONSISTENCY** - If you already sat down or leaned back, you can't lean back AGAIN. Instead: stand up, walk somewhere, gesture differently, adjust position, look away, etc.
        4. **VARIETY IS MANDATORY** - Each of your actions MUST be different from all your previous actions in this conversation
        5. **EXAMPLES OF VARIETY**:
        - First message: "leans back against sofa"
        - Second message: "sits forward suddenly" or "stands up" or "runs hand through hair"
        - Third message: "paces to the window" or "fidgets with wand" or "slumps in chair"
        - NEVER: "leans back" again after already doing it!

        - Stay COMPLETELY IN CHARACTER with your unique speaking style
        - Don't repeat what others just said - add something NEW or DON'T SPEAK
        - Keep messages realistic for casual conversation
        - If you have nothing unique to add, set wants_to_speak to false
        - Your personality should be OBVIOUS from how you speak and act
        - Don't sound like you're giving a lecture or writing an essay
        - Use natural dialogue, contractions, and emotion
        - Show, don't tell - use actions to convey mood and personality
        - **INDEPENDENCE**: Have your own opinions - don't just support what others said
        - **BACKING OFF**: Sometimes "Alright, fair enough" or "Suit yourself" is the perfect response
        - **RESPECTING AUTONOMY**: If someone clearly doesn't want to talk about something, that's OKAY
        - **NATURAL FLOW**: Not every topic needs resolution. Sometimes you just move on.
        - **REACT TO DANGER/CONCERN**: If your friend mentions pain, danger, or a threat - REACT! Even if they want to sleep after.
        """
        return prompt
    
    def decide_to_speak(
        self, 
        character: Character,
        story_context: Optional[str] = None
    ) -> Tuple[str, bool, float, str, Optional[str], Optional[str]]:
        """
        Decide whether this character should speak, act silently, or stay silent.
        Each character uses different generation settings for unique voices.
        
        Args:
            character: The Character making the decision
            story_context: Optional story context to guide responses
            
        Returns:
            Tuple of (response_type, wants_to_speak, priority, reasoning, action_description, message)
            - response_type: "speak", "act", or "silent"
            - wants_to_speak: True if response_type is "speak", False otherwise
            - priority: 0.0 to 1.0
            - reasoning: Explanation of decision
            - action_description: Physical action (required for "act", optional for "speak")
            - message: Dialogue (only for "speak", None otherwise)
        """
        
        try:
            # Build prompt from THIS character's perspective
            prompt = self.build_decision_prompt(character, story_context)
            
            # Generate with character's unique settings
            response = self.model.generate_content(
                prompt, 
                temperature=character.persona.temperature, 
                top_p=character.persona.top_p, 
                frequency_penalty=character.persona.frequency_penalty
            )
            
            # Parse JSON response
            decision_data = parse_json_response(response.text)
            
            response_type = decision_data.get("response_type", "silent").lower()
            wants_to_speak = response_type == "speak"
            
            return (
                response_type,
                wants_to_speak,
                decision_data.get("priority", 0.0),
                decision_data.get("reasoning", "No reasoning provided"),
                decision_data.get("action_description", None),
                decision_data.get("message", None)
            )
            
        except json.JSONDecodeError as e:
            raise e
        except Exception as e:
            raise e
    
    def broadcast_event_to_characters(self, characters: List[Character], event: TimelineEvent) -> None:
        """
        Add a TimelineEvent to all characters' events.
        This simulates all characters hearing/experiencing the event.
        
        Args:
            characters: List of all characters present
            event: The event being broadcasted
        """
        for character in characters:
            self.update_character_memory(character, timeline_memory=event)