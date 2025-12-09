"""
Timeline Manager for unified timeline event operations.
Combines message and scene management into a single chronological timeline.
"""

from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_models import Message, Scene, TimelineHistory, TimelineEvent, Character
from config import Config
from openrouter_client import GenerativeModel
from helpers.response_parser import parse_json_response


class TimelineManager:
    """Manager for timeline operations including messages and scenes."""
    
    def __init__(self):
        """Initialize TimelineManager."""
        self.model = GenerativeModel(Config.DEFAULT_MODEL)

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
            title: Optional timeline title (e.g., 'Evening in Common Room')
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
    ) -> TimelineEvent:
        """
        Add an event (Message or Scene) to the timeline.
        
        Args:
            timeline: TimelineHistory instance to add event to
            event: TimelineEvent instance to add (Message or Scene)
            
        Returns:
            The added event
        """
        timeline.events.append(event)
        
        # If it's a message, update participants
        if isinstance(event, Message):
            if event.speaker not in timeline.participants:
                timeline.participants.append(event.speaker)
        
        return event
    
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
            event_type: Optional filter - "message", "scene", or None for all
            
        Returns:
            List of recent events
        """
        events = timeline.events
        
        # Filter by type if specified
        if event_type == "message":
            events = [e for e in events if isinstance(e, Message)]
        elif event_type == "scene":
            events = [e for e in events if isinstance(e, Scene)]
        
        return events[-n:] if len(events) > n else events
    
    def get_recent_messages(
        self, 
        timeline: TimelineHistory, 
        n: int = 10
    ) -> List[Message]:
        """
        Get the n most recent messages from timeline.
        
        Args:
            timeline: TimelineHistory instance
            n: Number of recent messages
            
        Returns:
            List of recent Message objects
        """
        messages = [e for e in timeline.events if isinstance(e, Message)]
        return messages[-n:] if len(messages) > n else messages
    
    def get_recent_scenes(
        self, 
        timeline: TimelineHistory, 
        n: int = 5
    ) -> List[Scene]:
        """
        Get the n most recent scenes from timeline.
        
        Args:
            timeline: TimelineHistory instance
            n: Number of recent scenes
            
        Returns:
            List of recent Scene objects
        """
        scenes = [e for e in timeline.events if isinstance(e, Scene)]
        return scenes[-n:] if len(scenes) > n else scenes
    
    def get_current_location(self, timeline: TimelineHistory) -> Optional[str]:
        """
        Get the current location from the most recent Scene.
        
        Args:
            timeline: TimelineHistory instance
            
        Returns:
            Current location string or None
        """
        scenes = self.get_recent_scenes(timeline, n=1)
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
    
    def add_message(
        self,
        timeline: TimelineHistory,
        message: Message,
    ) -> Message:
        """
        Create and add a message to the timeline in one step.
        
        Args:
            timeline: TimelineHistory instance
            speaker: Name of the character speaking
            content: Message content
            action_description: Physical action or body language
            
        Returns:
            The created and added Message
        """
        self.add_event(timeline, message)
        return message
    
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
    
    def add_scene(
        self,
        timeline: TimelineHistory,
        scene: Scene,
    ) -> Scene:
        """
        Create and add a scene to the timeline in one step.
        
        Args:
            timeline: TimelineHistory instance
            location: Where this scene event takes place
            description: What happens in this scene event
            
        Returns:
            The created and added Scene
        """
        self.add_event(timeline, scene)
        return scene
    
    def generate_scene_event(
        self,
        timeline: TimelineHistory,
        characters_present: List[str],
        recent_event_count: int = 15
    ) -> Scene:
        """
        Generate a dramatic scene event when conversation stalls.
        Called EVERY time there's a silence round.
        
        Args:
            timeline: TimelineHistory instance
            characters_present: Names of characters in the scene
            recent_event_count: How many recent events to consider for context
            
        Returns:
            The newly created and added Scene
        """
        try:
            # Get recent events in chronological order
            recent_events = self.get_recent_events(timeline, n=recent_event_count)
            
            # Get current location from most recent scene
            current_location = "Unknown Location"
            for event in reversed(recent_events):
                if isinstance(event, Scene):
                    current_location = event.location
                    break
            
            # Build chronological timeline context for LLM
            timeline_context = []
            for event in recent_events:
                if isinstance(event, Message):
                    timeline_context.append(f"{event.speaker}: {event.content[:80]}")
                elif isinstance(event, Scene):
                    timeline_context.append(f"[SCENE] {event.description}")
            
            timeline_str = "\n".join(timeline_context) if timeline_context else "No recent activity"
            
            # Get initial scene description (should be first event)
            initial_scene = timeline.events[0] if timeline.events and isinstance(timeline.events[0], Scene) else None
            initial_setting = initial_scene.description if initial_scene else "Standard scene"
            
            # Count scene events (excluding initial scene)
            scene_count = sum(1 for e in timeline.events[1:] if isinstance(e, Scene))
            
            prompt = f"""You are generating a DRAMATIC SCENE EVENT for a Harry Potter roleplay story.
            CURRENT SCENE:
            - Location: {current_location}
            - Initial Setting: {initial_setting}
            - Characters Present: {', '.join(characters_present)}
            - Scene Events So Far: {scene_count}

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

            OUTPUT FORMAT (strict JSON):
            {{
            "event_description": "2-3 sentence vivid description of what happens"
            }}

            EXAMPLE:
            {{
            "event_description": "A sudden gust of ice-cold wind tears through the library, extinguishing half the torches. Pages flutter wildly as a single ancient book slides off a high shelf and crashes open on the table between them—landing on a page marked with a glowing symbol."
            }}"""
            
            response = self.model.generate_content(prompt, temperature=0.85)
            result = parse_json_response(response.text)
            
            event_desc = result.get("event_description", "").strip()
            
            # Create and add the scene
            scene = self.add_scene(timeline, current_location, event_desc)
            
            return scene
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate scene event: {e}")
    
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
        
        # Build timeline text for summarization
        timeline_text = []
        for event in timeline.events:
            if isinstance(event, Message):
                timeline_text.append(f"{event.speaker}: *{event.action_description}* {event.content}")
            elif isinstance(event, Scene):
                timeline_text.append(f"[SCENE at {event.location}] {event.description}")
        
        timeline_str = "\n".join(timeline_text)
        
        # Build context
        context_parts = []
        if timeline.title:
            context_parts.append(f"Title: {timeline.title}")
        if timeline.events and isinstance(timeline.events[0], Scene):
            context_parts.append(f"Initial Scene: {timeline.events[0].description}")
        
        context_str = "\n".join(context_parts) if context_parts else ""
        
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
