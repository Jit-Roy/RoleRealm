# RoleRealm User Guide

Comprehensive guide to using RoleRealm's features and creating engaging interactive stories.

## Table of Contents
- [Understanding RoleRealm](#understanding-rolerealm)
- [System Commands](#system-commands)
- [Character System](#character-system)
- [Timeline & Memory](#timeline--memory)
- [Story Progression](#story-progression)
- [Advanced Features](#advanced-features)
- [Tips & Best Practices](#tips--best-practices)

## Understanding RoleRealm

### Core Concepts

**Timeline-Based Events**
Everything in RoleRealm happens on a unified timeline. Events include:
- **Messages**: Character dialogue with body language
- **Scenes**: Environmental changes and transitions
- **Actions**: Physical actions without dialogue
- **Entry/Exit**: Characters joining or leaving conversations

**Character Memory**
Each character maintains their own memory of events they witnessed. This means:
- Characters only know what happened when they were present
- Information doesn't magically spread between characters
- You can create situations where some characters know secrets others don't

**Dynamic Turn Taking**
Characters don't take strict turns. Instead:
- All characters evaluate if they want to speak
- The most motivated character (highest priority) speaks
- Natural conversation flow emerges organically

**Story-Driven Objectives**
Two levels of goals guide the narrative:
- **Story Objectives**: Main plot points (e.g., "Find the treasure")
- **Character Objectives**: Individual tasks assigned by AI (e.g., "Use your navigation skills to chart a course")

## System Commands

### During Conversation

#### Basic Commands

**Speaking** (Just type naturally)
```
⚡ You: I think we should explore the cave first
```
Your input becomes dialogue for your character.

**`listen`** - Silent observation
```
⚡ You: listen
```
- You stay quiet for 5 AI turns
- Characters continue conversation naturally
- Good for watching character interactions

**`skip`** - Prompt continuation
```
⚡ You: skip
```
- Forces one AI character to respond
- Useful when there's an awkward silence
- Characters might pass the conversation along

**`progress`** - Check story status
```
⚡ You: progress

📖 STORY PROGRESS
════════════════════════════════════════════════════════════════════
Story: The Quest for the Phantom Pearl
Progress: 25% (2 of 8 objectives complete)

✓ COMPLETED OBJECTIVES:
  1. Decipher the mysterious map and determine the first destination
  2. Navigate through the Siren's Strait without losing the ship

→ CURRENT OBJECTIVE:
  Find and explore the abandoned island marked with the skull symbol
```

**`info`** - Character information
```
⚡ You: info
```
Shows details about all active characters:
- Name and traits
- Current objectives
- Relationships
- Speaking style

**`reset`** - Start fresh
```
⚡ You: reset
```
- Deletes conversation history
- Starts a completely new session
- Cannot be undone!

**`quit`** or `exit`** - Save and exit
```
⚡ You: quit
```
- Saves conversation state
- Exits gracefully
- Can resume next time

### Character-Specific Commands (Future)

*Note: Some commands may be added in future versions*

## Character System

### How Characters Work

#### Three Components

Every AI character has three parts:

1. **Persona** (Immutable)
   - Personality traits
   - Speaking style
   - Background and relationships
   - Goals and knowledge
   - Never changes during conversation

2. **Memory** (Growing)
   - Events they've witnessed
   - Grows as they experience more
   - Unique to each character

3. **State** (Dynamic)
   - Current objective
   - Changes as story progresses
   - Reflects immediate focus

#### Decision Making

Each turn, characters evaluate:

1. **Should I respond?**
   - Am I directly addressed?
   - Is this relevant to me?
   - Has there been awkward silence?
   - Do I have important information to share?

2. **How should I respond?**
   - **Speak**: Dialogue + body language
   - **Act**: Physical action only
   - **Silent**: Stay quiet

3. **Priority Score** (0.0 - 1.0)
   - Higher = more motivated to speak
   - Incorporates small random factor for naturalness
   - Highest priority character speaks

#### Example Decision Process

```
Situation: Player asks "What do you think, Captain?"

Marina evaluates:
- Not directly addressed to me
- Topic is relevant (I care about the ship)
- Captain will probably answer
→ Decision: SILENT (Priority: 0.2)
  Reasoning: "The Captain was directly asked and should answer first"

Captain evaluates:
- Directly addressed to me
- I have authority to decide
- My opinion matters here
→ Decision: SPEAK (Priority: 0.9)
  Reasoning: "I was directly asked for my opinion"

Result: Captain speaks
```

### Character Perspectives

#### Individual Memories

Characters only remember what they witnessed:

```python
# Timeline has 10 events
# Marina was present for events 1-7
# Jack entered at event 5

Marina's memory: [Event1, Event2, Event3, Event4, Event5, Event6, Event7]
Jack's memory: [Event5, Event6, Event7]
```

**This enables:**
- Secret conversations when characters are absent
- Characters learning information at different times
- Realistic "catch up" moments when someone rejoins

#### Example: Information Asymmetry

```
Scene 1: Captain's Quarters
Present: Captain, Marina

Captain: *leans in conspiratorially* I didn't want to say this in front 
of Jack, but I think he's been taking more than his fair share of the loot.

Marina: *eyes widen* Are you certain? That's a serious accusation.

[Marina now knows this secret, Jack does not]

Scene 2: Main Deck (30 minutes later)
Present: Captain, Marina, Jack

Jack: *walks over cheerfully* What are you two talking about?

Marina: *exchanges glance with Captain* Just discussing the route.
[Marina can choose to reveal or hide the information]
```

## Timeline & Memory

### Event Types

#### Messages
Character dialogue with action:
```
Captain: *slams fist on table* We sail at dawn, no exceptions!
```
Components:
- Character name: "Captain"
- Action: "slams fist on table"
- Dialogue: "We sail at dawn, no exceptions!"

#### Scenes
Environmental or transitional events:
```
[Scene at Ship Deck] Dark storm clouds gather on the horizon as 
waves crash against the hull. Thunder rumbles in the distance.
```
Components:
- Type: "environmental" or "transition"
- Location: "Ship Deck"
- Description: What's happening

#### Actions
Physical actions without speech:
```
[ACTION] Marina: carefully unfolds the ancient map and spreads it 
on the barrel, weighing down the corners with coins
```

#### Entry/Exit
Characters joining or leaving:
```
[ENTERED] Jack: bursts through the door, out of breath and soaking wet

[LEFT] Old Sailor: hobbles off toward the galley, muttering about 
superstitious young folk
```

### Timeline Context

The system builds context from recent timeline:

**For Characters** (making decisions):
```
Recent events from character's memory:
Captain: *studies the map* These markings indicate dangerous waters.
You: What kind of dangers are we talking about?
Marina: *traces finger along route* Reefs, whirlpools, possibly sirens.
[Scene at Ship Deck] The wind picks up, making the sails flutter.
```

**For You** (visual display):
```
Recent Conversation:
💬 Captain: These markings indicate dangerous waters.
💬 You: What kind of dangers are we talking about?
💬 Marina: Reefs, whirlpools, possibly sirens.
🎬 [Scene at Ship Deck]: The wind picks up...
```

### Persistence

**Automatic Saving**
- After each batch of AI responses
- When you use `quit` or `exit`
- Stored in `[Story Name]/group_chat.json`

**What's Saved**:
- Complete timeline (all events)
- Participants list
- Character memories (reconstructed on load)
- Story progress (current objective index)

**Loading**
- Automatic on startup if file exists
- Replays timeline to rebuild character memories
- Tracks character presence throughout timeline
- Shows recent events summary

## Story Progression

### How Stories Work

#### Sequential Objectives

Stories have ordered objectives:
```json
"objectives": [
  "Decipher the map",           // Must complete first
  "Navigate the strait",         // Then this
  "Find the island",             // Then this
  ...
]
```

**Linear Progression**:
1. Start at objective index 0
2. When completed, increment to 1
3. Continue until all objectives complete
4. Story ends when final objective complete

#### Character Objectives

When story has an objective, characters receive individual tasks:

**Story Objective**: "Navigate through the Siren's Strait"

**Character Objectives** (assigned by AI):
- Captain: "Maintain steady course and keep crew focused despite sirens"
- Marina: "Use celestial navigation to guide ship through treacherous waters"
- Jack: "Watch for rocks and reefs, warn of dangers ahead"

**Dynamic Assignment**:
- Considers character traits and abilities
- Aligns with character goals and knowledge
- Adapts based on recent conversation
- Reassigned when completed

### Objective Evaluation

**Frequency**: Every 3-5 turns

**Process**:
1. Review recent timeline events
2. Check each character's objective status
3. Determine if character objectives complete
4. Assign new objectives to characters who completed theirs
5. Check if overall story objective complete
6. If story objective complete, advance to next one

**Example Evaluation**:
```
Story Objective: "Navigate through the Siren's Strait"

Character Status:
- Captain: "Maintain steady course" → COMPLETED
  New objective: "Inspect ship for damage from rough passage"
  
- Marina: "Use celestial navigation" → COMPLETED
  New objective: "Rest and recover from concentration effort"
  
- Jack: "Watch for dangers" → CONTINUING
  (Still watching as they finish passage)

Story Objective Status: COMPLETE
Next Story Objective: "Find the abandoned island marked with skull symbol"
```

### Progress Tracking

View anytime with `progress` command:

```
📖 STORY PROGRESS
════════════════════════════════════════════════════════════════════
Story: The Quest for the Phantom Pearl
Progress: 37% (3 of 8 objectives complete)

✓ COMPLETED OBJECTIVES:
  1. Decipher the mysterious map and determine the first destination
  2. Navigate through the Siren's Strait without losing the ship
  3. Find and explore the abandoned island marked with the skull symbol

→ CURRENT OBJECTIVE:
  Recover the ancient compass hidden in the island's temple ruins

CHARACTER OBJECTIVES:
  Captain: Search the temple's main chamber for clues
  Marina: Decipher the ancient runes on the temple walls
  Jack: Keep watch for traps and dangers

UPCOMING OBJECTIVES:
  5. Evade or confront the rival pirate crew hunting the same treasure
  6. Use the compass to locate the underwater cave entrance
  7. Solve the riddles guarding the inner chamber of the cave
  8. Claim the Phantom Pearl and escape before the cave collapses
```

## Advanced Features

### Multi-Character Dynamics

#### Conversation Patterns

**Direct Address**:
```
You: Jack, what do you think we should do?
[Jack receives high priority to respond]
```

**Group Questions**:
```
You: Does anyone know how to read these symbols?
[All characters evaluate based on their knowledge]
[Character with relevant knowledge gets higher priority]
```

**Character-to-Character**:
```
Captain: Marina, check those navigation charts again.
Marina: *nods and unfolds the charts* Right away, Captain.
[Natural back-and-forth between AI characters]
```

#### Priority Factors

Characters get higher priority when:
- Directly addressed by name
- Topic matches their expertise
- Related to their current objective
- Breaking awkward silence
- Responding to emotional moment
- Having urgent information

Lower priority when:
- Not their area of expertise
- Recently spoke multiple times
- Another character better suited
- Scene doesn't involve them

### Scene Management

#### Automatic Scene Generation

System creates scenes when:
- Significant location change detected
- Major story development occurs
- Environmental shift happens
- Transition needed for pacing

**Environmental Scene Example**:
```
[Scene at Ancient Temple Ruins] The air grows cold as you enter the 
temple. Moss covers ancient stone walls, and strange symbols glow 
faintly in the darkness. Water drips somewhere in the distance.
```

**Transition Scene Example**:
```
[Scene Transition] Several hours pass as the crew navigates through 
the treacherous waters. The sun begins to set, painting the sky 
in brilliant oranges and reds.
```

### Character Entry & Exit

#### Dynamic Presence

Characters can join or leave mid-conversation:

**Entry Example**:
```
[Scene at Tavern]
Present: You, Innkeeper

You: Have you seen anything unusual lately?
Innkeeper: Well, now that you mention it...

[ENTERED] Mysterious Stranger: pushes through the door, cloak dripping 
with rain, and takes a seat at the bar

Present: You, Innkeeper, Mysterious Stranger

Innkeeper: *lowers voice* Speak of the devil...
[Stranger can now participate in conversation]
[Stranger's memory starts from this point]
```

**Exit Example**:
```
Captain: *stands abruptly* I need to check on the crew. You lot carry on.

[LEFT] Captain: strides off toward the main deck

Present: You, Marina, Jack
[Captain no longer receives broadcasts]
[Captain's memory stops here]
[Private conversation possible]
```

### Meta-Narrative Events

#### What Are They?

Events that shape the narrative beyond just dialogue:
- Scene changes
- Time passage
- Environmental shifts
- Character movements
- Atmospheric changes

#### How They're Triggered

**Player-Initiated** (future feature):
```
⚡ You: /scene We travel to the temple ruins
[System generates appropriate scene transition]
```

**AI-Generated**:
- System evaluates need for scene change
- Considers story pacing
- Generates naturally during flow

## Tips & Best Practices

### For Better Conversations

1. **Be Specific in Questions**
   ```
   ❌ "What do you think?"
   ✓ "Captain, do you think we can make it through the storm?"
   ```

2. **Address Characters by Name**
   ```
   ❌ "Can someone help me?"
   ✓ "Marina, can you help me decipher these symbols?"
   ```

3. **Include Actions**
   ```
   ❌ "I agree with the Captain"
   ✓ "*nods firmly* I agree with the Captain, we should sail at dawn"
   ```

4. **Create Drama**
   ```
   ✓ "I don't trust this. Something feels wrong about this treasure."
   ✓ "Are we really going to ignore what Jack saw?"
   ✓ "*challenges the Captain* With all respect, this plan is too risky"
   ```

5. **Use `listen` Strategically**
   - After asking a group question
   - When you want characters to debate
   - To see natural character dynamics
   - During tense moments

### For Story Design

1. **Start with Clear Objectives**
   - Each objective should be specific and achievable
   - Create natural progression
   - Build tension as objectives advance

2. **Create Character Synergy**
   - Give characters complementary skills
   - Create both alliances and conflicts
   - Define clear relationships

3. **Use Knowledge Asymmetry**
   - Give characters unique information
   - Create opportunities for reveals
   - Enable character-specific contributions

4. **Balance Character Numbers**
   - 2-3 characters: Intimate, easy to follow
   - 4-5 characters: Dynamic, multiple viewpoints
   - 6+ characters: Complex, may be chaotic

### For Character Design

1. **Specific Traits**
   ```
   ❌ "nice, friendly, helpful"
   ✓ "sarcastic wit, loyal to a fault, secretly insecure about magic abilities"
   ```

2. **Distinct Speaking Styles**
   ```
   ✓ Captain: "Gravitas, seafaring expressions, commands respect"
   ✓ Jack: "Casual slang, enthusiastic, interrupts with excitement"
   ✓ Marina: "Precise technical language, thoughtful pauses, scholarly"
   ```

3. **Meaningful Relationships**
   ```
   ✓ "Sees Jack as a younger brother, protective but frustrated by his recklessness"
   vs
   ❌ "Friends with Jack"
   ```

4. **Character Goals Create Motivation**
   ```
   ✓ "Prove herself worthy despite being the youngest crew member"
   ✓ "Find redemption for past cowardice by being brave this time"
   ```

### Common Issues & Solutions

#### Issue: Characters talk too much
**Solution**: 
- Adjust `MAX_CONSECUTIVE_AI_TURNS` in config.py (lower = less AI chatter)
- Use specific questions to guide conversation
- Give characters conflicting priorities

#### Issue: Same character always speaks
**Solution**:
- Address other characters by name
- Ask questions that match different characters' expertise
- Increase `PRIORITY_RANDOMNESS` for more variety

#### Issue: Objectives not completing
**Solution**:
- Make story objectives more specific
- Ensure characters have actions aligned with objectives
- Manually advance story if needed (future feature)

#### Issue: Characters repeating themselves
**Solution**:
- Increase `frequency_penalty` in character JSON
- Create more varied character objectives
- Ensure story is progressing

---

**Last Updated**: December 2025  
**Author**: Jit Roy  
**License**: MIT
