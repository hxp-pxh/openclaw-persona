/**
 * Vector memory operations
 * Wraps the Python memory-vault CLI
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs-extra';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_SCRIPT = path.resolve(__dirname, '../../../memory-vault/vault.py');

interface VmemOptions {
  full?: boolean;
  type?: string;
  threshold?: string;
}

export async function vmem(action: string, args: string[], options: VmemOptions) {
  // Check if vault.py exists
  if (!await fs.pathExists(VAULT_SCRIPT)) {
    console.error(chalk.red('❌ Memory vault not found. Run "persona init" first.'));
    process.exit(1);
  }
  
  // Check for Python
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  
  // Build command arguments
  const cmdArgs = [VAULT_SCRIPT, action];
  
  // Add options
  if (options.full) cmdArgs.push('--full');
  if (options.type) cmdArgs.push('--type', options.type);
  if (options.threshold && action === 'consolidate') {
    cmdArgs.push(`--threshold=${options.threshold}`);
  }
  
  // Add remaining args
  cmdArgs.push(...args);
  
  // Execute
  const proc = spawn(pythonCmd, cmdArgs, {
    stdio: 'inherit',
    cwd: process.cwd()
  });
  
  proc.on('error', (err) => {
    if ((err as any).code === 'ENOENT') {
      console.error(chalk.red('❌ Python3 not found. Please install Python 3.8+'));
    } else {
      console.error(chalk.red(`❌ Error: ${err.message}`));
    }
    process.exit(1);
  });
  
  proc.on('exit', (code) => {
    process.exit(code || 0);
  });
}
