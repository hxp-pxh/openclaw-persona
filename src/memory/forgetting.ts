/**
 * Memory Forgetting & Decay
 * Implements memory lifecycle: formation → evolution → forgetting
 */

export interface MemoryRecord {
  id: string;
  text: string;
  type: string;
  importance: number;
  createdAt: Date;
  lastAccessedAt: Date;
  accessCount: number;
  decayScore?: number;
}

/**
 * Calculate decay score for a memory
 * Higher score = more likely to forget
 */
export function calculateDecay(memory: MemoryRecord, now: Date = new Date()): number {
  const ageMs = now.getTime() - memory.createdAt.getTime();
  const ageDays = ageMs / (1000 * 60 * 60 * 24);
  
  const lastAccessMs = now.getTime() - memory.lastAccessedAt.getTime();
  const lastAccessDays = lastAccessMs / (1000 * 60 * 60 * 24);
  
  // Ebbinghaus-inspired forgetting curve
  // Factors: age, recency of access, access frequency, base importance
  
  const ageFactor = Math.log(ageDays + 1) / 10; // Older = higher decay
  const accessRecency = Math.log(lastAccessDays + 1) / 5; // Not accessed recently = higher decay
  const accessFrequency = 1 / (memory.accessCount + 1); // Less accessed = higher decay
  const importanceFactor = 1 - memory.importance; // Less important = higher decay
  
  // Weighted combination
  const decay = (
    ageFactor * 0.2 +
    accessRecency * 0.3 +
    accessFrequency * 0.2 +
    importanceFactor * 0.3
  );
  
  return Math.min(1, Math.max(0, decay));
}

/**
 * Get memories that should be forgotten (decay > threshold)
 */
export function getDecayedMemories(
  memories: MemoryRecord[],
  threshold: number = 0.7
): MemoryRecord[] {
  return memories
    .map(m => ({ ...m, decayScore: calculateDecay(m) }))
    .filter(m => m.decayScore! > threshold)
    .sort((a, b) => b.decayScore! - a.decayScore!);
}

/**
 * Memory consolidation: merge similar memories, strengthen important ones
 */
export function consolidateMemories(
  memories: MemoryRecord[],
  similarityPairs: Array<[string, string, number]> // [id1, id2, similarity]
): { toMerge: Array<[string, string]>; toStrengthen: string[] } {
  const toMerge: Array<[string, string]> = [];
  const toStrengthen: string[] = [];
  
  for (const [id1, id2, similarity] of similarityPairs) {
    if (similarity > 0.9) {
      // Very similar - merge
      toMerge.push([id1, id2]);
    } else if (similarity > 0.7) {
      // Related - strengthen both (they reinforce each other)
      toStrengthen.push(id1, id2);
    }
  }
  
  return { toMerge, toStrengthen: [...new Set(toStrengthen)] };
}

/**
 * Strengthen a memory (increase importance, reset access time)
 */
export function strengthenMemory(memory: MemoryRecord): MemoryRecord {
  return {
    ...memory,
    importance: Math.min(1, memory.importance + 0.1),
    lastAccessedAt: new Date(),
    accessCount: memory.accessCount + 1
  };
}
