# RESUME HERE (handoff note)

If you're a fresh Claude session: **read `CLAUDE.md` first** (full architecture + status), then this.

## Status: SMM Virality Decoder is SHIPPED
- Live app: `index.html` on `main`; Vercel auto-deploys on push to `main`.
  URL `social-media-calender-genrator.vercel.app` (this sandbox can't fetch vercel.app — verify in a browser).
- Source of truth for prompts: `PROMPTS.md` → `python3 inject_prompts.py`. Verify: `node selftest.mjs` (~45 checks).

## The chain is now FIVE steps (condensed from eight)
The dashboard generates **S1–S5**. Tightly-coupled stages were fused to cut operator copy-pastes, with no
loss of analysis; each merged step still saves its distinct vault files:
- **S1** Client Baseline → `s1-baseline`
- **S2** Discover & Rank (was discovery + outlier harvest) → `s2-discovery` + `s3-outliers`
- **S3** Decode & Synthesize (was decode + pattern synthesis) → `s4-decode` + `s5-patterns`
- **S4** Plan & Script (was calendar + scripts; two-column shooting-script format) → `s6-calendar` + `s7-scripts`
- **S5** Showcase Report + Learning Loop → `s8-report` + `s8b-learning-loop`

Scripts are written as **two-column shooting scripts** (TIME | AUDIO | VISUAL & TEXT) with a per-reel
Hook/CTA/Why-viral footer; S2–S4 carry **account origin (geo/language)** and S3 runs a **geo-skew guard**;
S5's report **shows the research** and includes a script for **every** calendar slot.

## Notes
- PPC Guru was the **test fixture** (do not re-run it). Its vault + the branded PDF/`PPC_GURU_FINAL_REPORT.*`
  in the repo are the older one-column 8-step artifacts — illustrative only; the canonical process is the
  5-step `PROMPTS.md`. `SAMPLE_PROMPTS_PPCGURU.md` is a legacy 8-step rendered sample.
- Open (owner's call): keep the in-app **Beautifier** as the client export (recommended), or productionize
  the `make_report_pdf.py` branded-PDF generator as a first-class export.

## How to continue
Edit `PROMPTS.md` → `python3 inject_prompts.py` → `node selftest.mjs` → commit → merge to `main` (auto-deploys).
