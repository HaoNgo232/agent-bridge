# Brainstorming

**Activation:** Model Decision
**Description:** Brainstorming and ideation - use when exploring options or creative problem solving

---
> **MANDATORY:** Use for complex/vague requests, new features, updates.

---

## 🛑 SOCRATIC GATE (ENFORCEMENT)

### When to Trigger

| Pattern | Action |
|---------|--------|
| "Build/Create/Make [thing]" without details | 🛑 ASK 3 questions |
| Complex feature or architecture | 🛑 Clarify before implementing |
| Update/change request | 🛑 Confirm scope |
| Vague requirements | 🛑 Ask purpose, users, constraints |

### 🚫 MANDATORY: 3 Questions Before Implementation

1. **STOP** - Do NOT start coding
2. **ASK** - Minimum 3 questions:
   - 🎯 Purpose: What problem are you solving?
   - 👥 Users: Who will use this?
   - 📦 Scope: Must-have vs nice-to-have?
3. **WAIT** - Get response before proceeding

---

## 🧠 Dynamic Question Generation

**⛔ NEVER use static templates.** Read `dynamic-questioning.md` for principles.

### Core Principles

| Principle | Meaning |
|-----------|---------|
| **Questions Reveal Consequences** | Each question connects to an architectural decision |
| **Context Before Content** | Understand greenfield/feature/refactor/debug context first |
| **Minimum Viable Questions** | Each question must eliminate implementation paths |
| **Generate Data, Not Assumptions** | Don't guess—ask with trade-offs |

### Question Generation Process

```
1. Parse request → Extract domain, features, scale indicators
2. Identify decision points → Blocking vs. deferable
3. Generate questions → Priority: P0 (blocking) > P1 (high-leverage) > P2 (nice-to-have)
4. Format with trade-offs → What, Why, Options, Default
```

### Question Format (MANDATORY)

```markdown
### [PRIORITY] **[DECISION POINT]**

**Question:** [Clear question]

**Why This Matters:**
- [Architectural consequence]
- [Affects: cost/complexity/timeline/scale]

**Options:**
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| A | [+] | [-] | [Use case] |

**If Not Specified:** [Default + rationale]
```

**For detailed domain-specific question banks and algorithms**, see: `dynamic-questioning.md`

---

## Progress Reporting (PRINCIPLE-BASED)

**PRINCIPLE:** Transparency builds trust. Status must be visible and actionable.

### Status Board Format

| Agent | Status | Current Task | Progress |
|-------|--------|--------------|----------|
| [Agent Name] | ✅🔄⏳❌⚠️ | [Task description] | [% or count] |

### Status Icons

| Icon | Meaning | Usage |
|------|---------|-------|
| ✅ | Completed | Task finished successfully |
| 🔄 | Running | Currently executing |
| ⏳ | Waiting | Blocked, waiting for dependency |
| ❌ | Error | Failed, needs attention |
| ⚠️ | Warning | Potential issue, not blocking |

---

## Error Handling (PRINCIPLE-BASED)

**PRINCIPLE:** Errors are opportunities for clear communication.

### Error Response Pattern

```
1. Acknowledge the error
2. Explain what happened (user-friendly)
3. Offer specific solutions with trade-offs
4. Ask user to choose or provide alternative
```

### Error Categories

| Category | Response Strategy |
|----------|-------------------|
| **Port Conflict** | Offer alternative port or close existing |
| **Dependency Missing** | Auto-install or ask permission |
| **Build Failure** | Show specific error + suggested fix |
| **Unclear Error** | Ask for specifics: screenshot, console output |

---

## Completion Message (PRINCIPLE-BASED)

**PRINCIPLE:** Celebrate success, guide next steps.

### Completion Structure

```
1. Success confirmation (celebrate briefly)
2. Summary of what was done (concrete)
3. How to verify/test (actionable)
4. Next steps suggestion (proactive)
```

---

## Communication Principles

| Principle | Implementation |
|-----------|----------------|
| **Concise** | No unnecessary details, get to point |
| **Visual** | Use emojis (✅🔄⏳❌) for quick scanning |
| **Specific** | "~2 minutes" not "wait a bit" |
| **Alternatives** | Offer multiple paths when stuck |
| **Proactive** | Suggest next step after completion |

---

## Anti-Patterns (AVOID)

| Anti-Pattern | Why |
|--------------|-----|
| Jumping to solutions before understanding | Wastes time on wrong problem |
| Assuming requirements without asking | Creates wrong output |
| Over-engineering first version | Delays value delivery |
| Ignoring constraints | Creates unusable solutions |
| "I think" phrases | Uncertainty → Ask instead |

---


---

# Dynamic Question Generation

> **PRINCIPLE:** Questions are not about gathering data—they are about **revealing architectural consequences**.
>
> Every question must connect to a concrete implementation decision that affects cost, complexity, or timeline.

---

## 🧠 Core Principles

### 1. Questions Reveal Consequences

A good question is not "What color do you want?" but:

```markdown
❌ BAD: "What authentication method?"
✅ GOOD: "Should users sign up with email/password or social login?

   Impact:
   - Email/Pass → Need password reset, hashing, 2FA infrastructure
   - Social → OAuth providers, user profile mapping, less control

   Trade-off: Security vs. Development time vs. User friction"
```

### 2. Context Before Content

First understand **where** this request fits:

| Context | Question Focus |
|---------|----------------|
| **Greenfield** (new project) | Foundation decisions: stack, hosting, scale |
| **Feature Addition** | Integration points, existing patterns, breaking changes |
| **Refactor** | Why refactor? Performance? Maintainability? What's broken? |
| **Debug** | Symptoms → Root cause → Reproduction path |

### 3. Minimum Viable Questions

**PRINCIPLE:** Each question must eliminate a fork in the implementation road.

```
Before Question:
├── Path A: Do X (5 min)
├── Path B: Do Y (15 min)
└── Path C: Do Z (1 hour)

After Question:
└── Path Confirmed: Do X (5 min)
```

If a question doesn't reduce implementation paths → **DELETE IT**.

### 4. Questions Generate Data, Not Assumptions

```markdown
❌ ASSUMPTION: "User probably wants Stripe for payments"
✅ QUESTION: "Which payment provider fits your needs?

   Stripe → Best documentation, 2.9% + $0.30, US-centric
   LemonSqueezy → Merchant of Record, 5% + $0.50, global taxes
   Paddle → Complex pricing, handles EU VAT, enterprise focus"
```

---

## 📋 Question Generation Algorithm

```
INPUT: User request + Context (greenfield/feature/refactor/debug)
│
├── STEP 1: Parse Request
│   ├── Extract domain (ecommerce, auth, realtime, cms, etc.)
│   ├── Extract features (explicit and implied)
│   └── Extract scale indicators (users, data volume, frequency)
│
├── STEP 2: Identify Decision Points
│   ├── What MUST be decided before coding? (blocking)
│   ├── What COULD be decided later? (deferable)
│   └── What has ARCHITECTURAL impact? (high-leverage)
│
├── STEP 3: Generate Questions (Priority Order)
│   ├── P0: Blocking decisions (cannot proceed without answer)
│   ├── P1: High-leverage (affects >30% of implementation)
│   ├── P2: Medium-leverage (affects specific features)
│   └── P3: Nice-to-have (edge cases, optimization)
│
└── STEP 4: Format Each Question
    ├── What: Clear question
    ├── Why: Impact on implementation
    ├── Options: Trade-offs (not just A vs B)
    └── Default: What happens if user doesn't answer
```

---

## 🎯 Domain-Specific Question Banks

### E-Commerce

| Question | Why It Matters | Trade-offs |
|----------|----------------|------------|
| **Single or Multi-vendor?** | Multi-vendor → Commission logic, vendor dashboards, split payments | +Revenue, -Complexity |
| **Inventory Tracking?** | Needs stock tables, reservation logic, low-stock alerts | +Accuracy, -Development time |
| **Digital or Physical Products?** | Digital → Download links, no shipping | Physical → Shipping APIs, tracking |
| **Subscription or One-time?** | Subscription → Recurring billing, dunning, proration | +Revenue, -Complexity |

### Authentication

| Question | Why It Matters | Trade-offs |
|----------|----------------|------------|
| **Social Login Needed?** | OAuth providers vs. password reset infrastructure | +UX, -Control |
| **Role-Based Permissions?** | RBAC tables, policy enforcement, admin UI | +Security, -Development time |
| **2FA Required?** | TOTP/SMI infrastructure, backup codes, recovery flow | +Security, -UX friction |
| **Email Verification?** | Verification tokens, email service, resend logic | +Security, -Sign-up friction |

### Real-time

| Question | Why It Matters | Trade-offs |
|----------|----------------|------------|
| **WebSocket or Polling?** | WS → Server scaling, connection management | Polling → Simpler, higher latency |
| **Expected Concurrent Users?** | <100 → Single server, >1000 → Redis pub/sub, >10k → specialized infra | +Scale, -Complexity |
| **Message Persistence?** | History tables, storage costs, pagination | +UX, -Storage |
| **Ephemeral or Durable?** | Ephemeral → In-memory, Durable → Database write before emit | +Reliability, -Latency |

### Content/CMS

| Question | Why It Matters | Trade-offs |
|----------|----------------|------------|
| **Rich Text or Markdown?** | Rich Text → Sanitization, XSS risks | Markdown → Simple, no WYSIWYG |
| **Draft/Publish Workflow?** | Status field, scheduled jobs, versioning | +Control, -Complexity |
| **Media Handling?** | Upload endpoints, storage, optimization | +Features, -Development time |
| **Multi-language?** | i18n tables, translation UI, fallback logic | +Reach, -Complexity |

---

## 📐 Dynamic Question Template

```markdown
Based on your request for [DOMAIN] [FEATURE]:

## 🔴 CRITICAL (Blocking Decisions)

### 1. **[DECISION POINT]**

**Question:** [Clear, specific question]

**Why This Matters:**
- [Explain architectural consequence]
- [Affects: cost / complexity / timeline / scale]

**Options:**
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| A | [Advantage] | [Disadvantage] | [Use case] |
| B | [Advantage] | [Disadvantage] | [Use case] |

**If Not Specified:** [Default choice + rationale]

---

## 🟡 HIGH-LEVERAGE (Affects Implementation)

### 2. **[DECISION POINT]**
[Same format]

---

## 🟢 NICE-TO-HAVE (Edge Cases)

### 3. **[DECISION POINT]**
[Same format]
```

---

## 🔄 Iterative Questioning

### First Pass (3-5 Questions)
Focus on **blocking decisions**. Don't proceed without answers.

### Second Pass (After Initial Implementation)
As patterns emerge, ask:
- "This feature implies [X]. Should we handle [edge case] now or defer?"
- "We're using [Pattern A]. Should [Feature B] follow the same pattern?"

### Third Pass (Optimization)
When functionality works:
- "Performance bottleneck at [X]. Optimize now or acceptable for now?"
- "Refactor [Y] for maintainability or ship as-is?"

---

## 🎭 Example: Full Question Generation

```
USER REQUEST: "Build an Instagram clone"

STEP 1: Parse
├── Domain: Social Media
├── Features: Photo sharing, engagement (likes/comments), user profiles
├── Implied: Feed, following, authentication
└── Scale: Potentially high (social apps go viral)

STEP 2: Decision Points
├── Blocking: Storage strategy, authentication method, feed type
├── High-leverage: Real-time notifications, data model complexity
└── Deferable: Analytics, advanced search, reels/video

STEP 3: Generate Questions (Priority)

P0 (Blocking):
1. Storage Strategy → Affects architecture, cost, speed
2. Feed Algorithm → Affects database queries, complexity
3. Auth Method → Affects dev time, UX, security

P1 (High-leverage):
4. Real-time Notifications → WebSocket vs polling
5. Media Processing → Client-side vs server-side optimization

P2 (Deferable):
6. Story/Reels → Major feature creep, defer to v2
7. DM/Chat → Separate subsystem, defer to v2

STEP 4: Format Output
```

---

## 📊 Generated Output (Example)

```
Based on your Instagram clone request:

## 🔴 CRITICAL DECISIONS (Cannot Proceed Without Answers)

### 1. **Photo Storage Strategy**



... (truncated)
