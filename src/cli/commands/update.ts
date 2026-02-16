/**
 * Update persona templates to latest version
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const AGENTS_DIR = path.resolve(__dirname, '../../../agents');

interface UpdateOptions {
  dryRun?: boolean;
}

export async function update(options: UpdateOptions = {}) {
  const workspaceDir = process.cwd();
  
  console.log(chalk.blue('🦞 Checking for updates...'));
  
  // Check if this is a persona workspace
  if (!await fs.pathExists(path.join(workspaceDir, 'SOUL.md'))) {
    console.error(chalk.red('❌ Not a persona workspace. Run "persona init" first.'));
    process.exit(1);
  }
  
  let updatesAvailable = 0;
  
  // Check agent profiles
  const agentProfiles = ['researcher.md', 'coder.md', 'scanner.md', 'analyst.md'];
  
  for (const profile of agentProfiles) {
    const src = path.join(AGENTS_DIR, profile);
    const dest = path.join(workspaceDir, 'agents', profile);
    
    if (await fs.pathExists(src)) {
      const srcContent = await fs.readFile(src, 'utf-8');
      const destExists = await fs.pathExists(dest);
      const destContent = destExists ? await fs.readFile(dest, 'utf-8') : '';
      
      if (srcContent !== destContent) {
        updatesAvailable++;
        if (options.dryRun) {
          console.log(chalk.yellow(`   Would update: agents/${profile}`));
        } else {
          await fs.copy(src, dest);
          console.log(chalk.green(`   ✓ Updated: agents/${profile}`));
        }
      }
    }
  }
  
  if (updatesAvailable === 0) {
    console.log(chalk.green('✅ All templates are up to date!'));
  } else if (options.dryRun) {
    console.log(chalk.yellow(`\n${updatesAvailable} update(s) available. Run without --dry-run to apply.`));
  } else {
    console.log(chalk.green(`\n✅ Applied ${updatesAvailable} update(s).`));
  }
}
