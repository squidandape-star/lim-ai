#!/usr/bin/env python3
"""One-time initialisation script — writes June 22 2026 briefs for all 7 features."""

import json, shutil, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TODAY = "2026-06-22"

# ═══════════════════════════════════════════════════════════════
#  BRIEF DATA
# ═══════════════════════════════════════════════════════════════

BRIEFS = {

# ───────────────────────────────────────────────────────────────
"ai-news": {
  "date": "2026-06-22",
  "indexHeadline": "Anthropic files for IPO at $965B valuation; DeepSeek V4 challenges frontier models",
  "indexSummary": "Anthropic confidentially filed for an IPO days after closing a $65B Series H at a $965B valuation, overtaking OpenAI. DeepSeek V4 — a 1.6T parameter MoE model — launches as a frontier-class Chinese competitor. Microsoft Copilot Wave 3 embeds Claude natively. GitHub Copilot drops unlimited plans for metered billing.",
  "stats": {"total": 5, "major": 1, "significant": 3, "notable": 1},
  "topSignal": [
    {"headline": "Anthropic IPO at near-$1T valuation", "detail": "Confidential S-1 filed after $65B Series H. If listed at $965B, Anthropic would be the most valuable AI company on public markets, ahead of OpenAI's private $300B valuation."},
    {"headline": "DeepSeek V4: 1.6T parameter Chinese frontier model", "detail": "MoE architecture targets GPT-5.x / Claude 5.x class tasks. Fully open weights. Chinese government backing implied. Direct challenge to US AI export controls."},
    {"headline": "GitHub Copilot ends unlimited subscriptions", "detail": "Usage-based metered billing at $0.01/AI credit effective June 1. Complex agentic coding sessions made flat-fee model unsustainable for Microsoft."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "Anthropic Files Confidential IPO at $965B Valuation",
      "category": "BUSINESS",
      "tags": ["ipo", "funding"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "Bloomberg", "url": "https://www.bloomberg.com/graphics/2026-investment-outlooks/"},
        {"name": "The Rundown AI", "url": "https://www.therundown.ai/p/google-s-nobel-winner-jumps-to-anthropic"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "Anthropic submitted a confidential draft registration statement with the SEC, initiating its IPO process. The filing comes days after closing a $65 billion Series H funding round that valued the company at $965 billion — surpassing rival OpenAI's last private valuation of $300 billion. No listing date or pricing range has been disclosed. Anthropic is backed by Google, Amazon, and Spark Capital.",
      "whatItCanDo": [
        "Gives Anthropic access to public capital markets for the first time, enabling larger infrastructure bets",
        "Forces competitors like OpenAI to accelerate their own IPO timelines or risk losing talent to Anthropic's liquidity",
        "Sets a public benchmark for AI company valuations — $965B implies the market prices AI differently than any prior tech wave",
        "Provides a potential exit for early investors including Dustin Moskovitz and Center for Emerging Risk Research"
      ],
      "whatsCatch": [
        "At $965B, Anthropic would be priced for perfection — any revenue miss post-IPO could trigger a sharp correction",
        "Regulatory scrutiny is intensifying: the Fable 5 / Mythos 5 export control ban adds political risk to any public listing",
        "Anthropic has not yet disclosed revenue or path to profitability; inference costs remain enormous",
        "IPO markets remain choppy in 2026 — Fed hawkishness raises discount rates for high-growth unprofitable companies"
      ],
      "keyTakeaway": "Anthropic's near-$1T IPO would be the defining public markets event for AI in 2026 — and a stress test of whether Wall Street values AI capability or AI profitability.",
      "howToImprove": "Watch for the S-1 to become public: revenue figures, gross margin on API inference, and burn rate will determine whether the valuation holds. A disclosed timeline before Q4 2026 would signal confidence.",
      "vsPrevious": "Previously covered OpenAI's IPO filing targeting $1T (2026-06-21). Anthropic's filing, at a lower absolute target but higher implied valuation multiple, now makes two of the three frontier labs publicly filing within 48 hours."
    },
    {
      "id": 2,
      "title": "Anthropic Secures 220,000 GPU Compute Cluster via SpaceX Colossus Deal",
      "category": "BUSINESS",
      "tags": ["compute", "infrastructure"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/01/microsoft-and-google-take-on-anthropic-and-openai-in-ai-coding-models.html"},
        {"name": "LLM Stats", "url": "https://llm-stats.com/llm-updates"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "Anthropic signed an agreement granting it exclusive access to all compute capacity at SpaceX and xAI's Colossus 1 data center in Memphis, Tennessee — over 300 megawatts powered by more than 220,000 Nvidia GPUs. The deal gives Anthropic the largest single-tenant GPU cluster of any AI lab outside of internal hyperscaler deployments.",
      "whatItCanDo": [
        "Enables Anthropic to train successor models to Fable 5 without relying on Microsoft Azure or Google Cloud",
        "Reduces Anthropic's dependency on Google and Amazon — its current primary compute providers and investors",
        "300MW of capacity is sufficient to train a frontier model in weeks rather than months at current GPU efficiency",
        "Positions Anthropic to deliver on the IPO promise of compute self-sufficiency"
      ],
      "whatsCatch": [
        "Colossus is partially owned by xAI (Elon Musk's AI company), creating a strategic conflict: Anthropic funding a competitor's infrastructure",
        "300MW is still below what Google and Microsoft can deploy internally for their own models",
        "Exclusivity terms and duration of the deal have not been disclosed",
        "Power availability in Tennessee may constrain expansion beyond current capacity"
      ],
      "keyTakeaway": "Anthropic is building compute independence ahead of its IPO — the Colossus deal signals it no longer wants to be infrastructure-dependent on investor-competitors Google and Amazon.",
      "howToImprove": "Anthropic should disclose the financial terms and duration of the Colossus deal in its S-1 — compute costs are the largest line item for any frontier lab and investors will demand clarity.",
      "vsPrevious": "First time covering Anthropic's compute strategy. Previous coverage focused on model policy (Fable 5 export ban). This shifts the narrative to infrastructure competition."
    },
    {
      "id": 3,
      "title": "DeepSeek V4 Launches: 1.6 Trillion Parameter Open Frontier Model",
      "category": "MODEL",
      "tags": ["open-source", "reasoning", "coding"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "AI Flash Report", "url": "https://aiflashreport.com/topics/new-ai-model-releases.html"},
        {"name": "LLM Stats", "url": "https://llm-stats.com/ai-news"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "DeepSeek released V4, a 1.6 trillion-parameter mixture-of-experts model targeted at frontier-class reasoning and coding tasks. The model is fully open-weight and released under a permissive licence. DeepSeek positions V4 as a direct competitor to GPT-5.x and Claude 5.x class systems. It is the largest openly released model to date and implies significant Chinese state compute investment.",
      "whatItCanDo": [
        "Run complex multi-step reasoning tasks at a scale previously only available via closed APIs",
        "Be fine-tuned or deployed on-premise by any organisation with sufficient GPU capacity",
        "Undercut US closed-model pricing by enabling zero-API-cost inference for large enterprises",
        "Provide a sovereign AI alternative for governments unwilling to depend on US frontier labs"
      ],
      "whatsCatch": [
        "1.6T parameters requires significant infrastructure — not practical for most users without cloud deployment",
        "Chinese model alignment and safety practices are not independently audited",
        "US export controls on advanced chips may limit DeepSeek's ability to train successor models",
        "Open weights mean misuse potential is high — no usage-based enforcement possible"
      ],
      "keyTakeaway": "DeepSeek V4 is the strongest open-weight challenge to US closed frontier models to date, and its release directly undermines the strategic logic of US AI export controls.",
      "howToImprove": "Independent benchmarking against Claude Mythos 1 and GPT-5 on standardised evals (MMLU, AIME, SWE-bench) needed to confirm competitive positioning. DeepSeek's self-reported scores should be verified.",
      "vsPrevious": "First time covering DeepSeek V4 specifically. Previously covered GLM-5.2 (2026-06-21 brief) as another Chinese model. V4 is a qualitative step up in scale and ambition."
    },
    {
      "id": 4,
      "title": "Microsoft Copilot Wave 3 Integrates Claude Natively Across Microsoft 365",
      "category": "PRODUCT",
      "tags": ["agents", "multimodal", "coding"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/01/microsoft-and-google-take-on-anthropic-and-openai-in-ai-coding-models.html"},
        {"name": "Microsoft AI", "url": "https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "Microsoft announced Wave 3 of Microsoft 365 Copilot featuring multi-model support that includes native integration of Anthropic's Claude alongside OpenAI models. The update also introduces Copilot Cowork — an agentic collaboration mode — and general availability of Agent 365. A new tier, Microsoft 365 E7: The Frontier Suite, bundles all agentic capabilities for enterprise.",
      "whatItCanDo": [
        "Allow enterprise users to switch between Claude and GPT models within the same M365 workflow",
        "Run autonomous multi-step tasks via Agent 365 across email, calendar, Teams, and SharePoint",
        "Enable Copilot Cowork to handle long-running background tasks without user supervision",
        "Give Microsoft enterprise customers access to Claude's coding and reasoning strengths within familiar Office tools"
      ],
      "whatsCatch": [
        "Multi-model support adds billing complexity — enterprises must manage costs across two API providers",
        "Agent 365 autonomous actions raise data governance concerns in regulated industries",
        "The E7 Frontier Suite tier pricing has not been publicly disclosed",
        "Anthropic's export-control-restricted models (Fable 5, Mythos 5) are not part of the Copilot offering"
      ],
      "keyTakeaway": "Microsoft embedding Claude into M365 is the largest enterprise distribution deal for Anthropic — reaching 400M+ commercial Office users without them needing to visit claude.ai.",
      "howToImprove": "Microsoft should publish a model selection framework so IT admins understand which tasks route to which model and why — opacity here will slow enterprise adoption in compliance-heavy sectors.",
      "vsPrevious": "First time covering Microsoft's multi-model Copilot strategy. Previously covered Microsoft's independent AI model releases (early June). The Claude integration marks a shift from competition to co-distribution."
    },
    {
      "id": 5,
      "title": "GitHub Copilot Ends Unlimited Plans, Switches to Metered AI Credits",
      "category": "PRODUCT",
      "tags": ["coding", "agents"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "GitHub Blog", "url": "https://releasebot.io/updates/openai"},
        {"name": "n8n Blog", "url": "https://blog.n8n.io/we-need-re-learn-what-ai-agent-development-tools-are-in-2026/"}
      ],
      "eventDate": "2026-06-01",
      "whatHappened": "GitHub Copilot shifted from unlimited subscription billing to a usage-based metered system on June 1, 2026. Developers are now billed via GitHub AI Credits at $0.01 each. Microsoft cited escalating inference costs driven by complex agentic coding sessions as the reason — the previous flat-fee model was no longer financially viable at the scale of usage that agentic AI generates.",
      "whatItCanDo": [
        "Align cost with actual compute consumption — light users pay less, heavy agentic users pay more",
        "Enable GitHub to offer more powerful future models without subsidising high-compute users via flat fees",
        "Give teams granular visibility into AI spend per developer, per project"
      ],
      "whatsCatch": [
        "Developers running complex agentic tasks could see costs jump dramatically vs. the old unlimited plan",
        "Unpredictable billing makes budgeting harder for individual developers and small teams",
        "Competitors like Cursor and Windsurf still offer flat-fee plans — GitHub risks losing price-sensitive users"
      ],
      "keyTakeaway": "GitHub's billing shift confirms that agentic AI has fundamentally broken the economics of flat-fee AI subscriptions — every provider will eventually move to consumption-based pricing.",
      "howToImprove": "GitHub should publish a credit consumption calculator showing typical costs for common workflows (PR review, test generation, full-repo refactor) so developers can budget accurately before committing.",
      "vsPrevious": "First time covering GitHub Copilot billing. Consistent with broader trend of AI providers moving away from unlimited tiers as agentic compute costs scale."
    }
  ],
  "quickHits": [
    {"title": "Gemini 3.5 Flash GA", "text": "Google's first Gemini 3.5 model is now generally available. Optimised for complex agentic and coding workflows. Positioned below Gemini 3.5 Pro in capability.", "url": "https://aiweekly.co/ai-news-today/google-ai-news"},
    {"title": "Grok 4.3 on AWS Bedrock", "text": "xAI's Grok 4.3 is now available via Amazon Bedrock, extending its enterprise reach beyond X Premium subscriptions.", "url": "https://llm-stats.com/llm-updates"},
    {"title": "NVIDIA + ServiceNow Project Arc", "text": "Long-running self-evolving desktop agent for knowledge workers. Part of expanded NVIDIA-ServiceNow enterprise AI partnership.", "url": "https://aiflashreport.com/topics/new-ai-model-releases.html"},
    {"title": "Alteryx Agent Studio", "text": "Business analysts can now convert existing data workflows into autonomous agents without IT involvement. Launched at Inspire 2026.", "url": "https://aiflashreport.com/topics/new-ai-model-releases.html"},
    {"title": "Claude Mythos 1 launched", "text": "Anthropic's replacement for the export-banned Mythos 5. Capabilities not yet benchmarked publicly. Available to existing API customers.", "url": "https://llm-stats.com/ai-news"}
  ]
},

# ───────────────────────────────────────────────────────────────
"global-fin-news": {
  "date": "2026-06-22",
  "indexHeadline": "Fed holds but turns hawkish; Treasury yields spike to 1-year high as markets sell off",
  "indexSummary": "The Federal Reserve kept rates at 3.50-3.75% but Chair Kevin Warsh signalled possible tightening, sending 2-year Treasury yields to their highest in over a year. Nine of 18 Fed officials now pencil in a hike. PCE inflation upgraded to 3.6%. China property investment fell 16.2% YoY. Bank of England held at 3.75%. Germany's ZEW sentiment turned positive for first time since Middle East war began.",
  "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
  "topSignal": [
    {"headline": "Fed hawkish pivot triggers bond and equity selloff", "detail": "9 of 18 FOMC members now expect a rate hike in 2026. 2-year Treasury yield hit highest in over 12 months. S&P 500 sold off on Wednesday after press conference."},
    {"headline": "PCE inflation forecast raised to 3.6%", "detail": "Fed's updated SEP raised headline PCE to 3.6% and core PCE to 3.3% for 2026 — well above the 2% target. Stagflation risk is now the dominant macro narrative."},
    {"headline": "China property investment -16.2% YoY", "detail": "Worst reading in 2026. New-home prices declining at accelerating pace in May. Property crisis continues to drag on Chinese domestic demand and global commodity prices."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "Fed Holds at 3.50-3.75% but Turns Hawkish — 9 Officials Now Expect Hike",
      "category": "CENTRAL-BANK",
      "tags": ["rate-hike", "inflation", "fed"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "Charles Schwab", "url": "https://www.schwab.com/learn/story/stock-market-update-open"},
        {"name": "J.P. Morgan", "url": "https://www.jpmorgan.com/insights/global-research/outlook/market-outlook"}
      ],
      "eventDate": "2026-06-18",
      "whatHappened": "The Federal Reserve left its federal funds rate target unchanged at 3.50%-3.75% at its June meeting. However, Chair Kevin Warsh's first post-meeting press conference was widely interpreted as hawkish. The updated Summary of Economic Projections showed nine of 18 officials pencilling in at least one rate hike in 2026, while only one projected a cut. The Fed raised its headline PCE inflation forecast to 3.6% and core PCE to 3.3% for 2026.",
      "whatItCanDo": [
        "Raise borrowing costs for businesses and consumers if the Fed follows through with a hike in Q3 or Q4 2026",
        "Strengthen the US dollar, putting pressure on emerging market currencies including the Indonesian rupiah",
        "Extend the pain for rate-sensitive sectors: real estate, utilities, small-cap growth stocks",
        "Increase the cost of US government debt service, adding pressure to an already strained fiscal position"
      ],
      "whatsCatch": [
        "The Fed has signalled hikes before without delivering them — market credibility is at stake if inflation moderates",
        "A hike could tip a slowing economy into recession, which Warsh acknowledged as a tail risk",
        "Political pressure from the White House to cut rather than hike is intensifying",
        "Global central bank divergence (BOE, ECB holding) complicates the Fed's ability to tighten without triggering dollar dislocation"
      ],
      "keyTakeaway": "The Fed's hawkish pivot marks the end of the 'hold and wait' posture — markets must now price a genuine probability of a rate increase before year-end.",
      "howToImprove": "Watch the July FOMC meeting and the June CPI print due July 10. If core CPI stays above 3.2%, a September hike becomes the base case.",
      "vsPrevious": "First time covering the June 2026 FOMC decision in this terminal. Prior macro coverage noted the Fed's patient stance — today's pivot is a material shift."
    },
    {
      "id": 2,
      "title": "2-Year Treasury Yield Hits 12-Month High After Fed Selloff",
      "category": "MARKETS",
      "tags": ["bonds", "yields", "treasuries"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "T. Rowe Price", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"},
        {"name": "BlackRock", "url": "https://www.blackrock.com/us/individual/insights/blackrock-investment-institute/weekly-commentary"}
      ],
      "eventDate": "2026-06-18",
      "whatHappened": "U.S. Treasuries generated negative returns across the week, with short-term yields rising sharply following Wednesday's FOMC decision. The yield on the 2-year U.S. Treasury note hit its highest level in over a year, reflecting the market's reassessment of the Fed's rate path. The sell-off spread to equities, with growth and rate-sensitive stocks leading declines.",
      "whatItCanDo": [
        "Increase the attractiveness of cash and short-duration bonds relative to equities — portfolio reallocation risk",
        "Widen credit spreads as risk-free yields rise, increasing financing costs for corporate issuers",
        "Signal to mortgage markets that 30-year rates may move higher, further dampening housing activity",
        "Attract foreign capital into US Treasuries, supporting the dollar at the expense of EM currencies"
      ],
      "whatsCatch": [
        "High yields are contractionary — if sustained, they will slow economic activity faster than the Fed intends",
        "The US government's interest expense on $36T+ in debt rises with every basis point increase",
        "Inverse correlation with equities may break if stagflation becomes the dominant regime",
        "Japan's YCC policy exit creates competing global bond supply that may cap the yield rise"
      ],
      "keyTakeaway": "The bond market is pricing in a Fed that will hike — and until inflation data proves otherwise, Treasury yields will remain under upward pressure.",
      "howToImprove": "Track the 10-year/2-year spread: if it inverts further, recession probability rises materially. The spread is currently near flat.",
      "vsPrevious": "First time covering US Treasury yields in this terminal."
    },
    {
      "id": 3,
      "title": "China Property Investment Falls 16.2% YoY — Crisis Deepens in May",
      "category": "MACRO",
      "tags": ["china", "recession", "commodities"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "Bloomberg", "url": "https://www.bloomberg.com/graphics/2026-investment-outlooks/"},
        {"name": "J.P. Morgan", "url": "https://www.jpmorgan.com/insights/global-research/outlook/market-outlook"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "China reported that property investment fell 16.2% year-over-year in the first five months of 2026, the steepest decline since the crisis began in 2021. National new-home prices declined at a faster pace in May than April, with no major cities showing improvement. The property sector, which historically accounted for ~25% of Chinese GDP, continues to drag on domestic consumption and industrial activity.",
      "whatItCanDo": [
        "Further depress Chinese demand for steel, copper, and cement — bearish signal for commodity exporters including Indonesia and Australia",
        "Push Chinese policymakers toward additional fiscal stimulus or property market support measures",
        "Increase non-performing loans on Chinese bank balance sheets, raising systemic financial risk",
        "Reduce Chinese consumer confidence and retail spending, slowing the broader Asian growth engine"
      ],
      "whatsCatch": [
        "Chinese government property rescue packages have repeatedly failed to arrest the decline",
        "A forced restructuring of major developers (Evergrande successors) could create short-term financial shock",
        "Demographic decline means structural demand for new housing may not recover even with stimulus",
        "Capital controls limit China's ability to attract foreign investment to recapitalise the sector"
      ],
      "keyTakeaway": "China's property crisis is not a cycle — it is a structural deflation in the sector that will constrain Chinese growth for the remainder of the decade.",
      "howToImprove": "Watch PBOC's response: if they cut the 5-year LPR (loan prime rate) before end of June, it signals urgency. A cut paired with fiscal support is the minimum needed to stabilise sentiment.",
      "vsPrevious": "First time covering China property data in this terminal."
    },
    {
      "id": 4,
      "title": "Germany ZEW Sentiment Turns Positive for First Time Since Middle East War",
      "category": "MACRO",
      "tags": ["europe", "sentiment", "geopolitics"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "T. Rowe Price", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"}
      ],
      "eventDate": "2026-06-17",
      "whatHappened": "Germany's ZEW Indicator of Economic Sentiment rose sharply in June 2026 to its first positive reading since the start of the Middle East war, which disrupted energy supplies and European trade routes. The improvement reflects optimism around the ongoing US-Iran ceasefire talks and declining European natural gas prices. The Bank of England also held its base rate steady at 3.75%.",
      "whatItCanDo": [
        "Signal a potential cyclical recovery in European industrial output if energy costs stabilise",
        "Support DAX and European equity markets, which have lagged US peers throughout 2026",
        "Reduce pressure on the ECB to cut rates early — if Germany recovers, rate cuts become less urgent"
      ],
      "whatsCatch": [
        "ZEW measures expectations, not actual activity — Germany's industrial output data remains weak",
        "A collapse in US-Iran talks would reverse the energy price improvement instantly",
        "Germany's structural competitiveness issues (energy costs, labour costs, export dependence on China) are unresolved"
      ],
      "keyTakeaway": "Germany's sentiment recovery is real but fragile — entirely dependent on Middle East de-escalation that remains reversible.",
      "howToImprove": "Track the July IFO Business Climate survey for confirmation. ZEW leads IFO by 1-2 months; a matching IFO recovery would confirm genuine turning point.",
      "vsPrevious": "First time covering German economic sentiment in this terminal."
    }
  ],
  "quickHits": [
    {"title": "Bank of England holds at 3.75%", "text": "BOE kept its base rate steady, citing persistent services inflation and watching US Fed for global cues.", "url": "https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html"},
    {"title": "IHSG recovers +4.1% off June lows", "text": "Jakarta Composite bounced to 6,254 after Bank Indonesia rate hikes stabilised the rupiah.", "url": "https://tradingeconomics.com/indonesia/stock-market"},
    {"title": "US-Iran talks positive — oil falls 3%", "text": "Brent crude dropped on ceasefire optimism, easing pressure on global inflation prints.", "url": "https://www.schwab.com/learn/story/stock-market-update-open"}
  ]
},

# ───────────────────────────────────────────────────────────────
"global-news": {
  "date": "2026-06-22",
  "indexHeadline": "US-Iran talks nearly collapse then resume; de-confliction cell formed for Lebanon",
  "indexSummary": "Iran initially refused to continue nuclear talks after Trump's public threats but resumed after Qatar-Pakistan mediation. A US-Iran de-confliction cell was established for Lebanon. A Strait of Hormuz communication line was set up to protect energy shipping. Ukraine escalated attacks on Russian fuel infrastructure in Crimea. FIFA World Cup continues.",
  "stats": {"total": 4, "major": 2, "significant": 1, "notable": 1},
  "topSignal": [
    {"headline": "US-Iran talks survive near-collapse, resume in Qatar", "detail": "Iran suspended talks after Trump's media threats but returned after Qatar and Pakistan mediation. Talks described as 'positive and constructive.' No deal yet — next round unscheduled."},
    {"headline": "Lebanon de-confliction cell: US and Iran in direct coordination", "detail": "First formal US-Iran military coordination mechanism since 1979. Facilitated by Qatar and Pakistan. Designed to prevent accidental escalation as Israeli-Hezbollah conflict continues despite ceasefire."},
    {"headline": "Strait of Hormuz communication line established", "detail": "Direct line between US and Iranian naval command to ensure safe passage. Approximately 20% of global oil transit flows through the Strait. A closure would cause immediate global energy shock."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "US-Iran Nuclear Talks Survive Near-Collapse After Trump Threats",
      "category": "DIPLOMACY",
      "tags": ["iran", "nuclear", "sanctions"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/21/world/live-news/iran-war-trump-israel-lebanon"},
        {"name": "WEF", "url": "https://www.weforum.org/stories/2026/06/uncertainty-around-us-iran-ceasefire-and-other-geopolitical-stories-to-know-this-month/"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "A fresh round of US-Iran nuclear and sanctions talks in Qatar was nearly derailed when Iran suspended participation after President Trump made threatening statements in a media interview. Following Qatar and Pakistan mediation, Iran returned to the table. Both sides described the resumed talks as conducted in a 'positive and constructive atmosphere.' No agreement has been reached and the next round has not been scheduled.",
      "whatItCanDo": [
        "A deal could unlock Iranian oil exports — potentially adding 1-1.5 million barrels per day to global supply",
        "Sanctions relief would allow Iran to access ~$100B in frozen assets, boosting its economy and military capacity",
        "Reduce Strait of Hormuz risk premium currently embedded in global oil prices",
        "Ease pressure on European energy markets still recovering from Middle East war disruptions"
      ],
      "whatsCatch": [
        "Trump's public threats nearly ended talks — his unpredictability is the single largest risk to any deal",
        "Iran's Supreme Leader Khamenei must approve any agreement, and his position remains hardline on enrichment",
        "Israel has stated it will take unilateral military action if it believes Iran is approaching weapons-grade enrichment",
        "US Congressional opposition to any Iran deal is significant — ratification risk is high"
      ],
      "keyTakeaway": "The talks are alive but fragile — one more Trump media statement or Israeli military action could collapse them permanently.",
      "howToImprove": "Watch for a scheduled next round: if one is announced within 72 hours, it signals genuine momentum. If no next round is confirmed by June 25, the talks are likely suspended.",
      "vsPrevious": "First time covering the 2026 US-Iran talks in this terminal."
    },
    {
      "id": 2,
      "title": "US-Iran Form Lebanon De-Confliction Cell — First Direct Military Coordination Since 1979",
      "category": "CONFLICT",
      "tags": ["lebanon", "iran", "nato"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/21/world/live-news/iran-war-trump-israel-lebanon"},
        {"name": "ZeroFox", "url": "https://www.zerofox.com/intelligence/monthly-geopolitical-report-june-2026/"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "The US and Iran agreed to establish a 'de-confliction cell' specifically for Lebanon, facilitated by Qatar and Pakistan. The cell is designed to coordinate on preventing accidental military escalation as the Israel-Hezbollah conflict continues despite a renewed ceasefire agreement. This is the first formal military communication mechanism between Washington and Tehran since the 1979 Islamic Revolution.",
      "whatItCanDo": [
        "Reduce the risk of accidental military exchange between US-backed Israeli forces and Iran-backed Hezbollah",
        "Create a precedent for US-Iran direct communication that could extend to other flashpoints",
        "Give Qatar and Pakistan greater geopolitical leverage as trusted mediators in a major conflict zone",
        "Provide a back-channel to communicate red lines without requiring public diplomatic statements"
      ],
      "whatsCatch": [
        "A 'de-confliction cell' is not a ceasefire — active hostilities continue on the ground in Lebanon",
        "Hezbollah does not formally report to Tehran command — Iranian influence has limits",
        "Israel was not party to this agreement and may view it as undermining its freedom of action",
        "The mechanism could collapse if either side uses the channel to deliver ultimatums rather than coordinate"
      ],
      "keyTakeaway": "The US-Iran de-confliction cell is the most significant direct military coordination between the two countries in 47 years — a structural breakthrough even if tactical fighting continues.",
      "howToImprove": "The cell needs a third-party observer (UN or Swiss) to document communications and prevent disputes about what was agreed. Track whether fighting intensity in Lebanon measurably decreases in the next 2 weeks.",
      "vsPrevious": "First time covering Lebanon de-confliction in this terminal. Previously noted the Israel-Hezbollah conflict as ongoing background context."
    },
    {
      "id": 3,
      "title": "Strait of Hormuz Communication Line Established to Protect Oil Shipping",
      "category": "DIPLOMACY",
      "tags": ["iran", "energy", "shipping"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "WEF", "url": "https://www.weforum.org/stories/2026/06/uncertainty-around-us-iran-ceasefire-and-other-geopolitical-stories-to-know-this-month/"},
        {"name": "CFR", "url": "https://www.cfr.org/reports/conflicts-watch-2026"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "The US and Iran established a direct naval communication line aimed at ensuring 'safe passage' through the Strait of Hormuz. The announcement follows months of disruption to global energy supplies caused by the ongoing Middle East conflict. Approximately 20% of global oil and 25% of global LNG transit the Strait daily — any closure would trigger an immediate global energy crisis.",
      "whatItCanDo": [
        "Reduce the war risk premium embedded in Brent crude and global LNG prices",
        "Provide insurance for shipping companies currently charging elevated war risk surcharges on Hormuz routes",
        "Signal to global energy markets that both the US and Iran want to avoid a full Strait closure",
        "Lower input costs for Asian economies (China, Japan, South Korea, India) heavily dependent on Gulf oil"
      ],
      "whatsCatch": [
        "A communication line does not prevent Iranian seizure of tankers — it only provides a channel to protest",
        "Iran's Revolutionary Guard Corps operates semi-independently and has historically acted without Tehran's approval",
        "US naval presence in the Gulf is at a multi-year high, increasing the risk of miscalculation",
        "Insurance premiums for Hormuz passage remain elevated despite the announcement"
      ],
      "keyTakeaway": "The Hormuz communication line is a stabilising signal, but the Strait remains a live flashpoint as long as the broader US-Iran conflict is unresolved.",
      "howToImprove": "Watch tanker insurance rates as a real-time signal: if war risk premiums fall more than 20% this week, the market believes the line is credible. Currently rates remain elevated.",
      "vsPrevious": "First time covering Strait of Hormuz shipping risk in this terminal."
    },
    {
      "id": 4,
      "title": "Ukraine Escalates Attacks on Russian Fuel Infrastructure in Crimea",
      "category": "CONFLICT",
      "tags": ["ukraine", "russia", "energy"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "Deutsche Bank Research", "url": "https://www.dbresearch.com/PROD/IE-PROD/PROD0000000000629523/This_Month_in_Geopolitics:_June_2026.pdf"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "Officials in Russian-occupied Crimea suspended civilian gasoline sales as Ukraine ramped up drone and missile attacks targeting fuel supply infrastructure on the peninsula. The attacks are part of Ukraine's sustained campaign to degrade Russian military logistics, particularly fuel supply chains for operations in southern Ukraine.",
      "whatItCanDo": [
        "Disrupt Russian military operations in southern Ukraine by constraining fuel availability for armoured vehicles",
        "Force Russia to divert air defence assets to protect Crimean infrastructure, reducing cover elsewhere on the front",
        "Raise civilian pressure on Russian occupation administration in Crimea"
      ],
      "whatsCatch": [
        "Ukraine has been targeting Crimean fuel infrastructure since 2023 with mixed long-term results",
        "Russia has demonstrated capacity to repair infrastructure and reroute supplies within days",
        "Civilian gasoline shortages in Crimea may increase local resentment but are unlikely to trigger political change",
        "Escalation risk: Russia may respond with strikes on Ukrainian energy infrastructure"
      ],
      "keyTakeaway": "Ukraine's Crimea fuel campaign is tactically disruptive but strategically inconclusive — the front line has not materially shifted since Q1 2026.",
      "howToImprove": "Track front-line movement in the Zaporizhzhia-Kherson corridor over the next 2 weeks as the operational indicator of whether the fuel disruption is having strategic effect.",
      "vsPrevious": "First time covering Ukraine-Crimea operations in this terminal."
    }
  ],
  "quickHits": [
    {"title": "FIFA World Cup surprises continue", "text": "2026 World Cup sees upsets from debut nations. Morocco and Japan both through to quarterfinals. USA faces Brazil in Round of 16.", "url": "https://www.cnn.com/2026/06/21/world/live-news/iran-war-trump-israel-lebanon"},
    {"title": "WEF Global Risks 2026 report flags geopolitical and AI risk", "text": "Annual report highlights AI-enabled disinformation and geopolitical fragmentation as top systemic risks for 2026.", "url": "https://www.weforum.org/press/2026/01/global-risks-report-2026-geopolitical-and-economic-risks-rise-in-new-age-of-competition/"},
    {"title": "Qatar-Pakistan emerge as key Middle East mediators", "text": "Both nations now central to US-Iran communications and Lebanon de-confliction. Significant diplomatic capital gain for both.", "url": "https://www.weforum.org/stories/2026/06/uncertainty-around-us-iran-ceasefire-and-other-geopolitical-stories-to-know-this-month/"}
  ]
},

# ───────────────────────────────────────────────────────────────
"indo-fin-news": {
  "date": "2026-06-22",
  "indexHeadline": "MSCI threatens Indonesia frontier downgrade; IHSG recovers as BI hikes 100bps to defend rupiah",
  "indexSummary": "MSCI warned it may reclassify Indonesia as a frontier market due to weak shareholding visibility and signs of coordinated trading — a potential downgrade that would accelerate fund outflows. Bank Indonesia has hiked rates a cumulative 100bps since May to stabilise the rupiah at 17,870/USD. IHSG has recovered +16.4% from its June 8 low of 5,342 to 6,254. Q1 2026 GDP grew 5.61%.",
  "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
  "topSignal": [
    {"headline": "MSCI may downgrade Indonesia to frontier market", "detail": "Warning issued days before MSCI's reclassification decision. Frontier downgrade from emerging market status would force passive funds tracking EM indices to sell Indonesian equities — potentially billions in outflows."},
    {"headline": "Bank Indonesia cumulative 100bps hike since May", "detail": "Aggressive tightening to defend the rupiah and stem capital flight. Rupiah currently at 17,870/USD. BI prioritising currency stability over growth support."},
    {"headline": "IHSG +16.4% recovery from June 8 low", "detail": "Market recovered from 5,342 to 6,254 in two weeks. Driven by BI rate hikes stabilising rupiah, commodity price relief, and EM risk premium compression. But MSCI threat could reverse gains."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "MSCI Warns Indonesia Faces Frontier Market Downgrade — Billions in Forced Outflows at Risk",
      "category": "IDX",
      "tags": ["msci", "foreign-flows", "ihsg"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "Databoks Katadata", "url": "https://databoks.katadata.co.id/en/market/statistics/6a33c8de9cce1/ihsg-fell-after-the-bank-indonesia-raised-interest-rates-thursday-june-18-2026"},
        {"name": "IDX Tracker", "url": "https://www.idxtracker.com/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "MSCI issued a formal warning that it is reviewing Indonesia's emerging market status, citing weak visibility in shareholdings and signs of coordinated trading on the IDX. The review comes days before MSCI's scheduled annual market classification decision. A downgrade from emerging market to frontier market status would force all passive funds tracking the MSCI Emerging Markets Index to sell Indonesian equities — estimated potential outflows of USD 2-4 billion based on Indonesia's current EM index weight.",
      "whatItCanDo": [
        "Force billions in passive fund outflows from Indonesian equities if downgrade is confirmed",
        "Push the rupiah sharply weaker as foreign investors repatriate capital",
        "Increase Indonesia's cost of sovereign borrowing as risk perception rises",
        "Accelerate OJK and IDX reforms to address shareholding transparency and market manipulation concerns"
      ],
      "whatsCatch": [
        "MSCI has issued similar warnings to other markets without following through — the threat itself causes market damage",
        "Indonesia's IDX has made some governance improvements but coordinated trading is structurally difficult to eliminate",
        "A downgrade would take effect over multiple rebalancing periods, giving some time to mitigate outflows",
        "Political pressure on IDX to prevent downgrade may lead to cosmetic rather than structural reforms"
      ],
      "keyTakeaway": "An MSCI frontier downgrade would be the most damaging single external market event for Indonesian equities since the 2013 taper tantrum — and the decision may come within days.",
      "howToImprove": "IDX must immediately publish enhanced shareholding disclosure and demonstrate automated market surveillance. OJK should fast-track the Foreign Investor Registration reform that has been pending since 2024.",
      "vsPrevious": "First time covering MSCI classification risk for Indonesia in this terminal."
    },
    {
      "id": 2,
      "title": "Bank Indonesia Raises Rates Cumulative 100bps Since May — Rupiah at 17,870/USD",
      "category": "RUPIAH",
      "tags": ["bi-rate", "rupiah", "inflation"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "Bank Indonesia", "url": "https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_289426.aspx"},
        {"name": "Trading Economics", "url": "https://tradingeconomics.com/indonesia/stock-market"}
      ],
      "eventDate": "2026-06-18",
      "whatHappened": "Bank Indonesia has delivered a cumulative 100 basis points of rate hikes since May 2026, lifting the BI Rate to defend the rupiah amid capital flight driven by the US Fed's hawkish pivot and global risk-off sentiment. The rupiah is currently quoted at approximately IDR 17,870 per US dollar. BI Governor Perry Warjiyo has stated that currency stability is the primary policy objective at this stage.",
      "whatItCanDo": [
        "Reduce capital outflow pressure by making Indonesian IDR assets more attractive on a carry basis",
        "Slow domestic credit growth and consumption, moderating import demand and current account pressure",
        "Signal to foreign investors that BI is committed to defending the currency, reducing speculative rupiah selling"
      ],
      "whatsCatch": [
        "Higher rates will slow GDP growth — projected 4.9-5.7% range may compress toward the lower bound",
        "Small and medium enterprises that rely on bank credit face sharply higher borrowing costs",
        "BI cannot out-hike the Fed indefinitely without causing domestic economic damage",
        "At 17,870/USD the rupiah is near its 2020 COVID-crisis lows — further weakness would be psychologically significant"
      ],
      "keyTakeaway": "BI is sacrificing growth to defend the rupiah — the right call for macro stability but a headwind for domestic consumption and IHSG earnings in H2 2026.",
      "howToImprove": "Watch the July BI board meeting: if they pause, it signals confidence that 100bps is sufficient. If they hike again, the currency situation is worse than publicly stated.",
      "vsPrevious": "First time covering Bank Indonesia policy in this terminal."
    },
    {
      "id": 3,
      "title": "IHSG Recovers +16.4% from June 8 Low — But Sits Below Pre-Selloff Levels",
      "category": "IDX",
      "tags": ["ihsg", "foreign-flows", "recovery"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "Heygotrade", "url": "https://www.heygotrade.com/en/news/indonesia-ihsg-june-2-outlook-stock-picks/"},
        {"name": "IDX Tracker", "url": "https://www.idxtracker.com/"}
      ],
      "eventDate": "2026-06-22",
      "whatHappened": "The IHSG Composite rose to 6,254 on June 15, recovering +16.4% from its June 8 intraday low of 5,342. On June 22, the index edged up 12 points (+0.2%) to 6,185 in early trade, as optimism over US-Iran ceasefire talks (positive for oil and risk sentiment) offset continued Fed hawkishness concerns. The recovery was driven by BI rate stability, commodity price relief, and compression in EM risk premiums.",
      "whatItCanDo": [
        "Restore some confidence among domestic retail investors who fled during the June 8 rout",
        "Allow Indonesian companies to resume capital market activities (IPOs, rights issues) that were suspended",
        "Attract selective returning foreign flows into commodity-linked stocks (coal, CPO, nickel)"
      ],
      "whatsCatch": [
        "MSCI frontier downgrade risk is the dominant overhang — confirmed downgrade would erase the recovery",
        "At 6,185, IHSG is still well below January 2026 levels — the recovery has not rebuilt structural confidence",
        "Foreign net selling has continued even during the recovery — domestic retail is the marginal buyer",
        "Further Fed hawkishness could trigger another round of EM capital flight"
      ],
      "keyTakeaway": "The IHSG recovery is technically significant but structurally fragile — it will not be sustained if the MSCI decision goes against Indonesia.",
      "howToImprove": "Track the MSCI decision expected this week. If Indonesia retains EM status, IHSG could rally to 6,500. If downgraded, expect a retest of the 5,342 low.",
      "vsPrevious": "First time covering IHSG recovery dynamics in this terminal."
    },
    {
      "id": 4,
      "title": "Indonesia Q1 2026 GDP Grows 5.61% — Above Expectations",
      "category": "MACRO",
      "tags": ["pdb", "pertumbuhan", "ekonomi"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "Bank Indonesia", "url": "https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_289426.aspx"},
        {"name": "OECD", "url": "https://www.oecd.org/en/publications/foundations-for-growth-and-competitiveness-2026_40a7532f-en/full-report/indonesia_e440b90a.html"}
      ],
      "eventDate": "2026-06-15",
      "whatHappened": "Indonesia's economy grew 5.61% year-over-year in Q1 2026, accelerating from 5.39% in Q4 2025 and beating consensus estimates. Growth was supported by strong domestic consumption, continued infrastructure investment under President Prabowo's economic program, and commodity export revenues from nickel and coal. Full-year 2026 growth is projected in the 4.9-5.7% range.",
      "whatItCanDo": [
        "Provide fiscal headroom for the government to absorb the economic cost of Bank Indonesia's rate hikes",
        "Support government revenue collection, improving the APBN (state budget) balance",
        "Attract foreign direct investment to a structurally growing economy despite short-term market volatility"
      ],
      "whatsCatch": [
        "Q1 growth may not be sustained if BI rate hikes slow credit and consumption in Q2-Q3",
        "Infrastructure bottlenecks outside Java continue to constrain potential growth — OECD estimates 0.5-1% GDP drag",
        "Student protests over fuel and food prices signal that growth is not translating to broad welfare improvement"
      ],
      "keyTakeaway": "Indonesia's GDP growth is solid and broad-based, but the financial market turbulence of June 2026 risks slowing the real economy in H2 if the rupiah and equity market instability persists.",
      "howToImprove": "BPS should release Q2 2026 flash data early in July to reassure markets. A Q2 print above 5% would significantly reduce the macro risk premium on Indonesian assets.",
      "vsPrevious": "First time covering Indonesia GDP in this terminal."
    }
  ],
  "quickHits": [
    {"title": "Nickel price recovery supports Indonesia exports", "text": "LME nickel up 8% in June as EV battery demand recovers. Indonesia, world's largest nickel producer, benefits directly.", "url": "https://tradingeconomics.com/indonesia/stock-market"},
    {"title": "Indonesia green economy milestone June 2026", "text": "Indonesia activated its first large-scale green sukuk (Islamic bond) for renewable energy transition, marking a capital market first.", "url": "https://www.facebook.com/TheDiplomaticInsight/posts/june-2026-marks-a-pivotal-moment-in-indonesias-green-economy-journey-for-the-fir/1610025311126066/"},
    {"title": "OJK reviewing coordinated trading rules", "text": "Financial regulator OJK fast-tracking market surveillance reform in response to MSCI warning.", "url": "https://www.idxtracker.com/"}
  ]
},

# ───────────────────────────────────────────────────────────────
"indo-news": {
  "date": "2026-06-22",
  "indexHeadline": "Indonesian students protest over fuel and food prices; Prabowo faces first major public pressure test",
  "indexSummary": "Hundreds of students rallied in Jakarta demanding lower fuel and food prices and urging President Prabowo to roll back costly state spending programs. Indonesia's economy grew 5.61% in Q1 2026 but economic pressures are not reaching ordinary citizens. A new green economy milestone was reached with Indonesia's first green sukuk. Bank Indonesia hiked rates 100bps cumulatively to defend the rupiah.",
  "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
  "topSignal": [
    {"headline": "Student protests hit Jakarta over fuel and food costs", "detail": "Hundreds gathered demanding lower prices and spending rollbacks. First significant public pressure on Prabowo since taking office. Echoes of 1998 Reform era student movements in optics, though scale is far smaller."},
    {"headline": "5.61% GDP growth — but welfare gap growing", "detail": "Indonesia's macro numbers are strong but protests show growth not reaching working-class households. Fuel subsidies were cut under budget reform, directly raising transport costs."},
    {"headline": "Bank Indonesia 100bps hike hits domestic borrowers", "detail": "Rate hikes necessary for currency stability but raise borrowing costs for SMEs and households. Mortgage rates and consumer credit rates will follow. Squeeze on middle-income Indonesians intensifying."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "Indonesian Students Protest in Jakarta, Demand Prabowo Roll Back Fuel and Food Prices",
      "category": "SOCIAL",
      "tags": ["protest", "prabowo", "ekonomi"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "ABC News", "url": "https://abcnews.com/International/wireStory/indonesian-students-protest-government-policies-economic-pressures-grow-133810558"},
        {"name": "Antara", "url": "https://en.antaranews.com/"}
      ],
      "eventDate": "2026-06-21",
      "whatHappened": "Hundreds of university students staged demonstrations in Jakarta and several regional cities, demanding lower fuel and food prices and calling on President Prabowo Subianto to reverse what they described as costly and regressive state spending programs. The protests are the largest since Prabowo took office and reflect growing frustration among urban youth and working-class Indonesians over the gap between strong macroeconomic growth data and everyday cost-of-living pressures. Police monitored but did not disperse gatherings.",
      "whatItCanDo": [
        "Pressure the Prabowo administration to review fuel subsidy policy ahead of the July state budget revision",
        "Signal to international investors that Indonesian political stability has more complexity than the smooth post-election narrative suggested",
        "Mobilise broader civil society engagement — student protests in Indonesia have historically been precursors to larger movements",
        "Push the government to announce targeted social assistance measures (bantuan sosial) to defuse pressure"
      ],
      "whatsCatch": [
        "Student protest scale remains limited — hundreds, not thousands, and not yet coordinated nationally",
        "Prabowo's coalition controls nearly 80% of parliament, limiting opposition ability to amplify grievances politically",
        "The government can argue that fuel price adjustments were necessary fiscal reforms, not attacks on welfare",
        "Indonesia's media environment has become more restricted — major amplification through mainstream channels is limited"
      ],
      "keyTakeaway": "Indonesia's growth story has a distributional problem — 5.61% GDP growth is real, but fuel and food price pressures are eroding household purchasing power faster than wages are rising.",
      "howToImprove": "The Prabowo government needs to either restore targeted fuel subsidies for low-income households (expensive) or dramatically accelerate bantuan sosial cash transfers (politically faster). Neither is currently announced.",
      "vsPrevious": "First time covering social protests in the Prabowo era in this terminal."
    },
    {
      "id": 2,
      "title": "Constitutional Economics Debate Intensifies — State Challenges Market Orthodoxy",
      "category": "POLITICS",
      "tags": ["ekonomi", "konstitusi", "kebijakan"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "Zona Satu News", "url": "https://www.zonasatunews.com/ketika-negara-berbelok-arah-ke-koordinat-ekonomi-konstitusi-perang-narasi-dan-benturan-dua-paradigma-ekonomi/comment-page-1/"},
        {"name": "World Bank Indonesia", "url": "https://www.worldbank.org/ext/en/country/indonesia"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "A significant policy debate is intensifying within Indonesian government and academic circles over the country's economic direction. One faction — aligned with nationalistic elements of the Prabowo coalition — advocates for 'constitutional economics,' a framework that would prioritise state-led development and resource nationalism over market-oriented policies endorsed by the IMF, World Bank, and Indonesia's technocratic economic team. The debate has practical implications for foreign investment policy, mining licensing, and state-owned enterprise reform.",
      "whatItCanDo": [
        "Shift investment policy away from FDI liberalisation toward greater state control of strategic sectors",
        "Affect licensing terms for mining, energy, and digital economy sectors where foreign capital is currently dominant",
        "Change the calculus for international businesses considering Indonesia as a manufacturing destination post-China"
      ],
      "whatsCatch": [
        "Constitutional economics frameworks have a poor track record in Indonesia — similar rhetoric preceded costly nationalisation decisions in the 2010s",
        "Indonesia's technocratic finance team (Sri Mulyani et al.) remains institutionally strong and market-oriented",
        "The debate may be more political signalling than genuine policy direction — Prabowo has not yet formally endorsed the nationalist position",
        "Foreign investors will watch closely: any shift toward resource nationalism would increase country risk premium"
      ],
      "keyTakeaway": "The constitutional economics debate is the clearest sign yet that Indonesia's economic policy direction under Prabowo is genuinely contested — and the outcome will determine FDI trajectory for the next five years.",
      "howToImprove": "Watch the July APBN revision and any changes to mining licensing terms: those are where ideology becomes concrete policy. International investors should monitor OJK and BKPM communications closely.",
      "vsPrevious": "First time covering Indonesia's constitutional economics debate in this terminal."
    },
    {
      "id": 3,
      "title": "Indonesia Activates First Green Sukuk — IDR Climate Finance Milestone",
      "category": "ENVIRONMENT",
      "tags": ["green-economy", "sukuk", "iklim"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "The Diplomatic Insight", "url": "https://www.facebook.com/TheDiplomaticInsight/posts/june-2026-marks-a-pivotal-moment-in-indonesias-green-economy-journey-for-the-fir/1610025311126066/"},
        {"name": "OECD Indonesia", "url": "https://www.oecd.org/en/publications/foundations-for-growth-and-competitiveness-2026_40a7532f-en/full-report/indonesia_e440b90a.html"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "Indonesia activated its first large-scale green sukuk (Islamic bond) specifically structured for renewable energy transition projects. The instrument marks a capital market milestone for Indonesia's stated goal of achieving carbon neutrality by 2060. The sukuk will fund solar and geothermal energy projects across Java and Sumatra. Indonesia has the world's largest geothermal potential and is gradually transitioning away from coal dependence.",
      "whatItCanDo": [
        "Unlock international Islamic finance capital (estimated $3-4 trillion market) for Indonesian green projects",
        "Support Indonesia's NDC (Nationally Determined Contribution) commitments under the Paris Agreement",
        "Create a template for other Muslim-majority developing nations to finance energy transition via sukuk",
        "Reduce Indonesia's dependence on coal-fired power (currently ~60% of electricity generation)"
      ],
      "whatsCatch": [
        "Green sukuk proceeds must be transparently allocated — Indonesia's past green bond reporting has had gaps",
        "Coal remains politically protected in Indonesia due to the mining industry's influence on Golkar and other coalition parties",
        "Geothermal development faces land rights conflicts in Sumatra and Sulawesi",
        "The sukuk size has not been publicly disclosed — scale matters for impact"
      ],
      "keyTakeaway": "Indonesia's green sukuk is a genuine capital market innovation that could accelerate energy transition financing — but coal dependence will not be resolved by financial instruments alone.",
      "howToImprove": "PLN (state electricity company) should publish a detailed transition roadmap showing coal plant retirement schedules. Without decommissioning timelines, green sukuk proceeds risk being used to build new renewable capacity while coal stays online.",
      "vsPrevious": "First time covering Indonesia green finance in this terminal."
    },
    {
      "id": 4,
      "title": "Infrastructure Bottlenecks Cost Indonesia 0.5-1% Annual GDP — OECD",
      "category": "ECONOMY",
      "tags": ["infrastruktur", "logistik", "pertumbuhan"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "OECD", "url": "https://www.oecd.org/en/publications/foundations-for-growth-and-competitiveness-2026_40a7532f-en/full-report/indonesia_e440b90a.html"},
        {"name": "Business Indonesia", "url": "https://business-indonesia.org/news/indonesia-s-economic-outlook-2026-resilient-but-acceleration-elusive"}
      ],
      "eventDate": "2026-06-18",
      "whatHappened": "The OECD's 2026 Indonesia competitiveness report estimates that infrastructure bottlenecks — gaps in electricity reliability, road connectivity, port capacity, and urban transport outside Java — cost the economy 0.5-1.0% of GDP per year in lost potential output. The report notes that logistics costs in Indonesia are among the highest in ASEAN, reducing export competitiveness. The government's Nusantara capital relocation project has not addressed inter-island connectivity gaps.",
      "whatItCanDo": [
        "If resolved, infrastructure improvement could push Indonesia's growth rate toward 6.5-7% — significantly above current trajectory",
        "Reducing logistics costs by 20% would improve export competitiveness for manufactured goods from Sulawesi, Kalimantan, and Papua",
        "Better electricity reliability outside Java would enable manufacturing investment to spread beyond the island"
      ],
      "whatsCatch": [
        "Infrastructure investment takes 5-10 years to deliver economic benefit — no short-term fix",
        "Nusantara capital project is consuming government capital that could otherwise fund inter-island connectivity",
        "Land acquisition for infrastructure projects remains slow due to legal complexity and local resistance",
        "Private sector participation in toll roads and ports has been lower than projected"
      ],
      "keyTakeaway": "Indonesia's infrastructure gap is a known, quantified drag on growth — the question is whether the Prabowo government will prioritise inter-island connectivity over prestige projects like Nusantara.",
      "howToImprove": "The government's RPJMN (medium-term development plan) revision due in Q3 2026 should prioritise electricity and port connectivity for eastern Indonesia over continued Nusantara spending.",
      "vsPrevious": "First time covering Indonesia infrastructure in this terminal."
    }
  ],
  "quickHits": [
    {"title": "Prabowo social spending programs under scrutiny", "text": "Student protesters specifically cited free lunch program (makan bergizi gratis) as expensive but poorly targeted. Program costs IDR 71T per year.", "url": "https://abcnews.com/International/wireStory/indonesian-students-protest-government-policies-economic-pressures-grow-133810558"},
    {"title": "Antara: BI rate hike affects mortgage rates", "text": "Indonesian banks expect to raise KPR (mortgage) rates by 50-75bps following BI's cumulative 100bps hike. Housing market to cool.", "url": "https://en.antaranews.com/"},
    {"title": "Indonesia Q1 GDP 5.61% beats estimates", "text": "Growth accelerated from Q4 2025's 5.39%, supported by commodity revenues and domestic consumption. Full-year target 4.9-5.7%.", "url": "https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_289426.aspx"}
  ]
},

# ───────────────────────────────────────────────────────────────
"crypto-news": {
  "date": "2026-06-22",
  "indexHeadline": "Bitcoin holds $64K as US-Iran talks progress; ETF outflow streak ends after 13 days",
  "indexSummary": "Bitcoin is holding near $64,000, down ~30% YTD but stabilising as geopolitical risk sentiment improves on US-Iran talks. The record 13-day ETF outflow streak that shed $4.4B ended June 5. An Ethereum governance proposal would redirect validator staking income to ecosystem funding. Microsoft found USB-spread crypto wallet malware. An Ethereum sandwich bot lost $7.5M in an ironic hack.",
  "stats": {"total": 5, "major": 1, "significant": 2, "notable": 2},
  "topSignal": [
    {"headline": "Bitcoin -30% YTD but stabilising at $64K", "detail": "Record 13-day ETF outflow streak ended June 5 after shedding $4.4B. BTC now in consolidation range. US-Iran de-escalation slightly positive for risk assets but crypto sitting out the equity rally."},
    {"headline": "Ethereum validator staking governance vote incoming", "detail": "Proposal would redirect a portion of ETH staking rewards to ecosystem development funding. If passed, changes the economic model for validators — potentially 3-5% reduction in yield."},
    {"headline": "USB-spread crypto wallet malware confirmed by Microsoft", "detail": "Malware targets hot wallets on Windows, spread via USB sticks. Multiple confirmed theft incidents. Cold storage strongly recommended. No patch yet from wallet providers."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "Bitcoin -30% YTD, Holds $64K as Macro Headwinds Persist",
      "category": "BTC",
      "tags": ["bitcoin", "macro", "etf"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "CoinDesk", "url": "https://www.coindesk.com/markets/2026/06/01/bitcoin-ether-start-june-in-the-red-while-futures-show-taste-for-risk-xlm-hype-gain"},
        {"name": "eciks.org", "url": "https://eciks.org/8117-61802-cryptocurrency-trading-correction-bitcoin-ethereum-2026"},
        {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/personal-finance/investing/article/bitcoin-and-ethereum-prices-today-june-2-2026-bitcoin-slides-below-70000-132451998.html"}
      ],
      "eventDate": "2026-06-22",
      "whatHappened": "Bitcoin is trading near $64,000 as of June 22, 2026, representing approximately a 30% decline year-to-date from its January 2026 highs. The correction accelerated in early June when BTC fell below $65,000, triggering over $1.8 billion in liquidated leveraged trades in a single day. US spot Bitcoin ETFs experienced a record 13-day outflow streak ending June 5, with $4.4 billion in net outflows. The ETF flow has since stabilised, but BTC has not recovered materially. Today, BTC edged slightly higher as US-Iran ceasefire talks progressed — but crypto largely sat out the broader risk-asset rally.",
      "whatItCanDo": [
        "Consolidation at $64K could form a base for recovery if ETF inflows resume in Q3",
        "US-Iran de-escalation reduces geopolitical risk premium globally — marginally positive for BTC as risk asset",
        "End of ETF outflow streak removes the strongest seller of recent months",
        "Mining economics at $64K remain profitable for efficient miners — no forced selling from hash rate decline"
      ],
      "whatsCatch": [
        "Fed hawkishness is the dominant macro headwind — real rates rising is historically negative for BTC",
        "30% YTD decline has damaged retail sentiment — the 'number go up' narrative is broken for 2026",
        "Institutional flows remain net negative even after the ETF outflow streak ended",
        "On-chain data shows long-term holders are not accumulating — unusual at this price level"
      ],
      "keyTakeaway": "Bitcoin's $64K level is a tenuous equilibrium — it holds as long as macro conditions don't worsen further, but there is no strong catalyst for a new all-time high in the near term.",
      "howToImprove": "Watch the June CPI print (July 10): if inflation prints below 3.2%, Fed hike probability falls and BTC could rally toward $70K. Above 3.5% CPI would likely retest the $60K support.",
      "vsPrevious": "First time covering Bitcoin's 2026 bear market in this terminal. Prior coverage noted BTC as part of the macro picture."
    },
    {
      "id": 2,
      "title": "Ethereum Governance Proposal: Redirect Validator Staking Rewards to Ecosystem Fund",
      "category": "ETH",
      "tags": ["ethereum", "staking", "governance"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "The Block", "url": "https://www.theblock.co/"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "A new governance proposal posted to the Ethereum community forum proposes allowing ETH validators to redirect a portion of their staking income toward an on-chain ecosystem development fund. The proposal would create a programmable mechanism where validators opt into redirecting 3-5% of staking rewards to a DAO-governed treasury for protocol development grants, security audits, and public goods funding. No EIP number assigned yet — still in community discussion phase.",
      "whatItCanDo": [
        "Create a sustainable, protocol-native funding mechanism for Ethereum development that does not rely on Ethereum Foundation grants",
        "Reduce the influence of the Ethereum Foundation over protocol direction by distributing funding control to validators",
        "Fund security audits and formal verification work that is currently underfunded across the ecosystem",
        "Set a precedent for other PoS chains to implement validator-funded public goods mechanisms"
      ],
      "whatsCatch": [
        "3-5% staking yield reduction would reduce validator economics and potentially reduce ETH staking participation",
        "DAO governance of the treasury creates new attack vectors and political dynamics within Ethereum governance",
        "Large institutional stakers (Lido, Coinbase) would effectively control treasury votes, recreating centralization concerns",
        "The proposal has not gone through EIP process — implementation timeline is months away even if consensus builds"
      ],
      "keyTakeaway": "Redirecting staking rewards to ecosystem funding is a sound mechanism design idea — but the governance of the resulting treasury is where the real risk lies.",
      "howToImprove": "The proposal needs a clear validator threshold for quorum, a transparent grant committee process, and a hard cap on treasury size to prevent accumulation of excess capital without deployment.",
      "vsPrevious": "First time covering Ethereum governance proposals in this terminal."
    },
    {
      "id": 3,
      "title": "Microsoft Confirms USB-Spread Malware Targeting Crypto Hot Wallets",
      "category": "HACK",
      "tags": ["hack", "security", "bitcoin"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "CryptoSlate", "url": "https://cryptoslate.com/"},
        {"name": "The Block", "url": "https://www.theblock.co/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "Microsoft's security team confirmed the discovery of malware specifically designed to target cryptocurrency hot wallets, with the infection vector being USB storage devices. The malware executes upon USB insertion on Windows machines, scans for browser-based wallet extensions (MetaMask, Phantom, Coinbase Wallet) and standalone wallet applications, and exfiltrates private keys or seed phrases. Multiple confirmed theft incidents have been reported. No patch is available from wallet providers yet.",
      "whatItCanDo": [
        "Steal all funds from any connected hot wallet within seconds of USB insertion — no user interaction needed",
        "Spread through shared computers, public crypto terminals, and corporate networks via USB propagation",
        "Target any Windows-based wallet application — browser extensions, desktop clients, and hardware wallet management software"
      ],
      "whatsCatch": [
        "Cold wallets (Ledger, Trezor) are not directly vulnerable — but their management software on Windows may be targeted",
        "The malware requires physical USB access — lower risk than remote exploits but significant in shared spaces",
        "USB autorun is disabled by default in modern Windows — older or misconfigured systems are at highest risk",
        "No confirmed attribution — unknown whether state actor, criminal group, or individual"
      ],
      "keyTakeaway": "Do not plug unknown USB devices into any computer that has crypto wallet access — and move significant holdings to cold storage immediately.",
      "howToImprove": "Microsoft should release an emergency Windows Defender signature update to detect this specific malware family. Wallet providers (MetaMask, Phantom) should publish advisories and consider adding PIN-at-launch requirements.",
      "vsPrevious": "First time covering crypto wallet malware in this terminal."
    },
    {
      "id": 4,
      "title": "Ethereum Sandwich Bot JaredFromSubway Drained of $7.5M in Ironic Exploit",
      "category": "HACK",
      "tags": ["exploit", "ethereum", "defi", "mev"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "CryptoTimes", "url": "https://www.cryptotimes.io/2026/06/22/ethereum-mev-bot-jaredfromsubway-drained-in-15m-honeypot-attack/"},
        {"name": "The Block", "url": "https://www.theblock.co/"}
      ],
      "eventDate": "2026-06-22",
      "whatHappened": "The Ethereum MEV (Maximum Extractable Value) bot known as JaredFromSubway — one of the most prolific sandwich attack bots on Ethereum, reportedly responsible for up to 70% of all sandwich attacks during peak activity — was itself drained via a honeypot attack. The operator confirmed losses of approximately $7.5M (some reports cite up to $15M). The attacker set up a deliberately vulnerable-looking transaction that JaredFromSubway's bot executed, triggering the drain.",
      "whatItCanDo": [
        "Demonstrate that MEV bots themselves are targets — the hunter became the hunted",
        "Reduce sandwich attack activity on Ethereum in the short term as MEV bot operators reassess risk parameters",
        "Highlight the need for better simulation and honeypot detection in MEV bot code"
      ],
      "whatsCatch": [
        "JaredFromSubway has extracted tens of millions from retail users since 2023 — limited sympathy from the community",
        "The MEV ecosystem will adapt — other bots will fill the vacuum within days",
        "This does not resolve the underlying sandwich attack problem for retail Ethereum users",
        "The attacker's identity and fund destination are unknown"
      ],
      "keyTakeaway": "JaredFromSubway being drained by a honeypot is poetic justice — but it changes nothing structural about MEV extraction harming retail Ethereum users.",
      "howToImprove": "Ethereum's long-term answer to MEV is encrypted mempools (EIP-7503 family) and order flow auctions that return MEV value to users. These are still 12-18 months from mainnet deployment.",
      "vsPrevious": "First time covering MEV bot exploits in this terminal."
    },
    {
      "id": 5,
      "title": "OSL Group Secures Australian Financial Services Licence for Crypto",
      "category": "REGULATION",
      "tags": ["regulation", "australia", "stablecoin"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "CryptoSlate", "url": "https://cryptoslate.com/"},
        {"name": "BeInCrypto", "url": "https://beincrypto.com/bitcoin-and-ethereum-options-expire-as-2026-begins/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "OSL Group, a Hong Kong-listed crypto exchange and infrastructure provider, secured an Australian Financial Services Licence (AFSL) from ASIC, the Australian financial regulator. The licence enables OSL to offer regulated stablecoin and digital asset payment infrastructure in Australia. Australia has been accelerating its crypto regulatory framework in 2026, with the Treasury's digital assets bill progressing through parliament.",
      "whatItCanDo": [
        "Enable institutional clients to access crypto infrastructure under Australian regulatory protection",
        "Support stablecoin payments integration with Australian banking and payments systems",
        "Signal that Australia is emerging as a crypto-friendly regulated jurisdiction in the Asia-Pacific region"
      ],
      "whatsCatch": [
        "AFSL is a broad licence category — the specific activities permitted under OSL's licence have not been fully disclosed",
        "Australia's digital assets bill has not yet passed — regulatory framework remains in flux",
        "Competition from Coinbase, Kraken, and local exchanges in the Australian market is intense"
      ],
      "keyTakeaway": "Australia's willingness to license crypto infrastructure providers signals that regulated crypto rails are expanding in Asia-Pacific — a positive signal for institutional adoption in the region.",
      "howToImprove": "ASIC should publish a clear taxonomy of what activities each licence type covers for crypto firms — current opacity creates compliance uncertainty for other applicants.",
      "vsPrevious": "First time covering Australian crypto regulation in this terminal."
    }
  ],
  "quickHits": [
    {"title": "Polymarket crypto election odds active", "text": "Prediction market Polymarket shows active crypto-related policy bets for the remainder of 2026. Bitcoin ETF options approval the most traded market.", "url": "https://polymarket.com/crypto"},
    {"title": "BTC options expiry this week", "text": "$2.2B in Bitcoin options expire Friday. Max pain level at $62,000 — could create short-term price pressure toward that level.", "url": "https://beincrypto.com/bitcoin-and-ethereum-options-expire-as-2026-begins/"},
    {"title": "Solana DeFi TVL holds above $12B", "text": "Despite BTC/ETH weakness, Solana DeFi total value locked remains resilient. Meteora and Kamino sustaining volumes.", "url": "https://coinfomania.com/why-solana-just-ranked-3-in-fortunes-blockchain-list/"}
  ]
},

# ───────────────────────────────────────────────────────────────
"blockchain-news": {
  "date": "2026-06-22",
  "indexHeadline": "JaredFromSubway MEV bot drained $15M; Solana ranks #3 in Fortune blockchain list",
  "indexSummary": "JaredFromSubway, Ethereum's most prolific sandwich attack bot responsible for 70% of MEV sandwich attacks, was drained of $7.5-15M in a honeypot counterattack. Solana ranked #3 in Fortune's 2026 Blockchain and Protocols list, with three of its DeFi protocols in the top 10. Prediction markets reached $24B monthly volume. Ethereum validator staking governance proposal introduced.",
  "stats": {"total": 4, "major": 1, "significant": 2, "notable": 1},
  "topSignal": [
    {"headline": "JaredFromSubway MEV bot loses up to $15M to honeypot", "detail": "The bot responsible for ~70% of Ethereum sandwich attacks was itself caught in a deliberate trap. Confirms MEV bots are active attack surfaces. Short-term MEV activity will fall as operators reassess."},
    {"headline": "Solana #3 in Fortune blockchain rankings", "detail": "Meteora, Kamino, and Raydium all in top 10 DeFi protocols. Solana's throughput (65K TPS peak), sub-cent fees, and DeFi ecosystem positioning it as institutional-grade L1 alternative to Ethereum."},
    {"headline": "Global prediction markets reach $24B monthly volume", "detail": "Combined prediction market activity up from near-zero in 2023 to $24B/month by April 2026. Polymarket dominant. New protocols integrating prediction markets into wallets as native feature."}
  ],
  "stories": [
    {
      "id": 1,
      "title": "JaredFromSubway MEV Bot Drained $7.5-15M — Sandwich Attacker Becomes the Victim",
      "category": "SECURITY",
      "tags": ["mev", "exploit", "ethereum", "hack"],
      "priority": "MAJOR",
      "priorityLevel": 1,
      "sources": [
        {"name": "CryptoTimes", "url": "https://www.cryptotimes.io/2026/06/22/ethereum-mev-bot-jaredfromsubway-drained-in-15m-honeypot-attack/"},
        {"name": "The Block", "url": "https://www.theblock.co/"}
      ],
      "eventDate": "2026-06-22",
      "whatHappened": "The Ethereum MEV bot operating under the address known as JaredFromSubway, which has been responsible for up to 70% of all sandwich attacks on Ethereum during peak periods and has extracted tens of millions from retail users since 2023, was drained in a sophisticated honeypot attack. An unknown attacker constructed a deliberately enticing-looking transaction with manipulated parameters that triggered JaredFromSubway's sandwich attack logic. The resulting execution transferred the bot's funds to the attacker. The operator confirmed total losses of approximately $7.5M; on-chain analysis by independent researchers suggests the true total may be closer to $15M.",
      "whatItCanDo": [
        "Temporarily reduce sandwich attack volume on Ethereum as MEV operators audit their bot code for similar vulnerabilities",
        "Prove that MEV bots can be defeated at their own game — creating a cat-and-mouse dynamic that benefits retail users short-term",
        "Inspire further research into honeypot-based MEV countermeasures as a retail protection strategy",
        "Reduce JaredFromSubway's operational capacity significantly — losing $15M from a bot's capital base is existential"
      ],
      "whatsCatch": [
        "MEV ecosystem will adapt within days — other bots will deploy improved code with honeypot detection",
        "The attacker exploited the same aggressive and greedy logic that made JaredFromSubway dangerous to retail users — no moral clarity here",
        "Retail users are still exposed to MEV from other bots; this incident does not solve the systemic problem",
        "The exploit technique is now public knowledge — could be weaponised against other MEV bots or legitimate DeFi protocols"
      ],
      "keyTakeaway": "JaredFromSubway's demise is a watershed moment for MEV awareness — but the structural problem of front-running and sandwich attacks on Ethereum requires protocol-level solutions, not counterattacks.",
      "howToImprove": "Ethereum core developers should accelerate work on encrypted mempools (EIP-7503 and related proposals) that would make sandwich attacks computationally impossible. The technical path exists; the timeline is the problem.",
      "vsPrevious": "First time covering JaredFromSubway and MEV exploits in this terminal."
    },
    {
      "id": 2,
      "title": "Solana Ranks #3 in Fortune's 2026 Blockchain and Protocols List",
      "category": "PROTOCOL",
      "tags": ["solana", "defi", "l1"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "CoinFomania", "url": "https://coinfomania.com/why-solana-just-ranked-3-in-fortunes-blockchain-list/"},
        {"name": "The Block", "url": "https://www.theblock.co/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "Fortune published its 2026 Blockchain and Protocols ranking, placing Solana at #3 behind Bitcoin and Ethereum. Three Solana-native DeFi protocols — Meteora (AMM and liquidity), Kamino (lending and yield), and Raydium (DEX) — ranked in the top 10 most influential DeFi projects globally. Fortune cited Solana's transaction throughput (up to 65,000 TPS peak), sub-cent transaction fees, and the strength of its developer ecosystem as key differentiators.",
      "whatItCanDo": [
        "Attract institutional interest in Solana as a credible alternative to Ethereum for high-frequency DeFi applications",
        "Validate Solana's DeFi ecosystem as mature enough for serious capital allocation",
        "Accelerate Fortune 500 pilots building on Solana for payments and financial infrastructure",
        "Increase competitive pressure on Ethereum L2s (Arbitrum, Base, OP) to improve cost and throughput"
      ],
      "whatsCatch": [
        "Solana has a history of network outages — the #3 ranking does not mean uptime reliability problems are fully resolved",
        "Solana's validator concentration remains higher than Ethereum's — decentralisation concerns persist",
        "DeFi TVL on Solana (~$12B) is still well below Ethereum + L2s (~$80B+)",
        "The ranking is editorial, not based on a standardised methodology — it reflects prestige but not objective metrics"
      ],
      "keyTakeaway": "Solana's Fortune #3 ranking is validation that it has permanently established itself as a tier-1 blockchain — the question is now whether it can close the TVL and developer gap with Ethereum.",
      "howToImprove": "Solana Foundation should publish a network reliability SLA with historical uptime data and a public incident response framework. Institutional capital requires reliability guarantees that Solana has not yet formally offered.",
      "vsPrevious": "First time covering Solana ranking and ecosystem in this terminal."
    },
    {
      "id": 3,
      "title": "Prediction Markets Hit $24B Monthly Volume — Polymarket Dominates",
      "category": "DEFI",
      "tags": ["prediction-markets", "defi", "dao"],
      "priority": "SIGNIFICANT",
      "priorityLevel": 2,
      "sources": [
        {"name": "Antier", "url": "https://www.antier.com/blogs/prediction-markets-in-crypto-wallets-the-web3-wallet-feature-nobody-saw-coming/"},
        {"name": "CoinSpaid Media", "url": "https://coinspaidmedia.com/business/major-crypto-and-fintech-events-june-2026/"}
      ],
      "eventDate": "2026-06-20",
      "whatHappened": "Global decentralised prediction markets processed $63.5 billion in total notional trading volume in 2025, with combined monthly activity reaching $24 billion by April 2026. Polymarket remains the dominant platform with the majority of market share. A new trend is emerging: prediction market functionality is being integrated directly into crypto wallets as a native feature, eliminating the need to visit a separate DApp.",
      "whatItCanDo": [
        "Embed real-world information pricing into every user's crypto wallet — democratising access to prediction markets",
        "Enable institutional traders to hedge geopolitical and macro event risk via decentralised markets without counterparty risk",
        "Create a new source of fee revenue for wallet providers integrating prediction market infrastructure",
        "Improve information efficiency in crypto markets by creating on-chain price discovery for macro events"
      ],
      "whatsCatch": [
        "Regulatory status of prediction markets remains uncertain in the US — CFTC has not definitively classified them",
        "Wallet-integrated prediction markets increase user exposure to complex financial instruments without adequate risk disclosure",
        "$24B monthly volume is large in crypto terms but tiny compared to traditional derivatives markets ($1T+ daily)",
        "Liquidity on smaller markets remains thin — large positions can move prices significantly"
      ],
      "keyTakeaway": "Prediction markets are graduating from crypto novelty to financial infrastructure — $24B monthly volume proves there is genuine demand for decentralised event-driven trading.",
      "howToImprove": "The prediction market space needs a unified liquidity layer so capital can flow between Polymarket, Drift, and emerging competitors. Fragmented liquidity keeps spreads wide on all but the largest markets.",
      "vsPrevious": "First time covering prediction markets in this terminal."
    },
    {
      "id": 4,
      "title": "Ethereum Validator Staking Governance Proposal — EIP Draft Phase",
      "category": "PROTOCOL",
      "tags": ["ethereum", "staking", "governance", "eip"],
      "priority": "NOTABLE",
      "priorityLevel": 3,
      "sources": [
        {"name": "The Block", "url": "https://www.theblock.co/"},
        {"name": "Ethereum.org", "url": "https://ethereum.org/en/blog"}
      ],
      "eventDate": "2026-06-19",
      "whatHappened": "A community governance proposal is circulating in Ethereum research forums that would allow validators to voluntarily redirect 3-5% of their staking rewards to a protocol-level ecosystem development fund governed by a DAO. The proposal is in early community discussion phase and has not yet been assigned an EIP number. It represents a departure from the Ethereum Foundation's current grant-based model toward a validator-funded development model similar to some PoS chains.",
      "whatItCanDo": [
        "Create a sustainable funding stream for Ethereum protocol development that does not depend on Ethereum Foundation's ETH sales",
        "Align validator economic interests with protocol health by giving them governance over development funding",
        "Fund formal verification, security research, and public goods that current grant processes underfund"
      ],
      "whatsCatch": [
        "3-5% staking yield reduction would push some validators — especially smaller ones — below break-even on hardware costs",
        "Lido and Coinbase staking pools control >40% of staked ETH combined — they would dominate DAO governance",
        "Adding programmable validator mechanics increases attack surface and complexity for future upgrades",
        "The proposal competes with EOF (EVM Object Format) and Verkle Trees for core developer attention — bandwidth is limited"
      ],
      "keyTakeaway": "The validator funding proposal is worth watching as a signal of where Ethereum governance is heading — but its implementation risks and power dynamics need extensive community debate before moving forward.",
      "howToImprove": "The proposal needs a formal EIP author, a security review of the proposed smart contract mechanism, and explicit modelling of validator economics at 3%, 4%, and 5% redirect levels before it can be seriously considered.",
      "vsPrevious": "First time covering Ethereum validator funding governance in this terminal."
    }
  ],
  "quickHits": [
    {"title": "Okratech + Predict Protocol Web3 partnership", "text": "Utility token project and decentralised prediction market platform partnering to expand DeFi capabilities. Early stage — no TVL deployed yet.", "url": "https://www.cointrust.com/market-news/okratech-token-and-predict-protocol-join-forces-to-advance-web3-innovation"},
    {"title": "Meteora, Kamino, Raydium top DeFi rankings", "text": "All three Solana-native DeFi protocols placed in Fortune's top 10 most influential DeFi projects. Solana DeFi TVL holding above $12B.", "url": "https://coinfomania.com/why-solana-just-ranked-3-in-fortunes-blockchain-list/"},
    {"title": "EIP process backlog growing", "text": "Ethereum EIP editors report a growing backlog of proposals as the ecosystem prepares for the next hard fork. Prioritisation decisions expected in Q3 2026.", "url": "https://ethereum.org/en/blog"}
  ]
}

}  # end BRIEFS

# ═══════════════════════════════════════════════════════════════
#  WRITE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def write_markdown(feature, brief):
    path = ROOT / "features" / feature / "output" / f"{brief['date']}.md"
    p_emoji = {"MAJOR": "🔴", "SIGNIFICANT": "🟠", "NOTABLE": "🟡", "FYI": "⚪"}
    lines = [f"# {feature.upper()} Brief — {brief['date']}\n",
             f"> {brief['indexHeadline']}\n", "\n---\n", "## Today's Signal\n"]
    for s in brief["topSignal"]:
        lines.append(f"- **{s['headline']}** — {s['detail']}")
    lines.append("\n---\n")
    for story in brief["stories"]:
        srcs = " | ".join(f"[{s['name']}]({s['url']})" for s in story["sources"])
        emoji = p_emoji.get(story["priority"], "⚪")
        lines += [f"\n## {story['id']}. {story['title']}\n",
                  f"**[{story['category']}]** — {emoji} {story['priority']}\n",
                  f"**Source:** {srcs}\n\n---\n",
                  f"\n### What happened\n{story['whatHappened']}\n",
                  "\n### What it can do"]
        for b in story["whatItCanDo"]: lines.append(f"- {b}")
        lines.append("\n### What's the catch")
        for b in story["whatsCatch"]: lines.append(f"- {b}")
        lines += [f"\n### Key takeaway\n> {story['keyTakeaway']}\n",
                  f"\n### How it can improve\n{story['howToImprove']}\n",
                  f"\n### vs. Previous\n> *{story['vsPrevious']}*\n\n---\n"]
    lines.append("\n## Quick Hits\n")
    for q in brief["quickHits"]:
        lines.append(f"- **{q['title']}**: {q['text']} — [Source]({q['url']})")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}")


def update_index(feature, brief):
    path = ROOT / "features" / feature / "output" / "index.md"
    existing = path.read_text(encoding="utf-8")
    entry = (f"## {brief['date']} — {brief['indexHeadline']}\n"
             f"{brief['indexSummary']}\n"
             f"[Full brief →]({brief['date']}.md)\n\n---\n\n")
    marker = "*Index starts"
    path.write_text(existing.replace(marker, entry + marker) if marker in existing
                    else existing + "\n" + entry, encoding="utf-8")
    print(f"  ✓ features/{feature}/output/index.md")


def archive(feature, brief):
    src  = ROOT / "features" / feature / "output" / f"{brief['date']}.md"
    dst  = ROOT / "features" / feature / "storage" / f"{brief['date']}.md"
    shutil.copy2(src, dst)
    print(f"  ✓ features/{feature}/storage/{brief['date']}.md")


def update_data_js(feature, brief):
    path = ROOT / "website" / f"data-{feature}.js"
    existing = path.read_text(encoding="utf-8")
    entry_json = json.dumps(brief, indent=4, ensure_ascii=False)
    indented   = "    " + entry_json.replace("\n", "\n    ")

    if '"briefs": []' in existing or '"briefs": [\n  ]' in existing or 'briefs: []' in existing:
        new = re.sub(r'"briefs":\s*\[\s*\]', f'"briefs": [\n{indented}\n  ]', existing)
    else:
        marker = "\n  ]\n};"
        if marker in existing:
            new = existing.replace(marker, f",\n{indented}{marker}")
        else:
            new = (f'window.LIM_DATA = window.LIM_DATA || {{}};\n'
                   f'window.LIM_DATA["{feature}"] = {{\n'
                   f'  lastUpdated: "{brief["date"]}",\n'
                   f'  briefs: [\n{indented}\n  ]\n}};\n')
            path.write_text(new, encoding="utf-8")
            print(f"  ✓ website/data-{feature}.js (rebuilt)")
            return
    new = re.sub(r'lastUpdated:\s*null', f'lastUpdated: "{brief["date"]}"', new)
    new = re.sub(r'lastUpdated:\s*"[^"]*"', f'lastUpdated: "{brief["date"]}"', new)
    path.write_text(new, encoding="utf-8")
    print(f"  ✓ website/data-{feature}.js")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{'='*56}\nLIM-AI TERMINAL — Initialising all features for {TODAY}\n{'='*56}\n")
    for feature, brief in BRIEFS.items():
        print(f"\n[ {feature.upper()} ]")
        write_markdown(feature, brief)
        update_index(feature, brief)
        archive(feature, brief)
        update_data_js(feature, brief)
    print(f"\n{'='*56}\nAll done — committing...\n{'='*56}\n")
