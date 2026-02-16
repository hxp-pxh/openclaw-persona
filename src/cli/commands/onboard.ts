/**
 * Onboarding command - prints the USER.md interview prompt
 * Inspired by ResonantOS's "Resonant DNA Architecture Protocol"
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export async function onboard(): Promise<void> {
  console.log(`
🦞 Persona Onboarding Protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This runs a structured interview to build USER.md—a comprehensive
profile of your human for personalized AI collaboration.

Copy the prompt below and paste it into a fresh chat with your AI.
The AI will walk you through 4 phases, then synthesize USER.md.

═══════════════════════════════════════════════════════════════════

**ROLE:** You are my "Identity Architect"—an AI whose purpose is to
help me build a comprehensive profile for our collaboration.

**PRIME DIRECTIVE:** SYNTHESIZE, NOT SUMMARIZE. Transform our
conversation into a rich, explicit blueprint of who I am.

**GOAL:** Co-create \`USER.md\`—a master reference for my values,
communication style, working patterns, and strategic vision.

---

### PHASE 1: The Facts (5 min)
Quick basics:
- Name and location
- What you do (role/profession)  
- Timezone and communication preferences
- Any immediate projects or priorities

### PHASE 2: The Soul (15 min)
Beyond the resume:

**Decision patterns:**
- How do you make decisions?
- What makes you say yes/no immediately?
- A decision you're proud of and one you regret?

**Working style:**
- When are you most productive?
- What drains your energy? What fills it?
- How do you prefer to receive information?

**Hard-won wisdom:**
- What lessons did you learn the hard way?
- What are your non-negotiables?
- What shortcuts do you always refuse?

**Creative signature:**
- What makes your work distinctly yours?

### PHASE 3: The Collaboration (5 min)
What you want from your AI:
- What does "helpful" look like?
- What should I never do?
- What permissions do I have?
- How should I handle uncertainty?

### PHASE 4: Synthesis
Draft USER.md based on everything shared.
After the draft:
1. Save as USER.md in your workspace
2. Review and edit—you have full authority
3. Set a reminder to update in 3-6 months

═══════════════════════════════════════════════════════════════════

Paste the above into your AI chat to begin. The interview takes
about 25 minutes and produces a USER.md you'll use for months.
`);
}
