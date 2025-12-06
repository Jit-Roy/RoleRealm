"""
Main entry point for the RoleRealm multi-character roleplay system.
An AI-powered interactive storytelling experience with dynamic conversations.
"""

import time
from roleplay_system import RoleplaySystem
from config import Config
from managers.storyManager import StoryManager
from character_loader import load_characters
from story_loader import load_story


def setup_scene(system: RoleplaySystem, title: str, location: str, description: str) -> None:
    """Set up the initial scene for the roleplay."""
    system.scene_manager.update_title(title)
    system.scene_manager.update_location(location)
    system.scene_manager.update_plot(description)
    
    print("\n" + "="*70)
    print(f"🎬 SCENE: {title.upper()}")
    print("="*70)
    print(f"\n📍 Location: {system.scene_manager.location}")
    print(f"\n📖 Setting:")
    print(f"   {system.scene_manager.plot}")
    print("\n" + "="*70 + "\n")


def display_welcome(player_name: str, character_names: list):
    """Display the welcome message for the roleplay session."""
    char_list = " and ".join(character_names)
    welcome = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                      🎭 ROLEREALM SYSTEM 🎭                         ║
║                                                                      ║
║                  Interactive AI-Powered Roleplay                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

You are playing as {player_name.upper()}, joined by {char_list}.

The conversation will flow naturally - AI characters will respond when they
have something to say, creating an organic, dynamic storytelling experience!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📜 COMMANDS:
   • Just type naturally to speak as {player_name}
   • 'listen' - Stay quiet and let AI characters continue talking
   • 'skip' - Prompt AI characters to continue the conversation
   • 'next' - Advance to the next story beat (when ready)
   • 'progress' - Check current story progress and objectives
   • 'info' - See character details
   • 'quit' or 'exit' - End the session and save the conversation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(welcome)


def main():
    """Main entry point for the roleplay system."""
    
    # Configuration - Customize these for your roleplay
    PLAYER_NAME = "Harry"
    CHARACTER_FILES = ["hermione", "ron"]  # Names of JSON files in characters/ folder
    STORY_FILE = "complete_journey"  # Name of JSON file in stories/ folder
    SCENE_TITLE = "Evening in the Common Room"
    SCENE_LOCATION = "Gryffindor Common Room, Hogwarts"
    SCENE_DESCRIPTION = (
        "It's evening in the Gryffindor common room. The fire crackles in the hearth, "
        "casting warm shadows on the scarlet and gold tapestries. Most students have "
        "gone to bed, but the group remains in their favorite armchairs near the fireplace. "
        "The atmosphere is relaxed - perfect for a chat between friends."
    )
    INITIAL_GREETING = "Hey, it's good to see you both. How's everyone doing?"
    
    # Load story from JSON
    print("\n📖 Loading Story...")
    try:
        story_arc = load_story(STORY_FILE)
        print(f"   ✓ Loaded: {story_arc.title}\n")
    except Exception as e:
        print(f"❌ Error loading story: {e}")
        print("Using default story configuration...")
        try:
            story_arc = load_story("evening_with_friends")
        except:
            print("❌ Could not load any story. Continuing without story progression.")
            story_arc = None
    
    # Create story manager
    story_manager = StoryManager(story_arc) if story_arc else None
    
    # Load character personas from JSON
    print("\n🔮 Loading characters...")
    try:
        characters = load_characters(CHARACTER_FILES)
        for char in characters:
            print(f"✨ {char.name} has joined")
        print()
    except Exception as e:
        print(f"❌ Error loading characters: {e}")
        print("Please make sure character JSON files exist in the 'characters' folder.")
        return
    
    # Display welcome message
    character_names = [char.name for char in characters]
    display_welcome(PLAYER_NAME, character_names)
    
    # Initialize the roleplay system
    try:
        system = RoleplaySystem(
            player_name=PLAYER_NAME,
            characters=characters,
            model_name=Config.DEFAULT_MODEL,
            story_manager=story_manager
        )
        
        # Setup the scene
        setup_scene(system, SCENE_TITLE, SCENE_LOCATION, SCENE_DESCRIPTION)
        
        # Display initial story beat with full scene description
        if story_manager:
            current_beat = story_manager.get_current_beat()
            if current_beat:
                story_manager.display_beat_transition(current_beat)
                if current_beat.get("scene_description"):
                    story_manager.display_scene_description(current_beat["scene_description"])
        
        # Start the roleplay session
        print("🎬 Starting the conversation...\n")
        print("="*70)
        
        # Send initial greeting
        print(f"\n💬 {PLAYER_NAME}: {INITIAL_GREETING}")
        system._add_player_message(INITIAL_GREETING)
        
        # Let AI characters respond
        ai_responses = system.turn_manager.process_ai_responses()
        
        # Main conversation loop
        message_count_at_beat_start = 0
        player_messages_count = 0
        
        while True:
            try:
                # Story progression logic (only if story manager exists)
                if story_manager:
                    current_beat = story_manager.get_current_beat()
                    current_message_count = len(system.scene.messages)
                    messages_in_beat = current_message_count - message_count_at_beat_start
                    story_manager.messages_in_current_beat = messages_in_beat
                    
                    # Check for story events periodically
                    if player_messages_count > 0 and player_messages_count % 3 == 0:
                        event = story_manager.check_for_story_event(silence_duration=2)
                        if event:
                            story_manager.display_story_event(event)
                            event_msg = system.message_manager.create_message(
                                speaker="Narrator",
                                content=f"[Event: {event.title}] {event.description}"
                            )
                            system.message_manager.add_message(system.scene, event_msg)
                    
                    # Check if we can advance story
                    can_advance = False
                    if current_beat and messages_in_beat >= current_beat.get("min_messages", 10):
                        recent_messages = system.scene.messages[-15:]
                        summary = " ".join([msg.content for msg in recent_messages])
                        if story_manager.check_beat_completion(summary):
                            can_advance = True
                else:
                    can_advance = False
                
                # Get player input
                print("\n" + "─"*70)
                prompt_parts = [f"⚡ {PLAYER_NAME}"]
                if can_advance:
                    prompt_parts.append(" [Story ready to advance - type 'next']")
                prompt_parts.append(": ")
                user_input = input("".join(prompt_parts)).strip()
                
                # Track player messages
                if user_input and user_input.lower() not in ['listen', 'skip', 'next', 'progress', 'info', 'quit', 'exit']:
                    player_messages_count += 1
                
                # Handle player withdrawal (sleeping, leaving, etc.)
                withdrawal_keywords = ['sleep', 'sleeping', 'asleep', 'went to sleep', 'going to sleep', 
                                      'leave', 'leaving', 'left', 'went away', 'going away']
                player_withdrawn = any(keyword in user_input.lower() for keyword in withdrawal_keywords)
                
                if player_withdrawn:
                    print(f"\n💤 {PLAYER_NAME} has withdrawn from the conversation...")
                    print("🗣️  The AI characters continue talking...\n")
                    system._add_player_message(user_input)
                    
                    # Let AI characters talk for several turns
                    for _ in range(3):
                        ai_responses = system.turn_manager.process_ai_responses(max_turns=2)
                        if not ai_responses:
                            break
                        time.sleep(1)
                    
                    print("\n" + "─"*70)
                    print("💬 (The conversation quiets down. Type 'listen' to hear more, or speak to rejoin)")
                    continue
                
                # Handle story advancement command
                if user_input.lower() in ['next', 'advance', 'continue story']:
                    if story_manager:
                        if can_advance:
                            advanced = story_manager.advance_story()
                            if advanced:
                                message_count_at_beat_start = current_message_count
                                player_messages_count = 0
                                new_beat = story_manager.get_current_beat()
                                if new_beat:
                                    story_manager.display_beat_transition(new_beat)
                                    if new_beat.get("scene_description"):
                                        story_manager.display_scene_description(new_beat["scene_description"])
                            else:
                                print("\n" + "="*70)
                                print("🎉 STORY COMPLETED!")
                                print("="*70)
                                print(f"\nYou've completed: {story_arc.title}")
                                print("The adventure concludes here... for now.")
                                print("="*70 + "\n")
                        else:
                            current_beat = story_manager.get_current_beat()
                            min_needed = current_beat.get("min_messages", 10) if current_beat else 10
                            remaining = max(0, min_needed - messages_in_beat)
                            print(f"\n⏳ The story isn't quite ready to advance yet.")
                            print(f"   Continue the conversation ({remaining} more messages recommended)")
                            print(f"   and work toward the current objectives.\n")
                    else:
                        print("\n⚠️  No story loaded - cannot advance.")
                    continue
                
                # Handle progress command
                if user_input.lower() == 'progress':
                    if story_manager:
                        print(story_manager.get_progress_summary())
                        beat = story_manager.get_current_beat()
                        if beat:
                            print("🎯 Current Objectives:")
                            for obj in beat.get("objectives", []):
                                print(f"   • {obj}")
                            print(f"\n📊 Messages in this beat: {messages_in_beat}/{beat.get('min_messages', 10)} minimum")
                    else:
                        print("\n⚠️  No story loaded.")
                    continue
                
                # Handle listen command
                if user_input.lower() == 'listen':
                    print(f"\n👂 {PLAYER_NAME} listens quietly as the conversation continues...")
                    ai_responses = system.turn_manager.process_ai_responses(max_turns=5)
                    if not ai_responses:
                        print(f"\n💤 The conversation naturally pauses. Everyone seems to be waiting for {PLAYER_NAME} to say something.")
                    continue
                
                # Handle normal input
                should_continue = system._handle_player_input(user_input)
                if not should_continue:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted! Ending roleplay...")
                print(f"💾 Chat saved to: {system.get_conversation_file_path()}")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                print("Please try again or type 'quit' to exit.")
        
        # Display session statistics
        stats = system.get_statistics()
        print("\n" + "="*70)
        print("📊 SESSION STATISTICS")
        print("="*70)
        print(f"Total messages exchanged: {stats['total_messages']}")
        print(f"Participants: {', '.join(stats['ai_characters'] + [stats['player_name']])}")
        print(f"💾 Conversation saved to: {system.get_conversation_file_path()}")
        print("="*70)
        print("\n✨ Thanks for using RoleRealm! Until next time! 🎭\n")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease make sure you have set up your GEMINI_API_KEY in a .env file.")
        print("Example .env file content:")
        print("  GEMINI_API_KEY=your_api_key_here")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
