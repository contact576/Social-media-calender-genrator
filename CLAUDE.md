# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A **single-file, keyless, static web app** (`index.html`) — the "SMM Virality Decoder". It turns an
intake form into eight copy-paste prompts (S1–S8) that an operator runs in a *separate* Claude chat
that has the Apify / Higgsfield / Google Drive connectors. The dashboard itself makes **no network
calls, holds no API keys, and has no build step** — it only generates text. The actual scraping/decode
happens when a human pastes the generated prompts into a connected chat. Keep that boundary: do not add
fetch/API calls or a bundler to `index.html`.

## The one architecture rule that matters: PROMPTS.md is the source of truth

The eight prompt templates live in **`PROMPTS.md`** (canonical). They are embedded into `index.html`
inside `<script type="text/plain" class="raw-prompt" data-step="S#">` blocks by a generator.

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
`['S1'..'S8']` array anywhere.

## Verify after every change

```bash
node selftest.mjs          # engine + reconciler + PROMPTS.md parity + validation (28 checks, no deps)
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
  play-count alone is misleading. S3 always scrapes each surfaced winner's own account for the median.
- Actor input keys are exact: transcription `donjuan_mime/audio-video-to-text` uses **`source_url`**
  (fed by the scraper's `videoUrl` output) with `model:"small"` (not `base`); reels/profiles use
  `apify/instagram-reel-scraper` (`username` array, `resultsLimit`, `skipPinnedPosts`); visual layer is
  Higgsfield `video_analysis` (call `media_import_url` first) + `grizzlygriff/video-llm-analyzer`
  (`framesToExtract` 4–6 to avoid a 413). Non-English/music reels route to Higgsfield, which translates.
- `get-dataset-items`: fetch full items and `omit` bulky blocks; never `fields=` on nested arrays (it
  silently drops them).

## Phase-gate workflow (read before doing project work)

This is a **gated build** governed by `KICKOFF_PROMPT.md` (process) + `BLUEPRINT.md` (methodology). The
rule is strict: do the numbered phase, end it with a QC pass by **blind fresh-eyes subagents** (given
the artifact + the relevant spec, NOT your reasoning), present a review package, then **STOP and wait
for the owner's explicit approval** before the next phase. Never start two phases in one turn. Commit at
each gate; push only after approval. Status so far: Phases 0–4 complete (brief, live validation,
architecture, prompt chain, dashboard). **Phase 5 = the Beautifier** (paste S8 markdown → branded
printable HTML, with a generic fallback renderer so unknown blocks never silently vanish) is next.

Cost guardrail for any phase that scrapes: ask the owner before a run exceeds ~$3 total / $5 per run /
1,500 items, and report actual spend.

## Document map

- `BLUEPRINT.md` — methodology (Swipe Test, outlier math, S1–S8 definitions, the operational traps). Source of truth for *what the prompts must do*.
- `KICKOFF_PROMPT.md` — the phase plan and gate/QC rules.
- `PROJECT_BRIEF.md` — pilot client (PPC Guru) facts + verified environment inventory.
- `VALIDATION_REPORT.md` — proven actor names/input-keys/costs (Phase 1, real data).
- `ARCHITECTURE.md` — the dashboard design spec (intake fields, S1–S8 spec, vault map).
- `PROMPTS.md` — **canonical** S1–S8 templates. `SAMPLE_PROMPTS_PPCGURU.md` — the same rendered for the pilot.
- `index.html` — the app. `inject_prompts.py` / `selftest.mjs` — build + test helpers (not shipped to the operator).

## Git

Develop on branch `claude/gallant-lamport-8u6hlo`; push with `git push -u origin <branch>` and open/keep
a draft PR. Commit messages are scoped per phase (e.g. "Phase 4: …").
