# RoleRealm Documentation Index

Welcome to the RoleRealm documentation! This comprehensive guide will help you understand, use, and extend the RoleRealm interactive AI roleplay system.

## Quick Links

### Getting Started
- 📘 [Getting Started Guide](getting-started.md) - Installation, setup, and your first story
- 📖 [User Guide](user-guide.md) - Complete guide to using RoleRealm features
- 🎭 [Character Creation Guide](character-guide.md) - Creating compelling AI characters
- 📚 [Story Design Guide](story-design-guide.md) - Crafting engaging narratives

### Reference
- 🔧 [API Reference](api-reference.md) - Complete API documentation
- 🏗️ [Architecture Documentation](architecture.md) - System design and internals

## Documentation Overview

### For Users

#### [Getting Started Guide](getting-started.md)
**Perfect for**: First-time users

**Covers**:
- Installation and setup
- Running the example story
- Creating your first custom story
- Basic commands and interface
- Quick tips for success

**Time**: 30 minutes to get your first story running

---

#### [User Guide](user-guide.md)
**Perfect for**: Users wanting to master the system

**Covers**:
- Understanding RoleRealm's core concepts
- All system commands and features
- Character memory and perspectives
- Timeline events and story progression
- Advanced features like character entry/exit
- Tips and best practices
- Troubleshooting common issues

**Time**: 1-2 hours to become proficient

---

#### [Character Creation Guide](character-guide.md)
**Perfect for**: Creating memorable AI characters

**Covers**:
- Character design fundamentals
- JSON structure and all fields
- Personality traits and complexity
- Speaking styles and voice
- Relationships and dynamics
- Goals and motivations
- Knowledge systems
- Advanced techniques
- Complete example characters

**Time**: Learn in 1 hour, master through practice

---

#### [Story Design Guide](story-design-guide.md)
**Perfect for**: Crafting engaging narratives

**Covers**:
- Story structure fundamentals
- Objective design (SMART framework)
- Pacing and tension curves
- Different story types (adventure, mystery, heist, etc.)
- Character-objective integration
- Advanced techniques
- Complete example stories

**Time**: Learn in 1 hour, improve with experimentation

---

### For Developers

#### [API Reference](api-reference.md)
**Perfect for**: Developers extending RoleRealm

**Covers**:
- Complete data model reference
- All manager classes and methods
- Loader utilities
- RoleplaySystem API
- Configuration options
- Error handling
- Code examples

**Time**: Reference as needed

---

#### [Architecture Documentation](architecture.md)
**Perfect for**: Understanding the system internals

**Covers**:
- Core architecture overview
- Data models and their relationships
- System managers and responsibilities
- Data flow diagrams
- Design patterns used
- Advanced concepts (parallel execution, memory systems)
- Best practices for extending the system

**Time**: 2-3 hours for full understanding

---

## Learning Paths

### Path 1: Quick Start (1 hour)
1. [Getting Started Guide](getting-started.md) - Setup and first run
2. Try the Pirate Adventure example
3. Create a simple custom character
4. Experiment with conversations

**Goal**: Run your first interactive story

---

### Path 2: Story Creator (3-4 hours)
1. [Getting Started Guide](getting-started.md) - Basics
2. [Character Creation Guide](character-guide.md) - Master characters
3. [Story Design Guide](story-design-guide.md) - Craft narratives
4. Create a complete custom story with 3+ characters

**Goal**: Create publication-worthy interactive stories

---

### Path 3: Power User (4-6 hours)
1. [Getting Started Guide](getting-started.md) - Basics
2. [User Guide](user-guide.md) - All features
3. [Character Creation Guide](character-guide.md) - Advanced characters
4. [Story Design Guide](story-design-guide.md) - Complex narratives
5. Experiment with all advanced features
6. Create multiple stories with different genres

**Goal**: Master all features and create diverse content

---

### Path 4: Developer (6-8 hours)
1. [Getting Started Guide](getting-started.md) - Basics
2. [Architecture Documentation](architecture.md) - System design
3. [API Reference](api-reference.md) - Complete API
4. Study the source code
5. Create custom extensions or integrations

**Goal**: Extend RoleRealm or integrate it into other projects

---

## Document Summaries

### Getting Started Guide
- **Length**: ~3,000 words
- **Difficulty**: Beginner
- **Hands-on**: Yes, includes complete walkthrough
- **Prerequisites**: None
- **Key Sections**:
  - Installation
  - Quick start
  - Creating your first story (complete example)
  - Running your story
  - Understanding the interface
  - Next steps

### User Guide
- **Length**: ~8,000 words
- **Difficulty**: Beginner to Intermediate
- **Hands-on**: Many examples
- **Prerequisites**: Getting Started Guide
- **Key Sections**:
  - Understanding RoleRealm
  - System commands
  - Character system
  - Timeline & memory
  - Story progression
  - Advanced features
  - Tips & best practices

### Character Creation Guide
- **Length**: ~7,000 words
- **Difficulty**: Intermediate
- **Hands-on**: Templates and examples
- **Prerequisites**: Getting Started Guide
- **Key Sections**:
  - Character fundamentals
  - JSON structure
  - Personality design
  - Speaking styles
  - Relationships
  - Goals & motivations
  - Knowledge systems
  - Three complete example characters

### Story Design Guide
- **Length**: ~6,000 words
- **Difficulty**: Intermediate
- **Hands-on**: Templates and complete stories
- **Prerequisites**: Getting Started Guide, Character Guide recommended
- **Key Sections**:
  - Story fundamentals
  - Objective design
  - Pacing & flow
  - Story types (6 complete templates)
  - Integration with characters
  - Advanced techniques
  - Three complete example stories

### API Reference
- **Length**: ~10,000 words
- **Difficulty**: Intermediate to Advanced
- **Hands-on**: Code examples throughout
- **Prerequisites**: Python knowledge
- **Key Sections**:
  - Data models (complete reference)
  - Managers (all methods documented)
  - Loaders
  - RoleplaySystem
  - Configuration
  - Utilities
  - Error handling

### Architecture Documentation
- **Length**: ~7,000 words
- **Difficulty**: Advanced
- **Hands-on**: Conceptual diagrams
- **Prerequisites**: Python, software architecture knowledge
- **Key Sections**:
  - Core architecture
  - Data models
  - System managers
  - Data flow
  - Design patterns
  - Advanced concepts
  - Best practices

---

## Key Concepts Reference

Quick reference to core RoleRealm concepts:

### Timeline Events
All events happen on a chronological timeline:
- **Message**: Character dialogue with action
- **Scene**: Environmental/narrative event
- **Action**: Physical action without speech
- **CharacterEntry**: Character joins conversation
- **CharacterExit**: Character leaves conversation

### Character Components
Every AI character has three parts:
- **Persona**: Immutable personality (traits, style, background)
- **Memory**: Growing list of witnessed events
- **State**: Current objective and condition

### Story Structure
Stories progress through sequential objectives:
- **Story Objectives**: Main plot points
- **Character Objectives**: Individual tasks (assigned by AI)
- **Progress Tracking**: Current objective index

### Key Managers
- **CharacterManager**: Character lifecycle and decisions
- **TimelineManager**: Event creation and timeline operations
- **TurnManager**: Conversation flow and turn selection
- **StoryManager**: Story progression and objectives

---

## Common Questions

**Q: Where do I start if I just want to try it out?**  
A: [Getting Started Guide](getting-started.md) - Takes 30 minutes to get running

**Q: How do I create good characters?**  
A: [Character Creation Guide](character-guide.md) - Covers everything from basics to advanced

**Q: How do I design engaging stories?**  
A: [Story Design Guide](story-design-guide.md) - Includes templates and complete examples

**Q: What can I do with RoleRealm?**  
A: [User Guide](user-guide.md) - Complete feature overview

**Q: How does the system work internally?**  
A: [Architecture Documentation](architecture.md) - Deep dive into design

**Q: Where's the API documentation?**  
A: [API Reference](api-reference.md) - Complete reference for all classes and methods

**Q: Can I extend or modify RoleRealm?**  
A: Yes! See [Architecture Documentation](architecture.md) and [API Reference](api-reference.md)

---

## Contributing to Documentation

Found an error? Want to improve these docs?

The documentation is written in Markdown and located in the `docs/` folder.

**To contribute**:
1. Fork the repository
2. Edit the relevant `.md` file
3. Submit a pull request

**Style guidelines**:
- Use clear, concise language
- Include code examples for technical concepts
- Add practical examples
- Keep formatting consistent
- Link between related sections

---

## Version Information

**Documentation Version**: 1.0  
**RoleRealm Version**: 1.0  
**Last Updated**: December 2025  
**Author**: Jit Roy

---

## License

This documentation is part of RoleRealm and is licensed under the MIT License.

Copyright (c) 2025 Jit Roy

See [LICENSE](../LICENSE) file for full license text.

---

**Need help?** Start with the [Getting Started Guide](getting-started.md) or jump to the specific guide that matches your needs!
