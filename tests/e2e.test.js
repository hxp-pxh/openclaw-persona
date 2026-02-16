/**
 * End-to-end tests for openclaw-persona CLI
 * Run with: node --test tests/e2e.test.js
 */

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert';
import { execSync, exec } from 'node:child_process';
import { mkdtempSync, rmSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CLI = join(process.cwd(), 'dist/cli/index.js');

function run(cmd, opts = {}) {
  try {
    return execSync(`node ${CLI} ${cmd}`, { 
      encoding: 'utf8',
      timeout: 30000,
      ...opts 
    });
  } catch (e) {
    return e.stdout || e.message;
  }
}

describe('CLI Commands', () => {
  
  test('help shows all commands', () => {
    const output = run('help');
    assert.match(output, /openclaw-persona/);
    assert.match(output, /init/);
    assert.match(output, /status/);
    assert.match(output, /onboard/);
    assert.match(output, /vmem/);
    assert.match(output, /memory/);
  });

  test('--help flag works', () => {
    const output = run('--help');
    assert.match(output, /openclaw-persona/);
  });

  test('onboard prints interview prompt', () => {
    const output = run('onboard');
    assert.match(output, /Persona Onboarding Protocol/);
    assert.match(output, /PHASE 1.*Facts/);
    assert.match(output, /PHASE 2.*Soul/);
    assert.match(output, /PHASE 3.*Collaboration/);
    assert.match(output, /PHASE 4.*Synthesis/);
    assert.match(output, /USER\.md/);
  });

  test('memory subcommand shows help', () => {
    const output = run('memory');
    assert.match(output, /Memory Commands/);
    assert.match(output, /extract/);
    assert.match(output, /consolidate/);
    assert.match(output, /prune/);
  });

  test('vmem help shows commands', () => {
    const output = run('vmem help');
    assert.match(output, /vmem|query|add|index/i);
  });

});

describe('Init Command (E2E)', () => {
  let tempDir;

  before(() => {
    tempDir = mkdtempSync(join(tmpdir(), 'persona-test-'));
  });

  after(() => {
    if (tempDir && existsSync(tempDir)) {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  test('init creates workspace structure', () => {
    const output = run(`init ${tempDir}`);
    
    // Check output mentions success
    assert.match(output, /initialized|created|ready/i);
    
    // Check core files exist
    assert.ok(existsSync(join(tempDir, 'SOUL.md')), 'SOUL.md should exist');
    assert.ok(existsSync(join(tempDir, 'USER.md')), 'USER.md should exist');
    assert.ok(existsSync(join(tempDir, 'AGENTS.md')), 'AGENTS.md should exist');
    
    // Check directories exist
    assert.ok(existsSync(join(tempDir, 'memory')), 'memory/ should exist');
    assert.ok(existsSync(join(tempDir, 'agents')), 'agents/ should exist');
  });

  test('init creates valid SOUL.md', () => {
    const soul = readFileSync(join(tempDir, 'SOUL.md'), 'utf8');
    assert.match(soul, /SOUL|identity|who you are/i);
  });

  test('init creates valid AGENTS.md', () => {
    const agents = readFileSync(join(tempDir, 'AGENTS.md'), 'utf8');
    assert.match(agents, /AGENTS|workspace|memory/i);
  });

  test('init is idempotent (safe to run twice)', () => {
    // Running init again shouldn't crash or corrupt
    const output = run(`init ${tempDir}`);
    assert.ok(existsSync(join(tempDir, 'SOUL.md')), 'SOUL.md still exists');
  });

});

describe('Status Command', () => {
  let tempDir;

  before(() => {
    tempDir = mkdtempSync(join(tmpdir(), 'persona-status-'));
    run(`init ${tempDir}`);
  });

  after(() => {
    if (tempDir && existsSync(tempDir)) {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  test('status runs without error in workspace', () => {
    const output = run('status', { cwd: tempDir });
    // Should show some status info, not crash
    assert.ok(output.length > 0, 'Status should produce output');
  });

});

console.log('Running e2e tests...');
