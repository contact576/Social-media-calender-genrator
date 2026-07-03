# COMMERCIALIZATION.md — from internal tool to paid product

*Prepared 2026-07-03 from a four-track audit (product architecture · pipeline reliability ·
UX/onboarding · legal + unit economics). This is the owner's decision document: what was already
fixed, what still stands between today's tool and charging strangers money, which business model to
launch with, and the build plan. It is a research memo, not legal advice — items marked ⚖️ warrant
one hour with a Canadian tech lawyer before public launch.*

---

## 1 · Executive verdict

The valuable asset is the **validated methodology** — `PROMPTS.md` + the proven data-layer facts
(account-relative outlier math, exact actor inputs, anti-fabrication gates). The dashboard is a thin,
well-guarded renderer around it. What exists today is a strong **internal operator tool**; it is
**not yet a self-serve product** (no accounts, no payments, no hosted execution — the customer would
need their own Claude + Apify + Drive stack and the skill to drive a 5-step agent pipeline).

**The fastest legitimate path to revenue is NOT building a SaaS first.** It is selling the
*deliverable* (a productized "Niche Virality Report") while the SaaS is built behind it — every paid
concierge run doubles as a live pipeline test.

## 2 · What this hardening pass already fixed (shipped on this branch)

| Area | Fix |
|---|---|
| **Geo-skewed discovery** (the "why only Indian creators?" problem) | S2 now runs a mandatory **GEO leg** (keyword + city/country queries derived from `GEO_PRIMARY`), buckets every account TARGET-MARKET / CULTURE-MATCH / GLOBAL, enforces a **MARKET MIX quota** (≥5 target/culture reels in the decode set, shortfall printed honestly), caps FORMAT-ONLY reels at 8, and prints an **ORIGIN MIX line**. Geography alone is no longer a kill; language mismatch is. |
| **Output language** | S4/S6 now write scripts, overlays, captions and hashtags in `LANGUAGE_PRIMARY` (wrong-language output = checker FAIL). Non-English clients were previously getting English scripts. |
| **Decode-layer truth** | Higgsfield `video_analysis` fully removed as an instruction (it is not callable); grizzlygriff is the sole (best-effort) visual engine; docs/README/prompt-preamble all reconciled to the live-verified state. Higgsfield connector no longer required at all. |
| **Proof for CONVERT reels** | New optional intake field `PROOF_ASSETS`; the grader's NO-PROOF CLIENT RULE re-weights instead of hard-blocking the whole CONVERT bucket when a client legitimately has no proof yet. |
| **Autonomous-mode coherence** | Grader **write-back** (post-grade scripts overwrite s7 before S5/S6 read it), BLOCKED-script stamps that don't break coverage, RESUME-from-vault rule, budget item-cap derived from the customer's `RUN_BUDGET_USD` (~350 items/$), THRIFT mode now protects the visual pass (26/100 grader points) instead of cutting it first, bucket labels pinned at Gate 4 (no re-labeling to reach a lower bar), grading in ≤5-script batches, Gate-2 datasetId spot-checks against fabricated numbers. |
| **Thin niches** | SEARCH-ACTOR health probe (dead actor ≠ thin niche), Leg-0 keyword EXPAND, MINIMUM-POOL GATE that stops **before** deep-scrape money is spent. |
| **Customer-grade UX** | "Before your first run" setup checklist (Claude plan + Apify account + Drive + connectors), cost disclosure ($2–6/run), per-step **"Done when"** success criteria, correct step pairing (2+3 same sitting), all stale 8-step copy removed, mode-adaptive Prompts tab, honest privacy footer, accessibility (labels/for, aria-required, role=alert, tab roles), how-it-works strip + one-click sample report. |
| **Cadence** | Calendar honors the client's stated capacity up to 7 reels/week (was silently capped at 3 — pilot residue). |

## 3 · What still stands between here and charging money

### Blockers (cannot take a stranger's money without these)
1. **BYO-everything dependency.** A paying customer has no Claude+Apify+Drive stack. Either you run
   it for them (Model A below — zero new code) or a hosted worker runs it via the Anthropic API +
   Apify REST API with your keys (Model B — 15–20 build days).
2. **⚖️ Anthropic consumer-subscription terms.** Serving third parties through a claude.ai
   subscription is prohibited (actively enforced since early 2026). Model A (sell the report, human
   operator on your own account — cleanest on a Team/commercial seat), Model C (agencies bring their
   own Claude), or the API (Model B) are the compliant shapes. Never resell access to your own chat.
3. **No accounts, no billing, no legal surface.** Zero user model; nothing takes money; no ToS,
   privacy policy, or refund policy anywhere. Stripe is the obvious rail (the Stripe connector
   attached to this workspace still needs OAuth authorization before Claude can wire it).
4. **The autonomous mode has never completed a live end-to-end run.** Scrape/rank/guardrails are
   live-validated; the full orchestrator run is not. Run ≥1 full autonomous run on a fresh
   (non-PPC-Guru) client before any money changes hands.
5. **Budget control is prompt-text, not code.** Fine when it's your own money; for hosted paid runs
   the item caps / loop bounds / kill-switches must be enforced by the orchestrating process (the
   templates stay as payloads).

### Majors (can charge, but churn/margin risk)
- **Fragile third-party decode actors** (single-maintainer; visual layer ~68% success, no viable
  replacement in the Apify Store today). Hosted v1 should own the decode: CDN video → Whisper API /
  Deepgram + ffmpeg frames → Claude vision. Keep actors only for scrape/discovery (proven,
  commoditized).
- **No job orchestration/observability/refund story** for hosted runs (durable job runner —
  Inngest/Trigger.dev — one step per gate; per-gate logs with tokens/$; degraded-run credit policy).
- **No prompt-pack/model versioning on outputs** (stamp runs with template SHA + model IDs; re-run
  grader calibration on any model bump).
- **Garbage-in risk on self-serve intake** (keyword quality is the pipeline keystone) → intake
  copilot: customer gives name/website/handle, an LLM drafts keywords/ICP for confirmation.
- **Report delivery is manual** (Beautifier → print). Hosted: headless-Chromium PDF of the same
  house-style HTML → signed link + email; tenant logo/colors for white-label.

### Minors
Real domain (the current URL carries the "calender-genrator" typo) · marketing-page analytics ·
add `contact576` as a Vercel team member (permanent deploy-block fix) · second intake example
(a local business) so the fixture doesn't anchor everyone to marketing agencies.

## 4 · Business model & pricing (recommendation)

**Sequence: A now → C for scale → B only after A proves repeat demand.**

| Model | What it is | Price | Marginal COGS | Notes |
|---|---|---|---|---|
| **A — "Niche Virality Report"** (start here) | Customer pays + fills intake; your operator runs the existing pipeline; branded PDF + calendar + scripts delivered in 3–5 business days | **$349 one-time** (test $249–499); Learning-Loop refresh **$99/mo** upsell | ~$1–3 Apify + 1–2 h operator | Zero new engineering. Every run is a paid pipeline test. Price against agencies ($1.5–4K for equivalent work), not $6/mo idea tools. |
| **C — Agency white-label license** | Agencies get the dashboard + playbook + N reports/mo, run on **their own** Claude/Apify accounts | **$499/mo (4 reports) – $999/mo (10)** | ≈$0 (their compute) | Sidesteps the Anthropic-terms issue entirely; ~95% gross. The current architecture was literally built for this shape. |
| **B — Self-serve SaaS** | Hosted backend runs the pipeline via Anthropic API + Apify REST; customer sees form → progress → report link | **$79/mo solo · $199/mo pro** | ~$3–10/run (Sonnet-class tokens + Apify) → 85–90% gross | The only model matching "any business fills a form". ~15–20 build days AFTER the live-run validation. |

**Unit economics (measured + estimated):** Apify $0.50–2 typical (hard cap $5 ≈ 1,500 items);
transcription ~$0.002/reel; LLM $0 in service mode (operator's subscription) or ~$2.50–6/run at
Sonnet-class API pricing with caching (batch −50%). Stripe 2.9% + C$0.30. Worst-case COGS ≈ $16.

## 5 · ⚖️ Legal / compliance checklist (before first paid customer)

1. **Customer ToS**: no-guarantee-of-virality; platform-risk clause (sources may change/fail →
   substitute or refund); customer owns delivered scripts, you keep the methodology; liability capped
   at fees; "not affiliated with Meta/Instagram/Anthropic"; indemnity mirroring Apify's.
2. **Refund policy**: re-run or refund if the deliverable isn't produced; never refunds on "it
   didn't go viral". Degraded runs (e.g. visual layer down) → automatic partial credit.
3. **Privacy policy (PIPEDA)**: what's collected, why, 30-day purge of raw scraped data (keep
   aggregates + URLs), Claude/Apify/Drive named as processors, creator opt-out email. Note: Canada's
   regulators treat scraped social data as personal information — "it's public" is not a defence
   here; low volume + business-context + short retention is the mitigation posture.
4. **Scraping posture** (keep as-is — it is the defensible pattern per *Meta v. Bright Data*, 2024):
   public data only, logged-out, no owned accounts touching Instagram, low per-run volume, all access
   through Apify (their infra, your responsibility contractually — mirror it downstream).
5. **Copyright**: transcripts stay internal (reports quote at most short hook lines with credit);
   grader keeps the anti-copying gate. Deliverables carry an "AI-generated content" disclosure line.
6. **Business basics (Canada)**: incorporation recommended for liability separation (~$200–400);
   GST/HST registration required at $30K worldwide taxable revenue (consider voluntary early
   registration to reclaim ITCs); separate business bank account; keep the per-run spend ledger.
7. **Run paid work off the personal consumer Claude account** (Team/commercial seat for Model A;
   customers' own accounts for C; API for B).

## 6 · Build plan (phase-gated, 1–3 days each)

- **P0 — Take money** (1–2d): domain, landing page + sample report, Stripe Payment Link, hosted
  intake capture, ToS/privacy/refund/disclaimer. *First customer possible here.*
- **P1 — Prove the pipeline** (2–3d): one full live autonomous run on a fresh client; fix whatever
  it surfaces; stamp generated prompts with template SHA+date; add `contact576` to Vercel.
- **P2 — Concierge ops kit** (2d): run ledger (cost/duration/defects), delivery checklist,
  headless-PDF export, 2–3 anonymized sample reports. *Serve the first 5–10 customers here.*
- **P3 — SaaS skeleton** (3d): Next.js + Supabase (auth/DB/storage) + Stripe Checkout/webhooks +
  intake form port + intake copilot.
- **P4–P6 — Hosted worker** (3d each): durable job runner with Gates 1–2 via Apify REST
  (code-enforced caps + spend ledger) → first-party decode (Whisper API + ffmpeg + Claude vision) →
  Gates 4–5 + grader loop in code with pinned models; report renderer → delivery email.
- **P7 — Customer surface + safety** (2–3d): run-status page, downloads, failure→credit automation,
  admin re-run-from-gate, Sentry + cost alerts.
- **P8 — Self-serve beta** (1–2d): 10-customer closed beta with human review of every output;
  go/no-go on removing the human.

Concierge revenue after **P0–P2 (~5–7 days)**; self-serve after **P3–P8 (~15–19 days)**, de-risked
and funded by the concierge runs in between.

## 7 · Known open technical gaps (tracked honestly)

- **Visual/overlay decode is best-effort** until the hosted first-party decode exists — grizzlygriff
  is the only multimodal frame actor in the Apify Store and fails ~1 run in 3; the pipeline degrades
  honestly (VERBAL + PACKAGING) rather than fabricating.
- **Full autonomous E2E run still unvalidated live** (see P1). Sub-agent MCP-connector inheritance in
  the operator's own Claude Code session is the specific thing to confirm.
- **Whisper fallback requires a ~$5/mo rental** if the default transcriber ever breaks.
