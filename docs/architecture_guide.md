# RoleRealm Architecture Documentation

## Table of Contents
- [Overview](#overview)
- [Core Architecture](#core-architecture)
- [Data Models](#data-models)
- [System Managers](#system-managers)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)

## Overview

RoleRealm is an AI-powered interactive roleplay system built with Python that enables dynamic multi-character conversations with story progression. The architecture follows a modular design with clear separation of concerns between data models, managers, and loaders.

### Key Features
- **Multi-character AI conversations** - Each character has unique personalities, memories, and objectives
- **Timeline-based event system** - Unified chronological tracking of messages, scenes, and actions
- **Dynamic story progression** - Objective-based narrative flow with automatic character goal assignment
- **Persistent state management** - Automatic saving and loading of conversation history
- **Parallel processing** - Concurrent character decision-making for natural conversations

## Core Architecture
### Layer Architecture

**Layer 1: Data Models** (`data_models.py`)
- Pure Pydantic models defining data structures
- No business logic
- Validation and type safety

**Layer 2: Loaders** (`loaders/`)
- File I/O operations
- JSON parsing and validation
- Creating model instances from files

**Layer 3: Managers** (`managers/`)
- Business logic for specific domains
- State management
- LLM interactions

**Layer 4: System Coordinator** (`roleplay_system.py`, `main.py`)
- Orchestrates all components
- User interaction
- Session lifecycle

## Data Models

All data models are defined using Pydantic for type safety and validation.

### Timeline Event Hierarchy

```python
TimelineEvent (Base Class)
│
├── Message          # Character dialogue with actions
├── Scene            # Environmental/narrative events
├── Action           # Character physical actions
├── CharacterEntry   # Character joins conversation
└── CharacterExit    # Character leaves conversation
```

### Core Models

#### TimelineEvent (Base)
```python
class TimelineEvent(BaseModel):
    timeline_id: str          # Unique identifier
    timestamp: datetime       # When event occurred
```

Every event in the system inherits from `TimelineEvent`, ensuring all timeline entries have consistent tracking.

#### Message
```python
class Message(TimelineEvent):
    character: str            # Speaker name
    dialouge: str            # What they say
    action_description: str  # Body language/actions
```

Represents spoken dialogue with accompanying physical actions. The character sees this through their own perspective in memory.

#### Scene
```python
class Scene(TimelineEvent):
    scene_type: str          # 'transition' or 'environmental'
    location: str            # Where it happens
    description: str         # What happens
```

Environmental or transitional narrative events that affect all characters present.

#### Character
```python
class Character(BaseModel):
    persona: CharacterPersona    # Personality, traits, relationships
    memory: CharacterMemory      # What they've witnessed
    state: CharacterState        # Current objective, condition
```

Complete representation of an AI character with three aspects:
- **Persona**: Immutable personality traits and background
- **Memory**: Growing list of witnessed events
- **State**: Mutable current condition and objectives

#### CharacterPersona
```python
class CharacterPersona(BaseModel):
    name: str
    traits: List[str]                      # Personality traits
    relationships: Dict[str, str]          # Character → relationship
    speaking_style: str                    # How they speak
    background: str                        # History/context
    goals: Optional[List[str]]             # Long-term motivations
    knowledge_base: Optional[Dict]         # Special information
    temperature: Optional[float]           # LLM creativity (0.75)
    top_p: Optional[float]                 # Sampling parameter (0.9)
    frequency_penalty: Optional[float]     # Repetition control (0.2)
```

Defines the immutable personality and characteristics of a character.

#### CharacterMemory
```python
class CharacterMemory(BaseModel):
    name: str
    event: List[TimelineEvent]  # Events this character witnessed
```

Each character has their **own perspective** - they only remember events they were present for.

#### TimelineHistory
```python
class TimelineHistory(BaseModel):
    id: str
    title: Optional[str]
    events: List[TimelineEvent]           # Chronological events
    participants: List[str]               # All who participated
    current_participants: List[str]       # Currently present
    timeline_summary: Optional[str]
    visible_to_user: bool
```

Master timeline containing all events in chronological order.

#### Story
```python
class Story(BaseModel):
    id: str
    title: str
    description: str
    objectives: List[str]                 # Sequential objectives
    current_objective_index: int         # Progress tracker
```

Story structure with sequential objectives that guide narrative progression.

## System Managers

### TurnManager

**Purpose**: Coordinates conversation flow and determines who speaks next.

**Key Methods**:
- `process_ai_responses()`: Main conversation loop
  - Collects decisions from all characters in parallel
  - Selects highest priority speaker
  - Handles consecutive AI turns
  - Triggers meta-narrative events

- `_collect_speaking_decisions()`: Parallel execution
  - Uses `ThreadPoolExecutor` for concurrent character evaluation
  - Returns list of (character, decision_tuple) for characters wanting to respond

- `_select_speaker_from_decisions()`: Priority-based selection
  - Adds random factor for naturalness
  - Returns selected character and their response

**Workflow**:
```
1. Collect decisions from all AI characters (parallel)
2. Select speaker based on priority + randomness
3. Generate and add their response to timeline
4. Broadcast event to character memories
5. Check for meta-narrative events (scenes, entry/exit)
6. Evaluate story progression
7. Repeat until silence or max turns
```

### CharacterManager

**Purpose**: Manages character lifecycle, memory, and decision-making.

**Key Methods**:
- `create_character()`: Initialize character with persona, memory, state
- `update_character_memory()`: Add timeline events to character's memory
- `decide_turn_response()`: LLM call to determine if character should speak/act/stay silent
- `generate_character_response()`: LLM call to generate actual dialogue and action

**Context Building**:
```python
build_persona_context()   # Personality, traits, relationships
build_state_context()     # Current objectives
build_memory_context()    # What they've witnessed
```

All three contexts are combined for LLM prompts.

**Decision Process**:
1. Character evaluates recent events from their memory
2. Considers their persona, state, and objectives
3. Returns decision tuple: `(response_type, priority, reasoning, dialogue, action)`
   - `response_type`: "speak", "act", or "silent"
   - `priority`: 0.0-1.0 importance score
   - `reasoning`: Why they chose this action
   - `dialogue`: What they say (if speaking)
   - `action`: Physical action/body language

### TimelineManager

**Purpose**: Manages timeline events and provides context building utilities.

**Key Methods**:
- `create_timeline_history()`: Initialize new timeline
- `add_event()`: Add event to timeline and update participants
- `create_message()`: Factory for Message objects
- `create_scene()`: Factory for Scene objects
- `get_recent_events()`: Retrieve last N events (with optional type filter)
- `get_timeline_context()`: Build formatted timeline string

**Event Flow**:
```
Event Creation → Add to Timeline → Update Participants → Broadcast to Characters
```

### StoryManager

**Purpose**: Manages story progression and character objective assignment.

**Key Methods**:
- `get_current_objective()`: Returns current story goal
- `evaluate_and_assign_objectives()`: Unified LLM call for:
  - Initial objective assignment (first turn)
  - Evaluating objective completion
  - Assigning new objectives to characters who completed theirs
  - Checking if story objective is complete

**Objective Flow**:
```
Story Objective → Character Objectives → Evaluate Completion → Next Story Objective
```

When a story objective is completed:
1. `current_objective_index` increments
2. All character objectives are cleared
3. New character objectives assigned for next story goal

### Loaders

#### CharacterLoader
**Purpose**: Load character personas from JSON files.

**Key Methods**:
- `load_character(name)`: Load single character
- `load_multiple_characters(names)`: Load multiple characters
- `list_available_characters()`: Show available character files

**File Structure**: `[Story Name]/characters/[character_name].json`

#### StoryLoader
**Purpose**: Load story configuration from JSON.

**Key Methods**:
- `load_story()`: Load the single story file from directory

**File Structure**: `[Story Name]/story/[story_name].json` (only one story file allowed)

## Data Flow

### Conversation Turn Flow

```
1. Player Input
   ↓
2. Create Message → Add to Timeline → Broadcast to Character Memories
   ↓
3. TurnManager.process_ai_responses()
   ↓
4. [PARALLEL] All characters evaluate if they want to speak
   │  ├─→ Character A: decide_turn_response()
   │  ├─→ Character B: decide_turn_response()
   │  └─→ Character C: decide_turn_response()
   ↓
5. Select highest priority speaker
   ↓
6. Generate response (dialogue + action)
   ↓
7. Create Message → Add to Timeline → Broadcast to Memories
   ↓
8. Check meta-narrative (scene changes, entries/exits)
   ↓
9. Evaluate story progression (every N turns)
   ↓
10. Save conversation state
    ↓
11. Repeat 3-10 until silence or max turns
```

### Character Memory Update Flow

```
Timeline Event Created
   ↓
TimelineManager.add_event()
   ↓
Determine which characters are present
   ↓
CharacterManager.broadcast_event_to_characters()
   ↓
For each present character:
   CharacterManager.update_character_memory()
   ↓
Event appended to character.memory.event[]
```

### Story Progression Flow

```
TurnManager evaluates every 3-5 turns
   ↓
StoryManager.evaluate_and_assign_objectives()
   ↓
Build context: story objective + timeline + character objectives
   ↓
LLM evaluates:
   - Are character objectives complete?
   - Is story objective complete?
   ↓
If character objective complete:
   - Assign new character objective
   ↓
If story objective complete:
   - Increment current_objective_index
   - Clear all character objectives
   - Next turn will assign new character objectives
```

### Persistence Flow

**Saving**:
```
After each AI response batch
   ↓
RoleplaySystem._save_conversation()
   ↓
Serialize timeline to JSON:
   - Timeline metadata
   - All events with type markers
   ↓
Write to [Story Name]/[story_name]_chat.json
```

**Loading**:
```
RoleplaySystem initialization
   ↓
Check if conversation file exists
   ↓
If exists: Load and parse JSON
   ↓
Reconstruct timeline:
   - Restore events by type
   - Track character presence
   ↓
Replay timeline to character memories:
   - For each event
   - Broadcast to characters present at that moment
```

## Design Patterns

### 1. **Factory Pattern**
Managers create objects using factory methods:
```python
TimelineManager.create_message(character, dialogue, action)
TimelineManager.create_scene(scene_type, location, description)
CharacterManager.create_character(persona, memory, state)
```

### 2. **Observer Pattern**
Events are broadcast to observers (characters):
```python
# Event occurs
event = timeline_manager.create_message(...)
# Broadcast to relevant characters
character_manager.broadcast_event_to_characters(active_characters, event)
```

### 3. **Strategy Pattern**
Different response strategies based on character decision:
- **Speak Strategy**: Generate dialogue + action
- **Act Strategy**: Generate action only (no dialogue)
- **Silent Strategy**: No response

### 4. **Coordinator Pattern**
`RoleplaySystem` coordinates all subsystems:
- Doesn't contain business logic
- Delegates to appropriate managers
- Manages lifecycle and persistence

### 5. **Command Pattern**
User commands trigger specific actions:
```python
"listen" → process_ai_responses(max_turns=5)
"skip" → process_ai_responses(max_turns=1)
"progress" → story_manager.get_progress_summary()
```

### 6. **Dependency Injection**
Components receive dependencies via constructor:
```python
TurnManager(characters, timeline, save_callback)
RoleplaySystem(player_name, characters, story_manager, ...)
```

## Advanced Concepts

### Parallel Character Evaluation

Using `ThreadPoolExecutor` for concurrent decision-making:

```python
with ThreadPoolExecutor(max_workers=len(self.characters)) as executor:
    futures = {executor.submit(get_character_decision, char): char 
               for char in self.characters}
    for future in as_completed(futures):
        character, decision = future.result()
        decisions.append((character, decision))
```

This allows all characters to "think" simultaneously, reducing response time.

### Priority-Based Speaker Selection

Characters don't take strict turns - they speak based on contextual priority:

```python
priority = base_priority + random.uniform(-randomness, randomness)
speaker = max(decisions, key=lambda x: x.adjusted_priority)
```

This creates natural conversation flow where the most motivated character speaks.

### Character Perspective Memory

Each character only remembers what they witnessed:

```python
# Only broadcast to characters present at this moment
active_characters = [c for c in characters if c.persona.name in present_at_moment]
broadcast_event_to_characters(active_characters, event)
```

This enables:
- Private conversations (characters in different locations)
- Character entry/exit (joining ongoing conversations)
- Realistic information asymmetry

### Story-Driven Objectives

Two-level objective system:
1. **Story Objectives**: High-level narrative goals (e.g., "Find the hidden temple")
2. **Character Objectives**: Individual tasks assigned by LLM (e.g., "Navigate through the jungle using your map skills")

Character objectives dynamically adjust based on story progress and character capabilities.

## Best Practices

### Adding New Event Types

1. Create model inheriting from `TimelineEvent` in `data_models.py`
2. Add serialization logic in `RoleplaySystem._save_conversation()`
3. Add deserialization logic in `RoleplaySystem._load_conversation_if_exists()`
4. Update `TimelineManager.get_timeline_context()` for formatting
5. Update `CharacterManager.build_memory_context()` for character perspective

### Modifying LLM Prompts

LLM interaction points:
- `CharacterManager.decide_turn_response()`: Decision prompt
- `CharacterManager.generate_character_response()`: Response generation
- `StoryManager.evaluate_and_assign_objectives()`: Objective evaluation
- `TimelineManager` (various scene generation methods)

Always return structured JSON for consistent parsing.

### Extending Character Capabilities

To add new character attributes:
1. Add field to `CharacterPersona` in `data_models.py`
2. Update character JSON files
3. Update `CharacterManager.build_persona_context()` to include in prompts
4. Update `CharacterLoader` validation if needed

### Performance Optimization

- Use parallel execution for independent operations
- Limit context window (last N events) for LLM calls
- Cache frequently accessed data
- Implement event filtering (by type, participant, time range)

## Configuration

See `config.py` for system configuration:

```python
DEFAULT_MODEL = "x-ai/grok-4.1-fast"  # LLM model
MODEL_TEMPERATURE = 0.7                # Creativity
MAX_TOKENS = 1024                      # Response length
DEFAULT_CONTEXT_WINDOW = 100           # Events to consider
MAX_CONSECUTIVE_AI_TURNS = 3           # AI conversation depth
PRIORITY_RANDOMNESS = 0.1              # Natural variation
```

## Error Handling

### API Errors
- Rate limit exceeded: Caught and displayed with retry suggestion
- Invalid API key: Raised during initialization
- Quota exceeded: Gracefully handled in parallel execution

### File Errors
- Missing character files: Clear error with available characters list
- Multiple story files: Validation prevents ambiguity
- Invalid JSON: Detailed error messages with file location

### State Errors
- Empty timeline: Graceful degradation
- Missing objectives: Default behavior defined
- Character not present: Filtered from broadcasts

---

**Last Updated**: December 2025  
**Author**: Jit Roy  
**License**: MIT
