#!/usr/bin/env node
/**
 * openclaw-persona CLI
 * Personality, memory, and self-improvement for OpenClaw agents
 */

import { init } from './commands/init.js';
import { vmem } from './commands/vmem.js';
import { update } from './commands/update.js';
import { status } from './commands/status.js';
import { extract, consolidate, prune, stats as memoryStats } from './commands/memory.js';

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  switch (command) {
    case 'init':
      await init(args[1] || process.cwd());
      break;
      
    case 'vmem':
      // vmem expects: action, args array, options
      const vmemAction = args[1] || 'help';
      const vmemArgs = args.slice(2);
      await vmem(vmemAction, vmemArgs, {});
      break;
      
    case 'update':
      await update();
      break;
      
    case 'status':
      await status();
      break;
    
    // Memory lifecycle commands
    case 'memory':
      const subCmd = args[1];
      switch (subCmd) {
        case 'extract':
          await extract(args[2]);
          break;
        case 'consolidate':
          const threshold = parseFloat(args[2]) || 0.85;
          await consolidate(threshold);
          break;
        case 'prune':
          const decay = parseFloat(args[2]) || 0.7;
          const maxAge = parseInt(args[3]) || 180;
          await prune(decay, maxAge);
          break;
        case 'stats':
          await memoryStats();
          break;
        default:
          console.log(`
🧠 Memory Commands:
  persona memory extract          Extract memories from conversation
  persona memory consolidate      Merge similar memories
  persona memory prune            Remove decayed memories
  persona memory stats            Show memory statistics
`);
      }
      break;
      
    case 'help':
    case '--help':
    case '-h':
    default:
      console.log(`
🦞 openclaw-persona v0.2.0

Commands:
  init [dir]              Initialize persona workspace
  status                  Show workspace status
  update                  Update templates to latest
  vmem <cmd>              Vector memory (query/add/index/consolidate/delete)
  memory <cmd>            Memory lifecycle (extract/consolidate/prune/stats)

Memory Lifecycle:
  persona memory extract          Auto-extract from conversations
  persona memory consolidate      Merge similar, strengthen related
  persona memory prune            Forget decayed memories

Examples:
  persona init ~/my-agent
  persona vmem query "user preferences"
  persona memory consolidate 0.9
`);
  }
}

main().catch(console.error);
