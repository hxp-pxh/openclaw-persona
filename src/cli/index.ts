#!/usr/bin/env node
/**
 * openclaw-persona CLI
 * 
 * Personality and memory layer for OpenClaw.
 * Gives your AI assistant continuity, identity, and growth.
 */

import { Command } from 'commander';
import { init } from './commands/init.js';
import { vmem } from './commands/vmem.js';
import { update } from './commands/update.js';
import { status } from './commands/status.js';

const program = new Command();

program
  .name('persona')
  .description('Personality and memory layer for OpenClaw')
  .version('0.1.0');

program
  .command('init [workspace]')
  .description('Initialize a new persona workspace')
  .option('--force', 'Overwrite existing files')
  .option('--name <name>', 'Name for your persona')
  .action(init);

program
  .command('vmem <action> [args...]')
  .description('Vector memory operations (query, add, consolidate, stats, delete)')
  .option('--full', 'Return full text instead of summaries')
  .option('--type <type>', 'Filter by observation type')
  .option('--threshold <n>', 'Similarity threshold for consolidation', '0.85')
  .action(vmem);

program
  .command('update')
  .description('Update persona templates to latest version')
  .option('--dry-run', 'Show what would be updated')
  .action(update);

program
  .command('status')
  .description('Show persona status and memory stats')
  .action(status);

program.parse();
