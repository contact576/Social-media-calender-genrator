# SMM Virality Decoder — Master Blueprint

> **What this is:** the founding brief for a new tool that does for ORGANIC social media what the
> PPC Prompt Generator does for paid ads: industrial-grade niche research → viral-pattern decoding →
> production-ready viral scripts → monthly content calendar, all run by non-technical employees
> through a simple dashboard, with Claude doing 100% of the heavy lifting.
>
> **This is a SEPARATE product.** It shares proven *architecture patterns* with the PPC Prompt
> Generator but no code, no repo, no files. Build it in its own repo.
>
> **Audience for this doc:** the Claude (web) session that will build the tool. Read all of it
> before writing any code.

---

## 1. The mission

PPC Guru (digital marketing agency, Canada) manages social media for local-business clients
(renovation, clinics, restaurants, services...). Today, reel scripts are written from instinct.
The agency already proved a better way in its ads research system: **scrape what is actually
winning, decode WHY mechanically, then write from evidence.** This tool applies that method to
Instagram Reels (+ TikTok as a leading indicator).

The bar: act as if YOU own the brand and get paid $100,000 per million views — but remember the
agency truth below (§2.7): views that don't reach the client's buyers are worth $0. Decode for
virality, filter for relevance.

## 2. The Decode Framework (the intelligence — read this twice)

This is the methodology the tool encodes. Every step of the prompt chain exists to feed this.

### 2.1 The Swipe Test (organic twin of the ads "1-Second Rule")
A reel gets ~0.7 seconds before the swipe decision. THREE channels fire simultaneously and EACH
must independently stop the scroll:
1. **Visual hook** — what the first frame/motion shows (face mid-action, surprising object,
   before/after tease, movement toward camera).
2. **Verbal hook** — the first spoken sentence (≤2 seconds of speech).
3. **Overlay hook** — the on-screen text (≤8 words, readable in <1s, must NOT duplicate the
   verbal hook — it's a second message, not a caption of the first).
Every decoded reel gets all three extracted separately. Every script we write specifies all three
explicitly. A script that only writes "the hook" as one line is REJECTED.

### 2.2 Outlier score — the single most important number
**Virality is relative, not absolute.** 500k views on a 2M-follower account is the algorithm
feeding its audience; 500k views on an 8k-follower account is a FORMAT WIN — the content itself
carried it. That's what we want to decode.

> `outlier_score = reel_plays ÷ account's median reel plays (last 30 reels)`
> (fallback if median unavailable: plays ÷ followers)

- Score ≥ 5x → outlier, decode-worthy.
- Score ≥ 20x → priority decode (something in it beat the algorithm cold).
- Also track **consistency winners**: accounts whose MEDIAN is high — they have a repeatable
  system, not one lucky reel. Decode their system, not just their best reel.

### 2.3 Viral-mechanics taxonomy (tag every decoded reel)
- **HOOK TYPE:** curiosity gap / bold claim / relatable callout ("POV: you...") / visual shock /
  before-after tease / negativity-mistake ("stop doing X") / insider secret / challenge.
- **RETENTION DEVICE:** list countdown / loop (end feeds start) / fast cuts (<2s shots) /
  burned-in captions / progress bar / transformation reveal held to the end / pattern interrupt.
- **PAYOFF:** the promise of the hook delivered (reels that go viral pay off; clickbait without
  payoff kills follows and shares).
- **SHARE TRIGGER (why a human sends it to a friend):** identity ("this is SO us") / usefulness
  (save-worthy how-to) / awe / humor / controversy (mild, on-brand) / local pride (powerful for
  local businesses: city-specific content gets shared in city group chats).

### 2.4 Format taxonomy (tag every decoded reel)
Talking head / voiceover + b-roll / silent text-on-screen + trending audio / skit-POV /
before-after transformation / process-timelapse (oddly satisfying) / tutorial-listicle /
street vox-pop / meme-repurpose / day-in-the-life / client-reaction-testimonial.
Track the niche's format DISTRIBUTION: what's saturated (avoid or out-execute) vs. what's absent
(opportunity).

### 2.5 Format Transplant — the actual growth hack
The highest-probability viral play is NOT copying the niche's top reel (audience has seen it).
It is taking a format PROVEN in an ADJACENT niche and being FIRST to apply it to the client's
niche. ("What I'd do with $0 marketing budget" from business-tok → applied to landscaping.
"Things in my house that just make sense" from home-decor → applied to basement renovations.)
The pipeline therefore deliberately scrapes 2-3 adjacent niches and keeps a transplant map:
`proven format (adjacent) × client niche = novelty + proven mechanics`.

### 2.6 The three-layer decode per reel (visual + verbal + packaging)
- **VERBAL layer** — full word-for-word transcript: spoken hook, structure beats, payoff, CTA.
- **VISUAL layer** — what's ON SCREEN (see §4 for tooling): first-frame composition, overlay
  text content + placement + style, shot types (face/b-roll/screen-rec), cut pace (avg shot
  length), captions burned-in or not, color/lighting mood, the visual hook in the first second.
- **PACKAGING layer** — caption first line (it's the 4th hook — shows above "more"), caption
  structure + CTA, hashtag mix (count + size tiers), audio (trending sound vs original vs
  voiceover; capture the audio name/ID), length in seconds, posting time.

### 2.7 Reach ≠ revenue — the 40/40/20 calendar rule
For a BUSINESS account, the calendar must mix:
- **40% REACH reels** — built from decoded viral formats, broad relatable angle (the $100k/1M-views game).
- **40% NURTURE reels** — niche-specific value (how-tos, mistakes, costs explained) — these get
  saves and follows from actual ICP.
- **20% CONVERT reels** — proof, transformations, testimonials, offers — these get DMs and calls.
A tool that only chases views produces a famous account with no customers. Encode this split.

### 2.8 The Learning Loop (unique advantage of organic — DO build this)
Unlike ads research, organic results are public and free: every month, scrape the CLIENT'S OWN
account, compute outlier scores on our own posts, and feed "what worked for us" back into the
next calendar (double down on our ≥3x posts, kill our <0.5x formats). The ads side postponed
its learning loop; here it's trivial and compounding. Step S8 below does this.

---

## 3. Data & scraping plan (Apify — same MCP the team already uses)

### 3.1 Actors (verify each in the Apify store at build time; run a 5-item test before trusting)
| Job | Actor (verify exact name at build) | Notes |
|---|---|---|
| Profile + recent reels of an account | `apify/instagram-scraper` or `apify/instagram-profile-scraper` | gets followers, posts, per-reel plays/likes/comments, captions, videoUrl |
| Reels in bulk per account | `apify/instagram-reel-scraper` | reel-specific fields incl. play counts + video URLs |
| Hashtag top posts | `apify/instagram-hashtag-scraper` | discovery net |
| TikTok niche scan | `clockworks/tiktok-scraper` (or apify/tiktok-scraper) | leading indicator — formats hit TikTok 2-6 weeks before IG |
| Audio transcription | `donjuan_mime/audio-video-to-text` (ALREADY RENTED by PPC Guru, $5/mo, Whisper) | input `{model:"base", source_url:<videoUrl>}` |
| Visual analysis | see §4 | |

### 3.2 Hard-won operational lessons (from the ads build — do not relearn these)
1. **CDN video URLs expire in hours.** Transcribe/analyze IN THE SAME SESSION as the scrape.
2. **Rental actors need a one-time permission approval** — first MCP call throws an
   "approve permissions" error with a link; the owner clicks it once in the Apify console.
3. **`get-dataset-items` field projection SILENTLY DROPS nested arrays/objects.** Fetch full
   items and use `omit` for bulky fields instead of `fields` selection.
4. **Cap scrape sizes.** Cost is trivial (~$2.3/1k posts); the REAL constraint is Claude's
   analysis context. Wide-but-capped net, then mechanical filtering, then deep analysis on
   survivors only (the funnel, §5 S2).
5. **The strategist will be lazy under deadline.** Every filter must be a mechanical rule the
   prompt forces Claude to apply and REPORT (funnel counts in the output), not a judgment call.
6. Apify MCP must be authed to the same org that rented the actors ("PPC guru").

---

## 4. The visual-analysis layer (the gap the owner correctly identified)

Whisper hears the reel; nobody is WATCHING it. Three options, in test order:

- **Option A — Higgsfield MCP (already connected in the team's setup):** it exposes
  `video_analysis_create/status` and a `virality_predictor` tool. Test it on 3 reels first:
  if its analysis covers first-frame description, overlay text, shot pacing, and visual hook,
  it's the zero-new-vendor answer. Run virality_predictor on our DRAFT scripts/storyboards too
  (pre-flight for content!).
- **Option B — a Gemini-powered video-understanding actor on Apify:** search the Apify store
  (`search-actors`: "video analysis", "gemini video", "video to description"). Gemini natively
  watches video (visuals + audio together). An Apify actor wrapping it keeps the team's workflow
  100% inside the Apify MCP they already use. Verify output quality on 3 reels before adopting.
- **Option C — frame-grid + Claude vision (always works, zero new vendors):** download video →
  ffmpeg extracts a grid (dense for seconds 0-3 — the hook — then 1 frame/2s) → Claude reads the
  frames as images alongside the Whisper transcript. Works great in Claude Code (local or web,
  which can run ffmpeg); NOT available inside a plain claude.ai chat. If the team runs research
  in claude.ai chats, use A or B there.

**Prompt-chain rule:** the visual layer runs on the TOP 10-12 outliers only (it's the expensive
layer); Whisper runs on the top 20-25. Every decoded reel card has a `VISUAL` block; if no visual
tool is connected, the prompt says so explicitly in the output ("visual layer skipped — analysis
based on audio + thumbnail only") instead of silently pretending.

---

## 5. The decode chain — what the dashboard generates (8 logical stages, delivered as 5 prompts)

The methodology has eight logical stages (below). The shipped dashboard **fuses the tightly-coupled
ones into five copy-paste prompts** so the operator pastes fewer times — no stage is dropped, and each
fused prompt still saves the same distinct vault files:
**S1** = stage 1 (`s1-baseline`); **S2 (Discover & Rank)** = stages 2+3 (`s2-discovery`+`s3-outliers`);
**S3 (Decode & Synthesize)** = stages 4+5 (`s4-decode`+`s5-patterns`);
**S4 (Plan & Script)** = stages 6+7 (`s6-calendar`+`s7-scripts`);
**S5 (Showcase + Learning Loop)** = stage 8 (`s8-report`+`s8b-learning-loop`).
Terse in-chat outputs; Research Vault save/load (§6); steps runnable in fresh chats.

- **S1 — Client Brand & Baseline Decode.** Scrape the CLIENT's own account (last 50-90 posts):
  median plays (the baseline for all future outlier math), engagement rate, top-5/bottom-5 with
  why-hypotheses, formats used, cadence, follower quality. Extract brand voice from captions.
  Intake fields define ICP, services, geo, no-go topics. Output ends with HANDOFF SUMMARY.
- **S2 — Niche Discovery Funnel.** (the ads funnel, adapted)
  - *Phase A — wide net:* client-named competitors/inspirations (force-include) + hashtag
    top-posts across 6-10 niche hashtags (prefer mid-size tags, 100k-1M posts — mega-tags are
    spam) + 2-3 ADJACENT-niche seeds for transplant hunting. Cap: ~40-60 candidate accounts.
  - *Phase B — mechanical kills:* inactive (<1 post/wk), aggregator/repost accounts, wrong
    language/geo (unless kept as format-only), engagement-anomaly accounts (huge views, dead
    comments = botted), course-sellers/gurus posing as practitioners.
  - *Phase C — classification:* **EXACT** (same niche + same audience) / **ADJACENT** (same
    audience different service, or same format different niche — keep for transplant) /
    **MACRO** (1M+ accounts: decode hooks only; their reach is account-driven).
  - *Phase D — deep scrape:* last 30-50 reels for every EXACT + ADJACENT survivor.
  - Funnel counts reported (candidates → killed → classified → deep-scraped).
- **S3 — Outlier Harvest.** Compute outlier scores across every deep-scraped reel; rank; select
  top 20-25 (mix: ≥15 EXACT, ≥5 ADJACENT transplant candidates, ≤3 MACRO hook studies). Flag
  consistency winners. Output the ranked table with scores, links, plays, account medians.
- **S4 — Deep Decode.** Per selected reel: VERBAL (Whisper, same-session — URLs expire),
  VISUAL (top 10-12, via §4 tool), PACKAGING (caption/hashtags/audio/length/time). One
  structured card per reel tagged with §2.3 + §2.4 taxonomies.
- **S5 — Pattern Synthesis & The Gap.** Roll-up: hook bank (verbal / visual / overlay SEPARATELY),
  format distribution (saturated vs absent), length sweet spot, audio strategy, share-trigger
  frequency, transplant map (adjacent format × client niche), and THE GAP: what nobody in the
  niche is doing that the decode says would work. **Geo/language skew guard:** tally the ORIGIN of
  the decoded winners (carried from S2/S3/S4); if they cluster in one geo/language or a non-client
  sub-niche, stamp the synthesis GEO-SKEWED and carry the caveat into THE GAP — the format still
  transplants, but the sample isn't representative; recommend a broader, geo-balanced re-run.
- **S6 — Content Strategy + 30-Day Calendar.** 40/40/20 split (§2.7) mapped onto the client's
  pillars; per slot: date, pillar, format (from bank), hook concept, topic, audio rec, CTA,
  production effort tag (phone-only / designer / on-site shoot). This output feeds the agency's
  SMM "Content Strategy & Calendar" stage directly.
- **S7 — Viral Scripts (the money output; designer/editor handoff — internal only).** **Coverage is
  1:1 with the calendar — N slots produce N scripts, ending with a COVERAGE CHECK (X/N); a partial
  "flagship-only" set is rejected.** Each reel is written as a **two-column shooting script** (a
  markdown table): `TIME | AUDIO — what they HEAR | VISUAL & TEXT — what they SEE & READ`,
  beat-by-beat, timecodes summing to the target length. The AUDIO column is the spoken script only
  (silent/trending-audio reels say "— no voiceover —" and carry the message as on-screen TEXT on the
  right). The first row IS the hook and carries all three channels (§2.1 — spoken / first-frame
  visual / overlay text ≤8 words; overlay must be a *second* message). Under each table a footer:
  **HOOK · CALL TO ACTION · WHY IT'LL GO VIRAL** (the decoded mechanism + share trigger), plus
  caption, hashtags, audio, length.
  **Quality gates (all mandatory, mirror the ads doctrine):**
  - Swipe test verdict per script (would each of the 3 channels alone stop the scroll?).
  - Account-swap test (logo-swap analog): if any competitor could post this script unchanged,
    it's generic — rewrite with the client's proof/place/personality.
  - Share-trigger named per script (which §2.3 trigger, and why a human forwards it).
  - Traceability: every script cites which decoded reel/format it derives from (S4 card ID) —
    no invented-from-thin-air scripts.
  - Divergent ideation: brainstorm 2-3x candidates internally, score on the gates, output winners.
- **S8 — Client Showcase Report + Learning Loop.** (a) Client-facing visual report that SHOWS THE
  RESEARCH: how-we-researched-it (funnel counts + the three-layer decode method & tools), the
  accounts decoded **with their origin** (and any GEO-SKEW flag), niche insights, strategy, the full
  calendar, and **every S7 script in two-column format (1:1 with the calendar)** — beautified,
  charts, 8-12+ pages. Load is by exact filename; **s2-discovery + s3-outliers are non-negotiable
  inputs** (STOP if missing — the research section can't be honest without them). (b) MONTHLY
  RE-RUN: scrape client's own last-30-days reels, outlier-score our own posts vs S1 baseline,
  "keep / kill / double-down" verdicts, feed S6's next month.

### 5b. Autonomous "Claude Code" mode (the same methodology, run hands-free)
The dashboard offers a second mode that runs the whole chain end-to-end with no human copy-pasting: one
ORCHESTRATOR prompt drives the five stages via sub-agents, each gate paired **maker → blind checker**
(the project's fresh-eyes QC rule), with a bounded AUGMENT→REVAMP→REGENERATE repair ladder and a
self-capping Apify budget. It adds a **virality grader** — an LLM judge on the *script text* (NOT
Higgsfield `virality_predictor`, which needs a finished video) that scores each script on the §2.1/§2.3
mechanics and loops regenerate-with-feedback until **≥90 (≥85 for proof/CONVERT reels)**, hard-blocking
anything below bar. The deliverable is an 8–10 frame storyboard emitted as **image-generation prompts**
(rendered externally on Nano Banana Pro / GPT-Image — the tool generates no images and spends no credits)
plus a designer-ready doc. The decode methodology (§2) is unchanged; autonomy is orchestration around it.

## 6. Architecture: reuse the PATTERNS, not the code

Build a fresh single-file `index.html` dashboard (new repo) with the proven skeleton:
1. **Intake form** (~25 fields): client handle, niche, services, ICP, geo/language, brand voice
   notes, client-known competitor/inspiration handles, adjacent niches (suggest 2-3
   automatically), no-go topics, posting capacity (reels/week, who films), pillars.
2. **Prompt assembly:** `RAW_PROMPTS` templates + literal placeholder replacement + a load-time
   **placeholder reconciler** (orphan/dead-key detection) + **pre-flight check** + a
   **Diagnostics self-test button**. (These killed the entire class of injection bugs in the ads
   tool — non-negotiable.)
3. **Research Vault:** every prompt ends with "save full report + ≤30-line HANDOFF SUMMARY to
   Google Drive `SMM Virality Vault / <client>/ s<N>-<name>.md`"; S5-S8 prompts begin with
   "load the vault BEFORE anything" — so any step runs in a fresh chat and step 7 never forgets
   step 4's decode. (Solved context-rot in the ads chain; bake it in from day one here.)
4. **Beautifier:** paste markdown → branded HTML report (client showcase + calendar). Reuse the
   house style spec: Instrument Serif/Sans + JetBrains Mono, paper/ink surfaces, burnt-orange
   #C2410C accent. CRITICAL LESSON: bespoke section renderers must never silently drop
   unrecognized content — always fall through to a generic renderer.
5. **Employee-proofing:** required-field validation, copy buttons per step, step order enforced,
   "what to do if an actor asks for permissions" inline help, graceful degradation notes in
   every prompt (no Higgsfield → say so; no Drive → manual save instructions).

## 7. Build order (for the new Claude session)

1. This blueprint → repo as `BLUEPRINT.md`. Set up repo + Vercel (auto-deploy on push).
2. **Live pipeline test BEFORE building UI** (one session, one real client niche):
   run S1-S5 manually via Apify MCP — verify actor names/fields, outlier math on real data,
   Whisper on 5 reels, ONE visual option from §4 on 3 reels. Adjust this blueprint with findings.
3. Dashboard skeleton: form → S1-S8 prompt templates → reconciler/pre-flight/diagnostics.
4. Vault injection + Beautifier + house style.
5. End-to-end dry run by a non-technical employee while someone watches silently. Fix every
   point of confusion. THEN ship.

## 8. Costs (order of magnitude per client per month)
Scraping ~2-4k posts ≈ $5-10 · Whisper 20-25 reels ≈ $1-2 · visual layer 10-12 reels ≈ $1-5
(option-dependent) · TOTAL ≈ **$10-20/client/month** — trivial vs. one viral reel's value.
The constraint to engineer around is analysis context, not money (hence the funnel + vault).

## 9. Out of scope for v1 (decide later, don't build now)
Auto-posting/scheduling integrations; YouTube Shorts; comment-sentiment mining; influencer
outreach lists; paid amplification of winners (bridge to the ads tool); multi-client trend
dashboard. Park them in the README roadmap.
