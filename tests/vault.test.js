/**
 * Tests for memory vault
 */

import { test, describe } from 'node:test';
import assert from 'node:assert';
import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';

const VAULT_SCRIPT = path.resolve(import.meta.dirname, '../memory-vault/vault.py');

describe('memory vault', () => {
  test('vault.py exists', () => {
    const exists = fs.existsSync(VAULT_SCRIPT);
    assert.strictEqual(exists, true, 'vault.py should exist');
  });
  
  test('vault.py has required functions', () => {
    const content = fs.readFileSync(VAULT_SCRIPT, 'utf-8');
    
    const requiredFunctions = [
      'def index_files',
      'def query',
      'def add_observation',
      'def stats',
      'def find_similar',
      'def delete_memory'
    ];
    
    for (const fn of requiredFunctions) {
      assert.ok(content.includes(fn), `Should have ${fn}`);
    }
  });
  
  test('vault.py has CLI commands', () => {
    const content = fs.readFileSync(VAULT_SCRIPT, 'utf-8');
    
    const commands = ['index', 'query', 'add', 'stats', 'consolidate', 'delete'];
    
    for (const cmd of commands) {
      assert.ok(content.includes(`cmd == '${cmd}'`), `Should handle ${cmd} command`);
    }
  });
});
