# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A **single-file, keyless, static web app** (`index.html`) — the "SMM Virality Decoder". It turns an
intake form into five copy-paste prompts (S1–S5) that an operator runs in a *separate* Claude chat
that has the Apify + Google Drive connectors (Higgsfield is NOT required — the pipeline generates
nothing and its `video_analysis` tool is not callable anyway). (The chain was condensed from eight steps to
five by fusing tightly-coupled stages — discovery+ranking, decode+synthesis, calendar+scripts — so the
operator pastes fewer times; the same nine vault files are still produced.) The dashboard itself makes **no network
calls, holds no API keys, and has no build step** — it only generates text. The actual scraping/decode
happens when a human pastes the generated prompts into a connected chat. Keep that boundary: do not add
fetch/API calls or a bundler to `index.html`.

**Two run modes (a toggle on the Intake tab, `localStorage.smm_mode`, default `chat`):**
- **Claude chat** — the default: emits the **five** copy-paste prompts (S1–S5), pasted one-by-one.
- **Claude Code** — emits **one** "auto-run" prompt the operator pastes into a Claude Code session: the
  **ORCHESTRATOR** template **plus the fully-rendered S1–S5 and S6 maker templates appended below it**
  (`generate()`'s `CURRENT_MODE==='code'` branch does the bundling — the pasted prompt must stay
  self-contained, since a Claude Code session can't fetch the templates). It runs the whole S1→S5 pipeline
  autonomously (maker→blind-checker at each gate, a bounded AUGMENT→REVAMP→REGENERATE ladder, an
  item-count-first budget governor, a hard NO-SILENT-DEGRADE block), grades every script with a
  weighted-rubric LLM judge — **tiered pass bars: proof-led REACH/NURTURE ≥ `MIN_VIRALITY_SCORE`,
  format-led (proof-less) ≥ MIN−3, CONVERT ≥ MIN−5** — then runs the **S6** deliverables: an 8–10 frame
  storyboard emitted as image-gen *prompts* (no images generated, zero credits) + a designer doc +
  optional generation prompts, with a two-way (frame↔source) faithfulness gate. The dashboard still only
  generates text; the autonomy happens in the connected Claude Code session.

## The one architecture rule that matters: PROMPTS.md is the source of truth

The five prompt templates live in **`PROMPTS.md`** (canonical). They are embedded into `index.html`
inside `<script type="text/plain" class="raw-prompt" data-step="S#">` blocks by a generator
(`inject_prompts.py` loops `S1..S5`). The two **Claude-Code-mode** templates (`## ORCHESTRATOR`, `## S6`)
also live in `PROMPTS.md` and are injected into `<script id="orchestrator-prompt">` / `<script id="s6-deliverables">`
— **NOT** `raw-prompt` blocks, so `STEPS = Object.keys(RAW).sort()` stays length 5. The reconciler runs over
`ALLTPL` (the 5 steps ∪ the 2 autonomous templates), so the `autorun` intake fields they consume
(`SCRIPTS_TO_WRITE`, `REELS_TO_DECODE`, `OUTPUTS_WANTED`, `MIN_VIRALITY_SCORE`, `MAX_REGEN_LOOPS`,
`RUN_BUDGET_USD`, `WHICH_AI_TOOL_NOTES`) are not flagged dead — land any new autorun field + its consuming
token together. `selftest.mjs` asserts byte-parity for all seven templates.

- **To change a prompt: edit `PROMPTS.md`, then run `python3 inject_prompts.py`.** Never hand-edit the
  `raw-prompt` blocks in `index.html` — they will be overwritten and will drift from the canonical copy.
- `selftest.mjs` asserts byte-for-byte parity between the two; a mismatch fails the suite.

## Templating engine + the invariants it enforces (in `index.html`, `<script id="engine">`)

Two placeholder forms: `{{UPPER_SNAKE}}` (literal replacement) and `[[IF KEY]]…[[ENDIF]]` (block kept
only when KEY is non-empty; **not nestable**). The intake fields are defined once in
`<script id="appdata">` as `FIELD_KEYS`; derived values are `DERIVED_KEYS` (`CURRENT_DATE`).

Three guards exist specifically to prevent the silent-data-loss bug class — preserve them when editing:
1. **Reconciler** (`reconcile`) compares every `{{KEY}}`/`[[IF KEY]]` token in the templates against
   `FIELD_KEYS ∪ DERIVED_KEYS`. **Orphan** (token with no field) → red banner + `generate()` hard-blocks.
   **Dead key** (field no template uses) → flagged. So: every new field must be consumed by a template,
   and every new template token must have a field.
2. **Pre-flight** (`preflight`) scans each generated prompt for leftover `{{`/`[[` and disables that
   step's Copy button if found.
3. **System-check tab** (`runDiagnostics`) runs both against the built-in `TEST_CLIENT` fixture.

The step list is derived once as `STEPS = Object.keys(RAW).sort()` — do not reintroduce a hand-written
`['S1'..'S5']` array anywhere.

**Intake specifics that the templates depend on:** `CLIENT_HANDLE` is **optional** — S1 branches on it
(`ESTABLISHED` account computes a baseline median; `NEW/THIN` account, i.e. no handle or <10 reels, skips
the baseline since S2's outlier math uses each *discovered* account's own median). A single
`ADDITIONAL_NOTES` catch-all field carries voice/pillars, and an optional `PROOF_ASSETS` field carries
owned results — S4 builds CONVERT slots only from it, and the grader's NO-PROOF CLIENT RULE re-weights
(instead of hard-blocking) when it's empty. S5's learning loop is guarded by `[[IF CLIENT_HANDLE]]`.
Discovery is geo-balanced: S2 runs a GEO query leg off `GEO_PRIMARY`, buckets origins
(TARGET-MARKET/CULTURE-MATCH/GLOBAL), and enforces a MARKET MIX quota (≥5 or an honest SHORTFALL) —
don't remove these when editing S2; they exist because generic keyword search returns the biggest
global-English creators regardless of the client's market.

**The 5-step → vault-file map:** S1→`s1-baseline`; **S2 (Discover & Rank)**→`s2-discovery`+`s3-outliers`;
**S3 (Decode & Synthesize)**→`s4-decode`+`s5-patterns`; **S4 (Plan & Script)**→`s6-calendar`+`s7-scripts`;
**S5 (Showcase + Learning Loop)**→`s8-report`+`s8b-learning-loop`. Step numbers (5) and vault-file numbers
(s1–s8) intentionally differ — the files are stable artifact names a merged step writes two at a time.

## Beautifier (`renderMarkdown` in `<script id="engine">`, "3 · Beautifier" tab)

Paste the S5 report markdown → branded printable HTML. The non-negotiable rule: **no silent drops** — every
non-blank source line is assigned to a block, with a generic-fallback branch so unrecognized content
still renders (visibly flagged), and a `dropped[]` coverage check. A ```` ```chart ```` fence (lines of
`Label: number`) becomes an inline SVG bar chart. All output is HTML-escaped before inline formatting;
link hrefs are scheme-whitelisted. Keep these guarantees if you touch the renderer.

## Verify after every change

```bash
node selftest.mjs          # engine + reconciler + parity (all 7 templates) + validation + grader/QC guards + beautifier (~62 checks, no deps)
python3 inject_prompts.py  # re-embed templates into index.html after editing PROMPTS.md
```

DOM-level render test (catches UI-wiring bugs) needs jsdom, which is not vendored:
```bash
cd /tmp && mkdir -p jsdomtest && (cd jsdomtest && npm install jsdom --no-save)
# then run a JSDOM script that loads index.html with runScripts:'dangerously' (stub window.confirm),
# resolving jsdom via createRequire('/tmp/jsdomtest/x.js'). Assert: chat mode → 5 stepcards; code mode →
# 1 card whose text contains "MAKER TEMPLATES" + all of S1–S6; no leftover {{ }}/[[ ]] in either mode.
```
There is no test framework; `selftest.mjs` is a flat list of `ok(name, condition)` assertions — to run
a "single test", comment out the others or read the labelled PASS/FAIL lines. To preview the app, just
open `index.html` in a browser (no server).

## Data-layer facts that must not drift (from VALIDATION_REPORT.md)

These were proven on real data; the prompt templates encode them and breaking them silently corrupts
the pipeline:
- Discovery is **niche-keyword-first** (`data-slayer/instagram-search-reels`, input `query`+`maxPages`),
  NOT competitor-handle-first. Competitor handles are optional force-include seeds.
- Outlier score = reel plays ÷ **that account's own median** (≥5× = outlier, ≥20× = priority) — raw
  play-count alone is misleading. S2 (Discover & Rank, Part 2) always scrapes each surfaced winner's own account for the median.
- Actor input keys are exact: reels/profiles use `apify/instagram-reel-scraper` (`username` array,
  `resultsLimit`, `skipPinnedPosts`); niche search is `data-slayer/instagram-search-reels`
  (`query`+`maxPages`, ~12 reels/page).
- `get-dataset-items`: fetch full items and `omit` bulky blocks; never `fields=` on nested arrays (it
  silently drops them). Search-actor items are huge — always project with `fields=`.
- **Decode-actor status (live-verified 2026-07; S3 carries a DECODE-ACTOR HEALTH probe for exactly this):**
  - **Transcription default = `apple_yang/instagram-transcripts-scraper`** — input
    `{ "videoUrl": "https://www.instagram.com/reel/<shortCode>/" }` (the reel *page* URL, not the CDN
    `videoUrl`). Proven live: multilingual incl. Hinglish→Hindi, timestamped `segments`, ~$0.002/reel,
    ~99% success. Whisper `donjuan_mime/audio-video-to-text` (`source_url` = CDN URL, `model:"small"`)
    is now a **paid fallback only** — its free trial expired live ("you must rent a paid Actor").
  - **Visual/overlay layer is best-effort:** `grizzlygriff/video-llm-analyzer` (`framesToExtract` 4–6 to
    avoid a 413) is the *only* multimodal frame analyzer in the Apify Store and is flaky (~68% success,
    recurring server-side HTTPStatusError). Retry once, then mark VISUAL/OVERLAY "unavailable" and proceed
    on VERBAL+PACKAGING. Higgsfield `video_analysis`/`media_import_url` are **not callable by those names**
    through the current connector — treat as absent (they appear in older docs as a 0-credit fallback).
  - Never fabricate a missing layer from the caption/topic; if the verbal engine is *also* down, S3
    STOPs and reports which actor needs rental/replacement.
- Higgsfield *generation* (Seedance/Kling/Nano-Banana) spends credits; the Decoder never generates —
  storyboards are emitted as image-gen prompts the operator renders externally.

## Phase-gate workflow (read before doing project work)

This is a **gated build** governed by `KICKOFF_PROMPT.md` (process) + `BLUEPRINT.md` (methodology). The
rule is strict: do the numbered phase, end it with a QC pass by **blind fresh-eyes subagents** (given
the artifact + the relevant spec, NOT your reasoning), present a review package, then **STOP and wait
for the owner's explicit approval** before the next phase. Never start two phases in one turn. Commit at
each gate; push only after approval. **Status: shipped and live** — Phases 0–7 (brief → PPC-Guru
end-to-end run → deploy), then the 8→5-step condense, the autonomous Claude-Code mode (QC-calibrated
grader + storyboard deliverables), and a supervised live run that validated scrape/rank and hardened the
decode-actor layer. Further work is maintenance/v2 (see README roadmap + `RESUME.md`). Keep the gate
discipline for any substantial new phase.

Cost guardrail for any phase that scrapes: ask the owner before a run exceeds ~$3 total / $5 per run /
1,500 items, and report actual spend.

## Document map

- `BLUEPRINT.md` — methodology (Swipe Test, outlier math, the decode-stage definitions, the operational traps). Source of truth for *what the prompts must do*.
- `KICKOFF_PROMPT.md` — the phase plan and gate/QC rules.
- `PROJECT_BRIEF.md` — pilot client (PPC Guru) facts + verified environment inventory.
- `VALIDATION_REPORT.md` — proven actor names/input-keys/costs (Phase 1, real data).
- `ARCHITECTURE.md` — the dashboard design spec (intake fields, S1–S5 spec, vault map).
- `PROMPTS.md` — **canonical** templates: S1–S5 + `## ORCHESTRATOR` + `## S6`. `SAMPLE_PROMPTS_PPCGURU.md` — a rendered pilot sample (legacy 8-step; illustrative only).
- `RESUME.md` — the session-handoff note: current status, live-run findings, open items. Read it after this file.
- `index.html` — the app. `inject_prompts.py` / `selftest.mjs` — build + test helpers (not shipped to the operator).
- `PPC_GURU_FINAL_REPORT.md/.html/.pdf` + `make_report_pdf.py` — the pilot deliverable and its branded-PDF generator (fpdf2; stubs the sandbox's broken `cryptography` import).
- `README.md` — operator quick-start + troubleshooting + cost notes + v2 roadmap. (The Drive "vault" with
  the PPC-Guru `s1`–`s8b` decode/scripts/report lives in Google Drive, not the repo.)

## Git & deploy

`main` is **production**: the repo is connected to Vercel, which **auto-deploys `index.html` on every push
to `main`**. Develop on a feature branch, open a PR, then **merge to `main` to ship** (that triggers the
deploy — there is no separate deploy step).

**Deploy-author gotcha (cost three blocked releases — read this):** Vercel **BLOCKs** a production
deployment when the `main` commit's GitHub author is `contact576` (not a linked Vercel contributor), but
deploys commits authored by "Claude" fine. A **squash merge re-attributes the commit to `contact576` →
BLOCKED**; a **rebase merge preserves the Claude author → deploys clean**. So: rebase-merge PRs, or fix it
permanently by adding `contact576` as a Vercel team member (else click Redeploy on the blocked deployment).
Verify deploys via the Vercel MCP tools (`list_deployments` — the newest `target:"production"` entry must be
`READY`, not `BLOCKED`) or the Vercel dashboard; a stale browser cache also hides fresh deploys, so
hard-refresh before concluding a deploy "didn't work".
