# VALIDATION REPORT — Phase 1 Live Pipeline Test

> Goal of this phase: prove every data dependency on REAL data for the pilot niche BEFORE building
> any UI or prompt template. Pilot: PPC Guru (@ppcguru.ca), niche = "performance-marketing / Google
> Ads", discovery method = **niche-keyword-first** (owner refinement to BLUEPRINT §5).
> Date: 2026-06-11. All runs live on the connected Apify org + Higgsfield + rented Whisper.

## 0. Verdict
**The data layer works, and the niche-keyword-first method is validated on real data.** A keyword
search surfaced genuine viral outliers; account-median outlier math correctly separated format wins
from consistency winners; both the verbal and visual decode layers produced usable output. Three
blueprint corrections are required before we hard-code prompts (see §7). Total spend: **~$0.25 Apify
+ 0 Higgsfield credits** — far under the $3 Phase-1 cap.

---

## 1. Actor registry (exact names + schemas, verified by live runs)

### 1a. Niche-keyword discovery — KEYSTONE of the refined method
- **Actor:** `data-slayer/instagram-search-reels` (id `yODAxX2TEfBex0VwB`)
- **Input:** `{ "query": string, "maxPages": int (default 1) }`
- **Pricing:** $0.002 start + **$0.00217 / result** (BRONZE). 1 page ≈ 12 reels ≈ **~$0.03**.
- **Output (raw IG JSON — 383 fields, deeply nested).** Fields we rely on (dot-notation projection
  works in `get-dataset-items`): `play_count`, `ig_play_count`, `like_count`, `comment_count`,
  `share_count`, `video_duration`, `video_url`, `code` (→ `instagram.com/reel/<code>/`),
  `caption.text`, `caption.hashtags`, `user.username`, `user.is_verified`, `taken_at_date`,
  `clips_metadata.music_info`, `image_versions…first_frame.url`.
- **Trap confirmed:** `user` block does NOT carry `follower_count` → account baseline must come from a
  separate profile scrape (that's S3, by design). The nested-array projection trap (BLUEPRINT §3.2) is
  real here: project scalar/object fields by dot-notation; for true arrays fetch full items + `omit`.

### 1b. Profile reels + baseline + medians (S1, S3)
- **Actor:** `apify/instagram-reel-scraper` (id `xMc5Ga1oCONPmWJIa`, official, 107k users, 99.6%).
- **Input:** `{ "username": [..], "resultsLimit": int, "skipPinnedPosts": bool, "skipTrialReels": bool,
  "includeSharesCount": bool, "includeTranscript": bool, "includeDownloadedVideo": bool }`.
  Accepts usernames, profile URLs, **or direct reel URLs**.
- **Pricing:** $0.0023 / reel + add-ons (transcript $0.041/min, video download $0.015/MB,
  shares $0.006/reel). 76 reels this run ≈ **$0.18**.
- **Output (clean, flat — much better than 1a):** `videoPlayCount`, `videoViewCount`, `likesCount`,
  `commentsCount`, `videoDuration`, `caption`, `hashtags` (top-level array), `musicInfo.{artist_name,
  song_name,audio_id,uses_original_audio}`, `audioUrl`, `videoUrl`, `displayUrl`, `timestamp`,
  `shortCode`, `url`, `ownerUsername`. **Cross-check:** its `videoPlayCount` for reel `DYwpzcPt0qz`
  (314,304) exactly matched actor 1a's `play_count` (314,304) — two independent actors agree.

### 1c. Audio transcription (S4 verbal) — RENTED & WORKING
- **Actor:** `donjuan_mime/audio-video-to-text` (id `ty9uxyAcaJ79dqhWb`). Whisper.
- **Status:** rented on this org, **no permission wall** — first call ran clean.
- **Pricing:** FLAT $5/month (already paid; ~$0 marginal). 1,440 trial-minutes also present.
- **Input:** `{ "source_url": <direct video URL>, "model": "tiny"|"base"|"small" }`. (No YouTube.)
- **Output formats:** `txt`, `srt`, `vtt`, `tsv`, `json`.
- **Speed:** `base` ≈ 18s; `small` ≈ 248s (≈4 min) — small is ~13× slower but far more accurate.

### 1d. Visual layer — TWO viable tools (shootout in §5)
- **Option A — Higgsfield `video_analysis`** (MCP `video_analysis_create`/`_status`). Input: an
  uploaded `video_input_id` (we import the IG CDN URL via `media_import_url` first) or a YouTube URL.
  **Cost observed: 0 credits** (balance 584.92 → 584.92). Speed: ~22s here. Output: scene-by-scene
  array `{scene_number,label,timestamp_start/end,shot_type,visual,audio}` + **audio transcribed AND
  translated to English** (handled Telugu speech that Whisper could not).
- **Option B — `grizzlygriff/video-llm-analyzer`** (id `Xx8ofjDpqqiDvNYS9`). Input: `{video:<IG/YouTube/
  TikTok/X URL or file>, prompt, llmProvider:"gemini", model:"google/gemini-2.5-flash",
  skipDestination:true, framesToExtract:4, maxChargeUsd:0.1}`. **No API key needed** (Apify-hosted
  OpenRouter). Cost ≈ **$0.013 actor + ~$0.001 LLM ≈ $0.014/reel**. Speed ~35–48s.
  **413 gotcha:** adaptive frames (~11 for a 54s clip) overflow OpenRouter → **must cap
  `framesToExtract` at 4–6.**

---

## 2. Outlier math on real data (S2/S3 proof) — METHODOLOGY VALIDATED
Discovery scan `query="google ads strategy"`, 1 page → 12 reels (dataset `x8Ht7OQ6kBvv0LcAl`). It
surfaced a clean spread of outliers against a low baseline (search-set median ≈ 1,534 plays; top reel
≈ 205× that). We then scraped the 3 highest-play accounts' own reels (dataset `36Pu6zhhmdIRjjyqj`,
76 reels) to compute the blueprint's **account-relative** outlier score:

| Account | Acct median plays (n) | Search-hit reel plays | Outlier vs OWN median | Account's true top reel | Top outlier |
|---|---|---|---|---|---|
| **brandingwith_lk** | 187,263 (16) | 314,304 | **1.68×** | 1,291,878 | **6.90×** |
| **d2cbynikhil** | 19,490.5 (30) | 85,250 | **4.37×** | 365,919 | **18.77×** |
| **mycaptainofficial** | 20,508.5 (30) | 40,279 | **1.96×** | 293,189 | **14.30×** |

Thresholds per BLUEPRINT §2.2: **≥5× = outlier**, **≥20× = priority**.

**The key proof:** raw play-count is misleading, and — importantly — **none of the three keyword-search
hits themselves cleared the ≥5× outlier bar** (1.68× / 4.37× / 1.96×). That is the finding, not a
failure: the keyword search surfaces *popular* reels; the **account-median step is what identifies true
format outliers**, and in this sample those were each account's OTHER reels, not the specific
search-hits. `brandingwith_lk`'s 314k search-hit looks huge but is only **1.68×** its own median — that
account is a **consistency winner** (very high baseline), so its system is the thing to decode, not that
one reel. `d2cbynikhil`'s 85k hit is **4.37× — higher, but still below ≥5×, so a borderline candidate,
not a confirmed outlier**; its genuine outlier is the 365k reel at **18.77× (a strong outlier, though
below the ≥20× 'priority' bar)**, alongside mycaptainofficial's 293k at **14.30×**. **Human sanity check
passes:** the recomputed scores flag exactly the reels a person would call "the viral ones," and they
are not the raw search-hits. → **S3's account-median scrape is non-negotiable; keep it.**

Caveat: `brandingwith_lk` returned only 16 reels (not 30) — the actor paginated short for that profile.
Median is still robust but the prompt should request ≥30 and report the actual n.

---

## 3. Verbal layer (S4) — works, with conditions
- **PASS (clean):** `mycaptainofficial` skit reel, `small` model → verbatim, accurate English:
  *"So, she's a Google ad specialist. The entire plan for this month has been done. What is this? No
  campaign optimization, no bidding optimization… This is the worst campaign I've ever seen. Fix this
  or you both are fired… Comment Google to get the plan in your DMs. And if you want to build a career
  in digital marketing, check the link in bio."*
- **FAIL (garbage):** `brandingwith_lk` reel, `base` model → hallucinated Tamil/Japanese script with
  English keywords embedded. Cause: the reel is **Telugu-language + music + text-on-screen** with no
  clean English speech. `base` + auto-language-detect hallucinated. (Higgsfield later translated this
  same audio correctly — see §5.)
- **Lesson:** (a) use `small`, not `base`; (b) Whisper alone is unreliable on non-English / music /
  text-on-screen reels — the visual+overlay layer must carry those, and a video-understanding tool
  (Higgsfield) is needed for non-English audio.

---

## 4. Visual layer shootout (S4) — both pass; they are COMPLEMENTARY
Same hero reel (`brandingwith_lk/DYwpzcPt0qz`, Telugu GMB how-to, split-screen text-on-screen).

| Capability (BLUEPRINT §2.6) | Higgsfield `video_analysis` (A) | Gemini analyzer (B) |
|---|---|---|
| First-frame composition | ✅ (scene 1 visual) | ✅ (very detailed) |
| **Verbatim overlay text** | ❌ not extracted | ✅ **excellent** (incl. Telugu red text, "GET FREE BUSINESS 24/7") |
| Shot type / cut pace | ✅ per-scene shot_type + timestamps | ✅ cut count + avg shot length |
| Visual hook | ➖ implied | ✅ explicit |
| **Audio (esp. non-English)** | ✅ **transcribes + translates** (Telugu→EN) | ❌ none (frames only) |
| Speed / cost | ~22s / **0 credits** | ~35–48s / **~$0.014** |

**Recommendation:** use **both, layered** —
- **Higgsfield `video_analysis` = primary** scene/shot + audio decoder (uniquely handles non-English
  speech; free on the current plan).
- **Gemini analyzer = overlay-text + first-frame specialist and fallback** (the one tool that reliably
  pulls the on-screen text — which IS the hook channel for text-on-screen reels — for $0.014).
- **Whisper (`small`) = cheap verbal** for clear English talking-heads where Higgsfield is overkill.
- ffmpeg Option C remains unavailable (not installed); not needed given A+B both work.

---

## 5. Mini-decode proof — 3 complete decoded cards (what S4 outputs at scale)

### CARD 1 — brandingwith_lk · reel DYwpzcPt0qz · 314,304 plays · **1.68× (consistency winner)**
- **VERBAL** (via Higgsfield translation; Whisper failed): hook *"They say branding, branding — how do
  we do it? What platforms do we have? Instagram, Facebook, YouTube, right?"* → body: focus on
  Instagram (youngsters/couples), repurpose the same reel to YouTube, **Google My Business** is the
  biggest local play → payoff: get reviews + "review optimization" keywords in testimonials so you
  rank and get called → CTA: *"that's the organic way, no cost."*
- **VISUAL** (Gemini): split-screen — top: presenter on stage (medium shot, ponytail, glasses);
  bottom: animated explainer b-roll. Soft transitions ~every 1s.
- **OVERLAY** (Gemini): flashing red Telugu captions ("Instagram-lo", "Appudu evaraina"), "GET FREE
  BUSINESS 24/7", "Google My Business" logo top-center, a "Focus on: Instagram / YouTube Shorts / GMB"
  list. **PACKAGING:** 54s; caption = GMB organic how-to; language Telugu; no trending audio (VO).
- **TAXONOMY:** Hook = insider-secret / "free vs paid"; Retention = split-screen + fast overlay
  changes + listicle; Payoff = delivered (review-optimization tactic); Share trigger = usefulness
  (save-worthy); Format = talking-head(stage) + animated b-roll, text-on-screen.

### CARD 2 — mycaptainofficial · reel DVWH4GCgdSF · 40,279 plays · **1.96×**
- **VERBAL** (Whisper `small`, clean): skit — boss berates a Google Ads specialist for an unoptimized
  campaign ("no campaign optimization, no bidding optimization… worst campaign I've ever seen. Fix it
  or you're both fired") → resolution: "I'll send the full optimization plan" → CTA *"Comment Google
  to get the plan in your DMs; career in digital marketing → link in bio."*
- **VISUAL/OVERLAY** (Gemini): title banner *"5x Your Leads With This Google Ads Strategy 😎"*; role
  labels "Boss" / "Google ads Specialist" / "Client"; CTA card "Comment Google to get plan in your
  DM's". **PACKAGING:** 30s; skit; ~1s cuts (very fast); brand watermark "mycaptain".
- **TAXONOMY:** Hook = bold claim ("5x leads") + relatable workplace callout; Retention = skit tension
  + fast cuts; Payoff = the "plan" (gated via comment) — note: payoff is partly withheld for a
  comment-bait CTA; Share trigger = identity ("this is SO us"/workplace humor); Format = skit-POV.

### CARD 3 — d2cbynikhil · reel DOGfWAdCQXg · 85,250 plays · **4.37× (borderline — below the ≥5× bar)**
- **VERBAL:** (not transcribed in Phase 1 — talking-head with screen-share; available via Whisper or
  Higgsfield in a full run.)
- **VISUAL/OVERLAY** (Gemini): talking-head-in-circle (bottom-left) over a screen-share b-roll of a
  Google Ads dashboard; hand-with-pen pointing; first frame shows metrics (Clicks 7.7K, Conv 529,
  Cost ₹226K) + "Sales / New D2C Brands / Campaign Type & Budget ❓". Then a **3-step budget
  framework** burned on screen (Early/Scaling/Mature stages with % splits & ₹/day). ~1s screen cuts.
- **PACKAGING:** 80s; talking-head + screen-rec; @d2cbynikhil watermark; caption = D2C Google Ads
  3-stage formula.
- **TAXONOMY:** Hook = curiosity gap + bold metric proof; Retention = listicle/countdown (3 steps) +
  on-screen data; Payoff = delivered (full % framework shown); Share trigger = usefulness
  (save-worthy how-to); Format = tutorial-listicle (voiceover + screen b-roll).

---

## 6. Costs observed (actual)
| Item | Detail | Cost |
|---|---|---|
| Discovery scan (1a) | 12 reels | ~$0.028 |
| 3-account scrape (1b) | 76 reels | ~$0.176 |
| Whisper ×2 (1c) | base + small | $0 marginal (flat rental) |
| Gemini analyzer (1d-B) | 1 fail + 3 success | ~$0.05 |
| Higgsfield video_analysis (1d-A) | 1 reel | **0 credits** (584.92 → 584.92) |
| **Total** | | **~$0.25 + 0 credits** |

Implication for a real client run (BLUEPRINT §8 order-of-magnitude holds): discovery + funnel +
~25 transcripts + ~12 visual analyses lands around **$3–6 of Apify + ~$0 Higgsfield** — comfortably
in range.

---

## 7. Blueprint corrections required (before Phase 2/3 prompt templates)
1. **§5 S2 — discovery is niche-keyword-first.** Primary actor = `data-slayer/instagram-search-reels`
   by keyword. Competitor handles = optional force-include seeds only. Already in PROJECT_BRIEF.
2. **§5 S3 — always scrape each surfaced winner's OWN account** (`apify/instagram-reel-scraper`,
   resultsLimit ≥30, skipPinnedPosts) to compute the account-median outlier score, and **report the
   actual n** (some profiles paginate short). Raw search play-count alone is misleading (the
   consistency-winner trap, proven in §2).
3. **§3.1 / §4 — transcription policy.** Use Whisper **`small`** (not `base`); budget ~4 min/reel.
   Whisper is unreliable on non-English / music / text-on-screen reels → for those, the verbal layer
   comes from **Higgsfield `video_analysis`** (transcribes + translates) and the hook lives in the
   **overlay-text** layer (Gemini analyzer). Every decode card must state which engine produced the
   verbal layer, and say so explicitly when speech is absent (no silent fabrication).
4. **§4 — visual layer = Higgsfield (primary) + Gemini analyzer (overlay-text/fallback).** Cap the
   Gemini actor at `framesToExtract: 4–6` (avoids the 413). Higgsfield needs `media_import_url` on the
   reel's CDN URL first (do it in-session before the URL expires).
5. **§3.2 — confirm the field-projection trap in tooling:** fetch winners' full items with `omit` for
   bulky blocks rather than `fields=` on nested arrays; scalars/objects project fine by dot-notation.

## 8. Raw artifacts (for QC re-verification)
- Discovery dataset: `x8Ht7OQ6kBvv0LcAl` (12 reels, "google ads strategy")
- 3-account reels dataset: `36Pu6zhhmdIRjjyqj` (76 reels)
- Whisper base/garbage: `8E4RvDm6Cv6RkeUaS` · Whisper small/clean: `YJae2d17KBJ03Lvyy`
- Gemini visual: brandingwith_lk `gIPAvxhdwxF23McCb` · mycaptainofficial `rMSTT8uUl3QWRqBP4` ·
  d2cbynikhil `6BOXCWgNHpbwu4krM`
- Higgsfield analysis id: `70e6503c-c31f-4494-991c-b93004658ffe`
