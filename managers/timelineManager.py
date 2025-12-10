"""
Timeline Manager for unified timeline event operations.
Combines message and scene management into a single chronological timeline.
"""

from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_models import Message, Scene, Action, TimelineHistory, TimelineEvent
from config import Config
from openrouter_client import GenerativeModel
from helpers.response_parser import parse_json_response


class TimelineManager:
    """Manager for timeline operations including messages and scenes."""
    
    def __init__(self):
        """Initialize TimelineManager."""
        self.model_name = Config.DEFAULT_MODEL
        self.model = GenerativeModel(self.model_name)

    # ========== Timeline Operations ==========
    
    def create_timeline_history(
        self,
        title: Optional[str] = None,
        participants: Optional[List[str]] = None,
        visible_to_user: bool = True
    ) -> TimelineHistory:
        """
        Create a new timeline history.
        
        Args:
            title: Optional timeline title 
            participants: Optional initial participants list
            visible_to_user: Whether user can view this timeline (default True)
            
        Returns:
            New TimelineHistory instance
        """
        return TimelineHistory(
            title=title,
            participants=participants,
            visible_to_user=visible_to_user
        )
    
    def add_event(
        self,
        timeline: TimelineHistory,
        event: TimelineEvent
    ) -> None:
        """
        Add an event (Message or Scene) to the timeline.
        
        Args:
            timeline: TimelineHistory instance to add event to
            event: TimelineEvent instance to add (Message or Scene)
        """
        timeline.events.append(event)
        
        # If it's a message, update participants
        if isinstance(event, Message):
            if event.speaker not in timeline.participants:
                timeline.participants.append(event.speaker)

    
    def get_recent_events(
        self, 
        timeline: TimelineHistory, 
        n: int = 10,
        event_type: Optional[str] = None
    ) -> List[TimelineEvent]:
        """
        Get the n most recent events from timeline.
        
        Args:
            timeline: TimelineHistory instance to retrieve from
            n: Number of recent events
            event_type: Optional filter - "message", "scene", "Action" or None for all
            
        Returns:
            List of recent events
        """
        events = timeline.events
        
        # Early exit if no events
        if not events:
            return []
        
        # Filter by type if specified - use single pass
        if event_type == "message":
            events = [e for e in events if isinstance(e, Message)]
        elif event_type == "scene":
            events = [e for e in events if isinstance(e, Scene)]
        elif event_type == "Action":
            events = [e for e in events if isinstance(e, Action)]
        
        # Return last n events efficiently
        return events[-n:] if len(events) > n else events
    
    def get_current_location(self, timeline: TimelineHistory) -> Optional[str]:
        """
        Get the current location from the most recent Scene.
        
        Args:
            timeline: TimelineHistory instance
            
        Returns:
            Current location string or None
        """
        scenes = self.get_recent_events(timeline,n=1,event_type="scene")
        return scenes[0].location if scenes else None
    
    # ========== Message Operations ==========
    
    def create_message(
        self, 
        speaker: str, 
        content: str, 
        action_description: str
    ) -> Message:
        """
        Create a new message instance.
        
        Args:
            speaker: Name of the character speaking
            content: Message content
            action_description: Physical action or body language
            
        Returns:
            New Message instance
        """
        return Message(
            speaker=speaker, 
            content=content, 
            action_description=action_description
        )
    
    # ========== Scene Operations ==========
    
    def create_scene(
        self,
        location: str,
        description: str
    ) -> Scene:
        """
        Create a new scene event.
        
        Args:
            location: Where this scene event takes place
            description: What happens in this scene event
            
        Returns:
            New Scene instance
        """
        return Scene(
            location=location,
            description=description
        )
    
    def generate_scene_event(
        self,
        timeline: TimelineHistory,
        recent_event_count: int = 15
    ) -> Scene:
        """
        Generate a dramatic scene event when conversation stalls.
        Called EVERY time there's a silence round.
        
        Args:
            timeline: TimelineHistory instance
            recent_event_count: How many recent events to consider for context
            
        Returns:
            The newly created and added Scene
        """
        try:
            # Get recent events in chronological order
            recent_events = self.get_recent_events(timeline, n=recent_event_count)

            # Build chronological timeline context for LLM - use list for efficiency
            timeline_context = []
            for event in recent_events:
                if isinstance(event, Message):
                    # Truncate content to 80 chars for context efficiency
                    content = event.content[:80]
                    timeline_context.append(f"{event.speaker}: {content}")
                elif isinstance(event, Scene):
                    timeline_context.append(f"[SCENE at {event.location}] {event.description}")
                elif isinstance(event, Action):
                    timeline_context.append(f"[ACTION] {event.character}: {event.description}")
            
            timeline_str = "\n".join(timeline_context) if timeline_context else "No recent activity"
            participants_str = ', '.join(timeline.participants)
            
            prompt = f"""You are generating a DRAMATIC SCENE EVENT for a Harry Potter roleplay story.
            - Characters Present: {participants_str}

            RECENT TIMELINE (in chronological order):
            {timeline_str}

            SITUATION:
            The conversation has stalled. Silence has fallen. You need to generate a DRAMATIC ENVIRONMENTAL EVENT that:

            1. **Interrupts the silence** with something happening in the environment
            2. **Demands character attention** - they MUST notice and react
            3. **Pushes story forward** - reveals clues, creates new tension, or advances plot
            4. **Is completely different** from previous scene events above

            EVENT TYPES (choose dynamically):
            - **Physical**: Wind blows, object falls, door slams, temperature changes
            - **Discovery**: Hidden object revealed, clue appears, book falls open
            - **Mysterious**: Strange sound, shadow moves, magic activates
            - **Danger**: Warning sign, threat appears, protective spell triggers
            - **Character**: Someone enters, portrait speaks, ghost appears

            CRITICAL RULES:
            - Make it SPECIFIC and VIVID (not generic)
            - Include sensory details (what they see/hear/feel)
            - Event should naturally lead to new conversation
            - Must be something characters can react to
            - Vary the type of event - don't repeat patterns from the timeline above
            - Infer the current location from the most recent scene in the timeline above

            OUTPUT FORMAT (strict JSON):
            {{
            "location": "The location where this event occurs (infer from recent scenes)",
            "event_description": "2-3 sentence vivid description of what happens"
            }}

            EXAMPLE:
            {{
            "location": "Hogwarts Library",
            "event_description": "A sudden gust of ice-cold wind tears through the library, extinguishing half the torches. Pages flutter wildly as a single ancient book slides off a high shelf and crashes open on the table between them—landing on a page marked with a glowing symbol."
            }}"""
            
            response = self.model.generate_content(prompt, temperature=0.85)
            result = parse_json_response(response.text)
            location = result.get("location", "Unknown Location").strip()
            event_desc = result.get("event_description", "").strip()
            
            return Scene(
                location=location,
                description=event_desc
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate scene event: {e}")
        
    # ========= Action Operations ==========

    def create_action(
        self,
        character: str,
        description: str
    ) -> Action:
        """
        Create a new action instance.
        Args:
            character: Name of the character taking the action
            description: Details about the action taken

        Returns:
            New Action instance
        """
        action = Action(
            character=character,
            description=description
        )
        return action
    
    def generate_action_event(
        self,
        character_name: str,
        timeline: TimelineHistory,
        recent_event_count: int = 10
    ) -> Action:
        """
        Generate a silent character action (no dialogue) based on recent context.
        Used when a character wants to react physically without speaking.
        
        Args:
            character_name: Name of the character performing the action
            timeline: TimelineHistory instance to consider
            recent_event_count: How many recent events to consider for context

        Returns:
            New Action instance
        """
        recent_events = self.get_recent_events(timeline, n=recent_event_count)
        
        # Build chronological timeline context for LLM
        timeline_context = []
        for event in recent_events:
            if isinstance(event, Message):
                timeline_context.append(f"{event.speaker}: {event.content[:80]}")
            elif isinstance(event, Scene):
                timeline_context.append(f"[SCENE at {event.location}] {event.description}")
            elif isinstance(event, Action):
                timeline_context.append(f"[ACTION] {event.character}: {event.description}")
        
        timeline_str = "\n".join(timeline_context) if timeline_context else "No recent activity"
        
        prompt = f"""You are {character_name}. You are generating an ACTION for a roleplay story WITHOUT DIALOGUE. This is a silent, visible reaction to what's happening.
        - Other Characters Present: {', '.join([p for p in timeline.participants if p != character_name])}

        RECENT TIMELINE (in chronological order):
        {timeline_str}

        TASK:
        ACTION TYPES:
        - **Emotional reaction**: steps back, leans forward, narrows eyes, clenches fist
        - **Physical movement**: moves to window, picks up object, backs away, approaches
        - **Gesture**: nods, shakes head, points, waves hand dismissively
        - **Body language**: crosses arms, relaxes posture, tenses up, looks away
        CRITICAL RULES:
        - NO spoken words - only physical action
        - Make it specific and revealing of character's state
        - Should be a natural reaction to recent events
        - Keep it concise (1-2 sentences max)
        - Show emotion through body language
        - Infer the current location from the most recent scene in the timeline above
        OUTPUT FORMAT (strict JSON):
        {{
            "action_description": "Brief description of the physical action"
        }}
        EXAMPLE:
        {{
            "action_description": "took a step back, eyes widening in sudden realization"
        }}"""
        
        try:
            response = self.model.generate_content(prompt, temperature=0.75)
            result = parse_json_response(response.text)
            action_desc = result.get("action_description", "").strip()
            
            return Action(
                character=character_name,
                description=action_desc
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate action event: {e}")
    
    # ========== Summary Operations ==========
    
    def summarize_timeline(self, timeline: TimelineHistory) -> str:
        """
        Generate a brief AI-powered summary of the timeline.
        
        Args:
            timeline: TimelineHistory instance to summarize
            
        Returns:
            Summary string
        """
        if not timeline.events:
            return "No events to summarize."
        
        # Build timeline text for summarization - use list for efficiency
        timeline_text = []
        for event in timeline.events:
            if isinstance(event, Message):
                timeline_text.append(f"{event.speaker}: *{event.action_description}* {event.content}")
            elif isinstance(event, Scene):
                timeline_text.append(f"[SCENE at {event.location}] {event.description}")
            elif isinstance(event, Action):
                timeline_text.append(f"[ACTION] {event.character}: *{event.description}*")
        
        timeline_str = "\n".join(timeline_text)
        
        # Build context efficiently
        context_str = f"Title: {timeline.title}" if timeline.title else ""
        
        prompt = f"""You are summarizing a roleplay timeline between characters.
        {context_str}
        TIMELINE:
        {timeline_str}
        TASK: Generate a concise summary (2-4 sentences) of this timeline covering:
        - What the main topics discussed were
        - Any important scene events that occurred
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
            timeline.timeline_summary = summary
            return summary
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {e}")
