/**
 * Memory Importance Scoring
 * Not all memories are equal - score and prioritize
 */

export interface ImportanceFactors {
  // Content-based
  isDecision: boolean;       // Decisions are important
  isPreference: boolean;     // Preferences personalize
  isCorrection: boolean;     // Corrections prevent future errors
  isTodo: boolean;           // Action items need tracking
  
  // Context-based
  mentionedByUser: boolean;  // User explicitly stated
  repeatedMention: number;   // How many times mentioned
  recentlyAccessed: boolean; // Recently retrieved
  
  // Semantic
  uniqueness: number;        // How different from existing memories (0-1)
  specificity: number;       // Concrete vs abstract (0-1)
}

/**
 * Calculate importance score from factors
 */
export function calculateImportance(factors: ImportanceFactors): number {
  let score = 0.5; // Base score
  
  // Content-based adjustments
  if (factors.isDecision) score += 0.2;
  if (factors.isPreference) score += 0.15;
  if (factors.isCorrection) score += 0.25; // Corrections are very valuable
  if (factors.isTodo) score += 0.1;
  
  // Context-based adjustments
  if (factors.mentionedByUser) score += 0.15;
  score += Math.min(0.2, factors.repeatedMention * 0.05);
  if (factors.recentlyAccessed) score += 0.05;
  
  // Semantic adjustments
  score += factors.uniqueness * 0.15;
  score += factors.specificity * 0.1;
  
  return Math.min(1, Math.max(0, score));
}

/**
 * Quick importance classification
 */
export function classifyImportance(score: number): 'critical' | 'high' | 'medium' | 'low' {
  if (score >= 0.85) return 'critical';
  if (score >= 0.65) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
}

/**
 * Memory type importance defaults
 */
export const TYPE_IMPORTANCE: Record<string, number> = {
  'correction': 0.9,    // Learning from mistakes
  'decision': 0.8,      // Choices made
  'preference': 0.7,    // User preferences
  'fact': 0.6,          // Factual information
  'todo': 0.6,          // Action items
  'observation': 0.4,   // General observations
  'transient': 0.2      // Temporary states
};

/**
 * Adjust importance based on age and access patterns
 * Called periodically to update scores
 */
export function ageAdjustedImportance(
  baseImportance: number,
  ageDays: number,
  accessCount: number,
  lastAccessDays: number
): number {
  // Important memories decay slower
  const decayRate = 1 - baseImportance; // High importance = low decay
  const agePenalty = Math.log(ageDays + 1) * decayRate * 0.05;
  
  // Frequent access boosts importance
  const accessBonus = Math.min(0.2, accessCount * 0.02);
  
  // Recent access prevents decay
  const recencyBonus = lastAccessDays < 7 ? 0.1 : 0;
  
  return Math.min(1, Math.max(0, baseImportance - agePenalty + accessBonus + recencyBonus));
}
