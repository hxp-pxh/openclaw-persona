/**
 * Auto Memory Formation
 * Extracts key facts, decisions, and preferences from conversation turns
 */

export interface MemoryCandidate {
  text: string;
  type: 'fact' | 'decision' | 'preference' | 'lesson' | 'todo';
  importance: number; // 0-1
  source: string;
  timestamp: Date;
}

export interface ExtractionPrompt {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

/**
 * Extraction prompt for LLM to identify memory candidates
 */
export const EXTRACTION_SYSTEM_PROMPT = `You are a memory extraction system. Analyze the conversation and extract discrete, memorable facts.

Extract ONLY:
- Facts stated by the user (preferences, personal info, decisions)
- Lessons learned (corrections, new knowledge)
- Action items / todos mentioned
- Important decisions made

Output JSON array:
[
  {
    "text": "User prefers CLI tools over GUIs",
    "type": "preference",
    "importance": 0.8
  }
]

Rules:
- Each item must be self-contained (understandable without context)
- Skip transient info (current mood, temporary states)
- Skip already-known facts (check against existing memories)
- Importance: 0.3=minor, 0.5=normal, 0.8=significant, 1.0=critical
- If nothing worth remembering, return []`;

/**
 * Extract memory candidates from a conversation turn
 */
export async function extractMemories(
  messages: ExtractionPrompt[],
  existingMemories: string[] = []
): Promise<MemoryCandidate[]> {
  // This would call an LLM with the extraction prompt
  // For now, return structure for the CLI to implement
  return [];
}

/**
 * Filter candidates against existing memories (dedup)
 */
export function deduplicateCandidates(
  candidates: MemoryCandidate[],
  existingMemories: string[],
  similarityThreshold: number = 0.85
): MemoryCandidate[] {
  // Would use vector similarity to filter near-duplicates
  return candidates;
}

/**
 * Score and rank candidates for storage
 */
export function rankCandidates(candidates: MemoryCandidate[]): MemoryCandidate[] {
  return candidates.sort((a, b) => b.importance - a.importance);
}
