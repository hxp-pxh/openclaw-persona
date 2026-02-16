/**
 * Initialize a new persona workspace
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.resolve(__dirname, '../../../templates');
const AGENTS_DIR = path.resolve(__dirname, '../../../agents');

interface InitOptions {
  force?: boolean;
  name?: string;
}

export async function init(workspace: string = '.', options: InitOptions = {}) {
  const targetDir = path.resolve(workspace);
  const personaName = options.name || 'Assistant';
  
  console.log(chalk.blue('🦞 Initializing openclaw-persona workspace...'));
  console.log(chalk.dim(`   Target: ${targetDir}`));
  
  // Check if workspace exists
  if (!options.force && await fs.pathExists(path.join(targetDir, 'SOUL.md'))) {
    console.log(chalk.yellow('⚠️  Workspace already initialized. Use --force to overwrite.'));
    return;
  }
  
  // Create directories
  await fs.ensureDir(targetDir);
  await fs.ensureDir(path.join(targetDir, 'memory'));
  await fs.ensureDir(path.join(targetDir, 'agents'));
  await fs.ensureDir(path.join(targetDir, '.learnings'));
  await fs.ensureDir(path.join(targetDir, 'tasks'));
  await fs.ensureDir(path.join(targetDir, 'memory-vault'));
  
  // Copy templates
  const templates = ['SOUL.md', 'AGENTS.md', 'USER.md', 'HEARTBEAT.md', 'IDENTITY.md'];
  for (const template of templates) {
    const src = path.join(TEMPLATES_DIR, template);
    const dest = path.join(targetDir, template);
    
    if (await fs.pathExists(src)) {
      let content = await fs.readFile(src, 'utf-8');
      // Replace placeholders
      content = content.replace(/\{\{PERSONA_NAME\}\}/g, personaName);
      content = content.replace(/\{\{DATE\}\}/g, new Date().toISOString().split('T')[0]);
      await fs.writeFile(dest, content);
      console.log(chalk.green(`   ✓ ${template}`));
    }
  }
  
  // Copy agent profiles
  const agentProfiles = ['researcher.md', 'coder.md', 'scanner.md', 'analyst.md'];
  for (const profile of agentProfiles) {
    const src = path.join(AGENTS_DIR, profile);
    const dest = path.join(targetDir, 'agents', profile);
    
    if (await fs.pathExists(src)) {
      await fs.copy(src, dest);
      console.log(chalk.green(`   ✓ agents/${profile}`));
    }
  }
  
  // Create .learnings structure
  const learningsFiles = {
    'ERRORS.md': '# Errors Log\n\nCapture errors and failures here.\n',
    'LEARNINGS.md': '# Learnings Log\n\nCapture corrections and insights here.\n',
    'FEATURE_REQUESTS.md': '# Feature Requests\n\nCapture capability gaps here.\n'
  };
  
  for (const [file, content] of Object.entries(learningsFiles)) {
    await fs.writeFile(path.join(targetDir, '.learnings', file), content);
    console.log(chalk.green(`   ✓ .learnings/${file}`));
  }
  
  // Create tasks template
  await fs.writeFile(
    path.join(targetDir, 'tasks', 'TEMPLATE.md'),
    `# Task: [Title]

**Created:** {{DATE}}
**Status:** 🔄 In Progress

## Objective
What you're trying to accomplish.

## Plan
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Progress Log
- {{DATE}}: Task created

## Notes
Additional context here.
`
  );
  console.log(chalk.green('   ✓ tasks/TEMPLATE.md'));
  
  // Create initial memory file
  const today = new Date().toISOString().split('T')[0];
  await fs.writeFile(
    path.join(targetDir, 'memory', `${today}.md`),
    `# ${today}\n\n### Persona Initialized\n- Workspace created at ${targetDir}\n- Name: ${personaName}\n`
  );
  console.log(chalk.green(`   ✓ memory/${today}.md`));
  
  // Create MEMORY.md
  await fs.writeFile(
    path.join(targetDir, 'MEMORY.md'),
    `# MEMORY — Long-Term Memory

*Last updated: ${today}*

## About This File

This is your curated long-term memory. Unlike daily logs, this contains the distilled essence of what matters.

## What Belongs Here

- Important decisions and their reasoning
- Lessons learned (that should persist)
- Key facts about people, projects, preferences
- Capabilities and limitations discovered

## What Doesn't Belong

- Temporary states
- Raw logs (those go in memory/*.md)
- Sensitive credentials

---

*Start adding memories as you learn and grow.*
`
  );
  console.log(chalk.green('   ✓ MEMORY.md'));
  
  console.log(chalk.blue('\n🦞 Workspace initialized!'));
  console.log(chalk.dim('\nNext steps:'));
  console.log(chalk.dim('  1. Edit SOUL.md to define your persona\'s identity'));
  console.log(chalk.dim('  2. Edit USER.md to describe yourself'));
  console.log(chalk.dim('  3. Run "persona vmem index" to set up vector memory'));
  console.log(chalk.dim('  4. Start OpenClaw in this workspace'));
}
