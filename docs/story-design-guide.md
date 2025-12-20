# Story Design Guide

Learn to craft engaging interactive narratives for RoleRealm.

## Table of Contents
- [Story Fundamentals](#story-fundamentals)
- [Story JSON Structure](#story-json-structure)
- [Objective Design](#objective-design)
- [Pacing & Flow](#pacing--flow)
- [Story Types](#story-types)
- [Integration with Characters](#integration-with-characters)
- [Advanced Techniques](#advanced-techniques)
- [Example Stories](#example-stories)

## Story Fundamentals

### What Makes a Great Interactive Story?

**1. Clear Direction**
Players should always know:
- What they're trying to achieve
- Why it matters
- What stands in their way

**2. Player Agency**
The story should:
- React to player choices
- Allow multiple approaches
- Feel responsive, not railroaded

**3. Escalating Stakes**
Build tension through:
- Increasing difficulty
- Rising consequences
- Deeper mysteries revealed

**4. Character Integration**
Best stories:
- Use character abilities meaningfully
- Create character-specific moments
- Evolve alongside character arcs

### RoleRealm Story Structure

**Sequential Objectives**
Stories progress through ordered objectives:
```
Objective 1 → Objective 2 → Objective 3 → ... → Conclusion
```

Each objective:
- Has a clear completion condition
- Builds on previous objectives
- Advances the overall narrative
- Generates character-specific tasks

**Dynamic Character Objectives**
When story has an objective, AI assigns individual character tasks:
```
Story Objective: "Navigate through dangerous strait"
  ├─ Captain: "Maintain steady course through rough waters"
  ├─ Navigator: "Chart safe passage using star charts"
  └─ Lookout: "Watch for rocks and warn of dangers"
```

## Story JSON Structure

### Complete Template

```json
{
  "title": "Story Title",
  "description": "Overall story premise and setting. This provides context 
                  for the entire narrative arc and establishes the world.",
  "objectives": [
    "First objective - specific and achievable",
    "Second objective - builds on first",
    "Third objective - escalates tension",
    "Final objective - satisfying conclusion"
  ],
  "current_objective_index": 0
}
```

### Required Fields

- **title** (string): Story name, displayed to player
- **description** (string): Overall story context and premise
- **objectives** (array): Sequential list of objectives
- **current_objective_index** (number): Starting index (usually 0)

### File Location

Stories must be in: `[Story Name]/story/[filename].json`

**Important**: Only ONE story file per directory!

## Objective Design

### Anatomy of a Good Objective

**Bad Objective**:
```json
"Do something cool"
```
Problems:
- Vague and unmeasurable
- No clear completion condition
- Doesn't guide AI or player

**Good Objective**:
```json
"Decipher the ancient map to determine the location of the first trial"
```
Strengths:
- Specific action (decipher map)
- Clear artifact (ancient map)
- Measurable outcome (determine location)
- Advances plot (to first trial)

### The SMART Framework

Make objectives **SMART**:

**S**pecific - Exactly what needs to happen
```
❌ "Find information"
✓ "Interrogate the tavern keeper about the missing merchants"
```

**M**easurable - Clear completion condition
```
❌ "Help the village"
✓ "Defeat the bandits raiding the village farms"
```

**A**chievable - Possible within story context
```
❌ "Defeat the invincible demon lord" (if characters are beginners)
✓ "Escape the demon lord's lair with the artifact"
```

**R**elevant - Advances overall story
```
❌ "Win the pie-eating contest" (in serious treasure hunt)
✓ "Win the navigator's trust by proving your sailing knowledge"
```

**T**ime-bound - Clear when it's done
```
❌ "Prepare for the journey" (when is it enough preparation?)
✓ "Gather supplies and set sail before the storm arrives"
```

### Objective Templates

**Investigation**:
```
"Investigate [location] to discover [information/clue/truth] about [mystery]"
```

**Acquisition**:
```
"Obtain/Recover [item/artifact/knowledge] from [location/person/challenge]"
```

**Navigation**:
```
"Reach/Navigate to [destination] while overcoming [obstacle/danger]"
```

**Social**:
```
"Convince/Persuade [person/group] to [action] by [method/demonstration]"
```

**Confrontation**:
```
"Confront/Defeat/Evade [antagonist/threat] to [goal/protection/escape]"
```

**Puzzle**:
```
"Solve [puzzle/riddle/mystery] to unlock/access [reward/location/knowledge]"
```

### Objective Sequences

#### The Classic Three-Act Structure

**Act 1: Setup** (25%)
```json
"objectives": [
  "Learn about the quest and gather initial information",
  "Assemble the team and prepare for the journey",
  "Depart on the adventure toward the first challenge"
]
```

**Act 2: Confrontation** (50%)
```json
"objectives": [
  "Overcome the first major obstacle",
  "Discover complication that changes the mission",
  "Face setback and recover",
  "Prepare for final confrontation"
]
```

**Act 3: Resolution** (25%)
```json
"objectives": [
  "Execute the plan to reach the goal",
  "Overcome final challenge",
  "Resolve and return victorious"
]
```

#### The Mystery Structure

```json
"objectives": [
  "Discover the crime/mystery has occurred",
  "Gather initial clues and interview witnesses",
  "Uncover the first layer of deception",
  "Follow the trail to a major revelation",
  "Confront false lead or red herring",
  "Piece together the true solution",
  "Reveal the culprit and resolve the mystery"
]
```

#### The Heist Structure

```json
"objectives": [
  "Identify the target and why it must be acquired",
  "Research the location and security measures",
  "Assemble specialized team members",
  "Create detailed plan accounting for obstacles",
  "Execute the heist, adapting to complications",
  "Escape with the prize",
  "Deal with the unexpected consequence"
]
```

#### The Journey Structure

```json
"objectives": [
  "Depart from home toward distant destination",
  "Overcome environmental challenge (storm, desert, mountains)",
  "Help settlement along the way",
  "Face personal trial that tests character",
  "Discover shortcut or alternate route",
  "Reach destination",
  "Achieve the goal that required the journey"
]
```

## Pacing & Flow

### Objective Length

**Short Objectives** (1-3 turns):
```json
"Introduce yourselves and discuss the mission"
```
- Quick, conversational
- Good for transitions
- Low stakes

**Medium Objectives** (5-10 turns):
```json
"Navigate through the treacherous mountain pass while avoiding avalanches"
```
- Standard pacing
- Room for character moments
- Moderate challenge

**Long Objectives** (10+ turns):
```json
"Infiltrate the fortress, locate the prisoner, and escape without detection"
```
- Complex, multi-part
- Multiple challenges
- High stakes

### The Tension Curve

Vary objective intensity:

```
High │     ╱╲         ╱╲
     │    ╱  ╲       ╱  ╲      ╱╲
     │   ╱    ╲     ╱    ╲    ╱  ╲
     │  ╱      ╲   ╱      ╲  ╱    ╲
Low  │─╱────────╲─╱────────╲╱──────╲─
     Setup  Peak  Rest   Climax  Resolution
```

Example tension mapping:
```json
"objectives": [
  "Gather at tavern and discuss the map",          // Low - Setup
  "Race to beat rivals to the temple entrance",    // High - Peak
  "Explore the peaceful outer chambers",           // Low - Rest
  "Solve deadly traps in the inner sanctum",       // High - Climax
  "Escape with treasure as temple collapses",      // High - Climax
  "Return home and celebrate victory"              // Low - Resolution
]
```

### Transition Objectives

Connect major story beats:

```json
"objectives": [
  "Defeat the guardian beast",           // Action climax
  "Tend to wounds and rest",             // Recovery/character moment
  "Decode the map found on the guardian", // Investigation begins
  "Journey to the location revealed",    // Transition
  "Infiltrate the enemy stronghold"      // Next action sequence
]
```

These "breathing room" objectives allow:
- Character development
- Relationship building
- Processing recent events
- Building anticipation

## Story Types

### Adventure/Quest

**Structure**: Journey → Challenges → Prize → Return

**Example**:
```json
{
  "title": "The Quest for the Phoenix Feather",
  "description": "The king lies dying from an incurable poison. Only a feather 
                  from the legendary Phoenix, said to dwell atop Mount Ashfire, 
                  can cure him. You must journey across dangerous lands, prove 
                  your worth, and return before time runs out.",
  "objectives": [
    "Receive the quest from the royal court and learn about the Phoenix",
    "Cross the Whispering Desert with its mirages and sandstorms",
    "Climb Mount Ashfire despite heat and volcanic hazards",
    "Prove your purity of intent to the Phoenix guardian",
    "Obtain a single feather from the Phoenix",
    "Descend the mountain and race back to the capital",
    "Administer the cure and save the king"
  ]
}
```

### Mystery/Investigation

**Structure**: Crime → Clues → Deduction → Revelation → Resolution

**Example**:
```json
{
  "title": "Murder at Blackwood Manor",
  "description": "Lord Blackwood has been found dead in his locked study. 
                  Six guests were present at the manor that night, each with 
                  secrets to hide. As the detective, you must uncover the truth 
                  before the murderer strikes again.",
  "objectives": [
    "Examine the crime scene and note all evidence",
    "Interview each of the six guests and note their alibis",
    "Discover the hidden passage in the study",
    "Uncover the blackmail scheme Lord Blackwood was running",
    "Determine which guest had access to the rare poison used",
    "Set a trap to make the killer reveal themselves",
    "Present your case and bring the murderer to justice"
  ]
}
```

### Heist/Infiltration

**Structure**: Target → Plan → Preparation → Execution → Escape

**Example**:
```json
{
  "title": "The Diamond of Destinies",
  "description": "The infamous Diamond of Destinies is being transported to 
                  the National Museum for exhibition. Your team has been hired 
                  to acquire it before it disappears into the vault. One chance, 
                  one week to plan, and a security system designed to be impenetrable.",
  "objectives": [
    "Scout the museum and identify security measures",
    "Recruit specialists: lockpicker, tech expert, and distraction artist",
    "Obtain blueprints and guard schedules through social engineering",
    "Test the plan using the museum's sister building across town",
    "Execute the heist during the gala opening night",
    "Overcome unexpected security upgrade",
    "Escape and deliver the diamond to the mysterious client"
  ]
}
```

### Survival/Escape

**Structure**: Trapped → Explore → Resources → Challenges → Freedom

**Example**:
```json
{
  "title": "Escape from Deadrock Prison",
  "description": "Wrongly convicted and sentenced to life in Deadrock, the 
                  most secure prison in the realm. You know you're innocent, 
                  and staying means death. You must escape, but first you need 
                  allies, resources, and a plan that has never succeeded before.",
  "objectives": [
    "Survive the first week and learn the prison's routines",
    "Gain the trust of veteran inmates who know the layout",
    "Acquire tools through the underground trade network",
    "Discover the weakness in the eastern wall drainage system",
    "Create a distraction during the guard shift change",
    "Navigate the drainage tunnels despite flooding",
    "Reach freedom and evade the pursuit"
  ]
}
```

### War/Conflict

**Structure**: Threat → Preparation → Battle → Victory/Defeat → Aftermath

**Example**:
```json
{
  "title": "The Siege of Last Light Citadel",
  "description": "The Shadow Army approaches. Last Light Citadel is the final 
                  stronghold before the capital. If it falls, the kingdom falls. 
                  You must prepare the defenses, boost morale, and hold the line 
                  long enough for reinforcements to arrive.",
  "objectives": [
    "Assess the citadel's defenses and available forces",
    "Convince neighboring villages to send supplies and fighters",
    "Fortify the weakest wall section before the enemy arrives",
    "Survive the first assault and identify enemy tactics",
    "Lead a raid to destroy enemy siege weapons",
    "Hold the breached wall through the night",
    "Welcome the reinforcements and turn the tide",
    "Pursue and scatter the retreating enemy forces"
  ]
}
```

### Romance/Relationship

**Structure**: Meeting → Bonding → Conflict → Resolution → Commitment

**Example**:
```json
{
  "title": "A Royal Affair",
  "description": "As a common artist commissioned for the royal portrait, you 
                  never expected to capture the heart of the crown prince. But 
                  love between classes is forbidden, and powerful forces conspire 
                  to keep you apart. Navigate court politics, prove your worth, 
                  and fight for a love that defies tradition.",
  "objectives": [
    "Complete the portrait while getting to know the prince",
    "Attend the royal ball as the prince's secret guest",
    "Navigate jealous nobles and scheming advisors",
    "Discover the plot to marry the prince to a foreign princess",
    "Prove your value by exposing the corrupt finance minister",
    "Earn the respect of the king through your talents and character",
    "Choose between love and letting the prince fulfill duty",
    "Find the solution that honors both heart and kingdom"
  ]
}
```

## Integration with Characters

### Character-Objective Synergy

Design objectives that utilize character abilities:

**Character**: Navigator with celestial navigation expertise
**Relevant Objectives**:
```json
"Navigate through the starless Void Sea using only the ancient compass"
"Determine the correct island among dozens by calculating stellar positions"
"Guide the ship through fog using knowledge of ocean currents"
```

**Character**: Diplomatic scholar who reads people well
**Relevant Objectives**:
```json
"Negotiate safe passage with the territorial pirates"
"Determine which council member is the traitor through conversation"
"Convince the hermit to share knowledge of the ancient temple"
```

### Spotlight Moments

Create objectives where each character shines:

```json
{
  "objectives": [
    "Decipher the ancient map's symbols",         // Scholar's moment
    "Navigate through the treacherous reef",      // Navigator's moment
    "Defeat the guardians in single combat",      // Warrior's moment
    "Unlock the magical seal on the vault",       // Mage's moment
    "Persuade the spirit to grant safe passage"   // Diplomat's moment
  ]
}
```

### Character Goals Alignment

Link story objectives to character goals:

**Character Goal**: "Prove worthiness to father's legacy"
**Story Objectives** that advance this:
```json
"Lead the team through the challenge father failed"
"Make the difficult choice father couldn't make"
"Succeed where father's expedition disappeared"
```

The story progression helps character arcs.

## Advanced Techniques

### Branching Hints

While RoleRealm uses linear objectives, you can hint at alternatives:

```json
{
  "title": "The Stolen Artifact",
  "description": "The sacred artifact has been stolen. Recover it by force, 
                  stealth, or negotiation - the choice is yours, but time is running out.",
  "objectives": [
    "Track down the thieves to their hideout",
    "Choose your approach: infiltrate stealthily, attack directly, or offer to trade",
    // The next objectives adapt based on the approach chosen
    "Overcome resistance and secure the artifact",
    "Escape with the artifact before reinforcements arrive"
  ]
}
```

The description suggests options, and character roleplay determines approach.

### Parallel Objectives

Create objectives that can be tackled simultaneously:

```json
{
  "objectives": [
    "Prepare for the festival: Gather information, secure invitations, and plan the heist timing"
  ]
}
```

One objective, multiple aspects - characters can work on different parts.

### Moral Dilemmas

Add depth with ethical choices:

```json
"Decide whether to use the dark ritual to save the village, knowing it requires a sacrifice"
```

Characters with different values will debate, creating rich roleplay.

### Cascading Consequences

Later objectives reference earlier choices:

```json
{
  "objectives": [
    "Steal supplies from the corrupt merchant or buy them honestly",
    "Cross the border checkpoint (harder if you're now wanted for theft)",
    "Seek help from the merchant's guild (impossible if you stole from a member)"
  ]
}
```

This creates a feeling that choices matter.

### Mystery Box Objectives

Build intrigue with mysterious goals:

```json
"Discover what the cryptic message 'The stars will fall when the heir returns' truly means"
```

The objective itself is learning what the objective is!

### Time Pressure

Add urgency:

```json
"Reach the temple before the eclipse ends and the portal closes forever"
```

Creates natural pacing and tension.

### Escalation Through Revelation

Each objective reveals more:

```json
{
  "objectives": [
    "Investigate why ships are disappearing near the island",
    "Discover the island is protected by an ancient sea monster",
    "Learn the monster is controlled by a marooned wizard",
    "Realize the wizard is your mentor, thought dead years ago",
    "Confront your mentor about why he's killing innocents"
  ]
}
```

Each answer raises bigger questions.

## Example Stories

### Complete Story: Fantasy Adventure

```json
{
  "title": "The Shattered Crown",
  "description": "The ancient Crown of Unity, which kept the five kingdoms at peace 
                  for centuries, has shattered into five pieces. Each kingdom now holds 
                  one shard, and old rivalries resurface. As neutral adventurers, you 
                  must recover all five shards and reforge the crown before war erupts 
                  across the land. But each kingdom has its own reason for keeping its 
                  shard, and not all will surrender it willingly.",
  "objectives": [
    "Meet with the Council of Elders to learn the crown's history and the location of each shard",
    "Journey to the Forest Kingdom and earn the Wood Elves' trust by solving the corruption in their sacred grove",
    "Convince the Mountain Dwarves to surrender their shard by proving your worth in their Trial of Steel",
    "Infiltrate the Desert Sultanate's palace during the Festival of Lights to reclaim the stolen shard",
    "Negotiate with the Ocean Kingdom's council while navigating their complex political alliances",
    "Confront the Shadow Kingdom's sorcerer who plans to use his shard to break the crown's protective magic forever",
    "Race to the Forge of Unity with all five shards before the eclipse",
    "Defend the forge from the Shadow Kingdom's army while the crown is being reforged",
    "Return the restored crown to the Council and broker a lasting peace between the kingdoms"
  ],
  "current_objective_index": 0
}
```

### Complete Story: Sci-Fi Mystery

```json
{
  "title": "Signal from the Dead Star",
  "description": "Your research vessel picks up an impossible signal from Kepler-442b, 
                  a star that went supernova three centuries ago. The signal is clearly 
                  artificial and contains coordinates to a location within the nebula. 
                  Against protocol, your captain decides to investigate. What you find 
                  there will challenge everything humanity thought it knew about the 
                  universe, time, and our place in it.",
  "objectives": [
    "Analyze the mysterious signal and decode its mathematical message",
    "Navigate through the radiation-heavy nebula to reach the coordinates",
    "Discover the massive ancient structure floating in the dead star's remains",
    "Board the structure despite its active defense systems",
    "Uncover evidence that a previous human expedition reached here... 200 years from now",
    "Access the central AI that's been waiting for you specifically",
    "Learn that the structure is a time-anchor preventing a future catastrophe",
    "Decide whether to destroy the anchor and prevent the dark future, or preserve it and doom your own timeline",
    "Deal with the consequences of your choice as reality begins to shift"
  ],
  "current_objective_index": 0
}
```

### Complete Story: Urban Fantasy

```json
{
  "title": "The Night Market",
  "description": "In modern London, a hidden world exists just beneath the surface. 
                  The Night Market appears only during the new moon, a bazaar where 
                  magical beings trade in impossible goods. Your best friend has gone 
                  missing after visiting the market, and you've discovered you have 
                  just enough magical blood to see it yourself. Find your friend, but 
                  be careful - everything in the Night Market has a price, and not 
                  all costs are paid in coin.",
  "objectives": [
    "Locate the Night Market's entrance hidden in the abandoned Underground station",
    "Navigate the market's confusing layout while avoiding drawing attention from dangerous beings",
    "Trade information with the goblin merchant about your friend's last known location",
    "Win a game of chance against the fate-weaver to earn passage to the restricted section",
    "Discover your friend made a deal with the Shadow Broker and is bound by contract",
    "Find a loophole in the contract by consulting the ancient Sphinx in the Court of Whispers",
    "Challenge the Shadow Broker according to the old rules of the market",
    "Pay the price for your friend's freedom (sacrifice something precious of your own)",
    "Escape before the market vanishes and you're trapped until the next new moon"
  ],
  "current_objective_index": 0
}
```

---

**Last Updated**: December 2025  
**Author**: Jit Roy  
**License**: MIT
