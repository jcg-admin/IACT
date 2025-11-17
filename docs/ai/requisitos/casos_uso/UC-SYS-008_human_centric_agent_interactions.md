# UC-SYS-008: Human-Centric Agent Interactions

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - UX Design
**Actor Principal**: Travel Planning Agent (Human-Centric)
**Stakeholders**: User
**Relación**:
- Implementa [ADR-056: Agentic Design Principles](../../../gobernanza/adr/ADR-056-agentic-design-principles.md)
- Sigue [RT-015: UX Standards](../reglas_tecnicas/RT-015_ux_standards_transparency_control_consistency.md)

---

## Descripción

Demonstrates human-centric design principles in action through a travel planning scenario, showing how agents connect workflows, embrace uncertainty, establish trust, and adapt to user needs while maintaining transparency, control, and consistency.

---

## Precondiciones

1. User has used agent 3+ times (has interaction history)
2. Agent has learned preferences from past interactions
3. User profile indicates: prefers detailed planning, budget-conscious, morning traveler

---

## Postcondiciones

### Éxito
1. Trip planned with user approval at each high-impact step
2. All decisions explained with reasoning
3. User preferences applied (learned from past)
4. Uncertainty communicated honestly (confidence < 0.8 disclosed)
5. Trust maintained (user satisfaction ≥ 4/5)

---

## Flujo Principal: Human-Centric Trip Planning

**Scenario**: User asks "Plan a weekend trip to Barcelona, budget $1500"

### Paso 1: Connecting Workflow (Not Collapsing)

**Agent behavior**:
```
📋 I'll help plan your Barcelona trip. Here's my approach:

1. Search flights (I'll show you top 3 options)
2. Find hotels (I'll show you 3-4 options matching your preferences)
3. Recommend activities (based on your interests)
4. Create day-by-day itinerary
5. Get your approval before booking anything

This usually takes 3-5 minutes. Sound good? (yes/no/modify)
```

**User**: "yes"

**Why this connects**: User sees full workflow, can modify, maintains control.

**Anti-pattern (collapsing)**: "I'll book everything for you. Done in 2 minutes." ❌

---

### Paso 2: Reflecting on Past (Learning Applied)

**Agent behavior**:
```
💡 Based on your past trips:
   - You prefer boutique hotels over chains
   - You like morning flights (before 10am)
   - You're interested in architecture and local food

I'll prioritize these in my search. Want to change any preferences?
```

**User**: "no, that's perfect"

**Why this reflects**: Agent applies learnings from past 3 trips, shows what it remembered.

---

### Paso 3: Transparent Planning with Uncertainty

**Agent searches flights**

```
🔍 Searching flights...

Found 5 options. Here are the top 3:

1. ✈️  Vueling VY8231 - Departs 8:30am
   Price: $320 (within budget ✓)
   My confidence: 85% (good price, matches your preference)

2. ✈️  Ryanair FR4421 - Departs 9:15am
   Price: $280 (saves $40)
   My confidence: 70% ⚠️  (cheaper but less reliable airline)

3. ✈️  Iberia IB3142 - Departs 11:00am
   Price: $380
   My confidence: 60% ⚠️  (later than you usually prefer)

💡 Recommendation: Option 1 (Vueling)
   Why: Best balance of price, timing, and reliability

Which one do you prefer? (1/2/3/see more)
```

**User**: "1"

**Why transparent**: Shows all reasoning, communicates uncertainty (confidence scores), explains recommendation.

---

### Paso 4: Nudging (Not Forcing)

**While searching hotels**

```
🏨 Searching hotels...

I found a great option:
Hotel Praktik Rambla - $180/night ($360 total)
- Boutique hotel (matches your preference ✓)
- Central location
- 4.7★ rating (850 reviews)

💡 Suggestion: There's a similar hotel for $150/night ($300 total)
   Hotel Curious - 4.6★, same neighborhood
   Difference: Smaller rooms, but saves $60

   Want to see it? (yes/no/book Praktik anyway)
```

**User**: "yes, show me Curious"

**Agent**: "Here's Hotel Curious: [details]. Which do you prefer? (Praktik/Curious)"

**Why nudging**: Suggests alternative but doesn't force, user maintains choice.

---

### Paso 5: Accessible Yet Invisible (Proactive Help)

**Agent detects opportunity**

```
💡 Quick tip: I notice you're traveling on a weekend.
   FC Barcelona has a home game on Saturday at 8pm.
   Tickets: $45-80

   Want me to add this to your itinerary? (yes/no/maybe later)
```

**User**: "yes"

**Why accessible**: Surfaces proactively but only when valuable (high confidence + significant value).

**Anti-pattern**: Constant notifications about minor things ❌

---

### Paso 6: High-Impact Action (Control Gate)

**Before booking flight**

```
⚠️  Ready to book: Vueling VY8231 - $320

📋 Review before I book:
   Depart: Barcelona (BCN) → Your City, Sat May 3, 8:30am
   Return: Your City → Barcelona (BCN), Mon May 5, 6:00pm
   Total: $320

   Cancellation: Free cancellation within 24h

   ⚠️  Important: This will charge your card immediately.

   Proceed with booking? (yes/no/hold 10min)
```

**User**: "yes"

**Agent executes booking**

```
🎫 Booking flight...
   ✓ Confirmed! Booking reference: VY8231ABC
   ✓ Confirmation email sent

   Total spent so far: $320 / $1500 budget
   Remaining: $1180
```

**Why control**: Explicit approval for high-impact action (booking = payment), shows what will happen, allows hold option.

---

### Paso 7: Adapting to Feedback (Real-Time)

**User books hotel manually (outside agent)**

**Agent detects**:

```
📊 I notice you booked Hotel Arts instead of my recommendations.

   That's a luxury hotel ($450/night vs my $180 suggestion).
   This puts you over budget by $540.

   Options:
   1. I can find cheaper activities to offset
   2. I can skip some planned activities
   3. Continue anyway (you'll exceed budget)

   What would you like? (1/2/3/explain why you chose Arts)
```

**User**: "explain why you chose Arts - I want to splurge on accommodation"

**Agent**: "Got it! I'll remember you prioritize accommodation quality. Adjusting budget allocation..."

**Why adapting**: Learns from user deviation, adjusts approach, asks for reasoning to improve.

---

### Paso 8: Embracing Uncertainty (Honest Communication)

**Planning activities**

```
🎨 Planning activities for Barcelona...

Day 1 (Saturday):
  Morning: Sagrada Familia tour
  Afternoon: Gothic Quarter walk
  Evening: FC Barcelona game ✓ (you wanted this)

Day 2 (Sunday):
  Morning: Park Güell
  Afternoon: Beach time
  ⚠️  Uncertainty: Weather forecast shows 40% chance of rain

      If it rains:
      Plan B: Picasso Museum instead of beach

      Want me to pre-book museum ticket just in case? ($15)
      (yes/no/I'll decide day-of)
```

**User**: "yes"

**Why embracing uncertainty**: Honest about weather uncertainty, offers contingency plan, lets user decide risk level.

---

### Paso 9: Establishing Trust (Complete Transparency)

**Final plan review**

```
✅ Your Barcelona Trip Plan

💰 Budget Status:
   Total budget: $1500
   Spent: $770 (flight $320 + hotel $450)
   Committed: $140 (activities)
   Remaining: $590 (meals, transport, extras)
   ⚠️  Over accommodation budget, but within total

📅 Itinerary:
   [Full day-by-day breakdown]

🎯 Confidence Assessment:
   Overall plan confidence: 82%

   High confidence (>90%):
   ✓ Flight bookings
   ✓ Hotel booking
   ✓ Major activities

   Medium confidence (70-80%):
   ⚠️  Weather-dependent activities
   ⚠️  Restaurant availability (didn't book)

   What I learned:
   💡 You prioritize accommodation quality over budget
   💡 You like architectural sights

   I'll remember this for future trips!

Everything look good? (yes/modify/cancel and start over)
```

**User**: "yes"

**Agent**: "✓ All set! Have an amazing trip to Barcelona! 🎉"

**Why trustworthy**: Complete transparency on budget, confidence, learnings. User knows exactly what to expect.

---

## Flujos Alternos

### FA-1: User Interrupts During Planning

**Trigger**: User presses Ctrl+C while agent searching

```
⏸  Planning paused

I've completed:
✓ Flight search (saved 5 options)
✓ Hotel search (saved 4 options)
⏳ Activities (50% complete)

Options:
1. Resume from here
2. Start over
3. Save and finish later

What would you like? (1/2/3)
```

**Metrics**: Cancel latency < 2s, state preserved ✓

### FA-2: Agent Low Confidence (Requests Human Guidance)

**Trigger**: Confidence < 0.5 for activity planning

```
🤔 I'm uncertain about activity planning (45% confidence)

Reasons:
- You haven't specified interests beyond architecture
- Barcelona has 200+ attractions, hard to prioritize
- Don't want to over-schedule or under-schedule

Can you help me?
1. Tell me more about your interests
2. Show me top 10 activities, I'll pick
3. Just suggest 3-4, I'll figure out rest

Which works best? (1/2/3)
```

**User chooses option 2**: Agent shows top 10, user selects 4.

**Agent**: "Perfect! Now I'm 85% confident in the plan."

### FA-3: Behavioral Change (Consistency Alert)

**Trigger**: Agent approach changed from v1.0 to v2.0

```
⚠️  Heads up: My planning approach has evolved

Old approach (v1.0): I always book cheapest options
New approach (v2.0): I balance price with quality/reviews

Why I changed: Users rated trips higher with quality focus

For your trip:
- Old: Would suggest $120/night hotel (3.8★)
- New: Suggesting $180/night hotel (4.7★)

Which approach do you prefer?
1. Use new (quality-focused)
2. Revert to old (budget-focused)
3. Let me decide per trip

Choice? (1/2/3)
```

---

## Métricas de Éxito

| Principio | Métrica | Objetivo | Resultado |
|-----------|---------|----------|-----------|
| Connecting not Collapsing | Approval requests for high-impact | > 0 | 2 (flight, activities) ✓ |
| Accessible yet Invisible | Proactive help accepted | > 60% | 100% (game suggestion accepted) ✓ |
| Reflecting | Preference application rate | > 70% | 100% (all 3 preferences applied) ✓ |
| Nudging | Nudge acceptance | > 40% | 100% (hotel suggestion accepted) ✓ |
| Adapting | Detection of user evolution | < 2 weeks | Immediate (hotel upgrade) ✓ |
| Embrace Uncertainty | Confidence disclosure when < 0.8 | 100% | 100% (weather, restaurants) ✓ |
| Establish Trust | User satisfaction | ≥ 4.0/5.0 | 4.8/5.0 ✓ |

---

## Referencias

1. [ADR-056: Agentic Design Principles](../../../gobernanza/adr/ADR-056-agentic-design-principles.md)
2. [RT-015: UX Standards](../reglas_tecnicas/RT-015_ux_standards_transparency_control_consistency.md)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
