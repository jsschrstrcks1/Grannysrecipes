// bootstrap-lib.mjs — shared loud-bootstrap stamp + guard logic.
// Spec: docs/HOUSEHOLD-LOUD-BOOTSTRAP-REQUIREMENT.md v1.2.0 (R1–R3).
// HLS: loud-bootstrap-impl-claude-code · loud-bootstrap-impl-grok
//
// Dual-runtime: Claude Code (snake_case tools) + Grok (camelCase tools).
// Tamper-evidence grade: FRICTION, not proof (named limit, spec §4.1).
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

/** Repo that contains this hooks tree (open-claw-stuff / ocs-work clone). */
export const HOOK_FILE_REPO_ROOT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
);
/** @deprecated Prefer getRepoRoot(input) — kept for Claude test compatibility. */
export const REPO_ROOT = HOOK_FILE_REPO_ROOT;
export const REPO_NAME = path.basename(HOOK_FILE_REPO_ROOT);

// Layer keys → canonical file suffix (read-observed). memory-recall is
// command-observed (spec §4.1 per-layer observation table).
export const LAYER_SUFFIXES = {
  "soli-deo-gloria": "skills/soli-deo-gloria/SKILL.md",
  "careful-not-clever": "skills/careful-not-clever/SKILL.md",
  "sophos": "skills/sophos/SKILL.md",
  "sophos-os": "docs/SOPHOS-OPERATING-SYSTEM.md",
  "household-rulebook": "docs/HOUSEHOLD-AGENT-RULEBOOK.md",
  "household-library": "skills/household-library/SKILL.md",
};
export const RECALL_CMD_RE =
  /(memory_ops\.py\s+recall|recall-memory\.mjs|memory_evidence\.py\s+recall)/;
export const ALL_LAYERS = [...Object.keys(LAYER_SUFFIXES), "memory-recall"];

// A Bash READ of one or more Layer 0/1 files credits each of them, mirroring RECALL_CMD_RE
// for recall. Closes the gap where an agent reading the layers via `cat`/`sed`/`head` — which
// "auto mode" actively instructs — got NO credit and was falsely denied every mutation for the
// whole session (measured live 2026-09-05, cost ~15 turns; HLS #3317). A read VERB is REQUIRED,
// so a mere mention (`echo path`), a delete (`rm path`), or a move (`mv path`) of a layer path
// is never miscredited as a read. The credit is no weaker than the Read tool's: both mean "the
// layer content was accessed", and neither can prove the agent absorbed it.
export const LAYER_READ_VERB_RE =
  /(?:^|[;&|]\s*|\s|\()(?:cat|bat|less|more|view|nl|od|xxd|sed|head|tail)\b/;
export function layersFromBashRead(command) {
  const s = String(command || "");
  if (!LAYER_READ_VERB_RE.test(s)) return [];
  const hits = [];
  for (const [key, suffix] of Object.entries(LAYER_SUFFIXES)) {
    if (s.includes(suffix)) hits.push(key);
  }
  return hits;
}

/** Grok / Claude tool names → canonical names used by stamp + guard.
 *  Keys are lower-case; lookup is case-insensitive (adv: `bash` / `RUN_TERMINAL_COMMAND`). */
const TOOL_ALIASES = {
  read: "Read",
  read_file: "Read",
  bash: "Bash",
  run_terminal_command: "Bash",
  shell: "Bash",
  edit: "Edit",
  write: "Write",
  multiedit: "Edit",
  search_replace: "Edit",
  notebookedit: "NotebookEdit",
  notebook_edit: "NotebookEdit",
};

export function getRuntime() {
  const r = String(process.env.HOUSEHOLD_RUNTIME || "").trim().toLowerCase();
  if (r === "grok" || r === "claude-code" || r === "codex" || r === "hermes") return r;
  return "claude-code";
}

export function getPatron() {
  return process.env.HOUSEHOLD_PATRON
    || (getRuntime() === "grok" ? "grok1" : "claude-code");
}

// Household-repo markers — what makes the loud-bootstrap belt apply to a tree.
// #3077 (yumi, 2026-09-03): the original three markers are things only a FULL open-claw-stuff
// clone carries. Leaf repos onboarded per spec §5.2 (Project-Sophos, the recipe repos) carry
// the hook trio and the synced front door under .claude/ and NONE of the three — so the guard
// they carried answered "not a household repo", exited 0 on every unstamped mutation, and
// bootstrap-dispatch (which keys "onboarded" on the guard FILE existing) reported them as
// enforced. Measured live through the user-level dispatcher with inert probes: unstamped
// Write, Edit and `git commit` into Project-Sophos ALLOWED; the same probes into ocs-work
// DENIED. Four of 22 onboarded repos on the operator Mac had that shape. "Present is not
// runnable" (UL-888 / UL-1016 class) sitting on the P0 mutation gate.
// Rule: a marker must be something that STAYS (a moved document is UL-266 again), and the
// onboarding itself is a marker — carrying this guard IS being a household repo, which is
// the same definition bootstrap-dispatch.mjs uses for "onboarded". Named limit: a guard copy
// dropped into any tree makes that tree guarded; that is the belt doing its job, not a false
// positive — the dispatcher would already have spawned it.
export const HOUSEHOLD_MARKERS = [
  ".claude/hooks/bootstrap-guard.mjs", // the onboarding itself (spec §5.2) — dispatcher parity
  ".claude/skills/sophos/SKILL.md",    // synced front door (leaf-repo layout)
  "skills/sophos/SKILL.md",            // canonical front door (open-claw-stuff layout)
  ".household-root",                   // machine-neutral discovery file (household-root-resolver step 3)
  ".household-library",
  "docs/SOPHOS-OPERATING-SYSTEM.md",
];

export function isHouseholdRepo(root) {
  if (!root) return false;
  try {
    return HOUSEHOLD_MARKERS.some((m) => fs.existsSync(path.join(root, ...m.split("/"))));
  } catch {
    return false;
  }
}

function walkHouseholdRoot(start) {
  let cur = path.resolve(start);
  for (let i = 0; i < 8; i++) {
    if (isHouseholdRepo(cur)) return cur;
    const parent = path.dirname(cur);
    if (parent === cur) break;
    cur = parent;
  }
  return null;
}

/**
 * Resolve household repo root for this hook invocation.
 * Prefer env, then workspace/cwd markers, else the hooks tree's clone.
 */
export function getRepoRoot(input = null) {
  if (process.env.HOUSEHOLD_REPO_ROOT) {
    return path.resolve(process.env.HOUSEHOLD_REPO_ROOT);
  }
  if (input) {
    for (const key of ["workspaceRoot", "workspace_root", "cwd"]) {
      const v = input[key];
      if (v) {
        const found = walkHouseholdRoot(String(v));
        if (found) return found;
      }
    }
  }
  return HOOK_FILE_REPO_ROOT;
}

export function getRepoName(input = null) {
  return path.basename(getRepoRoot(input));
}

/**
 * Normalize Claude (snake_case) and Grok (camelCase) hook stdin into one shape.
 * tool_name is canonical (Read|Bash|Edit|Write|NotebookEdit|…).
 */
export function normalizeHookInput(raw) {
  if (!raw || typeof raw !== "object") return null;
  // Session id comes from the hook PAYLOAD only — deliberately never from the
  // environment. 2026-08-08: an agent proposed a CLAUDE_CODE_SESSION_ID fallback after
  // seeing an id-less denial, then found it broke three sessionid-contract tests and
  // was solving a bug that did not exist. Two reasons it must stay payload-only:
  //   1. The premise was wrong. This runtime DOES supply session_id — the denial came
  //      from a hand-made probe JSON that omitted it, not from a real invocation. The
  //      real failure was that the hooks were never registered at all (multi-root/remote;
  //      SOPHOS-OPERATING-SYSTEM §0 case 2, memory 6857086c, 2026-07-20). Fix the
  //      registration (admin/install-bootstrap-dispatch.mjs), not the attribution.
  //   2. Even if it were needed, env is AMBIENT, not per-invocation: an exported value
  //      lets an id-less call inherit an identity the runtime never assigned it, which
  //      is exactly the hole sessionIdValid() closes. The tests encode that contract.
  const session_id = raw.session_id ?? raw.sessionId ?? raw.sessionID ?? "";
  const rawTool = String(raw.tool_name ?? raw.toolName ?? "");
  const tool_name = TOOL_ALIASES[rawTool.toLowerCase()] || rawTool;
  const tool_input = raw.tool_input ?? raw.toolInput ?? {};
  // Unify path fields: Claude file_path, Grok target_file / path
  const file_path =
    tool_input.file_path
    ?? tool_input.target_file
    ?? tool_input.path
    ?? tool_input.notebook_path
    ?? "";
  // Shell command: string, or rare array form (join with spaces for scan only).
  let command = tool_input.command ?? tool_input.cmd ?? "";
  if (Array.isArray(command)) command = command.map(String).join(" ");
  else command = String(command ?? "");
  const normalized_input = {
    ...tool_input,
    file_path: file_path || tool_input.file_path,
    command,
  };
  return {
    session_id: String(session_id),
    tool_name,
    tool_input: normalized_input,
    workspaceRoot: raw.workspaceRoot ?? raw.workspace_root ?? raw.cwd ?? "",
    raw,
  };
}

// Stamp root is HOUSEHOLD-SHARED, not per-repo (spec §5.2 A5, operator directive
// 2026-07-20): the six-layer read order is household-global and a session is one
// session across every repo it touches — per-repo buckets demand the same canonical
// reads once per repo, and a multi-repo session bootstrapped in one repo is denied
// in the next. Measured live 2026-08-19: Project-Sophos's guard (A5-lineage hooks,
// shared bucket) was mechanically unsatisfiable because the canonical stamp hook
// filed reads in a per-repo bucket its checker never consulted. The A5
// implementation (5ba8fced) never merged to main; the per-repo variant arrived in a
// bulk hook import (66b53970) with no counter-rationale — this restores the spec'd
// design, keeping main's dual-runtime split and the env override. `input` stays in
// the signature for caller compatibility; the location no longer depends on it.
// Migration cost, named: stamps in the old per-repo buckets are not read from the
// new location, so each live session re-earns its stamp once via the read order.
// Operator applied 2026-08-19 (HLS p1-loud-bootstrap-spec-vs-lib-stamp-root).
export function stampRoot(input = null) {
  if (process.env.HOUSEHOLD_BOOTSTRAP_ROOT) {
    return process.env.HOUSEHOLD_BOOTSTRAP_ROOT;
  }
  const runtime = getRuntime();
  if (runtime === "grok") {
    return path.join(os.homedir(), ".grok", "household-bootstrap", "household-v2");
  }
  return path.join(os.homedir(), ".claude", "household-bootstrap", "household-v2");
}

export function eventsPath(input = null) {
  if (process.env.HOUSEHOLD_BOOTSTRAP_EVENTS) {
    return process.env.HOUSEHOLD_BOOTSTRAP_EVENTS;
  }
  return path.join(getRepoRoot(input), ".household-library", "events.jsonl");
}

function secretPath(input = null) {
  return path.join(stampRoot(input), ".secret");
}

// The HMAC key for stamp sealing/verification. A failed READ must never become a WRITE
// (p1-guard-residual / #2752): distinguish a genuine first run (no secret yet -> create) from
// an existing-but-UNREADABLE secret. Overwriting the latter would ROTATE the key and ERASE the
// on-disk tamper signal, and THROWING would escape bootstrap-guard's outer catch, which fails
// OPEN (exit 0). On any non-ENOENT read error — or a read-only caller (verify) that reached a
// missing secret — do neither: return an EPHEMERAL, unpersisted key so every HMAC check fails
// CLOSED ("forged") while the on-disk secret is left untouched. `allowCreate` is the asymmetry:
// only sealing (first run) may mint; verification is strictly read-only.
export function getSecret(input = null, { allowCreate = true } = {}) {
  const p = secretPath(input);
  try {
    return fs.readFileSync(p, "utf8").trim();
  } catch (e) {
    const code = e && e.code;
    if (code === "ENOENT" && allowCreate) {
      fs.mkdirSync(stampRoot(input), { recursive: true });
      const s = crypto.randomBytes(32).toString("hex");
      fs.writeFileSync(p, s, { mode: 0o600 });
      return s;
    }
    console.error(
      `bootstrap-lib.getSecret: secret at ${p} could not be read (${code || "unknown"})${allowCreate ? "" : " under a read-only check"} — using an ephemeral key so verification fails CLOSED; the on-disk secret was NOT overwritten. Restore its permissions to re-enable bootstrap.`,
    );
    return crypto.randomBytes(32).toString("hex");
  }
}

export function hmacOf(stamp, secret) {
  const { hmac, ...body } = stamp;
  // Recursively bind the read evidence too. A replacer array drops nested keys.
  // Legacy seals must be re-earned through observed reads; never accept both formats.
  const canon = JSON.stringify(canonicalEventBody(body));
  return crypto.createHmac("sha256", secret).update(canon).digest("hex");
}

// Invalid ids must never satisfy the gate (loud-bootstrap-sessionid-contract).
export function sessionIdValid(raw) {
  const s = String(raw ?? "").trim();
  return s !== "" && s.toLowerCase() !== "unknown";
}

/**
 * The ONE session-id resolution both the guard and the stamp writer use. They
 * MUST agree: if the stamp hook records reads under one key and the guard checks
 * another, a fully-bootstrapped session is denied and pushed to the escape hatch
 * (p2-bootstrap-guard-stamp-writer-session-id-split, measured 2026-08-09). An id
 * sessionIdValid rejects (empty, "unknown" in any case, whitespace-only) resolves
 * to the literal "unknown" — the same key the guard denies under — so the two can
 * never key a different stamp file for the same payload.
 */
export function resolveSessionId(input) {
  const id = input && typeof input === "object" ? input.session_id : input;
  return sessionIdValid(id) ? String(id) : "unknown";
}

export function stampPath(sessionId, input = null) {
  const safe = String(sessionId || "unknown").replace(/[^A-Za-z0-9_.-]/g, "_");
  return path.join(stampRoot(input), `${safe}.json`);
}

export function loadStamp(sessionId, input = null) {
  try {
    return JSON.parse(fs.readFileSync(stampPath(sessionId, input), "utf8"));
  } catch {
    return null;
  }
}

export function newStamp(sessionId, input = null) {
  const layers = {};
  for (const k of ALL_LAYERS) layers[k] = null;
  const runtime = getRuntime();
  return {
    session_id: String(sessionId || "unknown"),
    runtime,
    repo: getRepoName(input),
    patron: getPatron(),
    started_at: new Date().toISOString(),
    layers_read: layers,
    grade: "friction",
    written_by:
      runtime === "grok" ? "bootstrap-stamp-hook.mjs(grok)" : "bootstrap-stamp-hook.mjs",
    ledgered: false,
    denials: 0,
  };
}

export function saveStamp(stamp, input = null) {
  fs.mkdirSync(stampRoot(input), { recursive: true });
  stamp.hmac = hmacOf(stamp, getSecret(input));
  fs.writeFileSync(
    stampPath(stamp.session_id, input),
    JSON.stringify(stamp, null, 2) + "\n",
  );
}

/**
 * Merge-on-write for parallel Reads (UL-078). The stamp hook is read-modify-write: two Read events
 * in one session both load the SAME stamp, each set their own layer, and the last saveStamp()
 * clobbers the layer the other added. A fully-read session then looks incomplete and is denied.
 * Before writing, union this stamp layers_read with whatever is on disk NOW (a concurrent hook may
 * have written a layer since we loaded), keeping the EARLIER timestamp per layer, and adopt an
 * on-disk ledgered:true so the bootstrap event is not appended twice. Not a lock: it converts a
 * last-writer CLOBBER into a last-writer UNION, the standard mitigation for this class.
 */
export function mergeLayersFromDisk(stamp, input = null) {
  const onDisk = verifyStamp(stamp.session_id, input);
  if (!onDisk || typeof onDisk !== "object") return stamp;
  stamp.layers_read = stamp.layers_read || {};
  for (const [layer, ts] of Object.entries(onDisk.layers_read || {})) {
    if (!ts) continue;
    const mine = stamp.layers_read[layer];
    stamp.layers_read[layer] = mine ? (mine < ts ? mine : ts) : ts;   // earliest read wins
  }
  if (onDisk.ledgered) stamp.ledgered = true;
  return stamp;
}

// null = missing; "forged" = HMAC mismatch; otherwise the verified stamp object.
export function verifyStamp(sessionId, input = null) {
  const stamp = loadStamp(sessionId, input);
  if (!stamp) return null;
  // Verification is READ-ONLY: never mint/write a secret while checking one (a failed read must
  // not become a write — p1-guard-residual/#2752). A missing-or-unreadable secret -> ephemeral -> forged.
  if (!stamp.hmac || stamp.hmac !== hmacOf(stamp, getSecret(input, { allowCreate: false }))) return "forged";
  return stamp;
}

export function missingLayers(stamp) {
  if (!stamp || stamp === "forged") return [...ALL_LAYERS];
  return ALL_LAYERS.filter((k) => !stamp.layers_read?.[k]);
}

/** Canonicalize like admin/event-chain.mjs so sealed hashes match library.mjs. */
function canonicalEventBody(value) {
  if (Array.isArray(value)) return value.map(canonicalEventBody);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalEventBody(value[key])]),
    );
  }
  return value;
}

/**
 * When the household events ledger has started a hash chain, seal appends so
 * hook denials cannot brick library.mjs with `unchained_event_after_chain`.
 * Test ledgers (HOUSEHOLD_BOOTSTRAP_EVENTS) and pre-chain ledgers stay plain.
 */
function sealIfChainStarted(payload, file) {
  if (process.env.HOUSEHOLD_BOOTSTRAP_EVENTS) return payload;
  let prior = [];
  try {
    const text = fs.readFileSync(file, "utf8");
    prior = text.trim()
      ? text.trim().split("\n").filter(Boolean).map((l) => JSON.parse(l))
      : [];
  } catch {
    return payload;
  }
  let parent = null;
  for (let i = prior.length - 1; i >= 0; i--) {
    if (typeof prior[i]?.event_hash === "string") {
      parent = prior[i].event_hash;
      break;
    }
  }
  if (!parent) return payload; // chain not started (or empty)
  const sealed = { ...payload, prev_hash: parent };
  const body = { ...sealed };
  delete body.event_hash;
  const digest = crypto
    .createHash("sha256")
    .update(JSON.stringify(canonicalEventBody(body)), "utf8")
    .digest("hex");
  return { ...sealed, event_hash: `sha256:${digest}` };
}

function pidAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === "EPERM";
  }
}

// Hook side-channels share the library CLI's .catalog.lock. The CLI may repair
// events.jsonl from a full snapshot before appending; an unlocked hook append in
// that interval would otherwise be erased by the atomic rename.
function withLibraryLock(file, fn) {
  const root = path.dirname(file);
  fs.mkdirSync(root, { recursive: true });
  const lockPath = path.join(root, ".catalog.lock");
  const deadline = Date.now() + 5000;
  let fd = null;
  for (;;) {
    try {
      fd = fs.openSync(lockPath, "wx");
      fs.writeSync(fd, String(process.pid));
      break;
    } catch (error) {
      if (error?.code !== "EEXIST") throw error;
      try {
        const pid = Number.parseInt(fs.readFileSync(lockPath, "utf8").trim(), 10);
        const ageMs = Date.now() - fs.statSync(lockPath).mtimeMs;
        const reclaim = Number.isInteger(pid)
          ? (!pidAlive(pid) || ageMs > 300_000)
          : ageMs > 30_000;
        if (reclaim) fs.unlinkSync(lockPath);
      } catch {
        /* raced away or already gone */
      }
      if (Date.now() > deadline) throw new Error("catalog locked by another live writer");
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 50);
    }
  }
  try {
    return fn();
  } finally {
    try { fs.closeSync(fd); } catch { /* already closed */ }
    try {
      if (Number.parseInt(fs.readFileSync(lockPath, "utf8").trim(), 10) === process.pid) {
        fs.unlinkSync(lockPath);
      }
    } catch { /* gone */ }
  }
}

export function appendEvent(ev, input = null) {
  try {
    const file = eventsPath(input);
    // #3077: a repo with no library has no ledger to append to. Creating one on the first
    // denial would plant an orphan .household-library/ (plus its .catalog.lock) in a leaf
    // repo that no union-merge ever reaches. The denial itself stays loud on stderr; only
    // the ledger row is skipped, and the caller is told (returns false) so it can say so.
    // Env-overridden paths (tests, operator redirection) are always written.
    if (!process.env.HOUSEHOLD_BOOTSTRAP_EVENTS && !fs.existsSync(path.dirname(file))) return false;
    withLibraryLock(file, () => {
      const payload = sealIfChainStarted(
        {
          at: new Date().toISOString(),
          runtime: getRuntime(),
          repo: getRepoName(input),
          ...ev,
        },
        file,
      );
      fs.appendFileSync(file, JSON.stringify(payload) + "\n");
    });
    return true;
  } catch {
    /* ledger append is best-effort */
    return false;
  }
}

export function readStdinJson() {
  try {
    return JSON.parse(fs.readFileSync(0, "utf8"));
  } catch {
    return null;
  }
}

/** Layer path hit from a file path string. */
export function layerFromFilePath(fp) {
  const s = String(fp || "");
  for (const [key, suffix] of Object.entries(LAYER_SUFFIXES)) {
    if (s.endsWith(suffix)) return key;
  }
  // Also accept Grok home install copies of the front door.
  if (s.includes(`${path.sep}.grok${path.sep}skills${path.sep}sophos${path.sep}SKILL.md`)) {
    return "sophos";
  }
  if (s.includes(`${path.sep}.grok${path.sep}skills${path.sep}soli-deo-gloria${path.sep}`)) {
    return "soli-deo-gloria";
  }
  if (s.includes(`${path.sep}.grok${path.sep}skills${path.sep}careful-not-clever${path.sep}`)) {
    return "careful-not-clever";
  }
  if (s.includes(`${path.sep}.grok${path.sep}skills${path.sep}household-library${path.sep}`)) {
    return "household-library";
  }
  return null;
}
