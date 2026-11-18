// Soli Deo Gloria. Probe stack integration only in disposable repositories.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const hooks = fileURLToPath(new URL('../', import.meta.url));
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'leaf-stack-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const repo = path.join(root, 'repo');
  const dir = path.join(repo, '.claude/hooks');
  fs.mkdirSync(dir, { recursive: true });
  for (const file of ['arm-hooks-path.sh', 'observe-tool-use-dispatch.sh']) fs.copyFileSync(path.join(hooks, file), path.join(dir, file));
  const env = { ...process.env, CLAUDE_PROJECT_DIR: repo, GIT_CONFIG_GLOBAL: path.join(root, 'no-global-config'), GIT_CONFIG_NOSYSTEM: '1' };
  for (const key of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'HOUSEHOLD_KEN_ROOT', 'HOOKS_PATH_ARM', 'OBSERVE_TOOL_USE']) delete env[key];
  // Keep the cluster fallback inside the fixture, never the operator's live observer.
  env.HOUSEHOLD_CLUSTER_ROOT = path.join(root, 'cluster');
  const run = (cmd, args, input = '') => spawnSync(cmd, args, { cwd: repo, env, input, encoding: 'utf8' });
  const init = run('git', ['init', '-q']);
  assert.equal(init.status, 0, init.stderr);
  fs.mkdirSync(path.join(repo, '.githooks'));
  const precommit = path.join(repo, '.githooks/pre-commit');
  fs.writeFileSync(precommit, '#!/bin/sh\nexit 0\n', { mode: 0o755 });
  return { root, repo, env, precommit, run, hook: file => run('bash', [path.join(dir, file)]) };
}

test('arming reports configuration, not an unmeasured downstream guard chain', t => {
  const f = fixture(t);
  const r = f.hook('arm-hooks-path.sh');
  assert.equal(r.status, 0, r.stderr);
  assert.equal(f.run('git', ['config', '--get', 'core.hooksPath']).stdout.trim(), '.githooks');
  assert.match(r.stdout, /downstream guard behavior was not verified/);
  assert.doesNotMatch(r.stdout, /are live|dangerous-command staged scan|concept-ledger/);
  const again = f.hook('arm-hooks-path.sh');
  assert.equal(again.status, 0, again.stderr);
  assert.equal(again.stdout, '', 'already configured path is stable');
});

test('arming warns about non-executable installed hooks', t => {
  const f = fixture(t);
  fs.chmodSync(f.precommit, 0o644);
  const r = f.hook('arm-hooks-path.sh');
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stderr, /NOT executable/);
  assert.doesNotMatch(r.stdout, /are live|configured and executable/);
});

test('arming preserves explicit custom configuration without judging an inactive chain', t => {
  const f = fixture(t);
  assert.equal(f.run('git', ['config', 'core.hooksPath', 'operator-hooks']).status, 0);
  fs.chmodSync(f.precommit, 0o644);
  const r = f.hook('arm-hooks-path.sh');
  assert.equal(r.status, 0, r.stderr);
  assert.equal(f.run('git', ['config', '--get', 'core.hooksPath']).stdout.trim(), 'operator-hooks');
  assert.match(r.stdout, /custom hook execution was not evaluated/);
  assert.equal(r.stderr, '');
});

test('observation dispatch is loud but nonfatal when no observer resolves', t => {
  const f = fixture(t);
  const r = f.hook('observe-tool-use-dispatch.sh');
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stderr, /NOT FOUND/);
});

test('observation dispatch forwards payload and reports observer failure without blocking', t => {
  const f = fixture(t);
  f.env.HOUSEHOLD_KEN_ROOT = path.join(f.root, 'observer');
  const observer = path.join(f.env.HOUSEHOLD_KEN_ROOT, '.claude/hooks/observe-tool-use.sh');
  fs.mkdirSync(path.dirname(observer), { recursive: true });
  fs.writeFileSync(observer, '#!/bin/sh\ncat\n');
  const payload = '{"session_id":"inert-probe"}';
  const r = f.run('bash', [path.join(f.repo, '.claude/hooks/observe-tool-use-dispatch.sh')], payload);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout, payload);
  fs.writeFileSync(observer, '#!/bin/sh\nexit 7\n');
  const failed = f.hook('observe-tool-use-dispatch.sh');
  assert.equal(failed.status, 0, failed.stderr);
  assert.match(failed.stderr, /observer failed/);
});

test('observation dispatch reaches the cluster fallback and reports its failure', t => {
  const f = fixture(t);
  const observer = path.join(f.env.HOUSEHOLD_CLUSTER_ROOT, 'ken/.claude/hooks/observe-tool-use.sh');
  fs.mkdirSync(path.dirname(observer), { recursive: true });
  fs.writeFileSync(observer, '#!/bin/sh\ncat\n');
  const payload = '{"session_id":"isolated-cluster-probe"}';
  const r = f.run('bash', [path.join(f.repo, '.claude/hooks/observe-tool-use-dispatch.sh')], payload);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout, payload);
  assert.equal(r.stderr, '');
  fs.writeFileSync(observer, '#!/bin/sh\nexit 7\n');
  const failed = f.hook('observe-tool-use-dispatch.sh');
  assert.equal(failed.status, 0, failed.stderr);
  assert.match(failed.stderr, /observer failed/);
  assert.ok(failed.stderr.includes(observer));
});
