# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A **single-file, keyless, static web app** (`index.html`) — the "SMM Virality Decoder". It turns an
intake form into five copy-paste prompts (S1–S5) that an operator runs in a *separate* Claude chat
that has the Apify / Higgsfield / Google Drive connectors. (The chain was condensed from eight steps to
five by fusing tightly-coupled stages — discovery+ranking, decode+synthesis, calendar+scripts — so the
operator pastes fewer times; the same nine vault files are still produced.) The dashboard itself makes **no network
calls, holds no API keys, and has no build step** — it only generates text. The actual scraping/decode
happens when a human pastes the generated prompts into a connected chat. Keep that boundary: do not add
fetch/API calls or a bundler to `index.html`.

**Two run modes (a toggle on the Intake tab, `localStorage.smm_mode`, default `chat`):**
- **Claude chat** — the default: emits the **five** copy-paste prompts (S1–S5), pasted one-by-one.
- **Claude Code** — emits **one** "auto-run" prompt (the **ORCHESTRATOR** template) the operator pastes into a
  Claude Code session; it runs the whole S1→S5 pipeline autonomously (maker→blind-checker at each gate, a
  bounded regenerate ladder, a virality grader that loops scripts to ≥90 / ≥85 for CONVERT, a self-capping
  Apify budget, then the **S6** deliverables: an 8–10 frame storyboard emitted as image-gen *prompts* — no
  images generated, zero credits — plus a designer doc and optional generation prompts). The dashboard still
  only generates text; the autonomy happens in the connected Claude Code session.

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
`ADDITIONAL_NOTES` catch-all field carries voice/proof/pillars (older per-topic fields were removed). S5's
learning loop is guarded by `[[IF CLIENT_HANDLE]]`.

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
node selftest.mjs          # engine + reconciler + PROMPTS.md parity + validation + beautifier (~45 checks, no deps)
python3 inject_prompts.py  # re-embed templates into index.html after editing PROMPTS.md
```

DOM-level render test (catches UI-wiring bugs) needs jsdom, which is not vendored:
```bash
cd /tmp && mkdir -p jsdomtest && (cd jsdomtest && npm install jsdom --no-save)
# then run a JSDOM script that loads index.html with runScripts:'dangerously' and drives the buttons,
# resolving jsdom via createRequire('/tmp/jsdomtest/x.js')
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
- Actor input keys are exact: transcription `donjuan_mime/audio-video-to-text` uses **`source_url`**
  (fed by the scraper's `videoUrl` output) with `model:"small"` (not `base`); reels/profiles use
  `apify/instagram-reel-scraper` (`username` array, `resultsLimit`, `skipPinnedPosts`); visual layer is
  Higgsfield `video_analysis` (call `media_import_url` first) + `grizzlygriff/video-llm-analyzer`
  (`framesToExtract` 4–6 to avoid a 413). Non-English/music reels route to Higgsfield, which translates.
- `get-dataset-items`: fetch full items and `omit` bulky blocks; never `fields=` on nested arrays (it
  silently drops them).
- **Whisper's free trial can expire** ("you must rent a paid Actor"); the chain falls back to Higgsfield
  `video_analysis`, which transcribes **and** translates. Verified during the Phase 6 run.
- **Higgsfield `video_analysis` / `media_import_url` cost 0 credits** (confirmed against an unchanged
  balance + empty transaction log). Only Higgsfield *generation* (Seedance/Kling/Nano-Banana) spends
  credits; the Decoder never generates. The `grizzlygriff` Gemini actor runs in `analysisMode:"frames"`
  (images only) — it does NOT transcribe audio; use Higgsfield or Whisper for the spoken track.

## Phase-gate workflow (read before doing project work)

This is a **gated build** governed by `KICKOFF_PROMPT.md` (process) + `BLUEPRINT.md` (methodology). The
rule is strict: do the numbered phase, end it with a QC pass by **blind fresh-eyes subagents** (given
the artifact + the relevant spec, NOT your reasoning), present a review package, then **STOP and wait
for the owner's explicit approval** before the next phase. Never start two phases in one turn. Commit at
each gate; push only after approval. **Status: Phases 0–7 complete** — brief, live validation,
architecture, prompt chain, dashboard, Beautifier, a real PPC-Guru end-to-end run, README + Vercel
deploy. The build is shipped; further work is maintenance/v2 (see README roadmap). Keep the gate
discipline for any substantial new phase.

Cost guardrail for any phase that scrapes: ask the owner before a run exceeds ~$3 total / $5 per run /
1,500 items, and report actual spend.

## Document map

- `BLUEPRINT.md` — methodology (Swipe Test, outlier math, the decode-stage definitions, the operational traps). Source of truth for *what the prompts must do*.
- `KICKOFF_PROMPT.md` — the phase plan and gate/QC rules.
- `PROJECT_BRIEF.md` — pilot client (PPC Guru) facts + verified environment inventory.
- `VALIDATION_REPORT.md` — proven actor names/input-keys/costs (Phase 1, real data).
- `ARCHITECTURE.md` — the dashboard design spec (intake fields, S1–S5 spec, vault map).
- `PROMPTS.md` — **canonical** S1–S5 templates. `SAMPLE_PROMPTS_PPCGURU.md` — a rendered pilot sample (legacy 8-step; illustrative only).
- `index.html` — the app. `inject_prompts.py` / `selftest.mjs` — build + test helpers (not shipped to the operator).
- `README.md` — operator quick-start + troubleshooting + cost notes + v2 roadmap. (The Drive "vault" with
  the PPC-Guru `s1`–`s8b` decode/scripts/report lives in Google Drive, not the repo.)

## Git & deploy

`main` is **production**: the repo is connected to Vercel, which **auto-deploys `index.html` on every push
to `main`**. Develop on a feature branch, open a PR, then **merge to `main` to ship** (that triggers the
deploy — there is no separate deploy step). This sandbox's network policy blocks `vercel.app`, so the live
URL can't be fetched from here; verify deploys from the Vercel dashboard / a real browser.
