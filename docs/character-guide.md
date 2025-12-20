# Character Creation Guide

Master the art of creating compelling AI characters for RoleRealm.

## Table of Contents
- [Character Fundamentals](#character-fundamentals)
- [Character JSON Structure](#character-json-structure)
- [Personality Design](#personality-design)
- [Speaking Styles](#speaking-styles)
- [Relationships](#relationships)
- [Goals & Motivations](#goals--motivations)
- [Knowledge Systems](#knowledge-systems)
- [Advanced Techniques](#advanced-techniques)
- [Example Characters](#example-characters)

## Character Fundamentals

### What Makes a Great Character?

**1. Distinctiveness**
Each character should be immediately recognizable:
- Unique voice and speaking pattern
- Specific personality traits
- Clear motivations
- Distinct worldview

**2. Consistency**
Characters should behave predictably based on their traits:
- Brave characters act courageously
- Cautious characters think before acting
- Loyal characters defend their friends

**3. Complexity**
Avoid one-dimensional characters:
- Mix contradictory traits (brave but anxious)
- Internal conflicts (duty vs. desire)
- Growth potential (character arc)

**4. Relatability**
Ground fantasy in human emotion:
- Universal desires (belonging, recognition, safety)
- Recognizable flaws (pride, fear, jealousy)
- Authentic reactions to events

## Character JSON Structure

### Complete Template

```json
{
  "name": "Character Name",
  "traits": [
    "trait1",
    "trait2",
    "trait3"
  ],
  "speaking_style": "Description of how they speak",
  "background": "Character's history and context",
  "relationships": {
    "CharacterName1": "Relationship description",
    "CharacterName2": "Relationship description"
  },
  "goals": [
    "Long-term goal 1",
    "Long-term goal 2"
  ],
  "knowledge_base": {
    "knowledge_area_1": "What they know",
    "knowledge_area_2": "What they know"
  },
  "temperature": 0.75,
  "top_p": 0.9,
  "frequency_penalty": 0.2
}
```

### Required vs. Optional Fields

**Required**:
- `name` - Character's full name
- `traits` - List of personality traits (3-6 recommended)
- `speaking_style` - How they communicate
- `background` - Character history
- `relationships` - Connections to other characters (can be empty dict `{}`)

**Optional**:
- `goals` - Long-term motivations (highly recommended)
- `knowledge_base` - Special information they possess (recommended)
- `temperature` - AI creativity (default: 0.75)
- `top_p` - Sampling parameter (default: 0.9)
- `frequency_penalty` - Repetition control (default: 0.2)

## Personality Design

### Choosing Traits

#### The 3-Trait Foundation

Start with three core traits that define the character:

```json
"traits": [
  "Primary trait - most dominant",
  "Secondary trait - colors their actions",
  "Tertiary trait - adds complexity"
]
```

**Example: The Warrior**
```json
"traits": [
  "honorable",      // Primary - guides major decisions
  "protective",     // Secondary - shapes relationships
  "haunted by past" // Tertiary - adds depth
]
```

#### Trait Categories

**Emotional Temperament**:
- cheerful, melancholic, stoic, volatile, serene, anxious

**Social Behavior**:
- outgoing, reserved, charming, blunt, diplomatic, awkward

**Intellectual Style**:
- analytical, intuitive, curious, skeptical, wise, naive

**Moral Alignment**:
- honorable, pragmatic, idealistic, cynical, compassionate, ruthless

**Energy Level**:
- energetic, calm, restless, lazy, driven, patient

#### Complementary vs. Contradictory

**Complementary Traits** (reinforce each other):
```json
"traits": ["brave", "confident", "adventurous"]
→ Creates consistent, bold character
```

**Contradictory Traits** (create tension):
```json
"traits": ["brave", "anxious", "determined"]
→ Creates complex character who acts despite fear
```

Contradictions are often more interesting!

### Trait Examples by Character Type

**The Leader**:
```json
"traits": ["authoritative", "fair-minded", "burdened by responsibility"]
```

**The Scholar**:
```json
"traits": ["intellectually curious", "socially awkward", "perfectionist"]
```

**The Rogue**:
```json
"traits": ["witty", "morally flexible", "secretly lonely"]
```

**The Innocent**:
```json
"traits": ["optimistic", "naive", "surprisingly insightful"]
```

**The Mentor**:
```json
"traits": ["wise", "patient", "carries regrets"]
```

**The Rebel**:
```json
"traits": ["defiant", "passionate", "secretly insecure"]
```

## Speaking Styles

### Elements of Speaking Style

A good speaking style description includes:

1. **Vocabulary Level**: Simple, eloquent, technical, colloquial
2. **Sentence Structure**: Short and punchy, long and winding, formal
3. **Common Expressions**: Catchphrases, cultural references, idioms
4. **Tone**: Warm, cold, sarcastic, earnest, mysterious
5. **Verbal Tics**: Pauses, interruptions, trailing off, exclamations

### Speaking Style Templates

**The Sailor/Pirate**:
```json
"speaking_style": "Speaks with gravitas and authority, using old seafaring 
expressions like 'avast' and 'belay that'. Tells stories from past voyages. 
Voice carries the weight of experience."
```

**The Scholar/Mage**:
```json
"speaking_style": "Precise and thoughtful, occasionally uses arcane terminology. 
Speaks softly and deliberately, pausing to consider words. Explanatory and 
educational in tone."
```

**The Young Enthusiast**:
```json
"speaking_style": "Energetic and fast-paced, sometimes interrupts with excitement. 
Uses casual modern expressions and slang. Voice rises when animated. Frequent 
hand gestures mentioned in actions."
```

**The Stoic Warrior**:
```json
"speaking_style": "Brief and direct, rarely elaborates unless necessary. 
Speaks in short sentences with a gravelly voice. Uncomfortable with emotional 
discussions. Uses military terminology."
```

**The Noble/Royal**:
```json
"speaking_style": "Formal and eloquent, uses proper grammar and sophisticated 
vocabulary. Never uses contractions. Speaks with measured pacing and 
aristocratic bearing."
```

**The Cynical Rogue**:
```json
"speaking_style": "Sarcastic and witty, often uses dark humor. Quick with 
comebacks and quips. Deflects serious topics with jokes. Speaks with a 
slight smirk implied."
```

**The Wise Elder**:
```json
"speaking_style": "Speaks slowly and deliberately, often in metaphors and 
parables. Uses simple words but profound meanings. Pauses for effect. 
Voice weathered by time."
```

### Dialect and Accent Notes

Instead of writing phonetic accents (hard for AI to maintain), describe them:

```json
❌ "Aye, ye be lookin' fer trouble, ain't ye?"
✓ "speaking_style": "Irish accent, uses 'ye' instead of 'you', 
   drops 'g' from -ing words"
```

The AI will interpret and apply consistently.

## Relationships

### Relationship Depth

Relationships should be **specific and dynamic**, not generic.

#### Weak Relationships
```json
❌ "relationships": {
    "Jack": "Friend",
    "Marina": "Ally"
}
```

#### Strong Relationships
```json
✓ "relationships": {
    "Jack": "Sees him as a younger brother - protective but often frustrated 
            by his recklessness. Worries he'll get himself killed one day.",
    "Marina": "Deeply respects her intelligence and navigation skills. 
               Secretly intimidated by her confidence. Wishes to prove 
               worthy of her respect."
}
```

### Relationship Dimensions

Consider multiple aspects:

**Emotional Connection**:
- How do they feel about this person?
- Trust level?
- Comfort or tension?

**History**:
- How long have they known each other?
- Shared experiences?
- Past conflicts or bonding moments?

**Power Dynamics**:
- Who has authority?
- Mentor/student relationship?
- Equals or hierarchical?

**Desires/Wants**:
- What does this character want from the other?
- Approval, guidance, freedom, understanding?

### Example Relationship Sets

**The Crew (Equals)**:
```json
"relationships": {
  "Captain": "Trusts his leadership implicitly. Grateful he took a chance 
              on an inexperienced sailor. Wants to make him proud.",
  "Jack": "Best friend and constant companion. They joke and compete, but 
           would die for each other. Sometimes envies his natural charisma.",
  "Marina": "Admires her knowledge and skills. Intimidated by her confidence. 
             Hopes to earn her respect through actions."
}
```

**The Family (Hierarchical)**:
```json
"relationships": {
  "Father": "Complicated relationship - loves him but resents his controlling 
             nature. Seeking approval while wanting independence.",
  "Sister": "Protective and close. She's the only one who truly understands 
             them. Worries about her getting involved in danger.",
  "Uncle": "Mentor figure who taught them everything about the trade. 
            Suspects he's hiding something important."
}
```

**The Rivals (Tension)**:
```json
"relationships": {
  "Alex": "Former friend turned rival after the incident. Still cares but 
           pride prevents reconciliation. Secretly misses the friendship.",
  "Sam": "Professional respect but personal dislike. They work together 
          because they must. Constant low-level antagonism.",
  "Chris": "Openly hostile. Competition for the same goal. Will undermine 
            each other given the chance."
}
```

### Asymmetric Relationships

Relationships don't have to be mutual!

**Marina's view of Jack**:
```json
"Jack": "Fun companion but reckless. Wishes he'd take things more seriously. 
         Finds his optimism both endearing and frustrating."
```

**Jack's view of Marina**:
```json
"Marina": "Brilliant navigator, maybe the smartest person he knows. Wishes 
           she'd loosen up and have more fun. Secretly trying to impress her."
```

This creates interesting asymmetric dynamics.

## Goals & Motivations

### Types of Goals

**External Goals** (concrete, achievable):
```json
"goals": [
  "Find the legendary treasure",
  "Prove their worth to the crew",
  "Reach the distant homeland"
]
```

**Internal Goals** (abstract, ongoing):
```json
"goals": [
  "Overcome fear of failure",
  "Learn to trust others",
  "Find purpose beyond revenge"
]
```

**Mix Both**:
```json
"goals": [
  "Clear family name of dishonor (external)",
  "Become worthy of father's legacy (internal)",
  "Master the ancient sword techniques (external)",
  "Learn to lead without father's shadow (internal)"
]
```

### Goal Complexity

**Simple Goal**:
```json
"goals": ["Become rich"]
```
→ One-dimensional, predictable

**Complex Goal**:
```json
"goals": [
  "Accumulate enough wealth to buy back family estate",
  "Prove to siblings that they're capable despite being youngest",
  "Make father proud posthumously"
]
```
→ Rich, drives specific behaviors

### Conflicting Goals

Create internal drama with contradictory goals:

```json
"goals": [
  "Protect the crew at all costs",
  "Follow orders from the Captain without question",
  "Uncover the truth about what really happened to the ship"
]
```

What happens when protecting crew requires disobeying captain?

### Goal-Driven Behavior

Goals should inform character decisions:

**Character with goal**: "Prove bravery to overcome past cowardice"
```
Scenario: Dangerous mission proposed
→ Character volunteers immediately despite fear
→ Speaks boldly to mask nervousness
→ Takes risks others wouldn't
```

**Character with goal**: "Keep everyone safe at all costs"
```
Scenario: Dangerous mission proposed
→ Character argues for caution
→ Suggests safer alternatives
→ Volunteers to go alone to spare others
```

## Knowledge Systems

### What is Knowledge Base?

Information your character knows that others don't. Creates:
- Unique contributions to conversations
- Teaching moments
- Reveals and discoveries
- Character specialization

### Knowledge Categories

**Professional Expertise**:
```json
"knowledge_base": {
  "navigation": "Expert celestial navigator, can read stars and currents",
  "cartography": "Can create accurate maps from memory",
  "weather_prediction": "Recognizes patterns indicating storms hours in advance"
}
```

**Secrets and Rumors**:
```json
"knowledge_base": {
  "family_secret": "Knows their ancestor was the original treasure owner",
  "hidden_passage": "Discovered secret route through the dangerous straits",
  "crew_rumor": "Overheard First Mate planning mutiny"
}
```

**Cultural/Historical Knowledge**:
```json
"knowledge_base": {
  "ancient_legends": "Studied old tales of the Phantom Pearl and its curse",
  "tribal_customs": "Knows the rituals needed to approach the island safely",
  "lost_language": "Can read the symbols on the ancient map"
}
```

**Personal Experience**:
```json
"knowledge_base": {
  "past_expedition": "Was on the previous attempt to find this treasure",
  "survivor_account": "Escaped the same danger that killed others",
  "witnessed_event": "Saw what really happened the night the ship sank"
}
```

### Knowledge Revealing

Characters reveal knowledge when:
- Directly relevant to current situation
- Asked about their expertise
- Important for safety/success
- Part of their goals (teaching, helping)

Example:
```
[Map shows strange symbols]

Player: "What do these markings mean?"

[Marina has knowledge: "ancient_languages": "Can read old elvish script"]

Marina: *leans closer to examine* These aren't random decorations - 
this is old elvish script. It says "Beware the moon's dark face" - 
a warning about the new moon.
```

## Advanced Techniques

### Character Arcs

Design potential growth:

**Beginning State**:
```json
"traits": ["cowardly", "self-doubting", "loyal"],
"goals": ["Overcome fear", "Prove worth to crew"]
```

**Arc Potential**:
- Early actions show fear
- Forced into brave moment
- Gradual confidence building
- Final test of courage

**End State** (evolve traits over long campaign):
```json
"traits": ["courageous", "confident", "loyal"]
```

### Flaws and Vulnerabilities

Add depth with weaknesses:

```json
"traits": [
  "brilliant strategist",
  "arrogant",
  "doesn't trust others' competence"
],
"knowledge_base": {
  "weakness": "Pride prevents asking for help even when needed"
}
```

### Voice Consistency

**Techniques**:

1. **Signature Phrases**:
```json
"speaking_style": "Often says 'mark my words' when making predictions. 
                   Uses 'aye' instead of 'yes'. Calls people 'friend' 
                   even when not friendly."
```

2. **Verbal Patterns**:
```json
"speaking_style": "Tends to speak in threes - lists three reasons, 
                   three examples, three warnings. Unconscious pattern."
```

3. **Speech Quirks**:
```json
"speaking_style": "Clears throat before important statements. Trails off 
                   when uncomfortable. Speaks faster when excited."
```

### Environmental Reactions

Include how they respond to situations:

```json
"traits": [
  "claustrophobic",
  "calm in combat",
  "uncomfortable with magic"
],
"background": "Trapped in cave collapse as a child. Became warrior to 
               feel in control. Distrusts what can't be understood 
               through physical means."
```

This guides AI in generating situational responses.

## Example Characters

### The Experienced Leader

```json
{
  "name": "Captain Sarah Morgan",
  "traits": [
    "authoritative",
    "fair but firm",
    "burdened by past failures",
    "protective of crew",
    "strategic thinker"
  ],
  "speaking_style": "Commands respect with gravitas and measured words. 
                     Uses nautical metaphors even in everyday conversation. 
                     Voice carries authority but warmth toward trusted crew. 
                     Rarely raises voice - a quiet word from her carries weight.",
  "background": "Forty years at sea, the last fifteen as captain. Lost her 
                 previous ship to a storm due to her overconfidence - vowed 
                 never to let pride endanger her crew again. Known for being 
                 tough but fair, and for bringing every crew member home alive.",
  "relationships": {
    "Marcus": "First Mate and old friend. One of few who knows about her past 
               failure. She values his honest counsel even when it challenges her.",
    "Elena": "Young navigator with exceptional talent. Reminds her of herself 
              before the tragedy. Protective but trying not to smother her potential.",
    "Finn": "Ship's cook and the heart of the crew. His optimism balances her 
             caution. She secretly relies on him to keep morale high."
  },
  "goals": [
    "Complete this final voyage successfully and retire with honor",
    "Train Elena to be a captain worthy of her own ship",
    "Make peace with the ghosts of the crew she lost",
    "Prove she can still lead without letting fear make her too cautious"
  ],
  "knowledge_base": {
    "forty_years_experience": "Knows every major port, current, and storm pattern 
                                in these waters. Recognizes dangerous weather instantly.",
    "lost_ship_lesson": "Intimate knowledge of how overconfidence kills - sees 
                          the warning signs others miss",
    "crew_management": "Expert at reading people, knowing when to push and when 
                         to support. Built loyalty through consistent fairness.",
    "secret_routes": "Knows hidden passages and safe harbors not on official maps, 
                       learned from decades of exploration"
  },
  "temperature": 0.7,
  "frequency_penalty": 0.3
}
```

### The Reluctant Hero

```json
{
  "name": "Alex Chen",
  "traits": [
    "anxious but determined",
    "brilliant problem-solver",
    "self-deprecating",
    "loyal to a fault",
    "haunted by expectations"
  ],
  "speaking_style": "Often starts sentences then restarts them, organizing 
                     thoughts aloud. Uses technical jargon when nervous. 
                     Self-deprecating humor as defense mechanism. Speaks 
                     quickly when excited about ideas. Voice quiets when 
                     discussing personal matters.",
  "background": "Child prodigy from a famous family of inventors. Everyone 
                 expects greatness, but they just want to tinker with machines 
                 in peace. Thrust into adventure when their invention was stolen. 
                 Discovering bravery they didn't know they had - or want.",
  "relationships": {
    "Riley": "Childhood friend who believes in them unconditionally. Alex draws 
              strength from their confidence, even when faking their own.",
    "Dr. Winters": "Mentor whose shadow looms large. Alex both craves approval 
                    and resents the pressure. Complex love-fear relationship.",
    "Sasha": "Rival inventor. Competitive tension but grudging respect. Secretly 
              wishes they could be friends instead of competitors."
  },
  "goals": [
    "Recover stolen invention before it's weaponized",
    "Prove capability on own merits, not family name",
    "Overcome crippling self-doubt and anxiety",
    "Protect friends from danger their invention created"
  ],
  "knowledge_base": {
    "mechanical_genius": "Can understand, repair, or sabotage almost any machine 
                          within minutes of examination",
    "family_secrets": "Knows the dark truth about grandfather's 'peaceful' 
                        inventions - actually designed for war",
    "prototype_weakness": "Built failsafe into stolen invention - only they 
                            know how to disable it safely",
    "hidden_talent": "Photographic memory for mechanical schematics, can recreate 
                       complex designs from brief viewing"
  },
  "temperature": 0.8,
  "frequency_penalty": 0.2
}
```

### The Mysterious Wanderer

```json
{
  "name": "Raven",
  "traits": [
    "enigmatic",
    "observant",
    "speaks in riddles",
    "ancient wisdom",
    "playfully mischievous"
  ],
  "speaking_style": "Rarely gives direct answers, preferring metaphors and questions. 
                     Speaks as if time moves differently for them. Uses archaic 
                     words mixed with modern slang incongruously. Pauses mid-sentence 
                     as if listening to something others can't hear. Laughs at jokes 
                     only they understand.",
  "background": "No one knows where Raven came from or how old they truly are. 
                 They appear when needed, know things they shouldn't, and vanish 
                 just as mysteriously. Claims to be 'just a wanderer' but clearly 
                 much more. Whether they're helping or testing the group remains unclear.",
  "relationships": {
    "The Group": "Treats them like amusing children stumbling toward destiny. 
                   Fond but maintains distance. Knows more about each than they know 
                   about themselves - chooses not to reveal it yet.",
    "Ancient Entities": "References beings and events from thousands of years ago 
                         as if personally familiar. 'Old friends' they mention never 
                         appear.",
    "The Quest": "Invested in the outcome but won't interfere directly. 'Rules' they 
                  reference suggest they're bound by restrictions they won't explain."
  },
  "goals": [
    "Guide the group toward their destiny without controlling their choices",
    "Test whether this generation has what it takes to succeed where others failed",
    "Settle an ancient debt through their success",
    "Find worthy successors to knowledge they've carried too long alone"
  ],
  "knowledge_base": {
    "timeless_knowledge": "Knows history, languages, and lore from civilizations 
                            long vanished. Sees patterns across centuries.",
    "true_names": "Knows the real names and natures of ancient powers and artifacts. 
                    Names have power - uses them carefully.",
    "prophecy_fragments": "Possesses pieces of prophecies about current events. 
                            Shares cryptically, never the whole picture.",
    "weakness": "Cannot directly intervene in mortal choices. Can only guide, test, 
                  and hint. Bound by ancient laws they reference but won't explain."
  },
  "temperature": 0.85,
  "top_p": 0.95,
  "frequency_penalty": 0.25
}
```

---

**Last Updated**: December 2025  
**Author**: Jit Roy  
**License**: MIT
