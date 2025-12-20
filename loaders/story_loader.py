"""
Story loader module for loading story configurations from JSON files.
"""

import json
from pathlib import Path
import uuid
from data_models import Story


class StoryLoader:
    """Load story configurations from JSON files."""
    
    def __init__(self, stories_dir: str):
        """
        Initialize the story loader.
        
        Args:
            stories_dir: Directory containing story JSON files (required)
        """
        if not stories_dir:
            raise ValueError("stories_dir is required and cannot be None or empty")
        self.stories_dir = Path(stories_dir)
        if not self.stories_dir.exists():
            raise ValueError(f"Stories directory not found: {self.stories_dir}")
    
    def load_story(self, story_name: str) -> Story:
        """
        Load a story from a JSON file.
        
        Args:
            story_name: Name of the story file (without .json extension)
            
        Returns:
            Story instance
            
        Raises:
            FileNotFoundError: If story file doesn't exist
            ValueError: If JSON is invalid or missing required fields
        """
        # Convert story name to lowercase for file lookup
        filename = f"{story_name.lower()}.json"
        filepath = self.stories_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Story file not found: {filepath}\n"
                f"Available stories: {self.list_available_stories()}"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                story_data = json.load(f)
            
            # No beat processing needed - just load the story with objectives
            # Ensure current_objective_index exists
            if "current_objective_index" not in story_data:
                story_data["current_objective_index"] = 0
            
            # Create and return Story
            return Story(**story_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading story from {filepath}: {e}")
    
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


def load_story(story_name: str, stories_dir: str) -> Story:
    """
    Convenience function to load a single story.
    
    Args:
        story_name: Name of the story to load
        stories_dir: Directory containing story JSON files (required)
        
    Returns:
        Story instance
    """
    loader = StoryLoader(stories_dir)
    return loader.load_story(story_name)


def list_stories(stories_dir: str) -> list[str]:
    """
    Convenience function to list available stories.
    
    Args:
        stories_dir: Directory containing story JSON files (required)
        
    Returns:
        List of available story names
    """
    loader = StoryLoader(stories_dir)
    return loader.list_available_stories()
