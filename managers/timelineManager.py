"""
Timeline Manager for unified timeline event operations.
Combines message and scene management into a single chronological timeline.
"""

from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_models import Message, Scene, Action, TimelineHistory, TimelineEvent, CharacterEntry, CharacterExit
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
            if event.character not in timeline.participants:
                timeline.participants.append(event.character)
            if event.character not in timeline.current_participants:
                timeline.current_participants.append(event.character)

        elif isinstance(event, Action):
            if event.character not in timeline.participants:
                timeline.participants.append(event.character)
            if event.character not in timeline.current_participants:
                timeline.current_participants.append(event.character)
        
        elif isinstance(event, CharacterEntry):
            if event.character not in timeline.participants:
                timeline.participants.append(event.character)
            if event.character not in timeline.current_participants:
                timeline.current_participants.append(event.character)
        
        elif isinstance(event, CharacterExit):
            if event.character not in timeline.participants:
                timeline.participants.append(event.character)
            if event.character in timeline.current_participants:
                timeline.current_participants.remove(event.character)

    
    def get_recent_events(
        self, 
        timeline: TimelineHistory, 
        n: Optional[int] = 10,
        event_type: Optional[str] = None
    ) -> List[TimelineEvent]:
        """
        Get the n most recent events from timeline.
        
        Args:
            timeline: TimelineHistory instance to retrieve from
            n: Number of recent events, or None to get all events
            event_type: Optional filter - "message", "scene", "action", "entry", "exit" or None for all
            
        Returns:
            List of recent events
        """
        events = timeline.events
        
        # Filter by type if specified
        if event_type == "message":
            events = [e for e in events if isinstance(e, Message)]
        elif event_type == "scene":
            events = [e for e in events if isinstance(e, Scene)]
        elif event_type == "action":
            events = [e for e in events if isinstance(e, Action)]
        elif event_type == "entry":
            events = [e for e in events if isinstance(e, CharacterEntry)]
        elif event_type == "exit":
            events = [e for e in events if isinstance(e, CharacterExit)]
        
        # Return all events if n is None, otherwise return last n events
        if n is None:
            return events
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
    
    def get_timeline_context(self, timeline: TimelineHistory, recent_event_count: int = 10) -> str:
        """
        Build a formatted string representation of timeline events.
        
        Args:
            events: List of TimelineEvent instances to format
            
        Returns:
            Formatted timeline string with one event per line
        """
        timeline_context = []
        events = self.get_recent_events(timeline, n=recent_event_count)
        for event in events:
            if isinstance(event, Message):
                timeline_context.append(f"{event.character}: {event.dialouge}")
            elif isinstance(event, Scene):
                timeline_context.append(f"[SCENE at {event.location}] {event.description}")
            elif isinstance(event, Action):
                timeline_context.append(f"[ACTION] {event.character}: {event.description}")
            elif isinstance(event, CharacterEntry):
                timeline_context.append(f"[ENTERED] {event.character}: {event.description}")
            elif isinstance(event, CharacterExit):
                timeline_context.append(f"[LEFT] {event.character}: {event.description}")
        
        return "\n".join(timeline_context) if timeline_context else "No recent activity"
    
    # ========== Message Operations ==========
    
    def create_message(
        self, 
        character: str, 
        dialouge: str, 
        action_description: str
    ) -> Message:
        """
        Create a new message instance.
        
        Args:
            character: Name of the character speaking
            dialouge: Message dialouge
            action_description: Physical action or body language
            
        Returns:
            New Message instance
        """
        return Message(
            character=character, 
            dialouge=dialouge, 
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
            timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
            
            prompt = f"""You are generating a DRAMATIC SCENE EVENT for a Harry Potter roleplay story.
            - Characters Present: {', '.join(timeline.participants)}

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
        
    def should_generate_scene(self, timeline: TimelineHistory, recent_event_count: int = 15) -> Optional[dict]:
        """
        Use LLM to decide if a scene event should be generated and what it should be.
        
        Args:
            timeline: TimelineHistory instance
            recent_event_count: Number of recent events to include in context
            
        Returns:
            dict with 'scene_generated' (bool), 'location' (str), 'event_description' (str) if scene should be generated,
            None if no scene should be generated
        """
        timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
        prompt = f"""You are a narrative AI assistant for a Harry Potter roleplay story.
        Characters Present: {', '.join(timeline.participants)}
        RECENT TIMELINE (in chronological order):
        {timeline_str}

        YOUR TASK:
        Analyze the recent conversation flow and decide whether a DRAMATIC SCENE EVENT should be generated.

        GENERATE A SCENE EVENT IF:
        1. **Conversation has stalled** - Multiple silence rounds or repetitive exchanges
        2. **Natural transition point** - Topic concluded, awkward pause, characters seem stuck
        3. **Story needs momentum** - Tension is low, nothing interesting happening
        4. **Environmental interruption would enhance drama** - Perfect moment for something unexpected

        DO NOT GENERATE A SCENE IF:
        1. **Active conversation** - Characters are engaged and responding naturally
        2. **Recent scene event** - Already generated one in last 5-10 messages
        3. **Mid-dialogue** - Someone is in the middle of making an important point
        4. **Emotional moment** - Characters processing feelings, don't interrupt

        IF YOU DECIDE TO GENERATE A SCENE:
        Create a DRAMATIC ENVIRONMENTAL EVENT that:
        - **Interrupts the current state** with something happening in the environment
        - **Demands character attention** - they MUST notice and react
        - **Pushes story forward** - reveals clues, creates tension, advances plot
        - **Is completely different** from previous scene events above
        - **Is SPECIFIC and VIVID** with sensory details

        EVENT TYPES (choose dynamically based on context):
        - **Physical**: Wind blows, object falls, door slams, temperature changes, lightning flashes
        - **Discovery**: Hidden object revealed, clue appears, book falls open, secret passage opens
        - **Mysterious**: Strange sound, shadow moves, magic activates, whispers heard
        - **Danger**: Warning sign, threat appears, protective spell triggers, alarm sounds
        - **Character**: Someone enters, portrait speaks, ghost appears, owl arrives

        OUTPUT FORMAT (strict JSON):
        If scene should be generated:
        {{
            "scene_generated": true,
            "location": "The location where this event occurs (infer from most recent [SCENE at X] in timeline above)",
            "event_description": "2-3 sentence vivid description of what happens with sensory details"
        }}

        If no scene should be generated:
        {{
            "scene_generated": false
        }}

        Decide now based on the timeline above."""
        
        try:
            response = self.model.generate_content(
                prompt,
                temperature=0.8,
                max_tokens=300
            )
            
            scene_data = parse_json_response(response.text)
            
            if scene_data.get("scene_generated", False):
                return {
                    'scene_generated': True,
                    'location': scene_data.get('location'),
                    'event_description': scene_data.get('event_description')
                }
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  Error in scene generation decision: {e}")
            return None
    
        
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
        timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
        
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
        
    # ========== Charracter Entry/Exit Operations ==========

    def create_character_entry(
        self,
        character: str,
        description: str
    ) -> CharacterEntry:
        """
        Create a new character entry event.
        
        Args:
            character: Name of the character entering
            description: Description of how the character enters
            
        Returns:
            New CharacterEntry instance
        """
        entry = CharacterEntry(
            character=character,
            description=description
        )
        return entry
    
    def create_character_exit(
        self,
        character: str,
        description: str
    ) -> CharacterExit:
        """
        Create a new character exit event.
        
        Args:
            character: Name of the character leaving
            description: Description of how the character leaves
            
        Returns:
            New CharacterExit instance
        """
        exit_event = CharacterExit(
            character=character,
            description=description
        )
        return exit_event
    
    def generate_character_entry_event(
        self,
        character_name: str,
        timeline: TimelineHistory,
        recent_event_count: int = 10
    ) -> CharacterEntry:
        """
        Generate a character entry event based on recent context.
        
        Args:
            character_name: Name of the character entering
            timeline: TimelineHistory instance to consider
            recent_event_count: How many recent events to consider for context
            
        Returns:
            New CharacterEntry instance
        """
        timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
        current_location = self.get_current_location(timeline)
        
        prompt = f"""You are generating a CHARACTER ENTRY EVENT for {character_name} in a roleplay story.
        - Characters Currently Present: {', '.join(timeline.current_participants)}
        - Current Location: {current_location or "Unknown location"}

        RECENT TIMELINE (in chronological order):
        {timeline_str}

        SITUATION:
        {character_name} is about to enter the scene. Generate a vivid description of their entrance.

        ENTRY TYPES (choose based on context and character personality):
        - **Casual**: walks in, strolls over, steps through doorway
        - **Dramatic**: bursts in, sweeps into the room, appears suddenly
        - **Cautious**: peers around corner, enters hesitantly, slips in quietly
        - **Urgent**: rushes in, hurries through, comes running
        - **Mysterious**: materializes, emerges from shadows, appears without warning

        CRITICAL RULES:
        - Make it SPECIFIC and character-appropriate
        - Include sensory details (what others see/hear)
        - Should reflect the current mood/tension in timeline
        - Keep it concise (1-2 sentences)
        - Consider the location when describing entrance

        OUTPUT FORMAT (strict JSON):
        {{
            "entry_description": "Brief vivid description of how {character_name} enters"
        }}

        EXAMPLE:
        {{
            "entry_description": "pushed open the heavy oak door and stepped into the library, her footsteps echoing softly as she glanced around with curious eyes"
        }}"""
        
        try:
            response = self.model.generate_content(prompt, temperature=0.75)
            result = parse_json_response(response.text)
            entry_desc = result.get("entry_description", "").strip()
            
            return CharacterEntry(
                character=character_name,
                description=entry_desc
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate character entry event: {e}")
    
    def generate_character_exit_event(
        self,
        character_name: str,
        timeline: TimelineHistory,
        recent_event_count: int = 10
    ) -> CharacterExit:
        """
        Generate a character exit event based on recent context.
        
        Args:
            character_name: Name of the character leaving
            timeline: TimelineHistory instance to consider
            recent_event_count: How many recent events to consider for context
            
        Returns:
            New CharacterExit instance
        """
        timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
        current_location = self.get_current_location(timeline)
        
        prompt = f"""You are generating a CHARACTER EXIT EVENT for {character_name} in a roleplay story.
        - Characters Currently Present: {', '.join([p for p in timeline.current_participants if p != character_name])}
        - Current Location: {current_location or "Unknown location"}

        RECENT TIMELINE (in chronological order):
        {timeline_str}

        SITUATION:
        {character_name} is about to leave the scene. Generate a vivid description of their exit.

        EXIT TYPES (choose based on context and character personality):
        - **Casual**: walks out, heads for the door, leaves quietly
        - **Dramatic**: storms out, sweeps from the room, departs abruptly
        - **Reluctant**: hesitates then leaves, backs away slowly, exits with a glance back
        - **Urgent**: hurries out, rushes away, bolts from the room
        - **Mysterious**: fades away, disappears into shadows, vanishes quietly

        CRITICAL RULES:
        - Make it SPECIFIC and character-appropriate
        - Include sensory details (what others see/hear)
        - Should reflect the current mood/tension in timeline
        - Keep it concise (1-2 sentences)
        - Consider the location and recent events when describing exit

        OUTPUT FORMAT (strict JSON):
        {{
            "exit_description": "Brief vivid description of how {character_name} leaves"
        }}

        EXAMPLE:
        {{
            "exit_description": "gathered her books with a resigned sigh and headed for the door, footsteps fading down the corridor"
        }}"""
        
        try:
            response = self.model.generate_content(prompt, temperature=0.75)
            result = parse_json_response(response.text)
            exit_desc = result.get("exit_description", "").strip()
            
            return CharacterExit(
                character=character_name,
                description=exit_desc
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate character exit event: {e}")
    
    def should_generate_character_entry(
        self,
        character_name: str,
        timeline: TimelineHistory,
        recent_event_count: int = 15
    ) -> Optional[dict]:
        """
        Use LLM to decide if a character entry event should be generated.
        
        Args:
            character_name: Name of the character considering entry
            timeline: TimelineHistory instance
            recent_event_count: Number of recent events to include in context
            
        Returns:
            dict with 'entry_generated' (bool) and 'entry_description' (str) if entry should happen,
            None if character should not enter
        """
        timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
        current_location = self.get_current_location(timeline)
        
        prompt = f"""You are a narrative AI assistant for a roleplay story.
        Character in Question: {character_name}
        Characters Currently Present: {', '.join(timeline.current_participants)}
        Current Location: {current_location or "Unknown location"}
        
        RECENT TIMELINE (in chronological order):
        {timeline_str}

        YOUR TASK:
        Decide if {character_name} should ENTER the scene right now.

        GENERATE A CHARACTER ENTRY IF:
        1. **Natural story moment** - {character_name} would realistically arrive now
        2. **Story enhancement** - Their entrance would add interest or push plot forward
        3. **Character motivation** - They have a reason to be at this location now
        4. **Good timing** - Not interrupting a critical emotional moment
        5. **Location makes sense** - {character_name} would plausibly be near {current_location or "this location"}

        DO NOT GENERATE ENTRY IF:
        1. **Already present** - {character_name} is already in current_participants
        2. **Recently left** - They just exited in the last few events
        3. **Bad timing** - Would interrupt important dialogue or emotional beat
        4. **No story reason** - Random entrance with no narrative purpose
        5. **Location illogical** - Character wouldn't realistically be here

        IF YOU DECIDE {character_name} SHOULD ENTER:
        Create a VIVID ENTRANCE that:
        - Fits their personality and the current situation
        - Is SPECIFIC with sensory details
        - Reflects the current mood/tension
        - Gives other characters something to react to

        OUTPUT FORMAT (strict JSON):
        If character should enter:
        {{
            "entry_generated": true,
            "entry_description": "1-2 sentence vivid description of how {character_name} enters"
        }}

        If character should NOT enter:
        {{
            "entry_generated": false
        }}

        Decide now based on the timeline and story context above."""
        
        try:
            response = self.model.generate_content(
                prompt,
                temperature=0.8,
                max_tokens=300
            )
            
            entry_data = parse_json_response(response.text)
            
            if entry_data.get("entry_generated", False):
                return {
                    'entry_generated': True,
                    'entry_description': entry_data.get('entry_description')
                }
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  Error in character entry decision: {e}")
            return None
    
    def should_generate_character_exit(
        self,
        character_name: str,
        timeline: TimelineHistory,
        recent_event_count: int = 15
    ) -> Optional[dict]:
        """
        Use LLM to decide if a character exit event should be generated.
        
        Args:
            character_name: Name of the character considering exit
            timeline: TimelineHistory instance
            recent_event_count: Number of recent events to include in context
            
        Returns:
            dict with 'exit_generated' (bool) and 'exit_description' (str) if exit should happen,
            None if character should stay
        """
        timeline_str = self.get_timeline_context(timeline, recent_event_count=recent_event_count)
        current_location = self.get_current_location(timeline)
        
        prompt = f"""You are a narrative AI assistant for a roleplay story.
        Character in Question: {character_name}
        Characters Currently Present: {', '.join(timeline.current_participants)}
        Current Location: {current_location or "Unknown location"}
        
        RECENT TIMELINE (in chronological order):
        {timeline_str}

        YOUR TASK:
        Decide if {character_name} should LEAVE the scene right now.

        GENERATE A CHARACTER EXIT IF:
        1. **Natural departure point** - Conversation concluded, business finished
        2. **Character motivation** - {character_name} has a reason to leave (uncomfortable, bored, urgent business elsewhere)
        3. **Story enhancement** - Their exit would create dramatic effect or enable new dynamics
        4. **Been present long enough** - They've participated sufficiently
        5. **Organic timing** - Natural break in conversation or after their turn

        DO NOT GENERATE EXIT IF:
        1. **Not currently present** - {character_name} is not in current_participants
        2. **Mid-conversation** - Actively engaged in important dialogue
        3. **Just arrived** - Recently entered in the last few events
        4. **Story needs them** - Critical moment where their presence is essential
        5. **Awkward timing** - Would seem forced or unnatural

        IF YOU DECIDE {character_name} SHOULD LEAVE:
        Create a VIVID EXIT that:
        - Fits their personality and current emotional state
        - Is SPECIFIC with sensory details
        - Reflects the reason for leaving (casual, urgent, dramatic, reluctant)
        - Gives other characters something to react to

        OUTPUT FORMAT (strict JSON):
        If character should exit:
        {{
            "exit_generated": true,
            "exit_description": "1-2 sentence vivid description of how {character_name} leaves"
        }}

        If character should NOT exit:
        {{
            "exit_generated": false
        }}

        Decide now based on the timeline and story context above."""
        
        try:
            response = self.model.generate_content(
                prompt,
                temperature=0.8,
                max_tokens=300
            )
            
            exit_data = parse_json_response(response.text)
            
            if exit_data.get("exit_generated", False):
                return {
                    'exit_generated': True,
                    'exit_description': exit_data.get('exit_description')
                }
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  Error in character exit decision: {e}")
            return None
    
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
        
        timeline_str = self.get_timeline_context(timeline, recent_event_count=None)
        
        # Build context
        context_parts = []
        if timeline.title:
            context_parts.append(f"Title: {timeline.title}")
        
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
