# PROJECT BRIEF — SMM Virality Decoder

> Phase 0 output. Source of truth for the pilot engagement. Pairs with `BLUEPRINT.md` (methodology)
> and `KICKOFF_PROMPT.md` (phase gates). Produced from the owner interview + a verified environment
> inventory. Status: **GATE 0 approved.**

## 1. What we are building (the end goal — read first)
A **repeatable dashboard tool** (single-file `index.html`), not a one-time research deliverable.
The operator fills an intake form → the tool generates the **S1–S8 copy-paste prompt chain** → the
operator runs each prompt against the connectors (Apify / Whisper / visual / Drive) → a **Beautifier**
renders the research + scripts into a branded report. The PPC Guru run in Phase 1 is a **test fixture**
to de-risk the prompt templates before they are hard-coded — it is not the product.

## 2. Pilot client
- **Client / handle:** PPC Guru — `@ppcguru.ca`
- **Niche:** performance-marketing / lead-gen agency for local service businesses.
- **Services (priority order for this engagement):**
  1. Google & Meta Ads management (frustrated-buyer angle)
  2. AI Visibility / AEO
  3. Website & Funnel development
  4. AI Clone / Avatar video
  5. Social Media Management
- **Geo:** GTA primary; Canada + USA wider.
- **Language:** English primary; Hindi/Gujarati hooks available for the South-Asian diaspora-owner
  (WhatsApp-first) segment.

## 3. Voice & guardrails
- **Brand voice:** blunt, confident, proof-driven.
- **No-go (hard):** no "we guarantee results"; no "SEO is dead / nobody uses Google". These overclaims
  repel the experienced buyer the agency targets. Further no-go topics: owner's call as they arise.

## 4. Strategy inputs
- **Posting capacity:** 2–3 reels/week. Founder-shot on phone for trust pieces; AI avatar (Higgsfield)
  for the rest — which doubles as a live demo of the AI-clone service; some fully AI / storytelling
  videos with no on-camera talent. Editing in-house (Vanshika + video editor).
- **Content pillars:**
  1. Education
  2. Social Proof / Case Studies
  3. Origin / Founder Story
  4. Contrarian / Industry-callout *(added for the frustrated-buyer ICP, e.g. "why your agency's
     reports are lying to you")*
- **Adjacent niches for transplant (all approved):**
  1. Agency-growth / "day in the life of an agency owner" creators (business-money niche) — highest
     format-transfer for the voice.
  2. Own client verticals (home services, realtors, clinics) — repurpose real client results; the
     agency owns the proof.
  3. AI / tech creators — fits AEO + AI-clone services; rides the AI-curiosity wave.

## 5. Discovery method — refinement to BLUEPRINT §5 (S2), owner-directed & approved
**Niche / keyword / hashtag search is the PRIMARY discovery engine**, not competitor handles.
We decode the high-outlier reels a niche search surfaces (e.g. "google ads strategy", "basement
renovation"), regardless of which account posted them. **Rationale:** the outlier score already
rewards content that beat its own account baseline; named local competitors mostly underperform on
social and would waste scrape runs. **Competitor handles become optional force-include seeds only.**
Architectural consequence (Phase 2): the intake form's primary discovery field is "niche search terms
/ hashtags" (required); "known competitor handles" is optional; S3 outlier math scrapes only the
*winning reels' own accounts* for medians; adjacent-niche transplant seeds are expressed as keyword
sets too.

## 6. Operators & ops
- **Primary operator:** Vanshika (Creative Manager) — employee-proofing tuned for **moderate** tech
  comfort, not developer-level.
- **Oversight:** Vihar (PM). **Backup:** Shrikaanth (high tech comfort).
- **Research Vault folder:** `PPC Guru — SMM Virality Vault` (Google Drive, ppcguru.ca workspace).

## 7. Environment inventory (verified this session — not assumed)
| Capability | Status | Notes |
|---|---|---|
| Apify MCP | ✅ live & billed | A paid actor (Facebook-ads scraper) ran this session, ~$0.06 billed → org is live and billed. Whisper actor `donjuan_mime/audio-video-to-text` rental **to be confirmed on first IG scrape** (may throw a one-time permission link). |
| Higgsfield MCP | ✅ live | `video_analysis` (visual decode candidate) + `virality_predictor`. **584.92 credits, Plus plan.** |
| Google Drive | ✅ live | Authed to the **ppcguru.ca** Workspace. No vault folder exists yet (create in Phase 1/4). |
| Web search | ✅ live | Available. |
| ffmpeg / ffprobe | ❌ NOT installed | Blueprint **Option C** (frame-grid visual) unavailable here → visual layer relies on Higgsfield (A) + Gemini Apify actor (B). |
| GitHub MCP | ✅ live | Repo scope: `contact576/social-media-calender-genrator`. |

## 8. Tooling decisions
- **`virality_predictor` — DROPPED from this task.** It scores an existing *video*, not a script or a
  competitor's decoded reel, so it is useless for research/decode. **Parked** for later use: QC gate on
  PPC Guru's own AI-avatar drafts before posting (Phase 6 / production).
- **`video_analysis` — tested on exactly ONE reel in Phase 1**, with exact credit burn reported;
  full-run credit budget decided at GATE 1. Caveat: it accepts only a YouTube URL or an uploaded
  video, so an IG reel must be pulled and uploaded first.
- **Visual-layer shootout (Phase 1):** same reel through Higgsfield `video_analysis` (credits) **and**
  a Gemini video-understanding Apify actor (dollars); recommend primary + fallback at GATE 1.

## 9. Cost guardrail
- **Phase 1 live validation held under $3 total** (realistically < $1 Apify scraping + a few Higgsfield
  credits). Owner pinged before any single run exceeds **$5 / 1,500 items**, and before exceeding the
  $3 Phase-1 envelope. Actual credits/$ reported in every scraping phase.

## 10. Open items to resolve during Phase 1
- Confirm Whisper actor rental on this Apify org (capture approval link if it errors).
- Lock exact actor names + input/output field schemas for IG profile/reels, IG keyword/hashtag → top
  reels, and the Gemini visual actor.
- Measure Higgsfield `video_analysis` credit cost on one reel.
