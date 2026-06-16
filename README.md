# SMM Virality Decoder

A **single-file, keyless web app** (`index.html`) that turns a client intake form into five
copy-paste prompts (S1–S5). An operator runs those prompts in a Claude chat that has the
**Apify + Higgsfield + Google Drive** connectors; the chat does the scraping/decoding and saves results
to a Google Drive "vault". The dashboard itself makes **no network calls and holds no API keys** — it
only generates text and renders the final report.

**What it does:** research what's *actually* going viral in a client's niche → decode *why* (visual +
verbal + packaging) → write viral reel scripts and a 30-day calendar **from that evidence.** It does not
predict whether a not-yet-made video will go viral; it writes from what already won.

---

## Operator quick-start (for Vanshika)

1. **Open the dashboard** (the live link, or `index.html` in any browser).
2. **Intake form** — fill every field marked with a red `*`. Hover the help text under each field for an
   example. The Google Drive folder name auto-fills from the client name.
3. Press **Generate prompts →**. The **Prompts** tab fills with S1–S5.
4. Open the **connected Claude chat** (the one your admin set up with Apify + Higgsfield + Google Drive).
   Pasting these into regular ChatGPT or plain Claude will **not** work.
5. **Run them in order, S1 → S5.** Copy one (the "Copy step N" button), paste it, let it finish, and let
   it **save to Drive**, then do the next. Don't skip ahead — each step loads the previous step's files.
   (S2, S3 and S4 each save **two** vault files — that's expected.)
6. Run **S2 and S3 in one sitting** — S2 grabs the reels and S3 decodes them, and Instagram video links
   expire within hours.
7. When you reach **S5**, copy its report, open the **Beautifier** tab, paste it, and press
   **Render report → Print / Save as PDF** for the client-ready document.

That's it. The "System check" tab is for developers; you only touch it if a red banner asks you to.

---

## Troubleshooting (the things that actually happen)

- **An actor says "rent the actor" / "approve permissions"** — copy the link it shows to the owner; they
  click it once in the Apify console, then re-run that prompt.
- **Whisper transcription says its free trial expired** (`donjuan_mime/audio-video-to-text`) — you have
  two options: (a) rent it for **$5/mo** in the Apify console, or (b) let **Higgsfield `video_analysis`**
  do the verbal layer instead — it transcribes **and** translates (great for Hindi/Hinglish reels). The
  S4 prompt already tells the chat to fall back to Higgsfield; nothing breaks, the transcript just comes
  from Higgsfield.
- **A video link gives a 403 / "expired"** — re-scrape that single reel in the same chat before decoding
  it. Never let the model write a transcript from the caption.
- **A later step says a vault file is missing** — go back and confirm the earlier step actually saved to
  Drive (each step echoes the saved path).
- **Red banner at the top of the dashboard** ("this tool has a problem") — don't run the prompts; tell
  the developer. It means the template and the form fields are out of sync.

## Cost notes (so there are no surprises)

- **Apify** (scraping) is pay-as-you-go and cheap: a full client research run is ~**$2–6** of Apify
  (the PPC Guru rehearsal cost **under $1**). Discovery/median scrapes are a few cents each.
- **Whisper actor:** flat **$5/month** if you choose to rent it (optional — Higgsfield covers the verbal
  layer for free).
- **Higgsfield `video_analysis` (the decode/transcription we use) costs 0 credits** — verified against an
  unchanged credit balance and an empty transaction log. **Only Higgsfield video *generation*** (your
  separate AI-avatar production: Seedance/Kling/Nano-Banana) spends credits. The Decoder never generates.
- **The dashboard + Beautifier:** $0 — static page, no accounts, no calls.
- Guardrail: ask the owner before any single scrape run is expected to exceed **$5 / 1,500 items**.

---

## Setting the connected-chat link

The Prompts tab shows a note telling operators where to paste. When you have the shareable link to your
connected Claude chat, open `index.html`, find `data-chat-link` near the top of the Prompts section, and
put the URL there (one line) — the note becomes a clickable button. Until then it reads "ask your admin".

## How to change a prompt (developers)

The five templates are the single source of truth in **`PROMPTS.md`**. Edit there, then run
`python3 inject_prompts.py` to re-embed them into `index.html`. Never hand-edit the `raw-prompt` blocks
in `index.html`. Verify with `node selftest.mjs` (engine + parity + reconciler, no dependencies).
See `CLAUDE.md` for the full architecture.

## Deploy

Static single file — host anywhere. This repo auto-deploys `index.html` to Vercel on push to the
default branch. To redeploy manually, drag `index.html` onto vercel.com or run `vercel` in the repo.

---

## Roadmap (v2 ideas — parked on purpose)

- **Optional pre-post check** — after an editor cuts a reel, score it with Higgsfield's
  `virality_predictor` before publishing (it scores a *finished video*, and spends credits — verify cost
  first). Deliberately left out of v1; the owner's goal is decode-then-write, not grade-before-post.
- Auto-posting / scheduling · TikTok + YouTube Shorts as leading indicators · comment-sentiment mining ·
  multi-client trend dashboard · the monthly **Learning Loop** as a one-click re-run (S5 Part B / s8b per client).
