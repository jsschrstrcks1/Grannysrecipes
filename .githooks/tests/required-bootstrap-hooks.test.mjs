// Soli Deo Gloria. Exercise registration removal in a disposable repository.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const repo = fileURLToPath(new URL('../../', import.meta.url));
const guard = path.join(repo, '.githooks/check-required-hooks.sh');
const settings = JSON.parse(fs.readFileSync(path.join(repo, '.claude/settings.json'), 'utf8'));
const required = ['bootstrap-guard.mjs', 'bootstrap-stamp-hook.mjs', 'dangerous-command-guard.mjs'];

test('required-hooks accepts the shipped registrations and refuses each removed bootstrap guard', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'leaf-required-hooks-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const env = { ...process.env };
  for (const key of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR']) delete env[key];
  const run = (command, args) => spawnSync(command, args, { cwd: root, env, encoding: 'utf8' });
  const init = run('git', ['init', '-q']);
  assert.equal(init.status, 0, init.stderr);
  fs.mkdirSync(path.join(root, '.claude'));
  const file = path.join(root, '.claude/settings.json');
  fs.writeFileSync(file, JSON.stringify(settings));
  const control = run('bash', [guard]);
  assert.equal(control.status, 0, control.stderr);
  for (const name of required) {
    const changed = structuredClone(settings);
    let removed = 0;
    for (const groups of Object.values(changed.hooks)) {
      for (const group of groups) {
        group.hooks = group.hooks.filter(hook => {
          if (!String(hook.command || '').includes(name)) return true;
          removed++;
          return false;
        });
      }
    }
    assert.ok(removed > 0, `fixture actually contains ${name}`);
    fs.writeFileSync(file, JSON.stringify(changed));
    const result = run('bash', [guard]);
    assert.equal(result.status, 1, `${name}: ${result.stderr}`);
    assert.ok(result.stderr.includes(name), result.stderr);
  }
});
