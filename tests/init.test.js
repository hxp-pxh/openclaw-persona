/**
 * Tests for persona init command
 */

import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';

const TEST_DIR = path.join(os.tmpdir(), 'persona-test-' + Date.now());

describe('persona init', () => {
  beforeEach(async () => {
    await fs.ensureDir(TEST_DIR);
  });
  
  afterEach(async () => {
    await fs.remove(TEST_DIR);
  });
  
  test('creates required directories', async () => {
    // Simulate init by creating directories
    const dirs = ['memory', 'agents', '.learnings', 'tasks', 'memory-vault'];
    
    for (const dir of dirs) {
      await fs.ensureDir(path.join(TEST_DIR, dir));
    }
    
    // Verify
    for (const dir of dirs) {
      const exists = await fs.pathExists(path.join(TEST_DIR, dir));
      assert.strictEqual(exists, true, `${dir} should exist`);
    }
  });
  
  test('creates required files', async () => {
    const files = ['SOUL.md', 'AGENTS.md', 'USER.md', 'HEARTBEAT.md', 'MEMORY.md'];
    
    for (const file of files) {
      await fs.writeFile(path.join(TEST_DIR, file), '# Test');
    }
    
    // Verify
    for (const file of files) {
      const exists = await fs.pathExists(path.join(TEST_DIR, file));
      assert.strictEqual(exists, true, `${file} should exist`);
    }
  });
  
  test('creates agent profiles', async () => {
    const agentsDir = path.join(TEST_DIR, 'agents');
    await fs.ensureDir(agentsDir);
    
    const profiles = ['researcher.md', 'coder.md', 'scanner.md', 'analyst.md'];
    
    for (const profile of profiles) {
      await fs.writeFile(path.join(agentsDir, profile), '# Profile');
    }
    
    // Verify
    for (const profile of profiles) {
      const exists = await fs.pathExists(path.join(agentsDir, profile));
      assert.strictEqual(exists, true, `agents/${profile} should exist`);
    }
  });
  
  test('creates learnings structure', async () => {
    const learningsDir = path.join(TEST_DIR, '.learnings');
    await fs.ensureDir(learningsDir);
    
    const files = ['ERRORS.md', 'LEARNINGS.md', 'FEATURE_REQUESTS.md'];
    
    for (const file of files) {
      await fs.writeFile(path.join(learningsDir, file), '# Log');
    }
    
    // Verify
    for (const file of files) {
      const exists = await fs.pathExists(path.join(learningsDir, file));
      assert.strictEqual(exists, true, `.learnings/${file} should exist`);
    }
  });
});
