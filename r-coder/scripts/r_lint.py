#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# r_lint.py -- deterministic R style gate for the R Style Constitution.
#
# PURPOSE
# -------
# A pure-stdlib, deterministic linter that checks a single .R file (or a folder of
# .R files) against the R Style Constitution. It is the enforcement half of the
# r-coder agent: the agent writes reviewable R, this gate proves it mechanically
# (verification-with-code iron rule -- never an LLM judgment).
#
# SOURCE OF TRUTH
# ---------------
#   <SET_YOUR_PATH>/r-style.md          (the constitution, long form)
#   agents/r-coder/AGENT.md             (operative rules)
# GOLD exemplar (must produce ZERO FAILs):
#   your own linear cleaning script + its config
# ANTI-example (must FAIL loudly):
#   your own un-reviewable pipeline (many custom functions + loop/apply/map)
#
# CHECKS (constitution rule in parentheses)
# -----------------------------------------
#   (a) custom function definitions        (rule 2)  -> FAIL unless 0, or each has a
#                                                        "# reason:" comment within 3 lines above/inline
#   (b) loops / apply / map                (rule 2)  -> WARN on while, nested loops, and apply/map calls;
#                                                        a single for-over-a-vector is OK
#   (c) bare numeric indexing              (rule 4)  -> WARN when [n] / [n,] / [,n] has no adjacent
#                                                        stopifnot / assert / comment
#   (d) step headers                       (rule 1)  -> FAIL if a pipeline file has none;
#                                                        WARN if density < 1 per 150 code lines
#   (e) per-step persistence               (rule 5)  -> WARN if zero save/write calls; WARN if zero cat()
#   (f) comment-density floor 8%           (rule 7)  -> FAIL below 8%
#   (g) non-ASCII in comments / cat()      (rule 7)  -> FAIL on non-ASCII, non-Hebrew symbols
#                                                        (Hebrew IS allowed per rule 7)
#   (h) stop() / stopifnot presence        (rule 5)  -> WARN if zero in a file > 100 lines
#
# CONFIG FILES (basename contains "config") are treated per rule 3 (pure DATA, no logic):
# checks (a) functions, (b) loops, (c) indices, (f) density, (g) non-ASCII still apply;
# the pipeline-shape checks (d) step-headers, (e) persistence, (h) stop are N/A for them.
#
# OUTPUT: [PASS]/[WARN]/[FAIL] per check with line evidence, then an OVERALL verdict.
#         Both the number of failing CHECKS and the number of FAIL FINDINGS are reported.
#         Exit code 0 only if there are NO FAILs (WARNs do not block).
#
# EXECUTION (house rules)
# -----------------------
#   Run only via:  py -X utf8 r_lint.py <file-or-folder>
#                  py -X utf8 r_lint.py --selftest
#   Console prints are ASCII-only (Hebrew-Windows CP1255 safety). Offending non-ASCII
#   characters are reported as U+XXXX + Unicode name, never echoed raw.
#   Pure stdlib -- no third-party imports, no subprocess, no network.
#
# BOUNDARIES: this tool reads only the .R text handed to it. It never opens clinical
# folders and never reads participant DATA files -- it lints CODE. Folder mode skips
# any path containing a clinical marker and reads only *.R / *.r.

import argparse
import bisect
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# 0. Constants
# ---------------------------------------------------------------------------

COMMENT_DENSITY_FLOOR = 0.08          # rule 7 floor (constitution "~15%" spirit; 8% hard floor)
STEP_HEADER_PER_LINES = 150           # rule 1: expect >= 1 step header per 150 code lines
STOP_MIN_FILE_LINES = 100             # rule 5: expect a stop()/stopifnot in files over 100 lines
FUNCTION_REASON_LOOKBACK = 3          # rule 2: "# reason:" allowed within 3 lines above
INDEX_JUSTIFY_LOOKAHEAD = 3           # rule 4: assert/comment allowed within 3 lines below
MAX_EVIDENCE_LINES = 8                # cap evidence rows per check in the console

# Clinical / data-safety guards for folder mode (never traverse these).
CLINICAL_MARKERS = ("data_clinic", "_work", "clinic", "patient")  # add your own clinical-folder markers
R_EXTENSIONS = (".r",)

# Hebrew is explicitly allowed in comments and data (rule 7):
# the ASCII rule targets NON-Hebrew Unicode symbols only. These ranges are treated
# as allowed so legitimate Hebrew never trips check (g).
HEBREW_RANGES = (
    (0x0590, 0x05FF),   # Hebrew block
    (0xFB1D, 0xFB4F),   # Hebrew presentation forms
)

# Regexes over string-masked, comment-stripped code (see mask_strings()).
FUNC_DEF_RE = re.compile(r'^\s*([A-Za-z.][\w.]*)\s*(<<-|<-|=)\s*(function|\\)\s*\(')
FUNC_CONT_RE = re.compile(r'^\s*([A-Za-z.][\w.]*)\s*(<<-|<-|=)\s*$')  # name <- on its own line
LOOP_KW_RE = re.compile(r'(?<![\w.])(for|while)\s*\(')
APPLY_RE = re.compile(r'(?<![\w.])(v|s|l|t|m|r|e)?apply\s*\(')
MAP_RE = re.compile(r'(?<![\w.])(map2?|pmap|imap|walk2?|iwalk|pwalk)(_[A-Za-z0-9]+)?\s*\(')

# Bare positional indexing: [n], [n,...], [,n]  (ranges like [1:6] are NOT matched here).
BARE_INDEX_RES = (
    re.compile(r'\[\s*[0-9]+\s*\]'),      # x[29]
    re.compile(r'\[\s*[0-9]+\s*,'),       # x[29, ]
    re.compile(r'\[\s*,\s*[0-9]+'),       # x[, 3]
)

# Persistence: any save/write-to-disk call satisfies rule 5's "save the intermediate".
SAVE_RE = re.compile(
    r'(?<![\w.])(saveRDS|write_rds|write_csv|write_excel_csv|write_tsv|write\.csv|'
    r'write\.table|writeLines|write_json|write\.xlsx|saveWorkbook|ggsave|write_delim|'
    r'write_xlsx|readr::write_\w+|jsonlite::write_json|openxlsx::write\.xlsx)\s*\(')
CAT_RE = re.compile(r'(?<![\w.])(cat|message)\s*\(')
STOP_RE = re.compile(r'(?<![\w.])(stopifnot|stop)\s*\(')
REASON_RE = re.compile(r'reason\s*:', re.IGNORECASE)


# ---------------------------------------------------------------------------
# 1. Line parsing helpers -- split code vs comment, mask string interiors
# ---------------------------------------------------------------------------

def split_code_comment(line):
    """Return (code_part, comment_text_or_None). Locate the first '#' that is NOT
    inside a quoted string (", ', or backtick). Everything before it is code."""
    in_s = None
    esc = False
    for i, c in enumerate(line):
        if in_s:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == in_s:
                in_s = None
        else:
            if c in ('"', "'", '`'):
                in_s = c
            elif c == '#':
                return line[:i], line[i + 1:]
    return line, None


def mask_strings(code):
    """Replace the interior of every string literal with 'x' so that structural
    regexes (functions, loops, brackets, braces) never match inside string data.
    Quote delimiters are preserved so the rest of the code keeps its shape."""
    out = []
    in_s = None
    esc = False
    for c in code:
        if in_s:
            if esc:
                esc = False
                out.append('x')
            elif c == '\\':
                esc = True
                out.append('x')
            elif c == in_s:
                in_s = None
                out.append(c)
            else:
                out.append('x')
        else:
            if c in ('"', "'", '`'):
                in_s = c
                out.append(c)
            else:
                out.append(c)
    return ''.join(out)


def is_hebrew(cp):
    return any(lo <= cp <= hi for lo, hi in HEBREW_RANGES)


def ascii_safe(text, limit=90):
    """Sanitize an evidence snippet for an ASCII-only console: non-ASCII -> '?'."""
    s = ''.join(ch if ord(ch) < 128 else '?' for ch in text).rstrip()
    if len(s) > limit:
        s = s[:limit - 3] + '...'
    return s


def string_literals_on_line(line):
    """Yield the raw string-literal contents present on a single line."""
    lits = []
    in_s = None
    esc = False
    buf = []
    for c in line:
        if in_s:
            if esc:
                esc = False
                buf.append(c)
            elif c == '\\':
                esc = True
            elif c == in_s:
                lits.append(''.join(buf))
                buf = []
                in_s = None
            else:
                buf.append(c)
        else:
            if c in ('"', "'", '`'):
                in_s = c
                buf = []
    return lits


def is_step_header(line):
    """rule 1 step header: a '##' comment that names a Step or opens a numbered section."""
    s = line.strip()
    if not s.startswith('##'):
        return False
    body = s[2:]
    if re.search(r'\bStep\b', body, re.IGNORECASE):
        return True
    if re.match(r'\s*\d+[\.\):]', body):
        return True
    return False


# ---------------------------------------------------------------------------
# 2. Loop / apply nesting analysis (char scan with brace + pending-loop state)
# ---------------------------------------------------------------------------

def find_nested_loop_lines(masked_lines):
    """Return the set of 1-based line numbers where a for/while header is NESTED
    inside another loop body (braced OR single-statement chained). A single
    top-level loop over a vector is fine and is not reported here."""
    text = '\n'.join(masked_lines)
    n = len(text)
    nl_positions = [i for i, ch in enumerate(text) if ch == '\n']

    def line_of(pos):
        return bisect.bisect_right(nl_positions, pos) + 1

    nested = set()
    i = 0
    brace_depth = 0
    loop_body_depths = []   # brace depths at which a loop body is currently open
    pending_loop = False    # a loop header was seen; its body is not yet resolved
    while i < n:
        m = LOOP_KW_RE.match(text, i)
        if m:
            # A loop header. It is nested if we are inside a loop body OR the
            # immediately-enclosing loop's body turned out to be this very loop.
            if loop_body_depths or pending_loop:
                nested.add(line_of(i))
            # Skip the balanced (...) condition.
            j = text.find('(', m.start())
            depth_p = 0
            k = j
            while k < n:
                ch = text[k]
                if ch == '(':
                    depth_p += 1
                elif ch == ')':
                    depth_p -= 1
                    if depth_p == 0:
                        break
                k += 1
            i = k + 1
            pending_loop = True
            continue
        c = text[i]
        if c == '{':
            brace_depth += 1
            if pending_loop:
                loop_body_depths.append(brace_depth)
                pending_loop = False
        elif c == '}':
            while loop_body_depths and loop_body_depths[-1] >= brace_depth:
                loop_body_depths.pop()
            brace_depth -= 1
        elif not c.isspace():
            # First significant token of a single-statement loop body resolves it.
            pending_loop = False
        i += 1
    return nested


# ---------------------------------------------------------------------------
# 3. The individual checks
# ---------------------------------------------------------------------------
# Each check returns a 4-tuple: (severity, message, evidence_list, n_findings)
# where n_findings is the count of concrete violations (0 for a clean PASS). The
# n_findings lets the report distinguish "1 failing check with 16 violations"
# from "1 failing check with 1 violation".

def check_functions(lines, code_lines, masked):
    """(a) rule 2: custom function definitions. FAIL unless 0, or each is justified
    by a '# reason:' comment within 3 lines above (or inline)."""
    hits = []          # (line_no, name, justified)
    for idx, mline in enumerate(masked):
        m = FUNC_DEF_RE.match(mline)
        if not m:
            # name <- (newline) function(...)
            if FUNC_CONT_RE.match(mline):
                nxt = masked[idx + 1].lstrip() if idx + 1 < len(masked) else ''
                if nxt.startswith('function') or nxt.startswith('\\('):
                    m = FUNC_CONT_RE.match(mline)
            if not m:
                continue
        name = m.group(1)
        justified = False
        _, inline_comment = split_code_comment(lines[idx])
        if inline_comment and REASON_RE.search(inline_comment):
            justified = True
        for back in range(1, FUNCTION_REASON_LOOKBACK + 1):
            j = idx - back
            if j < 0:
                break
            _, cmt = split_code_comment(lines[j])
            if cmt and REASON_RE.search(cmt):
                justified = True
                break
        hits.append((idx + 1, name, justified))

    if not hits:
        return ('PASS', '(a) custom functions: 0 named function definitions', [], 0)
    unjustified = [h for h in hits if not h[2]]
    justified = [h for h in hits if h[2]]
    ev = []
    for ln, name, ok in hits[:MAX_EVIDENCE_LINES]:
        tag = 'justified(# reason:)' if ok else 'NO reason comment'
        ev.append('L%d: %s <- function(...)  [%s]' % (ln, ascii_safe(name, 40), tag))
    if len(hits) > MAX_EVIDENCE_LINES:
        ev.append('... and %d more function definitions' % (len(hits) - MAX_EVIDENCE_LINES))
    if unjustified:
        msg = ('(a) custom functions: %d definition(s), %d WITHOUT a "# reason:" '
               'justification (rule 2)' % (len(hits), len(unjustified)))
        return ('FAIL', msg, ev, len(unjustified))
    msg = ('(a) custom functions: %d definition(s), all justified with "# reason:" '
           '(rule 2 exception)' % len(justified))
    return ('WARN', msg, ev, len(justified))


def check_loops(lines, masked):
    """(b) rule 2: while loops, nested loops, and apply/map chains -> WARN.
    A single for-over-a-vector is OK and is only reported as an info count."""
    while_lines = []
    for_headers = []
    apply_lines = []
    map_lines = []
    for idx, mline in enumerate(masked):
        for m in LOOP_KW_RE.finditer(mline):
            if m.group(1) == 'while':
                while_lines.append(idx + 1)
            else:
                for_headers.append(idx + 1)
        if APPLY_RE.search(mline):
            apply_lines.append(idx + 1)
        if MAP_RE.search(mline):
            map_lines.append(idx + 1)

    nested = sorted(find_nested_loop_lines(masked))
    n_simple_for = len(for_headers)   # informational; single loops are allowed

    problems = []
    ev = []
    for ln in while_lines[:MAX_EVIDENCE_LINES]:
        ev.append('L%d: while (...) loop -- needs a stated reason (rule 2)' % ln)
    for ln in nested[:MAX_EVIDENCE_LINES]:
        ev.append('L%d: nested loop -- unfold or justify (rule 2)' % ln)
    for ln in (apply_lines + map_lines)[:MAX_EVIDENCE_LINES]:
        ev.append('L%d: apply/map call -- %s' % (ln, ascii_safe(lines[ln - 1].strip(), 70)))
    if while_lines:
        problems.append('%d while' % len(while_lines))
    if nested:
        problems.append('%d nested loop(s)' % len(nested))
    if apply_lines:
        problems.append('%d apply' % len(apply_lines))
    if map_lines:
        problems.append('%d map/walk' % len(map_lines))

    n_findings = len(while_lines) + len(nested) + len(apply_lines) + len(map_lines)
    if problems:
        msg = ('(b) loops/apply/map: %s (single for-over-a-vector is fine; these need '
               'a reason -- rule 2)' % ', '.join(problems))
        return ('WARN', msg, ev, n_findings)
    msg = '(b) loops/apply/map: clean (%d simple for-loop(s), 0 while/nested/apply/map)' % n_simple_for
    return ('PASS', msg, [], 0)


def check_bare_index(lines, masked):
    """(c) rule 4: bare numeric indexing without an adjacent stopifnot/assert/comment."""
    has_comment = []
    has_assert = []
    is_blank = []
    for ln in lines:
        code, cmt = split_code_comment(ln)
        has_comment.append(cmt is not None and cmt.strip() != '')
        has_assert.append(bool(STOP_RE.search(mask_strings(code)) or re.search(r'assert', code)))
        is_blank.append(ln.strip() == '')

    def justified(idx):
        # a comment/assert within 3 lines below, on the line itself,
        # or anywhere in the contiguous (no blank line) block above.
        for k in range(0, INDEX_JUSTIFY_LOOKAHEAD + 1):
            j = idx + k
            if j < len(lines) and (has_comment[j] or has_assert[j]):
                return True
        j = idx - 1
        steps = 0
        while j >= 0 and not is_blank[j] and steps < 40:
            if has_comment[j] or has_assert[j]:
                return True
            j -= 1
            steps += 1
        return False

    flagged = []
    for idx, mline in enumerate(masked):
        found = False
        for rex in BARE_INDEX_RES:
            if rex.search(mline):
                found = True
                break
        if found and not justified(idx):
            flagged.append(idx + 1)

    if not flagged:
        return ('PASS', '(c) bare numeric indexing: none unjustified (rule 4)', [], 0)
    ev = []
    for ln in flagged[:MAX_EVIDENCE_LINES]:
        ev.append('L%d: %s' % (ln, ascii_safe(lines[ln - 1].strip(), 70)))
    if len(flagged) > MAX_EVIDENCE_LINES:
        ev.append('... and %d more' % (len(flagged) - MAX_EVIDENCE_LINES))
    msg = ('(c) bare numeric indexing: %d position(s) with no adjacent assert/comment '
           '(rule 4 -- select by name, or pin+assert)' % len(flagged))
    return ('WARN', msg, ev, len(flagged))


def check_step_headers(lines, n_code_lines, is_config):
    """(d) rule 1: at least one '## Step' / '## N' header; density >= 1 per 150 code lines."""
    if is_config:
        return ('PASS', '(d) step headers: N/A for a config (pure-data) file (rule 3)', [], 0)
    headers = [i + 1 for i, ln in enumerate(lines) if is_step_header(ln)]
    if not headers:
        return ('FAIL', '(d) step headers: NONE found -- a pipeline must be a linear "## Step N" '
                        'narrative (rule 1)', [], 1)
    expected = max(1, n_code_lines // STEP_HEADER_PER_LINES)
    ev = ['found %d header(s): L%s' % (len(headers), ', L'.join(str(h) for h in headers[:MAX_EVIDENCE_LINES]))]
    if len(headers) < expected:
        msg = ('(d) step headers: %d found but ~%d expected (>=1 per %d code lines) -- '
               'consider more sub-steps (rule 1)' % (len(headers), expected, STEP_HEADER_PER_LINES))
        return ('WARN', msg, ev, 1)
    return ('PASS', '(d) step headers: %d present (linear narrative) (rule 1)' % len(headers), [], 0)


def check_persistence(masked, is_config):
    """(e) rule 5: per-step persistence (save/write) and a plain-language cat() count line."""
    if is_config:
        return ('PASS', '(e) persistence: N/A for a config (pure-data) file (rule 3)', [], 0)
    n_saves = sum(1 for m in masked if SAVE_RE.search(m))
    n_cats = sum(1 for m in masked if CAT_RE.search(m))
    problems = []
    if n_saves == 0:
        problems.append('0 save/write calls (no step_outputs -- rule 5)')
    if n_cats == 0:
        problems.append('0 cat()/message() count lines (rule 5)')
    if problems:
        return ('WARN', '(e) persistence: ' + '; '.join(problems), [], len(problems))
    return ('PASS', '(e) persistence: %d save/write call(s), %d cat()/message() line(s) (rule 5)'
            % (n_saves, n_cats), [], 0)


def check_comment_density(n_comment_lines, n_nonblank):
    """(f) rule 7: comment-density floor of 8%."""
    if n_nonblank == 0:
        return ('PASS', '(f) comment density: empty file', [], 0)
    density = n_comment_lines / n_nonblank
    pct = density * 100.0
    if density < COMMENT_DENSITY_FLOOR:
        return ('FAIL', '(f) comment density: %.1f%% is BELOW the %.0f%% floor (%d comment / %d '
                        'non-blank lines) (rule 7)' % (pct, COMMENT_DENSITY_FLOOR * 100,
                                                       n_comment_lines, n_nonblank), [], 1)
    return ('PASS', '(f) comment density: %.1f%% (>= %.0f%% floor; %d/%d) (rule 7)'
            % (pct, COMMENT_DENSITY_FLOOR * 100, n_comment_lines, n_nonblank), [], 0)


def check_non_ascii(lines):
    """(g) rule 7: non-ASCII, NON-Hebrew symbols in comments or cat()/message() strings.
    Hebrew is allowed (rule 7); the ban targets Unicode symbols
    like em-dash, smart quotes, arrows, check marks, and math signs (CP1255 garbage)."""
    findings = []   # (line_no, where, cp, name)

    def scan(text, line_no, where):
        for ch in text:
            cp = ord(ch)
            if cp < 128 or is_hebrew(cp):
                continue
            try:
                name = unicodedata.name(ch)
            except ValueError:
                name = 'UNKNOWN'
            findings.append((line_no, where, cp, name))

    for idx, ln in enumerate(lines):
        code, cmt = split_code_comment(ln)
        if cmt:
            scan(cmt, idx + 1, 'comment')
        if CAT_RE.search(mask_strings(code)):
            for lit in string_literals_on_line(ln):
                scan(lit, idx + 1, 'cat()-string')

    if not findings:
        return ('PASS', '(g) non-ASCII: none in comments or cat() strings (Hebrew allowed) (rule 7)', [], 0)
    ev = []
    seen = set()
    for ln, where, cp, name in findings:
        key = (ln, cp)
        if key in seen:
            continue
        seen.add(key)
        ev.append('L%d [%s]: U+%04X %s' % (ln, where, cp, name))
        if len(ev) >= MAX_EVIDENCE_LINES:
            break
    if len(findings) > len(ev):
        ev.append('... and %d more non-ASCII occurrence(s)' % (len(findings) - len(ev)))
    msg = ('(g) non-ASCII: %d non-Hebrew Unicode symbol(s) in comments/cat() -- replace with '
           'ASCII (rule 7)' % len(findings))
    return ('FAIL', msg, ev, len(findings))


def check_stop(masked, n_total_lines, is_config):
    """(h) rule 5: a stop()/stopifnot guard should exist in files over 100 lines."""
    if is_config:
        return ('PASS', '(h) stop()/stopifnot: N/A for a config (pure-data) file (rule 3)', [], 0)
    n_stop = sum(1 for m in masked if STOP_RE.search(m))
    if n_stop == 0 and n_total_lines > STOP_MIN_FILE_LINES:
        return ('WARN', '(h) stop()/stopifnot: none in a %d-line pipeline -- critical invariants '
                        'should halt loudly (rule 5)' % n_total_lines, [], 1)
    return ('PASS', '(h) stop()/stopifnot: %d guard(s) present (rule 5)' % n_stop, [], 0)


# ---------------------------------------------------------------------------
# 4. File-level orchestration
# ---------------------------------------------------------------------------

def lint_text(text, display_name):
    """Run all checks over the text of one R file. Returns a result dict."""
    lines = text.split('\n')
    masked = [mask_strings(split_code_comment(ln)[0]) for ln in lines]

    nonblank = [ln for ln in lines if ln.strip() != '']
    comment_lines = [ln for ln in nonblank if ln.strip().startswith('#')]
    n_nonblank = len(nonblank)
    n_comment = len(comment_lines)
    n_code = n_nonblank - n_comment

    base = os.path.basename(display_name).lower()
    is_config = 'config' in base

    results = []
    results.append(check_functions(lines, n_code, masked))
    results.append(check_loops(lines, masked))
    results.append(check_bare_index(lines, masked))
    results.append(check_step_headers(lines, n_code, is_config))
    results.append(check_persistence(masked, is_config))
    results.append(check_comment_density(n_comment, n_nonblank))
    results.append(check_non_ascii(lines))
    results.append(check_stop(masked, len(lines), is_config))

    fail_checks = sum(1 for r in results if r[0] == 'FAIL')
    warn_checks = sum(1 for r in results if r[0] == 'WARN')
    fail_findings = sum(r[3] for r in results if r[0] == 'FAIL')
    warn_findings = sum(r[3] for r in results if r[0] == 'WARN')
    return {
        'name': display_name,
        'kind': 'config' if is_config else 'pipeline',
        'n_total': len(lines),
        'n_code': n_code,
        'n_comment': n_comment,
        'n_nonblank': n_nonblank,
        'results': results,
        'fail_checks': fail_checks,
        'warn_checks': warn_checks,
        'fail_findings': fail_findings,
        'warn_findings': warn_findings,
    }


def read_r_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def gather_r_files(folder):
    found = []
    for root, dirs, files in os.walk(folder):
        low_root = root.lower()
        if any(mark in low_root for mark in CLINICAL_MARKERS):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not any(mark in d.lower() for mark in CLINICAL_MARKERS)]
        for fn in files:
            if fn.lower().endswith(R_EXTENSIONS):
                found.append(os.path.join(root, fn))
    return sorted(found)


def print_report(report):
    print('')
    print('File: %s' % ascii_safe(report['name'], 120))
    print('  kind=%s  total_lines=%d  code=%d  comment=%d'
          % (report['kind'], report['n_total'], report['n_code'], report['n_comment']))
    for sev, msg, ev, _cnt in report['results']:
        print('  [%s] %s' % (sev, msg))
        for line in ev:
            print('        %s' % ascii_safe(line, 110))
    verdict = 'FAIL' if report['fail_checks'] else ('WARN' if report['warn_checks'] else 'PASS')
    print('  -> file verdict: %s  (%d FAIL check(s) / %d FAIL finding(s); %d WARN check(s))'
          % (verdict, report['fail_checks'], report['fail_findings'], report['warn_checks']))


# ---------------------------------------------------------------------------
# 5. Self-test -- planted-defect positive controls (one per check) + clean control
# ---------------------------------------------------------------------------

CLEAN_PIPELINE = r'''# clean_demo.R -- tiny in-style pipeline (positive control: must be clean).
# Source of truth: demo plan. Style: no functions, no nested loops, ASCII only.
## Step 1: load and keep valid rows ----
# Read the frozen input and keep only the finished responses (plan Step 1).
dat <- readRDS("in.rds")
kept <- dat[dat$finished == 1, ]
saveRDS(kept, "step_outputs/kept.rds")
stopifnot(nrow(kept) <= nrow(dat))
cat("Step 1: kept", nrow(kept), "of", nrow(dat), "rows.\n")
## Step 2: score one scale over a named item vector ----
# Iterate the questionnaire names (simple loop over a named vector = allowed, rule 2).
items <- c("q1", "q2", "q3")
for (nm in items) kept[[nm]] <- as.numeric(kept[[nm]])
kept$scale <- rowMeans(kept[, items])
write.csv(kept, "step_outputs/scored.csv")
cat("Step 2: scored", length(items), "items.\n")
'''

DEFECT_FUNCTIONS = r'''# bad_functions.R
## Step 1: do a thing ----
# no reason comment here, so this must FAIL check (a)
clean_it <- function(x) {
  x[!is.na(x)]
}
score_it <- function(x) mean(x)
saveRDS(1, "o.rds")
cat("done\n")
'''

DEFECT_NESTED_WHILE = r'''# bad_loops.R
## Step 1: nested + while (must WARN on b) ----
# nested loop and a while and an sapply
saveRDS(1, "o.rds")
for (i in seq_len(3)) {
  for (j in seq_len(4)) {
    x <- i + j
  }
}
k <- 0
while (k < 5) {
  k <- k + 1
}
res <- sapply(1:3, function(z) z * 2)
cat("done\n")
'''

DEFECT_BARE_INDEX = r'''# bad_index.R
## Step 1: bare positional index with no justification (must WARN on c) ----
saveRDS(1, "o.rds")
dat <- read_thing()

value <- dat[42]

cat("done\n")
'''

DEFECT_NO_STEP = r'''# bad_headers.R -- a real pipeline body but with NO step headers (must FAIL on d)
# it saves and prints but never announces a single "## Step"
dat <- readRDS("in.rds")
kept <- dat[dat$ok, ]
saveRDS(kept, "o.rds")
stopifnot(nrow(kept) >= 0)
cat("kept", nrow(kept), "\n")
'''

DEFECT_NO_SAVE_CAT = r'''# bad_persistence.R
## Step 1: transforms but never saves or prints counts (must WARN on e) ----
# a pipeline that neither persists an intermediate nor prints a count line
dat <- readRDS("in.rds")
kept <- dat[dat$ok, ]
final <- kept
stopifnot(nrow(final) >= 0)
'''


def _make_low_comment_file():
    """Build a >100-line pipeline with < 8% comments (must FAIL on f)."""
    head = ['# low_comment.R -- one header only, then lots of code (must FAIL on f)',
            '## Step 1: churn ----',
            'saveRDS(1, "o.rds")',
            'stopifnot(TRUE)',
            'cat("go\\n")']
    body = ['x%d <- %d + 1' % (i, i) for i in range(150)]
    return '\n'.join(head + body) + '\n'


DEFECT_LOW_COMMENT = _make_low_comment_file()

DEFECT_NON_ASCII = (
    '# bad_ascii.R\n'
    '## Step 1: comment with an em-dash — which is CP1255 garbage (must FAIL on g)\n'
    'saveRDS(1, "o.rds")\n'
    'cat("range 1–5 done\\n")\n'   # en-dash inside a cat() string
    'stopifnot(TRUE)\n'
)

# Negative control for (g): Hebrew in a comment AND in a data string must NOT fail.
CONTROL_HEBREW_OK = (
    '# heb.R -- Hebrew is allowed (rule 7); this must NOT fail check (g)\n'
    '## Step 1: markers ----\n'
    '# הערה בעברית -- allowed\n'
    'markers <- c("בדיקה", "test")\n'
    'saveRDS(markers, "o.rds")\n'
    'cat("kept", length(markers), "\\n")\n'
    'stopifnot(length(markers) == 2)\n'
)


def _make_no_stop_file():
    """A >100-line pipeline with adequate comments but no stop()/stopifnot (WARN on h)."""
    parts = ['# no_stop.R -- long pipeline, no guard (must WARN on h)',
             '## Step 1: churn with plenty of comments ----']
    for i in range(120):
        parts.append('# comment describing operation %d and why it runs' % i)
        parts.append('x%d <- %d + 1' % (i, i))
    parts.append('saveRDS(1, "o.rds")')
    parts.append('cat("done\\n")')
    return '\n'.join(parts) + '\n'


DEFECT_NO_STOP = _make_no_stop_file()


def sev_of(report, check_prefix):
    """Return the severity of the check whose message starts with e.g. '(a)'."""
    for item in report['results']:
        if item[1].startswith(check_prefix):
            return item[0]
    return 'MISSING'


def run_selftest():
    print('=== r_lint self-test : planted-defect positive controls ===')
    cases = [
        # (label, filename, text, check_prefix, expected_severity)
        ('(a) function w/o reason -> FAIL', 'bad_functions.R', DEFECT_FUNCTIONS, '(a)', 'FAIL'),
        ('(b) nested/while/apply -> WARN', 'bad_loops.R', DEFECT_NESTED_WHILE, '(b)', 'WARN'),
        ('(c) bare index -> WARN', 'bad_index.R', DEFECT_BARE_INDEX, '(c)', 'WARN'),
        ('(d) no step header -> FAIL', 'bad_headers.R', DEFECT_NO_STEP, '(d)', 'FAIL'),
        ('(e) no save/cat -> WARN', 'bad_persistence.R', DEFECT_NO_SAVE_CAT, '(e)', 'WARN'),
        ('(f) low comment density -> FAIL', 'low_comment.R', DEFECT_LOW_COMMENT, '(f)', 'FAIL'),
        ('(g) non-ASCII symbol -> FAIL', 'bad_ascii.R', DEFECT_NON_ASCII, '(g)', 'FAIL'),
        ('(h) no stop in long file -> WARN', 'no_stop.R', DEFECT_NO_STOP, '(h)', 'WARN'),
    ]
    passed = 0
    for label, name, text, prefix, expected in cases:
        rep = lint_text(text, name)
        got = sev_of(rep, prefix)
        ok = (got == expected)
        passed += ok
        print('  [%s] %-38s expected=%-4s got=%-4s' % ('OK' if ok else 'XX', label, expected, got))

    # Negative controls: clean pipeline must have 0 FAIL; Hebrew must not fail (g).
    neg_ok = 0
    clean = lint_text(CLEAN_PIPELINE, 'clean_demo.R')
    c1 = clean['fail_checks'] == 0
    neg_ok += c1
    print('  [%s] %-38s expected=%-4s got=%-4s'
          % ('OK' if c1 else 'XX', 'clean pipeline -> 0 FAIL', '0', str(clean['fail_checks'])))
    heb = lint_text(CONTROL_HEBREW_OK, 'heb.R')
    c2 = sev_of(heb, '(g)') == 'PASS'
    neg_ok += c2
    print('  [%s] %-38s expected=%-4s got=%-4s'
          % ('OK' if c2 else 'XX', 'Hebrew comment/data -> (g) PASS', 'PASS', sev_of(heb, '(g)')))

    total = len(cases) + 2
    got_total = passed + neg_ok
    print('')
    print('self-test: %d/%d controls behaved as expected' % (got_total, total))
    if got_total == total:
        print('OVERALL SELFTEST: PASS')
        return 0
    print('OVERALL SELFTEST: FAIL')
    return 1


# ---------------------------------------------------------------------------
# 6. Entry point
# ---------------------------------------------------------------------------

def main(argv):
    ap = argparse.ArgumentParser(
        description='Deterministic R style gate (R Style Constitution).')
    ap.add_argument('path', nargs='?', help='a single .R file or a folder of .R files')
    ap.add_argument('--selftest', action='store_true',
                    help='run planted-defect positive controls and exit')
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest()

    if not args.path:
        ap.print_help()
        return 2

    target = args.path
    if os.path.isdir(target):
        files = gather_r_files(target)
        if not files:
            print('No .R files found under: %s' % ascii_safe(target))
            return 2
    elif os.path.isfile(target):
        if not target.lower().endswith(R_EXTENSIONS):
            print('Not an .R file: %s' % ascii_safe(target))
            return 2
        files = [target]
    else:
        print('Path not found: %s' % ascii_safe(target))
        return 2

    print('=== r_lint : R Style Constitution gate ===')
    print('target: %s  (%d file(s))' % (ascii_safe(target), len(files)))

    total_fail_checks = 0
    total_warn_checks = 0
    total_fail_findings = 0
    for path in files:
        try:
            text = read_r_file(path)
        except Exception as exc:  # noqa: BLE001 -- report, never crash the batch
            print('\nFile: %s\n  [FAIL] could not read: %s' % (ascii_safe(path), ascii_safe(str(exc))))
            total_fail_checks += 1
            total_fail_findings += 1
            continue
        report = lint_text(text, path)
        print_report(report)
        total_fail_checks += report['fail_checks']
        total_warn_checks += report['warn_checks']
        total_fail_findings += report['fail_findings']

    print('')
    print('=' * 60)
    overall = 'FAIL' if total_fail_checks else ('WARN' if total_warn_checks else 'PASS')
    print('OVERALL: %s  (%d FAIL check(s) / %d FAIL finding(s), %d WARN check(s) across %d file(s))'
          % (overall, total_fail_checks, total_fail_findings, total_warn_checks, len(files)))
    print('exit 0 only when there are no FAILs.')
    return 0 if total_fail_checks == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
