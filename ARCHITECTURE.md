# ARCHITECTURE — SMM Virality Decoder (Phase 2, plan only)

> Phase 2 output. Plan only — **no UI is built in this phase.** Pairs with `BLUEPRINT.md`
> (methodology), `PROJECT_BRIEF.md` (pilot facts), `VALIDATION_REPORT.md` (proven actors/fields/costs).
> Every component below traces to a blueprint section or a brief decision; scope-creep is called out as
> OUT in §7. Status: **awaiting GATE 2.**

## 0. Design rules (non-negotiable, from BLUEPRINT §6)
- **One file, no build, no CDN, no network calls.** `index.html` is a pure *prompt generator +
  beautifier*. It holds **zero API keys** and never calls Apify/Higgsfield/Drive itself — the
  **operator** runs the generated prompts in a Claude chat that has those connectors. This keeps the
  tool employee-safe and deployable as a static page.
- **No silent drops, anywhere.** Placeholder reconciler (load-time), per-prompt pre-flight, and the
  beautifier's generic-fallback renderer all exist to make "content silently disappeared" impossible.
- **Graceful degradation is printed, not hidden.** Missing Higgsfield/Drive/Whisper → the prompt says
  so in its own output ("visual layer skipped…"), never pretends.

## 1. File structure
```
index.html        # the whole tool: Intake tab · Prompt-Chain tab (S1–S5) · Beautifier tab · Diagnostics
README.md         # operator quick-start, troubleshooting, costs, v2 roadmap (Phase 7)
BLUEPRINT.md      # methodology (exists)
PROJECT_BRIEF.md  # pilot facts (exists)
VALIDATION_REPORT.md  # proven actors/fields/costs (exists)
ARCHITECTURE.md   # this file
```
The Research Vault lives in **Google Drive**, not the repo: `SMM Virality Vault / <CLIENT> / s*.md`.

## 2. Intake form (19 fields → placeholder keys)
Placeholder convention: **`{{UPPER_SNAKE_CASE}}`** (double brace). One canonical JS array `FIELD_KEYS`
is the single source of truth; templates may only reference keys in `FIELD_KEYS` ∪ `DERIVED_KEYS`.

| # | Field (label) | Placeholder key | Req? | Validation rule |
|---|---|---|---|---|
| 1 | Client name | `{{CLIENT_NAME}}` | ✅ | non-empty |
| 2 | Client IG handle | `{{CLIENT_HANDLE}}` | ⬜ | empty (new client) or `^[A-Za-z0-9._]{1,30}$` after stripping `@` |
| 3 | Client website | `{{CLIENT_WEBSITE}}` | ⬜ | empty or URL-ish |
| 4 | Niche | `{{NICHE}}` | ✅ | non-empty |
| 5 | Services (priority order) | `{{SERVICES}}` | ✅ | ≥1 line |
| 6 | ICP (who the buyer is) | `{{ICP}}` | ✅ | non-empty |
| 7 | Geo — main area | `{{GEO_PRIMARY}}` | ✅ | non-empty |
| 8 | Language — primary | `{{LANGUAGE_PRIMARY}}` | ✅ | default "English" |
| 9 | Language — secondary/hooks | `{{LANGUAGE_SECONDARY}}` | ⬜ | — |
| 10 | **Niche search keywords** | `{{NICHE_KEYWORDS}}` | ✅ | **≥3 lines** (keystone of discovery) |
| 11 | Niche hashtags | `{{NICHE_HASHTAGS}}` | ⬜ | each line `#?[\w.]+` |
| 12 | Adjacent-niche keywords | `{{ADJACENT_KEYWORDS}}` | ✅ | ≥1 line (transplant seeds) |
| 13 | Known competitor handles | `{{COMPETITOR_HANDLES}}` | ⬜ | each line a valid handle (force-include seeds) |
| 14 | No-go topics (hard bans) | `{{NO_GO_TOPICS}}` | ✅ | non-empty |
| 15 | Posting capacity | `{{POSTING_CAPACITY}}` | ✅ | non-empty (reels/wk + who films) |
| 16 | Production modes | `{{PRODUCTION_MODES}}` | ✅ | non-empty (phone / AI-avatar / designer) — feeds S4's mandatory effort tag |
| 17 | Primary CTA | `{{CTA_PRIMARY}}` | ✅ | non-empty |
| 18 | Additional notes (catch-all) | `{{ADDITIONAL_NOTES}}` | ⬜ | — (brand voice, proof, pillars, constraints — consumed by S1/S4) |
| 19 | Vault folder | `{{VAULT_FOLDER}}` | ✅ | default `<CLIENT_NAME> — SMM Virality Vault` (auto-named from client name) |

**Every field has a downstream consumer** — see the §4 step inputs; the reconciler (§3) flags any field
that becomes a dead key. Owner-directed simplification (post-Phase-4) removed `GEO_WIDER`, `BRAND_VOICE`,
`PROOF_ASSETS`, `CONTENT_PILLARS`, and `CALENDAR_START_DATE`; their intent is now covered by the single
**`ADDITIONAL_NOTES`** catch-all (voice/proof/pillars) and by `CURRENT_DATE` (the calendar starts the
next Monday on/after it). Earlier-removed: `BASELINE_WINDOW` (hard-coded "50–90" in S1) and `OPERATOR_NAME`.

**New/thin-account handling (owner-directed):** `CLIENT_HANDLE` is **optional** — new clients often have
no account yet. S1 branches on it: *ESTABLISHED* (handle + ≥10 reels) computes the baseline median;
*NEW/THIN* (no handle, or <10 reels) sets baseline = N/A and infers a RECOMMENDED voice. Discovery/decode/
scripts (S2–S4) never use the client's own content, so they are unaffected. S5's learning loop is guarded
by `[[IF CLIENT_HANDLE]]` and prints "not yet active" when there is no account.

`DERIVED_KEYS` (computed, never user-entered, must be known to the reconciler so they aren't flagged
as orphans): `{{CURRENT_DATE}}`. (The vault path is written literally as `{{VAULT_FOLDER}}/<step-file>`
in each template, so no separate path/slug key is needed — keeps the canonical set free of dead keys.)

**Conditional sections** (for optional fields): `[[IF KEY]] … [[ENDIF]]` blocks are stripped when the
key is empty, so e.g. the competitor-handles instruction vanishes cleanly when none are given. The
reconciler and pre-flight both understand `[[IF]]`/`[[ENDIF]]`.

## 3. Reconciler / pre-flight / Diagnostics (BLUEPRINT §6.2 — the bug-killers)
- **Load-time reconciler.** On page load, regex every `RAW_PROMPTS` template for `{{…}}` and `[[IF …]]`
  tokens → compare to `FIELD_KEYS ∪ DERIVED_KEYS`. Emits two lists: **ORPHANS** (token used in a
  template but no matching key → would inject literally = the bug class we are killing) and **DEAD
  KEYS** (field defined but never referenced → harmless, flagged). **Any orphan blocks generation** and
  shows a red banner. This is the byte-for-byte guard.
- **Per-prompt pre-flight.** After replacement, scan the produced prompt for any residual `{{`, `}}`,
  `[[`, `]]`. If found → the Copy button is disabled and the leftover token is shown. Guarantees zero
  injectable placeholders ever reach the operator.
- **Diagnostics self-test button.** Loads a built-in `TEST_CLIENT` fixture (PPC Guru data from the
  brief), generates S1–S5, and asserts: (a) reconciler clean, (b) all 5 prompts pass pre-flight,
  (c) all 8 non-empty, (d) every Copy button wired, (e) required-field validation fires on a blank
  fixture. Prints PASS/FAIL per check. This is the "is the tool healthy?" button for the operator.

## 3a. Operator-facing live-run safeguards (BLUEPRINT §6.5 employee-proofing + §3.2 traps)
The dashboard is keyless, so it cannot *enforce* the live MCP run — but it must **inline-print** the
traps into each relevant prompt and into a sticky help panel, so a moderate-tech operator can't fall in
silently. Required safeguards, each surfaced where it bites:
- **S4 — same-session / expired URL:** S4's header states "run scrape→transcribe→visual in ONE chat
  session; IG CDN URLs die in hours — if a `videoUrl` 403s, re-scrape that reel first." (Proven in
  VALIDATION; expiry is the #1 silent S4 failure.)
- **S4 — engine selection is not a guess:** the prompt instructs "if the reel is non-English / music /
  text-on-screen, use Higgsfield `video_analysis` (it transcribes **and** translates); do NOT trust
  Whisper `base` auto-detect — it hallucinates plausible garbage (VALIDATION §3). Always print which
  engine produced the verbal layer; if there is no speech, say so — never fabricate."
- **S4 — `media_import_url` first:** numbered sub-steps for Higgsfield: (1) `media_import_url` the
  reel's CDN URL → get `media_id`; (2) `video_analysis_create` with that id; (3) poll `_status`. Never
  pass a raw URL into `params`.
- **S2 — per-keyword runs:** the prompt explicitly says "run the search actor once **per keyword** (up
  to ~10 runs); pool the datasets" so the operator expects multiple invocations.
- **Rental-actor permission wall (§3.2 trap #2):** a sticky help line — "if an actor returns an
  *approve-permissions* error, copy the link to Vihar/owner to click once in the Apify console, then
  re-run." (Whisper is already rented; this covers any new actor.)
- **Nested-array projection (§3.2 trap #3):** S2/S3/S4 prompts instruct `get-dataset-items` to **fetch
  full items and `omit` bulky blocks**, never `fields=` on nested arrays (silently drops them).
- **Vault-save verification:** every S2–S5 LOAD header tells the operator to **confirm the prior file
  exists in the vault before proceeding**; if the Drive connector is absent, the SAVE footer's manual
  paste-and-save instructions (`[[IF no Drive]]`) are followed instead. (Reconciler/pre-flight guard
  placeholders, not vault contents — this human check covers the gap.)

These live in the **prompt text + a collapsible "Before you run" help panel per step** (Phase 4 build),
and are exactly what the Phase-3 operational-trap auditor and the usability subagent verify.

## 4. The S1–S5 prompt chain (8 logical stages fused into 5 prompts; full text in `PROMPTS.md`)
Every step: terse in-chat output + a **vault SAVE footer** (the three merged steps save TWO files each);
S2–S5 begin with a **vault LOAD header**. Actor names/fields are the ones **proven in
`VALIDATION_REPORT.md`**. Step numbers (5) and vault-file numbers (s1–s8) intentionally differ — see §5.

- **S1 — Client Baseline.** In: `CLIENT_HANDLE?, CLIENT_WEBSITE?, NICHE, ICP, SERVICES, GEO_PRIMARY,
  LANGUAGE_PRIMARY, NO_GO_TOPICS, ADDITIONAL_NOTES?`. **Branches on MODE:** *ESTABLISHED* (handle present
  + ≥10 reels) → MCP `apify/instagram-reel-scraper` → **baseline median plays**, engagement, top/bottom-5,
  formats, cadence, follower quality, voice; *NEW/THIN* → baseline "N/A", RECOMMENDED voice inferred. The
  scrape is wrapped in `[[IF CLIENT_HANDLE]]`. SAVE `s1-baseline.md`.
- **S2 — Discover & Rank** *(fuses old discovery + outlier harvest)*. LOAD `s1?`. **PART 1 (discovery):**
  MCP `data-slayer/instagram-search-reels` per keyword + a mandatory hashtag leg + an adjacent leg
  (`[[IF COMPETITOR_HANDLES]]` seed leg) → candidate pool → mechanical kills
  (inactive/aggregator/wrong-geo/botted/guru) → classify **EXACT/ADJACENT/MACRO** + **record each
  survivor's ORIGIN (geo+language)** → funnel counts. **PART 2 (ranking):** `apify/instagram-reel-scraper`
  on each surfaced winner's OWN account → `outlier = plays ÷ account_median` (≥5×/≥20×), report actual n,
  consistency-winner flags; select top 20–25 (≥15 EXACT/≥5 ADJACENT/≤3 MACRO). Ranked table carries an
  **origin (geo/lang) column**. Has a **scrape COST GUARDRAIL**. SAVE `s2-discovery.md` + `s3-outliers.md`.
- **S3 — Decode & Synthesize** *(fuses old decode + pattern synthesis)*. LOAD `s3-outliers, s2, s1`.
  **Same-session** (CDN URLs expire — see §3a). **PART 1 (decode, per reel):** VERBAL
  `donjuan_mime/audio-video-to-text` (`source_url`, `model:small`; non-English → Higgsfield
  `video_analysis`, transcribes+translates); VISUAL (top 10–12) Higgsfield `video_analysis` +
  `grizzlygriff/video-llm-analyzer` (overlay text, `framesToExtract 4–6`); OVERLAY + PACKAGING; tag
  §2.3+§2.4 **+ ORIGIN**, card IDs. **PART 2 (synthesis):** **GEO/LANGUAGE SKEW CHECK** first, then hook
  bank (verbal/visual/overlay separated), format distribution, length sweet spot, audio strategy, share
  triggers, transplant map, **THE GAP**. SAVE `s4-decode.md` + `s5-patterns.md`.
- **S4 — Plan & Script** *(fuses old calendar + scripts)*. LOAD `s1, s4-decode, s5-patterns`. In:
  `POSTING_CAPACITY, PRODUCTION_MODES, CTA_PRIMARY, NO_GO_TOPICS, ADDITIONAL_NOTES?` + `CURRENT_DATE`.
  **PART 1 (calendar):** derive 3–5 pillars; **40/40/20** Reach/Nurture/Convert, cadence ≤3/wk, CONVERT
  slots use proof or flag "needs a proof asset". **PART 2 (scripts):** **COVERAGE RULE — one script per
  slot, ends with COVERAGE CHECK (X/N)**; each reel a **two-column shooting script**
  (`TIME | AUDIO (HEAR) | VISUAL & TEXT (SEE & READ)`), first row = all three hooks, footer **HOOK · CTA ·
  WHY IT'LL GO VIRAL** + caption/hashtags/audio/length; gates (swipe, overlay≠verbal, account-swap,
  share-trigger, card-ID traceability, no-go). SAVE `s6-calendar.md` + `s7-scripts.md`.
- **S5 — Showcase Report + Learning Loop** *(old S8)*. LOAD all seven `s1…s7` by exact filename
  (**s2-discovery + s3-outliers non-negotiable** — STOP if missing). (a) client report that **shows the
  research**: HOW WE RESEARCHED IT (funnel + 3-layer decode method & tools), ACCOUNTS WE DECODED (with
  **origin** + any GEO-SKEW flag), niche insights, strategy + full calendar, **every s7 script in
  two-column format (1:1, COVERAGE line)** → feeds the Beautifier. (b) **monthly re-run:** scrape client's
  last-30-days, outlier-score vs S1 baseline, keep/kill/double-down, feed next month's S4. SAVE
  `s8-report.md` + `s8b-learning-loop.md`.

## 5. Research Vault map + load matrix
`SMM Virality Vault / <CLIENT> /` → `s1-baseline.md · s2-discovery.md · s3-outliers.md · s4-decode.md ·
s5-patterns.md · s6-calendar.md · s7-scripts.md · s8-report.md · s8b-learning-loop.md` (9 files from 5 steps).

| Step | LOADs | SAVEs |
|---|---|---|
| S1 — Client Baseline | — | s1-baseline |
| S2 — Discover & Rank | (s1 optional) | s2-discovery, s3-outliers |
| S3 — Decode & Synthesize | s3-outliers, s2, s1 | s4-decode, s5-patterns |
| S4 — Plan & Script | s1, s4-decode, s5-patterns | s6-calendar, s7-scripts |
| S5 — Showcase + Loop | s1…s7 | s8-report, s8b-learning-loop |

Every SAVE footer also prints **manual-save instructions** (`[[IF no Drive]]`) so the chain works even
without the Drive connector.

## 6. Beautifier scope (v1)
- **In:** paste the S5 report markdown (also handles the S4 calendar / two-column script tables).
- **Out:** branded HTML — cover, sections, **KPI cards**, **simple inline SVG charts** (funnel counts,
  format-distribution bar, outlier scatter), **calendar table**, **two-column shooting-script tables**
  (`TIME | AUDIO | VISUAL & TEXT`, rendered by the standard table path) + their Hook/CTA/Why footers;
  print-to-PDF clean.
- **House style (BLUEPRINT §6.4):** Instrument Serif/Sans + JetBrains Mono via a **system-font fallback
  stack** (no CDN; web-fonts optional and degrade gracefully), paper/ink surfaces, burnt-orange
  **`#C2410C`** accent.
- **No-silent-drop (critical):** the markdown→HTML renderer routes unknown blocks to a **generic
  renderer** (styled raw container), never drops them. A **`blocksParsed === blocksRendered`** assertion
  shows a visible warning on mismatch. Phase-5 QC renders deliberately-unknown markdown to prove it.

## 7. Explicitly OUT of v1 (BLUEPRINT §9 + brief)
Auto-posting/scheduling · YouTube Shorts · comment-sentiment mining · influencer-outreach lists · paid
amplification bridge to the ads tool · multi-client trend dashboard · **the dashboard calling
connectors directly** (operator runs prompts; tool stays keyless/static) · **`virality_predictor`**
(parked for AI-avatar draft QC in production, not research).

## 8. Build sequence (Phases 3–5) + session estimate
- **Phase 3 — write the 8 prompt templates** (full text + embedded methodology + vault headers/footers
  + graceful-degradation notes) and run the **4 parallel blind QC auditors** (placeholder /
  methodology / operational-trap / lazy-strategist red-team); fix until clean. **Est. 2–3 sessions.**
- **Phase 4 — build `index.html`** (intake form → assembly → reconciler → pre-flight → Diagnostics +
  TEST_CLIENT) + code-review & usability QC. **Est. 2 sessions.**
- **Phase 5 — Beautifier + final wiring** + unknown-block QC. **Est. 1–2 sessions.**
- Then Phase 6 (real end-to-end run) and Phase 7 (Vercel deploy + handoff), each its own gate.
**Total to shippable v1: ~5–7 working sessions.**

## 9. Verification (how GATE 2 is judged)
Architecture-review QC subagent (fresh-eyes, given this file + BLUEPRINT.md, **not** my reasoning)
confirms: every blueprint requirement maps to a component; nothing here is untraceable scope creep;
flags where a moderate-tech-comfort operator (Vanshika) would get confused. Findings fixed, then owner
reviews at GATE 2.
