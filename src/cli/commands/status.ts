/**
 * Show persona status and memory stats
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_SCRIPT = path.resolve(__dirname, '../../../memory-vault/vault.py');

export async function status() {
  const workspaceDir = process.cwd();
  
  console.log(chalk.blue('🦞 Persona Status\n'));
  
  // Check workspace files
  const files = {
    'SOUL.md': 'Identity',
    'AGENTS.md': 'Operating rules',
    'USER.md': 'User context',
    'MEMORY.md': 'Long-term memory',
    'HEARTBEAT.md': 'Periodic tasks',
    'IDENTITY.md': 'Name/avatar'
  };
  
  console.log(chalk.bold('Workspace Files:'));
  for (const [file, desc] of Object.entries(files)) {
    const exists = await fs.pathExists(path.join(workspaceDir, file));
    const status = exists ? chalk.green('✓') : chalk.red('✗');
    console.log(`  ${status} ${file} — ${desc}`);
  }
  
  // Count memory files
  const memoryDir = path.join(workspaceDir, 'memory');
  let memoryCount = 0;
  let memorySize = 0;
  
  if (await fs.pathExists(memoryDir)) {
    const files = await fs.readdir(memoryDir);
    for (const file of files) {
      if (file.endsWith('.md')) {
        memoryCount++;
        const stat = await fs.stat(path.join(memoryDir, file));
        memorySize += stat.size;
      }
    }
  }
  
  console.log(chalk.bold('\nMemory:'));
  console.log(`  Daily logs: ${memoryCount} files (${(memorySize / 1024).toFixed(1)} KB)`);
  
  // Check MEMORY.md size
  const memoryMd = path.join(workspaceDir, 'MEMORY.md');
  if (await fs.pathExists(memoryMd)) {
    const stat = await fs.stat(memoryMd);
    console.log(`  MEMORY.md: ${(stat.size / 1024).toFixed(1)} KB`);
  }
  
  // Count agent profiles
  const agentsDir = path.join(workspaceDir, 'agents');
  let agentCount = 0;
  if (await fs.pathExists(agentsDir)) {
    const files = await fs.readdir(agentsDir);
    agentCount = files.filter(f => f.endsWith('.md')).length;
  }
  console.log(chalk.bold('\nAgent Profiles:'));
  console.log(`  ${agentCount} profile(s) available`);
  
  // Count learnings
  const learningsDir = path.join(workspaceDir, '.learnings');
  let learningsCount = { errors: 0, learnings: 0, features: 0 };
  
  if (await fs.pathExists(learningsDir)) {
    for (const [file, key] of [['ERRORS.md', 'errors'], ['LEARNINGS.md', 'learnings'], ['FEATURE_REQUESTS.md', 'features']]) {
      const filepath = path.join(learningsDir, file);
      if (await fs.pathExists(filepath)) {
        const content = await fs.readFile(filepath, 'utf-8');
        const entries = (content.match(/^## \[/gm) || []).length;
        (learningsCount as any)[key] = entries;
      }
    }
  }
  
  console.log(chalk.bold('\nSelf-Improvement:'));
  console.log(`  Errors logged: ${learningsCount.errors}`);
  console.log(`  Learnings captured: ${learningsCount.learnings}`);
  console.log(`  Feature requests: ${learningsCount.features}`);
  
  // Try to get vector memory stats
  if (await fs.pathExists(VAULT_SCRIPT)) {
    console.log(chalk.bold('\nVector Memory:'));
    
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const proc = spawn(pythonCmd, [VAULT_SCRIPT, 'stats'], {
      cwd: workspaceDir
    });
    
    let output = '';
    proc.stdout?.on('data', (data) => {
      output += data.toString();
    });
    
    proc.on('close', (code) => {
      if (code === 0 && output) {
        try {
          const stats = JSON.parse(output);
          console.log(`  Total chunks: ${stats.total_chunks || 0}`);
          if (stats.by_type) {
            console.log(`  By type: ${JSON.stringify(stats.by_type)}`);
          }
        } catch {
          console.log(chalk.dim('  (Run "persona vmem stats" for details)'));
        }
      } else {
        console.log(chalk.dim('  Not indexed yet. Run "persona vmem index"'));
      }
    });
  }
}
