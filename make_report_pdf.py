#!/usr/bin/env python3
"""Render the PPC Guru final report as a branded, client-ready PDF.
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
REACH = (29, 111, 184)
NURTURE = (46, 139, 87)
CONVERT = (192, 57, 43)
FLAG = (176, 106, 0)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TYPE_COLOR = {"REACH": REACH, "NURTURE": NURTURE, "CONVERT": CONVERT}


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("D", "", 7.5)
        self.set_text_color(*GREY)
        self.cell(0, 6, f"SMM Virality Decoder  ·  PPC Guru  ·  June 2026", align="L")
        self.cell(0, 6, f"{self.page_no()}", align="R")


pdf = PDF(format="A4")
pdf.set_auto_page_break(True, margin=16)
pdf.add_font("D", "", F)
pdf.add_font("D", "B", FB)
pdf.set_margins(16, 16, 16)
pdf.add_page()
EPW = pdf.epw  # effective page width


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
    start_y = pdf.get_y()
    # measure height by rendering into a dummy split
    lines = pdf.multi_cell(EPW - 10, 5.2, text, dry_run=True, output="LINES", markdown=True)
    h = len(lines) * 5.2 + 6
    if start_y + h > 272:
        pdf.add_page(); start_y = pdf.get_y()
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
        pdf.set_text_color(*INK)
        pdf.set_xy(16, y)
        pdf.cell(64, 6, label)
        w = max(1.5, maxw * val / mx)
        pdf.set_fill_color(*REACH)
        pdf.rect(82, y + 1, w, 4, style="F")
        pdf.set_xy(82 + w + 2, y)
        pdf.set_font("D", "B", 9)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, note, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("D", "", 9)
    pdf.ln(2)


def table(headers, data, widths):
    head_style = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=NAVY)
    pdf.set_font("D", "", 8.8)
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


def script_card(title, typ, meta, hooks, body, cta, tags, why, why_flag=False):
    # estimate height
    pdf.set_font("D", "", 9)
    blocks = [("", body), ("", cta), ("", why)]
    est = 7 + 6  # title + meta
    pdf.set_font("D", "", 9)
    for label, txt in [("Spoken", hooks[0]), ("Visual", hooks[1]), ("Overlay", hooks[2])]:
        est += len(pdf.multi_cell(EPW - 14, 4.8, f"**{label}:** {txt}", dry_run=True,
                                  output="LINES", markdown=True)) * 4.8
    est += 6
    for txt in [body, cta, why]:
        est += len(pdf.multi_cell(EPW - 8, 4.8, txt, dry_run=True, output="LINES")) * 4.8 + 2
    est += 12
    if pdf.get_y() + est > 276:
        pdf.add_page()
    top = pdf.get_y()
    pdf.set_draw_color(215, 221, 231)
    pdf.set_line_width(0.3)
    # title
    pdf.set_xy(20, top + 3)
    pdf.set_font("D", "B", 11.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
    # meta + type
    pdf.set_x(20)
    pdf.set_font("D", "B", 8)
    pdf.set_text_color(*TYPE_COLOR[typ])
    pdf.cell(pdf.get_string_width(typ) + 2, 5, typ)
    pdf.set_text_color(*GREY)
    pdf.set_font("D", "", 8)
    pdf.cell(0, 5, "   " + meta, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    # hooks block (light bg). Measure and render with the SAME markdown call so
    # the background box height always matches the text exactly.
    hook_lines = [f"**{lab}:** {txt}" for lab, txt in
                  [("Spoken", hooks[0]), ("Visual", hooks[1]), ("Overlay", hooks[2])]]
    hy = pdf.get_y()
    pdf.set_font("D", "", 9)
    hooks_h = 4
    for ln in hook_lines:
        hooks_h += len(pdf.multi_cell(EPW - 14, 4.8, ln, dry_run=True, output="LINES",
                                      markdown=True)) * 4.8
    pdf.set_fill_color(*LIGHT)
    pdf.rect(20, hy, EPW - 8, hooks_h, style="F")
    pdf.set_xy(23, hy + 2)
    for ln in hook_lines:
        pdf.set_x(23)
        pdf.set_text_color(*INK)
        pdf.multi_cell(EPW - 14, 4.8, ln, new_x="LMARGIN", new_y="NEXT", markdown=True)
    pdf.set_y(hy + hooks_h + 2)
    # body
    pdf.set_x(20)
    pdf.set_font("D", "B", 9); pdf.set_text_color(*NAVY); pdf.write(4.8, "Body: ")
    pdf.set_font("D", "", 9); pdf.set_text_color(*INK)
    pdf.multi_cell(EPW - 8, 4.8, body, new_x="LMARGIN", new_y="NEXT")
    # cta
    pdf.set_x(20)
    pdf.set_font("D", "B", 9); pdf.set_text_color(*NAVY); pdf.write(4.8, "CTA + tags: ")
    pdf.set_font("D", "", 9); pdf.set_text_color(*INK)
    pdf.multi_cell(EPW - 8, 4.8, cta + "  " + tags, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)
    # why
    pdf.set_x(20)
    pdf.set_font("D", "B", 8.5); pdf.set_text_color(*NAVY); pdf.write(4.6, "Why it works: ")
    pdf.set_font("D", "", 8.5); pdf.set_text_color(*(FLAG if why_flag else GREY))
    pdf.multi_cell(EPW - 8, 4.6, why, new_x="LMARGIN", new_y="NEXT")
    bot = pdf.get_y() + 3
    pdf.set_draw_color(215, 221, 231); pdf.set_line_width(0.3)
    pdf.rect(16, top, EPW, bot - top)
    pdf.set_y(bot + 3)


# ---------- COVER ----------
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, 210, 62, style="F")
pdf.set_xy(16, 14)
pdf.set_font("D", "B", 9)
pdf.set_text_color(*GOLD)
pdf.cell(0, 6, "S M M   V I R A L I T Y   D E C O D E R", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(16); pdf.ln(1)
pdf.set_font("D", "B", 26)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 13, "Social Virality Report", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(16)
pdf.set_font("D", "", 10.5)
pdf.set_text_color(199, 208, 224)
pdf.cell(0, 7, "PPC Guru   ·   Performance-marketing / lead-gen agency   ·   GTA   ·   Prepared June 2026")
pdf.set_y(70)

para("We searched your niche the way a buyer's algorithm does, scored every reel against its **own** "
     "account's average to separate real format-wins from luck, and decoded the winners frame-by-frame. "
     "The headline: **broad, proof-led, \"scoreboard\" content wins; service pitches lose.** Your own two "
     "biggest reels (psychology + AI-search) already prove it — they beat your average by ~9×, while your "
     "physio/contractor pitch reels sit at the bottom. The 30-day plan below transplants three proven viral "
     "formats onto your real client results, which competitors can't copy — with a full shot-by-shot script "
     "for all ten reels.", size=10.5, gap=1)

# ---------- 1 ----------
h2("1", "Research depth")
para("We didn't guess — here's the work behind this report.")
bars([("Niche reels surfaced", 36, "36"),
      ("Reels measured for averages", 149, "149  (5 accounts)"),
      ("Reels fully decoded (3-layer)", 3, "3"),
      ("Priority format-wins (20×+)", 2, "2")])
callout("Confidence note. The strategy rests on 3 fully-decoded winners plus your own 20-reel baseline — "
        "enough to act on. Nothing here is invented; where a script needs proof you haven't supplied yet, "
        "it's marked \"needs a client proof asset\".", accent=NAVY, bg=(238, 241, 247))

# ---------- 2 ----------
h2("2", "Your account today")
para("Your baseline (median) reel does **~4,355 plays** (last 20 reels — a small, directional sample). "
     "The pattern is loud and clear:")
table(["Your reel", "Plays", "vs your avg", "What it was"],
      [["\"The Halo Effect\" (brand psychology)", "39,470", "9.1× — best", "broad marketing-psychology education"],
       ["\"ChatGPT SEO / AI search is the future\"", "36,892", "8.5×", "AI-trend / AEO education"],
       ["\"Likes don't equal leads\" (audit)", "10,914", "2.5×", "nurture + DM CTA"],
       ["Physiotherapy Google Ads pitch", "~722", "0.17× — bottom", "narrow service pitch"],
       ["Contractor Google Ads pitch", "~708", "0.16× — bottom", "narrow service pitch"]],
      [44, 13, 17, 42])
callout("Read: your reach engine is broad education + trends, not service pitches. Lead with psychology / AI / "
        "\"here's how marketing actually works,\" then convert with proof. The pitch-first reels are quietly "
        "capping your reach.")

# ---------- 3 ----------
h2("3", "What's winning in your niche")
para("The keyword search surfaced genuine format-wins — reels that beat their own account's average by 8–28× "
     "(so the **content**, not account size, carried them). Three repeatable formats:")
bars([("6s POV listicle (akshatsadhu)", 27.6, "27.6×"),
      ("Split-screen demo (mycaptain)", 20.5, "20.5×"),
      ("Proof + comment-bait (rudransh)", 8.4, "8.4×  ·  6,225 comments")])
table(["Format", "The winner", "Beat avg", "Why it worked"],
      [["6-second POV text-listicle", "\"POV: you started an agency, now you need $1,500 clients\"", "27.6×", "ultra-short, save-worthy, loops"],
       ["Split-screen \"scoreboard\" demo", "\"LEADS 1833 vs 98\" (stressed vs calm)", "20.5×", "the number gap is an instant question"],
       ["On-screen proof + comment-bait", "real lead spreadsheet + \"comment for the guide\"", "8.4×", "undeniable proof + manufactured comments"]],
      [38, 50, 14, 44])
para("**A · The 6-second listicle (27.6×).** First frame: an over-the-shoulder shot at a messy desk "
     "(Red Bull, headphones) — the \"real operator\" look. Overlay hook: \"POV: You started an Agency. now "
     "you need $1500 clients.\" Then 5 rapid steps. No talking — trending audio. CTA: \"Comment LINKEDIN for "
     "the guide.\"")
para("**B · The split-screen demo (20.5×).** A two-person skit. The spoken hook is a question, not a claim — "
     "\"Bro, what black magic are you doing? How are your leads growing so much?\" — answered by a calm "
     "colleague demoing a lead tool, with a \"1833 vs 98\" scoreboard on screen. (Transcript verified via "
     "Higgsfield.)")
para("**C · The proof + comment-bait reel (8.4×, 6,225 comments).** Opens on a real lead spreadsheet: "
     "\"I generated this many leads in 10 days, without spending a single rupee.\" The engine behind 6,000+ "
     "comments is an explicit triple CTA (share to DM + comment 'leads' + follow). We keep the comment→DM "
     "mechanic for you but drop the \"follow or lose it forever\" line. Bonus: it's in Hinglish — your "
     "diaspora segment.")

# ---------- 4 ----------
h2("4", "The gap — your unfair advantage")
callout("Nobody in the local-agency lane runs these proven formats with real, specific client outcomes — the "
        "creators winning them use generic or invented numbers. You have un-fakeable proof: a contractor "
        "taken from $1,000/mo to $500K/mo, physio clinics booked from Google. Run the same formats with your "
        "receipts, and add the two angles nobody's using — GTA local pride and Hinglish for diaspora owners.")

# ---------- 5 ----------
h2("5", "Your 30-day plan")
para("A **40% reach / 40% nurture / 20% convert** mix — so the calendar grows an audience and books calls. "
     "Ten reels at 2–3/week:")
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
para("**Split check:** 4 reach / 4 nurture / 2 convert = exactly 40/40/20. Cadence never exceeds 3/week.")

# ---------- 6 ----------
pdf.add_page()
h2("6", "The scripts — all ten reels")
para("Each reel is written shot-by-shot with all three hooks (what they see, hear, and read in the first "
     "second), tied to a decoded winner and, on CONVERT slots, to your real proof.")

scripts = [
 ("Script 1 — \"Same $1,000\"", "REACH", "35s · original VO",
  ["\"Same thousand-dollar budget. One agency got zero booked jobs — we got thirty-seven leads. Here's the difference.\"",
   "hard split screen. LEFT (red) a boosted post \"BOOSTED — 0 booked jobs\"; RIGHT (green) a Google Ads dashboard \"STRUCTURED — 37 leads\". \"$1,000/mo\" stamped on both sides.",
   "\"Same $1,000. 37 leads vs 0.\""],
  "(1) hold the split — \"more leads isn't more budget.\" (2) wipe to the result — \"we didn't touch the spend, we fixed the structure: campaign build, high-intent keywords, one conversion landing page.\" (3) stamps: \"Mo1: 37 leads\" → \"Mo2: 3 deals = $150K.\"",
  "\"If your ads bring clicks but no jobs, comment STRUCTURE and I'll send the 3-part build.\"",
  "#GoogleAds #ContractorMarketing #LeadGeneration #GTA",
  "transplants the 20.5× split-screen scoreboard onto your real contractor case. A competitor can't post this — they don't have the result.", False),

 ("Script 2 — \"POV: your ads don't convert\"", "NURTURE", "8s · trending audio",
  ["none — trending audio (this format wins silent). Optional 1-word VO: \"Fix this.\"",
   "over-the-shoulder at a real desk, two monitors with a Google Ads dashboard, coffee + sticky notes, dim \"2am operator\" light. Fast ~1s cuts.",
   "\"POV: your ads don't convert. Fix this.\""],
  "rapid text cards: \"1. Landing page asks for everything → ask for ONE thing.\" · \"2. Offer is 'contact us' → give a reason to act now.\" · \"3. You reply in 12 hours → speed-to-lead under 5 min.\" · \"Structure beats budget.\"",
  "\"Save this. Comment AUDIT for a free funnel teardown.\"",
  "#GoogleAds #MetaAds #SmallBusinessMarketing",
  "the 27.6× ultra-short save-bait format. Format-led — strengthen with a client mini-result in the teardown.", True),

 ("Script 3 — \"42 patients from Google\"", "CONVERT", "40s · original VO · Hinglish cut available",
  ["\"This physio clinic was getting walk-ins and hope. Last month: forty-two patients booked from Google. Here's the exact setup.\"",
   "a real bookings + Google Ads dashboard fills the screen (filled calendar = proof), then cut to founder talking-head.",
   "\"42 patients booked. One Google setup.\""],
  "three fixes — (1) rank on Google Maps for \"physio near me\"; (2) treatment-specific campaigns, not \"physiotherapy\"; (3) a landing page with online booking. \"Someone searches 'back pain physio' at 10pm, sees you top 3, books instantly — that's the setup, not luck.\"",
  "\"Comment PHYSIO and we'll audit your Google presence free — this week only.\"  Hinglish hook: \"Is clinic ko ek mahine mein Google se 42 patients mile — poora setup dikhata hoon.\"",
  "#GoogleAdsCanada #PhysiotherapyClinic #LocalSEO #GTA",
  "the 8.4× proof + comment-bait format on your real clinic results.", False),

 ("Script 4 — \"Your customers ask ChatGPT first\"", "REACH", "30s · trending audio · AI-avatar",
  ["\"Your next customer isn't Googling you anymore — they're asking ChatGPT who to hire. Here's how to be the answer.\"",
   "screen-record of someone typing \"best [service] near me\" into ChatGPT, the answer generating; then cut to the AI-avatar presenter.",
   "\"They ask AI now. Be the answer.\""],
  "(1) \"People used to scroll ten blue links. Now they ask one question and get one recommendation.\" (2) \"If your business isn't structured so AI can read and trust it — reviews, a clear service page, consistent details — you're invisible in that answer.\" (3) \"We call it AEO: Answer Engine Optimization. Same idea as SEO, new front door.\"",
  "\"Comment AI and I'll send the 3-point AEO checklist.\"",
  "#AEO #AISearch #ChatGPT #LocalMarketing #GTA",
  "built on your own proven AEO angle (your 8.5× reel) + doubles as a live demo of your AI-avatar service. Framed as a new front door alongside Google — never \"SEO is dead.\" Add a client AEO result when you have one.", True),

 ("Script 5 — \"3 numbers your reels already tell you\"", "NURTURE", "9s · trending audio",
  ["none — trending audio. Optional VO: \"Read your own data.\"",
   "over-the-shoulder phone screen showing an Instagram Insights panel, finger scrolling. Fast ~1s cuts.",
   "\"3 numbers your reels already tell you\""],
  "rapid text cards: \"1. Plays ÷ your average = which FORMAT won (not luck).\" · \"2. Saves > likes = make more of THAT topic.\" · \"3. Comments near zero = your hook didn't start a conversation.\" · \"Your analytics are a content brief. Read them.\"",
  "\"Save this. Comment NUMBERS for our 1-page reel scorecard.\"",
  "#ContentStrategy #InstagramTips #Analytics",
  "the 27.6× text-listicle format + mirrors your own audit reel. Format-led — the edge is the branded scorecard offer.", True),

 ("Script 6 — \"Boosting vs a funnel\"", "REACH", "35s · original VO",
  ["\"Boosting a post and running a funnel are not the same thing — and the lead gap will shock you.\"",
   "hard split screen. LEFT (red) the IG \"Boost post\" button mid-tap \"BOOST — vanity\"; RIGHT (green) a structured campaign → landing page → leads list \"FUNNEL — booked calls\".",
   "\"Boost = likes. Funnel = leads.\""],
  "(1) \"Boosting buys you reach to people Instagram thinks look like your followers. Nice likes. Little intent.\" (2) \"A funnel puts your offer in front of someone actively searching, sends them to ONE page built to convert, and captures the lead.\" (3) \"Same money. One fills your ego, the other fills your calendar.\"",
  "\"Comment FUNNEL and I'll send the 1-page build we use.\"",
  "#MetaAds #GoogleAds #LeadGeneration #GTA",
  "the 20.5× split-screen scoreboard applied to your contrarian POV. Add a specific client boost-vs-funnel number to make it un-copyable.", True),

 ("Script 7 — \"10 din mein leads\"", "NURTURE", "Hinglish · 40s · original VO",
  ["(Hinglish) \"Agar aapki agency ya business ko leads nahi mil rahe — toh problem budget nahi, setup hai. 10 din ka setup main dikhata hoon.\" (English subtitle burned in.)",
   "over-the-shoulder of a real Google Ads / leads dashboard, then founder talking-head; English subtitles.",
   "\"Leads problem? It's the setup, not budget.\""],
  "(Hinglish VO, English subs) \"Ek — high-intent keywords pe jao, 'cheap' nahi, 'best [service] near me'.\" · \"Do — ek hi conversion landing page, na ki homepage.\" · \"Teen — 5 minute ke andar follow-up. Speed = leads.\"",
  "\"Comment SETUP — main aapko yeh 3-step framework bhej dunga.\"",
  "#DigitalMarketingIndia #LeadGeneration #DesiBusiness #GTA",
  "the C3 Hinglish proof format on your real 3-step framework — and it owns the Hinglish + GTA-diaspora lane no competitor is using. Add a client diaspora result when you have one.", True),

 ("Script 8 — \"Contractor: $1k → $500K/mo\"", "CONVERT", "40s · original VO",
  ["\"This contractor came to us at a thousand dollars a month in revenue. Today: five hundred thousand a month. Same ads budget — different machine.\"",
   "a real revenue/leads dashboard climbing, then the contractor's job pipeline.",
   "\"$1K/mo → $500K/mo. Same ad budget.\""],
  "(1) \"When we started, leads were random and cheap-looking. We rebuilt three things.\" (2) \"One — high-intent search campaigns, not spray-and-pray. Two — a conversion landing page per service. Three — speed-to-lead under 5 minutes.\" (3) \"Month one: 37 qualified leads. Then it compounded.\"",
  "\"If you're a contractor stuck on random leads, comment STRUCTURE and I'll send the 3-part build.\"",
  "#ContractorMarketing #GoogleAds #HomeServices #GTA",
  "your flagship real case — un-copyable. Framed strictly as one client's past result, never a promise the viewer will get $500K.", False),

 ("Script 9 — \"Running ads for 12 businesses at 2am\"", "REACH", "9s · trending audio",
  ["none — trending audio.",
   "over-the-shoulder \"real operator at 2am\" — two monitors, several ad dashboards open, coffee, dim light. Fast ~1s cuts between dashboards.",
   "\"POV: managing ads for 12 local businesses\""],
  "text cards over b-roll: \"11pm: a contractor's leads just spiked.\" · \"12am: tweak a physio clinic's budget.\" · \"1am: a realtor's cost-per-lead dropped.\" · \"Local businesses, real campaigns, no autopilot.\"",
  "\"Follow for the behind-the-scenes. Comment LOCAL if you want yours run like this.\"",
  "#AgencyLife #PerformanceMarketing #GTA #LocalBusiness",
  "the \"real operator at a messy desk\" visual hook that carried the 27.6× winner, as a founder-story REACH piece. Shoot it in the founder's actual workspace; use real or genericized client metrics.", True),

 ("Script 10 — \"Show up in ChatGPT — 3 steps\"", "NURTURE", "9s · trending audio · AI-avatar",
  ["none — trending audio. Optional VO: \"Get found by AI.\"",
   "split phone screen — left, a ChatGPT answer recommending a business; right, the Google Business Profile + reviews feeding it. Fast cuts.",
   "\"Show up when they ask AI — 3 steps\""],
  "rapid text cards: \"1. Claim + fully fill your Google Business Profile.\" · \"2. Get consistent, recent reviews (AI reads them).\" · \"3. One clear service page with plain-language answers.\" · \"SEO got you found on Google. This gets you found in AI.\"",
  "\"Save this. Comment AI for the full AEO checklist.\"",
  "#AEO #AISearch #LocalSEO #ChatGPT",
  "your proven AEO topic in the 6s text-listicle format — a save-bait companion to Script 4. Keeps Google (\"without ditching Google\") — never \"SEO is dead.\"", False),
]
for s in scripts:
    script_card(*s)

# ---------- 7 ----------
h2("7", "Learning loop — keep, kill, double-down")
table(["Verdict", "Reels", "Action"],
      [["DOUBLE-DOWN", "\"Halo Effect\" (9.1×), \"ChatGPT SEO\" (8.5×)", "broad psychology + AI-trend education is your reach lane — make more"],
       ["KEEP", "\"Likes don't equal leads\" (2.5×)", "solid nurture, keep the DM-keyword CTA"],
       ["KILL / REWORK", "physio & contractor pitch reels (~0.16×)", "re-shoot proof-led (Script 1/3/8 style), never pitch-first"]],
      [28, 55, 80])
para("Re-run this loop monthly: scrape your own last-30-days, score against this baseline, feed the verdicts "
     "into next month's calendar. Recompute the baseline once you have ≥30 reels.", gap=1)
para("_Method: niche-keyword discovery → account-relative outlier scoring → three-layer decode (visual via "
     "Gemini frames, spoken script via Higgsfield transcribe + translate) → format transplant onto owned "
     "proof. Research cost this run: under $1 of scraping, $0 in video credits. Scripts are traced to "
     "decoded winners and your owned client results; CONVERT slots use only proof on file._",
     size=8, color=GREY)

pdf.output("/home/user/Social-media-calender-genrator/PPC_GURU_FINAL_REPORT.pdf")
print("PDF written")
