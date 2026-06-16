#!/usr/bin/env python3
"""Render the PPC Guru final report as a branded, client-ready PDF.
Two-column shooting scripts (AUDIO | VISUAL & TEXT) + per-reel Hook/CTA/Why-viral.
Standalone: embeds DejaVu (Unicode) and stubs the sandbox's broken `cryptography`
import that fpdf2 pulls in. Run: python3 make_report_pdf.py"""
import sys, types
for _n in ["cryptography", "cryptography.hazmat", "cryptography.hazmat.primitives",
           "cryptography.hazmat.primitives.serialization",
           "cryptography.hazmat.primitives.serialization.pkcs12"]:
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.modules["cryptography.hazmat.primitives.serialization"].pkcs12 = \
    sys.modules["cryptography.hazmat.primitives.serialization.pkcs12"]

from fpdf import FPDF
from fpdf.fonts import FontFace

NAVY = (20, 33, 61)
GOLD = (255, 214, 10)
INK = (28, 36, 48)
GREY = (90, 102, 120)
LIGHT = (246, 248, 251)
AUDIOBG = (235, 242, 249)
VISBG = (244, 246, 240)
REACH = (29, 111, 184)
NURTURE = (46, 139, 87)
CONVERT = (192, 57, 43)
FLAG = (176, 106, 0)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FI = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
TYPE_COLOR = {"REACH": REACH, "NURTURE": NURTURE, "CONVERT": CONVERT}


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("D", "", 7.5)
        self.set_text_color(*GREY)
        self.cell(0, 6, "SMM Virality Decoder  ·  PPC Guru  ·  June 2026", align="L")
        self.cell(0, 6, f"{self.page_no()}", align="R")


import os
F_I = FI if os.path.exists(FI) else F
pdf = PDF(format="A4")
pdf.set_auto_page_break(True, margin=16)
pdf.add_font("D", "", F)
pdf.add_font("D", "B", FB)
pdf.add_font("D", "I", F_I)
pdf.set_margins(16, 16, 16)
pdf.add_page()
EPW = pdf.epw


def h2(num, title):
    pdf.ln(3)
    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.set_font("D", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, f"{num} · {title}", new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y()
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.1)
    pdf.line(16, y, 16 + EPW, y)
    pdf.ln(3)


def para(text, size=10, color=INK, gap=2):
    pdf.set_font("D", "", size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 5.2, text, new_x="LMARGIN", new_y="NEXT", markdown=True)
    pdf.ln(gap)


def callout(text, accent=GOLD, bg=(255, 248, 225)):
    pdf.set_font("D", "", 9.7)
    lines = pdf.multi_cell(EPW - 10, 5.2, text, dry_run=True, output="LINES", markdown=True)
    h = len(lines) * 5.2 + 6
    if pdf.get_y() + h > 272:
        pdf.add_page()
    start_y = pdf.get_y()
    pdf.set_fill_color(*bg)
    pdf.rect(16, start_y, EPW, h, style="F")
    pdf.set_fill_color(*accent)
    pdf.rect(16, start_y, 1.8, h, style="F")
    pdf.set_xy(20, start_y + 3)
    pdf.set_text_color(*INK)
    pdf.multi_cell(EPW - 10, 5.2, text, new_x="LMARGIN", new_y="NEXT", markdown=True)
    pdf.set_y(start_y + h + 3)


def bars(rows, maxw=86):
    mx = max(v for _, v, _ in rows)
    pdf.set_font("D", "", 9)
    for label, val, note in rows:
        if pdf.get_y() > 270:
            pdf.add_page()
        y = pdf.get_y()
        pdf.set_text_color(*INK); pdf.set_xy(16, y); pdf.cell(64, 6, label)
        w = max(1.5, maxw * val / mx)
        pdf.set_fill_color(*REACH); pdf.rect(82, y + 1, w, 4, style="F")
        pdf.set_xy(82 + w + 2, y)
        pdf.set_font("D", "B", 9); pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, note, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("D", "", 9)
    pdf.ln(2)


def table(headers, data, widths, fs=8.8):
    head_style = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=NAVY)
    pdf.set_font("D", "", fs)
    pdf.set_draw_color(223, 228, 236)
    with pdf.table(col_widths=widths, text_align="LEFT", headings_style=head_style,
                   line_height=5, cell_fill_color=LIGHT, cell_fill_mode="ROWS",
                   borders_layout="HORIZONTAL_LINES") as t:
        r = t.row()
        for hcol in headers:
            r.cell(hcol)
        for drow in data:
            r = t.row()
            for cell in drow:
                r.cell(str(cell))
    pdf.ln(2)


def reel(n, title, typ, meta, beats, hook, cta, why):
    """Two-column shooting script: TIME | AUDIO (heard) | VISUAL & TEXT (seen/read)."""
    if pdf.get_y() > 235:
        pdf.add_page()
    # title bar
    pdf.set_font("D", "B", 12)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 7, f"Reel {n} — {title}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("D", "B", 8); pdf.set_text_color(*TYPE_COLOR[typ])
    pdf.cell(pdf.get_string_width(typ) + 1, 5, typ)
    pdf.set_font("D", "", 8); pdf.set_text_color(*GREY)
    pdf.cell(0, 5, "   " + meta, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)
    # two-column shooting-script table
    head = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=NAVY)
    pdf.set_font("D", "", 8.6)
    pdf.set_draw_color(210, 216, 226)
    with pdf.table(col_widths=(13, 80, 87), text_align="LEFT", headings_style=head,
                   line_height=4.6, borders_layout="ALL") as t:
        r = t.row()
        r.cell("TIME"); r.cell("AUDIO  —  what they HEAR"); r.cell("VISUAL & TEXT  —  what they SEE & READ")
        for tm, aud, vis in beats:
            r = t.row()
            r.cell(tm); r.cell(aud); r.cell(vis)
    pdf.ln(1)
    # footer: hook / cta / why
    for lab, txt, col in [("HOOK", hook, NAVY), ("CALL TO ACTION", cta, NAVY),
                          ("WHY IT'LL GO VIRAL", why, NAVY)]:
        pdf.set_x(16)
        pdf.set_font("D", "B", 8.4); pdf.set_text_color(*GOLD if False else col)
        pdf.write(4.6, f"{lab}:  ")
        pdf.set_font("D", "", 8.6); pdf.set_text_color(*INK)
        pdf.multi_cell(EPW, 4.6, txt, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)


# ============ COVER ============
pdf.set_fill_color(*NAVY); pdf.rect(0, 0, 210, 62, style="F")
pdf.set_xy(16, 14); pdf.set_font("D", "B", 9); pdf.set_text_color(*GOLD)
pdf.cell(0, 6, "S M M   V I R A L I T Y   D E C O D E R", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(16); pdf.ln(1); pdf.set_font("D", "B", 26); pdf.set_text_color(255, 255, 255)
pdf.cell(0, 13, "Social Virality Report", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(16); pdf.set_font("D", "", 10.5); pdf.set_text_color(199, 208, 224)
pdf.cell(0, 7, "PPC Guru   ·   Performance-marketing / lead-gen agency   ·   GTA   ·   Prepared June 2026")
pdf.set_y(70)
para("We searched your niche the way a buyer's algorithm does, scored every reel against its **own** "
     "account's average to separate real format-wins from luck, decoded the winners on three layers "
     "(what viewers **see, hear and read**), then rebuilt those proven formats around your **real** client "
     "results — which competitors can't copy. This edition ships a full **two-column shooting script for "
     "all ten reels**, plus the research behind them.", size=10.5, gap=1)

# ============ 1 RESEARCH ============
h2("1", "How we did the research")
para("Four stages, each measured — not guessed:")
para("**1. Your baseline.** Scraped your last 20 reels to learn your own average and what already works.  "
     "**2. Niche discovery.** Searched the niche by keyword/hashtag (not competitor names) — **36 candidate "
     "reels** surfaced.  **3. Outlier math.** Deep-scraped **5 accounts (149 reels)** and scored every reel "
     "as *plays ÷ that account's own median* — so a format win is separated from a big-account win.  "
     "**4. Three-layer decode.** Decoded the top winners on visual, audio and on-screen-text channels.")
bars([("Niche reels surfaced", 36, "36"),
      ("Reels measured for averages", 149, "149  (5 accounts)"),
      ("Reels fully decoded (3-layer)", 3, "3  — thin; see note"),
      ("Priority format-wins (20×+)", 2, "2")])
callout("Honest scope note. Only 3 reels were fully decoded (the method targets 15+), and all three were "
        "India-based agency-growth creators — a thin, geo-skewed sample. The formats still transplant (that's "
        "what the outlier math proves), but a follow-up run should decode 15+ reels and deliberately include "
        "Canadian / Western local-service creators. The full list of the 36 candidates and 5 scraped accounts "
        "was not saved in the first run — a known gap we can close with a re-run.", accent=NAVY, bg=(238, 241, 247))

# ============ 1b TOOLS / DECODE METHOD ============
h2("2", "How we decoded each winner (the 3 layers)")
table(["Channel — what it captures", "Tool used", "What it returned"],
      [["VISUAL — first frame, shots, cut pace, mood", "Higgsfield video_analysis", "the visual hook in second 1 + shot rhythm"],
       ["ON-SCREEN TEXT (overlay) — read verbatim", "Gemini video-LLM (grizzlygriff)", "every text overlay, with timing"],
       ["AUDIO — the spoken script", "Higgsfield (Whisper trial had expired)", "verbatim transcript + translation (Hinglish)"]],
      [70, 50, 58])

# ============ 3 ACCOUNTS ============
h2("3", "The winners we decoded — and where they're from")
table(["Account", "Origin", "What it is", "Why it's relevant to you"],
      [["akshatsadhu", "India", "agency-growth creator", "#1 approved adjacent niche for format transplant"],
       ["mycaptainofficial", "India (edtech)", "lead-gen tool demo", "split-screen 'scoreboard' format transplant"],
       ["therudransh.sharma", "India (Jaipur)", "lead-gen, Hinglish", "directly serves your S-Asian diaspora segment"]],
      [38, 26, 38, 76])
para("**Why foreign accounts at all?** The outlier score rewards content that beat its *own* account's "
     "average — that's a signal about the **format**, which crosses borders. We then rebuild the format with "
     "**your** GTA proof, in English (plus an optional Hinglish cut for diaspora owners). The Hinglish winner "
     "isn't noise — it maps onto a segment your brief explicitly targets.")

# ============ 4 YOUR ACCOUNT ============
h2("4", "Your account today")
para("Your baseline (median) reel does **~4,355 plays** (last 20 reels — directional). The pattern is loud:")
table(["Your reel", "Plays", "vs avg", "What it was"],
      [["\"The Halo Effect\" (brand psychology)", "39,470", "9.1× — best", "broad marketing-psychology education"],
       ["\"ChatGPT SEO / AI search\"", "36,892", "8.5×", "AI-trend / AEO education"],
       ["\"Likes don't equal leads\" (audit)", "10,914", "2.5×", "nurture + DM CTA"],
       ["Physiotherapy Google Ads pitch", "~722", "0.17×", "narrow service pitch"],
       ["Contractor Google Ads pitch", "~708", "0.16×", "narrow service pitch"]],
      [46, 14, 18, 44])
callout("Read: your reach engine is broad education + trends, not service pitches. Lead with psychology / AI / "
        "\"how marketing actually works,\" then convert with proof. Pitch-first reels cap your reach.")

# ============ 5 WINNING FORMATS ============
h2("5", "The three winning formats (and the gap)")
bars([("6s POV listicle (akshatsadhu)", 27.6, "27.6×"),
      ("Split-screen scoreboard (mycaptain)", 20.5, "20.5×"),
      ("Proof + comment-bait (rudransh)", 8.4, "8.4×  ·  6,225 comments")])
para("**A · 6-second POV listicle (27.6×):** over-the-shoulder 'real operator' b-roll, 5 fast text steps, "
     "trending audio, comment-bait CTA — ultra-short so it loops.  **B · Split-screen scoreboard (20.5×):** a "
     "number gap (1833 vs 98) as an instant visual question; hook is a *question*, not a claim.  **C · Proof + "
     "comment-bait (8.4×, 6,225 comments):** opens on a real lead spreadsheet; a triple CTA manufactures "
     "comments. Hinglish.")
callout("THE GAP — your unfair advantage. Nobody in the local-agency lane runs these proven formats with "
        "real, specific client outcomes (the creators winning them use generic/invented numbers). You have "
        "un-fakeable proof — a contractor taken from $1,000/mo to $500K/mo, physio clinics booked from Google "
        "— plus two unused angles: GTA local pride and Hinglish for diaspora owners.")

# ============ 6 CALENDAR ============
h2("6", "Your 30-day plan (40 / 40 / 20)")
para("Ten reels at 2–3/week, balanced for **Reach / Nurture / Convert** so the calendar grows an audience "
     "**and** books calls:")
table(["#", "Date", "Type", "Format", "Hook concept"],
      [["1", "Mon Jun 16", "REACH", "Split-screen scoreboard", "\"Same $1,000 — 0 jobs vs 37 leads\""],
       ["2", "Thu Jun 19", "NURTURE", "6s POV listicle", "\"POV: your ads don't convert. Fix 3 things.\""],
       ["3", "Sat Jun 21", "CONVERT", "Proof + comment-bait", "\"42 patients booked from Google\""],
       ["4", "Mon Jun 23", "REACH", "AI-trend talking-head", "\"Customers ask ChatGPT before Google now\""],
       ["5", "Thu Jun 26", "NURTURE", "6s listicle", "\"3 numbers your reels already tell you\""],
       ["6", "Sat Jun 28", "REACH", "Split-screen scoreboard", "\"Boosting vs a funnel — the lead gap\""],
       ["7", "Tue Jul 1", "NURTURE", "Hinglish proof talking-head", "\"10 din mein leads — yeh setup\""],
       ["8", "Thu Jul 3", "CONVERT", "Comment-bait + dashboard", "\"Contractor: $1k → $500K/mo\""],
       ["9", "Sat Jul 5", "REACH", "\"Real operator\" POV", "\"Running ads for 12 businesses at 2am\""],
       ["10", "Tue Jul 8", "NURTURE", "6s text-listicle", "\"Show up in ChatGPT — 3 steps\""]],
      [7, 20, 19, 42, 60])
para("**Split:** 4 Reach / 4 Nurture / 2 Convert = exactly 40/40/20. Cadence never exceeds 3/week.")

# ============ 7 SCRIPTS ============
pdf.add_page()
h2("7", "The scripts — all ten reels (two-column shooting format)")
para("Read each like a film script: the **left column is what the viewer HEARS** (the spoken voiceover, by "
     "timestamp); the **right column is what they SEE and READ** (camera/visual + the on-screen text overlay). "
     "Under each table: the hook, the call-to-action, and why it should travel.")

NOVO = "— no voiceover —\n(trending audio)"

reel(1, "\"Same $1,000\"", "REACH", "35s · original voiceover",
 [("0–2s", "\"Same thousand-dollar budget. One agency got zero booked jobs — we got thirty-seven leads. Here's the difference.\"",
   "Hard split screen. LEFT (red): a boosted IG post. RIGHT (green): a Google Ads dashboard.\nTEXT: \"Same $1,000. 37 leads vs 0.\""),
  ("2–8s", "\"Most contractors think more leads means more budget. It doesn't.\"",
   "Hold the split; a finger taps the boosted (left) side.\nTEXT: \"BOOSTED — 0 jobs\" / \"STRUCTURED — 37 leads\""),
  ("8–20s", "\"This contractor was stuck at a grand a month. We didn't touch the spend — we fixed the structure: campaign build, high-intent keywords, one conversion landing page.\"",
   "Screen-recording: keyword list → the landing page being built."),
  ("20–30s", "\"Month one: 37 qualified leads on the same budget. Month two: three deals — a hundred and fifty grand.\"",
   "Animated stamps: \"Mo1: 37 leads\" → \"Mo2: $150K\"."),
  ("30–35s", "\"If your ads bring clicks but no jobs, comment STRUCTURE and I'll send the 3-part build.\"",
   "Founder to camera / end card.\nTEXT: \"Comment STRUCTURE\"")],
 "the split-screen number gap (0 vs 37) — an instant visual question in second one.",
 "Comment STRUCTURE → DM the 3-part build.",
 "transplants the 20.5× 'scoreboard' format onto a real contractor result no competitor can claim.")

reel(2, "\"POV: your ads don't convert\"", "NURTURE", "8s · trending audio (silent format)",
 [("0–1s", NOVO, "Over-the-shoulder at a real desk: two monitors with a Google Ads dashboard, coffee, dim '2am operator' light.\nTEXT: \"POV: your ads don't convert. Fix this.\""),
  ("1–3s", NOVO, "Text card 1: \"1. Landing page asks for everything → ask for ONE thing.\""),
  ("3–5s", NOVO, "Text card 2: \"2. Offer is 'contact us' → give a reason to act now.\""),
  ("5–7s", NOVO, "Text card 3: \"3. You reply in 12 hours → speed-to-lead under 5 min.\""),
  ("7–8s", NOVO, "Final card: \"Structure beats budget.\"\nTEXT: \"Comment AUDIT\"")],
 "the relatable 'POV: your ads don't convert' overlay over the real-operator desk.",
 "Comment AUDIT → free funnel teardown.",
 "the 27.6× ultra-short save/loop format; three fixes in 8 seconds is pure save-bait. (Format-led — add a client mini-result to strengthen.)")

reel(3, "\"42 patients from Google\"", "CONVERT", "40s · original VO · Hinglish cut available",
 [("0–2s", "\"This physio clinic was getting walk-ins and hope. Last month: forty-two patients booked from Google. Here's the exact setup.\"",
   "A real bookings + Google Ads dashboard fills the screen (a filled calendar = proof).\nTEXT: \"42 patients booked. One Google setup.\""),
  ("2–12s", "\"Three fixes. One — rank on Google Maps for 'physio near me'. Two — treatment-specific campaigns, not 'physiotherapy'. Three — a landing page with online booking.\"",
   "Screen-recording of each fix; numbered overlays 1 / 2 / 3."),
  ("12–30s", "\"Someone searches 'back pain physio' at 10pm, sees you in the top three, books instantly. That's not luck — that's the setup.\"",
   "Phone mock-up: search → map top-3 → booking confirmed.\nTEXT: \"search → top 3 → booked\""),
  ("30–40s", "\"Comment PHYSIO and we'll audit your Google presence free — this week only.\"\n[Hinglish hook: \"Is clinic ko ek mahine mein Google se 42 patients mile — poora setup dikhata hoon.\"]",
   "Founder talking-head end card.\nTEXT: \"Comment PHYSIO — free audit (this week)\"")],
 "a real bookings dashboard as the first frame — undeniable proof.",
 "Comment PHYSIO → free Google-presence audit (scarcity: this week only).",
 "the 8.4×/6,225-comment proof + comment-bait format, on your real clinic result.")

reel(4, "\"Your customers ask ChatGPT first\"", "REACH", "30s · trending audio + AI-avatar VO",
 [("0–2s", "\"Your next customer isn't Googling you anymore — they're asking ChatGPT who to hire. Here's how to be the answer.\"",
   "Screen-recording: typing \"best [service] near me\" into ChatGPT; the answer starts generating.\nTEXT: \"They ask AI now. Be the answer.\""),
  ("2–12s", "\"People used to scroll ten blue links. Now they ask one question and get one recommendation.\"",
   "Split: an old Google results page vs a single ChatGPT answer."),
  ("12–24s", "\"If AI can't read and trust your business — reviews, a clear service page, consistent details — you're invisible in that answer.\"",
   "AI-avatar presenter + a checklist graphic (reviews / service page / details)."),
  ("24–30s", "\"It's called AEO — Answer Engine Optimization. Comment AI and I'll send the 3-point checklist.\"",
   "End card.\nTEXT: \"AEO = the new front door\" · \"Comment AI\"")],
 "a live ChatGPT query for a local service — a behavior the viewer recognizes instantly.",
 "Comment AI → 3-point AEO checklist.",
 "rides the AI-curiosity wave on your own proven 8.5× topic, and doubles as a live demo of your AI-avatar service. Frames AI as a new front door — never 'SEO is dead.'")

reel(5, "\"3 numbers your reels already tell you\"", "NURTURE", "9s · trending audio (silent format)",
 [("0–1s", NOVO, "Over-the-shoulder phone showing an Instagram Insights panel, finger scrolling.\nTEXT: \"3 numbers your reels already tell you\""),
  ("1–3s", NOVO, "Card 1: \"1. Plays ÷ your average = which FORMAT won.\""),
  ("3–5s", NOVO, "Card 2: \"2. Saves > likes = make more of THAT topic.\""),
  ("5–7s", NOVO, "Card 3: \"3. Comments near zero = a weak hook.\""),
  ("7–9s", NOVO, "Final: \"Your analytics are a content brief.\"\nTEXT: \"Comment NUMBERS\"")],
 "\"your own data already told you\" — a curiosity-gap promise over a familiar Insights screen.",
 "Comment NUMBERS → 1-page reel scorecard.",
 "the 27.6× listicle format as a save-bait teach; mirrors your own audit reel. (Format-led — edge is the branded scorecard.)")

reel(6, "\"Boosting vs a funnel\"", "REACH", "35s · original voiceover",
 [("0–2s", "\"Boosting a post and running a funnel are not the same thing — and the lead gap will shock you.\"",
   "Hard split. LEFT (red): the IG 'Boost' button mid-tap. RIGHT (green): campaign → landing page → leads list.\nTEXT: \"Boost = likes. Funnel = leads.\""),
  ("2–14s", "\"Boosting buys reach to people who look like your followers. Nice likes, little intent.\"",
   "Animate: boost → a vague audience blob → a few likes."),
  ("14–28s", "\"A funnel puts your offer in front of someone actively searching, sends them to one page built to convert, and captures the lead.\"",
   "Animate: search term → landing page → form → a lead row appears."),
  ("28–35s", "\"Same money. One fills your ego, the other fills your calendar. Comment FUNNEL for the 1-page build.\"",
   "End card.\nTEXT: \"Comment FUNNEL\"")],
 "the split-screen plus a contrarian claim every owner has argued about.",
 "Comment FUNNEL → the 1-page funnel build.",
 "the 20.5× scoreboard format applied to a debate your buyers already have in their heads.")

reel(7, "\"10 din mein leads\" (Hinglish)", "NURTURE", "40s · original VO (Hinglish, English subtitles)",
 [("0–2s", "(Hinglish) \"Agar aapko leads nahi mil rahe — problem budget nahi, setup hai. 10 din ka setup dikhata hoon.\"",
   "Over-the-shoulder of a real leads dashboard → founder talking-head. English subtitle burned in.\nTEXT: \"Leads problem? It's the setup, not budget.\""),
  ("2–14s", "(Hinglish) \"Ek — high-intent keywords pe jao, 'cheap' nahi, 'best [service] near me'.\"",
   "Screen-recording of a keyword example.\nTEXT card: \"1. High-intent keywords\""),
  ("14–28s", "(Hinglish) \"Do — ek hi conversion landing page, na ki homepage.\"",
   "Screen-recording of a single conversion page.\nTEXT card: \"2. One conversion page\""),
  ("28–40s", "(Hinglish) \"Teen — 5 minute ke andar follow-up. Comment SETUP — framework bhej dunga.\"",
   "Founder end card.\nTEXT card: \"3. 5-minute follow-up\" · \"Comment SETUP\"")],
 "Hinglish hook + a real dashboard — speaks directly to diaspora business owners.",
 "Comment SETUP → the 3-step framework (in their DMs).",
 "the C3 Hinglish proof format, run in the GTA-diaspora lane no local competitor is using.")

reel(8, "\"Contractor: $1k → $500K/mo\"", "CONVERT", "40s · original voiceover",
 [("0–2s", "\"This contractor came to us at a thousand dollars a month. Today: five hundred thousand a month. Same ads budget.\"",
   "A real revenue dashboard climbing.\nTEXT: \"$1K/mo → $500K/mo. Same ad budget.\""),
  ("2–10s", "\"When we started, leads were random and cheap-looking. We rebuilt three things.\"",
   "B-roll: a messy 'before' funnel → a clean 'after'."),
  ("10–28s", "\"One — high-intent search campaigns, not spray-and-pray. Two — a conversion landing page per service. Three — speed-to-lead under five minutes.\"",
   "Screen-recording of each; overlays 1 / 2 / 3."),
  ("28–40s", "\"Month one: 37 qualified leads. Then it compounded. Comment STRUCTURE for the 3-part build.\"",
   "The job pipeline filling up; end card.\nTEXT: \"Comment STRUCTURE\"")],
 "the $1k → $500K/mo jump stated in the first two seconds.",
 "Comment STRUCTURE → the 3-part build.",
 "an un-copyable real transformation (your flagship case), framed as a past result — never a guarantee.")

reel(9, "\"Running ads for 12 businesses at 2am\"", "REACH", "9s · trending audio (silent format)",
 [("0–1s", NOVO, "Over-the-shoulder '2am operator': two monitors, several ad dashboards, coffee, dim light.\nTEXT: \"POV: managing ads for 12 local businesses\""),
  ("1–3s", NOVO, "Card: \"11pm — a contractor's leads just spiked.\""),
  ("3–5s", NOVO, "Card: \"12am — tweak a physio clinic's budget.\""),
  ("5–7s", NOVO, "Card: \"1am — a realtor's cost-per-lead dropped.\""),
  ("7–9s", NOVO, "Final: \"Local businesses. Real campaigns. No autopilot.\"\nTEXT: \"Comment LOCAL\"")],
 "the authentic 'real operator at 2am' visual that powered the 27.6× winner.",
 "Follow for behind-the-scenes · Comment LOCAL to get yours run this way.",
 "founder authenticity + the proven over-shoulder visual hook. (Shoot in the founder's real workspace; use real or genericized metrics.)")

reel(10, "\"Show up in ChatGPT — 3 steps\"", "NURTURE", "9s · trending audio + AI-avatar",
 [("0–1s", NOVO, "Split phone: LEFT a ChatGPT answer recommending a business; RIGHT a Google Business Profile + reviews feeding it.\nTEXT: \"Show up when they ask AI — 3 steps\""),
  ("1–3s", NOVO, "Card 1: \"1. Claim + fully fill your Google Business Profile.\""),
  ("3–5s", NOVO, "Card 2: \"2. Get consistent, recent reviews (AI reads them).\""),
  ("5–7s", NOVO, "Card 3: \"3. One clear service page, plain-language answers.\""),
  ("7–9s", NOVO, "Final: \"SEO got you found on Google. This gets you found in AI.\"\nTEXT: \"Comment AI\"")],
 "an AI answer next to the profile that feeds it — shows the mechanism in one frame.",
 "Comment AI → the full AEO checklist.",
 "the AEO trend packaged as a save-bait listicle; a companion to Reel 4. Keeps Google ('without ditching Google') — never 'SEO is dead.'")

# ============ 8 LEARNING LOOP ============
h2("8", "Learning loop — keep, kill, double-down")
table(["Verdict", "Reels", "Action"],
      [["DOUBLE-DOWN", "\"Halo Effect\" (9.1×), \"ChatGPT SEO\" (8.5×)", "broad psychology + AI-trend education is your reach lane — make more"],
       ["KEEP", "\"Likes don't equal leads\" (2.5×)", "solid nurture, keep the DM-keyword CTA"],
       ["KILL / REWORK", "physio & contractor pitch reels (~0.16×)", "re-shoot proof-led (Reel 1/3/8 style), never pitch-first"]],
      [28, 55, 80])
para("Re-run monthly: scrape your last-30-days, score against this baseline, feed the verdicts into next "
     "month's calendar. Recompute the baseline once you have ≥30 reels.", gap=1)
para("_Method: niche-keyword discovery → account-relative outlier scoring → three-layer decode (Higgsfield "
     "video_analysis for visual + audio; Gemini video-LLM for overlay text) → format transplant onto owned "
     "proof. Research cost: under $1 of scraping, $0 in video credits. Caveat: 3 reels decoded (thin, "
     "India-skewed); a broader, Canada-inclusive re-run is recommended._", size=8, color=GREY)

pdf.output("/home/user/Social-media-calender-genrator/PPC_GURU_FINAL_REPORT.pdf")
print("PDF written")
