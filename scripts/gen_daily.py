#!/usr/bin/env python3
"""
Daily brief generator — follows creator.md → categorization.md → example-output.md SOP.
Generates: output/YYYY-MM-DD.md, updates index.md, archives to storage, writes data-*.js
JS output uses UNQUOTED keys to match existing data-ai-news.js convention.
"""

import shutil, textwrap
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).parent.parent
TODAY = str(date.today())          # override with TODAY = "2026-06-22" if needed
TODAY = "2026-06-22"

# ──────────────────────────────────────────────────────────────────────────────
# JS serialiser — produces unquoted key format, matching data-ai-news.js style
# ──────────────────────────────────────────────────────────────────────────────

def js_val(v, depth=0):
    ind  = "  " * depth
    ind1 = "  " * (depth + 1)
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        escaped = v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(v, list):
        if not v:
            return "[]"
        items = [f"{ind1}{js_val(i, depth+1)}" for i in v]
        return "[\n" + ",\n".join(items) + f"\n{ind}]"
    if isinstance(v, dict):
        if not v:
            return "{}"
        pairs = []
        for k, val in v.items():
            pairs.append(f"{ind1}{k}: {js_val(val, depth+1)}")
        return "{\n" + ",\n".join(pairs) + f"\n{ind}}}"
    return str(v)


def write_data_js(feature, brief):
    path = ROOT / "website" / f"data-{feature}.js"
    inner = js_val(brief, depth=2)
    content = (
        f'window.LIM_DATA = window.LIM_DATA || {{}};\n'
        f'window.LIM_DATA["{feature}"] = {{\n'
        f'  lastUpdated: "{brief["date"]}",\n'
        f'  briefs: [\n'
        f'    {inner}\n'
        f'  ]\n'
        f'}};\n'
    )
    path.write_text(content, encoding="utf-8")
    print(f"  JS   website/data-{feature}.js")


def write_md(feature, brief):
    """Write output/YYYY-MM-DD.md following example-output.md format."""
    p_emoji = {1: "🔴 MAJOR", 2: "🟠 SIGNIFICANT", 3: "🟡 NOTABLE", 4: "⚪ FYI"}
    stories  = brief["stories"]
    n        = len(stories)
    counts   = {}
    for s in stories:
        counts[s["priority"]] = counts.get(s["priority"], 0) + 1

    cats_today = {}
    for s in stories:
        cats_today[s["category"]] = cats_today.get(s["category"], 0) + 1
    cats_str = " · ".join(f"{k} ({v})" for k, v in cats_today.items())

    all_tags = []
    for s in stories:
        all_tags += [f"`#{t}`" for t in s["tags"] if f"`#{t}`" not in all_tags]
    tags_str = " ".join(all_tags)

    lines = [
        f"# {feature.upper().replace('-', ' ')} Brief — {brief['date']}",
        "",
        f"> **Today's count:** {n} items &nbsp;|&nbsp; **Top signal:** {brief['topSignal'][0]['headline']}",
        "",
        "---",
        "",
        "## Today's Signal",
        "",
        "> Three bullets. The 3 things that matter most from today.",
        "",
    ]
    for s in brief["topSignal"]:
        lines.append(f"- **{s['headline']}** — {s['detail']}")

    lines += ["", "---", ""]

    for story in stories:
        src_parts = [f"[{s['name']}]({s['url']})" for s in story["sources"]]
        src_str   = " &nbsp;|&nbsp; ".join(src_parts)
        tags_h    = " ".join(f"`#{t}`" for t in story["tags"])
        prio_str  = p_emoji.get(story["priorityLevel"], "⚪")
        lines += [
            f"## {story['id']}. {story['title']}",
            "",
            f"**[{story['category']}]** {tags_h} — {prio_str}",
            "",
            f"**Source:** {src_str} &nbsp;|&nbsp; **Date:** {story['eventDate']}",
            "",
            "---",
            "",
            "### What happened",
            story["whatHappened"],
            "",
            "### What it can do",
        ]
        for b in story["whatItCanDo"]:
            lines.append(f"- {b}")
        lines += ["", "### What's the catch"]
        for b in story["whatsCatch"]:
            lines.append(f"- {b}")
        lines += [
            "",
            "### Key takeaway",
            f"> {story['keyTakeaway']}",
            "",
            "### How it can improve",
            story["howToImprove"],
            "",
            "### vs. Previous coverage",
            f"> *{story['vsPrevious']}*",
            "",
            "---",
            "",
        ]

    lines += [
        "## Quick Hits",
        "",
        "> Minor updates not worth a full section. One line each.",
        "",
    ]
    for q in brief["quickHits"]:
        lines.append(f"- **{q['title']}**: {q['text']} — [Source]({q['url']})")

    lines += [
        "",
        "---",
        "",
        f"## Tags used today",
        tags_str,
        "",
        f"## Categories today",
        cats_str,
        "",
        "---",
        "",
        f"*Brief compiled by Claude · Archived at `storage/{brief['date']}.md`*",
    ]

    path = ROOT / "features" / feature / "output" / f"{brief['date']}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  MD   features/{feature}/output/{brief['date']}.md")


def update_index(feature, brief):
    path = ROOT / "features" / feature / "output" / "index.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Index\n\n*Index starts below.*\n"
    entry = (
        f"## {brief['date']} — {brief['indexHeadline']}\n"
        f"{brief['indexSummary']}\n"
        f"[Full brief →]({brief['date']}.md)\n\n---\n\n"
    )
    marker = "*Index starts"
    new = existing.replace(marker, entry + marker) if marker in existing else existing + "\n" + entry
    path.write_text(new, encoding="utf-8")
    print(f"  IDX  features/{feature}/output/index.md")


def archive(feature, brief):
    src = ROOT / "features" / feature / "output" / f"{brief['date']}.md"
    dst = ROOT / "features" / feature / "storage" / f"{brief['date']}.md"
    shutil.copy2(src, dst)
    print(f"  ARC  features/{feature}/storage/{brief['date']}.md")


def run(feature, brief):
    print(f"\n[ {feature.upper()} ]")
    write_md(feature, brief)
    update_index(feature, brief)
    archive(feature, brief)
    write_data_js(feature, brief)


# ══════════════════════════════════════════════════════════════════════════════
#  BRIEF DATA — pulled from creator.md-specified sources
# ══════════════════════════════════════════════════════════════════════════════

# ── GLOBAL FINANCE ────────────────────────────────────────────────────────────
GLOBAL_FIN = {
    "date": TODAY,
    "indexHeadline": "Fed holds but turns hawkish; global growth hits 5-year low at 2.5%",
    "indexSummary": "The Federal Reserve held rates at 3.50-3.75% but Chair Kevin Warsh's first press conference leaned hawkish, lifting 2-year Treasury yields to a 12-month high. The World Bank cut 2026 global growth to 2.5% — lowest since COVID. Bank of England and Swiss National Bank both held. Nasdaq recovered +2.43% by week's end.",
    "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
    "topSignal": [
        {"headline": "Fed hawkish pivot — 9/18 officials pencil in a 2026 hike", "detail": "Chair Warsh's first press conference triggered a bond and equity sell-off. PCE inflation forecast raised to 3.6%. 2-year Treasury at 12-month high."},
        {"headline": "World Bank: global growth 2.5% in 2026 — lowest since COVID", "detail": "Middle East war driving energy price shock, inflation, and tighter financial conditions. Emerging market growth particularly at risk."},
        {"headline": "Nasdaq +2.43% — markets recover late-week after Fed sell-off", "detail": "Risk appetite returned Friday as US-Iran talks advanced and oil prices fell. S&P 500 +0.93%, Russell 2000 +1.21%."},
    ],
    "stories": [
        {
            "id": 1,
            "title": "Fed Holds at 3.50-3.75% — Hawkish Warsh Press Conference Triggers Bond Sell-Off",
            "category": "CENTRAL-BANK",
            "tags": ["rate-hike", "inflation"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "T. Rowe Price Weekly Update", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"},
                {"name": "Investing.com — Top 10 Global Economic Events 2026", "url": "https://www.investing.com/analysis/top-10-global-economic-events-of-2026-that-moved-financial-markets-200682295"},
            ],
            "eventDate": "2026-06-18",
            "whatHappened": "The Federal Reserve's June FOMC meeting left the federal funds rate unchanged at 3.50%-3.75%, but Chair Kevin Warsh's first post-meeting press conference was broadly interpreted as hawkish. The updated Summary of Economic Projections showed nine of 18 officials now pencilling in at least one rate hike before year-end. The Fed also raised its headline PCE inflation forecast to 3.6% and core PCE to 3.3% for 2026. The 2-year Treasury yield hit a 12-month high in the aftermath.",
            "whatItCanDo": [
                "Raise borrowing costs for consumers and businesses if the Fed delivers a hike in Q3 or Q4",
                "Strengthen the US dollar, pressuring emerging market currencies including the Indonesian rupiah",
                "Extend pain in rate-sensitive sectors: housing, utilities, small-cap growth",
                "Increase US government interest expense on $36T+ in outstanding debt",
            ],
            "whatsCatch": [
                "The Fed has signalled hikes before without following through — credibility depends on inflation data",
                "A hike risks tipping a slowing economy (global growth at 2.5%) into recession",
                "Political pressure from the White House favours cuts, not hikes",
                "Divergence from BOE and SNB (both holding) complicates Fed's room to tighten unilaterally",
            ],
            "keyTakeaway": "Warsh's hawkish debut ends the Fed's neutral posture — markets must now price a genuine probability of a 2026 rate hike for the first time this cycle.",
            "howToImprove": "Watch the July CPI print. If core CPI stays above 3.2%, a September hike becomes the base case. A sub-3.0% print would let Warsh pivot back to patient.",
            "vsPrevious": "First time covering the June 2026 FOMC in this terminal.",
        },
        {
            "id": 2,
            "title": "World Bank Cuts 2026 Global Growth to 2.5% — Lowest Since COVID Pandemic",
            "category": "MACRO",
            "tags": ["recession", "inflation"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "World Bank Global Economic Prospects June 2026", "url": "https://openknowledge.worldbank.org/server/api/core/bitstreams/5740355b-6f22-4c1f-a21f-015d5ff2192f/content"},
                {"name": "IMF Global Financial Stability Report April 2026", "url": "https://www.imf.org/en/publications/gfsr/issues/2026/04/14/global-financial-stability-report-april-2026"},
            ],
            "eventDate": "2026-06-20",
            "whatHappened": "The World Bank's June 2026 Global Economic Prospects report projects global growth slowing from 2.9% in 2025 to 2.5% in 2026 — the lowest rate since the COVID-19 pandemic. The primary driver is the Middle East war, which has triggered sharp increases in energy prices, renewed inflationary pressures globally, and increased expectations of monetary tightening. The IMF's April Global Financial Stability Report flags amplification risks from bond market stress and potential financial instability.",
            "whatItCanDo": [
                "Reduce revenue growth for multinational companies exposed to global demand",
                "Increase pressure on developing economy fiscal positions as export revenues fall",
                "Push central banks in developing markets to choose between defending currencies and supporting growth",
                "Create recessionary feedback loops if financial conditions tighten significantly above current levels",
            ],
            "whatsCatch": [
                "2.5% is a slowdown, not a contraction — a global recession still requires further deterioration",
                "World Bank forecasts have a long track record of being revised higher as data improves",
                "China's domestic stimulus could surprise to the upside and partially offset the energy shock",
                "The Middle East situation is volatile — a ceasefire could rapidly improve energy prices and the outlook",
            ],
            "keyTakeaway": "A 2.5% global growth rate is the floor of the post-COVID expansion — if it breaks lower, recession risk becomes the dominant market narrative for H2 2026.",
            "howToImprove": "The World Bank should publish a scenario analysis showing what happens to the 2.5% baseline under a Strait of Hormuz closure vs. a full US-Iran ceasefire — the range of outcomes is enormous.",
            "vsPrevious": "First time covering World Bank 2026 global growth forecast in this terminal.",
        },
        {
            "id": 3,
            "title": "Nasdaq +2.43%, S&P +0.93% — Markets Recover Late-Week on Iran Optimism",
            "category": "MARKETS",
            "tags": ["emerging-markets"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "T. Rowe Price Weekly Update", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"},
                {"name": "Amundi Global Investment Views June 2026", "url": "https://research-center.amundi.com/article/global-investment-views-june-2026"},
            ],
            "eventDate": "2026-06-20",
            "whatHappened": "US equity markets recovered strongly in late-week trading after the post-FOMC sell-off. The Nasdaq Composite led with +2.43%, followed by the Russell 2000 (+1.21%) and S&P 500 (+0.93%). The recovery was driven by falling oil prices as US-Iran ceasefire talks advanced, reducing the energy price headwind and improving risk sentiment. Technology and growth stocks outperformed as real rate expectations pulled back slightly.",
            "whatItCanDo": [
                "Signal that markets are pricing Iran de-escalation as the primary risk catalyst, more than Fed policy",
                "Support consumer spending indirectly if gasoline prices fall following oil's decline",
                "Encourage equity issuance and M&A that was on hold during the volatile week",
            ],
            "whatsCatch": [
                "A single session's recovery does not erase the broader downtrend — S&P is still below January 2026 levels",
                "The Fed's hawkish pivot remains intact regardless of one week's market move",
                "If Iran talks collapse, the oil rebound would reverse the equity recovery immediately",
                "Derivatives market positioning shows limited conviction — options skew remains bearish",
            ],
            "keyTakeaway": "Markets are treating Iran de-escalation as a bigger near-term catalyst than Fed hawkishness — oil prices are the dominant variable for 2026 equity performance.",
            "howToImprove": "Track Brent crude as the leading indicator for equity direction. A sustained break below $80/bbl would meaningfully ease the global inflation and Fed pressure that has dominated 2026.",
            "vsPrevious": "First time covering the June 2026 US equity weekly move in this terminal.",
        },
        {
            "id": 4,
            "title": "Bank of England Holds at 3.75%; Swiss National Bank Holds at 0%",
            "category": "CENTRAL-BANK",
            "tags": ["rate-cut"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "T. Rowe Price Weekly Update", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"},
            ],
            "eventDate": "2026-06-19",
            "whatHappened": "The Bank of England's Monetary Policy Committee voted to hold the base rate at 3.75%, citing persistent services inflation and the need to observe the pass-through of prior rate cuts to the economy. The Swiss National Bank also held its key rate at 0%, with little shift in its forecasts for Swiss growth or inflation. Both decisions were in line with market expectations.",
            "whatItCanDo": [
                "Signal that developed-market central banks outside the US are in a 'hold and assess' posture",
                "Maintain GBP/USD and CHF/USD rates near current levels, providing some stability for European-linked assets",
            ],
            "whatsCatch": [
                "BOE holding at 3.75% does not resolve UK services inflation — the fundamental problem persists",
                "The SNB's zero rate leaves it with limited ammunition if Swiss growth deteriorates",
            ],
            "keyTakeaway": "BOE and SNB both holding confirms a global central bank pause — but the Fed's hawkish break from the pack creates divergence that will pressure non-dollar currencies.",
            "howToImprove": "BOE should publish a clearer timeline for the next cut — current forward guidance is too vague to anchor inflation expectations meaningfully.",
            "vsPrevious": "First time covering June 2026 BOE and SNB decisions in this terminal.",
        },
    ],
    "quickHits": [
        {"title": "Brent crude -3% on Iran talks", "text": "Oil fell sharply as US-Iran ceasefire progress reduced geopolitical premium. Energy stocks underperformed Friday.", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"},
        {"title": "IMF flags Middle East war amplification risks", "text": "April GFSR: bond market stress, bank-sovereign nexus, and commodity price shocks all identified as systemic amplifiers.", "url": "https://www.imf.org/en/publications/gfsr/issues/2026/04/14/global-financial-stability-report-april-2026"},
        {"title": "Amundi: maintain defensive allocation", "text": "June Investment Views recommend overweight cash and commodities, underweight equities, given growth/inflation mix.", "url": "https://research-center.amundi.com/article/global-investment-views-june-2026"},
    ],
}

# ── GLOBAL NEWS ───────────────────────────────────────────────────────────────
GLOBAL_NEWS = {
    "date": TODAY,
    "indexHeadline": "US-Iran talks survive collapse scare; Al Jazeera cameraman killed in Gaza",
    "indexSummary": "Iran suspended US nuclear talks after Trump threats then returned following Qatar-Pakistan mediation. A joint US-Iran de-confliction cell for Lebanon was established — first military coordination since 1979. A Strait of Hormuz communication line was created. In Gaza, Al Jazeera cameraman Ahmed Wishah was killed in an Israeli strike. Alan Greenspan died aged 100.",
    "stats": {"total": 4, "major": 2, "significant": 1, "notable": 1},
    "topSignal": [
        {"headline": "US-Iran talks resume after near-collapse — de-confliction cell for Lebanon created", "detail": "Iran suspended talks after Trump media threats, returned after Qatar-Pakistan mediation. First US-Iran military coordination cell since 1979, covering Lebanon operations."},
        {"headline": "Al Jazeera cameraman Ahmed Wishah killed in Israeli airstrike in Gaza", "detail": "Confirmed by Al Jazeera on June 20. Part of ongoing IDF operations in Gaza. Media freedom organisations condemning the strike."},
        {"headline": "Hormuz communication line established — energy shipping risk premium falls", "detail": "Direct US-Iran naval line to ensure safe passage through the Strait. ~20% of global oil and 25% of LNG flows through daily. Oil prices fell 3% on the news."},
    ],
    "stories": [
        {
            "id": 1,
            "title": "US-Iran Nuclear Talks Survive Near-Collapse — De-Confliction Cell Formed for Lebanon",
            "category": "DIPLOMACY",
            "tags": ["nuclear", "sanctions"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "CNN World Live — Iran/Israel/Lebanon", "url": "https://www.cnn.com/2026/06/21/world/live-news/iran-war-trump-israel-lebanon"},
                {"name": "WEF — Uncertainty Around US-Iran Talks", "url": "https://www.weforum.org/stories/2026/06/uncertainty-around-us-iran-ceasefire-and-other-geopolitical-stories-to-know-this-month/"},
            ],
            "eventDate": "2026-06-21",
            "whatHappened": "Iran suspended participation in US nuclear and sanctions talks in Qatar after President Trump made threatening statements in a media interview. Following rapid mediation by Qatar and Pakistan, Iran returned to the table. Both sides described resumed talks as held in a 'positive and constructive atmosphere.' As part of the same diplomatic track, the US and Iran agreed to establish a joint de-confliction cell for Lebanon — the first formal US-Iran military coordination mechanism since the 1979 Islamic Revolution — to prevent accidental escalation in the ongoing Israel-Hezbollah conflict.",
            "whatItCanDo": [
                "Unlock potential for sanctions relief on Iranian oil exports — adding 1-1.5 million barrels/day to global supply",
                "Reduce Strait of Hormuz risk premium embedded in current oil prices",
                "Create a precedent for US-Iran direct communication extending to other flashpoints",
                "Give Qatar and Pakistan outsized geopolitical leverage as co-mediators",
            ],
            "whatsCatch": [
                "Trump's unpredictability is the single largest risk — one more media statement could end talks",
                "Khamenei must approve any deal; his position remains hardline on enrichment levels",
                "Israel has stated it will act unilaterally if Iran approaches weapons-grade enrichment",
                "The Lebanon cell coordinates but does not stop active hostilities on the ground",
            ],
            "keyTakeaway": "The US-Iran de-confliction cell is the most significant diplomatic development in 47 years — fragile, but structurally new.",
            "howToImprove": "A UN or Swiss observer role in the de-confliction cell would give both sides deniability and create an independent record of communications — essential for trust-building.",
            "vsPrevious": "First time covering US-Iran talks and Lebanon de-confliction in this terminal.",
        },
        {
            "id": 2,
            "title": "Al Jazeera Cameraman Ahmed Wishah Killed in Israeli Airstrike in Gaza",
            "category": "CONFLICT",
            "tags": ["war"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/6/20/al-jazeera-cameraman-ahmad-wishah-killed-in-israeli-attack-in-gaza"},
            ],
            "eventDate": "2026-06-20",
            "whatHappened": "Al Jazeera cameraman Ahmed Wishah was killed in an Israeli airstrike in Gaza on June 20, 2026. Al Jazeera confirmed the death and called for accountability. The strike hit in an active operations zone. Wishah is among dozens of journalists killed in Gaza since the conflict began, making it one of the deadliest conflicts for media workers in modern history. The International Federation of Journalists and Reporters Without Borders condemned the strike.",
            "whatItCanDo": [
                "Increase international pressure on Israel regarding civilian and media casualty rates in Gaza",
                "Amplify Al Jazeera's editorial coverage of the conflict as the outlet documents its own losses",
                "Provide material for UN Human Rights Council investigations into IDF operational conduct",
            ],
            "whatsCatch": [
                "Israel denies deliberately targeting journalists and cites the active combat environment",
                "International condemnation has not materially altered Israeli military operations to date",
                "The number of confirmed journalist deaths in Gaza is disputed between different tracking organisations",
            ],
            "keyTakeaway": "Gaza remains the deadliest conflict for journalists in decades — each confirmed media casualty increases legal and diplomatic pressure on Israel that accumulates over time.",
            "howToImprove": "The UN should establish an independent mechanism for rapid investigation of journalist deaths in active conflict zones, with findings published within 30 days of each incident.",
            "vsPrevious": "First time covering journalist casualties in Gaza in this terminal.",
        },
        {
            "id": 3,
            "title": "Strait of Hormuz Naval Communication Line Established Between US and Iran",
            "category": "DIPLOMACY",
            "tags": ["sanctions", "un"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "WEF — Geopolitical Stories to Know", "url": "https://www.weforum.org/stories/2026/06/uncertainty-around-us-iran-ceasefire-and-other-geopolitical-stories-to-know-this-month/"},
                {"name": "CFR — Conflicts to Watch 2026", "url": "https://www.cfr.org/reports/conflicts-watch-2026"},
            ],
            "eventDate": "2026-06-21",
            "whatHappened": "The US and Iran established a direct naval communication line to ensure safe passage through the Strait of Hormuz. The agreement followed months of disruption to global energy supplies during the Middle East conflict. Approximately 20% of global oil and 25% of global LNG transit the Strait daily. Oil prices fell 3% on the announcement as the market reduced the war risk premium on Hormuz passage.",
            "whatItCanDo": [
                "Reduce war risk insurance premiums for shipping companies operating on Hormuz routes",
                "Signal to energy markets that both sides want to avoid a full Strait closure",
                "Lower input costs for China, Japan, South Korea, and India — all heavily dependent on Gulf energy",
            ],
            "whatsCatch": [
                "A communication line does not prevent Iran's Revolutionary Guard from seizing tankers — IRGC operates semi-independently",
                "US naval presence in the Gulf is at a multi-year high, raising miscalculation risk despite the line",
                "Insurance premiums remain elevated — markets are cautiously optimistic, not fully convinced",
            ],
            "keyTakeaway": "The Hormuz communication line reduces the probability of accidental escalation — the most dangerous near-term risk — without resolving the underlying conflict.",
            "howToImprove": "Lloyd's of London war risk premiums are the real-time signal to watch: a drop above 20% this week would confirm market credibility of the communication line.",
            "vsPrevious": "First time covering Strait of Hormuz risk in this terminal.",
        },
        {
            "id": 4,
            "title": "Alan Greenspan, Former Federal Reserve Chair, Dies at 100",
            "category": "POLITICS",
            "tags": ["g7"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "NBC News", "url": "https://www.nbcnews.com/news/obituaries/alan-greenspan-economist-longtime-head-federal-reserve-dies-100-rcna42286"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "Alan Greenspan, who served as Chairman of the Federal Reserve from 1987 to 2006 — spanning the Reagan, Bush Sr., Clinton, and Bush Jr. administrations — died at the age of 100. Greenspan oversaw the 1987 Black Monday response, the dot-com boom, the September 11 aftermath, and the conditions that contributed to the 2008 global financial crisis. His legacy remains contested: celebrated for the 'Great Moderation' of the 1990s-2000s, criticised for his faith in self-regulating markets and the subprime mortgage crisis.",
            "whatItCanDo": [
                "Prompt renewed debate about the role of central bank independence, which Greenspan championed",
                "Draw comparisons to current Fed Chair Warsh's approach at a time of renewed monetary policy uncertainty",
            ],
            "whatsCatch": [
                "Greenspan's reputation was significantly damaged by his admission that he had found a 'flaw' in his free-market ideology after the 2008 crisis",
                "His tenure is studied as a cautionary tale about regulatory complacency as much as a success story",
            ],
            "keyTakeaway": "Greenspan's death closes a chapter in central banking history — and his 2008 admission of ideological error remains the most consequential self-critique by any central bank chair.",
            "howToImprove": "The Federal Reserve should commission a public retrospective on the Greenspan era's policy lessons — not as hagiography, but as institutional learning.",
            "vsPrevious": "First time covering this topic in this terminal.",
        },
    ],
    "quickHits": [
        {"title": "FIFA World Cup — Morocco, Japan in quarterfinals", "text": "2026 World Cup continues with upsets. Morocco and Japan both through. USA faces Brazil in Round of 16.", "url": "https://www.cnn.com/2026/06/21/world/live-news/iran-war-trump-israel-lebanon"},
        {"title": "Ukraine attacks Crimea fuel infrastructure", "text": "Russian-occupied Crimea suspended civilian gasoline sales as Ukraine ramped up drone strikes on fuel supply depots.", "url": "https://www.dbresearch.com/PROD/IE-PROD/PROD0000000000629523/This_Month_in_Geopolitics:_June_2026.pdf"},
        {"title": "DC Reflecting Pool vandalism — former Olympian charged", "text": "Multiple arrests including a former Olympian after vandalism at the Lincoln Memorial Reflecting Pool. Trump ordered immediate repairs.", "url": "https://www.foxnews.com/politics/former-olympian-among-charged-vandalizing-reflecting-pool-trump-vows-immediate-repairs-report"},
    ],
}

# ── INDONESIA FINANCE ─────────────────────────────────────────────────────────
INDO_FIN = {
    "date": TODAY,
    "indexHeadline": "BI raises rate 25bps to 5.75%; banks face liquidity squeeze as global funds withdraw",
    "indexSummary": "Bank Indonesia raised the BI-Rate 25bps to 5.75% at its June 17-18 meeting to defend the rupiah against capital flight. Banks are reporting liquidity pressure since April as global funds exit developing markets. Kontan analysis suggests MSCI may retain Indonesia at emerging market status. The government is developing IIFC, an international financial centre rivalling Dubai.",
    "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
    "topSignal": [
        {"headline": "BI Rate at 5.75% — highest since 2019, banks feel the squeeze", "detail": "25bps hike at June 17-18 board meeting. Lending Facility rate now 6.50%. Construction credit at risk in H2 2026 as banks' cost of funds rises."},
        {"headline": "Global funds withdrawing from Indonesia since April — liquidity tight", "detail": "Bank BTN Chief Economist confirmed liquidity pressure since April, triggered by oil prices and Middle East tensions. Capital outflows not yet reversed."},
        {"headline": "MSCI may retain Indonesia as Emerging Market — Kontan analysis", "detail": "Analyst consensus on kontan.co.id suggests MSCI will maintain EM classification despite recent concerns. Frontier downgrade risk receding."},
    ],
    "stories": [
        {
            "id": 1,
            "title": "Bank Indonesia Raises BI-Rate 25bps to 5.75% to Defend Rupiah",
            "category": "RUPIAH",
            "tags": ["bi-rate", "rupiah"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "Bank Indonesia — BI-Rate Press Release", "url": "https://www.bi.go.id/en/publikasi/ruang-media/news-release/Pages/sp_2725025.aspx"},
                {"name": "Kontan — Perbankan Waspadai Tekanan Likuiditas", "url": "https://keuangan.kontan.co.id/news/perbankan-waspadai-tekanan-likuiditas-di-tengah-gejolak-global"},
            ],
            "eventDate": "2026-06-18",
            "whatHappened": "Bank Indonesia's Board of Governors agreed at its June 17-18 meeting to raise the BI-Rate by 25 basis points to 5.75%, lifting the Deposit Facility rate to 4.75% and the Lending Facility rate to 6.50%. The hike is designed to defend the rupiah and prevent further capital outflows amid global risk-off sentiment driven by Middle East tensions and rising US interest rate expectations. Bank BTN's Chief Economist noted that liquidity pressure has been felt since April 2026, with global funds beginning to withdraw from developing markets.",
            "whatItCanDo": [
                "Defend the rupiah by making IDR-denominated assets more attractive on a carry basis",
                "Signal BI's commitment to currency stability over growth support in the near term",
                "Reduce speculative rupiah selling by raising the cost of short positions",
                "Contain imported inflation from a weaker currency",
            ],
            "whatsCatch": [
                "Higher rates will slow domestic credit growth — construction and consumer lending are already slowing",
                "Banks face a cost-of-funds squeeze: deposit rates must rise to match BI Rate, compressing margins",
                "NPL (non-performing loan) risks are rising in the construction sector as rates increase",
                "BI cannot sustain aggressive hiking without causing a domestic economic slowdown",
            ],
            "keyTakeaway": "BI's rate hike is the right call for macro stability, but the cost is a credit slowdown in H2 2026 that will weigh on economic growth and banking sector earnings.",
            "howToImprove": "BI should accompany the rate hike with targeted liquidity support for SME lenders to prevent the rate increase from cutting off productive credit entirely. Blanket tightening without sector-specific support is blunt.",
            "vsPrevious": "First time covering Bank Indonesia rate decisions in this terminal.",
        },
        {
            "id": 2,
            "title": "MSCI Likely to Retain Indonesia as Emerging Market — Analyst Consensus",
            "category": "IDX",
            "tags": ["ihsg", "emerging-markets"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "Kontan — MSCI Bisa Pertahankan Indonesia", "url": "https://investasi.kontan.co.id/news/msci-bisa-pertahankan-indonesia-di-emerging-market-ini-alasannya"},
                {"name": "IDX Tracker June 2026", "url": "https://www.idxtracker.com/"},
            ],
            "eventDate": "2026-06-21",
            "whatHappened": "Analyst consensus reported by kontan.co.id suggests MSCI is likely to retain Indonesia in its Emerging Markets index rather than downgrade to Frontier Market status at this review cycle. Analysts cite recent IDX governance improvements, OJK's fast-tracking of market surveillance rules, and the BI rate hike stabilising the rupiah as factors supporting EM retention. The formal MSCI decision is expected this week. A downgrade would have forced passive EM funds to sell Indonesian equities, estimated at USD 2-4 billion in forced outflows.",
            "whatItCanDo": [
                "Remove the largest single market overhang on IHSG sentiment if EM status is confirmed",
                "Enable IHSG to sustain its recovery from the June 8 low of 5,342 toward the 6,500 range",
                "Restore confidence among foreign institutional investors considering re-entry into Indonesian equities",
                "Give IDX and OJK breathing room to implement governance reforms at a measured pace",
            ],
            "whatsCatch": [
                "MSCI retaining EM status does not resolve the underlying concerns about shareholding transparency",
                "If concerns are flagged but not acted on, MSCI could downgrade at the next review in 6-12 months",
                "Coordinated trading risks on IDX have not been structurally eliminated — only partially addressed",
                "Foreign net selling has continued even during the IHSG recovery — retention alone won't reverse flows immediately",
            ],
            "keyTakeaway": "MSCI EM retention is the near-term positive catalyst for IHSG — but it buys time, not a permanent fix for the underlying market structure concerns.",
            "howToImprove": "IDX must publish a concrete 12-month roadmap for shareholding disclosure reform with quarterly milestones. MSCI will review again — Indonesia needs to show progress, not just intent.",
            "vsPrevious": "First time covering MSCI classification risk for Indonesia in this terminal.",
        },
        {
            "id": 3,
            "title": "Government Develops IIFC — International Financial Centre Rivalling Dubai",
            "category": "REGULATION",
            "tags": ["trade-war", "emerging-markets"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "Kontan — Airlangga IIFC Statement", "url": "https://nasional.kontan.co.id/news/airlangga-pemerintah-siapkan-iifc-setara-dubai-investor-diberi-insentif-khusus"},
                {"name": "Bank Indonesia Presentation Book June 2026", "url": "https://www.bi.go.id/en/iru/presentation/Pages/Republic-of-Indonesia-Presentation-Book---June-2026.aspx"},
            ],
            "eventDate": "2026-06-21",
            "whatHappened": "Coordinating Minister Airlangga Hartarto announced that the Indonesian government is developing the Indonesia International Financial Centre (IIFC), positioned as a financial hub equivalent to Dubai's DIFC or Singapore's MAS-regulated financial centre. The IIFC will offer special incentives and regulatory flexibility for international investors. Inter-ministerial discussions on the incentive framework and institutional structure are ongoing as of June 22, with a formal launch timeline not yet announced.",
            "whatItCanDo": [
                "Attract Islamic finance, hedge funds, and family offices that currently route through Singapore or Dubai",
                "Create a regulatory sandbox for fintech and digital asset firms wanting ASEAN access",
                "Reduce Indonesia's dependence on Singapore as the gateway for foreign capital into Indonesian markets",
                "Generate fee income and high-skilled employment in financial services — currently underdeveloped relative to GDP",
            ],
            "whatsCatch": [
                "Singapore and Dubai have decades of institutional trust, legal certainty, and talent pipelines that Indonesia cannot replicate quickly",
                "Indonesia's legal system and contract enforcement reliability are consistently cited as barriers for institutional investors",
                "The IIFC competes with Nusantara capital project for government attention and budget — both cannot be fully resourced simultaneously",
                "No formal legislation, location, or launch date announced — still in planning phase",
            ],
            "keyTakeaway": "IIFC is an ambitious long-term vision, but without a concrete legal framework and an independent regulator, it risks being another announcement without execution.",
            "howToImprove": "The government should engage Singapore's MAS and Dubai's DFSA as technical advisors on regulatory architecture — building credibility by association before trying to compete with them.",
            "vsPrevious": "First time covering IIFC development in this terminal.",
        },
        {
            "id": 4,
            "title": "KB Bank Q1 2026: Credit Rp43.19T, Net Interest Income +97.28% YoY",
            "category": "BANKING",
            "tags": ["earnings"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "CNBC Indonesia — KB Bank Q1 2026", "url": "https://www.cnbcindonesia.com/news/20260622083829-4-744475/kb-bank-perkuat-pertumbuhan-lewat-kemitraan-layanan-transformasi"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "KB Bank (formerly KEB Hana Bank Indonesia) reported strong Q1 2026 performance: total credit channelled of Rp43.19 trillion and net interest income of Rp363 billion, up 97.28% compared to the same period in 2025. The bank attributed growth to expanded partnerships, improved service quality, and digital transformation initiatives. KB Bank is a subsidiary of KB Financial Group (South Korea) and focuses on corporate and SME lending in Indonesia.",
            "whatItCanDo": [
                "Demonstrate that Korean-owned banks are expanding aggressively in Indonesia despite global risk-off environment",
                "Signal that NII growth remains strong in Indonesian banking even as BI hikes create cost-of-funds pressure",
            ],
            "whatsCatch": [
                "97% NII growth is from a low base — absolute NII of Rp363B is small relative to Indonesia's largest state banks",
                "The BI rate hike to 5.75% will increase KB Bank's deposit costs in Q2-Q3, likely moderating NII growth",
                "KB Bank's loan-to-deposit ratio and NPL figures were not disclosed in the announcement",
            ],
            "keyTakeaway": "KB Bank's strong Q1 shows foreign bank subsidiaries are growing faster than the headline market stress suggests — but the rate hike will test margins in H2.",
            "howToImprove": "KB Bank should publish NPL ratios and sector exposure breakdown to give investors a complete picture of credit quality alongside the impressive top-line growth.",
            "vsPrevious": "First time covering KB Bank in this terminal.",
        },
    ],
    "quickHits": [
        {"title": "Construction credit NPL risk rising — BI warns", "text": "Higher BI Rate to 5.75% will affect construction credit disbursement in H2 2026. Banks increasing provisioning as borrower stress mounts.", "url": "https://keuangan.kontan.co.id/news/kredit-konstruksi-masih-tumbuh-tinggi-tapi-perbankan-perlu-waspada-kenaikan-npl"},
        {"title": "BI June 2026 Presentation Book available", "text": "Bank Indonesia published its updated Republic of Indonesia Presentation Book for June 2026, covering macro, monetary, and external sector data.", "url": "https://www.bi.go.id/en/iru/presentation/Pages/Republic-of-Indonesia-Presentation-Book---June-2026.aspx"},
        {"title": "IDX IHSG at 6,185 — up 0.2% in early Monday trade", "text": "Jakarta Composite edged up 12 points as Iran optimism offset Fed hawkishness. Market watching MSCI decision this week.", "url": "https://www.idxtracker.com/"},
    ],
}

# ── INDONESIA NEWS ────────────────────────────────────────────────────────────
INDO_NEWS = {
    "date": TODAY,
    "indexHeadline": "Three protest groups hit Jakarta; PMII demands full cabinet evaluation under Prabowo",
    "indexSummary": "Three separate protest groups gathered in Jakarta on June 22 — PMII demanding Merah Putih Cabinet evaluation, Jakarta Community Alliance supporting free meals, and KNARA demanding a National Agrarian Reform Body. Indonesia projects 3.88 million green jobs in 2026. PT Pupuk Indonesia began exporting urea to Australia. Indonesian police seized Rp97.8B worth of etomidate at Soekarno-Hatta.",
    "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
    "topSignal": [
        {"headline": "Three protest groups in Jakarta — PMII demands Merah Putih Cabinet evaluation", "detail": "PB PMII, Jakarta Community Alliance, and KNARA (agrarian reform coalition) all mobilised on June 22. PMII's call for full cabinet evaluation is the most significant political demand."},
        {"headline": "Indonesia to create 3.88 million green jobs in 2026 — Ministry of Manpower", "detail": "Green economy employment projection from Employment Outlook 2026. Low-emission farming and renewable energy transition cited as primary drivers."},
        {"headline": "PT Pupuk Indonesia exports first 47,250-tonne urea shipment to Australia", "detail": "Part of a 250,000-tonne trade agreement. Arrives at Port of Brisbane. Significant for Indonesia's agricultural export diversification strategy."},
    ],
    "stories": [
        {
            "id": 1,
            "title": "Three Groups Protest in Jakarta — PMII Demands Full Evaluation of Merah Putih Cabinet",
            "category": "POLITICS",
            "tags": ["presiden", "dpr"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "Tempo.co — Jakarta Braces for Three Protests", "url": "https://en.tempo.co/read/2109674/jakarta-braces-for-three-protests-across-the-city-today"},
                {"name": "Antara News", "url": "https://en.antaranews.com/"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "Three separate protest groups mobilised in Jakarta on June 22, 2026. The Central Board of the Indonesian Islamic Students Movement (PB PMII) held the most politically significant rally, calling for a total evaluation of President Prabowo Subianto's Merah Putih Cabinet and Deputy President Gibran Rakabuming Raka's administration. Separately, the Jakarta Community Alliance held a demonstration supporting the free nutritious meals program (makan bergizi gratis). A third group, the National Coalition for Agrarian Reform (KNARA), demanded the immediate establishment of the National Agrarian Reform Body (BNARA). Police monitored all three gatherings.",
            "whatItCanDo": [
                "Signal growing organised civil society pressure on the Prabowo administration from across the political spectrum",
                "PMII's demand for a cabinet evaluation could embolden other student and civil society groups to escalate demands",
                "KNARA's agrarian reform demand draws attention to unresolved land rights conflicts across the archipelago",
                "Competing protest agendas on the same day reduce the clarity of the political message — government can dismiss each individually",
            ],
            "whatsCatch": [
                "Scale remains limited — hundreds, not thousands, with no national coordination yet",
                "Prabowo's coalition controls ~80% of parliament, limiting opposition channels for amplification",
                "The pro-government Jakarta Community Alliance protest complicates the narrative: not all protesters oppose Prabowo",
                "Student protests in Indonesia historically require sustained momentum over weeks to achieve policy impact",
            ],
            "keyTakeaway": "Multiple protest groups on the same day reflects diffuse but real social pressure on Prabowo — the critical question is whether PMII can unify demands into a sustained national movement.",
            "howToImprove": "The Prabowo administration should respond to PMII's evaluation demand with a concrete accountability mechanism — ignoring organised Islamic student movements has historically backfired for Indonesian governments.",
            "vsPrevious": "First time covering Jakarta protests under the Prabowo administration in this terminal.",
        },
        {
            "id": 2,
            "title": "Indonesia's Green Economy to Create 3.88 Million Jobs in 2026 — Ministry of Manpower",
            "category": "ECONOMY",
            "tags": ["infrastruktur", "pendidikan"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "Antara — Ministry Projects 3.88 Million Green Jobs", "url": "https://en.antaranews.com/news/419999/ministry-projects-388-million-green-jobs-in-indonesia-in-2026"},
            ],
            "eventDate": "2026-06-21",
            "whatHappened": "Indonesia's Ministry of Manpower projected that the green economy will create approximately 3.88 million employment opportunities across Indonesia in 2026, according to the Employment Outlook 2026 report. The projection covers jobs in renewable energy, sustainable agriculture, eco-tourism, and green manufacturing. The government is simultaneously preparing a low-emission rice farming transition, targeting low- and medium-yield production areas across Java and Sumatra.",
            "whatItCanDo": [
                "Provide a counter-narrative to the protest concerns about economic pressures — green jobs as policy response",
                "Support Indonesia's Paris Agreement NDC commitments through domestic job creation incentives",
                "Create training and reskilling opportunities for workers displaced from coal and conventional agriculture",
                "Attract international green finance and climate fund flows to support the job creation program",
            ],
            "whatsCatch": [
                "3.88M is a projection — actual job creation depends on investment flows and policy implementation that remain uncertain",
                "Green jobs often pay less than fossil fuel sector jobs, particularly in the early transition phase",
                "Low-emission farming transition requires significant farmer education and equipment investment — timelines typically 3-5 years",
                "The coal mining sector employs ~100,000 directly and many more indirectly — green job creation must absorb this workforce",
            ],
            "keyTakeaway": "3.88M green jobs is a politically useful number, but the government needs a detailed transition plan showing how coal workers specifically will be reskilled and rehired.",
            "howToImprove": "The Ministry should publish a sector-by-sector breakdown of the 3.88M jobs — renewable energy vs. agriculture vs. eco-tourism — with regional distribution data showing which provinces benefit most.",
            "vsPrevious": "First time covering Indonesia green economy employment in this terminal.",
        },
        {
            "id": 3,
            "title": "PT Pupuk Indonesia Exports First 47,250-Tonne Urea Shipment to Australia",
            "category": "ECONOMY",
            "tags": ["ekspor", "pertamina"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "Antara — Indonesia's First Urea Shipment to Australia", "url": "https://en.antaranews.com/news/419983/indonesias-first-47250-tonne-urea-shipment-reaches-australia"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "State fertiliser producer PT Pupuk Indonesia delivered its first urea export consignment of 47,250 tonnes to the Port of Brisbane, Australia, on June 22, 2026. The shipment is part of a government-to-government trade agreement between Indonesia and Australia for 250,000 tonnes of urea. This is PT Pupuk Indonesia's first significant agricultural commodity export to Australia, part of Indonesia's strategy to diversify export revenues and deepen trade ties with Australia.",
            "whatItCanDo": [
                "Open a recurring export channel for Indonesian urea to Australia worth approximately $100-120M at current prices for the full 250,000T",
                "Strengthen the Indonesia-Australia trade relationship ahead of IA-CEPA review discussions",
                "Support PT Pupuk Indonesia's revenue diversification beyond domestic subsidised fertiliser sales",
                "Demonstrate SOE capacity to compete in international markets — relevant for BUMN reform narrative",
            ],
            "whatsCatch": [
                "Urea export revenue depends on global urea prices, which are volatile and currently below 2022 highs",
                "Australia's domestic fertiliser market is competitive — sustaining the contract beyond the initial 250,000T requires price competitiveness",
                "PT Pupuk Indonesia's primary mandate is domestic food security — large exports could create domestic supply tension if needed",
            ],
            "keyTakeaway": "Indonesia's first major urea export to Australia is a concrete SOE trade success — modest in scale but significant as a proof of concept for agricultural export diversification.",
            "howToImprove": "PT Pupuk Indonesia should disclose the contract pricing and duration to allow market assessment of whether this is a sustainable commercial arrangement or a one-time diplomatic trade.",
            "vsPrevious": "First time covering PT Pupuk Indonesia in this terminal.",
        },
        {
            "id": 4,
            "title": "Police Seize Rp97.8B Etomidate Haul at Soekarno-Hatta — International Ring Bust",
            "category": "LAW",
            "tags": ["hukum", "kpk"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "Antara — Police Confiscate Rp97B Etomidate", "url": "https://en.antaranews.com/news/420001/police-confiscate-rp97-bln-worth-of-etomidate-from-international-ring"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "The Soekarno-Hatta Airport Police seized 8.6 litres of etomidate — a Class II narcotic — with a street value of Rp97.8 billion (approximately US$5.3 million) from an international drug trafficking ring. The seizure targeted an organised network operating through Soekarno-Hatta. Etomidate is a sedative anaesthetic increasingly abused in Indonesia and Southeast Asia. Multiple arrests were made in connection with the seizure.",
            "whatItCanDo": [
                "Demonstrate the effectiveness of airport-based narcotic interdiction at Indonesia's busiest international gateway",
                "Disrupt a specific international trafficking route for etomidate entering Indonesia",
                "Signal to international trafficking networks that Soekarno-Hatta surveillance has improved",
            ],
            "whatsCatch": [
                "Etomidate trafficking has been rising across Southeast Asia — one seizure addresses a symptom, not the source supply chain",
                "The international network's origin country and full structure have not been disclosed",
                "Rp97.8B in street value suggests a significant but not extraordinary seizure by regional standards",
            ],
            "keyTakeaway": "The etomidate bust at Soekarno-Hatta highlights Indonesia's growing vulnerability to synthetic drug trafficking via international air routes — a challenge requiring regional cooperation, not just airport security.",
            "howToImprove": "Indonesia should fast-track its bilateral drug enforcement agreements with origin countries identified in the investigation. Airport interdiction without upstream disruption only creates temporary setbacks for networks.",
            "vsPrevious": "First time covering drug trafficking in this terminal.",
        },
    ],
    "quickHits": [
        {"title": "Jakarta prepares for city's 500th anniversary", "text": "Antara reports Jakarta is advancing global city positioning plans tied to its 2027 500th anniversary. Cultural and infrastructure milestones being organised.", "url": "https://en.antaranews.com/news/419991/jakarta-prepares-as-global-city-push-ahead-of-the-500th-anniversary"},
        {"title": "Low-emission rice farming transition begins", "text": "Government targets low- and medium-yield rice production areas for transition to low-emission systems. Java and Sumatra priority zones.", "url": "https://en.antaranews.com/news/419995/indonesia-prepares-low-emission-farming-transition"},
        {"title": "Trade Minister pushes franchise expansion globally", "text": "Minister Budi Santoso urges Indonesian franchises to expand internationally — citing established market share and management as key advantages.", "url": "https://en.antaranews.com/news/419944/indonesia-taps-franchise-models-to-boost-global-expansion"},
    ],
}

# ── CRYPTO NEWS ───────────────────────────────────────────────────────────────
CRYPTO_NEWS = {
    "date": TODAY,
    "indexHeadline": "BTC $63,996 — derivatives signal scepticism despite rally; ETF outflows 6th straight week",
    "indexSummary": "Bitcoin trades near $63,996 as Iran optimism pushed oil lower. ETH +2.4%, SOL +1.5% on the day. BTC spot ETFs recorded $228M in outflows this week — the 6th consecutive week of net redemptions totalling $5.94B. Taiko L2 network halted after a bridge exploit costing ~$1.7M. Bitmine bought $92M in ETH last week. Derivatives show scepticism over sustained rally.",
    "stats": {"total": 5, "major": 1, "significant": 2, "notable": 2},
    "topSignal": [
        {"headline": "BTC $63,996 — gains fail to convince; derivatives lean bearish", "detail": "Bitcoin up 1.4% as Iran-US oil correlation trades. CoinDesk: options skew and perpetual funding rates signal institutional scepticism about a sustained move higher."},
        {"headline": "BTC ETF outflows: 6th consecutive week, $5.94B cumulative", "detail": "US spot BTC ETFs shed $228M in the latest week. Outflow streak began in mid-May. Cumulative $5.94B represents significant reversal from Q1 2026 inflows."},
        {"headline": "Taiko L2 bridge exploit — network halted, $1.7M lost", "detail": "Taiko's Ethereum Layer-2 network halted after a bridge vulnerability was exploited. Approximately $1.7M in losses confirmed."},
    ],
    "stories": [
        {
            "id": 1,
            "title": "Bitcoin $63,996 — Altcoins Rally but Derivatives Signal Scepticism Over Sustained Move",
            "category": "BTC",
            "tags": ["bitcoin", "on-chain"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "CoinDesk — BTC holds near $64,000 as US-Iran talks progress", "url": "https://www.coindesk.com/markets/2026/06/22/bitcoin-holds-near-usd64-000-as-us-iran-talks-progress-but-crypto-sits-out-the-rally"},
                {"name": "CoinDesk — BTC, altcoin prices gain, derivatives signal scepticism", "url": "https://www.coindesk.com/markets/2026/06/22/as-bitcoin-altcoin-prices-gain-derivatives-signal-skepticism-over-a-sustained-rally"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "Bitcoin is trading at approximately $63,996 as of June 22, up 1.4% since midnight UTC after US-Iran talks progress sent oil prices lower. Major altcoins outperformed: ETH +2.4%, SOL +1.5%, BNB +1.5%. Despite the gains, CoinDesk reports that derivatives market indicators including options skew and perpetual funding rates show institutional scepticism about a sustained rally. Bitcoin is still down 0.4% over 24 hours and 2.2% on the week. The broader narrative remains one of crypto sitting out the risk-asset rally driven by Iran optimism.",
            "whatItCanDo": [
                "If Iran-oil correlation holds, further ceasefire progress could push BTC toward $66,000-$68,000 short term",
                "Altcoin outperformance (ETH, SOL) suggests capital rotation within crypto — positive for DeFi and L1 ecosystems",
                "A close above $65,000 would technically break the downtrend from the January highs",
            ],
            "whatsCatch": [
                "Derivatives signal scepticism — large players are not backing the move with conviction positioning",
                "BTC ETF outflows are ongoing: if ETFs continue to bleed, spot buying from retail cannot offset institutional exits",
                "A collapse in Iran talks would reverse the oil/risk catalyst and likely push BTC back below $62,000",
                "30% YTD decline has damaged the retail 'number go up' narrative — no obvious near-term catalyst for new ATH",
            ],
            "keyTakeaway": "BTC's $64K is a geopolitics-driven bounce, not a structural reversal — the derivatives market knows it and is not chasing.",
            "howToImprove": "Watch on-chain long-term holder accumulation: if LTH net position change turns positive this week, it signals real conviction buying beneath the surface. Currently LTH are not accumulating at this level.",
            "vsPrevious": "First time covering BTC daily market action in this terminal.",
        },
        {
            "id": 2,
            "title": "BTC Spot ETFs: 6th Consecutive Week of Outflows — $5.94B Cumulative",
            "category": "MACRO",
            "tags": ["bitcoin", "etf"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "CoinDesk — Bitcoin ETF Outflow Pain Eases", "url": "https://www.coindesk.com/daybook-us/2026/06/22/bitcoin-etf-outflow-pain-eases-just-as-another-headwind-strengthens"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "US spot Bitcoin ETFs recorded approximately $228 million in net redemptions in the week ending June 20, marking the sixth consecutive week of net outflows. The cumulative total since the outflow streak began in mid-May has reached $5.94 billion. The pace of outflows is slowing — the record 13-day consecutive outflow streak ended June 5 — but has not yet reversed to net inflows. BlackRock's IBIT and Fidelity's FBTC have both seen significant redemptions relative to their earlier inflow peaks.",
            "whatItCanDo": [
                "A reversal to net inflows would be the most powerful near-term bullish signal for BTC price",
                "If outflows slow to under $100M/week, it suggests institutional selling pressure is exhausting",
                "The cumulative $5.94B represents BTC that has been liquidated — once outflows stop, that overhang is removed",
            ],
            "whatsCatch": [
                "$5.94B in cumulative outflows represents a significant structural shift in institutional positioning on BTC",
                "The Fed's hawkish pivot is an ongoing headwind — rising real rates are structurally negative for BTC as an asset class",
                "If a sixth week turns into a seventh, market confidence in BTC as an institutional product will be further damaged",
                "ETF outflows are lagging indicators — by the time they reverse, price may have already moved significantly",
            ],
            "keyTakeaway": "Six weeks of continuous BTC ETF outflows confirms institutional risk-off, not just retail selling — the reversal signal to watch is weekly inflows, not BTC price.",
            "howToImprove": "Bloomberg Intelligence should publish daily ETF flow data with a breakdown by fund. Currently the data lag of several days reduces the signal value for active traders.",
            "vsPrevious": "First time covering BTC ETF flow data in this terminal.",
        },
        {
            "id": 3,
            "title": "Taiko L2 Bridge Exploit — Network Halted, ~$1.7M Lost",
            "category": "HACK",
            "tags": ["exploit", "bridge", "l2"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "The Block — Taiko Bridge Exploit", "url": "https://www.theblock.co/"},
                {"name": "CoinDesk — Crypto Security Update", "url": "https://www.coindesk.com/"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "Taiko, an Ethereum Layer-2 network, halted its bridge operations after a vulnerability was exploited, resulting in losses estimated at approximately $1.7 million. The Taiko team confirmed the halt on social media and stated that investigations are ongoing. The exploit targeted Taiko's bridge contract — the mechanism that allows assets to move between Ethereum mainnet and the Taiko L2. Taiko uses a based rollup architecture that relies on Ethereum for sequencing.",
            "whatItCanDo": [
                "Force a comprehensive security audit of the bridge contract before Taiko can restart operations",
                "Highlight bridge security as the weakest link in L2 infrastructure — a known but underweighted risk",
                "Potentially delay Taiko's planned ecosystem expansion if the root cause is architectural rather than implementation-level",
            ],
            "whatsCatch": [
                "$1.7M loss is relatively small compared to major bridge hacks (Ronin $625M, Wormhole $320M) — but reputational damage is disproportionate for an early-stage L2",
                "Based rollup architecture does not eliminate bridge risk — the sequencing model is safe, but bridge contracts remain attack surfaces",
                "No timeline for network resumption has been announced",
                "User funds locked in the bridge during the halt are inaccessible — unknown duration of freeze",
            ],
            "keyTakeaway": "Taiko's bridge exploit is a reminder that every new L2 is a security experiment at launch — bridge contracts are consistently the highest-risk component and deserve the most rigorous auditing.",
            "howToImprove": "Taiko should implement a multi-signature time-locked bridge with emergency circuit breakers before resuming — the current architecture allowed a single exploit to halt the entire network.",
            "vsPrevious": "First time covering Taiko in this terminal.",
        },
        {
            "id": 4,
            "title": "Bitmine Buys $92M in ETH — Closing in on 5% Network Ownership Target",
            "category": "ETH",
            "tags": ["ethereum", "staking"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "CoinDesk — Bitmine ETH Purchase", "url": "https://www.coindesk.com/business/2026/06/22/bitmine-added-usd92-million-of-eth-with-tom-lee-continuing-to-believe-in-crypto-spring"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "Bitmine (ticker: BMNR), a publicly traded company that has pivoted to an Ethereum accumulation strategy, added $92 million of ETH last week, closing in on its publicly stated goal of owning 5% of the Ethereum network's supply. Tom Lee, Bitmine's strategic advisor and founder of Fundstrat, continues to maintain his 'crypto spring' thesis, predicting ETH will reach $250,000. Bitmine is part of a trend of publicly listed companies adopting aggressive crypto accumulation strategies.",
            "whatItCanDo": [
                "Signal to traditional equity investors that institutional crypto accumulation is ongoing despite the bear market",
                "Create a new class of Ethereum proxy stocks for investors who cannot hold ETH directly",
                "Add to the structural supply demand pressure on ETH — 5% of circulating supply held by one entity is significant",
            ],
            "whatsCatch": [
                "A 5% ownership target by one entity is a significant concentration risk for a supposedly decentralised network",
                "Tom Lee's $250,000 ETH prediction implies a ~65x return from current levels — extraordinary claims require extraordinary evidence",
                "Bitmine's stock is leveraged to ETH price — a further BTC/ETH decline would severely damage the company's balance sheet",
                "The 'crypto spring' narrative has been called prematurely multiple times in 2025-2026",
            ],
            "keyTakeaway": "Bitmine's $92M ETH purchase is a bold accumulation bet — but a single company targeting 5% of ETH supply raises concentration and governance concerns that the Ethereum community should address.",
            "howToImprove": "Ethereum Foundation should publish a position on maximum acceptable single-entity ETH holdings and how it relates to decentralisation. Silence on concentration risks is not a policy.",
            "vsPrevious": "First time covering Bitmine and ETH institutional accumulation in this terminal.",
        },
        {
            "id": 5,
            "title": "Ethereum Validator Redirected Revenue Proposal Introduced",
            "category": "ETH",
            "tags": ["ethereum", "staking"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "CoinDesk — Ethereum Validator Proposal", "url": "https://www.coindesk.com/daybook-us/2026/06/22/bitcoin-etf-outflow-pain-eases-just-as-another-headwind-strengthens"},
            ],
            "eventDate": "2026-06-20",
            "whatHappened": "A new Ethereum governance proposal has introduced 'validator redirected revenue' — a protocol-level mechanism that would allow Ethereum network validators to voluntarily redirect a portion of their staking rewards to ecosystem development funding. The proposal is in early discussion phase and has not yet been assigned an EIP number. If adopted, it could create a sustainable, on-chain funding source for Ethereum protocol development independent of Ethereum Foundation grants.",
            "whatItCanDo": [
                "Create a protocol-native funding stream for Ethereum development without relying on Ethereum Foundation ETH sales",
                "Align validator economic interests with protocol health by giving them governance control over development funds",
                "Fund security research, formal verification, and public goods that current grant processes underprioritise",
            ],
            "whatsCatch": [
                "Voluntary redirect mechanisms historically see low participation — most validators will default to keeping maximum yield",
                "If the redirect is mandatory, it reduces validator economics and may push smaller validators below profitability",
                "Lido and Coinbase combined control >40% of staked ETH — they would dominate any resulting treasury governance",
                "EIP process for this type of change could take 12-18 months to reach mainnet",
            ],
            "keyTakeaway": "Validator redirected revenue is a clever funding mechanism in principle — but the governance of the resulting treasury is where the real risk lies, and it deserves extensive community debate before moving forward.",
            "howToImprove": "The proposal needs a formal EIP author, independent economic modelling of validator participation rates at different redirect levels, and explicit governance design before advancing.",
            "vsPrevious": "First time covering Ethereum validator funding governance in this terminal.",
        },
    ],
    "quickHits": [
        {"title": "USB malware hijacking crypto wallets — Microsoft warning", "text": "Microsoft confirmed malware spreading via USB sticks that harvests private keys from browser wallet extensions. Move to cold storage.", "url": "https://www.theblock.co/"},
        {"title": "Tom Lee: 'crypto spring' still intact", "text": "Fundstrat's Tom Lee reaffirmed his bullish crypto outlook despite 6 weeks of BTC ETF outflows, citing corporate validator accumulation as the new driver.", "url": "https://www.coindesk.com/business/2026/06/22/bitmine-added-usd92-million-of-eth-with-tom-lee-continuing-to-believe-in-crypto-spring"},
        {"title": "SOL +1.5%, BNB +1.5% on Iran optimism", "text": "Altcoins outperformed BTC on Monday as oil fell. SOL is showing relative strength against ETH for the second consecutive week.", "url": "https://www.coindesk.com/markets/2026/06/22/bitcoin-holds-near-usd64-000-as-us-iran-talks-progress-but-crypto-sits-out-the-rally"},
    ],
}

# ── BLOCKCHAIN NEWS ───────────────────────────────────────────────────────────
BLOCKCHAIN_NEWS = {
    "date": TODAY,
    "indexHeadline": "Zama launches first confidential DeFi yield vault using homomorphic encryption on Ethereum",
    "indexSummary": "Zama, Morpho, and Steakhouse launched the first confidential DeFi yield vault on Ethereum, using fully homomorphic encryption (FHE) to hide balances and transfer amounts while preserving compliance. The Block Research's 2026 DeFi Outlook notes tokenised RWAs tripled to $16.7B in 2025, and perp DEXs hit all-time high volumes. Taiko L2 bridge was exploited for $1.7M. DefiLlama tracks Ethereum's ongoing DeFi TVL leadership.",
    "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
    "topSignal": [
        {"headline": "First confidential DeFi vault using FHE launches on Ethereum", "detail": "Zama's cUSDC hides balances and transfer amounts via fully homomorphic encryption. Morpho and Steakhouse are co-deployers. Deposits open. Represents a fundamental privacy breakthrough for on-chain finance."},
        {"headline": "Tokenised RWAs tripled to $16.7B — institutions now using blockchain at scale", "detail": "The Block Research 2026 DeFi Outlook: RWA tokenisation crossed from pilot to production in 2025. Institutional-grade DeFi is no longer theoretical."},
        {"headline": "Taiko L2 bridge exploit — $1.7M lost, network halted", "detail": "Bridge vulnerability exploited on June 22. Network halted pending investigation. Highlights bridge contracts as the persistent weakest link in L2 infrastructure."},
    ],
    "stories": [
        {
            "id": 1,
            "title": "Zama + Morpho + Steakhouse Launch First Confidential DeFi Yield Vault on Ethereum Using FHE",
            "category": "DEFI",
            "tags": ["defi", "tvl"],
            "priority": "MAJOR",
            "priorityLevel": 1,
            "sources": [
                {"name": "The Block — Zama, Morpho, Steakhouse confidential vault", "url": "https://www.theblock.co/amp/post/404992/zama-morpho-steakhouse-launch-first-confidential-defi-yield-vault-ethereum"},
                {"name": "Messari — Understanding Zama", "url": "https://messari.io/report/understanding-zama-a-comprehensive-overview"},
            ],
            "eventDate": "2026-06-23",
            "whatHappened": "Zama (a cryptography research firm specialising in fully homomorphic encryption), Morpho (Ethereum lending protocol), and Steakhouse Financial (DeFi strategy team) jointly launched the first confidential DeFi yield vault on Ethereum. The vault's key innovation is Zama's cUSDC token, which uses FHE to shield depositor balances and transfer amounts from public visibility on-chain — while preserving auditability and compliance checks. Deposits are now open. Zama's GPU-accelerated testnet has been live since June 2026, with mainnet integration targeting Q3 2026.",
            "whatItCanDo": [
                "Enable institutional and high-net-worth depositors to use Ethereum DeFi without exposing their balances to front-running or competitive intelligence",
                "Satisfy financial privacy requirements for regulated entities that currently cannot use transparent on-chain protocols",
                "Create a template for confidential DeFi across all asset classes — lending, DEXs, derivatives",
                "Demonstrate that FHE can run in production with acceptable performance using GPU acceleration",
            ],
            "whatsCatch": [
                "FHE is computationally expensive — vault fees and gas costs will be higher than standard DeFi vaults",
                "Complexity of FHE makes independent security auditing significantly harder than standard Solidity contracts",
                "Regulatory treatment of confidential DeFi is unclear — regulators may view transaction shielding as a compliance red flag",
                "cUSDC is not yet battle-tested at scale — FHE implementation bugs could have catastrophic consequences",
            ],
            "keyTakeaway": "The Zama-Morpho confidential vault is not an incremental improvement — it is a fundamental architectural shift that makes privacy-preserving DeFi practically deployable for the first time.",
            "howToImprove": "Zama should publish a full security audit from three independent firms before accepting significant deposits. FHE is powerful but novel — the audit bar should be correspondingly higher than standard DeFi protocols.",
            "vsPrevious": "First time covering Zama and FHE-based DeFi in this terminal.",
        },
        {
            "id": 2,
            "title": "Tokenised RWAs Tripled to $16.7B in 2025 — Institutions Now Use Blockchain at Scale",
            "category": "DEFI",
            "tags": ["tvl", "defi"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "The Block — 2026 DeFi Outlook", "url": "https://www.theblock.co/post/383120/2026-defi-outlook"},
                {"name": "DefiLlama — Protocol Revenue Rankings", "url": "https://defillama.com/revenue"},
            ],
            "eventDate": "2026-06-20",
            "whatHappened": "The Block Research's 2026 DeFi Outlook report identifies tokenised real-world assets (RWAs) as the defining theme of 2025: market cap of tokenised public-market RWAs tripled to $16.7 billion as institutions adopted blockchains for issuance and distribution. The report notes that tokenisation crossed from pilot programs to production deployment at scale. Major institutions involved include BlackRock (BUIDL fund), Franklin Templeton, and JPMorgan. Perp DEXs also set all-time highs in volume as execution quality improved.",
            "whatItCanDo": [
                "Bring traditional capital markets liquidity to DeFi rails — potentially unlocking trillions in institutional capital over the next decade",
                "Create new yield sources for DeFi protocols by bridging on-chain liquidity with off-chain asset returns",
                "Validate the thesis that public blockchain infrastructure is suitable for regulated financial instruments",
                "Drive demand for Ethereum block space and DeFi infrastructure that supports RWA protocols",
            ],
            "whatsCatch": [
                "$16.7B is still tiny relative to the $100T+ global capital markets — institutional DeFi is early-stage despite the tripling",
                "Most RWA tokenisation uses permissioned or semi-permissioned blockchain rails, not fully open DeFi",
                "Regulatory frameworks for tokenised RWAs vary dramatically across jurisdictions — cross-border use cases remain limited",
                "Custodian and oracle risk for off-chain assets is significant and not resolved by blockchain technology alone",
            ],
            "keyTakeaway": "The RWA tripling confirms institutional blockchain adoption is real and accelerating — but the infrastructure supporting it (oracles, custody, legal wrappers) needs to mature faster than the capital deployment.",
            "howToImprove": "DefiLlama should launch a dedicated RWA TVL dashboard breaking down assets by issuer, underlying asset class, and chain — current data is fragmented across multiple trackers and difficult to aggregate.",
            "vsPrevious": "First time covering RWA tokenisation trends in this terminal.",
        },
        {
            "id": 3,
            "title": "Taiko L2 Bridge Exploit — Network Halted After $1.7M Vulnerability",
            "category": "SECURITY",
            "tags": ["exploit", "bridge"],
            "priority": "SIGNIFICANT",
            "priorityLevel": 2,
            "sources": [
                {"name": "The Block — DeFi Security", "url": "https://www.theblock.co/category/defi"},
            ],
            "eventDate": "2026-06-22",
            "whatHappened": "Taiko's Ethereum Layer-2 network halted its bridge operations after an attacker exploited a vulnerability in the bridge smart contract, draining approximately $1.7 million. The Taiko team confirmed the halt and announced an investigation. Taiko uses a based rollup architecture that relies on Ethereum for sequencing, making the bridge the primary interaction surface between Ethereum and Taiko's L2. User funds locked in the bridge during the halt are temporarily inaccessible.",
            "whatItCanDo": [
                "Force a security audit of all Taiko bridge contracts before operations resume",
                "Highlight the need for formal verification of bridge contracts across the entire L2 ecosystem",
                "Trigger a broader review of based rollup bridge architecture across the Ethereum scaling ecosystem",
            ],
            "whatsCatch": [
                "Based rollup security does not guarantee bridge security — these are separate concerns that are often conflated",
                "No resumption timeline has been announced — prolonged halt would damage Taiko's ecosystem development timeline",
                "The exploit methodology has not been fully disclosed — other L2s may have similar vulnerabilities",
                "Bridge exploits have historically been the largest category of DeFi losses by volume (Ronin $625M, Wormhole $320M)",
            ],
            "keyTakeaway": "At $1.7M Taiko's exploit is small, but the pattern is old: bridge contracts are the most dangerous component of any L2 stack and deserve formal verification, not just auditing.",
            "howToImprove": "All L2 projects should implement a standardised bridge security framework with formal verification requirements. The Ethereum Foundation should fund this as a public good rather than leaving each team to independently solve the same problem.",
            "vsPrevious": "First time covering Taiko in this terminal.",
        },
        {
            "id": 4,
            "title": "Perp DEXs Hit All-Time High Volume in 2025-2026 — Prediction Markets Surge to $24B/Month",
            "category": "DEFI",
            "tags": ["defi", "tvl"],
            "priority": "NOTABLE",
            "priorityLevel": 3,
            "sources": [
                {"name": "The Block — 2026 DeFi Outlook", "url": "https://www.theblock.co/post/383120/2026-defi-outlook"},
                {"name": "DefiLlama", "url": "https://defillama.com/"},
            ],
            "eventDate": "2026-06-20",
            "whatHappened": "The Block Research's 2026 DeFi Outlook reports that perpetual DEXs (decentralised perpetual futures exchanges) set all-time high trading volumes through 2025-2026 as execution quality improved and incentive programs attracted traders from centralised exchanges. Separately, prediction market activity reignited in 2025 through broader distribution via crypto wallets and a wider range of event contracts, with combined monthly volume reaching $24 billion by April 2026. Polymarket dominates prediction market market share.",
            "whatItCanDo": [
                "Signal that DeFi derivatives are maturing into a credible alternative to CEX derivatives for active traders",
                "Create new revenue streams for DeFi protocols as volume grows and fee capture improves",
                "Embed prediction market functionality into everyday crypto wallets, reaching millions of users without requiring DApp visits",
                "Generate on-chain price discovery for real-world events that improves information efficiency in related markets",
            ],
            "whatsCatch": [
                "Perp DEX volumes are still dominated by incentive farming — sustainable organic volume is a fraction of reported totals",
                "Regulatory status of on-chain prediction markets remains uncertain globally — CFTC classification pending",
                "Liquidity on smaller prediction markets remains thin — large positions move prices significantly",
                "Perp DEX user experience still lags CEX for most traders — onboarding and UX friction remain barriers",
            ],
            "keyTakeaway": "DeFi derivatives are crossing from niche to infrastructure — perp DEXs and prediction markets together represent the most significant DeFi volume expansion since 2021 without the accompanying bubble dynamics.",
            "howToImprove": "DefiLlama and The Block should publish a standardised methodology for organic vs. incentivised perp DEX volume so investors can assess true adoption. Raw volume numbers without this distinction are misleading.",
            "vsPrevious": "First time covering perp DEX and prediction market volume trends in this terminal.",
        },
    ],
    "quickHits": [
        {"title": "Zama GPU testnet live — mainnet Q3 2026", "text": "Zama's FHE infrastructure reached GPU-accelerated testnet in June. Mainnet integration into Ethereum planned Q3 2026.", "url": "https://messari.io/report/understanding-zama-a-comprehensive-overview"},
        {"title": "DefiLlama: Ethereum DeFi TVL leads all chains", "text": "Ethereum maintains DeFi TVL leadership per DefiLlama. Protocol revenue rankings show Uniswap and Aave in top 5 by retained revenue.", "url": "https://defillama.com/revenue"},
        {"title": "a16z crypto: RWA infrastructure is the 2026 investment thesis", "text": "Andreessen Horowitz crypto fund publicly backing RWA infrastructure plays — oracles, custody bridges, and legal wrapper protocols.", "url": "https://a16zcrypto.com/"},
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  RUN ALL
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  LIM-AI TERMINAL  —  Daily Brief  —  {TODAY}")
    print(f"{'='*60}")

    run("global-fin-news", GLOBAL_FIN)
    run("global-news",     GLOBAL_NEWS)
    run("indo-fin-news",   INDO_FIN)
    run("indo-news",       INDO_NEWS)
    run("crypto-news",     CRYPTO_NEWS)
    run("blockchain-news", BLOCKCHAIN_NEWS)

    print(f"\n{'='*60}")
    print("  All briefs written. Commit and push to deploy.")
    print(f"{'='*60}\n")
