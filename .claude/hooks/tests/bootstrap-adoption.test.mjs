// Soli Deo Gloria. Exercise shipped hooks with isolated state, never live commands.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const hooks = fileURLToPath(new URL('../', import.meta.url));
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'sophos-adoption-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const repo = path.join(root, 'leaf');
  fs.mkdirSync(path.join(repo, '.claude/hooks'), { recursive: true });
  for (const f of ['bootstrap-lib.mjs', 'bootstrap-guard.mjs', 'bootstrap-stamp-hook.mjs']) {
    fs.copyFileSync(path.join(hooks, f), path.join(repo, '.claude/hooks', f));
  }
  const env = { ...process.env, HOUSEHOLD_REPO_ROOT: repo, HOUSEHOLD_BOOTSTRAP_ROOT: path.join(root, 'stamps'), HOUSEHOLD_BOOTSTRAP_GUARD_BLOCK: '1' };
  delete env.HOUSEHOLD_BOOTSTRAP_EVENTS;
  const run = (file, input) => spawnSync(process.execPath, [path.join(repo, '.claude/hooks', file)], { env, input: JSON.stringify(input), encoding: 'utf8' });
  const script = code => spawnSync(process.execPath, ['--input-type=module', '-e', `import * as b from ${JSON.stringify(path.join(repo, '.claude/hooks/bootstrap-lib.mjs'))}; import fs from 'node:fs'; ${code}`], { env, encoding: 'utf8' });
  const input = { session_id: 'test', cwd: repo, tool_name: 'Write', tool_input: { file_path: path.join(repo, 'inert.txt') } };
  return { root, repo, env, run, script, input };
}

test('leaf denies unstamped writes without creating an orphan ledger', t => {
  const f = fixture(t);
  const r = f.run('bootstrap-guard.mjs', f.input);
  assert.equal(r.status, 2, r.stderr);
  assert.match(r.stderr, /Denial NOT ledgered/);
  assert.equal(fs.existsSync(path.join(f.repo, '.household-library')), false);
});

test('observing the required reads allows the same session', t => {
  const f = fixture(t);
  const layers = ['skills/soli-deo-gloria/SKILL.md', 'skills/careful-not-clever/SKILL.md', 'skills/sophos/SKILL.md', 'docs/SOPHOS-OPERATING-SYSTEM.md', 'docs/HOUSEHOLD-AGENT-RULEBOOK.md', 'skills/household-library/SKILL.md'];
  for (const file_path of layers) {
    const r = f.run('bootstrap-stamp-hook.mjs', { ...f.input, tool_name: 'Read', tool_input: { file_path } });
    assert.equal(r.status, 0, r.stderr);
  }
  f.run('bootstrap-stamp-hook.mjs', { ...f.input, tool_name: 'Bash', tool_input: { command: 'node admin/recall-memory.mjs' } });
  const r = f.run('bootstrap-guard.mjs', f.input);
  assert.equal(r.status, 0, r.stderr);
  const stamp = JSON.parse(fs.readFileSync(path.join(f.env.HOUSEHOLD_BOOTSTRAP_ROOT, 'test.json'), 'utf8'));
  assert.equal(stamp.ledgered, false, 'a skipped leaf ledger is not a successful append');
  assert.equal(fs.existsSync(path.join(f.repo, '.household-library')), false);
});

test('symlinked leaf writes deny even when several parent directories do not exist', t => {
  const f = fixture(t);
  const alias = path.join(f.root, 'alias');
  fs.symlinkSync(f.repo, alias, 'dir');
  for (const suffix of ['inert.txt', 'missing/deeper/inert.txt']) {
    const r = f.run('bootstrap-guard.mjs', { ...f.input, tool_input: { file_path: path.join(alias, suffix) } });
    assert.equal(r.status, 2, `${suffix}: ${r.stderr}`);
  }
  const outside = f.run('bootstrap-guard.mjs', { ...f.input, tool_input: { file_path: path.join(f.root, 'outside/inert.txt') } });
  assert.equal(outside.status, 0, outside.stderr);
});

test('verification with a missing secret is read-only', t => {
  const f = fixture(t);
  const r = f.script(`fs.mkdirSync(b.stampRoot(), {recursive:true}); const s=b.newStamp('test'); s.hmac='invalid'; fs.writeFileSync(b.stampPath('test'),JSON.stringify(s)); console.log(b.verifyStamp('test'));`);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /forged/);
  assert.equal(fs.existsSync(path.join(f.env.HOUSEHOLD_BOOTSTRAP_ROOT, '.secret')), false);
});

test('altering nested read evidence invalidates the seal', t => {
  const f = fixture(t);
  const r = f.script(`const s=b.newStamp('test'); b.saveStamp(s); s.layers_read.sophos='fabricated'; fs.writeFileSync(b.stampPath('test'),JSON.stringify(s)); console.log(b.verifyStamp('test') === 'forged');`);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout.trim(), 'true');
});

test('disk merge rejects a forged stamp rather than sealing its claimed reads', t => {
  const f = fixture(t);
  const r = f.script(`const s=b.newStamp('test'); s.layers_read.sophos='fabricated'; s.hmac='invalid'; fs.mkdirSync(b.stampRoot(),{recursive:true}); fs.writeFileSync(b.stampPath('test'),JSON.stringify(s)); const fresh=b.newStamp('test'); b.mergeLayersFromDisk(fresh); console.log(fresh.layers_read.sophos === null);`);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout.trim(), 'true');
});

test('legacy seals are rejected even when their signing secret is available', t => {
  const f = fixture(t);
  const r = f.script(`const {createHmac}=await import('node:crypto'); const s=b.newStamp('test'); const key=b.getSecret(); const {hmac,...body}=s; s.hmac=createHmac('sha256',key).update(JSON.stringify(body,Object.keys(body).sort())).digest('hex'); fs.writeFileSync(b.stampPath('test'),JSON.stringify(s)); console.log(b.verifyStamp('test') === 'forged');`);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout.trim(), 'true');
});

test('default v2 storage is separate for Claude and Grok; explicit override is preserved', t => {
  const f = fixture(t);
  const r = f.script(`const explicit=b.stampRoot(); delete process.env.HOUSEHOLD_BOOTSTRAP_ROOT; process.env.HOUSEHOLD_RUNTIME='claude-code'; const claude=b.stampRoot(); process.env.HOUSEHOLD_RUNTIME='grok'; console.log(JSON.stringify({explicit,claude,grok:b.stampRoot()}));`);
  assert.equal(r.status, 0, r.stderr);
  const paths = JSON.parse(r.stdout);
  assert.equal(paths.explicit, f.env.HOUSEHOLD_BOOTSTRAP_ROOT);
  assert.equal(paths.claude, path.join(os.homedir(), '.claude/household-bootstrap/household-v2'));
  assert.equal(paths.grok, path.join(os.homedir(), '.grok/household-bootstrap/household-v2'));
});
