"""
Character loader module for loading character personas from JSON files.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from data_models import CharacterPersona


class CharacterLoader:
    """Load character personas from JSON files with caching."""
    
    def __init__(self, characters_dir: str = "characters"):
        """
        Initialize the character loader.
        
        Args:
            characters_dir: Directory containing character JSON files
        """
        self.characters_dir = Path(characters_dir)
        if not self.characters_dir.exists():
            raise ValueError(f"Characters directory not found: {self.characters_dir}")
        
        # Cache for loaded characters to avoid repeated file I/O
        self._character_cache: Dict[str, CharacterPersona] = {}
    
    def load_character(self, character_name: str, use_cache: bool = True) -> CharacterPersona:
        """
        Load a character persona from a JSON file.
        
        Args:
            character_name: Name of the character (without .json extension)
            use_cache: Whether to use cached version if available (default True)
            
        Returns:
            CharacterPersona instance
            
        Raises:
            FileNotFoundError: If character file doesn't exist
            ValueError: If JSON is invalid or missing required fields
        """
        # Check cache first if enabled
        cache_key = character_name.lower()
        if use_cache and cache_key in self._character_cache:
            return self._character_cache[cache_key]
        
        # Convert character name to lowercase for file lookup
        filename = f"{cache_key}.json"
        filepath = self.characters_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Character file not found: {filepath}\n"
                f"Available characters: {self.list_available_characters()}"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Create CharacterPersona
            persona = CharacterPersona(**character_data)
            
            # Cache the loaded character
            if use_cache:
                self._character_cache[cache_key] = persona
            
            return persona
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading character from {filepath}: {e}")
    
    def load_multiple_characters(self, character_names: list[str], use_cache: bool = True) -> list[CharacterPersona]:
        """
        Load multiple character personas from JSON files.
        
        Args:
            character_names: List of character names to load
            use_cache: Whether to use cached versions if available (default True)
            
        Returns:
            List of CharacterPersona instances
        """
        return [self.load_character(name, use_cache=use_cache) for name in character_names]
    
    def clear_cache(self) -> None:
        """Clear the character cache."""
        self._character_cache.clear()
    
    def list_available_characters(self) -> list[str]:
        """
        List all available character JSON files.
        
        Returns:
            List of character names (without .json extension)
        """
        character_files = self.characters_dir.glob("*.json")
        return [f.stem for f in character_files]
    
    def character_exists(self, character_name: str) -> bool:
        """
        Check if a character JSON file exists.
        
        Args:
            character_name: Name of the character to check
            
        Returns:
            True if character file exists, False otherwise
        """
        filename = f"{character_name.lower()}.json"
        filepath = self.characters_dir / filename
        return filepath.exists()


def load_character(character_name: str, characters_dir: str = "characters") -> CharacterPersona:
    """
    Convenience function to load a single character.
    
    Args:
        character_name: Name of the character to load
        characters_dir: Directory containing character JSON files
        
    Returns:
        CharacterPersona instance
    """
    loader = CharacterLoader(characters_dir)
    return loader.load_character(character_name)


def load_characters(character_names: list[str], characters_dir: str = "characters") -> list[CharacterPersona]:
    """
    Convenience function to load multiple characters.
    
    Args:
        character_names: List of character names to load
        characters_dir: Directory containing character JSON files
        
    Returns:
        List of CharacterPersona instances
    """
    loader = CharacterLoader(characters_dir)
    return loader.load_multiple_characters(character_names)
