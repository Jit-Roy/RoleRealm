"""
Story loader module for loading story configurations from JSON files.
"""

import json
from pathlib import Path
import uuid
from typing import Dict
from data_models import Story


class StoryLoader:
    """Load story configurations from JSON files with caching."""
    
    def __init__(self, stories_dir: str = "stories"):
        """
        Initialize the story loader.
        
        Args:
            stories_dir: Directory containing story JSON files
        """
        self.stories_dir = Path(stories_dir)
        if not self.stories_dir.exists():
            raise ValueError(f"Stories directory not found: {self.stories_dir}")
        
        # Cache for loaded stories to avoid repeated file I/O
        self._story_cache: Dict[str, Story] = {}
    
    def load_story(self, story_name: str, use_cache: bool = True) -> Story:
        """
        Load a story from a JSON file.
        
        Args:
            story_name: Name of the story file (without .json extension)
            use_cache: Whether to use cached version if available (default True)
            
        Returns:
            Story instance
            
        Raises:
            FileNotFoundError: If story file doesn't exist
            ValueError: If JSON is invalid or missing required fields
        """
        # Check cache first if enabled
        cache_key = story_name.lower()
        if use_cache and cache_key in self._story_cache:
            return self._story_cache[cache_key]
        
        # Convert story name to lowercase for file lookup
        filename = f"{cache_key}.json"
        filepath = self.stories_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Story file not found: {filepath}\n"
                f"Available stories: {self.list_available_stories()}"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                story_data = json.load(f)
            
            # Process beats to add IDs and default values
            beats = story_data.get("beats", [])
            processed_beats = []
            
            for beat in beats:
                # Add beat ID if not present
                if "id" not in beat:
                    beat["id"] = str(uuid.uuid4())
                
                # Add completed flag if not present
                if "completed" not in beat:
                    beat["completed"] = False
                
                # Process events within the beat
                events = beat.get("events", [])
                processed_events = []
                
                for event in events:
                    # Add event ID if not present
                    if "id" not in event:
                        event["id"] = str(uuid.uuid4())
                    
                    # Add triggered flag if not present
                    if "triggered" not in event:
                        event["triggered"] = False
                    
                    processed_events.append(event)
                
                beat["events"] = processed_events
                processed_beats.append(beat)
            
            story_data["beats"] = processed_beats
            
            # Create Story
            story = Story(**story_data)
            
            # Cache the loaded story
            if use_cache:
                self._story_cache[cache_key] = story
            
            return story
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading story from {filepath}: {e}")
    
    def clear_cache(self) -> None:
        """Clear the story cache."""
        self._story_cache.clear()
    
    def list_available_stories(self) -> list[str]:
        """
        List all available story JSON files.
        
        Returns:
            List of story names (without .json extension)
        """
        story_files = self.stories_dir.glob("*.json")
        return [f.stem for f in story_files]
    
    def story_exists(self, story_name: str) -> bool:
        """
        Check if a story JSON file exists.
        
        Args:
            story_name: Name of the story to check
            
        Returns:
            True if story file exists, False otherwise
        """
        filename = f"{story_name.lower()}.json"
        filepath = self.stories_dir / filename
        return filepath.exists()
    
    def get_story_info(self, story_name: str) -> dict:
        """
        Get basic information about a story without fully loading it.
        
        Args:
            story_name: Name of the story to get info about
            
        Returns:
            Dictionary with title and description
        """
        filename = f"{story_name.lower()}.json"
        filepath = self.stories_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Story file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                story_data = json.load(f)
            
            return {
                "title": story_data.get("title", "Unknown"),
                "description": story_data.get("description", "No description"),
                "num_beats": len(story_data.get("beats", []))
            }
        except Exception as e:
            raise ValueError(f"Error reading story info from {filepath}: {e}")


def load_story(story_name: str, stories_dir: str = "stories") -> Story:
    """
    Convenience function to load a single story.
    
    Args:
        story_name: Name of the story to load
        stories_dir: Directory containing story JSON files
        
    Returns:
        Story instance
    """
    loader = StoryLoader(stories_dir)
    return loader.load_story(story_name)


def list_stories(stories_dir: str = "stories") -> list[str]:
    """
    Convenience function to list available stories.
    
    Args:
        stories_dir: Directory containing story JSON files
        
    Returns:
        List of available story names
    """
    loader = StoryLoader(stories_dir)
    return loader.list_available_stories()
