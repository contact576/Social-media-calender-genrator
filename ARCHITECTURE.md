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
index.html        # the whole tool: Intake tab · Prompt-Chain tab (S1–S8) · Beautifier tab · Diagnostics
README.md         # operator quick-start, troubleshooting, costs, v2 roadmap (Phase 7)
BLUEPRINT.md      # methodology (exists)
PROJECT_BRIEF.md  # pilot facts (exists)
VALIDATION_REPORT.md  # proven actors/fields/costs (exists)
ARCHITECTURE.md   # this file
```
The Research Vault lives in **Google Drive**, not the repo: `SMM Virality Vault / <CLIENT> / s*.md`.

## 2. Intake form (the ~25 fields → placeholder keys)
Placeholder convention: **`{{UPPER_SNAKE_CASE}}`** (double brace). One canonical JS array `FIELD_KEYS`
is the single source of truth; templates may only reference keys in `FIELD_KEYS` ∪ `DERIVED_KEYS`.

| # | Field (label) | Placeholder key | Req? | Validation rule |
|---|---|---|---|---|
| 1 | Client name | `{{CLIENT_NAME}}` | ✅ | non-empty |
| 2 | Client IG handle | `{{CLIENT_HANDLE}}` | ✅ | strip leading `@`; `^[A-Za-z0-9._]{1,30}$` |
| 3 | Client website | `{{CLIENT_WEBSITE}}` | ⬜ | empty or URL-ish |
| 4 | Niche | `{{NICHE}}` | ✅ | non-empty |
| 5 | Services (priority order) | `{{SERVICES}}` | ✅ | ≥1 line |
| 6 | ICP (who the buyer is) | `{{ICP}}` | ✅ | non-empty |
| 7 | Geo — primary | `{{GEO_PRIMARY}}` | ✅ | non-empty |
| 8 | Geo — wider | `{{GEO_WIDER}}` | ⬜ | — |
| 9 | Language — primary | `{{LANGUAGE_PRIMARY}}` | ✅ | default "English" |
| 10 | Language — secondary/hooks | `{{LANGUAGE_SECONDARY}}` | ⬜ | — |
| 11 | **Niche search keywords** | `{{NICHE_KEYWORDS}}` | ✅ | **≥3 lines** (keystone of discovery) |
| 12 | Niche hashtags | `{{NICHE_HASHTAGS}}` | ⬜ | each line `#?[\w.]+` |
| 13 | Adjacent-niche keywords | `{{ADJACENT_KEYWORDS}}` | ✅ | ≥1 line (transplant seeds) |
| 14 | Known competitor handles | `{{COMPETITOR_HANDLES}}` | ⬜ | each line a valid handle (force-include seeds) |
| 15 | Brand voice (3 adjectives) | `{{BRAND_VOICE}}` | ✅ | non-empty |
| 16 | No-go topics (hard bans) | `{{NO_GO_TOPICS}}` | ✅ | non-empty |
| 17 | Proof assets (owned results) | `{{PROOF_ASSETS}}` | ⬜ | — |
| 18 | Content pillars | `{{CONTENT_PILLARS}}` | ✅ | ≥1 line |
| 19 | Posting capacity | `{{POSTING_CAPACITY}}` | ✅ | non-empty (reels/wk + who films) |
| 20 | Production modes | `{{PRODUCTION_MODES}}` | ✅ | non-empty (phone / AI-avatar / designer) — feeds S6's mandatory effort tag |
| 21 | Primary CTA | `{{CTA_PRIMARY}}` | ✅ | non-empty |
| 22 | Calendar start date | `{{CALENDAR_START_DATE}}` | ✅ | valid date |
| 23 | Vault folder | `{{VAULT_FOLDER}}` | ✅ | default `<CLIENT_NAME> — SMM Virality Vault` |

23 visible fields ("~25" target met). **Every field has a downstream consumer** — see the §4 step
inputs; the reconciler (§3) flags any field that becomes a dead key. Two fields the first QC caught as
unsourced/unused were removed: `BASELINE_WINDOW` (now hard-coded "50–90" inside S1, not an operator
knob) and `OPERATOR_NAME` (no consumer). `PROOF_ASSETS` (field 17) is wired into S6/S7 below.

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
  brief), generates S1–S8, and asserts: (a) reconciler clean, (b) all 8 prompts pass pre-flight,
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
- **Vault-save verification:** every S3–S8 LOAD header tells the operator to **confirm the prior file
  exists in the vault before proceeding**; if the Drive connector is absent, the SAVE footer's manual
  paste-and-save instructions (`[[IF no Drive]]`) are followed instead. (Reconciler/pre-flight guard
  placeholders, not vault contents — this human check covers the gap.)

These live in the **prompt text + a collapsible "Before you run" help panel per step** (Phase 4 build),
and are exactly what the Phase-3 operational-trap auditor and the usability subagent verify.

## 4. The S1–S8 prompt chain (design spec; full text is Phase 3)
Every step: terse in-chat output + a **vault SAVE footer**; S3–S8 also begin with a **vault LOAD
header**. Actor names/fields are the ones **proven in `VALIDATION_REPORT.md`**.

- **S1 — Client Baseline.** In: `CLIENT_HANDLE, CLIENT_WEBSITE, NICHE, ICP, SERVICES, GEO_*, BRAND_VOICE,
  NO_GO_TOPICS` (`CLIENT_WEBSITE` = brand/offer context + the destination CTAs ultimately drive to). MCP: `apify/instagram-reel-scraper` (`username=[CLIENT_HANDLE]`, `resultsLimit=50–90`
  hard-coded in prompt, `skipPinnedPosts=true`). Out: **baseline median plays**, engagement rate, top-5/bottom-5 + why,
  formats, cadence, follower quality, voice extracted from captions. Cap ≤90. Fallback: <10 reels →
  "INSUFFICIENT DATA, baseline = plays/followers." SAVE `s1-baseline.md` + HANDOFF (≤30 lines).
- **S2 — Niche Discovery (keyword-first).** In: `NICHE_KEYWORDS, NICHE_HASHTAGS, ADJACENT_KEYWORDS,
  COMPETITOR_HANDLES?, GEO_*, LANGUAGE_*`. MCP: `data-slayer/instagram-search-reels` (one run per
  keyword, `maxPages` cap), optional hashtag scraper, `[[IF COMPETITOR_HANDLES]]` force-include via
  reel-scraper. Out: candidate pool → mechanical kills (inactive/aggregator/wrong-geo/botted/guru) →
  classify **EXACT/ADJACENT/MACRO** → **funnel counts reported**. Caps: ≤10 keywords, `maxPages` 1–2
  (~12–24 reels each), pool ≤~150. Fallback: a keyword returning 0 is reported, not fatal. SAVE
  `s2-discovery.md`.
- **S3 — Outlier Harvest.** LOAD `s2`. MCP: `apify/instagram-reel-scraper` on **each surfaced winner's
  OWN account** (`resultsLimit≥30, skipPinnedPosts=true`) → account median → `outlier =
  plays ÷ account_median` (fallback `plays ÷ followers`), **report actual n** (profiles paginate
  short). Out: ranked top 20–25 (≥15 EXACT, ≥5 ADJACENT, ≤3 MACRO), scores/links/plays/medians,
  **consistency-winner flags**. Thresholds ≥5× / ≥20×. SAVE `s3-outliers.md`.
- **S4 — Deep Decode (3 layers).** LOAD `s3`. **Same-session** (CDN URLs expire — see §3a). VERBAL:
  `donjuan_mime/audio-video-to-text` `{ source_url: <the reel-scraper `videoUrl`>, model:"small" }`
  (input key is **`source_url`**, fed by the scraper's `videoUrl` output — proven in VALIDATION §1c);
  non-English/music reel → Higgsfield
  `video_analysis` (import CDN URL via `media_import_url` first) which transcribes+translates; **state
  which engine, never fabricate**. VISUAL (top 10–12): Higgsfield `video_analysis` (scene/shot/audio,
  primary) + `grizzlygriff/video-llm-analyzer` (`gemini`, `framesToExtract:4–6`, `maxChargeUsd:0.1`) for
  **overlay text + first frame**. PACKAGING from reel-scraper fields (caption/hashtags/`musicInfo`/
  duration/timestamp). Out: one card/reel, taxonomy tags (§2.3+§2.4), **card IDs** for traceability.
  Caps: Whisper top 20–25, visual top 10–12. Fallbacks printed. SAVE `s4-decode.md`.
- **S5 — Pattern Synthesis & The Gap.** LOAD `s1–s4`. Out: hook bank (**verbal/visual/overlay
  separated**), format distribution (saturated vs absent), length sweet spot, audio strategy,
  share-trigger frequency, **transplant map** (adjacent format × client niche), **THE GAP**. SAVE
  `s5-patterns.md`.
- **S6 — Strategy + 30-Day Calendar.** LOAD `s1,s5`. In: `CONTENT_PILLARS, POSTING_CAPACITY,
  CALENDAR_START_DATE, PRODUCTION_MODES, CTA_PRIMARY, PROOF_ASSETS` (PROOF_ASSETS seeds the **20%
  CONVERT** slots — transformations/testimonials). Out: **40/40/20** calendar; per slot
  date/pillar/format/hook concept/topic/audio/CTA/production-effort tag. SAVE `s6-calendar.md`.
- **S7 — Viral Scripts.** LOAD `s4,s5,s6`. In (intake): `PROOF_ASSETS` (for the account-swap rewrite —
  inject the client's real proof/place/personality). Out per reel: **THREE hooks verbatim** (spoken /
  first-frame visual / overlay ≤8 words), beat-by-beat body w/ b-roll, payoff, CTA, caption
  (first-line hook + body + CTA), hashtags, audio, target length. **Quality gates:** swipe verdict per
  channel; **overlay ≠ verbal gate** (BLUEPRINT §2.1 — the overlay text must be a *second* message, not
  a caption of the spoken hook; reject if they duplicate); account-swap test (rewrite generic scripts
  with `PROOF_ASSETS`); share-trigger named; **S4 card-ID traceability**; divergent ideation (2–3
  candidates scored, winners output). SAVE `s7-scripts.md`.
- **S8 — Showcase Report + Learning Loop.** LOAD `s1–s7`. (a) client-facing report markdown (funnel
  counts, insights, strategy, calendar) → feeds the Beautifier. (b) **monthly re-run:** scrape client's
  own last-30-days, outlier-score vs S1 baseline, **keep/kill/double-down**, feed next month's S6.
  SAVE `s8-report.md` + `s8b-learning-loop.md`.

## 5. Research Vault map + load matrix
`SMM Virality Vault / <CLIENT> /` → `s1-baseline.md · s2-discovery.md · s3-outliers.md · s4-decode.md ·
s5-patterns.md · s6-calendar.md · s7-scripts.md · s8-report.md · s8b-learning-loop.md`

| Step | LOADs | SAVEs |
|---|---|---|
| S1 | — | s1 |
| S2 | (s1 optional) | s2 |
| S3 | s2 | s3 |
| S4 | s3 | s4 |
| S5 | s1,s2,s3,s4 | s5 |
| S6 | s1,s5 | s6 |
| S7 | s4,s5,s6 | s7 |
| S8 | s1–s7 | s8, s8b |

Every SAVE footer also prints **manual-save instructions** (`[[IF no Drive]]`) so the chain works even
without the Drive connector.

## 6. Beautifier scope (v1)
- **In:** paste S8 report markdown (also handles S6 calendar / S7 script-card markdown).
- **Out:** branded HTML — cover, sections, **KPI cards**, **simple inline SVG charts** (funnel counts,
  format-distribution bar, outlier scatter), **calendar table**, **script cards**; print-to-PDF clean.
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
