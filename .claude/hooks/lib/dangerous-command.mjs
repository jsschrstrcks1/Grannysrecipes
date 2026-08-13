// A.B.O.R.T. destructive-command detector — the SINGLE SOURCE OF TRUTH for "this shell command could
// cause catastrophic, irreversible harm and must never run." Pure (no I/O), so every layer imports it:
// the Claude Code PreToolUse hook (.claude/hooks/dangerous-command-guard.js), the git pre-commit/pre-push
// hooks (.githooks/), and the CLI (cluster/scripts/scan-command.mjs).
//
// WHY THIS EXISTS: during a 2026-07-13 verification pass a sub-agent executed a command containing
// `<(ssh atlas rm -rf /)` to "prove" a guard bypass — it only failed to wipe a host because `atlas`
// didn't resolve. Never again. This blocks the class outright, INCLUDING danger hidden inside command
// substitution `$()`, process substitution `<()`/`>()`, backticks, `eval`, `sh -c`, `ssh <host> …`,
// `xargs`, and `find -exec` — the exact wrapping that slipped past the narrow preflight guard.
//
// DESIGN (careful, not clever): a real shell parser is where bypasses hide. Instead we match a small set
// of CATASTROPHIC patterns and only ever treat a dangerous verb as real when it sits at a COMMAND
// boundary (string start, after a separator/opener, or unwrapped by eval/xargs/-exec/sh -c/ssh/sudo) —
// so `grep "rm -rf /"` (danger inside a quoted arg) does not trip, but `a && rm -rf /`, `$(rm -rf ~)`,
// and `<(ssh h rm -rf /)` do. We bias toward BLOCKING: a false block is a minor annoyance; a false pass
// is a wiped disk. If you must reference these strings, put them in a file (Write), not a Bash command.

// A dangerous verb only counts at a command position: the start, after a shell separator/opener, or
// unwrapped by a command-runner. This is the crux that catches nested danger without a full parser.
// PREFIX COMMAND-RUNNERS: verbs that sit in front of the REAL command and run it, so a dangerous
// verb after them is still at a command position. `sudo`/`env`/`xargs`/`ssh` were covered; this
// adds the rest of the class — `command`/`builtin`/`exec` (bypass aliases & functions),
// `nohup`/`setsid`/`nice`/`ionice`/`stdbuf`/`time`/`timeout` (job wrappers people actually type).
// They optionally consume flags (`ionice -c3`) and bare numbers (`timeout 5`) before the verb.
// Found by spensa's 2026-07-15 adversarial pass: `nohup rm -rf /`, `exec rm -rf /`, `command rm
// -rf /`, `timeout 5 rm -rf /` all PASSED the "hardened" detector — the same sieve class C4 named.
//
// 4TH-ROUND ADDITIONS (Lift/Jasnah-lane hostile pass 2026-07-16): spensa's list ALSO missed the
// privilege/isolation runners `doas` (BSD sudo), `su -c` (universal), `runuser`, `watch`, `unshare`,
// `flock <lock>`, `chroot <dir>` — `su -c 'rm -rf /'` and `doas rm -rf /` both PASSED. That FOUR
// hostile rounds still leave common runners open is the whole argument for dangerous-command-deny-
// by-default: a prefix-runner allow-set is unwinnable by enumeration. These close the common ones;
// `flock`/`chroot` consume a bare arg before the verb; `su`/`runuser` carry the command after -c/--.
const PREFIX_RUNNERS = "\\b(?:command|builtin|exec|nohup|setsid|nice|ionice|stdbuf|time|timeout|watch|unshare)\\s+(?:-\\S+\\s+|\\d+\\s+)*";
const ARG_RUNNERS = "\\b(?:flock|chroot)\\s+(?:-\\S+\\s+)*\\S+\\s+";           // consume one bare arg (lockfile / newroot)
const BUSYBOX_RUNNER = "(?:[^\\s]*/)?busybox\\s+"; // applet name is the executed command
// PRIVILEGE RUNNERS take FLAG-VALUE pairs and a BARE arg (username / host) before the real command — which
// the old bare `\bsudo\s+`, one-token `\bssh\s+\S+\s+`, and `doas` in PREFIX_RUNNERS all missed, so
// `sudo -u root rm -rf /`, `ssh -i key host rm -rf /`, `su root -c 'rm -rf /'`, `doas -u root rm -rf /` ALL
// bypassed (vivenna 2026-07-20, re-attack of registered G-F1 — its "superseded" disposition did not hold).
// Consume the option block PRECISELY (value-flags with their arg first, then bare flags) and STOP at the
// command, so the verb after the runner is checked — but a dangerous verb INSIDE a quoted arg of a SAFE
// command (`sudo -u root grep "rm -rf /"`) is NOT reached (the command token is `grep`, not `rm`; the quoted
// `rm` sits at no boundary). Verified: closes the bypasses with zero over-block across the probe matrix.
const SUDO_RUNNER = "\\bsudo\\s+(?:-[aCghpRrtTUu]\\s+\\S+\\s+|--\\w[\\w-]*=\\S*\\s+|--\\w[\\w-]*\\s+|--\\s+|-[A-Za-z]+\\s+)*";
const DOAS_RUNNER = "\\bdoas\\s+(?:-[aCu]\\s+\\S+\\s+|--\\s+|-[A-Za-z]+\\s+)*";
const SSH_RUNNER = "\\bssh\\s+(?:-[bcDEeFIiJLlmOopQRSW]\\s+\\S+\\s+|-[A-Za-z]+\\s+)*\\S+\\s+";  // options (+their values) then the host token
const CMDSTR_RUNNERS = "\\b(?:sh|bash|zsh|dash|ksh|ash|hush)\\s+-[A-Za-z]*c\\s+|\\bsu\\s+(?:-\\s+|[\\w@.-]+\\s+)*-[A-Za-z]*c\\s+|\\brunuser\\b[^\\n;&|]*?--\\s+";  // `-c 'cmd'`, `su [user] -c 'cmd'`, `runuser … -- cmd`
// A bare `VAR=val command` env-prefix is a real shell command form (temp env var), so `X=1 rm -rf /` was
// catastrophic yet the boundary only recognized the literal `env VAR=val` (vivenna 2026-07-20, guard-env-prefix).
const BARE_ASSIGN = "(?:\\w+=\\S*\\s+)+";

// POSIX.1-2024 Shell Command Language, §§2.4, 2.7, 2.9, and 2.10:
// https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html
//
// BOUNDARY used to encode command position as a hand-written punctuation/runner regex. The published
// grammar also lets reserved words introduce commands, and lets redirections plus ASSIGNMENT_WORDs
// precede the command name. Consequently `then rm -rf /`, `2>/tmp/log rm -rf /`, and
// `X='a b' rm -rf /` were live false allows. Project those grammar positions to a private marker
// before destructive spelling normalization. This is a lexical projection, never an evaluator:
// quoted/escaped would-be reserved words remain ordinary command/argument text.
const POSIX_COMMAND_BOUNDARY = "\uE00B";
const SHELL_COMPLEXITY_MARKER = "\uE00C";
const POSIX_COMMAND_INTRODUCERS = new Set([
  "!", "if", "then", "else", "elif", "while", "until", "do",
]);
// Standalone grouping braces are already covered by BOUNDARY. Do not lex `{`/`}` here: the same
// bytes delimit `${parameter}` expansions, and inserting a marker inside one corrupts its semantics.
const POSIX_CONTROL_OPERATORS = [";;&", ";;", ";&", "&&", "||", "|&", ";", "&", "|", "(", ")"];
const POSIX_REDIRECTION = /^(?:[0-9]+)?(?:<<-|<<|>>|<>|<&|>&|>\||[<>])/;

function posixCommandTokens(input) {
  const source = String(input == null ? "" : input);
  const tokens = [];
  for (let i = 0; i < source.length;) {
    if (source[i] === "\n") { tokens.push({ type: "operator", value: "\n", start: i, end: ++i }); continue; }
    if (/[ \t\r]/.test(source[i])) { i++; continue; }

    // POSIX grouping braces are reserved words only when they are standalone tokens. `${x}` and
    // brace-expansion operands are ordinary word syntax and must never be split here.
    if ((source[i] === "{" || source[i] === "}")
        && (i === 0 || /[\s;&|()]/.test(source[i - 1]))
        && (i + 1 === source.length || /[\s;&|()]/.test(source[i + 1]))) {
      tokens.push({ type: "operator", value: source[i], start: i, end: i + 1 });
      i++;
      continue;
    }

    // A process substitution is one shell WORD (and may carry a literal suffix), not an outer
    // redirection. Its inner command is projected separately by projectCommandSubstitutions().
    const processSubstitution = (source[i] === "<" || source[i] === ">") && source[i + 1] === "(";
    const redirection = processSubstitution ? null : source.slice(i).match(POSIX_REDIRECTION);
    if (redirection) {
      tokens.push({ type: "redirection", value: redirection[0], start: i, end: i + redirection[0].length });
      i += redirection[0].length;
      continue;
    }
    const operator = POSIX_CONTROL_OPERATORS.find((op) => source.startsWith(op, i));
    if (operator) {
      tokens.push({ type: "operator", value: operator, start: i, end: i + operator.length });
      i += operator.length;
      continue;
    }

    const start = i;
    let quoted = false;
    while (i < source.length) {
      const c = source[i];
      // Expansions are part of the surrounding WORD even when their bodies contain spaces or shell
      // operators. Keep the outer word whole; executable substitution bodies are descended into by
      // projectCommandSubstitutions(), not mistaken for outer grammar.
      if ((c === "$" && (source[i + 1] === "(" || source[i + 1] === "{"))
          || ((c === "<" || c === ">") && source[i + 1] === "(")) {
        const close = source[i + 1] === "{" ? parameterExpansionClose(source, i + 1)
          : commandSubstitutionClose(source, i + 1);
        if (close > i) { i = close + 1; continue; }
      }
      if (/\s/.test(c) || /[<>&|;()]/.test(c)) break;
      if (c === "\\" && i + 1 < source.length) { quoted = true; i += 2; continue; }
      if (c === "'" || c === '"' || c === "`") {
        quoted = true;
        const q = c;
        i++;
        while (i < source.length) {
          if (q !== "'" && source[i] === "\\" && i + 1 < source.length) { i += 2; continue; }
          if (source[i++] === q) break;
        }
        continue;
      }
      i++;
    }
    if (i === start) { i++; continue; } // defensive progress on unknown syntax
    tokens.push({ type: "word", value: source.slice(start, i), quoted, start, end: i });
  }
  return tokens;
}

function projectPosixCommandPositions(input) {
  const source = String(input == null ? "" : input);
  const marks = [];
  let expectCommand = true;
  let redirectionResume = null;
  let redirectionNeedsProjection = false;
  let needsProjection = false;
  const caseStates = []; // each nested case: subject → await-in → patterns → body
  const caseState = () => caseStates.at(-1) || null;

  for (const token of posixCommandTokens(source)) {
    if (token.type === "operator") {
      redirectionResume = null;
      redirectionNeedsProjection = false;
      // POSIX case grammar: `)` opens a compound_list only after a case pattern. Other closing
      // parentheses (group/process/command substitution) stay closers. Case terminators return to
      // pattern mode; pattern `|`/optional `(` never earn command position.
      if (caseState() === "patterns") {
        if (token.value === ")") { caseStates[caseStates.length - 1] = "body"; expectCommand = true; }
        else expectCommand = false;
        needsProjection = false;
        continue;
      }
      if (caseState() === "body" && [";;", ";&", ";;&"].includes(token.value)) {
        caseStates[caseStates.length - 1] = "patterns";
        expectCommand = false;
        needsProjection = false;
        continue;
      }
      // Openers/separators start a command; closers end one. `<(`/`>(` open nested commands.
      expectCommand = token.value === "\n" || token.value === ";" || token.value === ";;"
        || token.value === ";&" || token.value === ";;&" || token.value === "&"
        || token.value === "|" || token.value === "|&" || token.value === "&&"
        || token.value === "||" || token.value === "(" || token.value === "{"
        || token.value === "<(" || token.value === ">(";
      // These positions were already encoded in BOUNDARY. Adding a marker here would sit between
      // `|`/`<(` and the next verb and break rules that match whole pipelines/substitutions.
      needsProjection = false;
      continue;
    }
    if (token.type === "redirection") {
      redirectionResume = expectCommand;
      redirectionNeedsProjection = expectCommand;
      continue;
    }
    if (redirectionResume !== null) {
      expectCommand = redirectionResume;
      if (redirectionNeedsProjection) needsProjection = true;
      redirectionResume = null;
      redirectionNeedsProjection = false;
      continue;
    }
    if (caseState() === "subject") { caseStates[caseStates.length - 1] = "await-in"; expectCommand = false; continue; }
    if (caseState() === "await-in") {
      if (!token.quoted && token.value === "in") caseStates[caseStates.length - 1] = "patterns";
      expectCommand = false;
      continue;
    }
    if (caseState() === "patterns") {
      if (!token.quoted && token.value === "esac") caseStates.pop();
      expectCommand = false;
      continue;
    }
    if (!expectCommand) continue;

    // POSIX ASSIGNMENT_WORD: the name before '=' is unquoted; its value may contain quoted spaces.
    if (/^[A-Za-z_][A-Za-z0-9_]*=/.test(token.value)) { needsProjection = true; continue; }
    if (!token.quoted && token.value === "case") { caseStates.push("subject"); expectCommand = false; continue; }
    if (!token.quoted && token.value === "esac" && caseState() === "body") {
      caseStates.pop();
      expectCommand = false;
      continue;
    }
    if (!token.quoted && POSIX_COMMAND_INTRODUCERS.has(token.value)) { needsProjection = true; continue; }

    if (needsProjection) marks.push(token.start);
    expectCommand = false;
    needsProjection = false;
  }

  if (!marks.length) return source;
  let out = "", cursor = 0;
  for (const at of marks) { out += source.slice(cursor, at) + POSIX_COMMAND_BOUNDARY; cursor = at; }
  return out + source.slice(cursor);
}
const BOUNDARY =
  "(?:^|" + POSIX_COMMAND_BOUNDARY + "|[\\n;&|(){}]|&&|\\|\\||\\$\\(|[<>]\\(|`|\\beval\\s+|\\bxargs\\s+(?:-\\S+\\s+)*|" + SUDO_RUNNER + "|" + DOAS_RUNNER + "|" + SSH_RUNNER + "|\\benv\\s+(?:-\\S+\\s+|\\w+=\\S*\\s+)*|" + BARE_ASSIGN + "|" + PREFIX_RUNNERS + "|" + ARG_RUNNERS + "|" + BUSYBOX_RUNNER + "|" + CMDSTR_RUNNERS + "|-exec\\s+)\\s*['\"]?\\s*";

const QUOTED_LITERAL_DOLLAR = "\uE000";
const QUOTED_LITERAL_BACKTICK = "\uE001";
const QUOTED_LITERAL_SINGLE = "\uE002";
const QUOTED_LITERAL_DOUBLE = "\uE003";
const PARAM_LITERAL_OPEN = "\uE004";
const PARAM_LITERAL_CLOSE = "\uE005";
const NESTED_BRACED_IFS = "\uE006";
const NESTED_PLAIN_IFS = "\uE007";
const QUOTED_BRACED_IFS = "\uE008";
const QUOTED_PLAIN_IFS = "\uE009";
const ANSI_LITERAL_BACKSLASH = "\uE00A";
const ANSI_SYNTAX_CHARS = [" ", "\t", "\n", ";", "&", "|", "(", ")"];
function markAnsiSyntax(str, base) {
  let out = String(str);
  for (let i = 0; i < ANSI_SYNTAX_CHARS.length; i++) {
    out = out.replaceAll(ANSI_SYNTAX_CHARS[i], String.fromCodePoint(base + i));
  }
  return out;
}
function restoreAnsiSyntax(str, base) {
  let out = String(str);
  for (let i = 0; i < ANSI_SYNTAX_CHARS.length; i++) {
    out = out.replaceAll(String.fromCodePoint(base + i), ANSI_SYNTAX_CHARS[i]);
  }
  return out;
}
const ANSI_INTERPRETED_BASE = 0xE010;
const ANSI_LITERAL_BASE = 0xE020;

// An outer shell removes backslash-newline before tokenization, including inside double quotes but
// not inside ordinary single quotes. Model that lexical join so `r\<newline>m` is still `rm` and a
// continued target still reaches `/`. This is also applied after projecting a quoted downstream
// command string, because that next interpreter performs the same removal at its own shell layer.
function stripShellLineContinuations(str) {
  const source = String(str == null ? "" : str);
  let out = "", quote = null;
  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    if (quote === "single") {
      out += c;
      if (c === "'") quote = null;
      continue;
    }
    if (c === "\\" && source[i + 1] === "\n" && quote !== "ansi") { i++; continue; }
    if (c === "\\" && i + 1 < source.length) { out += c + source[++i]; continue; }
    if (quote === "double") {
      out += c;
      if (c === '"') quote = null;
      continue;
    }
    if (quote === "ansi") {
      out += c;
      if (c === "'") quote = null;
      continue;
    }
    if (c === "$" && source[i + 1] === "'") { out += "$'"; i++; quote = "ansi"; continue; }
    if (c === "'") quote = "single";
    else if (c === '"') quote = "double";
    out += c;
  }
  return out;
}

// ANSI-C quoting: bash decodes `$'…'` escape sequences to BYTES before the command runs, so `rm -rf $'\x2f'`
// IS `rm -rf /` (\x2f=/), and `$'\057'` (octal), `$'/'` (unicode), `$'\x7e'` (=~) are real root/home
// wipes the target detector never saw — the raw `$'…'` token hid the root. Decode the escapes to their
// chars so canonicalization sees the real target. Must run BEFORE the backslash-escape strip below (that
// strip would eat the `\` in `\x2f` and destroy the sequence). Decode-only can REVEAL a hidden target,
// never hide one (safe for a scan-only detector). Non-hex/octal escapes (\n \t …) decode to their literal
// (harmless) char; an unrecognized escape is left as-is.
function decodeAnsiC(str, remainingDepth = String(str == null ? "" : str).length) {
  const source = String(str == null ? "" : str);
  const re = /\$'((?:\\[\s\S]|[^'\\])*)'/g;
  let out = "", cursor = 0, m;
  while ((m = re.exec(source))) {
    out += source.slice(cursor, m.index);
    const body = m[1];
    const decoded = body.replace(/\\(x[0-9a-fA-F]{1,2}|u[0-9a-fA-F]{1,4}|U[0-9a-fA-F]{1,8}|[0-7]{1,3}|[\s\S])/g, (m, esc) => {
      try {
        const c = esc[0];
        if (c === "x") return String.fromCharCode(parseInt(esc.slice(1), 16));
        if (c === "u" || c === "U") return String.fromCodePoint(parseInt(esc.slice(1), 16));
        if (/^[0-7]{1,3}$/.test(esc)) return String.fromCharCode(parseInt(esc, 8) & 0xff);
        const simple = { n: "\n", t: "\t", r: "\r", a: "\x07", b: "\b", f: "\f", v: "\v", e: "\x1b", "\\": "\\", "'": "'", '"': '"' };
        return Object.prototype.hasOwnProperty.call(simple, esc) ? simple[esc] : "\\" + esc;
      } catch { return m; }
    });
    // ANSI-C quotes suppress expansion in a direct operand, but a decoded argument to `sh -c`,
    // eval, ssh, su, or runuser becomes source for the next interpreter and expands there. Decode
    // left-to-right so a payload sees any ANSI-C-encoded runner spelling already present in `out`.
    // If that downstream source itself contains ANSI-C syntax, decode one more shell layer there:
    // `bash -c $'rm -rf $\'\\x2f\''` becomes downstream source `rm -rf $'\x2f'`, whose
    // target is `/`. Direct ANSI-C operands still decode exactly once. A source-length budget is a
    // simple termination proof: every recursive match removes at least the `$'…'` delimiters.
    const interpreted = singleQuoteFeedsInterpreter(out, out.length);
    if (interpreted) {
      const downstream = remainingDepth > 0 ? decodeAnsiC(decoded, remainingDepth - 1) : decoded;
      let projected = projectInterpretedSource(stripShellLineContinuations(downstream), remainingDepth - 1);
      // Expansion bytes cannot escape syntax that the OUTER shell parses after this ANSI segment.
      // Preserve a trailing decoded slash at a raw substitution boundary; internal slashes and
      // ANSI-to-ANSI concatenation remain downstream source and keep their syntax.
      if (/^(?:(?:""|'')|\$'')*\\*(?:`|\$\(|[<>]\()/.test(source.slice(re.lastIndex))) {
        projected = projected.replace(/\\+$/, (slashes) => ANSI_LITERAL_BACKSLASH.repeat(slashes.length));
      }
      out += markAnsiSyntax(projected, ANSI_INTERPRETED_BASE);
    } else {
      out += markAnsiSyntax(decoded, ANSI_LITERAL_BASE)
        .replaceAll("\\", ANSI_LITERAL_BACKSLASH)
        .replaceAll("$", QUOTED_LITERAL_DOLLAR)
        .replaceAll("`", QUOTED_LITERAL_BACKTICK)
        .replaceAll("'", QUOTED_LITERAL_SINGLE)
        .replaceAll('"', QUOTED_LITERAL_DOUBLE);
    }
    cursor = re.lastIndex;
  }
  return out + source.slice(cursor);
}

// Preserve `$` inside ordinary single-quoted shell segments before normalization joins adjacent
// quote segments. Without this lexical bit, `'$X'/$Y/` became `$X/$Y/`; the parameter reducer then
// erased BOTH names even though the first dollar is literal shell text. A private-use marker behaves
// as an ordinary filename character during scanning and is restored in any reported sample.
// Canonicalize shell WORD spelling for runner recognition. Quote delimiters disappear and adjacent
// segments join (`e'val'`, `bash -''c`), while whitespace/separators INSIDE quotes become inert
// placeholders so they cannot masquerade as outer syntax. This is not expansion or execution.
function runnerLexicalView(text) {
  let out = "";
  let quote = null;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quote === "single") {
      if (c === "'") { quote = null; continue; }
      out += /[\s;&|()]/.test(c) ? "_" : c;
      continue;
    }
    if (quote === "ansi") {
      if (c === "\\" && i + 1 < text.length) { out += text[++i]; continue; }
      if (c === "'") { quote = null; continue; }
      out += /[\s;&|()]/.test(c) ? "_" : c;
      continue;
    }
    if (quote === "double") {
      if (c === "\\" && i + 1 < text.length) { out += text[++i]; continue; }
      if (c === '"') { quote = null; continue; }
      out += /[\s;&|()]/.test(c) ? "_" : c;
      continue;
    }
    if (c === "\\" && i + 1 < text.length) { out += text[++i]; continue; }
    if (c === "$" && text[i + 1] === "'") { quote = "ansi"; i++; continue; }
    if (c === "'") { quote = "single"; continue; }
    if (c === '"') { quote = "double"; continue; }
    out += c;
  }
  return out;
}

function currentSimpleCommandSegment(view) {
  const source = String(view == null ? "" : view);
  let segmentStart = 0;
  for (let i = 0; i < source.length; i++) {
    // Standalone grouping braces are already projected to POSIX_COMMAND_BOUNDARY. Treating every
    // raw brace as a separator split ordinary argv words such as xargs' conventional `{}` token.
    if (source[i] === POSIX_COMMAND_BOUNDARY || /[\n;&|()]/.test(source[i])) segmentStart = i + 1;
  }
  return source.slice(segmentStart).trimStart();
}

function boundaryReachesSegmentEnd(view, tailSource) {
  const segment = currentSimpleCommandSegment(view);
  const match = new RegExp(`${BOUNDARY}${tailSource}$`, "i").exec(segment);
  return match?.index === 0;
}

function commandChainReachesEnd(view, expectedCommand) {
  const words = posixCommandTokens(currentSimpleCommandSegment(view))
    .filter((token) => token.type === "word")
    .map((token) => cookShellWord(token.value));
  const base = (word) => String(word || "").split("/").pop();
  const generic = new Set([
    "command", "builtin", "exec", "nohup", "setsid", "nice", "ionice", "stdbuf",
    "time", "timeout", "watch", "unshare", "xargs",
  ]);
  const sudoValue = /^-[aCDghpRrtTUu]$/;
  const doasValue = /^-[aCu]$/;
  const sudoLongValue = new Set([
    "--chdir", "--chroot", "--close-from", "--command-timeout", "--group", "--host", "--prompt",
    "--role", "--type", "--user",
  ]);
  const xargsValue = /^(?:-[adEILnPs]|--arg-file|--delimiter|--eof|--max-args|--max-chars|--max-lines|--max-procs|--replace)$/;
  const bundledXargsValue = /^-[^-].*[adEILnPs]$/;
  const bundledGenericValue = new Map([
    ["exec", /a/], ["nice", /n/], ["ionice", /[cnpPu]/], ["stdbuf", /[ioe]/],
    ["time", /[fo]/], ["timeout", /[ks]/], ["watch", /n/],
  ]);
  const genericValue = new Map([
    ["exec", new Set(["-a"])],
    ["nice", new Set(["-n", "--adjustment"])],
    ["ionice", new Set(["-c", "-n", "-p", "-P", "-u", "--class", "--classdata", "--pid", "--pgid", "--uid"])],
    ["stdbuf", new Set(["-i", "-o", "-e", "--input", "--output", "--error"])],
    ["time", new Set(["-f", "-o", "--format", "--output"])],
    ["timeout", new Set(["-k", "-s", "--kill-after", "--signal"])],
    ["watch", new Set(["-n", "--interval"])],
    ["unshare", new Set([
      "--map-user", "--map-group", "--map-users", "--map-groups", "-R", "--root", "-w", "--wd",
      "-S", "--setuid", "-G", "--setgid", "--owner", "--monotonic", "--boottime", "-l", "--propagation",
    ])],
  ]);

  let i = 0;
  for (let hops = 0; i < words.length && hops < words.length; hops++) {
    const command = base(words[i]);
    if (command === expectedCommand) return i === words.length - 1;

    if (command === "sudo" || command === "doas") {
      const valueFlag = command === "sudo" ? sudoValue : doasValue;
      i++;
      while (i < words.length && words[i].startsWith("-")) {
        if (words[i] === "--") { i++; break; }
        const bundledValue = command === "sudo" && /^-[^-]*[aCDghpRrtTUu]$/.test(words[i]);
        if (valueFlag.test(words[i]) || bundledValue || (command === "sudo" && sudoLongValue.has(words[i]))) i++;
        i++;
      }
      while (i < words.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i])) i++;
      continue;
    }
    if (command === "env") {
      i++;
      while (i < words.length) {
        if (words[i] === "--") { i++; break; }
        if (["-u", "--unset", "-C", "--chdir", "-a", "--argv0", "-S", "--split-string"].includes(words[i])) { i += 2; continue; }
        if (/^-[^-].*[uCaS]$/.test(words[i])) { i += 2; continue; }
        if (words[i].startsWith("-") || /^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i])) { i++; continue; }
        break;
      }
      continue;
    }
    if (generic.has(command)) {
      const valueFlags = command === "xargs" ? null : genericValue.get(command);
      i++;
      while (i < words.length) {
        if (words[i] === "--") { i++; break; }
        if (!words[i].startsWith("-") && !/^\d+(?:\.\d+)?[smhd]?$/.test(words[i])) break;
        const bundledValue = bundledGenericValue.get(command);
        const takesValue = command === "xargs"
          ? xargsValue.test(words[i]) || bundledXargsValue.test(words[i])
          : valueFlags?.has(words[i])
            || (bundledValue && /^-[^-].{1,}$/.test(words[i]) && bundledValue.test(words[i].at(-1)));
        i += takesValue ? 2 : 1;
      }
      continue;
    }
    if (command === "flock" || command === "chroot") {
      const valueFlags = command === "flock"
        ? new Set(["-w", "-E", "--wait", "--timeout", "--conflict-exit-code", "--start", "--length"])
        : new Set(["--userspec", "--groups"]);
      i++;
      while (i < words.length && words[i].startsWith("-")) {
        if (words[i] === "--") { i++; break; }
        const bundledValue = command === "flock" && /^-[^-].*[wE]$/.test(words[i]);
        i += valueFlags.has(words[i]) || bundledValue ? 2 : 1;
      }
      i++; // lockfile/new root
      continue;
    }
    if (command === "busybox") { i++; continue; }
    if (command === "runuser") {
      const separator = words.indexOf("--", i + 1);
      if (separator >= 0) { i = separator + 1; continue; }
      const valueFlags = new Set([
        "-u", "--user", "-g", "--group", "-G", "--supp-group", "-s", "--shell",
        "-w", "--whitelist-environment",
      ]);
      i++;
      while (i < words.length && words[i].startsWith("-")) i += valueFlags.has(words[i]) ? 2 : 1;
      continue;
    }
    if (command === "find") {
      const exec = words.findIndex((word, at) => at > i
        && ["-exec", "-execdir", "-ok", "-okdir"].includes(word));
      if (exec < 0) return false;
      i = exec + 1;
      continue;
    }
    return false;
  }
  return false;
}

// Reuse the detector's own runner sources, then keep their semantics for the correct lexical extent:
// `sh -c`/`su -c` consume one shell WORD (possibly many adjacent quote segments), while eval and ssh
// interpret all later arguments until an unquoted command boundary.
function singleQuoteFeedsInterpreter(source, offset) {
  const prefix = withoutShellRedirections(source.slice(0, offset));
  const view = runnerLexicalView(projectPosixCommandPositions(prefix));
  // Require the consumer itself to be reached by the command-boundary model. A bare substring
  // search made `echo sh -c '…'` and `printf %s eval '…'` look executable merely because their
  // inert argv happened to contain runner spellings.
  if (boundaryReachesSegmentEnd(view, CMDSTR_RUNNERS)) return true;
  if (boundaryReachesSegmentEnd(view, "\\beval\\s+[^\\n;&|()]*")) return true;
  if (boundaryReachesSegmentEnd(view, SSH_RUNNER + "[^\\n;&|()]*")) return true;
  return false;
}

function singleQuoteFeedsEmbeddedInterpreter(source, offset) {
  const prefix = withoutShellRedirections(source.slice(0, offset));
  const view = runnerLexicalView(projectPosixCommandPositions(prefix));
  return boundaryReachesSegmentEnd(
    view,
    "/?(?:[^\\s/]+/)*(?:ruby|python3?|perl|node|php|lua)\\b[^\\n;&|()]*"
      + "(?:-[ecr]|--eval|--command)\\s+",
  );
}

function removeAdjacentOuterEmptyQuotes(text) {
  let out = "", quote = null;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quote) {
      out += c;
      if (c === "\\" && quote === "double" && i + 1 < text.length) out += text[++i];
      else if ((quote === "single" && c === "'") || (quote === "double" && c === '"')) quote = null;
      continue;
    }
    const pair = text.slice(i, i + 2);
    if ((pair === "''" || pair === '""')
        && (/\S/.test(out.at(-1) || "") || /\S/.test(text[i + 2] || ""))) {
      i++;
      continue;
    }
    if (c === "'") quote = "single";
    else if (c === '"') quote = "double";
    out += c;
  }
  return out;
}

function maskSingleQuotedDollars(str, remainingDepth = String(str == null ? "" : str).length) {
  let out = "";
  for (let i = 0; i < str.length; i++) {
    const c = str[i];
    // Outside single quotes, backslash-quote is a literal quote character, not a segment boundary.
    if (c === "\\" && str[i + 1] === "'") {
      out += c + str[++i];
      continue;
    }
    if (c === "'") {
      const end = str.indexOf("'", i + 1);
      if (end < 0) { out += c; continue; }
      const interpreted = singleQuoteFeedsInterpreter(str, i);
      const embeddedInterpreter = !interpreted && singleQuoteFeedsEmbeddedInterpreter(str, i);
      const body = str.slice(i + 1, end);
      // Interpreted arguments are a scan projection of downstream SOURCE: remove the outer quote
      // delimiters so spaces and separators become syntax for that interpreter. Direct operands
      // retain their quotes and literal markers.
      let literalBody = body
        .replaceAll("$", QUOTED_LITERAL_DOLLAR)
        .replaceAll("`", QUOTED_LITERAL_BACKTICK);
      if (/^"+$/.test(body)) literalBody = literalBody.replaceAll('"', QUOTED_LITERAL_DOUBLE);
      const wordStart = Math.max(
        str.lastIndexOf(" ", i - 1), str.lastIndexOf("\t", i - 1), str.lastIndexOf("\n", i - 1),
        str.lastIndexOf(";", i - 1), str.lastIndexOf("&", i - 1), str.lastIndexOf("|", i - 1),
      ) + 1;
      const assignmentSegment = /^[A-Za-z_][A-Za-z0-9_]*=/.test(str.slice(wordStart, i));
      // Whitespace/operators inside an ordinary single-quoted argv word are data. Leave them
      // masked during rule matching so an unanchored runner spelling elsewhere in inert argv
      // cannot manufacture a boundary inside the quote (`echo flock -c 'if rm -rf / …'`).
      out += interpreted
        ? projectInterpretedSource(body, remainingDepth - 1)
        : "'" + (assignmentSegment || embeddedInterpreter
          ? literalBody
          : markAnsiSyntax(literalBody, ANSI_LITERAL_BASE)) + "'";
      i = end;
      continue;
    }
    if (c === '"') {
      let end = i + 1;
      for (; end < str.length; end++) {
        if (str[end] === "\\") { end++; continue; }
        if (str[end] === '"') break;
      }
      if (end >= str.length) { out += c; continue; }
      const interpreted = singleQuoteFeedsInterpreter(str, i);
      const body = str.slice(i + 1, end);
      const literalBody = /^'+$/.test(body) ? body.replaceAll("'", QUOTED_LITERAL_SINGLE) : body;
      out += interpreted ? projectInterpretedSource(body, remainingDepth - 1) : '"' + literalBody + '"';
      i = end;
      continue;
    }
    out += c;
  }
  return out;
}

function commandSubstitutionClose(source, openParen) {
  let depth = 1;
  let quote = null;
  for (let i = openParen + 1; i < source.length; i++) {
    const c = source[i];
    if (c === "\\" && quote !== "single" && i + 1 < source.length) { i++; continue; }
    if (quote === "single") { if (c === "'") quote = null; continue; }
    if (quote === "double") {
      if (c === '"') { quote = null; continue; }
      if (c === "$" && source[i + 1] === "(") { depth++; i++; }
      continue;
    }
    if (quote === "backtick") { if (c === "`") quote = null; continue; }
    if (c === "'") { quote = "single"; continue; }
    if (c === '"') { quote = "double"; continue; }
    if (c === "`") { quote = "backtick"; continue; }
    if (c === "$" && source[i + 1] === "(") { depth++; i++; continue; }
    if (c === "(") { depth++; continue; }
    if (c === ")" && --depth === 0) return i;
  }
  return -1;
}

function parameterExpansionClose(source, openBrace) {
  let depth = 1, quote = null;
  for (let i = openBrace + 1; i < source.length; i++) {
    const c = source[i];
    if (c === "\\" && quote !== "single" && i + 1 < source.length) { i++; continue; }
    if (quote === "single") { if (c === "'") quote = null; continue; }
    if (quote === "double") { if (c === '"') quote = null; continue; }
    if (c === "'") { quote = "single"; continue; }
    if (c === '"') { quote = "double"; continue; }
    if (c === "$" && source[i + 1] === "{") { depth++; i++; continue; }
    if (c === "}" && --depth === 0) return i;
  }
  return -1;
}

function backtickClose(source, open) {
  for (let i = open + 1; i < source.length; i++) {
    if (source[i] === "\\" && i + 1 < source.length) { i++; continue; }
    if (source[i] === "`") return i;
  }
  return -1;
}

// Command substitutions remain active inside double quotes and inside already-unwrapped interpreter
// source. Walk only those explicit execution seams; ordinary single-quoted text remains inert. Each
// recursive descent consumes a delimiter pair and decrements a source-length budget, so malformed or
// adversarial nesting cannot recurse forever.
function projectCommandSubstitutions(input, remainingDepth) {
  const source = String(input == null ? "" : input);
  if (remainingDepth <= 0) return source;
  let out = "", quote = null;
  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    if (c === "\\" && quote !== "single" && i + 1 < source.length) {
      out += c + source[++i];
      continue;
    }
    if (quote === "single") {
      out += c;
      if (c === "'") quote = null;
      continue;
    }
    if (c === "'" && quote !== "double") { quote = "single"; out += c; continue; }
    if (c === '"') { quote = quote === "double" ? null : "double"; out += c; continue; }

    if (c === "$" && source[i + 1] === "(" && source[i + 2] === "(") {
      const close = commandSubstitutionClose(source, i + 1);
      if (close > i) {
        // Arithmetic is data, but command substitutions inside it still execute.
        const body = source.slice(i + 3, close - 1);
        out += "$((" + projectCommandSubstitutions(body, remainingDepth - 1) + "))";
        i = close;
        continue;
      }
    }
    if (c === "$" && source[i + 1] === "(") {
      const close = commandSubstitutionClose(source, i + 1);
      if (close > i) {
        const body = source.slice(i + 2, close);
        out += "$(" + projectInterpretedSource(body, remainingDepth - 1) + ")";
        i = close;
        continue;
      }
    }
    if (quote === null && (c === "<" || c === ">") && source[i + 1] === "(") {
      const close = commandSubstitutionClose(source, i + 1);
      if (close > i) {
        const body = source.slice(i + 2, close);
        out += c + "(" + projectInterpretedSource(body, remainingDepth - 1) + ")";
        i = close;
        continue;
      }
    }
    if (c === "`") {
      const close = backtickClose(source, i);
      if (close > i) {
        const body = source.slice(i + 1, close);
        out += "`" + projectInterpretedSource(body, remainingDepth - 1) + "`";
        i = close;
        continue;
      }
    }
    out += c;
  }
  return out;
}

function projectInterpretedSource(input, remainingDepth) {
  const source = String(input == null ? "" : input);
  if (remainingDepth <= 0) return source;
  // The next shell parses ANSI-C quotes that were only literal bytes inside an outer double-quoted
  // source word (`sh -c "rm -rf $'\\x2f'"`). Decode at this interpreter layer before projecting its
  // command positions.
  const decoded = decodeAnsiC(source, remainingDepth - 1);
  const commandWords = projectCommandStringWords(decoded, remainingDepth - 1);
  const unwrapped = maskSingleQuotedDollars(commandWords, remainingDepth - 1);
  const nested = projectCommandSubstitutions(unwrapped, remainingDepth - 1);
  return projectPosixCommandPositions(nested);
}

function decodeAnsiWordBody(body) {
  return body.replace(/\\(x[0-9a-fA-F]{1,2}|u[0-9a-fA-F]{1,4}|U[0-9a-fA-F]{1,8}|[0-7]{1,3}|[\s\S])/g, (match, esc) => {
    try {
      if (esc[0] === "x") return String.fromCharCode(parseInt(esc.slice(1), 16));
      if (esc[0] === "u" || esc[0] === "U") return String.fromCodePoint(parseInt(esc.slice(1), 16));
      if (/^[0-7]{1,3}$/.test(esc)) return String.fromCharCode(parseInt(esc, 8) & 0xff);
      const simple = { n: "\n", t: "\t", r: "\r", a: "\x07", b: "\b", f: "\f", v: "\v", e: "\x1b", "\\": "\\", "'": "'", '"': '"' };
      return Object.prototype.hasOwnProperty.call(simple, esc) ? simple[esc] : "\\" + esc;
    } catch { return match; }
  });
}

// Cook one outer-shell WORD just far enough to recover the source string passed to `-c`/`eval`:
// adjacent quote segments join, quote delimiters disappear, and escaped bytes become literal. This
// does not expand variables or execute substitutions.
function cookShellWord(raw) {
  const source = String(raw == null ? "" : raw);
  let out = "", quote = null, ansi = "";
  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    if (quote === "single") { if (c === "'") quote = null; else out += c; continue; }
    if (quote === "double") {
      if (c === '"') { quote = null; continue; }
      if (c === "\\" && i + 1 < source.length) {
        // POSIX double quotes only remove backslash before $, `, ", \\, or newline. Before any
        // other byte it survives into the cooked WORD and may be syntax for a downstream shell.
        if (/[\\$`"\n]/.test(source[i + 1])) out += source[++i];
        else out += c;
        continue;
      }
      out += c;
      continue;
    }
    if (quote === "ansi") {
      if (c === "\\" && i + 1 < source.length) { ansi += c + source[++i]; continue; }
      if (c === "'") { out += decodeAnsiWordBody(ansi); ansi = ""; quote = null; continue; }
      ansi += c;
      continue;
    }
    if (c === "\\" && i + 1 < source.length) { out += source[++i]; continue; }
    if (c === "$" && source[i + 1] === "'") { quote = "ansi"; ansi = ""; i++; continue; }
    if (c === "'") { quote = "single"; continue; }
    if (c === '"') { quote = "double"; continue; }
    out += c;
  }
  if (quote === "ansi") out += "$'" + ansi; // malformed input stays visible, never invented
  return out;
}

function hasUnbalancedShellQuote(input) {
  const source = String(input == null ? "" : input);
  let quote = null;
  for (let i = 0; i < source.length; i++) {
    if (source[i] === "\\" && quote !== "single" && i + 1 < source.length) { i++; continue; }
    if (quote === "single") { if (source[i] === "'") quote = null; continue; }
    if (quote === "double") { if (source[i] === '"') quote = null; continue; }
    if (source[i] === "'") quote = "single";
    else if (source[i] === '"') quote = "double";
  }
  return quote !== null;
}

function commandWordsAfter(tokens, commandIndex) {
  const words = [];
  for (let i = commandIndex + 1; i < tokens.length; i++) {
    if (tokens[i].type === "operator") break;
    if (tokens[i].type === "redirection") {
      if (tokens[i + 1]?.type === "word") i++;
      continue;
    }
    if (tokens[i].type === "word") words.push(tokens[i]);
  }
  return words;
}

function sourceDescriptor(token, rawSource = token?.value) {
  return token ? { token, rawSource, cookedSource: cookShellWord(rawSource) } : null;
}

function accountCommandSourceToken(args, command) {
  const sourceFlags = new Set(["-c", "--command", "--session-command"]);
  const valueFlags = command === "runuser"
    ? new Set(["-u", "--user", "-g", "--group", "-G", "--supp-group", "-s", "--shell", "-w", "--whitelist-environment"])
    : new Set(["-g", "--group", "-s", "--shell"]);
  let positionalUserSeen = false;
  for (let i = 0; i < args.length; i++) {
    const arg = cookShellWord(args[i].value);
    if (arg === "--") break;
    if (sourceFlags.has(arg) || /^-[A-Za-z]*c[A-Za-z]*$/.test(arg)) return sourceDescriptor(args[i + 1]);
    const longAttached = /^(?:--command|--session-command)=(.*)$/s.exec(args[i].value);
    if (longAttached) return sourceDescriptor(args[i], longAttached[1]);
    const shortAttached = /^-c(.+)$/s.exec(args[i].value);
    if (shortAttached) return sourceDescriptor(args[i], shortAttached[1]);
    if (valueFlags.has(arg)) { i++; continue; }
    if (arg.startsWith("-")) continue;
    if (!positionalUserSeen) { positionalUserSeen = true; continue; }
    break; // the executed command/argv has begun; later `-c` text belongs to it
  }
  return null;
}

// A source consumer is executable only when its WORD is itself at a shell command boundary, or
// when one of the already-modelled command runners reaches it. Looking for every spelling of
// `sh -c`/`eval` anywhere in argv falsely interpreted inert data such as
// `printf %s sh -c 'rm -rf /'`. Build the prefix's lexical execution view, project the published
// POSIX command positions, remove redirections (which do not change argv), and require BOUNDARY to
// reach the candidate at the end of that view.
function sourceConsumerExecutes(input, token, command) {
  const prefix = String(input).slice(0, token.end);
  const projected = projectPosixCommandPositions(withoutShellRedirections(prefix));
  const lexical = runnerLexicalView(projected).replace(/[ \t]+/g, " ").trimEnd();
  return commandChainReachesEnd(lexical, command);
}

function projectConsumedSource(rawSource, cookedSource, remainingDepth) {
  const cookedActive = countActiveExecutionDelimiters(cookedSource);
  const outerActive = countActiveExecutionDelimiters(rawSource);
  const newlyActive = Math.max(0, cookedActive - outerActive);
  if (newlyActive > 128) {
    throw new RangeError("downstream shell execution structure exceeds review ceiling");
  }
  const interpreted = projectInterpretedSource(cookedSource, remainingDepth - 1);
  // Expansions in the OUTER source WORD execute before the downstream consumer starts. Keep a
  // second view of those seams: cooking the WORD can otherwise make an ANSI-C-produced backslash
  // appear to quote an adjacent raw backtick that the outer parser had already recognized.
  const outerExecutions = projectCommandSubstitutions(rawSource, remainingDepth - 1);
  // Recursive views can describe the same syntactic seam twice (once cooked for the downstream
  // shell, once raw for outer substitutions). Carry the larger subtree count, not their sum, then
  // collapse the private markers so each parent sees one command-wide subtotal.
  const nested = Math.max(complexityMarkerCount(interpreted), complexityMarkerCount(outerExecutions));
  const total = newlyActive + nested;
  if (total > 128) throw new RangeError("cumulative downstream shell execution structure exceeds review ceiling");
  return interpreted.replaceAll(SHELL_COMPLEXITY_MARKER, "") + "\n"
    + outerExecutions.replaceAll(SHELL_COMPLEXITY_MARKER, "") + "\n"
    + SHELL_COMPLEXITY_MARKER.repeat(total);
}

function projectCommandStringWords(input, remainingDepth) {
  const source = String(input == null ? "" : input);
  if (remainingDepth <= 0) return source;
  const tokens = posixCommandTokens(source);
  const replacements = [];
  const shells = new Set(["sh", "bash", "zsh", "dash", "ksh", "ash", "hush"]);

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.type !== "word") continue;
    const command = cookShellWord(token.value).split("/").pop();
    if (!shells.has(command) && !["eval", "ssh", "su", "env", "flock", "runuser"].includes(command)) continue;
    if (!sourceConsumerExecutes(source, token, command)) continue;
    const args = commandWordsAfter(tokens, i);

    if (shells.has(command)) {
      for (let j = 0; j < args.length; j++) {
        const arg = cookShellWord(args[j].value);
        if (!/^-[A-Za-z]*c[A-Za-z]*$/.test(arg)) continue;
        const sourceToken = args[j + 1];
        if (sourceToken) {
          const tailEnd = args.at(-1).end;
          const malformedTail = hasUnbalancedShellQuote(source.slice(sourceToken.end, tailEnd));
          const rawSource = malformedTail ? source.slice(sourceToken.start, tailEnd) : sourceToken.value;
          const cookedSource = malformedTail
            ? args.slice(j + 1).map((t) => cookShellWord(t.value)).join(" ")
            : cookShellWord(sourceToken.value);
          replacements.push({ start: token.start, end: malformedTail ? tailEnd : sourceToken.end,
            value: projectConsumedSource(rawSource, cookedSource, remainingDepth - 1) });
        }
        break;
      }
    } else if (command === "eval") {
      if (args.length) replacements.push({
        start: token.start,
        end: args.at(-1).end,
        value: projectConsumedSource(
          args.map((t) => t.value).join(" "),
          args.map((t) => cookShellWord(t.value)).join(" "),
          remainingDepth - 1,
        ),
      });
    } else if (command === "su" || command === "runuser") {
      const source = accountCommandSourceToken(args, command);
      if (source) replacements.push({
        start: token.start,
        end: source.token.end,
        value: projectConsumedSource(source.rawSource, source.cookedSource, remainingDepth - 1),
      });
    } else if (command === "ssh") {
      const optionNeedsValue = /^-[bBcDEeFIiJLlmOopQRSWw]$/;
      let host = -1;
      for (let j = 0; j < args.length; j++) {
        const arg = cookShellWord(args[j].value);
        if (arg === "--") { host = j + 1; break; }
        if (optionNeedsValue.test(arg)) { j++; continue; }
        if (arg.startsWith("-")) continue;
        host = j;
        break;
      }
      const remote = host >= 0 ? args.slice(host + 1) : [];
      if (remote.length) replacements.push({
        start: token.start,
        end: remote.at(-1).end,
        value: projectConsumedSource(
          remote.map((t) => t.value).join(" "),
          remote.map((t) => cookShellWord(t.value)).join(" "),
          remainingDepth - 1,
        ),
      });
    } else if (command === "env") {
      let interpreted = null;
      for (let j = 0; j < args.length; j++) {
        const arg = cookShellWord(args[j].value);
        if (/^(?:-S|--split-string)$/.test(arg)) { interpreted = sourceDescriptor(args[j + 1]); break; }
        const longAttached = /^--split-string=(.*)$/s.exec(args[j].value);
        if (longAttached) { interpreted = sourceDescriptor(args[j], longAttached[1]); break; }
        const shortAttached = /^-S(.+)$/s.exec(args[j].value);
        if (shortAttached) { interpreted = sourceDescriptor(args[j], shortAttached[1]); break; }
      }
      if (interpreted) replacements.push({
        start: token.start,
        end: interpreted.token.end,
        value: projectConsumedSource(interpreted.rawSource, interpreted.cookedSource, remainingDepth - 1),
      });
    } else if (command === "flock") {
      const valueFlags = new Set(["-w", "-E", "--wait", "--timeout", "--conflict-exit-code", "--start", "--length"]);
      let i = 0;
      while (i < args.length && cookShellWord(args[i].value).startsWith("-")) {
        const flag = cookShellWord(args[i].value);
        if (flag === "--") { i++; break; }
        i += valueFlags.has(flag) || /^-[^-].*[wE]$/.test(flag) ? 2 : 1;
      }
      i++; // lockfile / directory
      let interpreted = null;
      if (args[i] && /^(?:-c|--command)$/.test(cookShellWord(args[i].value))) {
        interpreted = sourceDescriptor(args[i + 1]);
      } else if (args[i]) {
        const longAttached = /^--command=(.*)$/s.exec(args[i].value);
        const shortAttached = /^-c(.+)$/s.exec(args[i].value);
        if (longAttached) interpreted = sourceDescriptor(args[i], longAttached[1]);
        else if (shortAttached) interpreted = sourceDescriptor(args[i], shortAttached[1]);
      }
      if (interpreted) replacements.push({
        start: token.start,
        end: interpreted.token.end,
        value: projectConsumedSource(interpreted.rawSource, interpreted.cookedSource, remainingDepth - 1),
      });
    }
  }
  let out = source;
  for (const replacement of replacements.sort((a, b) => b.start - a.start)) {
    out = out.slice(0, replacement.start) + replacement.value + out.slice(replacement.end);
  }
  return out;
}

function withoutShellRedirections(input) {
  const source = String(input == null ? "" : input);
  const tokens = posixCommandTokens(source);
  const ranges = [];
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].type !== "redirection") continue;
    const operand = tokens[i + 1]?.type === "word" ? tokens[++i] : null;
    ranges.push([tokens[i - (operand ? 1 : 0)].start, operand ? operand.end : tokens[i].end]);
  }
  let out = source;
  for (const [start, end] of ranges.sort((a, b) => b[0] - a[0])) out = out.slice(0, start) + " " + out.slice(end);
  return out.replace(/[ \t]+/g, " ");
}

// Count execution syntax with shell quoting/escaping, not a raw substring tally. Ordinary
// single-quoted text and escaped delimiters are inert; command substitutions remain active inside
// double quotes. A small explicit context stack keeps nested substitutions iterative and total.
function countActiveExecutionDelimiters(input, stopAfter = 128) {
  const source = String(input == null ? "" : input);
  const contexts = [{ quote: null, close: null }];
  let count = 0;
  for (let i = 0; i < source.length; i++) {
    const context = contexts.at(-1);
    const c = source[i];
    if (c === "\\" && context.quote !== "single" && i + 1 < source.length) { i++; continue; }
    if (context.quote === "single") { if (c === "'") context.quote = null; continue; }
    if (context.quote === "ansi") { if (c === "'") context.quote = null; continue; }
    if (context.quote === "double") {
      if (c === '"') { context.quote = null; continue; }
      if (c === "$" && source[i + 1] === "(") {
        if (++count > stopAfter) return count;
        contexts.push({ quote: null, close: ")" });
        i++;
        continue;
      }
      if (c === "`") { if (++count > stopAfter) return count; }
      continue;
    }
    if (c === "$" && source[i + 1] === "'") { context.quote = "ansi"; i++; continue; }
    if (c === "'") { context.quote = "single"; continue; }
    if (c === '"') { context.quote = "double"; continue; }
    if (c === "$" && source[i + 1] === "(") {
      if (++count > stopAfter) return count;
      contexts.push({ quote: null, close: ")" });
      i++;
      continue;
    }
    if ((c === "<" || c === ">") && source[i + 1] === "(") {
      if (++count > stopAfter) return count;
      contexts.push({ quote: null, close: ")" });
      i++;
      continue;
    }
    if (c === "`") { if (++count > stopAfter) return count; continue; }
    if (c === ")" && context.close === ")" && contexts.length > 1) contexts.pop();
  }
  return count;
}

function complexityMarkerCount(input) {
  let count = 0;
  for (const c of String(input == null ? "" : input)) if (c === SHELL_COMPLEXITY_MARKER) count++;
  return count;
}

function restoreSingleQuotedDollars(str) {
  return restoreAnsiSyntax(String(str == null ? "" : str), ANSI_LITERAL_BASE)
    .replaceAll(POSIX_COMMAND_BOUNDARY, "")
    .replaceAll(SHELL_COMPLEXITY_MARKER, "")
    .replaceAll(QUOTED_LITERAL_DOLLAR, "$")
    .replaceAll(QUOTED_LITERAL_BACKTICK, "`")
    .replaceAll(QUOTED_LITERAL_SINGLE, "'")
    .replaceAll(QUOTED_LITERAL_DOUBLE, '"')
    .replaceAll(PARAM_LITERAL_OPEN, "(")
    .replaceAll(PARAM_LITERAL_CLOSE, ")")
    .replaceAll(QUOTED_BRACED_IFS, "${IFS}")
    .replaceAll(QUOTED_PLAIN_IFS, "$IFS")
    .replaceAll(ANSI_LITERAL_BACKSLASH, "\\");
}

// Rule matchers use `)` as a shell-command boundary. A LEADING Zsh parameter flag group
// (`${(U)foo}`) is instead part of one operand. Mask only that group: parentheses later in the
// expression may be live `$()` command substitution and must remain visible to the deny rule.
function maskParameterParens(str) {
  const source = String(str == null ? "" : str);
  let out = "";
  for (let i = 0; i < source.length; i++) {
    if (source[i] !== "$" || source[i + 1] !== "{" || source[i + 2] !== "(") {
      out += source[i];
      continue;
    }
    out += "${" + PARAM_LITERAL_OPEN;
    i += 2;
    let groupDepth = 1;
    while (i + 1 < source.length && groupDepth > 0) {
      i++;
      if (source[i] === "(") { groupDepth++; out += PARAM_LITERAL_OPEN; }
      else if (source[i] === ")") { groupDepth--; out += PARAM_LITERAL_CLOSE; }
      else out += source[i];
    }
  }
  return out;
}

// Standalone IFS expansion is a shell word separator (`rm${IFS}-rf`), but IFS inside another
// parameter expression is first part of that expression's selected word. Preserve the nested form
// until branch reduction; otherwise early whitespace replacement splits/truncates the operand and
// hides `${A:-${IFS}}/` -> `/`.
function maskNestedIfs(str) {
  const source = String(str == null ? "" : str);
  let out = "", depth = 0, quote = null;
  for (let i = 0; i < source.length; i++) {
    if (quote === null && source[i] === "\\" && i + 1 < source.length) {
      out += source[i] + source[++i];
      continue;
    }
    if (quote === "single") {
      out += source[i];
      if (source[i] === "'") quote = null;
      continue;
    }
    if (quote === "double" && source[i] === "\\" && i + 1 < source.length) {
      out += source[i] + source[++i];
      continue;
    }
    if (source[i] === "'" && quote !== "double") { quote = "single"; out += source[i]; continue; }
    if (source[i] === '"') { quote = quote ? null : "double"; out += source[i]; continue; }
    if (quote === "double" && source.startsWith("${IFS}", i)) {
      out += QUOTED_BRACED_IFS;
      i += 5;
      continue;
    }
    if (quote === "double" && source.startsWith("$IFS", i)) {
      out += QUOTED_PLAIN_IFS;
      i += 3;
      continue;
    }
    if (depth > 0 && source.startsWith("${IFS}", i)) {
      out += NESTED_BRACED_IFS;
      i += 5;
      continue;
    }
    if (depth > 0 && source.startsWith("$IFS", i)) {
      out += NESTED_PLAIN_IFS;
      i += 3;
      continue;
    }
    if (source[i] === "$" && source[i + 1] === "{") {
      out += "${";
      i++;
      depth++;
      continue;
    }
    if (depth > 0 && source[i] === "{") depth++;
    if (depth > 0 && source[i] === "}") depth--;
    out += source[i];
  }
  return out;
}

// Backslash parity decides whether an old-style backtick delimiter is active. Odd runs quote the
// backtick; even runs leave it active after shell escape processing. Remove the even run entirely
// for scan projection (conservative across the backtick parser's second escape layer), and mark an
// odd-run backtick literal so BOUNDARY cannot treat it as command substitution.
function canonicalizeBacktickEscapes(str) {
  const source = String(str);
  let out = "", inLegacy = false;
  for (let i = 0; i < source.length; i++) {
    if (source[i] !== "\\") {
      out += source[i];
      if (source[i] === "`") inLegacy = !inLegacy;
      continue;
    }
    let end = i;
    while (source[end] === "\\") end++;
    if (source[end] !== "`") { out += source.slice(i, end); i = end - 1; continue; }
    const count = end - i;
    if (count % 2 === 0) {
      out += "`";
      inLegacy = !inLegacy;
    } else if (inLegacy) {
      // `\`` inside an active old-style substitution is the delimiter of a nested substitution.
      out += "`";
    } else {
      out += QUOTED_LITERAL_BACKTICK;
    }
    i = end;
  }
  return out;
}

function canonicalizeRunnerTokens(text) {
  const shells = new Set(["sh", "bash", "zsh", "dash", "ksh", "ash", "hush", "su", "runuser", "ssh", "eval"]);
  return text.replace(/\S+/g, (token) => {
    // The POSIX projection marker carries position, not spelling. Keep it on the returned token but
    // remove it while recognizing quote-joined runners (`e'val'`, `b'as'h`) or it becomes part of
    // the basename and disables the pre-existing downstream-source projection.
    const marker = token.startsWith(POSIX_COMMAND_BOUNDARY) ? POSIX_COMMAND_BOUNDARY : "";
    const view = runnerLexicalView(marker ? token.slice(marker.length) : token);
    const base = view.split("/").pop();
    if (shells.has(base) || /^-[A-Za-z]*c$/.test(view)) return marker + view;
    return token;
  });
}

function normalize(raw) {
  // The shell expands ${IFS}/$IFS to whitespace (the classic word-split obfuscation that turns
  // `rm${IFS}-rf${IFS}/` into `rm -rf /`), so we treat those tokens as whitespace BEFORE matching —
  // otherwise a dangerous verb hides behind ${IFS} at what looks like a non-boundary position.
  // Backslashes before a letter are shell alias-escapes (`\rm` runs the real `rm`, skipping any alias);
  // drop the WHOLE run so the verb canonicalizes to `rm` no matter how many are stacked. A single
  // `\\(?=letter)` stripped only ONE per position in one pass, so `\\rm` / `\\\rm` survived as `\rm`
  // and slipped past the command-boundary check (audit C4 — reproduced). `\\+` strips the full run.
  // Stripping escapes can only REVEAL a hidden verb, never hide one — safe for a scan-only detector.
  //
  // RESIDUAL LIMIT (a static regex cannot canonicalize this — documented, not silently ignored):
  //   • variable indirection: `X=rm; $X -rf /` — resolving $X needs a live shell. Out of reach for
  //     pattern matching; the audit-C4 recommendation is a deny-by-default redesign (own follow-up
  //     task). Write-then-run (`bash ./script.sh` where the unseen script holds the danger) is the
  //     same class. These are why the guard is defense-in-depth behind the agent's P0 posture + human
  //     review, not a sandbox — truly untrusted execution needs OS-level isolation, not regex.
  const outerSource = stripShellLineContinuations(String(raw == null ? "" : raw));
  const commandWords = projectCommandStringWords(outerSource, Math.min(64, outerSource.length));
  const maskedSource = maskSingleQuotedDollars(maskParameterParens(decodeAnsiC(commandWords)));
  const projectedSource = projectPosixCommandPositions(
    projectCommandSubstitutions(maskedSource, outerSource.length),
  );
  let s = restoreAnsiSyntax(
    maskNestedIfs(canonicalizeBacktickEscapes(stripShellLineContinuations(projectedSource))),
    ANSI_INTERPRETED_BASE,
  )
    // $'\x2f'→/ etc. before masking/backslash stripping; ordinary single-quoted dollars stay literal.
    .replace(/\$\{IFS\}|\$IFS\b/g, " ")
    .replaceAll(NESTED_BRACED_IFS, "${IFS}")
    .replaceAll(NESTED_PLAIN_IFS, "$IFS")
    // Strip shell-escape backslash runs before a verb OR a target char. A run before a LETTER
    // canonicalizes the verb (`\rm`→`rm`); a run before a target char (`/ ~ $ . *` and digits)
    // canonicalizes the OPERAND — `rm -rf \/`, `\~`, `\$HOME`, `/\*` are real root/home wipes the
    // shell un-escapes, and stripping only-before-letters left that whole family open (found by
    // the 2026-07-15 hostile pass; the original C4 fix closed the verb side only).
    .replace(/\\+(?=[A-Za-z0-9/~.$*])/g, "")
    // Unescape quote chars so mid-verb splits written as r\"m\" (e.g. inside bash -c "…") still
    // rejoin. Scan-only: can only REVEAL a hidden verb, never hide one.
    .replace(/\\(['"])/g, "$1");
  // Empty OUTER quote segments contribute zero characters when adjacent inside a shell word.
  // Opposite quote characters inside a quoted filename (`"''"/`, `'""'/`) remain literal.
  s = removeAdjacentOuterEmptyQuotes(s);
  // Context recognition already uses quote-joined runner spelling. Apply the same canonical spelling
  // to runner/option TOKENS before BOUNDARY matching, without dequoting arbitrary operands.
  s = canonicalizeRunnerTokens(s);
  // In-word quotes join in the real shell (`r"m"` → `rm`, `r'm' -rf /` → `rm -rf /`). BOUNDARY
  // only allows one optional quote *around* a verb, so mid-verb quotes passed unblocked
  // (guard-quote-split-verb / vivenna 2026-07-20). Strip only quotes *between* word chars —
  // never outer quoting of whole args (`rm -rf "/"` stays a quoted catastrophic target).
  // Loop until stable so stacked splits (`r"m""x`) collapse.
  // The boundary classes are NON-SPACE, not word-char. Requiring [A-Za-z0-9_] on the left made the
  // rule positional: `r"m"` joined (both sides word chars) but `-"r"f` did NOT, because `-` is not a
  // word char — so the identical evasion one word to the right survived. The inconsistency was
  // visible from inside the family: `rm -r"f" /` blocked while `rm -"r"f /` did not, and both remove
  // quotes to the same catastrophic command in a real shell (found by adversarial verification of
  // the encoding family, 2026-08-08). Excluding quotes themselves from both sides keeps OUTER
  // quoting of a whole argument intact — `rm -rf "/"` still reads as a quoted catastrophic target,
  // and a quote with whitespace on either side is a word boundary, never an in-word split.
  for (let i = 0; i < 8; i++) {
    const n = s.replace(/([^\s'"])['"]+(?=[^\s'"])/g, "$1");
    if (n === s) break;
    s = n;
  }
  const normalized = s.replace(/[ \t]+/g, " ");
  const withoutRedirections = withoutShellRedirections(normalized);
  return withoutRedirections === normalized ? normalized : normalized + "\n" + withoutRedirections;
}

// Collapse a path to its canonical form so the many SPELLINGS of the filesystem root all reduce to
// "/": `//`, `/.`, `/./`, `/..`, `/../`, `/.//`. A blocklist that enumerates root literally misses
// these (hostile pass 2026-07-15 reproduced `rm -rf //` and `rm -rf /.` as PASSes). Absolute paths
// resolve `.`/`..` segments; a leading-slash path that empties out IS root. Non-absolute inputs are
// returned trimmed of duplicate slashes only (cwd-relative canonicalization would over-reach).
function canonicalizePath(p) {
  if (!p.startsWith("/")) return p.replace(/\/{2,}/g, "/");
  const segs = [];
  for (const s of p.split("/")) {
    if (s === "" || s === ".") continue;
    if (s === "..") { segs.pop(); continue; }   // parent-of-root is still root
    segs.push(s);
  }
  return "/" + segs.join("/");
}

// Does this single path SEGMENT glob match every entry of its directory — i.e. carry no literal
// character that constrains the match? (UL-344.)
//
// Under ROOT any glob at all is catastrophic, because every top-level entry is a system directory,
// and the `/[^/]*[*?\[]` rule below says exactly that. Under HOME that reasoning does NOT transfer:
// `~/build*` deletes two project directories and is ordinary work. Mirroring the root rule onto
// home would over-block it, and an over-blocking guard gets switched off — its own P0.
//
// The distinguishing property is not "contains a glob" but "is UNCONSTRAINED": remove the glob
// metacharacters, the leading dot, and a leading negated-dot class, and ask whether any literal
// name character survives. `.*` `.??*` `.[!.]*` `?*` `*` leave nothing, so they match the whole
// directory (and `.*` additionally matches `..`, i.e. the PARENT). `build*` leaves "build" and
// `.cache*` leaves "cache", so both stay allowed.
// Any bracket EXPRESSION is stripped, not just the negated-dot class. A character class is a
// wildcard over its members, not a literal constraint: `.[a-z]*` matches `.ssh`, `.gnupg`, `.aws`,
// `.config` — practically the whole dotfile set — so treating `a-z` as surviving "literal name
// characters" left it ALLOWED. Measured 2026-08-11 after landing this rule: `~/.[a-z]*`,
// `~/.[A-Za-z]*`, `~/.[a-zA-Z0-9]*`, `/root/.[a-z]*` and `/home/<u>/.[a-z]*` all walked through,
// while the `[!.]` and `[^.]` spellings of the same sweep were correctly refused.
// A class alongside real literals still constrains: `.[a-z]ache` keeps "ache" and stays allowed.
function isUnconstrainedGlobSegment(seg) {
  if (!/[*?]/.test(seg)) return false;                    // not a glob at all
  return seg.replace(/\[[^\]]*\]/g, "").replace(/[.*?]/g, "") === "";
}

// Is an `rm` operand a whole-filesystem / home / cwd / system-root wipe (vs a specific safe subdir)?
function isCatastrophicTarget(tok) {
  const t = tok.trim();
  // Strip EVERY quote character, not just one surrounding pair. The old `^['"]|['"]$` stripped a
  // single leading and a single trailing quote, so `"/"` collapsed to `/` and blocked — but an
  // EMPTY quote pair adjacent to the target did not: `""/` kept a stray quote (`"/`), matched no
  // literal, and reached rm as `/`. The shell drops `""` entirely during word expansion, so all six
  // of `""/`  `/''`  `""$HOME`  `""~`  `''/*`  `/""` were live root/home wipes that this function
  // declared safe. Found by the generated fault-injection battery (guard-fault-injection-discipline),
  // not by hand — the hand-written corpus had `"/"` and stopped there.
  //
  // Same reasoning as isUnprovableRecursiveTarget below: a shell quote cannot make a catastrophic
  // target safe. Over-block risk is nil — a real filename containing a quote de-quotes to a
  // non-catastrophic name and still passes.
  const rawBare = t.replace(/['"]/g, "");
  // Canonicalize absolute paths so every root spelling (// /. /./ /.. …) collapses to "/" before the
  // literal/system-root checks below. Non-absolute forms (~, $HOME, ., *) keep their original shape.
  const bare = rawBare.startsWith("/") ? canonicalizePath(rawBare) : rawBare;
  const noSlash = bare.replace(/\/+$/, "") || "/";      // drop trailing slashes; keep bare "/"
  const LITERAL = new Set(["/", "~", "$HOME", "${HOME}", ".", "..", "*"]);
  if (LITERAL.has(bare)) return true;
  if (/^\/\*+$/.test(bare)) return true;                // /*  /**
  // Any glob metachar (* ? [) in the FIRST path segment under root — `/[a-z]*`, `/.*`, `/b*`, `/?*`,
  // `/etc*`, `/*/x` — makes the shell iterate the TOP-LEVEL entries (`/bin /etc /usr …` all match), i.e.
  // a whole-root wipe exactly like `/*`. The pure-star rule above only caught a bare `*` segment; a glob
  // carrying any literal or char-class slipped straight through (live root-wipe bypass, inert-probed
  // 2026-07-24). A DEEPER-scoped glob keeps a LITERAL first segment (`/tmp/build*`, `/var/log/*.gz`,
  // `/opt/x-*`) and correctly passes — the metachar must sit in the segment DIRECTLY under root.
  if (/^\/[^/]*[*?\[]/.test(bare)) return true;         // /[a-z]*  /.*  /b*  /?*  /etc*  /*/x
  if (/^~\/?\*?$/.test(bare)) return true;              // ~  ~/  ~/*
  // (The home first-segment DOTGLOB rule lives below, at the tilde-user block — UL-344, navani.
  // An earlier, BROADER rule here — any glob metachar in the first segment under ~ — was removed:
  // it over-blocked leading-literal targets like `~/build*` and `~/*.bak`, which name real work,
  // and a P0 pre-commit guard that refuses ordinary cleanup gets disabled. The catastrophic signal
  // is specifically the DOTGLOB, which sweeps the hidden credential dirs; see the dot-only rule below.)
  // TILDE-USER / dir-stack tilde — `~root`, `~ken` (another user's WHOLE home), `~-` (OLDPWD), `~+` (PWD,
  // = a cwd wipe like `.`), `~1` (dirstack). The `~` rule above only caught the bare/own-home tilde; a
  // username or ± after it expands to a home/dynamic directory and slips through (`rm -rf ~root` wipes
  // root's home exactly as thoroughly as `rm -rf ~`). A trailing SUBDIR (`~ken/project`) is a targeted
  // delete and still passes — the char-run must be the WHOLE operand (optionally `/` or `/*`), never `/leaf`.
  if (/^~[A-Za-z0-9_+-]+\/?\*?$/.test(bare)) return true;   // ~root ~ken ~- ~+ ~1  (+ ~user/ ~user/*)
  // (A tilde-anchored dot-glob rule lived here from #2934 and has been REMOVED as superseded. It
  // matched only the `~`-spelled forms, so every absolute spelling of the identical target —
  // `/root/.*`, `/home/<u>/.*`, `/Users/<u>/.*` — walked straight through it. The
  // unconstrained-glob-segment rule below covers every shape it covered and those as well. Two
  // overlapping rules for one concept is how a later reader deletes the wrong one.)
  if (/^\$\{?HOME\}?\/?\*?$/.test(bare)) return true;   // $HOME  ${HOME}  $HOME/  $HOME/*
  // HOME DOTGLOB — `~/.*` was ALLOWED while `~/*` was blocked (measured on main 2026-08-11, P0
  // #2924, found validating #2908). The tell was a spelling split: `$HOME/.*` blocked — but only
  // incidentally, via the unprovable-variable-glob rule below — while the tilde form of the same
  // target walked through, because the tilde rules above only ever covered `~`, `~/` and `~/*`.
  // The concept was already understood elsewhere; this was a missing ALIAS, not a missing idea.
  // Severity is above "loses your dotfiles": in bash `~/.*` expands to include `~/..`, the PARENT
  // of home, so the blast radius leaves the user entirely.
  // Anchors are every spelling of a whole home: `~`, `~user`/`~+`/`~-`, `$HOME`/`${HOME}`, and the
  // literal `/home/<u>` `/Users/<u>` forms the single-segment rule below already treats as homes.
  // The operand must END here: `~/.*/cache` is a targeted delete under each dotdir, not a home wipe.
  {
    const m = bare.match(
      /^(?:~[A-Za-z0-9_+-]*|\$\{?HOME\}?|\/(?:home|Users)\/[^/*?\[]+)\/([^/]+)\/?$/,
    );
    if (m && isUnconstrainedGlobSegment(m[1])) return true;   // ~/.*  ~/.??*  ~/.[!.]*  ~/?*  ~root/.*
  }
  if (/^\.\/?\*?$/.test(bare)) return true;             // .  ./  ./*   (cwd wipe)
  // PARENT-CLIMB THROUGH HOME — `~/../..`, `$HOME/../../..`, `${HOME}/..` (Lift hostile pass
  // 2026-07-16, a live P0 bypass). These are NEITHER absolute (canonicalizePath never touches
  // them) NOR pure-relative (the `../..` rule above requires the WHOLE target be dots), so both
  // prior fixes missed them — yet the shell expands them to a home ANCESTOR: `~/..` → /home or
  // /Users (a system root), `~/../..` → /. The rule is depth-independent: there is no legitimate
  // `rm -rf` target reached by climbing AT OR ABOVE your home directory (home's only ancestors
  // are the system roots and /). Strip the home prefix and simulate the remainder from home-root
  // depth 0; if any `..` pops to or below 0, the target lands on home itself or an ancestor.
  {
    const homePrefix = /^(?:~|\$\{?HOME\}?)(?:\/|$)/;
    if (homePrefix.test(bare) && /\.\./.test(bare)) {
      const remainder = bare.replace(/^(?:~|\$\{?HOME\}?)/, "").replace(/\*$/, "");
      let depth = 0, minDepth = 0;
      for (const s of remainder.split("/")) {
        if (s === "" || s === ".") continue;
        depth += (s === "..") ? -1 : 1;
        if (depth < minDepth) minDepth = depth;
      }
      // Block if it ever climbs strictly ABOVE home (minDepth < 0 — an ancestor of home),
      // or NET-resolves to home itself (final depth <= 0). A transient dip to home-root that
      // then descends back INTO home (`~/a/../b` → depth 1,0,1) is a real in-home target and
      // must still pass — so this checks net/min, never a transient touch of 0.
      if (minDepth < 0 || depth <= 0) return true;
    }
  }
  // A target that is NOTHING but traversal segments — `../..`, `../../*`, `.././../../` — resolves to a
  // pure ANCESTOR of cwd, and a recursive force-delete of a bare ancestor is never legitimate (a real
  // sibling target NAMES a dir: `../dist`, `../repo/build`). canonicalizePath is absolute-only by
  // design, so the sibling hostile-pass that closed absolute root spellings left this relative
  // parent-climb open — `rm -rf ../../../../../..` reaches / from any depth (spensa cross-review
  // 2026-07-16). Requires a `..` so this never double-covers the `.`/`./` cwd case just above.
  if (/\.\./.test(bare) && /^(?:\.{1,2}\/?)+\*?$/.test(bare)) return true;
  // MIXED traversal that RESOLVES to cwd or a bare ancestor — `x/../../../../..`, `foo/..`,
  // `a/b/../../../..`. A named segment cancelled by a following `..` that then keeps climbing lands
  // on cwd or an ANCESTOR of cwd exactly as pure `../..` does — but the pure-traversal rule just
  // above (whole target must be dots) passes it, because a real name appears first (jasnah hostile
  // pass 2026-07-16, finding 7). Canonicalize the RELATIVE path against a symbolic cwd: a `..` pops a
  // standing named segment, else records a climb above cwd. If NO named segment survives, the target
  // is cwd itself (empty, no leaf) or a bare ancestor (only climbs) — the same catastrophic class.
  // A surviving name (`src/../dist` → dist, `../build` → build) is a real target and passes.
  // Relative-only: absolute paths are canonicalizePath'd into the SYS/LITERAL checks, and a
  // home-prefixed climb was already caught by the parent-climb-through-home block above.
  if (!bare.startsWith("/") && !/^(?:~|\$)/.test(bare) && /\.\./.test(bare)) {
    const stack = [];
    for (const s of bare.replace(/\*$/, "").split("/")) {
      if (s === "" || s === ".") continue;
      if (s === "..") { if (stack.length) stack.pop(); /* else: climb above cwd */ }
      else stack.push(s);
    }
    if (stack.length === 0) return true;   // resolves to cwd or an ancestor of cwd — no named leaf
  }
  // A SINGLE segment under /home or /Users is an entire user home directory (e.g. /home/user — this
  // container's $HOME, /Users/kenbaker — the operator's Mac home). Wiping it is catastrophic even
  // though the literal path isn't `~`/`$HOME`. Two+ segments (/home/user/project) is a subdir → safe.
  if (/^\/(?:home|Users)\/[^/*]+\/?\*?$/.test(bare)) return true;
  const SYS = ["/bin", "/sbin", "/usr", "/etc", "/var", "/lib", "/lib64", "/boot", "/dev", "/proc",
    "/sys", "/root", "/opt", "/System", "/Library", "/Applications", "/Users", "/private", "/Volumes",
    "/cores", "/home", "/srv", "/nix", "/mnt", "/media",
    // macOS: /var is a symlink into /private/var — wiping either is catastrophic
    "/private/var", "/private/etc", "/private/tmp"];
  if (SYS.includes(noSlash)) return true;               // exactly a system root (not a subdir under it)
  if (SYS.some((d) => bare === d + "/*")) return true;  // /usr/*  etc.
  // The same unconstrained-glob concept under a system root: `/root/.*` was ALLOWED (P0 #2924)
  // while `/root/*` was blocked by the line above. `/root` is a home like any other, and `/etc/.*`
  // is the same shape. A CONSTRAINED glob (`/var/log*`, `/etc/nginx*`) is a targeted delete and
  // still passes — only a segment with no literal character left is a whole-directory wipe.
  {
    const m = bare.match(/^(\/[^/]+(?:\/[^/]+)?)\/([^/]+)\/?$/);
    if (m && SYS.includes(m[1]) && isUnconstrainedGlobSegment(m[2])) return true;
  }
  return false;
}

// DENY-BY-DEFAULT for the UNRESOLVABLE target class (task dangerous-command-deny-by-default). The
// isCatastrophicTarget blocklist above can only judge a LITERAL operand — it is structurally BLIND to a
// target whose value is decided at runtime, and passes it. That blind spot is the residual the audit
// named "a blocklist cannot enumerate its way to safety". We close the two shapes that are BOTH genuinely
// catastrophic AND have zero legitimate-script exposure (measured across the repo before shipping):
//   1. command substitution — `rm -rf $(…)` / the value could be `/`; a static scan cannot prove it isn't;
//   2. a variable running STRAIGHT into a root-reaching glob — `$X/*`, `$X*`: an unset or `/`-valued var
//      expands to `/*` or `*` (the Steam bug that deleted users' home directories). The safe form guards
//      the var (`${X:?}`) or deletes the directory itself, not its glob.
// Deliberately NARROW so the shared git-content scan does not cry wolf on careful scripts: a variable with
// a FIXED leaf (`$HOME/.cache`, a bare `$D` from mktemp, `$X/build`) is LEFT to the literal blocklist and
// passes here. Only the glob-to-root and command-substitution shapes are denied by default. (The broader
// "a live rm must name a concrete target, not a bare $VAR" posture needs a live-vs-content strictness mode
// — an API change across all callers — tracked as a follow-up, not folded into this shared detector.)
function isUnprovableRecursiveTarget(tok) {
  // A fully single-quoted shell word is literal: variables, globs and substitutions inside it do
  // not expand. Preserve that narrow provable case; mixed or double-quoted words still expand.
  if (/^'[^']*'$/.test(tok)) return false;
  const u = tok.replace(/['"]/g, "");          // mixed/double quoting cannot prove a runtime target
  if (/\$\(/.test(u)) return true;             // command substitution: $(…)
  if (/`/.test(u)) return true;                // backtick substitution: `…` (hostile-g-f3; was only $(…))
  // Variable feeding a glob or bare PATH SEPARATOR. These are one shell-expansion problem and must
  // use one grammar. The older independent var-glob regex treated `\w+` as a parameter name, so it
  // missed disappearing special parameters (`$@/*`) and consumed too much of unbraced positionals
  // (`$10/*` is `$1` + literal `0/*`, not parameter 10). Keep an explicit marker for a possible empty
  // contribution; that lets the glob judgment see whether the parameter DIRECTLY feeds `*` after
  // shell-correct reduction without confusing a safe surviving suffix such as the `0` in `$10/*`.
  //
  // The G-F4 boundary remains: a leading empty-parameter glob and one under an absolute path are
  // unprovable; a relative mid-path form is bounded by cwd. Thus `$X/*` and `/opt/$X/*` block, while
  // `build/$X/*`, `$10/*`, and `$1x/*` stay allowed.
  //
  // The task that found this described the wrong shape, and the correction is the whole point:
  // a TRULY BARE `$X` is harmless. Unset, it produces ZERO words (verified inertly with
  // `set -- $X; echo $#`), so `rm -rf $X` has no operand at all and rm simply complains. The
  // danger is the trailing SEPARATOR, which keeps the token alive as one word:
  //     $X/   → /      ${X}/ → /      "$X/" → /      $X// → //     $X/. → /.     /$X/ → //
  // Six live root wipes, none blocked, while `$X/*` blocked — the glob was doing all the work.
  //
  // SCOPED DELIBERATELY to branches that reduce to a target the literal classifier already calls
  // catastrophic, not to every var-path. A relative cleanup (`build/$ARCH/` leaves `build//`) keeps
  // a named segment and passes. Root, cwd, bare-ancestor, and protected-system-root branches do not.
  //
  // `${VAR:?}` is deliberately NOT erased: the shell aborts on an unset guarded var, so it is
  // provable, and the remedy in every message ("guard the variable with ${var:?}") keeps working.
  //
  // NAMED RESIDUAL, not an oversight: `$X/foo` → `/foo` and `/opt/$X/logs` → `/opt//logs` still pass.
  // They delete a named directory rather than a filesystem/system root, which is a different
  // severity, and widening to them would deny `rm -rf $HOME/.cache` — exactly the over-block that
  // gets a P0 guard disabled. Recorded rather than silently left. Bare `/opt/$X/` is NOT named:
  // empty expansion makes it `/opt`, already a catastrophic literal target, so it blocks.
  // A relative branch is allowed only when a named segment survives. `./$X/` becomes `.//`, the
  // current directory, and `../$X/` becomes `..//`, a bare ancestor; both are already catastrophic
  // literal targets. `build/$X/` remains bounded by the named `build` segment and passes.
  // Reduce parameter expansions to every RELEVANT reachable contribution. Conditional operators
  // cannot soundly collapse to one string: `${X:+/}` reaches `/` on its set branch, while `${X-/}`
  // reaches `/` on its unset branch. Iterate one innermost expansion at a time and retain both the
  // empty and declared-word branches where shell semantics permit them. Error guards (`?` / `:?`)
  // stay intact only where they abort rather than produce a value. An adversarial combinatorial
  // token fails closed once its distinct branch set exceeds the bound.
  const EMPTY_PARAM = "\u0000";
  const GUARDED_PARAM = "\u0001"; // `${X:?}` is nonempty-or-abort, and must not stall an outer reduction
  const MAX_PARAMETER_BRANCHES = 256;
  let reducedBranches = [u.replace(/\$(?:[A-Za-z_]\w*|[0-9]|[@*!])/g, EMPTY_PARAM)];
  let branchOverflow = false;
  for (let i = 0; i < u.length; i++) {
    let changed = false;
    const nextBranches = [];
    for (const candidate of reducedBranches) {
      const match = candidate.match(/\$\{([^{}]+)\}/s);
      if (!match) { nextBranches.push(candidate); continue; }
      changed = true;
      const whole = match[0];
      const expression = match[1];
      let parameterExpression = String(expression);
      if (parameterExpression.startsWith(PARAM_LITERAL_OPEN)) {
        let flagDepth = 0;
        for (let j = 0; j < parameterExpression.length; j++) {
          if (parameterExpression[j] === PARAM_LITERAL_OPEN) flagDepth++;
          if (parameterExpression[j] === PARAM_LITERAL_CLOSE && --flagDepth === 0) {
            parameterExpression = parameterExpression.slice(j + 1);
            break;
          }
        }
      }
      const parsed = parameterExpression.match(/^(\w+|[@*!?#$-])(.*)$/s);
      const anonymous = parameterExpression.match(/^:([-=+?])(.*)$/s);
      // An unrecognized innermost expression must never remain identical and stall reduction of a
      // containing conditional. It is also NOT provably nonempty: valid Zsh forms such as `${^foo}`
      // and `${(U)foo}` can disappear. Model unknown syntax as possibly empty (fail closed).
      let replacements = [EMPTY_PARAM];
      if (anonymous) {
        const operator = anonymous[1];
        const word = anonymous[2];
        // Zsh accepts `${:-word}` and `${(flags):-word}` with no named parameter. The anonymous
        // value is unset: default/assignment selects word, alternative selects empty, error aborts.
        if (operator === "-" || operator === "=") replacements = [word || EMPTY_PARAM];
        else if (operator === "+") replacements = [EMPTY_PARAM];
        else replacements = [GUARDED_PARAM];
      } else if (parsed) {
        const name = parsed[1];
        const tail = parsed[2];
        const fixedSpecial = /^[?#$-]$/.test(name);
        const fixedAlternative = fixedSpecial && tail.match(/^:?\+(.*)$/s);
        if (fixedSpecial) {
          // Exit status, argument count, PID, and option flags have a known named/numeric value.
          // Default/error/assignment forms therefore retain that value; only `+` selects its word.
          replacements = fixedAlternative
            ? [fixedAlternative[1] || EMPTY_PARAM]
            : [GUARDED_PARAM];
        } else if (tail === "") replacements = [EMPTY_PARAM];
        else if (tail.startsWith(":?")) replacements = [GUARDED_PARAM];
        else if (tail.startsWith("?")) replacements = [EMPTY_PARAM]; // set-empty branch
        else {
          const colonFallback = tail.match(/^:[-=](.*)$/s);
          const plainFallback = tail.match(/^[-=](.*)$/s);
          const alternative = tail.match(/^:?\+(.*)$/s);
          if (colonFallback) replacements = [colonFallback[1] || EMPTY_PARAM];
          else if (plainFallback) replacements = [EMPTY_PARAM, plainFallback[1] || EMPTY_PARAM];
          else if (alternative) replacements = [EMPTY_PARAM, alternative[1] || EMPTY_PARAM];
          // Trim/substitution/substring transforms of an unset ordinary variable produce empty.
          else replacements = [EMPTY_PARAM];
        }
      }
      const at = match.index;
      for (const replacement of new Set(replacements)) {
        nextBranches.push(candidate.slice(0, at) + replacement + candidate.slice(at + whole.length));
      }
    }
    reducedBranches = [...new Set(nextBranches)];
    if (reducedBranches.length > MAX_PARAMETER_BRANCHES) { branchOverflow = true; break; }
    if (!changed) break;
  }
  if (branchOverflow) return true;
  for (const varsReduced of reducedBranches) {
    const didReduce = varsReduced !== u;
    const emptyFeedsGlob = /\u0000[/.]*\*/.test(varsReduced);
    if (emptyFeedsGlob && (varsReduced.startsWith(EMPTY_PARAM) || u.startsWith("/"))) return true;
    const varsErased = varsReduced.replaceAll(EMPTY_PARAM, "");
    // Judge every reduced branch with the same canonical target classifier as a literal operand.
    // This covers repeated separators, dot segments, and first-segment glob spellings rather than
    // enumerating only `/` and `/*`. A surviving relative name remains bounded and therefore passes.
    const reducedTarget = varsErased.replace(/\/{2,}/g, "/");
    if (didReduce && reducedTarget.length > 0 && isCatastrophicTarget(reducedTarget)) return true;
  }

  // xargs -I{} / -i placeholder: the real path arrives only at runtime (often from `echo /`)
  if (/^\{\d*\}$/.test(u) || u === "{}" ) return true;
  return false;
}

// Shell BRACE EXPANSION runs before the command does, so `rm -rf {/,}` reaches rm as `rm -rf / `
// (the empty alternative drops out) — a root wipe the token-literal blocklist missed because the
// operand token is `{/,}`, not `/` (guard-brace-expansion, vivenna 2026-07-21). Expand comma-brace
// groups so EVERY alternative is checked as its own target. Ranges (`{1..9}`) and the bare xargs
// placeholder (`{}` — no comma) are left literal: a range never reaches a filesystem root, and `{}`
// has its own placeholder rule. Bounded (cap results + iterations) so a big/adversarial expansion
// can't blow up; a legit `dist/{a,b,c}` expands to safe subdir targets and still passes.
function firstCommaBrace(s) {
  for (let i = 0; i < s.length; i++) {
    if (s[i] !== "{") continue;
    let depth = 0, cur = "", hasTopComma = false;
    const parts = [];
    for (let j = i; j < s.length; j++) {
      const ch = s[j];
      if (ch === "{") { depth++; if (depth > 1) cur += ch; continue; }
      if (ch === "}") { depth--; if (depth === 0) { parts.push(cur); if (hasTopComma) return { start: i, end: j, parts }; break; } cur += ch; continue; }
      if (ch === "," && depth === 1) { hasTopComma = true; parts.push(cur); cur = ""; continue; }
      cur += ch;
    }
    // this `{` held no top-level comma (range/plain/unbalanced) → keep scanning for the next `{`
  }
  return null;
}
function expandBraces(token, cap = 256) {
  if (typeof token !== "string" || !token.includes("{")) return [token];
  let out = [token];
  for (let iter = 0; iter < 16 && out.length < cap; iter++) {
    let changed = false;
    const next = [];
    for (const s of out) {
      const g = firstCommaBrace(s);
      if (!g) { next.push(s); continue; }
      changed = true;
      const pre = s.slice(0, g.start), post = s.slice(g.end + 1);
      for (const part of g.parts) { next.push(pre + part + post); if (next.length >= cap) break; }
      if (next.length >= cap) break;
    }
    out = next;
    if (!changed) break;
  }
  return out;
}

// Shared classification of an rm-like tail (flags + targets) after a known recursive-delete verb.
// Used by literal `rm` and by variable-as-command-verb (`X=rm; $X -rf /`).
function classifyRmTail(tail, samplePrefix = "rm") {
  if (/--no-preserve-root/.test(tail)) {
    return { sample: (samplePrefix + tail).trim().slice(0, 120), detail: "--no-preserve-root only exists to wipe /" };
  }
  const unquoteWord = (t) => t.replace(/^(['"])(.*)\1$/, "$2");
  const flagTail = tail.replace(/(^|\s)(['"])(-{1,2}[A-Za-z-]+)\2(?=\s|$)/g, "$1$3");
  const flagText = (flagTail.match(/(?:^|\s)(-{1,2}[A-Za-z-]+)/g) || []).join(" ");
  const recursive = /--recursive/.test(tail) || /-[A-Za-z]*[rR]/.test(flagText);
  const force = /--force/.test(tail) || /-[A-Za-z]*f/.test(flagText);
  if (!recursive) return null;
  const targets = tail.trim().split(/\s+/).filter((t) => t && !unquoteWord(t).startsWith("-"))
    .flatMap((t) => expandBraces(t));
  for (const t of targets) {
    if (isCatastrophicTarget(t)) {
      return { sample: (samplePrefix + " " + tail).trim().slice(0, 120), detail: `recursive delete of ${t}` };
    }
  }
  if (force) {
    for (const t of targets) {
      if (isUnprovableRecursiveTarget(t)) {
        return {
          sample: (samplePrefix + " " + tail).trim().slice(0, 120),
          detail: `recursive force-delete of an unresolvable target ${t} (deny-by-default: resolve to a literal path, or guard the variable with \${var:?})`,
        };
      }
    }
  }
  const noTarget = noOnlineTargetDeny(samplePrefix, targets, tail);
  if (noTarget) return noTarget;
  return null;
}

// SHARED no-on-line-target rule (p1-guard-indirection-wrappers-are-rm-only).
//
// A destructive verb reached with NO literal target on the line is being fed its operand from
// stdin/xargs, where the operand is UNPROVABLE and can be `/` — `echo / | xargs chmod -R 777`,
// `cat paths | xargs srm -rf`. rm has denied this since guard-xargs-stdin-target, but the rule
// lived inside classifyRmTail, so chmod/chown/shred/srm inherited the wrapper BOUNDARY (they parse
// after `xargs`/`-exec`/`eval`) yet not the no-target DENY. Measured live: the identical stdin shape
// carrying a permission or secure-delete verb walked straight through while its rm twin was blocked.
//
// ONE implementation, called by every destructive matcher, so teaching the guard a new verb reaches
// the wrapped path at the same time as the direct path. Each caller supplies its OWN danger-gate
// before calling — rm/chmod/chown gate on `recursive`; shred/srm/wipe are destructive with no -r, so
// they call unconditionally — which matches exactly what each verb's direct-invocation path already
// treats as dangerous. The over-block this imposes (`find ./x | xargs rm -rf`, `… | xargs chmod -R`)
// is the SAME tradeoff already shipped and quorum-accepted for rm: an unprovable operand to a
// recursive/destructive verb is refused, and the fix is to name a literal path.
function noOnlineTargetDeny(verb, targets, tail) {
  // xargs -I{} / -i placeholder: the real operand arrives at runtime (often `echo / | xargs -I{} …`).
  for (const t of targets) {
    const u = t.replace(/['"]/g, "");
    if (/^\{\d*\}$/.test(u) || u === "{}") {
      return {
        sample: (verb + " " + tail).trim().slice(0, 120),
        detail: `${verb} of xargs placeholder ${t} (stdin path unprovable)`,
      };
    }
  }
  if (targets.length === 0) {
    return {
      sample: (verb + " " + tail).trim().slice(0, 120),
      detail: `${verb} with no on-line target (stdin/xargs — name a literal path)`,
    };
  }
  return null;
}

// rm at a command boundary → parse its flags+targets, block on recursive+force of a catastrophic
// target, or on --no-preserve-root (a flag whose only purpose is to allow wiping /).
// An optional PATH PREFIX before the verb. BOUNDARY already understands sudo/env/xargs/busybox/
// eval and friends, but it had no notion of invoking the binary by path, so the verb matched only
// as a bare word: `/bin/rm -rf /` and `/usr/bin/rm -rf /` were ALLOWED, with no variable and no
// obfuscation involved (verified pre-existing at 854b1619~1, so this is not a regression from the
// POSIX-grammar work — that work is sound and simply did not touch this line).
//
// Scoped to a prefix ENDING in `/`, so the basename must still be the verb itself: `rmdir` is
// untouched because `\brm\b` cannot match inside it, and a directory merely containing "rm" in its
// name does not match because the group has to end at the separator immediately before the verb.
//
// The prefix must also admit a PARAMETER EXPANSION, not just a literal path (UL-254, found by
// differential-testing our scanCommand against deer-flow's rule set and confirmed live here on
// 2026-08-09): the original class only accepted `.`/`~`/`/`, so `P=/bin; $P/rm -rf /` — and the
// bare `$P/rm -rf /` / `${P}/rm -rf /` — were ALLOWED while `/bin/rm -rf /` and `rm -rf /` were
// both correctly blocked. The variable-as-command-VERB rule below does not cover it either: there
// the variable holds the verb, here it holds the DIRECTORY and `rm` is a literal that simply never
// sat at a boundary. Same blind spot as UL-223, one indirection further out.
//
// Deliberately not resolving the variable: this is a static scanner, and what makes the shape
// catastrophic is the recursive+force tail against a catastrophic target, which is classified
// exactly as before. An unset `$P` would make the command fail rather than wipe — blocking it is
// the safe direction on the operator's own machine (UL-215: my last calibration here was too
// loose and was reversed).
//
// ── 2026-08-10, #2747 + #2898: STOP ENUMERATING PREFIX SPELLINGS ──────────────────────────
// The line below used to enumerate which characters could introduce a directory, and it was
// widened SEVEN times in four days (varpath-separator 08-08, verb-path-prefix 08-09, UL-254
// 08-10 …), each time closing exactly the one spelling that had just been demonstrated. An
// enumeration of an open set is not a guard; it is a list of the attacks someone already
// thought of. Measured cost of that decomposition, live on main with inert probes: ten more
// parameter-expansion shapes still walked through (`$1/rm`, `${1}/rm`, `${!P}/rm`, `${@}/rm`,
// `$*/rm`, `$(dirname /bin/ls)/rm`, the backtick twin …), and `$1/` is not exotic — it is the
// ordinary way a shell script names a path passed as its first argument.
//
// So invert it. What makes a command `rm` is not how its DIRECTORY is spelled; it is that the
// executed BASENAME is `rm`. Everything before the final `/` is a directory expression and we
// do not care what it says. A directory expression is any run of shell WORD ATOMS, of which
// there are exactly three kinds — an ordinary path character, a parameter expansion, and a
// command substitution. That set is closed by the shell's own grammar, so a new *spelling* of
// a parameter expansion (`${!P}`, `${1}`, `${@}`) needs no new alternative here. This is the
// difference between a rule and a blocklist.
//
// So the rule is simply: OPTIONAL DIRECTORY, then the verb. Anything that is not a command
// separator, up to the final `/`. One line, no spelling list — and nothing to widen next time
// someone finds an expansion form we did not think of, because the form no longer matters.
//
// This deliberately replaces a five-alternative version (an atom set enumerating command
// substitution / backticks / braced / short expansions) that I wrote first and then MEASURED:
// dropping the command-substitution, backtick, and braced-expansion alternatives one at a time
// changed *nothing* — 11/11 cases stayed blocked. Only the short-expansion alternative was
// load-bearing, and the line below covers it. The reason is worth recording, because it is not
// obvious: BOUNDARY already counts `)`, `}` and a backtick as command boundaries, so in
// `$(dirname /bin/ls)/rm` and `${!P}/rm` the closing bracket IS the boundary and all that is
// needed after it is the plain `/`. Bracketed expansions were therefore never the hard case.
// The genuinely new coverage here is the UNBRACKETED forms, which have no closing token to act
// as a boundary (`$1/rm`, `$9/rm`, `$P/rm`, `$*/rm`), plus literal directories on the sibling
// verbs below. Shipping the atom set would have meant claiming a mechanism that does no work.
const PATH_PREFIX = "(?:[^\\s;&|`)]*/)?";

function matchRm(cmd) {
  const re = new RegExp(BOUNDARY + PATH_PREFIX + "rm\\b([^\\n;&|`)]*)", "gi");
  let m;
  while ((m = re.exec(cmd))) {
    const hit = classifyRmTail(m[1] || "", "rm");
    if (hit) return hit;
  }
  return null;
}

// Variable-as-command-verb (dc-guard-variable-indirection): `X=rm; $X -rf /` never matches
// BOUNDARY+rm because the verb is the expansion of $X. Static approx: simple assignment of a
// catastrophic verb name in the same command string, then that name used as $VAR / ${VAR} at a
// command boundary with the same recursive-delete classification. Does NOT resolve live shell
// state; write-then-run of an unseen script remains out of scope (documented residual).
function matchVariableCommandRm(cmd) {
  const assigned = new Set();
  // X=rm / X="rm" / X='rm' at a command-ish position (start or after separator), AND the same
  // assignment written as a PATH to the binary — X=/bin/rm, X=/usr/bin/rm, X=./rm. The bare-name
  // form was covered and the path form was not, which is the same blind spot the literal verb
  // matcher had: `rm` was recognised as a word but never as the basename of a path.
  //
  // #2898: the directory half of the assignment carried its OWN copy of the enumerated prefix
  // (`[.~/]…`), so `D=/bin; X=$D/rm; $X -rf /` walked through while the literal `X=/bin/rm`
  // twin was blocked. It now shares PATH_PREFIX — one definition of "a directory expression",
  // used everywhere a binary is named by path, so the two can no longer drift apart.
  // PATH_PREFIX is all non-capturing, so the \2 backreference below still means the quote.
  for (const m of String(cmd).matchAll(
    new RegExp("(?:^|[\\s;|&()])([A-Za-z_][A-Za-z0-9_]*)=(?:([\"'])?" + PATH_PREFIX + "rm\\2?)\\b", "g"),
  )) {
    assigned.add(m[1]);
  }
  if (assigned.size === 0) return null;
  const re = new RegExp(BOUNDARY + "\\$\\{?([A-Za-z_][A-Za-z0-9_]*)\\}?\\b([^\\n;&|`)]*)", "g");
  let m;
  while ((m = re.exec(cmd))) {
    if (!assigned.has(m[1])) continue;
    const hit = classifyRmTail(m[2] || "", `$${m[1]}`);
    if (hit) {
      return {
        sample: hit.sample,
        detail: `variable-as-command-verb: ${m[1]}=rm then $${m[1]} used as recursive delete (${hit.detail})`,
      };
    }
  }
  return null;
}

// Gap family A (GUARD-ENCODING-GAPS-2026-08-09): verb reconstruction via command substitution —
// `$(printf '\x72\x6d') -rf /`, `$(echo -e '\x72\x6d') -rf /`, `` `printf …` -rf / ``.
// The verb token is not the literal `rm`, so BOUNDARY+rm and variable-as-command-verb both miss.
// Static approx: command-sub / backticks at a command boundary, then an rm-like recursive tail
// with a catastrophic target. Does not decode printf hex; requires the same classifyRmTail bar.
function matchCmdsubVerbRm(cmd) {
  const re = new RegExp(
    BOUNDARY + "(?:\\$\\([^\\n)]{1,240}\\)|`[^\\n`]{1,240}`)\\s+([^\\n;&|`]*)",
    "g",
  );
  let m;
  while ((m = re.exec(cmd))) {
    const hit = classifyRmTail(m[1] || "", "$(…)");
    if (hit) {
      return {
        sample: hit.sample,
        detail: `command-substitution-as-verb with recursive delete (${hit.detail})`,
      };
    }
  }
  return null;
}

// Gap family B — decoder → interpreter (same untrusted-bytes→shell shape as curl|sh, but
// the source is a decoder rather than a network fetcher). `echo … | base64 -d | sh`,
// `… | xxd -r -p | bash`. Plain `echo hello | sh` stays allowed (no decoder stage).
function matchDecoderPipeShell(cmd) {
  const m = String(cmd).match(
    /\b(base64|xxd|uudecode|openssl)\b[^\n;]*?\|\s*(?:[^\n;|]*\|\s*)*(sudo\s+)?(sh|bash|zsh|dash|ksh|ash)\b/i,
  );
  return m ? { sample: m[0].trim().slice(0, 120) } : null;
}

// Gap family B — `sh -c "$(curl …)"` / `bash -c "$(wget …)"`: fetcher is inside command
// substitution fed to -c, so there is no pipe token for curl-pipe-shell to see.
function matchShellCDownloadSub(cmd) {
  const m = String(cmd).match(
    /\b(sh|bash|zsh|dash|ksh|ash)\s+-[A-Za-z]*c\s+["']?\$\(\s*(curl|wget|fetch)\b/i,
  );
  return m ? { sample: m[0].trim().slice(0, 120) } : null;
}

// Gap family B residual shape: download-to-file then execute that path in the same line
// (`curl -o /tmp/i.sh URL; sh /tmp/i.sh`). Write-then-run across separate tool calls remains
// out of scope (documented residual — the guard only sees one command string).
function matchDownloadThenExecute(cmd) {
  const s = String(cmd);
  const dl = [
    ...s.matchAll(
      /\b(curl|wget|fetch)\b([^\n;|&]*)/gi,
    ),
  ];
  if (dl.length === 0) return null;
  const outPaths = new Set();
  for (const m of dl) {
    const tail = m[2] || "";
    const o =
      tail.match(/(?:^|\s)-(?:o|O)\s+(\S+)/) ||
      tail.match(/(?:^|\s)--output(?:=|\s+)(\S+)/) ||
      tail.match(/(?:^|\s)--output-document(?:=|\s+)(\S+)/);
    if (o) outPaths.add(o[1].replace(/^['"]|['"]$/g, ""));
  }
  if (outPaths.size === 0) return null;
  const run = new RegExp(
    BOUNDARY + "(?:sudo\\s+)?(sh|bash|zsh|dash|ksh|ash|source|\\.)\\s+(\\S+)",
    "gi",
  );
  let m;
  while ((m = run.exec(s))) {
    const pathTok = (m[2] || "").replace(/^['"]|['"]$/g, "");
    if (outPaths.has(pathTok)) {
      return {
        sample: `${m[0]}`.trim().slice(0, 120),
        detail: `download-to-file then execute ${pathTok}`,
      };
    }
  }
  return null;
}

// #2898: this matcher had NO path prefix at all, so `/bin/chmod -R 777 /` was ALLOWED while the
// bare `chmod -R 777 /` was blocked — no variable, no expansion, no obfuscation, just the ordinary
// habit of naming a binary by absolute path. The household spent four days hardening the `rm`
// prefix and never swept the equally irreversible siblings. A recursive chmod/chown of a
// filesystem root destroys the permission structure of the whole system.
function matchChmodChownRoot(cmd) {
  const re = new RegExp(BOUNDARY + PATH_PREFIX + "(chmod|chown)\\b([^\\n;&|`)]*)", "gi");
  let m;
  while ((m = re.exec(cmd))) {
    const tail = m[2] || "";
    const recursive = /--recursive/.test(tail) || /(?:^|\s)-[A-Za-z]*R/.test(tail);
    if (!recursive) continue;
    const targets = tail.trim().split(/\s+/).filter((t) => t && !t.startsWith("-"))
      .flatMap((t) => expandBraces(t));   // brace expansion: chmod -R 777 {/,} → /
    for (const t of targets) if (isCatastrophicTarget(t)) return { sample: (m[1] + tail).trim().slice(0, 120), detail: `recursive ${m[1]} of ${t}` };
    for (const t of targets) if (isUnprovableRecursiveTarget(t)) return { sample: (m[1] + tail).trim().slice(0, 120), detail: `recursive ${m[1]} of an unresolvable target ${t} (deny-by-default: resolve to a literal path, or guard the variable with \${var:?})` };
    // A RECURSIVE chmod/chown fed from stdin/xargs with no on-line PATH is the same unprovable-`/`
    // shape rm already refuses (guard-indirection-wrappers). chmod/chown take a MODE/OWNER as their
    // first positional token (`chmod -R 777 /` → ["777","/"]), so the paths are targets.slice(1):
    // `echo / | xargs chmod -R 777` parses to just ["777"], i.e. no path. Gated on `recursive`
    // above, so `find . -type f | xargs chmod 644` (no -R) is untouched.
    const noTarget = noOnlineTargetDeny(m[1], targets.slice(1), tail);
    if (noTarget) return noTarget;
  }
  return null;
}

// shred/srm/wipe destroy file contents IRREVERSIBLY (shred overwrites the bytes, -u also unlinks; srm/wipe
// secure-delete). The rm guard needs -r + a catastrophic target — but these need NO -r for a glob or a
// home/root operand: `shred -u ~/*` overwrites every file under home, `srm -rf ~` / `wipe -rf /Users/ken`
// wipe a whole home beyond recovery, and the guard knew none of them (only shred-against-/dev was covered).
// Block a secure-delete whose target is catastrophic (home/root/tilde-user/wildcard); a NAMED file
// (`shred -u secret.key`, `srm -rf ./build`) is a legitimate targeted op and still passes.
// #2898: same missing-prefix defect as chmod/chown — `/usr/bin/shred -u ~/*` and
// `/usr/local/bin/srm -rf ~` were ALLOWED while their bare twins were blocked. Secure-delete is
// the least recoverable verb in the file: shred overwrites the bytes on purpose.
function matchSecureDelete(cmd) {
  const re = new RegExp(BOUNDARY + PATH_PREFIX + "(shred|srm|wipe)\\b([^\\n;&|`)]*)", "gi");
  let m;
  while ((m = re.exec(cmd))) {
    const verb = m[1], tail = m[2] || "";
    const targets = tail.trim().split(/\s+/).filter((t) => t && !t.startsWith("-"))
      .flatMap((t) => expandBraces(t));   // `{~,}` etc. checked per alternative, same as rm
    for (const t of targets) if (isCatastrophicTarget(t)) return { sample: (verb + tail).trim().slice(0, 120), detail: `irreversible ${verb} of ${t}` };
    for (const t of targets) if (isUnprovableRecursiveTarget(t)) return { sample: (verb + tail).trim().slice(0, 120), detail: `irreversible ${verb} of an unresolvable target ${t} (deny-by-default)` };
    // shred/srm/wipe are destructive with no -r needed (the direct path blocks a bare catastrophic
    // target above), so a stdin/xargs-fed secure-delete with no on-line target is refused
    // unconditionally — the operand is unprovable and the verb is the least recoverable in the file.
    const noTarget = noOnlineTargetDeny(verb, targets, tail);
    if (noTarget) return noTarget;
  }
  return null;
}

// `git clean -f` deletes untracked files git cannot recover; adding -x/-X ALSO removes git-IGNORED
// files (build outputs, local .env, caches) — irreversible loss of state git deliberately keeps out of
// history. Block the forced form that reaches ignored files. Plain `git clean` (no -f) is a no-op git
// refuses, and `git clean -fd` (untracked only) is left allowed to avoid crying wolf on routine cleanup.
function matchGitClean(cmd) {
  const re = /\bgit\s+clean\b([^\n;|&]*)/gi;
  let m;
  while ((m = re.exec(cmd))) {
    const tail = m[1] || "";
    const flags = (tail.match(/(?:^|\s)(-{1,2}[A-Za-z-]+)/g) || []).join(" ");
    const force = /--force/.test(tail) || /-[A-Za-z]*f/.test(flags);
    const ignored = /-[A-Za-z]*[xX]/.test(flags);           // -x / -X → also delete ignored files
    if (force && ignored) return { sample: ("git clean" + tail).trim().slice(0, 120), detail: "force-clean removing git-ignored files (irreversible)" };
  }
  return null;
}

function matchForcePushProtected(cmd) {
  // Block a FORCE-push whose DESTINATION ref is protected. Force is a global flag
  // (--force, -f, --force-with-lease) or a leading `+` on a refspec.
  // The protected check is on the DESTINATION (after `:` in `src:dst`), not the source — so
  // `+HEAD:main` and `-f origin topic:production` block, while `+main:feature` (force TO a
  // non-protected ref) and a normal non-force push to main do not. The prior version only matched
  // `+main`/`--force … main` in the same segment and missed every `+src:dst` colon refspec.
  //
  // UL-302 — `--force-with-lease` used to be excluded here as "the sanctioned safe form". The
  // exclusion was documented and deliberate, and the safety argument is only half true. A lease
  // guarantees you are not clobbering commits you have not SEEN; it does not stop you rewriting
  // history others have already PULLED. On a protected branch those are different harms, and the
  // second one is the harm this rule exists to prevent. Note the incentive shape: a careful agent
  // reaches for `--force-with-lease` precisely BECAUSE it is the safe-sounding one, so the single
  // force variant most likely to be aimed at `main` was the only unguarded one.
  //
  // This is a SUPERSET, not a tightening: the rule fires only when the DESTINATION is protected,
  // so `--force-with-lease` stays completely free on every other ref — which is where the
  // sanctioned-safe-form argument actually holds. Operator-authorised 2026-08-10.
  const PROT = /^(?:main|master|prod|production|release)$/;
  // Allow git's global options between `git` and `push` — `git -C <dir> push …`, `git -c k=v push …`
  // (spensa 2026-07-15: `git -C /repo push --force origin main` evaded the old `git\s+push` anchor).
  const re = /\bgit\s+(?:-[A-Za-z]\S*\s+\S+\s+|-[A-Za-z]\S*\s+)*push\b([^\n;|]*)/gi;
  let m;
  while ((m = re.exec(cmd))) {
    const seg = m[0], args = m[1] || "";
    // `--force-with-lease` may carry a value: --force-with-lease=main, --force-with-lease=main:<sha>.
    const leaseForce = /(?:^|\s)--force-with-lease(?:=\S*)?(?=\s|$)/.test(seg);
    const hardForce = /(?:^|\s)(?:--force(?!-with-lease)|-f)\b/.test(seg);
    const globalForce = hardForce || leaseForce;
    const toks = args.trim().split(/\s+/).filter((t) => t && !t.startsWith("-"));  // remote + refspecs, no flags
    for (const t of toks) {
      const plus = t.startsWith("+");
      const body = plus ? t.slice(1) : t;
      const dst = (body.includes(":") ? body.split(":").pop() : body)
        .replace(/^refs\/heads\//, "").replace(/[\^~].*$/, "");   // strip refs/heads/ and ^{}/~N suffixes
      if ((plus || globalForce) && PROT.test(dst)) {
        // Name WHICH harm, because the two force forms fail differently and a reader who is told
        // "force-push" while holding a lease will reasonably think the guard misfired.
        const detail = (!plus && leaseForce && !hardForce)
          ? "force-push (--force-with-lease) to a protected branch — a lease prevents clobbering " +
            "commits you have not seen, but not rewriting history others have already pulled"
          : "force-push to a protected branch";
        return { sample: seg.trim().slice(0, 120), detail };
      }
    }
  }
  return null;
}

// severity is "block" for every rule here — all are catastrophic + irreversible.
const RULES = [
  { id: "rm-recursive-root", reason: "recursive force-delete of a filesystem root / home / system dir", test: matchRm },
  {
    id: "rm-variable-command-verb",
    reason: "recursive force-delete via variable-as-command-verb (X=rm; $X -rf …)",
    test: matchVariableCommandRm,
  },
  {
    id: "rm-cmdsub-verb",
    reason: "recursive force-delete via command-substitution-as-verb ($(printf…) -rf …)",
    test: matchCmdsubVerbRm,
  },
  { id: "chmod-chown-root", reason: "recursive permission/ownership change on a filesystem root", test: matchChmodChownRoot },
  { id: "secure-delete-catastrophic", reason: "irreversible secure-delete (shred/srm/wipe) of a filesystem root / home", test: matchSecureDelete },
  { id: "no-preserve-root", reason: "--no-preserve-root (only used to erase /)", test: (c) => (/--no-preserve-root/.test(c) ? { sample: "--no-preserve-root" } : null) },
  { id: "disk-dd", reason: "dd writing to a raw device (disk wipe)", test: (c) => { const m = c.match(new RegExp(BOUNDARY + "dd\\b[^\\n;&|]*\\bof=\\/dev\\/\\w", "i")); return m ? { sample: m[0].trim().slice(0, 120) } : null; } },
  { id: "device-redirect", reason: "redirecting output onto a raw device", test: (c) => { const m = c.match(/>\s*\/dev\/(?!null|zero|stdout|stderr|tty|random|urandom|fd\/)\w+/i); return m ? { sample: m[0].trim() } : null; } },
  { id: "mkfs", reason: "formatting a filesystem (mkfs/newfs)", test: (c) => { const m = c.match(new RegExp(BOUNDARY + "(mkfs(\\.\\w+)?|newfs)\\b", "i")); return m ? { sample: m[0].trim() } : null; } },
  { id: "diskutil-erase", reason: "diskutil erase/zero/reformat", test: (c) => { const m = c.match(/\bdiskutil\b[^\n;&|]*\b(eraseDisk|eraseVolume|zeroDisk|reformat|apfs\s+delete)/i); return m ? { sample: m[0].trim().slice(0, 120) } : null; } },
  { id: "shred-device", reason: "shred against a raw device", test: (c) => { const m = c.match(/\bshred\b[^\n;&|]*\/dev\/\w/i); return m ? { sample: m[0].trim().slice(0, 120) } : null; } },
  { id: "fork-bomb", reason: "fork bomb", test: (c) => { const m = c.match(/\w*\(\)\s*\{[^}]*\|[^}]*&[^}]*\}\s*;\s*\S/); return m ? { sample: m[0].trim().slice(0, 60) } : null; } },
  { id: "find-delete-root", reason: "find on / ~ or $HOME with -delete or -exec rm", test: (c) => { const m = c.match(/\bfind\s+(?:-\S+\s+)*(\/|~\/?|\$\{?HOME\}?)\s[^\n;]*(-delete\b|-exec\s+rm\b)/i); return m ? { sample: m[0].trim().slice(0, 120) } : null; } },
  // `find . -delete` with no FILTER predicate wipes everything under cwd (same class as `rm -rf .`).
  // Only the unfiltered form blocks: after `find .` we allow a run of non-selecting flags (-maxdepth N,
  // -depth, -xdev …) before -delete/-exec rm, but a predicate (-name/-path/-type/-regex/-size/-mtime…)
  // stops the run, so targeted cleanups like `find . -name '*.tmp' -delete` stay ALLOWED.
  { id: "find-delete-cwd", reason: "unfiltered find in cwd with -delete/-exec rm (recursive cwd wipe)", test: (c) => { const m = c.match(/\bfind\s+\.\s+(?:-(?:maxdepth|mindepth|depth|xdev|mount|noleaf|H|L|P)\S*\s+(?:\d+\s+)?)*(-delete\b|-exec\s+rm\b)/i); return m ? { sample: m[0].trim().slice(0, 120) } : null; } },
  { id: "force-push-protected", reason: "force-push to a protected branch (main/master/prod)", test: matchForcePushProtected },
  { id: "git-clean-ignored", reason: "force git-clean that deletes git-ignored files (irreversible)", test: matchGitClean },
  // curl|sh and multi-stage curl|tee|bash / curl|…|python (hostile-g-f5): any pipe chain that
  // starts with a downloader and ends at an interpreter is RCE — not only the adjacent `| bash`.
  { id: "curl-pipe-shell", reason: "piping a network download straight into a shell/interpreter", test: (c) => {
    const m = c.match(/\b(curl|wget|fetch)\b[^\n;]*?\|\s*(?:[^\n;|]*\|\s*)*(sudo\s+)?(sh|bash|zsh|dash|python3?|perl|ruby|node|php|lua|awk)\b/i);
    return m ? { sample: m[0].trim().slice(0, 120) } : null;
  } },
  {
    id: "decoder-pipe-shell",
    reason: "piping a decoder (base64/xxd/…) straight into a shell/interpreter",
    test: matchDecoderPipeShell,
  },
  {
    id: "shell-c-download-sub",
    reason: "shell -c with command-substitution download (curl/wget/fetch inside $())",
    test: matchShellCDownloadSub,
  },
  {
    id: "download-then-execute",
    reason: "download to a file then execute that path in the same command",
    test: matchDownloadThenExecute,
  },
  // Same execute-remote-code risk as curl|sh, but via process substitution: `bash <(curl …)`,
  // `python3 <(wget -qO- …)`, and `source <(curl …)` / `. <(wget …)` (hostile-g-f6).
  { id: "interpreter-download-substitution", reason: "interpreter executing a freshly-downloaded script via process substitution", test: (c) => {
    // Interpreters + `source`/`.` (dot) sourcing a process-sub download (hostile-g-f6).
    const m = c.match(/(?:(?:sudo\s+)?(?:sh|bash|zsh|dash|python3?|perl|ruby|node)\b|\bsource\b|(?:^|[\n;&|])\s*\.)\s+<\(\s*(curl|wget|fetch)\b/i);
    return m ? { sample: m[0].trim().slice(0, 120) } : null;
  } },
  // Language -e/-c/-r one-liners that embed a recursive catastrophic rm (ruby/python/node/perl/php).
  // The shell never sees `rm` at a command boundary — the interpreter executes it — so BOUNDARY+rm
  // alone misses `ruby -e 'system "rm -rf /"'` (hostile residual after pipe/source pass).
  { id: "interpreter-embedded-rm", reason: "interpreter one-liner embedding recursive delete of a catastrophic path", test: matchInterpreterEmbeddedRm },
];

function matchInterpreterEmbeddedRm(cmd) {
  const re = new RegExp(BOUNDARY + "(?:ruby|python3?|perl|node|php|lua)\\b([^\\n;&|]*)", "gi");
  let m;
  while ((m = re.exec(cmd))) {
    const body = m[1] || "";
    // Flag forms: -e/-c/-r / --eval / --command. Do NOT use \b before `-` (space-dash has no word boundary).
    if (!/(?:^|\s)(?:-[ecr]\b|--eval\b|--command\b)/i.test(body)) continue;
    if (!/\brm\b/i.test(body)) continue;
    // recursive flag anywhere in the one-liner ( -r / -rf / --recursive )
    if (!/(?:--recursive|(?:^|[\s"'`])-[A-Za-z]*[rR])/.test(body)) continue;
    // catastrophic path token inside the one-liner (quoted or bare)
    const catastrophic =
      /(?:-rf|-fr|-[A-Za-z]*r[A-Za-z]*f)\s*\/(?:\s|["'`);,]|$)/i.test(body) ||
      /rm\b[\s\S]{0,120}["'`]\s*\/\s*["'`]/.test(body) ||
      /rm\b[\s\S]{0,120}(?:\s|["'`(=])\/(?:\s|["'`);,]|$)/.test(body) ||
      /rm\b[\s\S]{0,120}(?:~|\$\{?HOME\}?)(?:\s|["'`);,/]|$)/.test(body) ||
      /rm\b[\s\S]{0,120}\/(?:Users|home|etc|var|usr|private|System|Library)\b/.test(body);
    if (catastrophic) return { sample: m[0].trim().slice(0, 120), detail: "interpreter embeds recursive catastrophic rm" };
  }
  return null;
}

/**
 * Scan a shell command string.
 * @param {string} raw
 * @returns {{blocked:boolean, matched:Array<{id,reason,sample,detail?}>}}
 */
function isInertWholeQuotedCommand(raw) {
  const text = stripShellLineContinuations(String(raw == null ? "" : raw)).trim();
  if (text.length < 2 || (text[0] !== "'" && text[0] !== '"')) return false;
  const quote = text[0];
  if (quote === "'") return text.indexOf("'", 1) === text.length - 1;
  let close = -1;
  for (let i = 1; i < text.length; i++) {
    if (text[i] === "\\") { i++; continue; }
    if (text[i] === '"') { close = i; break; }
  }
  if (close !== text.length - 1) return false;
  const body = text.slice(1, -1);
  // Double quotes still execute command substitution/backticks; those nested commands must scan.
  for (let i = 0; i < body.length; i++) {
    if (body[i] === "\\" && i + 1 < body.length) { i++; continue; }
    if (body[i] === "`" || (body[i] === "$" && body[i + 1] === "(")) return false;
  }
  return true;
}

export function scanCommand(raw) {
  if (isInertWholeQuotedCommand(raw)) return { blocked: false, matched: [] };
  const source = String(raw == null ? "" : raw);
  // A static detector must stay total under adversarial input. Extremely deep/large execution
  // syntax is unreviewable and previously overflowed recursive projection, making the live hook
  // exit 1 instead of issuing its explicit deny (exit 2). Refuse before normalization. The ceiling
  // is far above any legitimate command line but below the recursive stack hazard.
  const executionDelimiters = countActiveExecutionDelimiters(source);
  if (executionDelimiters > 128) {
    return { blocked: true, matched: [{
      id: "shell-structure-complexity",
      reason: "shell execution structure exceeds the detector's bounded review ceiling",
      sample: `${executionDelimiters} execution delimiters`,
      detail: "deny-by-default: put complex logic in a reviewed file instead of a live shell command",
    }] };
  }
  let cmd;
  try {
    cmd = normalize(source);
  } catch (error) {
    return { blocked: true, matched: [{
      id: "shell-structure-complexity",
      reason: "shell command could not be safely normalized",
      sample: String(error?.name || "normalization error").slice(0, 80),
      detail: "deny-by-default: detector errors never authorize live shell execution",
    }] };
  }
  const downstreamExecutionDelimiters = complexityMarkerCount(cmd);
  if (executionDelimiters + downstreamExecutionDelimiters > 128) {
    return { blocked: true, matched: [{
      id: "shell-structure-complexity",
      reason: "shell execution structure exceeds the detector's bounded review ceiling",
      sample: `${executionDelimiters + downstreamExecutionDelimiters} execution delimiters across shell layers`,
      detail: "deny-by-default: put complex logic in a reviewed file instead of a live shell command",
    }] };
  }
  cmd = cmd.replaceAll(SHELL_COMPLEXITY_MARKER, "");
  // Most rules run on the normalized surface only (quote-aware projection). A small set also
  // runs on the raw spelling: shapes like `sh -c "$(curl …)"` lose the download token under
  // projection while remaining live shell. Do NOT dual-scan curl-pipe-shell etc. — that would
  // re-block inert quoted references (`grep 'curl|sh'`) that normalize correctly leaves alone.
  const RAW_ALSO = new Set([
    "shell-c-download-sub",
    "rm-cmdsub-verb",
    "download-then-execute",
    "decoder-pipe-shell",
  ]);
  const matched = [];
  const seen = new Set();
  for (const rule of RULES) {
    const surfaces = RAW_ALSO.has(rule.id) ? [cmd, source] : [cmd];
    for (const surface of surfaces) {
      let hit;
      try { hit = rule.test(surface); } catch { hit = null; }   // a rule bug must never crash the guard
      if (!hit) continue;
      const sample = restoreSingleQuotedDollars(hit.sample || "");
      const key = `${rule.id}\0${sample}`;
      if (seen.has(key)) continue;
      seen.add(key);
      matched.push({ id: rule.id, reason: rule.reason, sample, detail: hit.detail });
      break; // one hit per rule is enough
    }
  }
  return { blocked: matched.length > 0, matched };
}

// Human-readable block message for a hook/CLI to print.
export function explain(result) {
  if (!result.blocked) return "";
  const lines = result.matched.map((r) => `  ✗ [${r.id}] ${r.reason}${r.detail ? ` — ${r.detail}` : ""}${r.sample ? `\n      ↳ ${r.sample}` : ""}`);
  return "BLOCKED: this command matches a catastrophic, irreversible pattern and will not run.\n" +
    lines.join("\n") +
    "\nIf this is a false positive: reference the string in a file instead of a live command, narrow the target, or ask the operator to run it manually. This guard errs toward blocking on purpose.";
}

export const RULE_IDS = [...RULES.map((r) => r.id), "shell-structure-complexity"];
