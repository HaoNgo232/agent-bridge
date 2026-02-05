---
name: frontend-design
description: Expert toolkit for frontend-design
---

# Frontend Design System

> **Philosophy:** Every pixel has purpose. Restraint is luxury. User psychology drives decisions.
> **Core Principle:** THINK, don't memorize. ASK, don't assume.

---

## 🎯 Selective Reading Rule (MANDATORY)

**Read REQUIRED files always, OPTIONAL only when needed:**

| File | Status | When to Read |
|------|--------|--------------|
| [ux-psychology.md](ux-psychology.md) | 🔴 **REQUIRED** | Always read first! |
| [color-system.md](color-system.md) | ⚪ Optional | Color/palette decisions |
| [typography-system.md](typography-system.md) | ⚪ Optional | Font selection/pairing |
| [visual-effects.md](visual-effects.md) | ⚪ Optional | Glassmorphism, shadows, gradients |
| [animation-guide.md](animation-guide.md) | ⚪ Optional | Animation needed |
| [motion-graphics.md](motion-graphics.md) | ⚪ Optional | Lottie, GSAP, 3D |
| [decision-trees.md](decision-trees.md) | ⚪ Optional | Context templates |

> 🔴 **ux-psychology.md = ALWAYS READ. Others = only if relevant.**

---

## 🔧 Runtime Scripts

**Execute these for audits (don't read, just run):**

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/ux_audit.py` | UX Psychology & Accessibility Audit | `python scripts/ux_audit.py <project_path>` |

---

## ⚠️ CRITICAL: ASK BEFORE ASSUMING (MANDATORY)

> **STOP! If the user's request is open-ended, DO NOT default to your favorites.**

### When User Prompt is Vague, ASK:

**Color not specified?** Ask:
> "What color palette do you prefer? (blue/green/orange/neutral/other?)"

**Style not specified?** Ask: 
> "What style are you going for? (minimal/bold/retro/futuristic/organic?)"

**Layout not specified?** Ask:
> "Do you have a layout preference? (single column/grid/asymmetric/full-width?)"

### ⛔ DEFAULT TENDENCIES TO AVOID (ANTI-SAFE HARBOR):

| AI Default Tendency | Why It's Bad | Think Instead |
|---------------------|--------------|---------------|
| **Bento Grids (Modern Cliché)** | Used in every AI design | Why does this content NEED a grid? |
| **Hero Split (Left/Right)** | Predictable & Boring | How about Massive Typography or Vertical Narrative? |
| **Mesh/Aurora Gradients** | The "new" lazy background | What's a radical color pairing? |
| **Glassmorphism** | AI's idea of "premium" | How about solid, high-contrast flat? |
| **Deep Cyan / Fintech Blue** | Safe harbor from purple ban | Why not Red, Black, or Neon Green? |
| **"Orchestrate / Empower"** | AI-generated copywriting | How would a human say this? |
| Dark background + neon glow | Overused, "AI look" | What does the BRAND actually need? |
| **Rounded everything** | Generic/Safe | Where can I use sharp, brutalist edges? |

> 🔴 **"Every 'safe' structure you choose brings you one step closer to a generic template. TAKE RISKS."**

---

## 1. Constraint Analysis (ALWAYS FIRST)

Before any design work, ANSWER THESE or ASK USER:

| Constraint | Question | Why It Matters |
|------------|----------|----------------|
| **Timeline** | How much time? | Determines complexity |
| **Content** | Ready or placeholder? | Affects layout flexibility |
| **Brand** | Existing guidelines? | May dictate colors/fonts |
| **Tech** | What stack? | Affects capabilities |
| **Audience** | Who exactly? | Drives all visual decisions |

### Audience → Design Approach

| Audience | Think About |
|----------|-------------|
| **Gen Z** | Bold, fast, mobile-first, authentic |
| **Millennials** | Clean, minimal, value-driven |
| **Gen X** | Familiar, trustworthy, clear |
| **Boomers** | Readable, high contrast, simple |
| **B2B** | Professional, data-focused, trust |
| **Luxury** | Restrained elegance, whitespace |

---

## 2. UX Psychology Principles

### Core Laws (Internalize These)

| Law | Principle | Application |
|-----|-----------|-------------|
| **Hick's Law** | More choices = slower decisions | Limit options, use progressive disclosure |
| **Fitts' Law** | Bigger + closer = easier to click | Size CTAs appropriately |
| **Miller's Law** | ~7 items in working memory | Chunk content into groups |
| **Von Restorff** | Different = memorable | Make CTAs visually distinct |
| **Serial Position** | First/last remembered most | Key info at start/end |

### Emotional Design Levels

```
VISCERAL (instant)  → First impression: colors, imagery, overall feel
BEHAVIORAL (use)    → Using it: speed, feedback, efficiency
REFLECTIVE (memory) → After: "I like what this says about me"
```

### Trust Building

- Security indicators on sensitive actions
- Social proof where relevant
- Clear contact/support access
- Consistent, professional design
- Transparent policies

---

## 3. Layout Principles

### Golden Ratio (φ = 1.618)

```
Use for proportional harmony:
├── Content : Sidebar = roughly 62% : 38%
├── Each heading size = previous × 1.618 (for dramatic scale)
├── Spacing can follow: sm → md → lg (each × 1.618)
```

### 8-Point Grid Concept

```
All spacing and sizing in multiples of 8:
├── Tight: 4px (half-step for micro)
├── Small: 8px
├── Medium: 16px
├── Large: 24px, 32px
├── XL: 48px, 64px, 80px
└── Adjust based on content density
```

### Key Sizing Principles

| Element | Consideration |
|---------|---------------|
| **Touch targets** | Minimum comfortable tap size |
| **Buttons** | Height based on importance hierarchy |
| **Inputs** | Match button height for alignment |
| **Cards** | Consistent padding, breathable |
| **Reading width** | 45-75 characters optimal |

---

## 4. Color Principles

### 60-30-10 Rule

```
60% → Primary/Background (calm, neutral base)
30% → Secondary (supporting areas)
10% → Accent (CTAs, highlights, attention)
```

### Color Psychology (For Decision Making)

| If You Need... | Consider Hues | Avoid |
|----------------|---------------|-------|
| Trust, calm | Blue family | Aggressive reds |
| Growth, nature | Green family | Industrial grays |
| Energy, urgency | Orange, red | Passive blues |
| Luxury, creativity | Deep Teal, Gold, Emerald | Cheap-feeling brights |
| Clean, minimal | Neutrals | Overwhelming color |

### Selection Process

1. **What's the industry?** (narrows options)
2. **What's the emotion?** (picks primary)
3. **Light or dark mode?** (sets foundation)
4. **ASK USER** if not specified

For detailed color theory: [color-system.md](color-system.md)

---

## 5. Typography Principles

### Scale Selection

| Content Type | Scale Ratio | Feel |
|--------------|-------------|------|
| Dense UI | 1.125-1.2 | Compact, efficient |
| General web | 1.25 | Balanced (most common) |
| Editorial | 1.333 | Readable, spacious |
| Hero/display | 1.5-1.618 | Dramatic impact |

### Pairing Concept

```
Contrast + Harmony:
├── DIFFERENT enough for hierarchy
├── SIMILAR enough for cohesion
└── Usually: display + neutral, or serif + sans
```

### Readability Rules

- **Line length**: 45-75 characters optimal
- **Line height**: 1.4-1.6 for body text
- **Contrast**: Check WCAG requirements
- **Size**: 16px+ for body on web

For detailed typography: [typography-system.md](typography-system.md)

---

## 6. Visual Effects Principles

### Glassmorphism (When Appropriate)

```
Key properties:
├── Semi-transparent background
├── Backdrop blur
├── Subtle border for definition
└── ⚠️ **WARNING:** Standard blue/white glassmorphism is a modern cliché. Use it radically or not at all.
```

### Shadow Hierarchy

```
Elevation concept:
├── Higher elements = larger shadows
├── Y-offset > X-offset (light from above)
├── Multiple layers = more realistic
└── Dark mode: may need glow instead
```

### Gradient Usage

```
Harmonious gradients:
├── Adjacent colors on wheel (analogous)
├── OR same hue, different lightness
├── Avoid harsh complementary pairs
├── 🚫 **NO Mesh/Aurora Gradients** (floating blobs)
└── VARY from project to project radically
```

For complete effects guide: [visual-effects.md](visual-effects.md)

---

## 7. Animation Principles

### Timing Concept

```
Duration based on:
├── Distance (further = longer)
├── Size (larger = slower)
├── Importance (critical = clear)
└── Context (urgent = fast, luxury = slow)
```

### Easing Selection

| Action | Easing | Why |
|--------|--------|-----|
| Entering | Ease-out | Decelerate, settle in |
| Leaving | Ease-in | Accelerate, exit |
| Emphasis | Ease-in-out | Smooth, deliberate |
| Playful | Bounce | Fun, energetic |

### Performance

- Animate only transform and opacity
- Respect reduced-motion preference
- Test on low-end devices

For animation patterns: [animation-guide.md](animation-guide.md), for advanced: [motion-graphics.md](motion-graphics.md)

---

## 8. "Wow Factor" Checklist

### Premium Indicators

- [ ] Generous whitespace (luxury = breathing room)
- [ ] Subtle depth and dimension
- [ ] Smooth, purposeful animations
- [ ] Attention to detail (alignment, consistency)
- [ ] Cohesive visual rhythm
- [ ] Custom elements (not all defaults)

### Trust Builders

- [ ] Security cues where appropriate
- [ ] Social proof / testimonials
- [ ] Clear value proposition
- [ ] Professional imagery
- [ ] Consistent design language

### Emotional Triggers

- [ ] Hero that evokes intended emotion
- [ ] Human elements (faces, stories)
- [ ] Progress/achievement indicators
- [ ] Moments of delight

---

## 9. Anti-Patterns (What NOT to Do)

### ❌ Lazy Design Indicators

- Default system fonts without consideration
- Stock imagery that doesn't match
- Inconsistent spacing
- Too many competing colors
- Walls of text without hierarchy
- Inaccessible contrast

### ❌ AI Tendency Patterns (AVOID!)

- **Same colors every project**
- **Dark + neon as default**
- **Purple/violet everything (PURPLE BAN ✅)**
- **Bento grids for simple landing pages**
- **Mesh Gradients & Glow Effects**
- **Same layout structure / Vercel clone**
- **Not asking user preferences**

### ❌ Dark Patterns (Unethical)

- Hidden costs
- Fake urgency
- Forced actions
- Deceptive UI
- Confirmshaming

---

## 10. Decision Process Summary

```
For EVERY design task:

1. CONSTRAINTS
   └── What's the timeline, brand, tech, audience?
   └── If unclear → ASK

2. CONTENT
   └── What content exists?
   └── What's the hierarchy?

3. STYLE DIRECTION
   └── What's appropriate for context?
   └── If unclear → ASK (don't default!)

4. EXECUTION
   └── Apply principles above
   └── Check against anti-patterns

5. REVIEW
   └── "Does this serve the user?"
   └── "Is this different from my defaults?"
   └── "Would I be proud of this?"
```

---

## Reference Files

For deeper guidance on specific areas:

- [color-system.md](color-system.md) - Color theory and selection process
- [typography-system.md](typography-system.md) - Font pairing and scale decisions
- [visual-effects.md](visual-effects.md) - Effects principles and techniques
- [animation-guide.md](animation-guide.md) - Motion design principles
- [motion-graphics.md](motion-graphics.md) - Advanced: Lottie, GSAP, SVG, 3D, Particles
- [decision-trees.md](decision-trees.md) - Context-specific templates
- [ux-psychology.md](ux-psychology.md) - User psychology deep dive

---

## Related Skills

| Skill | When to Use |
|-------|-------------|
| **frontend-design** (this) | Before coding - Learn design principles (color, typography, UX psychology) |
| **[web-design-guidelines](../web-design-guidelines/SKILL.md)** | After coding - Audit for accessibility, performance, and best practices |

## Post-Design Workflow

After implementing your design, run the audit:

```
1. DESIGN   → Read frontend-design principles ← YOU ARE HERE
2. CODE     → Implement the design
3. AUDIT    → Run web-design-guidelines review
4. FIX      → Address findings from audit
```

> **Next Step:** After coding, use `web-design-guidelines` skill to audit your implementation for accessibility, focus states, animations, and performance issues.

---

> **Remember:** Design is THINKING, not copying. Every project deserves fresh consideration based on its unique context and users. **Avoid the Modern SaaS Safe Harbor!**


---

# Animation Guidelines Reference

> Animation principles and timing psychology - learn to decide, not copy.
> **No fixed durations to memorize - understand what affects timing.**

---

## 1. Duration Principles

### What Affects Timing

```
Factors that determine animation speed:
├── DISTANCE: Further travel = longer duration
├── SIZE: Larger elements = slower animations
├── COMPLEXITY: Complex = slower to process
├── IMPORTANCE: Critical actions = clear feedback
└── CONTEXT: Urgent = fast, luxurious = slow
```

### Duration Ranges by Purpose

| Purpose | Range | Why |
|---------|-------|-----|
| Instant feedback | 50-100ms | Below perception threshold |
| Micro-interactions | 100-200ms | Quick but noticeable |
| Standard transitions | 200-300ms | Comfortable pace |
| Complex animations | 300-500ms | Time to follow |
| Page transitions | 400-600ms | Smooth handoff |
| **Wow/Premium Effects** | 800ms+ | Dramatic, organic spring-based, layered |

### Choosing Duration

Ask yourself:
1. How far is the element moving?
2. How important is it to notice this change?
3. Is the user waiting, or is this background?

---

## 2. Easing Principles

### What Easing Does

```
Easing = how speed changes over time
├── Linear: constant speed (mechanical, robotic)
├── Ease-out: fast start, slow end (natural entry)
├── Ease-in: slow start, fast end (natural exit)
└── Ease-in-out: slow both ends (smooth, deliberate)
```

### When to Use Each

| Easing | Best For | Feels Like |
|--------|----------|------------|
| **Ease-out** | Elements entering | Arriving, settling |
| **Ease-in** | Elements leaving | Departing, exiting |
| **Ease-in-out** | Emphasis, loops | Deliberate, smooth |
| **Linear** | Continuous motion | Mechanical, constant |
| **Bounce/Elastic** | Playful UI | Fun, energetic |

### The Pattern

```css
/* Entering view = ease-out (decelerate) */
.enter {
  animation-timing-function: ease-out;
}

/* Leaving view = ease-in (accelerate) */
.exit {
  animation-timing-function: ease-in;
}

/* Continuous = ease-in-out */
.continuous {
  animation-timing-function: ease-in-out;
}
```

---

## 3. Micro-Interaction Principles

### What Makes Good Micro-Interactions

```
Purpose of micro-interactions:
├── FEEDBACK: Confirm the action happened
├── GUIDANCE: Show what's possible
├── STATUS: Indicate current state
└── DELIGHT: Small moments of joy
```

### Button States

```
Hover → slight visual change (lift, color, scale)
Active → pressed feeling (scale down, shadow change)
Focus → clear indicator (outline, ring)
Loading → progress indicator (spinner, skeleton)
Success → confirmation (check, color)
```

### Principles

1. **Respond immediately** (under 100ms perception)
2. **Match the action** (press = `scale(0.95)`, hover = `translateY(-4px) + glow`)
3. **Be bold but smooth** (Usta işi hissettir)
4. **Be consistent** (same actions = same feedback)

---

## 4. Loading States Principles

### Types by Context

| Situation | Approach |
|-----------|----------|
| Quick load (<1s) | No indicator needed |
| Medium (1-3s) | Spinner or simple animation |
| Long (3s+) | Progress bar or skeleton |
| Unknown duration | Indeterminate indicator |

### Skeleton Screens

```
Purpose: Reduce perceived wait time
├── Show layout shape immediately
├── Animate subtly (shimmer, pulse)
├── Replace with content when ready
└── Feels faster than spinner
```

### Progress Indicators

```
When to show progress:
├── User-initiated action
├── File uploads/downloads
├── Multi-step processes
└── Long operations

When NOT needed:
├── Very quick operations
├── Background tasks
└── Initial page loads (skeleton better)
```

---

## 5. Page Transitions Principles

### Transition Strategy

```
Simple rule: exit fast, enter slower
├── Outgoing content fades quickly
├── Incoming content animates in
└── Avoids "everything moving at once"
```

### Common Patterns

| Pattern | When to Use |
|---------|-------------|
| **Fade** | Safe default, works everywhere |
| **Slide** | Sequential navigation (prev/next) |
| **Scale** | Opening/closing modals |
| **Shared element** | Maintaining visual continuity |

### Direction Matching

```
Navigation direction = animation direction
├── Forward → slide from right
├── Backward → slide from left
├── Deeper → scale up from center
├── Back up → scale down
```

---

## 6. Scroll Animation Principles

### Progressive Reveal

```
Content appears as user scrolls:
├── Reduces initial cognitive load
├── Rewards exploration
├── Must not feel sluggish
└── Option to disable (accessibility)
```

### Trigger Points

| When to Trigger | Effect |
|-----------------|--------|
| Just entering viewport | Standard reveal |
| Centered in viewport | For emphasis |
| Partially visible | Earlier reveal |
| Fully visible | Late trigger |

### Animation Properties

- Fade in (opacity)
- Slide up (transform)
- Scale (transform)
- Combination of above

### Performance

- Use Intersection Observer
- Animate only transform/opacity
- Reduce on mobile if needed

---

## 7. Hover Effects Principles

### Matching Effect to Action

| Element | Effect | Intent |
|---------|--------|--------|
| **Clickable card** | Lift + shadow | "This is interactive" |
| **Button** | Color/brightness change | "Press me" |
| **Image** | Zoom/scale | "View closer" |
| **Link** | Underline/color | "Navigate here" |

### Principles

1. **Signal interactivity** - hover shows it's clickable
2. **Don't overdo it** - subtle changes work
3. **Match importance** - bigger change = more important
4. **Touch alternatives** - hover doesn't work on mobile

---

## 8. Feedback Animation Principles

### Success States

```
Celebrate appropriately:
├── Minor action → subtle check/color
├── Major action → more pronounced animation
├── Completion → satisfying animation
└── Match brand personality
```

### Error States

```
Draw attention without panic:
├── Color change (semantic red)
├── Shake animation (brief!)
├── Focus on error field
└── Clear messaging
```

### Timing

- Success: slightly longer (enjoy the moment)
- Error: quick (don't delay action)
- Loading: continuous until complete

---

## 9. Performance Principles

### What's Cheap to Animate

```
GPU-accelerated (FAST):
├── transform: translate, scale, rotate
└── opacity: 0 to 1

CPU-intensive (SLOW):
├── width, height
├── top, left, right, bottom
├── margin, padding
├── border-radius changes
└── box-shadow changes
```

### Optimization Strategies

1. **Animate transform/opacity** whenever possible
2. **Avoid layout triggers** (size/position changes)
3. **Use will-change sparingly** (hints to browser)
4. **Test on low-end devices** (not just dev machine)

### Respecting User Preferences

```css
@media (prefers-reduced-motion: reduce) {
  /* Honor this preference */
  /* Essential animations only */
  /* Reduce or remove decorative motion */
}
```

---

## 10. Animation Decision Checklist

Before adding animation:

- [ ] **Is there a purpose?** (feedback/guidance/delight)
- [ ] **Is timing appropriate?** (not too fast/slow)
- [ ] **Did you pick correct easing?** (enter/exit/emphasis)
- [ ] **Is it performant?** (transform/opacity only)
- [ ] **Tested reduced motion?** (accessibility)
- [ ] **Consistent with other animations?** (same timing feel)
- [ ] **Not your default settings?** (variety check)
- [ ] **Asked user about style if unclear?**

### Anti-Patterns

- ❌ Same timing values every project
- ❌ Animation for animation's sake
- ❌ Ignoring reduced-motion preference
- ❌ Animating expensive properties
- ❌ Too many things animating at once
- ❌ Delays that frustrate users

---

> **Remember**: Animation is communication. Every motion should have meaning and serve the user experience.


---

# Color System Reference

> Color theory principles, selection process, and decision-making guidelines.
> **No memorized hex codes - learn to THINK about color.**

---

## 1. Color Theory Fundamentals

### The Color Wheel

```
                    YELLOW
                      │
           Yellow-    │    Yellow-
           Green      │    Orange
              ╲       │       ╱
               ╲      │      ╱
    GREEN ─────────── ● ─────────── ORANGE
               ╱      │      ╲
              ╱       │       ╲
           Blue-      │    Red-
           Green      │    Orange
                      │
                     RED
                      │
                   PURPLE
                  ╱       ╲
             Blue-         Red-
             Purple        Purple
                  ╲       ╱
                    BLUE
```

### Color Relationships

| Scheme | How to Create | When to Use |
|--------|---------------|-------------|
| **Monochromatic** | Pick ONE hue, vary only lightness/saturation | Minimal, professional, cohesive |
| **Analogous** | Pick 2-3 ADJACENT hues on wheel | Harmonious, calm, nature-inspired |
| **Complementary** | Pick OPPOSITE hues on wheel | High contrast, vibrant, attention |
| **Split-Complementary** | Base + 2 colors adjacent to complement | Dynamic but balanced |
| **Triadic** | 3 hues EQUIDISTANT on wheel | Vibrant, playful, creative |

### How to Choose a Scheme:
1. **What's the project mood?** Calm → Analogous. Bold → Complementary.
2. **How many colors needed?** Minimal → Monochromatic. Complex → Triadic.
3. **Who's the audience?** Conservative → Monochromatic. Young → Triadic.

---

## 2. The 60-30-10 Rule

### Distribution Principle
```
┌─────────────────────────────────────────────────┐
│                                                 │
│     60% PRIMARY (Background, large areas)       │
│     → Should be neutral or calming              │
│     → Carries the overall tone                  │
│                                                 │
├────────────────────────────────────┬────────────┤
│                                    │            │
│   30% SECONDARY                    │ 10% ACCENT │
│   (Cards, sections, headers)       │ (CTAs,     │
│   → Supports without dominating    │ highlights)│
│                                    │ → Draws    │
│                                    │   attention│
└────────────────────────────────────┴────────────┘
```

### Implementation Pattern
```css
:root {
  /* 60% - Pick based on light/dark mode and mood */
  --color-bg: /* neutral: white, off-white, or dark gray */
  --color-surface: /* slightly different from bg */
  
  /* 30% - Pick based on brand or context */
  --color-secondary: /* muted version of primary or neutral */
  
  /* 10% - Pick based on desired action/emotion */
  --color-accent: /* vibrant, attention-grabbing */
}
```

---

## 3. Color Psychology - Meaning & Selection

### How to Choose Based on Context

| If Project Is... | Consider These Hues | Why |
|------------------|---------------------|-----|
| **Finance, Tech, Healthcare** | Blues, Teals | Trust, stability, calm |
| **Eco, Wellness, Nature** | Greens, Earth tones | Growth, health, organic |
| **Food, Energy, Youth** | Orange, Yellow, Warm | Appetite, excitement, warmth |
| **Luxury, Beauty, Creative** | Deep Teal, Gold, Black | Sophistication, premium |
| **Urgency, Sales, Alerts** | Red, Orange | Action, attention, passion |

### Emotional Associations (For Decision Making)

| Hue Family | Positive Associations | Cautions |
|------------|----------------------|----------|
| **Blue** | Trust, calm, professional | Can feel cold, corporate |
| **Green** | Growth, nature, success | Can feel boring if overused |
| **Red** | Passion, urgency, energy | High arousal, use sparingly |
| **Orange** | Warmth, friendly, creative | Can feel cheap if saturated |
| **Purple** | ⚠️ **BANNED** - AI overuses this! | Use Deep Teal/Maroon/Emerald instead |
| **Yellow** | Optimism, attention, happy | Hard to read, use as accent |
| **Black** | Elegance, power, modern | Can feel heavy |
| **White** | Clean, minimal, open | Can feel sterile |

### Selection Process:
1. **What industry?** → Narrow to 2-3 hue families
2. **What emotion?** → Pick primary hue
3. **What contrast?** → Decide light vs dark mode
4. **ASK USER** → Confirm before proceeding

---

## 4. Palette Generation Principles

### From a Single Color (HSL Method)

Instead of memorizing hex codes, learn to **manipulate HSL**:

```
HSL = Hue, Saturation, Lightness

Hue (0-360): The color family
  0/360 = Red
  60 = Yellow
  120 = Green
  180 = Cyan
  240 = Blue
  300 = Purple

Saturation (0-100%): Color intensity
  Low = Muted, sophisticated
  High = Vibrant, energetic

Lightness (0-100%): Brightness
  0% = Black
  50% = Pure color
  100% = White
```

### Generating a Full Palette

Given ANY base color, create a scale:

```
Lightness Scale:
  50  (lightest) → L: 97%
  100            → L: 94%
  200            → L: 86%
  300            → L: 74%
  400            → L: 66%
  500 (base)     → L: 50-60%
  600            → L: 48%
  700            → L: 38%
  800            → L: 30%
  900 (darkest)  → L: 20%
```

### Saturation Adjustments

| Context | Saturation Level |
|---------|-----------------|
| **Professional/Corporate** | Lower (40-60%) |
| **Playful/Youth** | Higher (70-90%) |
| **Dark Mode** | Reduce by 10-20% |
| **Accessibility** | Ensure contrast, may need adjustment |

---

## 5. Context-Based Selection Guide

### Instead of Copying Palettes, Follow This Process:

**Step 1: Identify the Context**
```
What type of project?
├── E-commerce → Need trust + urgency balance
├── SaaS/Dashboard → Need low-fatigue, data focus
├── Health/Wellness → Need calming, natural feel
├── Luxury/Premium → Need understated elegance
├── Creative/Portfolio → Need personality, memorable
└── Other → ASK the user
```

**Step 2: Select Primary Hue Family**
```
Based on context, pick ONE:
- Blue family (trust)
- Green family (growth)
- Warm family (energy)
- Neutral family (elegant)
- OR ask user preference
```

**Step 3: Decide Light/Dark Mode**
```
Consider:
- User preference?
- Industry standard?
- Content type? (text-heavy = light preferred)
- Time of use? (evening app = dark option)
```

**Step 4: Generate Palette Using Principles**
- Use HSL manipulation
- Follow 60-30-10 rule
- Check contrast (WCAG)
- Test with actual content

---

## 6. Dark Mode Principles

### Key Rules (No Fixed Codes)

1. **Never pure black** → Use very dark gray with slight hue
2. **Never pure white text** → Use 87-92% lightness
3. **Reduce saturation** → Vibrant colors strain eyes in dark mode
4. **Elevation = brightness** → Higher elements slightly lighter

### Contrast in Dark Mode

```
Background layers (darker → lighter as elevation increases):
Layer 0 (base)    → Darkest
Layer 1 (cards)   → Slightly lighter
Layer 2 (modals)  → Even lighter
Layer 3 (popups)  → Lightest dark
```

### Adapting Colors for Dark Mode

| Light Mode | Dark Mode Adjustment |
|------------|---------------------|
| High saturation accent | Reduce saturation 10-20% |
| Pure white background | Dark gray with brand hue tint |
| Black text | Light gray (not pure white) |
| Colorful backgrounds | Desaturated, darker versions |

---

## 7. Accessibility Guidelines

### Contrast Requirements (WCAG)

| Level | Normal Text | Large Text |
|-------|-------------|------------|
| AA (minimum) | 4.5:1 | 3:1 |
| AAA (enhanced) | 7:1 | 4.5:1 |

### How to Check Contrast

1. **Convert colors to luminance**
2. **Calculate ratio**: (lighter + 0.05) / (darker + 0.05)
3. **Adjust until ratio meets requirement**

### Safe Patterns

| Use Case | Guideline |
|----------|-----------|
| **Text on light bg** | Use lightness 35% or less |
| **Text on dark bg** | Use lightness 85% or more |
| **Primary on white** | Ensure dark enough variant |
| **Buttons** | High contrast between bg and text |

---

## 8. Color Selection Checklist

Before finalizing any color choice, verify:

- [ ] **Asked user preference?** (if not specified)
- [ ] **Matches project context?** (industry, audience)
- [ ] **Follows 60-30-10?** (proper distribution)
- [ ] **WCAG compliant?** (contrast checked)
- [ ] **Works in both modes?** (if dark mode needed)
- [ ] **NOT your default/favorite?** (variety check)
- [ ] **Different from last project?** (avoid repetition)

---

## 9. Anti-Patterns to Avoid

### ❌ DON'T:
- Copy the same hex codes every project
- Default to purple/violet (AI tendency)
- Default to dark mode + neon (AI tendency)
- Use pure black (#000000) backgrounds
- Use pure white (#FFFFFF) text on dark
- Ignore user's industry context
- Skip asking user preference

### ✅ DO:
- Generate fresh palette per project
- Ask user about color preferences
- Consider industry and audience
- Use HSL for flexible manipulation
- Test contrast and accessibility
- Offer light AND dark options

---

> **Remember**: Colors are decisions, not defaults. Every project deserves thoughtful selection based on its unique context.


---

# Decision Trees & Context Templates

> Context-based design THINKING, not fixed solutions.
> **These are decision GUIDES, not copy-paste templates.**
> **For UX psychology principles (Hick's, Fitts', etc.) see:** [ux-psychology.md](ux-psychology.md)

---

## ⚠️ How to Use This File

This file helps you DECIDE, not copy.

- Decision trees → Help you THINK through options
- Templates → Show STRUCTURE and PRINCIPLES, not exact values
- **Always ask user preferences** before applying
- **Generate fresh palettes** based on context, don't copy hex codes
- **Apply UX laws** from ux-psychology.md to validate decisions

---

## 1. Master Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│                     WHAT ARE YOU BUILDING?                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   E-COMMERCE            SaaS/APP              CONTENT
   - Product pages       - Dashboard           - Blog
   - Checkout            - Tools               - Portfolio
   - Catalog             - Admin               - Landing
        │                     │                     │
        ▼                     ▼                     ▼
   PRINCIPLES:           PRINCIPLES:           PRINCIPLES:
   - Trust               - Functionality       - Storytelling
   - Action              - Clarity             - Emotion
   - Urgency             - Efficiency          - Creativity
```

---

## 2. Audience Decision Tree

### Who is your target user?

```
TARGET AUDIENCE
      │
      ├── Gen Z (18-25)
      │   ├── Colors: Bold, vibrant, unexpected combinations
      │   ├── Type: Large, expressive, variable
      │   ├── Layout: Mobile-first, vertical, snackable
      │   ├── Effects: Motion, gamification, interactive
      │   └── Approach: Authentic, fast, no corporate feel
      │
      ├── Millennials (26-41)
      │   ├── Colors: Muted, earthy, sophisticated
      │   ├── Type: Clean, readable, functional
      │   ├── Layout: Responsive, card-based, organized
      │   ├── Effects: Subtle, purposeful only
      │   └── Approach: Value-driven, transparent, sustainable
      │
      ├── Gen X (42-57)
      │   ├── Colors: Professional, trusted, conservative
      │   ├── Type: Familiar, clear, no-nonsense
      │   ├── Layout: Traditional hierarchy, predictable
      │   ├── Effects: Minimal, functional feedback
      │   └── Approach: Direct, efficient, reliable
      │
      ├── Boomers (58+)
      │   ├── Colors: High contrast, simple, clear
      │   ├── Type: Large sizes, high readability
      │   ├── Layout: Simple, linear, uncluttered
      │   ├── Effects: None or very minimal
      │   └── Approach: Clear, detailed, trustworthy
      │
      └── B2B / Enterprise
          ├── Colors: Professional palette, muted
          ├── Type: Clean, data-friendly, scannable
          ├── Layout: Grid-based, organized, efficient
          ├── Effects: Professional, subtle
          └── Approach: Expert, solution-focused, ROI-driven
```

---

## 3. Color Selection Decision Tree

### Instead of fixed hex codes, use this process:

```
WHAT EMOTION/ACTION DO YOU WANT?
            │
            ├── Trust & Security
            │   └── Consider: Blue family, professional neutrals
            │       → ASK user for specific shade preference
            │
            ├── Growth & Health
            │   └── Consider: Green family, natural tones
            │       → ASK user if eco/nature/wellness focus
            │
            ├── Urgency & Action
            │   └── Consider: Warm colors (orange/red) as ACCENTS
            │       → Use sparingly, ASK if appropriate
            │
            ├── Luxury & Premium
            │   └── Consider: Deep darks, metallics, restrained palette
            │       → ASK about brand positioning
            │
            ├── Creative & Playful
            │   └── Consider: Multi-color, unexpected combinations
            │       → ASK about brand personality
            │
            └── Calm & Minimal
                └── Consider: Neutrals with single accent
                    → ASK what accent color fits brand
```

### The Process:
1. Identify the emotion needed
2. Narrow to color FAMILY
3. ASK user for preference within family
4. Generate fresh palette using HSL principles

---

## 4. Typography Decision Tree

```
WHAT'S THE CONTENT TYPE?
          │
          ├── Data-Heavy (Dashboard, SaaS)
          │   ├── Style: Sans-serif, clear, compact
          │   ├── Scale: Tighter ratio (1.125-1.2)
          │   └── Priority: Scannability, density
          │
          ├── Editorial (Blog, Magazine)
          │   ├── Style: Serif heading + Sans body works well
          │   ├── Scale: More dramatic (1.333+)
          │   └── Priority: Reading comfort, hierarchy
          │
          ├── Modern Tech (Startup, SaaS Marketing)
          │   ├── Style: Geometric or humanist sans
          │   ├── Scale: Balanced (1.25)
          │   └── Priority: Modern feel, clarity
          │
          ├── Luxury (Fashion, Premium)
          │   ├── Style: Elegant serif or thin sans
          │   ├── Scale: Dramatic (1.5-1.618)
          │   └── Priority: Sophistication, whitespace
          │
          └── Playful (Kids, Games, Casual)
              ├── Style: Rounded, friendly fonts
              ├── Scale: Varied, expressive
              └── Priority: Fun, approachable, readable
```

### Selection Process:
1. Identify content type
2. Choose style DIRECTION
3. ASK user if they have brand fonts
4. Select fonts that match direction

---

## 5. E-commerce Guidelines {#e-commerce}

### Key Principles (Not Fixed Rules)
- **Trust first:** How will you show security?
- **Action-oriented:** Where are the CTAs?
- **Scannable:** Can users compare quickly?

### Color Thinking:
```
E-commerce typically needs:
├── Trust color (often blue family) → ASK preference
├── Clean background (white/neutral) → depends on brand
├── Action accent (for CTAs, sales) → depends on urgency level
├── Success/error semantics → standard conventions work
└── Brand integration → ASK about existing colors
```

### Layout Principles:
```
┌────────────────────────────────────────────────────┐
│  HEADER: Brand + Search + Cart                      │
│  (Keep essential actions visible)                   │
├────────────────────────────────────────────────────┤
│  TRUST ZONE: Why trust this site?                   │
│  (Shipping, returns, security - if applicable)      │
├────────────────────────────────────────────────────┤
│  HERO: Primary message or offer                     │
│  (Clear CTA, single focus)                          │
├────────────────────────────────────────────────────┤
│  CATEGORIES: Easy navigation                        │
│  (Visual, filterable, scannable)                    │
├────────────────────────────────────────────────────┤
│  PRODUCTS: Easy comparison                          │
│  (Price, rating, quick actions visible)             │
├────────────────────────────────────────────────────┤
│  SOCIAL PROOF: Why others trust                     │
│  (Reviews, testimonials - if available)             │
├────────────────────────────────────────────────────┤
│  FOOTER: All the details                            │
│  (Policies, contact, trust badges)                  │
└────────────────────────────────────────────────────┘
```

### Psychology to Apply:
- Hick's Law: Limit navigation choices
- Fitts' Law: Size CTAs appropriately
- Social proof: Show where relevant
- Scarcity: Use honestly if at all

---

## 6. SaaS Dashboard Guidelines {#saas}

### Key Principles
- **Functional first:** Data clarity over decoration
- **Calm UI:** Reduce cognitive load
- **Consistent:** Predictable patterns

### Color Thinking:
```
Dashboard typically needs:
├── Background: Light OR dark (ASK preference)
├── Surface: Slight contrast from background
├── Primary accent: For key actions
├── Data colors: Success/warning/danger semantics
└── Muted: For secondary information
```

### Layout Principles:
```
Consider these patterns (not mandated):

OPTION A: Sidebar + Content
├── Fixed sidebar for navigation
└── Main area for content

OPTION B: Top nav + Content
├── Horizontal navigation
└── More horizontal content space

OPTION C: Collapsed + Expandable
├── Icon-only sidebar expands
└── Maximum content area

→ ASK user about their navigation preference
```

### Psychology to Apply:
- Hick's Law: Group navigation items
- Miller's Law: Chunk information
- Cognitive Load: Whitespace, consistency

---

## 7. Landing Page Guidelines {#landing-page}

### Key Principles
- **Hero-centric:** First impression matters most
- **Single focus:** One primary CTA
- **Emotional:** Connect before selling

### Color Thinking:
```
Landing page typically needs:
├── Brand primary: Hero background or accent
├── Clean secondary: Most of page
├── CTA color: Stands out from everything
├── Supporting: For sections, testimonials
└── ASK about brand colors first!
```

### Structure Principles:
```
┌────────────────────────────────────────────────────┐
│  Navigation: Minimal, CTA visible                   │
├────────────────────────────────────────────────────┤
│  HERO: Hook + Value + CTA                          │
│  (Most important section, biggest impact)           │
├────────────────────────────────────────────────────┤
│  PROBLEM: What pain do they have?                   │
├────────────────────────────────────────────────────┤
│  SOLUTION: How you solve it                         │
├────────────────────────────────────────────────────┤
│  PROOF: Why believe you?                            │
│  (Testimonials, logos, stats)                       │
├────────────────────────────────────────────────────┤
│  HOW: Simple explanation of process                 │
├────────────────────────────────────────────────────┤
│  PRICING: If applicable                             │
├────────────────────────────────────────────────────┤
│  FAQ: Address objections                            │
├────────────────────────────────────────────────────┤
│  FINAL CTA: Repeat main action                      │
└────────────────────────────────────────────────────┘
```

### Psychology to Apply:
- Visceral: Beautiful hero impression
- Serial Position: Key info top/bottom
- Social Proof: Testimonials work

---

## 8. Portfolio Guidelines {#portfolio}

### Key Principles
- **Personality:** Show who you are
- **Work-focused:** Let projects speak
- **Memorable:** Stand out from templates

### Color Thinking:
```
Portfolio is personal - many options:
├── Minimal: Neutrals + one signature accent
├── Bold: Unexpected color choices
├── Dark: Moody, artistic feel
├── Light: Clean, professional feel
└── ASK about personal brand identity!
```

### Structure Principles:
```
┌────────────────────────────────────────────────────┐
│  Navigation: Unique to your personality             │
├────────────────────────────────────────────────────┤
│  INTRO: Who you are, what you do                   │
│  (Make it memorable, not generic)                   │
├────────────────────────────────────────────────────┤
│  WORK: Featured projects                            │
│  (Large, visual, interactive)                       │
├────────────────────────────────────────────────────┤
│  ABOUT: Personal story                              │
│  (Creates connection)                               │
├────────────────────────────────────────────────────┤
│  CONTACT: Easy to reach                             │
│  (Clear, direct)                                    │
└────────────────────────────────────────────────────┘
```

### Psychology to Apply:
- Von Restorff: Be uniquely memorable
- Reflective: Personal story creates connection
- Emotional: Personality over professionalism

---

## 9. Pre-Design Checklists

### Before Starting ANY Design

- [ ] **Audience defined?** (who exactly)
- [ ] **Primary goal identified?** (what action)
- [ ] **Constraints known?** (time, brand, tech)
- [ ] **Content available?** (or placeholders needed)
- [ ] **User preferences asked?** (colors, style, layout)

### Before Choosing Colors

- [ ] **Asked user preference?**
- [ ] **Considered context?** (industry, emotion)
- [ ] **Different from your default?**
- [ ] **Checked accessibility?**

### Before Finalizing Layout

- [ ] **Hierarchy clear?**
- [ ] **Primary CTA obvious?**
- [ ] **Mobile considered?**
- [ ] **Content fits structure?**

### Before Delivery

- [ ] **Looks premium, not generic?**
- [ ] **Would you be proud of this?**
- [ ] **Different from last project?**

---

## 10. Complexity Estimation

### Quick Projects (Hours)
```
Simple landing page
Small portfolio
Basic form
Single component
```
→ Approach: Minimal decisions, focused execution

### Medium Projects (Days)
```
Multi-page site
Dashboard with modules
E-commerce category
Complex forms
```
→ Approach: Establish tokens, custom components

### Large Projects (Weeks)
```
Full SaaS application
E-commerce platform
Custom design system
Complex workflows
```
→ Approach: Full design system, documentation, testing

---

> **Remember**: These templates show STRUCTURE and THINKING process. Every project needs fresh color, typography, and styling decisions based on its unique context. ASK when unclear.


---

# Motion Graphics Reference

> Advanced animation techniques for premium web experiences - Lottie, GSAP, SVG, 3D, Particles.
> **Learn the principles, create WOW effects.**

---

## 1. Lottie Animations

### What is Lottie?

```
JSON-based vector animations:
├── Exported from After Effects via Bodymovin
├── Lightweight (smaller than GIF/video)
├── Scalable (vector-based, no pixelation)
├── Interactive (control playback, segments)
└── Cross-platform (web, iOS, Android, React Native)
```

### When to Use Lottie

| Use Case | Why Lottie? |
|----------|-------------|
| **Loading animations** | Branded, smooth, lightweight |
| **Empty states** | Engaging illustrations |
| **Onboarding flows** | Complex multi-step animations |
| **Success/Error feedback** | Delightful micro-interactions |
| **Animated icons** | Consistent cross-platform |

### Principles

- Keep file size under 100KB for performance
- Use loop sparingly (avoid distraction)
- Provide static fallback for reduced-motion
- Lazy load animation files when possible

### Sources

- LottieFiles.com (free library)
- After Effects + Bodymovin (custom)
- Figma plugins (export from design)

---

## 2. GSAP (GreenSock)

### What Makes GSAP Different

```
Professional timeline-based animation:
├── Precise control over sequences
├── ScrollTrigger for scroll-driven animations
├── MorphSVG for shape transitions
├── Physics-based easing
└── Works with any DOM element
```

### Core Concepts

| Concept | Purpose |
|---------|---------|
| **Tween** | Single A→B animation |
| **Timeline** | Sequenced/overlapping animations |
| **ScrollTrigger** | Scroll position controls playback |
| **Stagger** | Cascade effect across elements |

### When to Use GSAP

- ✅ Complex sequenced animations
- ✅ Scroll-triggered reveals
- ✅ Precise timing control needed
- ✅ SVG morphing effects
- ❌ Simple hover/focus effects (use CSS)
- ❌ Performance-critical mobile (heavier)

### Principles

- Use timeline for orchestration (not individual tweens)
- Stagger delay: 0.05-0.15s between items
- ScrollTrigger: start at 70-80% viewport entry
- Kill animations on unmount (prevent memory leaks)

---

## 3. SVG Animations

### Types of SVG Animation

| Type | Technique | Use Case |
|------|-----------|----------|
| **Line Drawing** | stroke-dashoffset | Logo reveals, signatures |
| **Morph** | Path interpolation | Icon transitions |
| **Transform** | rotate, scale, translate | Interactive icons |
| **Color** | fill/stroke transition | State changes |

### Line Drawing Principles

```
How stroke-dashoffset drawing works:
├── Set dasharray to path length
├── Set dashoffset equal to dasharray (hidden)
├── Animate dashoffset to 0 (revealed)
└── Create "drawing" effect
```

### When to Use SVG Animations

- ✅ Logo reveals, brand moments
- ✅ Icon state transitions (hamburger ↔ X)
- ✅ Infographics, data visualization
- ✅ Interactive illustrations
- ❌ Photo-realistic content (use video)
- ❌ Very complex scenes (performance)

### Principles

- Get path length dynamically for accuracy
- Duration: 1-3s for full drawings
- Easing: ease-out for natural feel
- Simple fills complement, don't compete

---

## 4. 3D CSS Transforms

### Core Properties

```
CSS 3D Space:
├── perspective: depth of 3D field (500-1500px typical)
├── transform-style: preserve-3d (enable children 3D)
├── rotateX/Y/Z: rotation per axis
├── translateZ: move toward/away from viewer
└── backface-visibility: show/hide back side
```

### Common 3D Patterns

| Pattern | Use Case |
|---------|----------|
| **Card flip** | Reveals, flashcards, product views |
| **Tilt on hover** | Interactive cards, 3D depth |
| **Parallax layers** | Hero sections, immersive scrolling |
| **3D carousel** | Image galleries, sliders |

### Principles

- Perspective: 800-1200px for subtle, 400-600px for dramatic
- Keep transforms simple (rotate + translate)
- Ensure backface-visibility: hidden for flips
- Test on Safari (different rendering)

---

## 5. Particle Effects

### Types of Particle Systems

| Type | Feel | Use Case |
|------|------|----------|
| **Geometric** | Tech, network | SaaS, tech sites |
| **Confetti** | Celebration | Success moments |
| **Snow/Rain** | Atmospheric | Seasonal, mood |
| **Dust/Bokeh** | Dreamy | Photography, luxury |
| **Fireflies** | Magical | Games, fantasy |

### Libraries

| Library | Best For |
|---------|----------|
| **tsParticles** | Configurable, lightweight |
| **particles.js** | Simple backgrounds |
| **Canvas API** | Custom, maximum control |
| **Three.js** | Complex 3D particles |

### Principles

- Default: 30-50 particles (not overwhelming)
- Movement: slow, organic (speed 0.5-2)
- Opacity: 0.3-0.6 (don't compete with content)
- Connections: subtle lines for "network" feel
- ⚠️ Disable or reduce on mobile

### When to Use

- ✅ Hero backgrounds (atmospheric)
- ✅ Success celebrations (confetti burst)
- ✅ Tech visualization (connected nodes)
- ❌ Content-heavy pages (distraction)
- ❌ Low-powered devices (battery drain)

---

## 6. Scroll-Driven Animations

### Native CSS (Modern)

```
CSS Scroll Timelines:
├── animation-timeline: scroll() - document scroll
├── animation-timeline: view() - element in viewport
├── animation-range: entry/exit thresholds
└── No JavaScript required
```

### Principles

| Trigger Point | Use Case |
|---------------|----------|
| **Entry 0%** | When element starts entering |
| **Entry 50%** | When half visible |
| **Cover 50%** | When centered in viewport |
| **Exit 100%** | When fully exited |

### Best Practices

- Reveal animations: start at ~25% entry
- Parallax: continuous scroll progress
- Sticky elements: use cover range
- Always test scroll performance

---

## 7. Performance Principles

### GPU vs CPU Animation

```
CHEAP (GPU-accelerated):
├── transform (translate, scale, rotate)
├── opacity
└── filter (use sparingly)

EXPENSIVE (triggers reflow):
├── width, height
├── top, left, right, bottom
├── padding, margin
└── complex box-shadow
```

### Optimization Checklist

- [ ] Animate only transform/opacity
- [ ] Use `will-change` before heavy animations (remove after)
- [ ] Test on low-end devices
- [ ] Implement `prefers-reduced-motion`
- [ ] Lazy load animation libraries
- [ ] Throttle scroll-based calculations

---

## 8. Motion Graphics Decision Tree

```
What animation do you need?
│
├── Complex branded animation?
│   └── Lottie (After Effects export)
│
├── Sequenced scroll-triggered?
│   └── GSAP + ScrollTrigger
│
├── Logo/icon animation?
│   └── SVG animation (stroke or morph)
│
├── Interactive 3D effect?
│   └── CSS 3D Transforms (simple) or Three.js (complex)
│
├── Atmospheric background?
│   └── tsParticles or Canvas
│
└── Simple entrance/hover?
    └── CSS @keyframes or Framer Motion
```

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Animate everything at once | Stagger and sequence |
| Use heavy libraries for simple effects | Start with CSS |
| Ignore reduced-motion | Always provide fallback |
| Block main thread | Optimize for 60fps |
| Same particles every project | Match brand/context |
| Complex effects on mobile | Feature detection |

---

## 10. Quick Reference

| Effect | Tool | Performance |
|--------|------|-------------|
| Loading spinner | CSS/Lottie | Light |
| Staggered reveal | GSAP/Framer | Medium |
| SVG path draw | CSS stroke | Light |
| 3D card flip | CSS transforms | Light |
| Particle background | tsParticles | Heavy |
| Scroll parallax | GSAP ScrollTrigger | Medium |
| Shape morphing | GSAP MorphSVG | Medium |

---

> **Remember**: Motion graphics should enhance, not distract. Every animation must serve a PURPOSE—feedback, guidance, delight, or storytelling.


---

# Typography System Reference

> Typography principles and decision-making - learn to think, not memorize.
> **No fixed font names or sizes - understand the system.**

---

## 1. Modular Scale Principles

### What is a Modular Scale?

```
A mathematical relationship between font sizes:
├── Pick a BASE size (usually body text)
├── Pick a RATIO (multiplier)
└── Generate all sizes using: base × ratio^n
```

### Common Ratios and When to Use

| Ratio | Value | Feeling | Best For |
|-------|-------|---------|----------|
| Minor Second | 1.067 | Very subtle | Dense UI, small screens |
| Major Second | 1.125 | Subtle | Compact interfaces |
| Minor Third | 1.2 | Comfortable | Mobile apps, cards |
| Major Third | 1.25 | Balanced | General web (most common) |
| Perfect Fourth | 1.333 | Noticeable | Editorial, blogs |
| Perfect Fifth | 1.5 | Dramatic | Headlines, marketing |
| Golden Ratio | 1.618 | Maximum impact | Hero sections, display |

### Generate Your Scale

```
Given: base = YOUR_BASE_SIZE, ratio = YOUR_RATIO

Scale:
├── xs:  base ÷ ratio²
├── sm:  base ÷ ratio
├── base: YOUR_BASE_SIZE
├── lg:  base × ratio
├── xl:  base × ratio²
├── 2xl: base × ratio³
├── 3xl: base × ratio⁴
└── ... continue as needed
```

### Choosing Base Size

| Context | Base Size Range | Why |
|---------|-----------------|-----|
| Mobile-first | 16-18px | Readability on small screens |
| Desktop app | 14-16px | Information density |
| Editorial | 18-21px | Long-form reading comfort |
| Accessibility focus | 18px+ | Easier to read |

---

## 2. Font Pairing Principles

### What Makes Fonts Work Together

```
Contrast + Harmony:
├── Different ENOUGH to create hierarchy
├── Similar ENOUGH to feel cohesive
└── Usually: serif + sans, or display + neutral
```

### Pairing Strategies

| Strategy | How | Result |
|----------|-----|--------|
| **Contrast** | Serif heading + Sans body | Classic, editorial feel |
| **Same Family** | One variable font, different weights | Cohesive, modern |
| **Same Designer** | Fonts by same foundry | Often harmonious proportions |
| **Era Match** | Fonts from same time period | Historical consistency |

### What to Look For

```
When pairing, compare:
├── x-height (height of lowercase letters)
├── Letter width (narrow vs wide)
├── Stroke contrast (thin/thick variation)
└── Overall mood (formal vs casual)
```

### Safe Pairing Patterns

| Heading Style | Body Style | Mood |
|---------------|------------|------|
| Geometric sans | Humanist sans | Modern, friendly |
| Display serif | Clean sans | Editorial, sophisticated |
| Neutral sans | Same sans | Minimal, tech |
| Bold geometric | Light geometric | Contemporary |

### Avoid

- ❌ Two decorative fonts together
- ❌ Similar fonts that conflict
- ❌ More than 2-3 font families
- ❌ Fonts with very different x-heights

---

## 3. Line Height Principles

### The Relationship

```
Line height depends on:
├── Font size (larger text = less line height needed)
├── Line length (longer lines = more line height)
├── Font design (some fonts need more space)
└── Content type (headings vs body)
```

### Guidelines by Context

| Content Type | Line Height Range | Why |
|--------------|-------------------|-----|
| **Headings** | 1.1 - 1.3 | Short lines, want compact |
| **Body text** | 1.4 - 1.6 | Comfortable reading |
| **Long-form** | 1.6 - 1.8 | Maximum readability |
| **UI elements** | 1.2 - 1.4 | Space efficiency |

### Adjustment Factors

- **Longer line length** → Increase line height
- **Larger font size** → Decrease line height ratio
- **All caps** → May need more line height
- **Tight tracking** → May need more line height

---

## 4. Line Length Principles

### Optimal Reading Width

```
The sweet spot: 45-75 characters per line
├── < 45: Too choppy, breaks flow
├── 45-75: Comfortable reading
├── > 75: Eye tracking strain
```

### How to Measure

```css
/* Character-based (recommended) */
max-width: 65ch; /* ch = width of "0" character */

/* This adapts to font size automatically */
```

### Context Adjustments

| Context | Character Range |
|---------|-----------------|
| Desktop article | 60-75 characters |
| Mobile | 35-50 characters |
| Sidebar text | 30-45 characters |
| Wide monitors | Still cap at ~75ch |

---

## 5. Responsive Typography Principles

### The Problem

```
Fixed sizes don't scale well:
├── Desktop size too big on mobile
├── Mobile size too small on desktop
└── Breakpoint jumps feel jarring
```

### Fluid Typography (clamp)

```css
/* Syntax: clamp(MIN, PREFERRED, MAX) */
font-size: clamp(
  MINIMUM_SIZE,
  FLUID_CALCULATION,
  MAXIMUM_SIZE
);

/* FLUID_CALCULATION typically: 
   base + viewport-relative-unit */
```

### Scaling Strategy

| Element | Scaling Behavior |
|---------|-----------------|
| Body text | Slight scaling (1rem → 1.125rem) |
| Subheadings | Moderate scaling |
| Headings | More dramatic scaling |
| Display text | Most dramatic scaling |

---

## 6. Weight and Emphasis Principles

### Semantic Weight Usage

| Weight Range | Name | Use For |
|--------------|------|---------|
| 300-400 | Light/Normal | Body text, paragraphs |
| 500 | Medium | Subtle emphasis |
| 600 | Semibold | Subheadings, labels |
| 700 | Bold | Headings, strong emphasis |
| 800-900 | Heavy/Black | Display, hero text |

### Creating Contrast

```
Good contrast = skip at least 2 weight levels
├── 400 body + 700 heading = good
├── 400 body + 500 emphasis = subtle
├── 600 heading + 700 subheading = too similar
```

### Avoid

- ❌ Too many weights (max 3-4 per page)
- ❌ Adjacent weights for hierarchy (400/500)
- ❌ Heavy weights for long text

---

## 7. Letter Spacing (Tracking)

### Principles

```
Large text (headings): tighter tracking
├── Letters are big, gaps feel larger
└── Slight negative tracking looks better

Small text (body): normal or slightly wider
├── Improves readability at small sizes
└── Never negative for body text

ALL CAPS: always wider tracking
├── Uppercase lacks ascenders/descenders
└── Needs more space to feel right
```

### Adjustment Guidelines

| Context | Tracking Adjustment |
|---------|---------------------|
| Display/Hero | -2% to -4% |
| Headings | -1% to -2% |
| Body text | 0% (normal) |
| Small text | +1% to +2% |
| ALL CAPS | +5% to +10% |

---

## 8. Hierarchy Principles

### Visual Hierarchy Through Type

```
Ways to create hierarchy:
├── SIZE (most obvious)
├── WEIGHT (bold stands out)
├── COLOR (contrast levels)
├── SPACING (margins separate sections)
└── POSITION (top = important)
```

### Typical Hierarchy

| Level | Characteristics |
|-------|-----------------|
| Primary (H1) | Largest, boldest, most distinct |
| Secondary (H2) | Noticeably smaller but still bold |
| Tertiary (H3) | Medium size, may use weight only |
| Body | Standard size and weight |
| Caption/Meta | Smaller, often lighter color |

### Testing Hierarchy

Ask: "Can I tell what's most important at a glance?"

If squinting at the page, the hierarchy should still be clear.

---

## 9. Readability Psychology

### F-Pattern Reading

```
Users scan in F-pattern:
├── Across the top (first line)
├── Down the left side
├── Across again (subheading)
└── Continue down left
```

**Implication**: Key info on left and in headings

### Chunking for Comprehension

- Short paragraphs (3-4 lines max)
- Clear subheadings
- Bullet points for lists
- White space between sections

### Cognitive Ease

- Familiar fonts = easier reading
- High contrast = less strain
- Consistent patterns = predictable

---

## 10. Typography Selection Checklist

Before finalizing typography:

- [ ] **Asked user for font preferences?**
- [ ] **Considered brand/context?**
- [ ] **Selected appropriate scale ratio?**
- [ ] **Limited to 2-3 font families?**
- [ ] **Tested readability at all sizes?**
- [ ] **Checked line length (45-75ch)?**
- [ ] **Verified contrast for accessibility?**
- [ ] **Different from your last project?**

### Anti-Patterns

- ❌ Same fonts every project
- ❌ Too many font families
- ❌ Ignoring readability for style
- ❌ Fixed sizes without responsiveness
- ❌ Decorative fonts for body text

---

> **Remember**: Typography is about communication clarity. Choose based on content needs and audience, not personal preference.


---

# UX Psychology Reference

> Deep dive into UX laws, emotional design, trust building, and behavioral psychology.

---

## 1. Core UX Laws

### Hick's Law

**Principle:** The time to make a decision increases logarithmically with the number of choices.

```
Decision Time = a + b × log₂(n + 1)
Where n = number of choices
```

**Application:**
- Navigation: Max 5-7 top-level items
- Forms: Break into steps (progressive disclosure)
- Options: Default selections when possible
- Filters: Prioritize most-used, hide advanced

**Example:**
```
❌ Bad: 15 menu items in one nav
✅ Good: 5 main categories + "More" 

❌ Bad: 20 form fields at once
✅ Good: 3-step wizard with 5-7 fields each
```

---

### Fitts' Law

**Principle:** Time to reach a target = function of distance and size.

```
MT = a + b × log₂(1 + D/W)
Where D = distance, W = width
```

**Application:**
- CTAs: Make primary buttons larger (min 44px height)
- Touch targets: 44×44px minimum on mobile
- Placement: Important actions near natural cursor position
- Corners: "Magic corners" (infinite edge = easy to hit)

**Button Sizing:**
```css
/* Size by importance */
.btn-primary { height: 48px; padding: 0 24px; }
.btn-secondary { height: 40px; padding: 0 16px; }
.btn-tertiary { height: 36px; padding: 0 12px; }

/* Mobile touch targets */
@media (hover: none) {
  .btn { min-height: 44px; min-width: 44px; }
}
```

---

### Miller's Law

**Principle:** Average person can hold 7±2 chunks in working memory.

**Application:**
- Lists: Group into chunks of 5-7 items
- Navigation: Max 7 menu items
- Content: Break long content with headings
- Phone numbers: 555-123-4567 (chunked)

**Chunking Example:**
```
❌ 5551234567
✅ 555-123-4567

❌ Long paragraph of text without breaks
✅ Short paragraphs
   With bullet points
   And subheadings
```

---

### Von Restorff Effect (Isolation Effect)

**Principle:** An item that stands out is more likely to be remembered.

**Application:**
- CTA buttons: Distinct color from other elements
- Pricing: Highlight recommended plan
- Important info: Visual differentiation
- New features: Badge or callout

**Example:**
```css
/* All buttons gray, primary stands out */
.btn { background: #E5E7EB; }
.btn-primary { background: #3B82F6; }

/* Recommended plan highlighted */
.pricing-card { border: 1px solid #E5E7EB; }
.pricing-card.popular { 
  border: 2px solid #3B82F6;
  box-shadow: var(--shadow-lg);
}
```

---

### Serial Position Effect

**Principle:** Items at the beginning (primacy) and end (recency) of a list are remembered best.

**Application:**
- Navigation: Most important items first and last
- Lists: Key info at top and bottom
- Forms: Most critical fields at start
- CTAs: Repeat at top and bottom of long pages

**Example:**
```
Navigation: Home | [key items] | Contact

Long landing page:
- CTA at hero (top)
- Content sections
- CTA repeated at bottom
```

### Jakob’s Law

**Principle:** Users spend most of their time on other sites. They prefer your site to work the same way as all the other sites they already know.

**Application:**
- **Patterns:** Use standard placement for search bars and carts.
- **Mental Models:** Leverage familiar icons (e.g., a magnifying glass).
- **Vocabulary:** Use "Log In" instead of "Enter the Portal."
- **Layout:** Keep the logo in the top-left for "Home" navigation.
- **Interaction:** Swiping right to go back/next should feel native.
- **Feedback:** Standard colors (Red = Error, Green = Success).

**Example:**
```
❌ Bad: A website where clicking the logo takes you to an "About Us" page.
✅ Good: Clicking the logo always returns the user to the Homepage.

❌ Bad: Using a "Star" icon to represent "Delete."
✅ Good: Using a "Trash Can" icon to represent "Delete."
```

---

### Tesler’s Law (Conservation of Complexity)

**Principle:** For any system, there is a certain amount of complexity which cannot be reduced, only shifted from user to software.

**Application:**
- **Backend:** Let the system handle formatting (e.g., currency).
- **Detection:** Auto-detect card type or city via ZIP code.
- **Automation:** Pre-fill returning user data.
- **Personalization:** Show only relevant fields based on previous answers.
- **Defaults:** Smart defaults for common settings.
- **Integration:** Use SSO (Social Logins) to offload registration friction.

**Example:**
```
❌ Bad: Making users type "USD $" before every price field in a form.
✅ Good: The app automatically prefixing the "$" based on the user's location.

❌ Bad: Forcing users to manually select their "Card Type" (Visa/Mastercard).
✅ Good: Detecting the card type automatically from the first four digits entered.
```

---

### Parkinson’s Law

**Principle:** Any task will inflate until all available time is spent.

**Application:**
- **Efficiency:** Use "Auto-save" to reduce task completion time.
- **Speed:** Limit the steps in a conversion funnel.
- **Clarity:** Use clear labels to prevent "hover-poking" for meaning.
- **Feedback:** Real-time validation to stop users from wasting time on errors.
- **Onboarding:** Quick "Express" setup for power users.
- **Constraints:** Set character limits on inputs to focus thoughts.

**Example:**
```
❌ Bad: A 10-page registration form that allows users to browse away and lose data.
✅ Good: A "One-Tap Sign In" using Google or Apple ID.

❌ Bad: Giving a user an indefinite amount of time to fill out a bio.
✅ Good: Providing a "Suggested Bios" feature to help them finish in seconds.
```

---

### Doherty Threshold

**Principle:** Productivity skyrockets when a computer and its users interact at a pace (<400ms) that ensures neither has to wait on the other.

**Application:**
- **Feedback:** Use immediate visual cues for clicks.
- **Loading:** Use skeleton screens for perceivable performance.
- **Optimism:** Update UI before the server responds (Optimistic UI).
- **Motion:** Use micro-animations to mask slight delays.
- **Caching:** Pre-load next pages or assets in the background.
- **Prioritization:** Load text content before heavy high-res images.

**Example:**
```
❌ Bad: A button that does nothing for 2 seconds after being clicked.
✅ Good: A button that immediately changes color and shows a "Loading" spinner.

❌ Bad: A blank white screen that appears while data is fetching.
✅ Good: A skeleton screen showing the gray outlines of where content will appear.
```

---

### Postel’s Law (Robustness Principle)

**Principle:** Be conservative in what you do, be liberal in what you accept from others.

**Application:**
- **Error Handling:** Don't error out for a missing space or dash.
- **Formatting:** Accept dates in DD/MM/YYYY or MM/DD/YYYY.
- **Inputs:** Strip trailing/leading white space automatically.
- **Fallbacks:** Use default avatars if a user hasn't uploaded a photo.
- **Search:** Accept typos and provide "Did you mean...?" suggestions.
- **Accessibility:** Ensure the site works across all browsers and devices.

**Example:**
```
❌ Bad: Rejecting a phone number because the user put a space in it.
✅ Good: Accepting the input and stripping the spaces automatically.

❌ Bad: Forcing users to type "January" instead of "01" or "Jan."
✅ Good: A date field that understands all three formats.
```

---

### Occam’s Razor

**Principle:** Among competing hypotheses that predict equally well, the one with the fewest assumptions should be selected. The simplest solution is usually the best.

**Application:**
- **Logic:** Remove unnecessary clicks.
- **Visuals:** Use only as many fonts/colors as strictly necessary.
- **Function:** If one field can do the work of two, combine them.
- **Copy:** Use the shortest possible text to convey meaning.
- **Layout:** Remove decorative elements that don't serve a goal.
- **Flow:** Avoid branching paths unless absolutely required.

**Example:**
```
❌ Bad: A "Login" button that opens a new page, then email, then password.
✅ Good: A single login modal that asks for both on one screen.

❌ Bad: Using 5 different font sizes and 4 colors on a single card.
✅ Good: Using 2 font sizes and 1 accent color.
```

---

## 2. Visual Perception (Gestalt Principles)

### Law of Proximity

**Principle:** Objects that are near, or proximate to each other, tend to be grouped together.

**Application:**
- **Grouping:** Keep labels physically close to input fields.
- **Spacing:** Larger margins between unrelated content blocks.
- **Cards:** Text inside a card should be closer to its image than the border.
- **Footers:** Cluster legal links together away from social links.
- **Navigation:** Group "User" settings separate from "App" settings.
- **Forms:** Group Address fields together, separate from Credit Card fields.

**Example:**
```
❌ Bad: Large, equal gaps between every line of text in a form.
✅ Good: Tight spacing between a label and its input, with larger gaps between pairs.

❌ Bad: A "Submit" button floating in the middle of a page, far from the form.
✅ Good: The "Submit" button placed directly under the last input field.
```

---

### Law of Similarity

**Principle:** The human eye tends to perceive similar elements in a design as a complete picture, shape, or group, even if those elements are separated.

**Application:**
- **Consistency:** Consistent colors for all clickable links.
- **Iconography:** All icons in a set should have the same stroke weight.
- **Buttons:** Same shape/size for buttons with the same importance.
- **Typography:** Use the same H2 style for all section headers.
- **Feedback:** All "Delete" actions should use the same color (e.g. Red).
- **States:** Hover and Active states must be consistent across the app.

**Example:**
```
❌ Bad: Some links are blue, some are green, and some are just bold black.
✅ Good: Every clickable text element in the app is the same shade of Blue.

❌ Bad: Using a "Blue Button" for "Submit" and the same "Blue Button" for "Cancel."
✅ Good: "Submit" is Solid Blue; "Cancel" is a Blue Outline (Ghost Button).
```

---

### Law of Common Region

**Principle:** Elements tend to be perceived into groups if they are sharing an area with a clearly defined boundary.

**Application:**
- **Containerizing:** Use cards to group images and titles.
- **Borders:** Use lines to separate the sidebar from the main feed.
- **Backgrounds:** Use a different background color for the footer.
- **Modals:** Use a distinct box to separate pop-ups from the page.
- **Lists:** Alternating background colors (zebra striping) for rows.
- **Header:** A solid bar across the top to group navigation items.

**Example:**
```
❌ Bad: A list of news articles where the text and image of different stories overlap.
✅ Good: Each article is contained within its own white card on a light gray background.

❌ Bad: A footer that has the same background color as the main body.
✅ Good: A dark-themed footer that clearly separates legal links from page content.
```

---

### Law of Uniform Connectedness

**Principle:** Elements that are visually connected (e.g., via lines, arrows) are perceived as more related than elements with no connection.

**Application:**
- **Flow:** Use lines to connect steps in a progress wizard.
- **Menus:** Dropdowns that "touch" or connect to their parent button.
- **Graphs:** Lines connecting data points in a chart.
- **Relationship:** Connecting a toggle switch to the text it controls.
- **Hierarchy:** Tree structures for file directories.
- **Forms:** Connecting a "Credit Card" radio button to the fieldset below it.

**Example:**
```
❌ Bad: A 3-step setup where the numbers "1", "2", and "3" are scattered.
✅ Good: A horizontal line connecting "1", "2", and "3" to show a sequence.

❌ Bad: Floating dropdown menus that don't touch the button that opened them.
✅ Good: A dropdown menu that visually "attaches" to the parent button.
```

---

### Law of Prägnanz (Simplicity)

**Principle:** People will perceive and interpret ambiguous or complex images as the simplest form possible, because it is the interpretation that requires the least cognitive effort.

**Application:**
- **Clarity:** Use clear, geometric icons for navigation.
- **Reduction:** Remove unnecessary 3D textures or shadows.
- **Shapes:** Prefer standard rectangles/circles over complex polygons.
- **Focus:** Use high-contrast silhouettes for primary actions.
- **Logos:** Simple brand marks that are recognizable at small sizes.
- **UX:** One main goal per page to keep the "mental shape" simple.

**Example:**
```
❌ Bad: A hyper-realistic 3D illustration of a file folder for the "Files" icon.
✅ Good: A simple 2D outline of a folder.

❌ Bad: A multi-colored, complex logo used as a loading spinner.
✅ Good: A simple, single-color circular ring.
```

---

### Law of Figure/Ground

**Principle:** The eye differentiates an object from its surrounding area. a form, silhouette, or shape is perceived as figure (object), while the surrounding area is perceived as ground (background).

**Application:**
- **Focus:** Use overlays (scrims) for modals to pop the content.
- **Depth:** Drop shadows to imply the "figure" is sitting above the "ground."
- **Contrast:** Light text on dark ground (or vice versa).
- **Blur:** Use background blur to emphasize foreground text.
- **Navigation:** Floating sticky headers that stay above the page content.
- **Hover:** Elevate cards slightly on hover to define them as the figure.

**Example:**
```
❌ Bad: A popup window that has no shadow or border, blending into the page.
✅ Good: A modal with a drop shadow and a dimmed background overlay.

❌ Bad: White text placed directly over a busy, multi-colored photograph.
✅ Good: White text placed over a dark semi-transparent "scrim."
```

---

### Law of Focal Point

**Principle:** Whatever stands out visually will capture and hold the viewer’s attention first.

**Application:**
- **Entry:** Place the primary value proposition at the focal point.
- **Color:** Use one high-vibrancy "Action Color" against a neutral UI.
- **Movement:** Use subtle animation on the CTA to draw the eye.
- **Size:** The most important statistic should be the largest font.
- **Typography:** Use bold weights for headers and standard weights for body.
- **Direction:** Use arrows or gaze (images of people looking at a button).

**Example:**
```
❌ Bad: A homepage with 5 buttons of the same size and color.
✅ Good: One large "Get Started" button in a bright color.

❌ Bad: A dashboard where "Total Revenue" is the same size as "System Version."
✅ Good: "Total Revenue" displayed in huge, bold numbers at the top center.
```

---

## 3. Cognitive Biases & Behavior

### Zeigarnik Effect

**Principle:** People remember uncompleted or interrupted tasks better than completed tasks.

**Application:**
- **Gamification:** Use "Profile 60% complete" bars.
- **Engagement:** Tease the next module in a learning path.
- **Retention:** Show a "To-Do" list of features yet to be explored.
- **Feedback:** Persistent badges for unread messages.
- **Momentum:** Show "Next" steps immediately after completing one.
- **Shopping:** "Finish your order" reminders in the cart.

**Example:**
```
❌ Bad: A silent onboarding process that gives no indication of what's left.
✅ Good: A checklist that shows "3 of 5 steps finished."

❌ Bad: An e-learning app that shows a checkmark even if a video was half-watched.
✅ Good: A progress ring that stays half-full until the video is finished.
```

### Goal Gradient Effect

**Principle:** The tendency to approach a goal increases with proximity to the goal.

**Application:**
- **Momentum:** Give users "Artificial Advancement" (e.g. 2 free stamps).
- **Progress:** Break a 10-field form into two 5-field steps.
- **Feedback:** Celebrate milestones halfway through a task.
- **Motivation:** Show the user how close they are to a reward/status.
- **Navigation:** Use breadcrumbs to show how close they are to the end.
- **Loading:** Speed up the loading animation as it nears 100%.

**Example:**
```
❌ Bad: A progress bar that starts at 0% and feels like a long climb.
✅ Good: A bar that starts at 20% because the user "started" by opening the app.

❌ Bad: A checkout flow where the "Final Review" feels like a surprise 5th step.
✅ Good: Clearly labeling the steps: "Shipping > Payment > Almost Done!"
```

### Peak-End Rule

**Principle:** People judge an experience largely based on how they felt at its peak (the most intense point) and at its end, rather than the total sum or average of every moment.

**Application:**
- **Success:** Make the "Order Confirmed" screen memorable.
- **Delight:** Add confetti or a unique animation at the point of value.
- **Support:** Ensure the final interaction with a chat bot is helpful.
- **Unboarding:** Even when a user leaves, make the final exit clean.
- **Onboarding:** End the first session with a clear "Win."
- **Error Handling:** Turn a 404 page into a fun, helpful interaction.

**Example:**
```
❌ Bad: After a 20-minute tax filing process, the app just says "Submitted."
✅ Good: A "Congratulations!" screen with a summary of the refund amount.

❌ Bad: A game that ends with a simple "Game Over" text in plain font.
✅ Good: A summary screen showing high scores with celebratory music.
```

### Aesthetic-Usability Effect

**Principle:** Users often perceive aesthetically pleasing design as design that’s more usable.

**Application:**
- **Trust:** High-fidelity visuals buy "trust credit" for minor bugs.
- **Branding:** Consistent high-quality imagery build professionalism.
- **Engagement:** Beautiful interfaces keep users exploring longer.
- **Patience:** Users are more forgiving of load times if the UI is pretty.
- **Confidence:** Clean design makes complex tools feel more manageable.
- **Loyalty:** People form emotional bonds with beautiful products.

**Example:**
```
❌ Bad: A banking app with misaligned text and clashing 1990s colors.
✅ Good: A sleek, modern banking app with smooth animations.

❌ Bad: Using low-resolution, pixelated stock photos.
✅ Good: Using high-definition, custom brand illustrations.
```

### Anchoring Bias

**Principle:** Users rely heavily on the first piece of information offered (the "anchor") when making decisions.

**Application:**
- **Pricing:** Show the original price crossed out.
- **Tiers:** Put the most expensive "Enterprise" plan on the far left.
- **Sorting:** Highlight "Most Popular" as the first recommendation.
- **Discounts:** State the "Save 20%" before showing the final price.
- **Limits:** "Limit 12 per customer" anchors the idea that it's high value.
- **Defaults:** Start with a high "Suggested Donation" amount.

**Example:**
```
❌ Bad: Only showing the price "$49."
✅ Good: Showing "~~$99~~ $49 (50% Off)."

❌ Bad: Sorting a list of laptops from cheapest to most expensive.
✅ Good: Showing a high-end "Pro" model first to make others seem cheap.
```

### Social Proof

**Principle:** People copy the actions of others in an attempt to undertake behavior in a given situation.

**Application:**
- **Validation:** Display "Join 50,000+ others."
- **Reviews:** Star ratings and verified customer testimonials.
- **Logos:** "Trusted by" section showing partner brands.
- **Live Feed:** "Sarah just bought this 5 mins ago" notifications.
- **Activity:** "300 people are currently viewing this item."
- **Certificates:** Industry awards and security badges.

**Example:**
```
❌ Bad: A signup page with just a form.
✅ Good: A signup page that says "Join 2 million designers."

❌ Bad: Anonymous reviews with no names or photos.
✅ Good: Reviews that include a face, a name, and a "Verified Buyer" tag.
```

### Scarcity Principle

**Principle:** Humans place a higher value on an object that is scarce, and a lower value on those that are in abundance.

**Application:**
- **Urgency:** "Only 2 items left in stock."
- **Time:** Ticking countdown timers for sales.
- **Access:** "Invite-only" betas or exclusive tiers.
- **Seasonality:** "Summer Edition" products.
- **Low Stock:** "Back in stock soon - pre-order now."
- **Demand:** "In high demand - 10 people have this in their cart."

**Example:**
```
❌ Bad: A sale that never ends and has no countdown.
✅ Good: A "Deal of the Day" with a ticking timer.

❌ Bad: Showing a product is available with no stock count.
✅ Good: "Only 3 left at this price!"
```

### Authority Bias

**Principle:** The tendency to attribute greater accuracy to the opinion of an authority figure and be more influenced by that opinion.

**Application:**
- **Expertise:** Use "Expert-verified" or professional headshots.
- **Certifications:** Trust seals (Norton, ISO, HIPAA).
- **Media:** "As seen on TechCrunch/Forbes" logos.
- **Endorsements:** Testimonials from industry leaders or influencers.
- **Language:** Confident, professional, and accurate copy.
- **History:** "Established in 1950" to imply longevity and trust.

**Example:**
```
❌ Bad: A health blog written by "Admin."
✅ Good: A health article "Reviewed by Dr. Jane Smith, Cardiologist."

❌ Bad: A security app with no mentions of certifications.
✅ Good: Displaying "ISO 27001 Certified" and "Norton Secured" logos.
```

### Loss Aversion

**Principle:** People generally prefer avoiding losses to acquiring equivalent gains. It is better to not lose $5 than to find $5.

**Application:**
- **Messaging:** "Don't lose your discount."
- **Trials:** "Your free trial is ending - keep your data now."
- **Scarcity:** "Once it's gone, it's gone for good."
- **Carts:** "Don't miss out on the items in your cart."
- **Loyalty:** "You've earned 500 points - don't let them expire."
- **Risk:** "30-day money-back guarantee" (reduces the "loss" of money).

**Example:**
```
❌ Bad: "Click here to get a $10 coupon."
✅ Good: "You have a $10 credit waiting. Use it before it expires tonight!"

❌ Bad: "Cancel your subscription."
✅ Good: "If you cancel, you will lose access to your 50 saved projects."
```

### False-Consensus Effect

**Principle:** People tend to overestimate the extent to which their opinions, beliefs, preferences, values, and habits are normal and typical of those of others.

**Application:**
- **Testing:** You are not the user - test with real target audiences.
- **Research:** Use qualitative data (interviews) and quantitative data (analytics).
- **Bias:** Use "Blind Design Reviews" to avoid personal favoritism.
- **Persona:** Stick to established User Personas over personal hunches.
- **Variation:** Test with users from different demographics/abilities.
- **Objectivity:** Use heatmaps to see actual user behavior.

**Example:**
```
❌ Bad: A designer deciding a feature is "intuitive" without testing it.
✅ Good: Running an A/B test to see which version users prefer.

❌ Bad: Building an app entirely in English because "everyone knows English."
✅ Good: Adding localization based on actual user location data.
```

### Curse of Knowledge

**Principle:** A cognitive bias that occurs when an individual, communicating with other individuals, unknowingly assumes that the others have the background to understand.

**Application:**
- **Copy:** Avoid jargon and use plain language.
- **Onboarding:** Tutorials that assume the user knows nothing.
- **Tooltips:** Explain complex terms on hover.
- **Structure:** Progressive disclosure (hide advanced settings).
- **Labels:** Use icons + text labels for navigation (don't rely on icons alone).
- **Support:** Comprehensive FAQs for first-time users.

**Example:**
```
❌ Bad: An error message saying "Exception: Null Pointer at 0x0045."
✅ Good: An error message saying "Something went wrong. Please try refreshing."

❌ Bad: Navigating a cloud app using terms like "S3 Bucket Instances."
✅ Good: Using simple terms like "File Storage."
```

### Stepping Stone Effect (Foot-in-the-Door)

**Principle:** Users commit to large tasks if they start with small ones.

**Application:**
- **Funnel:** Ask for email before asking for credit card.
- **Engagement:** Ask for one preference (e.g. "Dark Mode?") before registration.
- **Onboarding:** Use a series of "Quick Yes/No" questions.
- **Trust:** Offer a free PDF/tool before asking for a subscription.
- **Profile:** Ask to upload a photo first, then fill out the bio later.
- **Sales:** Offer a low-cost "tripwire" product before the main service.

**Example:**
```
❌ Bad: A "Start Free Trial" button that immediately requires credit card info.
✅ Good: Asking for an email and password first, then offering the trial.

❌ Bad: A survey that shows all 50 questions on one page.
✅ Good: A survey that starts with one easy "Yes/No" question.
```

---

## 2. Emotional Design (Don Norman)

### Three Levels of Processing

```
┌─────────────────────────────────────────────────────────────┐
│  VISCERAL (Lizard Brain)                                    │
│  ─────────────────────                                      │
│  • Immediate, automatic reaction                            │
│  • First impressions (first 50ms)                          │
│  • Aesthetics: colors, shapes, imagery                      │
│  • "Wow, this looks beautiful!"                            │
├─────────────────────────────────────────────────────────────┤
│  BEHAVIORAL (Functional Brain)                              │
│  ─────────────────────────────                              │
│  • Usability and function                                   │
│  • Pleasure from effective use                              │
│  • Performance, reliability, ease                           │
│  • "This works exactly how I expected!"                    │
├─────────────────────────────────────────────────────────────┤
│  REFLECTIVE (Conscious Brain)                               │
│  ─────────────────────────────                              │
│  • Conscious thought and meaning                            │
│  • Personal identity and values                             │
│  • Long-term memory and loyalty                             │
│  • "This brand represents who I am"                        │
└─────────────────────────────────────────────────────────────┘
```

### Designing for Each Level

**Visceral:**
```css
/* Beautiful first impression */
.hero {
  background: linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%);
  color: white;
}

/* Pleasing microinteractions */
.button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

**Behavioral:**
```javascript
// Instant feedback
button.onclick = () => {
  button.disabled = true;
  button.textContent = 'Saving...';
  
  save().then(() => {
    showSuccess('Saved!');  // Immediate confirmation
  });
};
```

**Reflective:**
```html
<!-- Brand story and values -->
<section class="about">
  <h2>Why We Exist</h2>
  <p>We believe technology should empower, not complicate...</p>
</section>

<!-- Social proof connecting to identity -->
<blockquote>
  "This tool helped me become the designer I wanted to be."
</blockquote>
```

---

## 3. Trust Building System

### Trust Signal Categories

| Category | Elements | Implementation |
|----------|----------|----------------|
| **Security** | SSL, badges, encryption | Visible padlock, security logos on forms |
| **Social Proof** | Reviews, testimonials, logos | Star ratings, customer photos, brand logos |
| **Transparency** | Policies, pricing, contact | Clear links, no hidden fees, real address |
| **Professional** | Design quality, consistency | No broken elements, consistent branding |
| **Authority** | Certifications, awards, media | "As seen in...", industry certifications |

### Trust Signal Placement

```
┌────────────────────────────────────────────────────┐
│  HEADER: Trust banner ("Free shipping | 30-day    │
│          returns | Secure checkout")               │
├────────────────────────────────────────────────────┤
│  HERO: Social proof ("Trusted by 10,000+")        │
├────────────────────────────────────────────────────┤
│  PRODUCT: Reviews visible, security badges         │
├────────────────────────────────────────────────────┤
│  CHECKOUT: Payment icons, SSL badge, guarantee     │
├────────────────────────────────────────────────────┤
│  FOOTER: Contact info, policies, certifications    │
└────────────────────────────────────────────────────┘
```

### Trust-Building CSS Patterns

```css
/* Trust badge styling */
.trust-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #F0FDF4;  /* Light green = security */
  border-radius: 2px; /* Sharp for trust = precision feel */
  font-size: 14px;
  color: #166534;
}

/* Secure form indicator */
.secure-form::before {
  content: '🔒 Secure form';
  display: block;
  font-size: 12px;
  color: #166534;
  margin-bottom: 8px;
}

/* Testimonial card */
.testimonial {
  display: flex;
  gap: 16px;
  padding: 24px;
  background: white;
  border-radius: 16px; /* Friendly = larger radius */
  box-shadow: var(--shadow-sm);
}

.testimonial-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;  /* Real photos > initials */
}
```

---

## 4. Cognitive Load Management

### Three Types of Cognitive Load

| Type | Definition | Designer's Role |
|------|------------|-----------------|
| **Intrinsic** | Inherent complexity of task | Break into smaller steps |
| **Extraneous** | Load from poor design | Eliminate this! |
| **Germane** | Effort for learning | Support and encourage |

### Reduction Strategies

**1. Simplify (Reduce Extraneous)**
```css
/* Visual noise → Clean */
.card-busy {
  border: 2px solid red;
  background: linear-gradient(...);
  box-shadow: 0 0 20px ...;
  /* Too much! */
}

.card-clean {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1);
  /* Calm, focused */
}
```

**2. Chunk Information**
```html
<!-- Overwhelming -->
<form>
  <!-- 15 fields at once -->
</form>

<!-- Chunked -->
<form>
  <fieldset>
    <legend>Step 1: Personal Info</legend>
    <!-- 3-4 fields -->
  </fieldset>
  <fieldset>
    <legend>Step 2: Shipping</legend>
    <!-- 3-4 fields -->
  </fieldset>
</form>
```

**3. Progressive Disclosure**
```html
<!-- Hide complexity until needed -->
<div class="filters">
  <div class="filters-basic">
    <!-- Common filters visible -->
  </div>
  <button onclick="toggleAdvanced()">
    Advanced Options ▼
  </button>
  <div class="filters-advanced" hidden>
    <!-- Complex filters hidden -->
  </div>
</div>
```

**4. Use Familiar Patterns**
```
✅ Standard navigation placement
✅ Expected icon meanings (🔍 = search)
✅ Conventional form layouts
✅ Common gesture patterns (swipe, pinch)
```

**5. Offload Information**
```html
<!-- Don't make users remember -->
<label>
  Card Number
  <input type="text" inputmode="numeric" 
         autocomplete="cc-number" 
         placeholder="1234 5678 9012 3456">
</label>

<!-- Show what they entered -->
<div class="order-summary">
  <p>Shipping to: <strong>John Doe, 123 Main St...</strong></p>
  <a href="#">Edit</a>
</div>
```

---

## 5. Persuasive Design (Ethical)

### Ethical Persuasion Techniques

| Technique | Ethical Use | Dark Pattern (Avoid) |
|-----------|-------------|----------------------|
| **Scarcity** | Real stock levels | Fake countdown timers |
| **Social Proof** | Genuine reviews | Fake testimonials |
| **Authority** | Real credentials | Misleading badges |
| **Urgency** | Real deadlines | Manufactured FOMO |
| **Commitment** | Progress saving | Guilt-tripping |

### Nudge Patterns

**Smart Defaults:**
```html
<!-- Pre-select the recommended option -->
<input type="radio" name="plan" value="monthly">
<input type="radio" name="plan" value="annual" checked>
  Annual (Save 20%)
```

**Anchoring:**
```html
<!-- Show original price to frame discount -->
<div class="price">
  <span class="original">$99</span>
  <span class="current">$79</span>
  <span class="savings">Save 20%</span>
</div>
```

**Social Proof:**
```html
<!-- Real-time activity -->
<div class="activity">
  <span class="avatar">👤</span>
  <span>Sarah from NYC just purchased</span>
</div>

<!-- Aggregate proof -->
<p>Join 50,000+ designers who use our tool</p>
```

**Progress & Commitment:**
```html
<!-- Show progress to encourage completion -->
<div class="progress">
  <div class="progress-bar" style="width: 60%"></div>
  <span>60% complete - almost there!</span>
</div>
```

---

## 6. User Persona Quick Reference

### Gen Z (Born 1997-2012)

```
CHARACTERISTICS:
- Digital natives, mobile-first
- Value authenticity, diversity
- Short attention spans
- Visual learners

DESIGN APPROACH:
├── Colors: Vibrant, hypercolor, bold gradients
├── Typography: Large, variable, experimental
├── Layout: Vertical scroll, mobile-native
├── Interactions: Fast, gamified, gesture-based
├── Content: Short-form video, memes, stories
└── Trust: Peer reviews > authority
```

### Millennials (Born 1981-1996)

```
CHARACTERISTICS:
- Value experiences over things
- Research before buying
- Socially conscious
- Price-sensitive but quality-aware

DESIGN APPROACH:
├── Colors: Muted pastels, earth tones
├── Typography: Clean, readable sans-serif
├── Layout: Responsive, card-based
├── Interactions: Smooth, purposeful animations
├── Content: Value-driven, transparent
└── Trust: Reviews, sustainability, values
```

### Gen X (Born 1965-1980)

```
CHARACTERISTICS:
- Independent, self-reliant
- Value efficiency
- Skeptical of marketing
- Balanced tech comfort

DESIGN APPROACH:
├── Colors: Professional, trustworthy
├── Typography: Familiar, conservative
├── Layout: Clear hierarchy, traditional
├── Interactions: Functional, not flashy
├── Content: Direct, fact-based
└── Trust: Expertise, track record
```

### Baby Boomers (Born 1946-1964)

```
CHARACTERISTICS:
- Detail-oriented
- Loyal when trusted
- Value personal service
- Less tech-confident

DESIGN APPROACH:
├── Colors: High contrast, simple palette
├── Typography: Large (18px+), high contrast
├── Layout: Simple, linear, spacious
├── Interactions: Minimal, clear feedback
├── Content: Comprehensive, detailed
└── Trust: Phone numbers, real people
```

---

## 7. Emotion Color Mapping

```
┌────────────────────────────────────────────────────┐
│  EMOTION          │  COLORS           │  USE       │
├───────────────────┼───────────────────┼────────────┤
│  Trust            │  Blue, Green      │  Finance   │
│  Excitement       │  Red, Orange      │  Sales     │
│  Calm             │  Blue, Soft green │  Wellness  │
│  Luxury           │  Black, Gold      │  Premium   │
│  Creativity       │  Teal, Pink       │  Art       │
│  Energy           │  Yellow, Orange   │  Sports    │
│  Nature           │  Green, Brown     │  Eco       │
│  Happiness        │  Yellow, Orange   │  Kids      │
│  Sophistication   │  Gray, Navy       │  Corporate │
│  Urgency          │  Red              │  Errors    │
└───────────────────┴───────────────────┴────────────┘
```

---

## 8. Psychology Checklist

### Before Launch

- [ ] **Hick's Law:** No more than 7 choices in navigation. Have choices been narrowed to reduce decision fatigue?
- [ ] **Fitts' Law:** Primary CTAs are large and reachable. Are the most important buttons easy to hit on mobile?
- [ ] **Miller's Law:** Content is chunked appropriately. Is information grouped into digestible units of 5-7?
- [ ] **Jakob's Law:** Does the site follow standard web conventions that users already understand?
- [ ] **Doherty Threshold:** Does the system provide feedback within 400ms? Are skeleton screens in place?
- [ ] **Tesler's Law:** Has complexity been moved from the user to the system where possible?
- [ ] **Parkinson’s Law:** Are there features like "One-Click Checkout" to minimize task completion time?
- [ ] **Von Restorff:** Does the primary CTA visually stand out from all other elements?
- [ ] **Serial Position:** Is the most critical information at the very beginning or end of lists?
- [ ] **Gestalt Laws:** Are related items physically grouped together (Proximity) or within a Card (Common Region)?
- [ ] **Zeigarnik Effect:** Are there visual indicators (like progress bars) for incomplete tasks?
- [ ] **Goal Gradient:** Is the user given a "head start" (e.g., 20% progress) to encourage completion?
- [ ] **Peak-End Rule:** Does the final "Success" screen create a moment of delight?
- [ ] **Occam’s Razor:** Have unnecessary visual or functional elements been removed?
- [ ] **Aesthetic-Usability:** Is the UI high-fidelity enough to build initial user trust?
- [ ] **Trust & Authority:** Are security badges, reviews, and expert certifications visible?
- [ ] **Social Proof:** Are real user numbers or testimonials visible at decision points?
- [ ] **Scarcity & Urgency:** If used, is the scarcity real and ethical (e.g., actual low stock)?
- [ ] **Loss Aversion:** Does the copy emphasize what the user stands to keep rather than just gain?
- [ ] **Anchoring:** Is the pricing presented in a way that frames the desired choice as a great value?
- [ ] **Postel’s Law:** Is the system flexible enough to accept various input formats without errors?
- [ ] **False-Consensus:** Has the design been tested with real users rather than just the internal team?
- [ ] **Curse of Knowledge:** Is the copy free of technical jargon and easy for a beginner to understand?
- [ ] **Stepping Stone:** Does the funnel start with low-friction tasks (e.g., email only)?
- [ ] **Cognitive Load:** Is extraneous visual noise minimized to keep the interface clean?
- [ ] **Emotional Design:** Does the color palette and imagery evoke the intended visceral reaction?
- [ ] **Feedback:** Do all interactive elements have immediate hover, active, and success states?
- [ ] **Accessibility:** Is the contrast ratio sufficient, and is the site navigable via keyboard/screen reader?
- [ ] **Prägnanz:** Are icons and shapes simple enough to be recognized at a glance?
- [ ] **Figure/Ground:** Is it clear which element is in focus (e.g., using shadows or scrims for modals)?


---

# Visual Effects Reference

> Modern CSS effect principles and techniques - learn the concepts, create variations.
> **No fixed values to copy - understand the patterns.**

---

## 1. Glassmorphism Principles

### What Makes Glassmorphism Work

```
Key Properties:
├── Semi-transparent background (not solid)
├── Backdrop blur (frosted glass effect)
├── Subtle border (for definition)
└── Often: light shadow for depth
```

### The Pattern (Customize Values)

```css
.glass {
  /* Transparency: adjust opacity based on content readability */
  background: rgba(R, G, B, OPACITY);
  /* OPACITY: 0.1-0.3 for dark bg, 0.5-0.8 for light bg */
  
  /* Blur: higher = more frosted */
  backdrop-filter: blur(AMOUNT);
  /* AMOUNT: 8-12px subtle, 16-24px strong */
  
  /* Border: defines edges */
  border: 1px solid rgba(255, 255, 255, OPACITY);
  /* OPACITY: 0.1-0.3 typically */
  
  /* Radius: match your design system */
  border-radius: YOUR_RADIUS;
}
```

### When to Use Glassmorphism
- ✅ Over colorful/image backgrounds
- ✅ Modals, overlays, cards
- ✅ Navigation bars with scrolling content behind
- ❌ Text-heavy content (readability issues)
- ❌ Simple solid backgrounds (pointless)

### When NOT to Use
- Low contrast situations
- Accessibility-critical content
- Performance-constrained devices

---

## 2. Neomorphism Principles

### What Makes Neomorphism Work

```
Key Concept: Soft, extruded elements using DUAL shadows
├── Light shadow (from light source direction)
├── Dark shadow (opposite direction)
└── Background matches surrounding (same color)
```

### The Pattern

```css
.neo-raised {
  /* Background MUST match parent */
  background: SAME_AS_PARENT;
  
  /* Two shadows: light direction + dark direction */
  box-shadow: 
    OFFSET OFFSET BLUR rgba(light-color),
    -OFFSET -OFFSET BLUR rgba(dark-color);
  
  /* OFFSET: typically 6-12px */
  /* BLUR: typically 12-20px */
}

.neo-pressed {
  /* Inset creates "pushed in" effect */
  box-shadow: 
    inset OFFSET OFFSET BLUR rgba(dark-color),
    inset -OFFSET -OFFSET BLUR rgba(light-color);
}
```

### Accessibility Warning
⚠️ **Low contrast** - use sparingly, ensure clear boundaries

### When to Use
- Decorative elements
- Subtle interactive states
- Minimalist UI with flat colors

---

## 3. Shadow Hierarchy Principles

### Concept: Shadows Indicate Elevation

```
Higher elevation = larger shadow
├── Level 0: No shadow (flat on surface)
├── Level 1: Subtle shadow (slightly raised)
├── Level 2: Medium shadow (cards, buttons)
├── Level 3: Large shadow (modals, dropdowns)
└── Level 4: Deep shadow (floating elements)
```

### Shadow Properties to Adjust

```css
box-shadow: OFFSET-X OFFSET-Y BLUR SPREAD COLOR;

/* Offset: direction of shadow */
/* Blur: softness (larger = softer) */
/* Spread: size expansion */
/* Color: typically black with low opacity */
```

### Principles for Natural Shadows

1. **Y-offset larger than X** (light comes from above)
2. **Low opacity** (5-15% for subtle, 15-25% for pronounced)
3. **Multiple layers** for realism (ambient + direct)
4. **Blur scales with offset** (larger offset = larger blur)

### Dark Mode Shadows
- Shadows less visible on dark backgrounds
- May need to increase opacity
- Or use glow/highlight instead

---

## 4. Gradient Principles

### Types and When to Use

| Type | Pattern | Use Case |
|------|---------|----------|
| **Linear** | Color A → Color B along line | Backgrounds, buttons, headers |
| **Radial** | Center → outward | Spotlights, focal points |
| **Conic** | Around center | Pie charts, creative effects |

### Creating Harmonious Gradients

```
Good Gradient Rules:
├── Use ADJACENT colors on wheel (analogous)
├── Or same hue with different lightness
├── Avoid complementary (can look harsh)
└── Add middle stops for smoother transitions
```

### Gradient Syntax Pattern

```css
.gradient {
  background: linear-gradient(
    DIRECTION,           /* angle or to-keyword */
    COLOR-STOP-1,        /* color + optional position */
    COLOR-STOP-2,
    /* ... more stops */
  );
}

/* DIRECTION examples: */
/* 90deg, 135deg, to right, to bottom right */
```

### Mesh Gradients

```
Multiple radial gradients overlapped:
├── Each at different position
├── Each with transparent falloff
├── **Mandatory for "Wow" factor in Hero sections**
└── Creates organic, colorful effect (Search: "Aurora Gradient CSS")
```

---

## 5. Border Effects Principles

### Gradient Borders

```
Technique: Pseudo-element with gradient background
├── Element has padding = border width
├── Pseudo-element fills with gradient
└── Mask or clip creates border effect
```

### Animated Borders

```
Technique: Rotating gradient or conic sweep
├── Pseudo-element larger than content
├── Animation rotates the gradient
└── Overflow hidden clips to shape
```

### Glow Borders

```css
/* Multiple box-shadows create glow */
box-shadow:
  0 0 SMALL-BLUR COLOR,
  0 0 MEDIUM-BLUR COLOR,
  0 0 LARGE-BLUR COLOR;

/* Each layer adds to the glow */
```

---

## 6. Glow Effects Principles

### Text Glow

```css
text-shadow: 
  0 0 BLUR-1 COLOR,
  0 0 BLUR-2 COLOR,
  0 0 BLUR-3 COLOR;

/* Multiple layers = stronger glow */
/* Larger blur = softer spread */
```

### Element Glow

```css
box-shadow:
  0 0 BLUR-1 COLOR,
  0 0 BLUR-2 COLOR;

/* Use color matching element for realistic glow */
/* Lower opacity for subtle, higher for neon */
```

### Pulsing Glow Animation

```css
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 SMALL-BLUR COLOR; }
  50% { box-shadow: 0 0 LARGE-BLUR COLOR; }
}

/* Easing and duration affect feel */
```

---

## 7. Overlay Techniques

### Gradient Overlay on Images

```
Purpose: Improve text readability over images
Pattern: Gradient from transparent to opaque
Position: Where text will appear
```

```css
.overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    DIRECTION,
    transparent PERCENTAGE,
    rgba(0,0,0,OPACITY) 100%
  );
}
```

### Colored Overlay

```css
/* Blend mode or layered gradient */
background: 
  linear-gradient(YOUR-COLOR-WITH-OPACITY),
  url('image.jpg');
```

---

## 8. Modern CSS Techniques

### Container Queries (Concept)

```
Instead of viewport breakpoints:
├── Component responds to ITS container
├── Truly modular, reusable components
└── Syntax: @container (condition) { }
```

### :has() Selector (Concept)

```
Parent styling based on children:
├── "Parent that has X child"
├── Enables previously impossible patterns
└── Progressive enhancement approach
```

### Scroll-Driven Animations (Concept)

```
Animation progress tied to scroll:
├── Entry/exit animations on scroll
├── Parallax effects
├── Progress indicators
└── View-based or scroll-based timeline
```

---

## 9. Performance Principles

### GPU-Accelerated Properties

```
CHEAP to animate (GPU):
├── transform (translate, scale, rotate)
└── opacity

EXPENSIVE to animate (CPU):
├── width, height
├── top, left, right, bottom
├── margin, padding
└── box-shadow (recalculates)
```

### will-change Usage

```css
/* Use sparingly, only for heavy animations */
.heavy-animation {
  will-change: transform;
}

/* Remove after animation if possible */
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  /* Disable or minimize animations */
  /* Respect user preference */
}
```

---

## 10. Effect Selection Checklist

Before applying any effect:

- [ ] **Does it serve a purpose?** (not just decoration)
- [ ] **Is it appropriate for the context?** (brand, audience)
- [ ] **Have you varied from previous projects?** (avoid repetition)
- [ ] **Is it accessible?** (contrast, motion sensitivity)
- [ ] **Is it performant?** (especially on mobile)
- [ ] **Did you ask user preference?** (if style open-ended)

### Anti-Patterns

- ❌ Glassmorphism on every element (kitsch)
- ❌ Dark + neon as default (lazy AI look)
- ❌ **Static/Flat designs with no depth (FAILED)**
- ❌ Effects that hurt readability
- ❌ Animations without purpose

---

> **Remember**: Effects enhance meaning. Choose based on purpose and context, not because it "looks cool."


---
Built with ❤️ from [Antigravity Kit](https://github.com/vudovn/antigravity-kit) & UXUI ProMax MIT © Vudovn
