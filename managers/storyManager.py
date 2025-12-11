"""
Manager for story progression and narrative flow.
"""

from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
import random
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_models import Story


class StoryManager:
    """Manager for story arc progression and narrative guidance."""
    
    def __init__(self, story: Optional[Story] = None):
        """
        Initialize StoryManager.
        
        Args:
            story: The story to manage
        """
        self.story = story
        self.messages_in_current_beat = 0
        self.last_event_at_message = 0
    
    def set_story_arc(self, story: Story) -> None:
        """Set the story arc."""
        self.story = story
    
    def get_current_beat(self) -> Optional[Dict[str, Any]]:
        """Get the current story beat."""
        if self.story and self.story.current_beat_index < len(self.story.beats):
            return self.story.beats[self.story.current_beat_index]
        return None
    
    def get_current_objectives(self) -> List[str]:
        """Get the objectives for the current beat."""
        beat = self.get_current_beat()
        if beat:
            return beat.get("objectives", [])
        return []
    
    def get_story_context(self) -> str:
        """Get the current story context for AI characters."""
        if not self.story:
            return "No story defined."
        
        beat = self.get_current_beat()
        if not beat:
            return "Story completed!"
        
        context = f"""
CURRENT STORY CONTEXT:
Story: {self.story.title}
Current Beat: {beat.get('title', 'Unknown')}
Location: {beat.get('location', 'Unspecified')}

WHAT'S HAPPENING NOW:
{beat.get('description', '')}

CURRENT OBJECTIVES:
{chr(10).join(f"- {obj}" for obj in beat.get('objectives', []))}

STORY GUIDANCE:
- Keep the conversation moving toward these objectives
- Characters should naturally work toward accomplishing the goals
- Stay true to your personality while advancing the plot
- React to the current situation and motivate action when needed
"""
        return context
    
    def check_beat_completion(self, conversation_summary: str) -> bool:
        """
        Check if the current beat's objectives have been met.
        This is a simple implementation - you can enhance with AI analysis.
        
        Args:
            conversation_summary: Summary of recent conversation
            
        Returns:
            True if beat should be advanced
        """
        beat = self.get_current_beat()
        trigger_conditions = beat.get("trigger_conditions", []) if beat else []
        if not beat or not trigger_conditions:
            return False
        
        # Use OpenRouter API to intelligently check if objectives are being met
        try:
            from config import Config
            from openrouter_client import GenerativeModel
            
            model = GenerativeModel(Config.DEFAULT_MODEL)
            
            objectives = beat.get("objectives", [])
            objectives_text = "\n".join([f"- {obj}" for obj in objectives])
            
            prompt = f"""Analyze if the conversation is meeting the story beat objectives.

CURRENT STORY BEAT: {beat.get('title', 'Unknown')}

OBJECTIVES:
{objectives_text}

RECENT CONVERSATION SUMMARY:
{conversation_summary}

Have the objectives been substantially addressed in the conversation? Consider:
1. Are the key topics being discussed?
2. Have characters engaged with the main themes?
3. Is there meaningful progress toward the objectives?

Respond with ONLY:
- 'YES' if objectives are being met and story can progress
- 'NO' if more conversation is needed
- 'PARTIAL' if some but not all objectives are addressed"""
            
            response = model.generate_content(prompt)
            decision = response.text.strip().upper()
            
            # Progress if YES or PARTIAL (give flexibility)
            return 'YES' in decision or 'PARTIAL' in decision
            
        except Exception as e:
            # Fallback to simple keyword matching if AI fails
            print(f"   ⚠️ Beat completion check failed, using fallback: {e}")
            summary_lower = conversation_summary.lower()
            conditions_met = sum(
                1 for condition in trigger_conditions
                if condition.lower() in summary_lower
            )
            return conditions_met >= len(trigger_conditions) / 2
    
    def advance_story(self) -> bool:
        """
        Advance to the next story beat.
        
        Returns:
            True if advanced successfully, False if at end
        """
        if self.story:
            result = self.advance_beat()
            # Reset message count for new beat
            self.messages_in_current_beat = 0
            self.last_event_at_message = 0
            return result
        return False
    
    def get_progress_summary(self) -> str:
        """Get a summary of story progress."""
        if not self.story:
            return "No story active."
        
        beat = self.get_current_beat()
        progress = self.story.get_progress_percentage()
        
        return f"""
📖 Story Progress: {progress:.1f}%
📍 Current: {beat.get('title', 'Unknown') if beat else 'Completed'}
🎯 Beat {self.story.current_beat_index + 1} of {len(self.story.beats)}
"""
    
    def display_beat_transition(self, new_beat: Dict[str, Any]) -> None:
        """Display a transition message when moving to a new beat."""
        print("\n" + "="*70)
        print("📖 STORY PROGRESSION")
        print("="*70)
        print(f"\n🎬 New Chapter: {new_beat.get('title', 'Unknown')}")
        print(f"📍 Location: {new_beat.get('location', 'Unknown')}")
        print(f"\n{new_beat.get('description', '')}")
        print("\n🎯 Objectives:")
        for obj in new_beat.get('objectives', []):
            print(f"   • {obj}")
        print("\n" + "="*70 + "\n")
    
    def display_scene_description(self, scene_text: str) -> None:
        """Display a rich, atmospheric scene description."""
        print("\n" + "═"*70)
        print("🌟 SCENE 🌟")
        print("═"*70)
        print()
        # Wrap text nicely
        import textwrap
        wrapped = textwrap.fill(scene_text, width=68)
        print(textwrap.indent(wrapped, "  "))
        print()
        print("═"*70 + "\n")
    
    def display_story_event(self, event: Dict[str, Any]) -> None:
        """Display a dynamic story event happening."""
        print("\n" + "✨"*35)
        print(f"⚡ EVENT: {event.get('title', 'Unknown Event')} ⚡")
        print("✨"*35)
        print()
        import textwrap
        wrapped = textwrap.fill(event.get('description', ''), width=68)
        print(textwrap.indent(wrapped, "  "))
        print()
        print("✨"*35 + "\n")
    
    def check_for_story_event(self, silence_duration: int = 0, message_count: int = 0, recent_messages: list = None) -> Optional[Dict[str, Any]]:
        """
        Check if a story event should trigger based on context.
        
        Args:
            silence_duration: How many turns since last player input (higher = more likely to trigger)
            message_count: Total message count for trigger timing
            recent_messages: Recent messages to analyze context
            
        Returns:
            Event dict if one should trigger, None otherwise
        """
        if not self.story:
            return None
        
        # Use provided message_count or fall back to internal counter
        current_count = message_count if message_count > 0 else self.messages_in_current_beat
        
        # Check if enough messages have passed since last event
        messages_since_last_event = current_count - self.last_event_at_message
        if messages_since_last_event < 5:  # Minimum 5 messages between events for better pacing
            return None
        
        # Analyze recent context using AI to avoid awkward timing
        if recent_messages and len(recent_messages) > 0:
            # Build context including both Messages and Scenes in chronological order
            from data_models import Message, Scene
            context_lines = []
            
            for event in recent_messages[-3:]:
                if isinstance(event, Message):
                    context_lines.append(f"{event.character}: {event.dialouge}")
                elif isinstance(event, Scene):
                    context_lines.append(f"[SCENE at {event.location}]: {event.description}")
            
            if context_lines:
                context = "\n".join(context_lines)
            
                # Use OpenRouter to determine if timing is appropriate
                try:
                    from config import Config
                    from openrouter_client import GenerativeModel
                    
                    model = GenerativeModel(Config.DEFAULT_MODEL)
                    
                    prompt = f"""Analyze this conversation context and determine if NOW is a good time for a dramatic story event to occur.

RECENT CONVERSATION:
{context}

A dramatic event could be: a sudden danger, mysterious occurrence, or unexpected interruption.

Consider:
1. Is someone in the middle of making a request or asking for something?
2. Is the conversation at a natural transition point (going to sleep, leaving, etc.)?
3. Are characters about to take an action that would be interrupted awkwardly?
4. Is there an unresolved question or request that needs answering first?
5. Are characters saying goodnight or going to sleep? (If yes, answer NO)
6. Has someone just withdrawn or left? (If yes, answer NO)
7. Is the conversation wrapping up naturally? (If yes, answer NO)

CRITICAL: If people are going to sleep, saying goodnight, or the conversation is ending, answer NO.

Respond with ONLY 'YES' if timing is good for an event, or 'NO' if it would be awkward/inappropriate."""
                    
                    response = model.generate_content(prompt)
                    decision = response.text.strip().upper()
                    
                    if 'NO' in decision:
                        return None  # Wait for better timing
                except Exception as e:
                    # Fallback: if AI fails, be conservative and don't trigger
                    print(f"   ⚠️ Event timing check failed: {e}")
                    return None
        
        # Get available events
        available_events = self.get_available_events(current_count)
        
        if not available_events:
            return None
        
        # Events should be rare and impactful, not constant
        # Lower base chance, only increase with long silence
        base_chance = 0.15  # Reduced from 0.2
        silence_bonus = 0.0
        
        # Only boost chance if player has been quiet for a while (3+ turns)
        if silence_duration >= 3:
            silence_bonus = min((silence_duration - 2) * 0.12, 0.35)
        
        trigger_chance = base_chance + silence_bonus
        
        if random.random() < trigger_chance:
            # Events are already sorted by priority
            selected_event = available_events[0]
            # Mark as triggered
            self.trigger_event(selected_event.get("id"))
            self.last_event_at_message = current_count
            return selected_event
        
        return None
    
    def increment_message_count(self) -> None:
        """Increment the message counter for the current beat."""
        self.messages_in_current_beat += 1
    
    def advance_beat(self) -> bool:
        """Move to the next beat. Returns True if advanced, False if at end."""
        if not self.story:
            return False
        
        if self.story.current_beat_index < len(self.story.beats) - 1:
            self.story.beats[self.story.current_beat_index]["completed"] = True
            self.story.current_beat_index += 1
            return True
        else:
            if self.story.beats:
                self.story.beats[self.story.current_beat_index]["completed"] = True
            self.story.completed = True
            return False
    
    def get_progress_percentage(self) -> float:
        """Get the percentage of story completion."""
        if not self.story or not self.story.beats:
            return 0.0
        return (self.story.current_beat_index / len(self.story.beats)) * 100
    
    def get_available_events(self, message_count: int) -> List[Dict[str, Any]]:
        """Get events that can trigger based on message count and priority."""
        available = []
        
        # Check current beat events
        current_beat = self.get_current_beat()
        if current_beat and "events" in current_beat:
            for event in current_beat["events"]:
                if not event.get("triggered", False):
                    trigger_after = event.get("trigger_after_messages")
                    if trigger_after is None or message_count >= trigger_after:
                        available.append(event)
        
        # Sort by priority (descending)
        available.sort(key=lambda e: e.get("priority", 0.5), reverse=True)
        return available
    
    def trigger_event(self, event_id: str) -> bool:
        """Mark an event as triggered. Returns True if found and triggered."""
        if not self.story:
            return False
        
        # Check all beat events
        for beat in self.story.beats:
            if "events" in beat:
                for event in beat["events"]:
                    if event.get("id") == event_id:
                        event["triggered"] = True
                        return True
        
        return False