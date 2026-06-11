# KICKOFF PROMPT — SMM Virality Decoder Build

> **How to use:** paste the text below as the FIRST message of the new Claude Code session
> working in this repo (or just say: *"Read KICKOFF_PROMPT.md and BLUEPRINT.md in full,
> then begin Phase 0."*). Everything Claude needs is in this file + BLUEPRINT.md.

---

## THE PROMPT (paste from here down)

You are the lead engineer and product owner's right hand for building the **SMM Virality
Decoder** — a tool that researches what is going viral on Instagram in a client's niche,
decodes WHY (visual + verbal + packaging), and generates viral reel scripts and a 30-day
content calendar, operated by non-technical agency employees through a simple dashboard.

**Before anything else: read `BLUEPRINT.md` in this repo, top to bottom.** It is the source
of truth for the methodology (Swipe Test, outlier score, format transplant, 40/40/20 rule,
the S1–S8 prompt chain, the visual-analysis options, and operational traps already learned
the hard way on a sister project). Do not deviate from it silently — if you believe something
in it is wrong or you find a better way, SAY SO and get my approval before changing course.

### Operating rules (apply to the entire project, every phase)

1. **Phase gates.** Work in the numbered phases below. At the end of every phase: STOP,
   present me a concise review package (what was done, what was verified, what's risky,
   what you need from me), and WAIT for my explicit approval ("approved" / "go") before
   starting the next phase. Never start two phases in one turn.
2. **Interview me whenever you're unsure.** Never assume business facts (client names,
   niches, brand voice, budgets). Batch your questions — ask them all at once at the start
   of a phase, not one-by-one across ten turns. If my answer contradicts the blueprint,
   flag the contradiction instead of silently picking one.
3. **Honest reporting.** If a test fails, an actor returns garbage, or a feature is unverified,
   the review package says exactly that. Never present unverified work as done. Never fake
   or extrapolate data — "INSUFFICIENT DATA" is always an acceptable answer.
4. **Commit at every gate.** Each phase ends with a git commit (clear message) so we can roll
   anything back. Push after I approve the phase.
5. **Cost guardrail.** Ask me before any single scraping/API run expected to cost more than $5
   or pull more than 1,500 items. Report actual credits spent in every phase that scrapes.
6. **QC by fresh-eyes subagents** (details per phase below). QC agents must be given the
   ARTIFACT and the SPEC (relevant BLUEPRINT.md sections) but NOT your reasoning — they judge
   the work cold, the way a new employee or a hostile reviewer would. You fix what they find,
   then re-run them until clean.
7. **Separation.** This project shares zero code/files with the PPC Prompt Generator. Patterns
   are described in BLUEPRINT.md — reimplement them fresh here.

---

### PHASE 0 — Orientation, environment check, and owner interview

1. Read `BLUEPRINT.md` fully. Write back (≤1 page) your understanding of: the decode
   methodology, the S1–S8 chain, and the 3 biggest risks you see.
2. **Environment inventory — verify, don't assume.** Report which of these are actually
   available in THIS session: Apify MCP (and which org it's authed to), Higgsfield MCP
   (video_analysis + virality_predictor), Google Drive connector, web search, ffmpeg/shell.
   For anything missing that the blueprint needs, tell me the impact and the workaround
   (e.g., if Apify MCP isn't available in this cloud session, Phase 1 validation runs in a
   claude.ai chat with the Apify connector instead, and you'll write the exact prompts for me
   to paste there).
3. **Interview me (one batch).** At minimum: pilot client + IG handle; their niche, services,
   city/geo, language; 3-5 competitor/inspiration handles they already know; 2-3 adjacent
   niches you propose (suggest them yourself, I confirm); brand voice in 3 adjectives; no-go
   topics; posting capacity (reels/week, who films, phone vs designer); who the employees are
   that will operate the tool and their tech comfort level; the Drive folder name for the vault.
4. Produce `PROJECT_BRIEF.md` (my answers + environment findings) and commit.

**GATE 0:** I approve the brief → Phase 1.

---

### PHASE 1 — Live pipeline validation (NO UI code yet — prove the data first)

Goal: prove every data dependency on REAL data for the pilot niche before building anything.

1. **Actor verification.** Use Apify `search-actors` to confirm the exact, currently-available
   actors for: Instagram profile/reels scrape, hashtag top-posts, TikTok niche scan,
   audio transcription (`donjuan_mime/audio-video-to-text` is already rented), and a
   video-understanding actor (Gemini-based) as visual-layer candidate. For each: 5-item test
   run, then list the exact output fields we'll rely on (plays, videoUrl, caption, hashtags,
   audio/music metadata, timestamps, follower count). Remember the traps in BLUEPRINT §3.2
   (URL expiry → analyze in-session; field projection drops nested arrays; rental actors need
   a one-time permission click from me — when that error appears, give me the approval link).
2. **Outlier math on real data.** Scrape last ~30 reels for 3 accounts in the pilot niche,
   compute median plays and outlier scores, show me the table. Sanity-check: do the scores
   surface the reels a human would call "the viral ones"?
3. **Verbal layer test.** Transcribe 3-5 of those reels with Whisper. Show me one full
   transcript word-for-word so I can verify quality.
4. **Visual layer shootout.** Test ONE reel through each available option (Higgsfield
   video_analysis; Gemini-based Apify actor; ffmpeg frame-grid + your own vision if shell is
   available). Compare outputs against BLUEPRINT §2.6's VISUAL requirements (first-frame
   composition, overlay text, cut pacing, visual hook). Recommend the primary + fallback.
5. **Mini-decode proof.** Produce 3 complete decoded-reel cards (all three layers + taxonomy
   tags) — exactly what S4 will output at scale.
6. Write `VALIDATION_REPORT.md`: what works, exact actor names + input/output schemas, costs
   observed, blueprint corrections needed. Commit.

**QC for Phase 1:** spawn one skeptical subagent with the VALIDATION_REPORT and the raw
dataset IDs whose only job is to verify every claim in the report against the actual data
(re-fetch samples; recompute 3 outlier scores; check the transcript matches the reel's
caption/context). It reports discrepancies; you fix and re-verify.

**GATE 1:** I review the report + decoded cards. This is the most important gate — if the
data layer is shaky, we fix it HERE, not after the UI exists.

---

### PHASE 2 — Architecture plan (plan only, still no build)

1. Propose, in `ARCHITECTURE.md`:
   - File structure (single-file `index.html` dashboard per BLUEPRINT §6, plus README).
   - The intake form: every field, its placeholder key, required/optional, validation rule.
   - The S1–S8 prompt templates: per step — inputs (placeholders), MCP calls, output sections,
     HANDOFF SUMMARY content, caps (items, words), failure fallbacks.
   - Placeholder naming convention + the reconciler/pre-flight/diagnostics design (BLUEPRINT
     §6.2 — this killed an entire bug class in the sister project; non-negotiable).
   - Research Vault file map (s1…s8 filenames, which steps load which files).
   - Beautifier scope for v1 (client showcase + calendar render; the no-silent-drop rule).
   - What is explicitly OUT of v1 (BLUEPRINT §9).
2. Include a build sequence for Phases 3-5 with estimated session count.

**QC for Phase 2:** one architecture-review subagent reads ARCHITECTURE.md + BLUEPRINT.md cold
and answers: does every blueprint requirement map to a component? Is anything in the
architecture NOT traceable to the blueprint or the brief (scope creep)? Where will a
non-technical employee get confused or break it?

**GATE 2:** I approve the architecture (this is where I get to say "simpler" or "change X").

---

### PHASE 3 — Build the S1–S8 prompt chain (content before chrome)

1. Write all eight prompt templates in full, with placeholders, embedded methodology
   (Swipe Test, outlier formula, funnel phases with mechanical kill rules, three-layer decode,
   40/40/20 calendar, script quality gates incl. account-swap test and three-hooks rule),
   vault SAVE footers on all steps and LOAD headers on S5-S8, and graceful-degradation notes
   (no Higgsfield → say so in output; no Drive → manual save instructions).
2. Generate a full sample of each prompt with the pilot client's data filled in.

**QC for Phase 3 — run these as PARALLEL subagents, each blind to the others:**
- **Placeholder auditor:** every placeholder in every template has exactly one matching
  replacement key, byte-for-byte; no orphans, no dead keys; conditional fields covered.
- **Methodology auditor:** diff each template against BLUEPRINT §2 + §5 — list every
  requirement that is missing, weakened, or contradicted (e.g., S7 scripts missing the
  overlay-hook channel, S2 funnel missing the report-the-counts mandate).
- **Operational-trap auditor:** checks the chain against §3.2 — in-session transcription
  ordering, dataset-fetch instructions, caps present, permission-link instructions present.
- **Lazy-strategist red-team:** role-plays a rushed, non-technical employee: where can steps
  be skipped, misread, or produce garbage without anyone noticing? Output = concrete abuse
  cases; you harden the prompts against each.
Fix everything; re-run the auditors until all four come back clean. Include the final auditor
verdicts in the review package.

**GATE 3:** I review 2-3 sample prompts end-to-end (especially S4 and S7).

---

### PHASE 4 — Dashboard UI

1. Build `index.html`: intake form → prompt generation with literal placeholder replacement →
   copy buttons → required-field validation → load-time placeholder reconciler →
   pre-flight check on every generated prompt → a **Run Diagnostics** self-test button with a
   built-in TEST_CLIENT fixture. House style per BLUEPRINT §6.4 (Instrument Serif/Sans,
   JetBrains Mono, paper/ink, burnt-orange #C2410C accent). No CDNs, no build step — one file.
2. Verify in a real browser (or headless render): generate all 8 prompts with TEST_CLIENT,
   confirm zero leftover injectable placeholders, diagnostics passes, copy buttons work.

**QC for Phase 4:**
- **Code-review subagent** focused on the two killer patterns: (a) any renderer/parser that
  silently drops unrecognized content, (b) any hand-maintained pair of lists that must match
  byte-for-byte without a reconciler guarding them. Plus: JS errors, broken state on refresh.
- **Usability subagent** role-playing the non-technical employee from the PROJECT_BRIEF:
  walks the UI cold, top to bottom; reports every moment of confusion ("which step do I run
  first?", "what do I paste where?"). You fix with inline helper text, numbered steps, and
  disabled-until-ready buttons.

**GATE 4:** I click through the dashboard myself.

---

### PHASE 5 — Beautifier + final wiring

1. Beautifier tab: paste S8 markdown → branded HTML report (cover, sections, KPI cards,
   simple SVG charts, the calendar table, script cards) → print-to-PDF clean.
2. QC: render a test report containing BOTH all known block types AND deliberately unknown
   markdown — verify nothing is silently dropped (unknown content must render generically,
   never vanish). Structural checks: backtick/brace balance, no console errors.

**GATE 5:** I review a rendered sample report.

---

### PHASE 6 — End-to-end real-world run (the dress rehearsal)

1. Using the dashboard (not hand-written prompts), generate S1–S8 for the pilot client.
2. Run S1–S5 for REAL in a fresh chat/session with the connectors (you write exact operator
   instructions if a human must paste them). Vault saves verified after every step.
3. Produce the real deliverables: pattern synthesis, 30-day calendar, and at least 3 full
   viral scripts + the client showcase report through the Beautifier.
4. **Quality bar:** present the 3 scripts to me with their Swipe-Test verdicts and
   source-decode traceability. The question I will ask: "would I pay for this, and would a
   stranger stop scrolling?" Be your own harshest critic before I see it.

**GATE 6:** I judge output quality. We iterate here until the scripts are genuinely excellent.

---

### PHASE 7 — Employee-proofing, deploy, handoff

1. README.md: what the tool is, operator quick-start (numbered, screenshots optional),
   troubleshooting (permission links, expired URLs, missing connectors), cost notes.
2. Deploy: connect this repo to Vercel for auto-deploy on push (if the session can't do the
   one-time Vercel link, give me the exact 3 clicks to do in the Vercel dashboard).
3. Final regression: diagnostics green, all 8 prompts generate clean, beautifier renders,
   live URL works.
4. Dry-run protocol: a checklist I give an employee to run the whole flow while I watch
   silently; every stumble becomes a UI fix.
5. Roadmap section in README for the v2 ideas (BLUEPRINT §9) + the monthly Learning Loop
   schedule (S8b every month per client).

**GATE 7 (final):** live URL + my sign-off.

---

Begin now with **Phase 0, step 1**: read `BLUEPRINT.md` and report back your understanding,
the environment inventory, and your batched interview questions.
