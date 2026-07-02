# PROMPTS — the S1–S5 template chain (canonical source)

> These are the five copy-paste prompts the dashboard generates. They are written with placeholders;
> `index.html` loads them verbatim as `RAW_PROMPTS` and does literal replacement. **Do not paraphrase a
> template when porting — byte-for-byte, or the reconciler breaks.**
>
> **Placeholder syntax:** `{{UPPER_SNAKE}}` = literal replacement from the intake form (or DERIVED).
> `[[IF KEY]] … [[ENDIF]]` = block kept only when KEY is non-empty; stripped (with its content) when
> empty. Reconciler/pre-flight (BLUEPRINT §6.2) guard both.
>
> **Five steps, nine vault files.** The chain was condensed from eight steps to five by fusing the
> tightly-coupled stages (discovery+ranking, decode+synthesis, calendar+scripts) so the operator pastes
> fewer times — no analysis was dropped. Each merged step still saves the SAME distinct vault artifacts:
> S1→`s1-baseline`; S2→`s2-discovery`+`s3-outliers`; S3→`s4-decode`+`s5-patterns`;
> S4→`s6-calendar`+`s7-scripts`; S5→`s8-report`+`s8b-learning-loop`.
>
> **Proven actors (VALIDATION_REPORT.md):** profile/reels + medians = `apify/instagram-reel-scraper`;
> niche keyword search = `data-slayer/instagram-search-reels`; transcription =
> `donjuan_mime/audio-video-to-text` (input key `source_url`, `model:"small"`); visual = Higgsfield
> `video_analysis` (primary) + `grizzlygriff/video-llm-analyzer` (overlay-text/fallback).
>
> **Universal data-fetch rule (every step that reads a dataset):** fetch FULL items with
> `get-dataset-items` and `omit` bulky blocks — never use `fields=` on nested arrays (it silently drops
> them, BLUEPRINT §3.2). **Universal permission rule:** if any actor returns an *approve-permissions*
> error, copy the link to the owner to click once in the Apify console, then re-run.

---

## S1 — Client Brand & Baseline Decode

```
You are a senior social-media research analyst. Establish whatever BASELINE the client's own Instagram
allows — many clients are brand-new or near-empty, and that is expected and fine. Be mechanical and
honest: report counts, never invent numbers. A "NEW/THIN ACCOUNT" verdict is a correct, useful answer.

CLIENT CONTEXT
- Client: {{CLIENT_NAME}}[[IF CLIENT_HANDLE]]  (@{{CLIENT_HANDLE}})[[ENDIF]]
[[IF CLIENT_WEBSITE]]- Website / destination: {{CLIENT_WEBSITE}}[[ENDIF]]
- Niche: {{NICHE}}
- Services (priority order): {{SERVICES}}
- Ideal customer (ICP): {{ICP}}
- Geo: {{GEO_PRIMARY}}
- Primary language: {{LANGUAGE_PRIMARY}}
- Hard no-go (never produce): {{NO_GO_TOPICS}}
[[IF ADDITIONAL_NOTES]]- Operator notes (extra context — voice, proof, constraints): {{ADDITIONAL_NOTES}}[[ENDIF]]

STEP 0 — DECIDE THE MODE.
[[IF CLIENT_HANDLE]]Scrape the client's own reels. MCP — apify/instagram-reel-scraper:
   { "username": ["{{CLIENT_HANDLE}}"], "resultsLimit": 90, "skipPinnedPosts": true }
   Fetch full dataset items with `omit` for heavy blocks; never `fields=` on nested arrays. If the actor
   returns an "approve-permissions" error, send the link to the owner to approve once, then re-run.
   Count reels WITH a non-null `videoPlayCount` (call it n).[[ENDIF]]
   - No handle provided, or n < 10  → MODE = NEW/THIN ACCOUNT.
   - Otherwise                      → MODE = ESTABLISHED ACCOUNT.
   State the chosen MODE on the first line of your output.

IF MODE = NEW/THIN ACCOUNT:
   - BASELINE_MEDIAN_PLAYS = "N/A — new/thin account (n=<count>)". Do NOT fabricate a baseline. The
     discovery step (S2) scores each DISCOVERED account against its own median, so the pipeline needs no
     client baseline — discovery proceeds exactly the same.
   - Brand voice: infer a RECOMMENDED voice from the niche, services, ICP and any operator notes (label
     it RECOMMENDED, not observed). If a handful of posts exist, add observed traits and mark them so.
   - Skip the play-count statistics; complete the HANDOFF SUMMARY with what you have.

IF MODE = ESTABLISHED ACCOUNT, compute and REPORT as a table:
   - n (reels analysed) and date range covered.
   - BASELINE = MEDIAN of `videoPlayCount`. (Sacred — S2's outlier math and S5's learning loop use it.)
     Report how many reels had missing/zero `videoPlayCount` and whether you excluded or zero-filled them
     BEFORE the median. If n < 30, stamp the BASELINE "LOW-CONFIDENCE (n=X)" and repeat that stamp in the
     HANDOFF SUMMARY.
   - Mean plays + median:mean ratio (skew check).
   - Engagement rate per reel = (likesCount + commentsCount) / videoPlayCount; report the median ER.
   - Posting cadence: reels/week from `timestamp` spread.
   - Top-5 and Bottom-5 reels by `videoPlayCount`: plays, ER, a one-line WHY-HYPOTHESIS (labelled
     HYPOTHESIS, not fact).
   - Format mix used (talking-head / voiceover+b-roll / text-on-screen / skit / before-after /
     tutorial-listicle / other) with rough %.
   - Brand voice read: 3–5 observed traits from captions + 3 example caption first-lines.
   - Follower-quality sniff test: do plays/likes/comments move together, or is there an engagement
     anomaly (views high, comments dead = possible botting)? State the verdict.

OUTPUT: the MODE line, then the relevant block above, terse. Then a HANDOFF SUMMARY (≤30 lines)
containing exactly: MODE, BASELINE_MEDIAN_PLAYS (or "N/A"), n, median_ER (or "N/A"), cadence_per_week
(or "N/A"), top_format (or "N/A"), voice (observed or RECOMMENDED, 3–5 traits), no_go (echo), one-line
"biggest opportunity" hypothesis.

VAULT SAVE: save the FULL report and the HANDOFF SUMMARY to Google Drive at
"{{VAULT_FOLDER}}/s1-baseline.md". After saving, echo the exact saved path + file link and confirm you
did NOT create a duplicate vault folder.
If the Google Drive connector is unavailable, output the full file contents in a
single code block and tell me to paste-save it as s1-baseline.md myself.
```

---

## S2 — Discover & Rank (niche discovery + outlier harvest)

```
You are a niche-research analyst AND quantitative analyst. In ONE pass: (PART 1) find the reels worth
decoding for {{CLIENT_NAME}} by searching the NICHE — not named competitors — then (PART 2) rank them
with ACCOUNT-RELATIVE math. Apply mechanical kill rules, REPORT every funnel count, and surface the
outliers that beat their own account's median — raw play-count is misleading.

VAULT LOAD (FIRST): load "{{VAULT_FOLDER}}/s1-baseline.md" (the client's own baseline). LOAD RECEIPT:
echo found y/n + last-modified. If missing/empty, note it and proceed — discovery does not require it.

CLIENT CONTEXT
- Niche: {{NICHE}} · Services: {{SERVICES}} · ICP: {{ICP}}
- Geo: {{GEO_PRIMARY}} · Language: {{LANGUAGE_PRIMARY}}[[IF LANGUAGE_SECONDARY]] / {{LANGUAGE_SECONDARY}}[[ENDIF]]

DISCOVERY INPUTS
- Niche search keywords (run one search PER keyword): {{NICHE_KEYWORDS}}
[[IF NICHE_HASHTAGS]]- Niche hashtags (prefer mid-size, 100k–1M posts): {{NICHE_HASHTAGS}}[[ENDIF]]
- Adjacent-niche keywords (for format transplant — keep these separate): {{ADJACENT_KEYWORDS}}
[[IF COMPETITOR_HANDLES]]- Force-include these competitor handles as seeds: {{COMPETITOR_HANDLES}}[[ENDIF]]

PART 1 — DISCOVERY FUNNEL
PHASE A — WIDE NET (three legs — run ALL three, then print the RUN RECEIPT below).
   Leg 1 — KEYWORDS: for EACH niche keyword, MCP — data-slayer/instagram-search-reels:
     { "query": "<keyword>", "maxPages": 2 }  (≈12 reels/page, ~24/keyword; run SEPARATELY per keyword.)
   Leg 2 — HASHTAGS (always run, even if the hashtag field is empty): use the operator hashtags above
     if present; otherwise DERIVE 6–10 mid-size (100k–1M post) niche hashtags for {{NICHE}} yourself,
     and run EACH as its own query through the same actor (a "#tag" string is a valid query). Do NOT
     skip this leg — it is core to the wide net.
   Leg 3 — ADJACENT: run each ADJACENT keyword the same way and TAG those results "ADJACENT".
[[IF COMPETITOR_HANDLES]]   Leg 4 — SEEDS: also pull the force-include handles via
     apify/instagram-reel-scraper ({ "username": [<handles>], "resultsLimit": 12,
     "skipPinnedPosts": true }) and tag "SEED".[[ENDIF]]
   Pool all results. Fetch full items with `omit`; if a query returns 0, report "0 results" and
   continue (not fatal). HARD CAPS — do NOT raise them, report a shortfall instead: maxPages = 2 per
   query; total pool ≈ 150 reels.
   RUN RECEIPT (mandatory): a table — query | type (keyword/hashtag/adjacent/seed) | ran y/n | pages |
   reels returned. The funnel is INVALID if any keyword/hashtag/adjacent query lacks a row; if you ran
   fewer searches than queries, STOP and say so.
PHASE B — MECHANICAL KILLS (apply in order; report how many die at each):
   - inactive author (no recent posting signal in the data) ;
   - aggregator / repost / meme-only accounts ;
   - wrong language/geo — UNLESS the format is strong, then keep but tag "FORMAT-ONLY" ;
   - engagement anomaly (huge plays, near-zero comments = likely botted) ;
   - course-sellers / gurus posing as practitioners.
   For each rule, list the usernames killed (a representative sample if large) — a kill COUNT with no
   named accounts is REJECTED (don't fabricate rigor).
PHASE C — CLASSIFY each survivor account:
   EXACT (same niche + same audience) · ADJACENT (same audience diff service, OR same format diff niche
   — transplant candidates) · MACRO (1M+ followers: decode HOOKS ONLY, reach is account-driven).
   For EACH survivor also RECORD its ORIGIN — geo/country signal + primary language (read from the
   profile, captions, and the reel's spoken/written language). This travels into the ranking and decode
   so S3 can catch a geo/language skew. "geo unclear" is an acceptable, honest value.
PHASE D — name the accounts to deep-scrape (every EXACT + ADJACENT survivor).
FUNNEL LINE (mandatory): candidates_found → killed_by_rule (per-rule counts) → survivors →
{EXACT n, ADJACENT n, MACRO n} → accounts_to_rank (usernames + ORIGIN (geo/language) + the single best
reel URL seen per account).

PART 2 — OUTLIER HARVEST (account-relative math; decode the outliers, not the loud numbers)
1) For EACH account named in PHASE D, MCP — apify/instagram-reel-scraper:
   { "username": ["<account>"], "resultsLimit": 40, "skipPinnedPosts": true }
   We want ≥30 reels per account for a stable median. REPORT the actual n per account — some profiles
   paginate short. Fetch full items with `omit`.
2) For each account compute ACCOUNT_MEDIAN = median `videoPlayCount` over its scraped reels.
3) For every reel, OUTLIER_SCORE = videoPlayCount ÷ ACCOUNT_MEDIAN.
   (Fallback only if a median is unavailable: videoPlayCount ÷ follower count, label it, and list those
   reels in a SEPARATE table — never co-rank them with account-relative scores.)
4) Thresholds: ≥5x = OUTLIER (decode-worthy); ≥20x = PRIORITY. Also flag CONSISTENCY WINNERS (accounts
   whose ACCOUNT_MEDIAN is itself high vs peers — their repeatable SYSTEM is the prize). If an account's
   n < 20, label its scores LOW-CONFIDENCE and do NOT let it contribute a ≥20x PRIORITY reel without a
   written caveat.
5) SELECT the decode set: top 20–25 reels overall, composed of ≥15 EXACT, ≥5 ADJACENT (transplant),
   ≤3 MACRO (hook-only). If a bucket can't be filled, print the SHORTFALL (e.g. "EXACT 9/15") and
   proceed under-filled — reclassifying or padding to hit a quota is REJECTED.

COST GUARDRAIL: this step scrapes. Before any run would exceed ~$5 or 1,500 items, PAUSE and ask the
owner; report actual spend at the end.

OUTPUT: the RUN RECEIPT + funnel line + kill table (PART 1), then ONE ranked table —
rank | account | origin (geo/lang) | reel URL | plays | account_median (n) | OUTLIER_SCORE |
class (EXACT/ADJACENT/MACRO) | consistency-winner? | reel videoUrl (direct, for the S3 decode) — and a
3-line read of what the scores reveal.

VAULT SAVE: save TWO files —
  "{{VAULT_FOLDER}}/s2-discovery.md" — full funnel + kill table + EXACT/ADJACENT/MACRO lists WITH each
    account's ORIGIN + the deep-scrape targets;
  "{{VAULT_FOLDER}}/s3-outliers.md" — the ranked table + HANDOFF SUMMARY (≤30 lines: the selected 20–25
    with scores, classes, origins, and direct videoUrls).
After saving, echo BOTH exact paths + links and confirm no duplicate folder was created. Both files are
REQUIRED downstream (S5's report cannot be assembled without them) — do not skip either save.
No Drive connector? Output both files in code blocks for me to paste-save.
```

---

## S3 — Decode & Synthesize (three-layer decode + pattern synthesis)

```
You are a viral-content decoder AND strategy synthesist. In ONE pass: (PART 1) decode each selected reel
on THREE independent layers, then (PART 2) roll the decoded cards up into the patterns that drive the
calendar and scripts. Separate the three hook channels — never blend them.

VAULT LOAD (FIRST): load "{{VAULT_FOLDER}}/s3-outliers.md" (the selected reels + direct videoUrls),
"{{VAULT_FOLDER}}/s2-discovery.md" (account origins) and "{{VAULT_FOLDER}}/s1-baseline.md". LOAD RECEIPT:
echo each found y/n + last-modified. If s3-outliers is missing or empty, STOP — never reconstruct a prior
step's output from memory.

Work in ONE session: Instagram CDN video URLs expire within hours, so transcribe/analyse a reel in the
same run you loaded it — if a videoUrl 403s, re-scrape that single reel first; if re-scrape also fails,
the VERBAL/VISUAL/OVERLAY layers for that reel MUST read "UNAVAILABLE — URL expired". Writing a
transcript or overlay from the caption or topic is FABRICATION and is forbidden.

DECODE-ACTOR HEALTH (check FIRST — the decode actors are third-party and can be expired/renamed/broken):
  Do a 1-reel probe of each decode actor before decoding the full set. If the transcription actor errors
  "must rent a paid Actor / free trial expired", the audio engine is DOWN — send the owner the rental link
  once (or switch to a working transcription actor they provide) and DO NOT proceed on a fabricated
  transcript. If the Higgsfield video_analysis tool is not callable by name in this session, treat it as
  unavailable (do not assume it exists). If the visual actor (grizzlygriff/video-llm-analyzer) FAILS, retry
  once, then mark VISUAL unavailable. If ALL decode paths are down, STOP the decode and report exactly which
  actor needs fixing (rental or replacement) with its console link — a decode with no working
  transcription/visual engine produces NOTHING real, so inventing VERBAL/VISUAL/OVERLAY is FORBIDDEN and a
  "decode blocked — <actor> needs <rental/replacement>" report is the correct, useful answer.

PART 1 — DEEP DECODE — per selected reel, produce a CARD with these four blocks:
VERBAL (full word-for-word):
  - Default engine = transcription. MCP — donjuan_mime/audio-video-to-text:
    { "source_url": "<the reel's videoUrl>", "model": "small" }   (use `small`, NOT `base`.)
  - STATE the detected language + a confidence note BEFORE trusting any transcript. IF the reel is
    non-English / music-only / heavy text-on-screen: Whisper output is INADMISSIBLE — use Higgsfield
    video_analysis (it transcribes AND translates) or mark "no reliable verbal". Auto-detecting English
    on a visibly non-English reel is a FAILURE. STATE which engine produced the verbal layer. If there is
    no speech at all, write "no spoken track — message carried by overlay/visual".
  - Capture: spoken hook (first ≤2s), structure beats, payoff, CTA.
VISUAL (MANDATORY on at least the top 10 outliers — it is the ONLY source for the visual-hook channel
  the scripts require; skipping it for all reels INVALIDATES the script step, so say so loudly if you
  ever must):
  - Primary, MCP Higgsfield: (1) media_import_url("<videoUrl>") → media_id ;
    (2) video_analysis_create({ "video_input_id": media_id }) ; (3) poll video_analysis_status.
    Pull: first-frame composition, shot types, cut pace (avg shot length), whether captions are
    burned-in or not, color/lighting mood, and the visual hook in second 1.
  - Overlay-text specialist + fallback, MCP — grizzlygriff/video-llm-analyzer:
    { "video": "<videoUrl>", "prompt": "Extract every on-screen text overlay verbatim with timing;
      describe the first frame and cut pacing.", "llmProvider": "gemini",
      "model": "google/gemini-2.5-flash", "skipDestination": true, "framesToExtract": 4,
      "maxChargeUsd": 0.1 }   HARD CAP: never raise framesToExtract above 6 (the LLM 413s) — note thin
      coverage instead. If charge-capped or partial, mark the VISUAL block "PARTIAL (cost-capped)".
  - IF no visual tool is connected, write "VISUAL skipped — audio + thumbnail only" (do not pretend).
OVERLAY (the on-screen text as its own channel): the verbatim overlay words + placement/style. A SEPARATE
  hook channel from the spoken words. If overlay text could not be independently read (no VISUAL run),
  write "OVERLAY not captured" — never copy the spoken hook here.
PACKAGING: caption first line (the 4th hook), caption structure + CTA, hashtag mix (count + size tiers),
  audio (`musicInfo`: trending vs original vs voiceover — capture song_name/artist/audio_id), length in
  seconds, posting time.
THEN TAG each card (BLUEPRINT §2.3 + §2.4):
  HOOK TYPE · RETENTION DEVICE · PAYOFF (delivered? y/n) · SHARE TRIGGER · FORMAT · ORIGIN (geo/language,
  carried from s2/s3). Give each card an ID (C1, C2, …) — the scripts must cite these, and PART 2 uses
  ORIGIN to detect geo/language skew.
CAPS: VERBAL on all selected 20–25; VISUAL on the top 10–12 only (mandatory on at least the top 10).
End PART 1 with a decoded-vs-URL-dead count.

PART 2 — PATTERN SYNTHESIS & THE GAP
First, a confidence + skew read on the cards you just produced:
  - Count cards fully decoded vs UNAVAILABLE/low-confidence; if fewer than ~15 carry real 3-layer data,
    STAMP the whole synthesis "LOW-CONFIDENCE" and do not assert THE GAP as fact.
  - GEO/LANGUAGE SKEW CHECK: tally the ORIGIN of the decoded cards. If the winners cluster in ONE geo or
    ONE language — or a single sub-niche that isn't the client's own market — STAMP the synthesis
    "GEO-SKEWED", say so plainly, and repeat it in THE GAP and the HANDOFF. The formats may still
    transplant (that's what the account-relative score proves), but the sample is not representative of
    {{GEO_PRIMARY}}; recommend a broader, geo-balanced re-run.
PRODUCE:
1) HOOK BANK — three separate lists: VERBAL hooks, VISUAL (first-frame) hooks, OVERLAY-text hooks. Each
   entry cites the card IDs it came from.
2) FORMAT DISTRIBUTION — which formats are SATURATED (avoid or out-execute) vs ABSENT (opportunity).
3) LENGTH SWEET SPOT — seconds range of the highest outliers.
4) AUDIO STRATEGY — trending-sound vs original vs voiceover split among winners; name recurring sounds.
5) SHARE-TRIGGER FREQUENCY — which §2.3 triggers recur (identity / usefulness / awe / humor /
   controversy / local pride).
6) TRANSPLANT MAP — for each ADJACENT format: "proven format (adjacent niche) × {{NICHE}} = concrete
   reel idea". At least 3 transplants.
7) THE GAP — the single biggest thing NOBODY in the niche is doing that the decode says would work for
   {{CLIENT_NAME}}. It MUST cite ≥3 specific card IDs (what's present) AND name what's absent. A GAP with
   no card citations is REJECTED.

OUTPUT: the decoded cards (compact), then the seven synthesis sections (terse).
VAULT SAVE: save TWO files —
  "{{VAULT_FOLDER}}/s4-decode.md" — full cards + HANDOFF SUMMARY (≤30 lines: card IDs with one-line hook
    + format + outlier score + ORIGIN each; mark any UNAVAILABLE/low-confidence cards);
  "{{VAULT_FOLDER}}/s5-patterns.md" — full synthesis + HANDOFF SUMMARY (≤30 lines: top 5 verbal + 5
    visual + 5 overlay hooks, the 3 transplants, THE GAP in one sentence, and the GEO/LANGUAGE SKEW
    verdict + confidence stamp).
After saving, echo BOTH exact paths + links and confirm no duplicate folder was created.
No Drive? Output both files in code blocks to paste-save.
```

---

## S4 — Plan & Script (30-day calendar + viral scripts)

```
You are a content strategist AND a viral scriptwriter who gets paid $100,000 per million views — but you
also know that views that don't reach {{CLIENT_NAME}}'s buyers are worth $0. In ONE pass: (PART 1) turn
the patterns into a 30-day calendar balanced for REACH/NURTURE/CONVERT, then (PART 2) write a
production-ready two-column script for EVERY slot.

VAULT LOAD (FIRST): load "{{VAULT_FOLDER}}/s1-baseline.md", "{{VAULT_FOLDER}}/s4-decode.md",
"{{VAULT_FOLDER}}/s5-patterns.md". LOAD RECEIPT: echo each found y/n + last-modified; if s5-patterns or
s4-decode is missing or empty, STOP — never reconstruct from memory.

STRATEGY INPUTS
- Posting capacity: {{POSTING_CAPACITY}}
- Production modes available: {{PRODUCTION_MODES}}
- Primary CTA: {{CTA_PRIMARY}}
[[IF ADDITIONAL_NOTES]]- Operator notes (proof, preferred pillars, voice, constraints): {{ADDITIONAL_NOTES}}[[ENDIF]]
- Calendar starts the next Monday on/after {{CURRENT_DATE}} (state the actual start date you use).
- Hard no-go (never produce): {{NO_GO_TOPICS}}. Use the client's voice from s1-baseline (observed or RECOMMENDED).

PART 1 — 30-DAY CALENDAR (40/40/20)
DERIVE PILLARS FIRST: from the services, the ICP and the s5 patterns + THE GAP (plus any operator notes),
define 3–5 content pillars and list them up front. Map every calendar slot to one of these pillars.
RULES
- MIX every week toward the 40/40/20 split:
  40% REACH (decoded viral formats, broad relatable angle) ·
  40% NURTURE (niche value: how-tos, mistakes, costs explained — saves & follows from the ICP) ·
  20% CONVERT (proof, transformations, testimonials, offers). Build CONVERT slots from any proof in the
  operator notes; if none was supplied, mark each CONVERT slot "needs a proof asset from the client"
  rather than inventing a result.
- Honor the cadence in {{POSTING_CAPACITY}} — CAP at 3 reels/week; a week with >3 slots is REJECTED.
- Pull hooks/formats from the s5 hook bank + transplant map; tag which card/transplant each derives from.
  Every source card ID you cite MUST exist in the loaded s4/s5 set — cross-check, don't invent.
CALENDAR TABLE — one row per slot: date | week | REACH/NURTURE/CONVERT | pillar | format (from bank) |
hook concept | topic | audio rec | CTA | production-effort tag (phone-only / designer / on-site shoot —
from {{PRODUCTION_MODES}}) | source (card ID or transplant). Print the LITERAL integer counts +
percentages per bucket and per week. With a 2–3 reel/week cadence an exact 40/40/20 is usually
impossible — show the NEAREST achievable split and FLAG the deviation; never claim "40/40/20" if the
math doesn't.

PART 2 — VIRAL SCRIPTS (two-column shooting scripts)
COVERAGE RULE (mandatory): write ONE script for EVERY slot in the PART 1 calendar — if there are N slots,
output N scripts, numbered to match. Do NOT output "a few flagship scripts" or stop early. End with a
COVERAGE CHECK line: "scripts written X / calendar slots N". If X < N, STOP and name the unscripted
slots — a partial set is REJECTED.
FORMAT — write each reel as a TWO-COLUMN SHOOTING SCRIPT (a markdown table) so a shooter can read it at a
glance. The columns separate what the viewer HEARS from what they SEE and READ:

  ### Reel <n> — "<title>" · <REACH/NURTURE/CONVERT> · <length>s · <audio>
  | TIME | AUDIO — what they HEAR | VISUAL & TEXT — what they SEE & READ |
  |---|---|---|
  | 0–2s | <spoken hook, exact first words ≤2s — or "— no voiceover — (trending audio)"> | <first-frame / first-motion visual> · OVERLAY: "<on-screen text ≤8 words>" |
  | <t> | <spoken VO for this beat> | <shot / b-roll direction> · OVERLAY: "<text card, if any>" |
  | <t> | <CTA, spoken — tied to {{CTA_PRIMARY}}> | <end-card visual> · OVERLAY: "<CTA text>" |

  Table rules:
  - Beat-by-beat rows whose timecodes sum to the target length (per the s5 sweet spot).
  - AUDIO column = the spoken script ONLY (voiceover / dialogue). For a silent or trending-audio reel,
    write "— no voiceover — (trending audio)" in every AUDIO cell and carry the message as on-screen
    TEXT in the right column.
  - VISUAL column = the camera/shot direction AND the verbatim on-screen text, the text prefixed
    "OVERLAY:". Keep visual and overlay together here; keep them OUT of the AUDIO column.
  - The first row IS the hook and MUST carry all three hook channels: the SPOKEN hook (AUDIO cell), the
    VISUAL hook and the OVERLAY hook (right cell, overlay ≤8 words). The OVERLAY must be a SECOND message,
    not a transcript of the spoken hook — if they say the same thing, rewrite the overlay.
Directly UNDER each table, a FOOTER of labelled lines:
- HOOK: the one thing that stops the scroll in second 1, and which channel carries it.
- CALL TO ACTION: tied to {{CTA_PRIMARY}}.
- WHY IT'LL GO VIRAL: the decoded mechanism — cite the decode card ID (C#) / s5 transplant it derives
  from and the §2.3 share trigger.
- CAPTION: first-line hook + body + CTA. · HASHTAGS: a set sized per the s5 findings. · AUDIO + LENGTH.
QUALITY GATES — run all of these internally on each script and report them COMPACTLY (one line per
script; a bare "pass" is NOT accepted — keep the evidence):
- SWIPE: would EACH of the 3 channels independently stop the scroll? (visual / verbal / overlay)
- OVERLAY ≠ VERBAL: the overlay text must differ from the spoken hook (if identical, rewrite).
- ACCOUNT-SWAP: name the specific owned proof point used (operator notes / s1-baseline). No proof on
  file → flag the script "needs client proof" — never invent one.
- SHARE TRIGGER: the one §2.3 trigger and why a human forwards it.
- TRACEABILITY: the decode card ID (C#) / s5 transplant it derives from. A card flagged
  UNAVAILABLE/low-confidence makes the script SPECULATIVE — label it so; no invented-from-nothing scripts.
- NO-GO: quote the script's strongest claim and explain why it does NOT cross into {{NO_GO_TOPICS}}.

OUTPUT: the calendar table + the literal split counts (PART 1), then the N two-column scripts (table +
footer + one-line gate verdict each), then the COVERAGE CHECK.
VAULT SAVE: save TWO files —
  "{{VAULT_FOLDER}}/s6-calendar.md" — full calendar + HANDOFF SUMMARY (≤30 lines: split counts + the slot
    list dates/formats);
  "{{VAULT_FOLDER}}/s7-scripts.md" — full scripts + HANDOFF SUMMARY (≤30 lines: one line per script — its
    hook gist + source card + share trigger).
After saving, echo BOTH exact paths + links and confirm no duplicate folder was created.
No Drive? Output both files in code blocks to paste-save.
```

---

## S5 — Client Showcase Report + Learning Loop

```
You are producing (a) a client-facing showcase report and (b) the monthly learning-loop re-run for
{{CLIENT_NAME}}. Part (a) is paste-ready for the Beautifier. Part (b) makes next month smarter.

VAULT LOAD (FIRST): load the chain's vault files from "{{VAULT_FOLDER}}/". LOAD RECEIPT: print a 7-file
checklist by EXACT filename — s1-baseline, s2-discovery, s3-outliers, s4-decode, s5-patterns,
s6-calendar, s7-scripts (found y/n + last-modified). If ANY is missing, STOP and list which — do not
assemble a partial showcase from memory. s2-discovery and s3-outliers are NON-NEGOTIABLE: the report's
research section (funnel + accounts + origins) cannot be honestly written without them, so if either is
absent, STOP and ask the operator to (re-)run the discovery step rather than papering over the gap.

PART A — SHOWCASE REPORT (markdown, paste into the Beautifier). It must SHOW THE RESEARCH, not just the
output — include all of these sections:
- Cover: {{CLIENT_NAME}} · {{NICHE}} · prepared {{CURRENT_DATE}}.
- HOW WE RESEARCHED IT: the funnel counts (from s2 — candidates → kills → survivors), how many accounts
  were deep-scraped and how many reels were fully decoded (from s3/s4), and the THREE-LAYER DECODE METHOD
  naming the tool used per layer (visual / on-screen-text / audio, from s4). Make the rigor visible.
- ACCOUNTS WE DECODED: a table of each decoded account WITH ITS ORIGIN (geo + language, from s2/s4) and
  one line on why it was relevant / how its format transplants. If s5 stamped a GEO/LANGUAGE SKEW (e.g.
  every winner from one region), state it plainly here — never hide a thin or skewed sample.
- NICHE INSIGHTS: saturated vs absent formats, hook-bank highlights, THE GAP (from s5).
- STRATEGY: the 40/40/20 logic + the FULL 30-day calendar table (from s6).
- THE SCRIPTS: include EVERY script from s7, each in its two-column shooting-script format (table +
  Hook/CTA/Why-viral footer) — one script per calendar slot, matching the calendar 1:1. Do NOT reduce to
  "a few flagship examples". Print a COVERAGE line: "scripts shown X / calendar slots N".
- Keep claims evidence-bound; for each headline number cite which vault file it came from. A count that
  was flagged LOW-CONFIDENCE / UNAVAILABLE / PARTIAL / GEO-SKEWED upstream must NOT appear as a clean
  stat here — carry the flag through to the client report.

PART B — LEARNING LOOP (monthly re-run):
The learning loop compares the client's OWN posts against their S1 baseline each month. It only runs
once the client has an account with posts — if there is no client handle yet, write "Learning loop not
yet active — client has no account/posts" and skip the rest of Part B.
[[IF CLIENT_HANDLE]]- First check the S1 baseline's age + n. If older than ~60 days OR stamped
  LOW-CONFIDENCE (n<30), RECOMPUTE the baseline from a fresh client scrape before any verdict.
- MCP — apify/instagram-reel-scraper on the client's OWN last-30-days:
  { "username": ["{{CLIENT_HANDLE}}"], "resultsLimit": 30, "skipPinnedPosts": true }
  If the actor returns an "approve-permissions" error, send the link to the owner to approve once, re-run.
- Outlier-score the client's own posts vs the S1 BASELINE_MEDIAN_PLAYS. If the baseline is "N/A —
  new/thin account", treat this as MONTH 1: just record each post + its plays to SEED next month's
  baseline, and skip keep/kill verdicts (nothing to compare against yet).
- Verdicts (once a baseline exists): KEEP / KILL / DOUBLE-DOWN — double down on ≥3x posts, kill <0.5x
  formats. Feed the verdicts into next month's S4 calendar.[[ENDIF]]

OUTPUT: Part A markdown, then Part B verdict table. VAULT SAVE: Part A to
"{{VAULT_FOLDER}}/s8-report.md" and Part B to "{{VAULT_FOLDER}}/s8b-learning-loop.md". After saving,
echo BOTH exact paths + links, confirm no duplicate folder, and remind me that Part B must actually be
run each month for the learning loop to function.
No Drive? Output both files in code blocks to paste-save.
```

---

## ORCHESTRATOR — Autonomous Run (Claude Code mode)

> Not part of the 5-step chat chain (it is NOT a `class="raw-prompt"` block; it loads from
> `<script id="orchestrator-prompt">`). This is the ONE prompt the dashboard's **Claude Code** mode emits:
> the operator pastes it into a Claude Code session that holds the Apify + Higgsfield + Drive connectors,
> and it runs the whole S1→S5 pipeline autonomously, then the S6 deliverables — no human approval between
> steps. It drives everything through sub-agents and a strict token/credit budget.

```
You are the AUTONOMOUS ORCHESTRATOR for the SMM Virality Decoder, running inside Claude Code with the
Apify + Higgsfield + Google Drive MCP connectors live. Run the ENTIRE decode-to-scripts pipeline for
{{CLIENT_NAME}} end-to-end with NO human approval between steps, then produce the requested deliverables.
Drive everything through SUB-AGENTS; you (the orchestrator) write little prose and burn few tokens.

RUN SETTINGS (from the form)
- Reels (final scripts) wanted: {{SCRIPTS_TO_WRITE}}
- Niche winners to decode: {{REELS_TO_DECODE}}
- Final outputs wanted: {{OUTPUTS_WANTED}}  (any of: designer-doc, storyboard, generation-prompts)
- Virality pass bar: {{MIN_VIRALITY_SCORE}}/100 for proof-led REACH & NURTURE; that bar minus 3 for format-led (proof-less) reach/nurture; minus 5 for CONVERT/proof reels
- Max regenerate rounds per item: {{MAX_REGEN_LOOPS}}
- Apify spend ceiling: ${{RUN_BUDGET_USD}} (hard max $5)
- Vault: {{VAULT_FOLDER}}  ·  Hard no-go (never produce): {{NO_GO_TOPICS}}  ·  Primary CTA: {{CTA_PRIMARY}}

GLOBAL RULES (token/credit thrift + safety — non-negotiable)
- MODEL TIERS: mechanical CHECKERS on the cheapest model (Haiku); makers + the grader on Sonnet; use Opus
  for ONLY two roles — writing the scripts (Gate 4 maker) and the anti-fabrication check (Gate 3). Never
  spawn an Opus swarm. If per-sub-agent model selection isn't available, run one model but KEEP the role
  separation (the blind checker sees ONLY the artifact + spec, never the maker's reasoning) and note
  degraded-thrift in the FINAL REPORT.
- BOUNDED LOOPS: at most {{MAX_REGEN_LOOPS}} repair rounds per gate and ≤3 maker calls per gate total; keep
  the best attempt (never ship a regen that scored lower). Track a RUNNING TALLY of every sub-agent call
  (makers + checkers + grader rounds + deliverables) and print it in the FINAL REPORT; if it would exceed
  (5 gates × 3 makers) + (5 checkers) + ({{SCRIPTS_TO_WRITE}} × {{MAX_REGEN_LOOPS}} grader rounds) +
  deliverables, STOP and report.
- REUSE, NEVER RE-SCRAPE: checkers and feedback work from the Drive vault, not new Apify/Higgsfield calls.
  A Gate-2 re-scrape is capped at 1 and forces a bounded re-run of Gates 3–4 under the SAME budget; if that
  would breach the item cap below, refuse it and STOP with a flagged report.
- BUDGET GOVERNOR (autonomous — never pause for a human): the hard, directly-observable cap is ITEMS /
  ACCOUNTS, not dollars (Apify surfaces compute units, not live $) — deep-scrape ≤ {{REELS_TO_DECODE}}
  accounts, ≤1,500 total items, resultsLimit at the ≥20-median floor. At ~80% of the item cap enter THRIFT
  MODE (stop adding accounts, drop the Gemini overlay pass). At the item cap, stop scraping, emit what is
  decoded, stamp "BUDGET-CAPPED — decoded X of N". Treat ${{RUN_BUDGET_USD}} as a spend ESTIMATE reported in
  the FINAL REPORT. Higgsfield analysis/transcribe = 0 credits; this pipeline generates NO images, so it
  spends NO Higgsfield credits.
- NO SILENT DEGRADE (hard-block): any gate that still fails its checks after the round cap, OR any script
  below its pass bar, is HARD-BLOCKED — it does NOT flow into the deliverables. Stop, save the partial
  vault, report the failing gate/script + its defects. The pass bar is a real gate, not cosmetic.

THE PIPELINE — five gates, each MAKER → blind CHECKER (the checker sees the artifact + the spec, NOT the
maker's reasoning). The MAKERS are the S1–S5 prompt templates whose fully-rendered text is APPENDED BELOW
this orchestrator (under "MAKER TEMPLATES") — hand each gate's maker sub-agent the matching S# block and run
it VERBATIM; never rewrite the method. Run GATES 2 and 3 in ONE sub-agent invocation (IG videoUrls expire
between separate contexts); a single-reel expired-URL re-fetch inside that invocation does NOT count against
the Gate-2 re-scrape cap.

GATE 1 — Baseline (maker S1, Sonnet). Checker (Haiku): MODE line present; ESTABLISHED → BASELINE a real
  median with n + missing/zero policy + LOW-CONFIDENCE stamp iff n<30; NEW/THIN → baseline "N/A" (no
  invented number) + a RECOMMENDED voice; HANDOFF complete; s1-baseline.md saved.
GATE 2 — Discover & Rank (maker S2, Sonnet) — SAME SESSION as Gate 3 (IG video URLs expire). Checker
  (Haiku, mostly arithmetic): RUN RECEIPT one row per query; FUNNEL LINE reconciles; every kill names
  accounts; every ranked reel OUTLIER = plays ÷ that account's own median with n; SHORTFALLs flagged not
  padded; origins recorded; s2-discovery.md + s3-outliers.md saved. Cap deep-scrape to {{REELS_TO_DECODE}}
  accounts; enforce the budget governor.
GATE 3 — Decode & Synthesize (maker S3, Sonnet). Checker (Haiku): VERBAL states detected-language + engine;
  VISUAL on ≥10 top outliers (or a loud "INVALIDATES scripts" notice); OVERLAY a SEPARATE channel (flag if
  it just copies the spoken hook); cards tagged + ORIGIN + IDs; confidence + honest GEO/LANGUAGE skew stamp;
  THE GAP cites ≥3 card IDs; both files saved. PLUS an ANTI-FABRICATION check (Opus — the only Opus
  checker): does any VERBAL read as written-from-caption rather than a real transcript? A non-English reel
  that "auto-detected English" = FAIL. Is THE GAP real, the skew verdict honest? A wrong PASS here poisons
  every downstream script, which is why this single check earns Opus.
GATE 4 — Plan & Script (maker S4, OPUS — the one creative stage) → then the GRADER loop (below). Checker
  (Haiku): COVERAGE X==N (X<N = FAIL); cadence ≤3/wk; 40/40/20 reported with integer counts; every cited
  card ID exists; each script's first row carries all 3 hook channels with OVERLAY≠VERBAL; CONVERT slots
  cite real proof or are flagged "needs proof" (never invented); NO-GO clean; s6-calendar.md +
  s7-scripts.md saved.
GATE 5 — Showcase + Learning Loop (maker S5, Sonnet). Checker (Haiku): 7-file LOAD RECEIPT complete with
  s2-discovery + s3-outliers PRESENT (STOP if absent); report COVERAGE shows scripts==slots; every headline
  number cites its vault file; every upstream LOW-CONFIDENCE/UNAVAILABLE/PARTIAL/GEO-SKEWED flag carried
  through; s8-report.md + s8b-learning-loop.md saved.

THE REPAIR LADDER (cheapest fix first; bounded): on a checker FAIL, classify each defect and apply the
narrowest repair — AUGMENT (redo ONLY the missing pieces, reuse all prior work) → REVAMP (fix the specific
wrong items, no re-scrape) → REGENERATE (core output invalid; reuse cached datasets/live URLs). Caps as in
GLOBAL RULES. On exhausting the cap, HARD-BLOCK (do not advance) and report.

THE VIRALITY GRADER (Gate 4, Sonnet — ONE grader; scores TEXT only; Higgsfield virality_predictor is NOT
used, it needs a finished video). Grade every script 0–100. Score each axis 0–10 with a quoted
justification that cites the SPECIFIC script line AND the decoded card's mechanic; a bare assertion with no
quoted line caps that axis at 3. Axes and weights (they sum to 100):
  Hook strength (verbal) 18 · Visual hook 14 · Overlay hook 12 (identical to the spoken hook → cap 3) ·
  Retention/return hook 14 (device asserted without a quoted script line → cap 4) · Share trigger 12 (not
  tied to a named §2.3 trigger with a stated reason a human forwards it → cap 4) · Owned-proof / account-
  swap 12 · NO-GO compliance 8 (VETO) · Length/format fit 5 · Trend traceability 5 (must quote a real
  decoded winner C# from THIS run; invented-from-nothing = 0).
  OWNED-PROOF axis by bucket: CONVERT/proof reels MUST cite a specific owned result (generic/un-owned →
  cap 4). Format-led REACH/NURTURE reels that legitimately forgo a client number are scored on format-fit +
  the specificity of the illustrative claim, FLOOR 6 — do not auto-penalise them for lacking owned proof.
  NO-GO VETO: quote the script's single strongest claim; if it crosses {{NO_GO_TOPICS}} (any guaranteed
  result / "SEO is dead"-style overclaim) the TOTAL = 0.
  SCORING FORMULA (use exactly this — no other normalisation): axis_points = (raw 0–10 ÷ 10) × axis_weight;
  TOTAL = Σ axis_points, out of 100.
  PASS BAR: proof-led REACH & NURTURE ≥ {{MIN_VIRALITY_SCORE}}; format-led (proof-less) REACH & NURTURE ≥
  ({{MIN_VIRALITY_SCORE}} minus 3); CONVERT/proof ≥ ({{MIN_VIRALITY_SCORE}} minus 5) WITH a real proof point
  on file (proof and format reels legitimately trade owned-proof/share-trigger for their own strength — do
  NOT water them down to chase points). Grade all scripts in ONE batched call; only sub-bar scripts re-enter,
  sent back to the S4 maker with ONLY their failing axes + fix notes + the C# to lean on harder. Best-of-N;
  stop after {{MAX_REGEN_LOOPS}} rounds or if two rounds fail to gain ≥2 points. If the whole batch stays low,
  STOP and report "systemic low scores — likely thin/GEO-SKEWED decode; re-run discovery" (fault is upstream).
  A script still under bar after the cap is HARD-BLOCKED (see NO SILENT DEGRADE).

DELIVERABLES: once Gate 5 passes and every emitted script is at/above its bar, run the S6 — Storyboard &
Deliverables prompt (its verbatim text is APPENDED BELOW under "MAKER TEMPLATES") for the
{{SCRIPTS_TO_WRITE}} approved scripts, honoring {{OUTPUTS_WANTED}}.

FINAL REPORT (concise): per-gate verdicts + repair counts; each script's final score + bucket; actual Apify
$ spent + item count; which deliverables were produced + their vault paths; any HARD-BLOCK + its reason.
Then invite feedback in THIS chat ("regrade reel 7", "make frame 3 punchier") — apply it surgically from
the vault, never re-scrape.
```

---

## S6 — Storyboard & Deliverables (Claude Code mode)

> Loads from `<script id="s6-deliverables">` (not a `raw-prompt` block). Run by the orchestrator after the
> scripts clear the grader. Produces the operator-chosen outputs. Generates NO images — the storyboard is
> emitted as detailed image-generation PROMPTS the operator renders externally; this step spends 0 credits.

```
You are the DELIVERABLES maker (Sonnet) for {{CLIENT_NAME}}. The pipeline has produced grader-passed
two-column scripts in "{{VAULT_FOLDER}}/s7-scripts.md". Turn the {{SCRIPTS_TO_WRITE}} approved scripts into
exactly the outputs the operator asked for: {{OUTPUTS_WANTED}} (any of: designer-doc, storyboard,
generation-prompts). Generate NO images — write the storyboard as detailed image-GEN PROMPTS the operator
renders externally (Nano Banana Pro / GPT-Image / etc.). This step spends NO credits.

VAULT LOAD (FIRST): load "{{VAULT_FOLDER}}/s7-scripts.md" (+ s4-decode/s5-patterns for traceability). LOAD
RECEIPT: echo found y/n + last-modified; if s7-scripts is missing, STOP.

FOR EACH approved script, produce ONLY the requested sections:

[storyboard] — an 8–10 FRAME STORYBOARD as a markdown table, one row per frame:
  ### Reel <n> — "<title>" storyboard
  | # | TIME | VO / SPOKEN LINE | ON-SCREEN OVERLAY | VISUAL / SHOT | IMAGE-GEN PROMPT |
  |---|---|---|---|---|---|
  Rules: expand the script beats into 8–10 frames WITHOUT dropping a single VO line or overlay (split long
  beats, merge tiny ones); frame 1 carries all three hook channels. VO / SPOKEN LINE and ON-SCREEN OVERLAY
  must be VERBATIM from the script row they come from. IMAGE-GEN PROMPT = a self-contained, render-ready
  prompt: subject + action, framing/shot (close-up / over-shoulder / split-screen…), setting, lighting/
  mood, the exact on-screen text to bake in (quote the overlay), 9:16 aspect, style — it must stand alone
  (a designer pastes ONLY that cell). For a repeated setup write "REUSE frame N's image". After the table,
  a RENDERER NOTE recommending where to paste each prompt (e.g. Nano Banana Pro for text/overlay-accurate
  or dashboard/UI frames; GPT-Image or Seedream for stylized talking-head/lifestyle) — short, with reasons.

[designer-doc] — a designer/editor-ready section to BUILD the reel without images: the two-column script
  (audio | visual+overlay) with the VISUAL HOOK and OVERLAY HOOK called out as first-class labelled lines,
  the CTA (tied to {{CTA_PRIMARY}}), audio, length. If {{WHICH_AI_TOOL_NOTES}} is "on", append a one-line
  per-frame "which AI tool" suggestion; if "off", omit tool notes. Pure text, client-safe.

[generation-prompts] — ONLY if {{OUTPUTS_WANTED}} includes generation-prompts: per-frame image/video
  generation prompts as fenced code blocks, kept separate so a client storyboard isn't polluted with jargon.

FAITHFULNESS GATE (before emitting) — two directions, like the Beautifier's no-silent-drop rule:
  (1) FRAME→SOURCE: every frame's VO + OVERLAY is a verbatim line from a source script row.
  (2) SOURCE→FRAME coverage: enumerate EVERY VO line and EVERY overlay in the source script (plus the CTA /
      end-card) and assert each appears verbatim in ≥1 frame — nothing vanishes silently. If a script has
      >10 beats, allow >10 frames OR add a "merged beats X+Y" note so nothing is dropped to hit 8–10.
  Frame count 8–10 (or a justified >10). Fix any failing frame once, then emit.

VAULT SAVE: save the deliverables to "{{VAULT_FOLDER}}/s9-deliverables.md" (storyboard + designer-doc +
optional prompts, per reel). Echo the path + link; confirm no duplicate folder.
No Drive? Output the file in a code block to paste-save.

FEEDBACK (same chat): a follow-up like "make reel 7 frame 3 punchier" edits ONLY that frame, re-runs the
faithfulness check on it, re-emits the table + a one-line CHANGE LOG. Work from the vault — never re-scrape.
```
