#!/usr/bin/env python3
"""
LIM-AI Terminal — Daily Brief Generator
Usage: python generate_brief.py --feature ai-news

Features: ai-news, global-fin-news, global-news, indo-fin-news,
          indo-news, crypto-news, blockchain-news

Required environment variables:
  ANTHROPIC_API_KEY
  TAVILY_API_KEY
"""

import anthropic
import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("Warning: tavily-python not installed, search will be skipped")

ROOT    = Path(__file__).parent.parent
TODAY   = date.today().isoformat()

# ═══════════════════════════════════════════════════════════════
#  FEATURE CONFIGS
# ═══════════════════════════════════════════════════════════════
FEATURES = {
    "ai-news": {
        "name": "AI News",
        "categories": ["MODEL","TOOL","RESEARCH","PRODUCT","BUSINESS","POLICY","PEOPLE","SAFETY"],
        "domains": [
            "anthropic.com","openai.com","deepmind.google","ai.meta.com",
            "x.ai","mistral.ai","ssi.inc","thinkingmachines.ai",
            "huggingface.co","llm-stats.com","aireleasetracker.com",
            "buildfastwithai.com","techcrunch.com","theverge.com",
            "bloomberg.com","therundown.ai","venturebeat.com",
        ],
        "queries": [
            "AI model release announcement today {date}",
            "OpenAI Anthropic Google DeepMind Meta xAI news {date}",
            "AI safety policy regulation export control {date}",
            "AI startup funding acquisition {date}",
            "AI developer tools agents framework release {date}",
            "AI researcher scientist hire departure {date}",
            "Hugging Face papers trending {date}",
            "llm-stats buildfastwithai AI updates {date}",
        ],
        "system_prompt": """You are the AI journalist behind LIM-AI TERMINAL — a personal Bloomberg Terminal for AI news.

Analyze the search results and produce a structured daily brief using the write_brief tool.

CATEGORIES: MODEL, TOOL, RESEARCH, PRODUCT, BUSINESS, POLICY, PEOPLE, SAFETY
PRIORITY: 1=MAJOR (frontier model/paradigm shift), 2=SIGNIFICANT (major tool/funding/move), 3=NOTABLE, 4=FYI

RULES:
- Official company blogs beat press reports for facts
- Label unverified: [press report — unconfirmed]
- Focus on the LAST 24-48 HOURS only
- No hype — facts and implications only
- whatHappened: 2-4 sentences, pure facts
- whatItCanDo: 3-5 bullets on capabilities/implications
- whatsCatch: 2-4 bullets on limits/risks/concerns
- keyTakeaway: exactly one sentence
- howToImprove: 1-2 sentences of editorial
- vsPrevious: compare to prior coverage or "First time covering this topic"
- topSignal: exactly 3 bullets — the 3 things that matter most today
- quickHits: one-liners for minor updates""",
    },

    "global-fin-news": {
        "name": "Global Finance",
        "categories": ["MARKETS","MACRO","CENTRAL-BANK","EARNINGS","COMMODITIES","FOREX","IPO","POLICY"],
        "domains": [
            "reuters.com","bloomberg.com","ft.com","wsj.com",
            "cnbc.com","marketwatch.com","seekingalpha.com",
            "imf.org","worldbank.org","federalreserve.gov","ecb.europa.eu",
            "apnews.com","economist.com",
        ],
        "queries": [
            "global financial markets stocks bonds {date}",
            "Federal Reserve ECB central bank interest rate {date}",
            "S&P 500 NYSE Nasdaq major market move {date}",
            "oil gold commodity prices {date}",
            "EUR USD JPY currency forex {date}",
            "global economy GDP inflation recession {date}",
            "major earnings report corporate results {date}",
            "IMF World Bank global finance {date}",
        ],
        "system_prompt": """You are the financial journalist behind LIM-AI TERMINAL — a Bloomberg Terminal for global finance news.

Analyze the search results and produce a structured daily brief using the write_brief tool.

CATEGORIES: MARKETS, MACRO, CENTRAL-BANK, EARNINGS, COMMODITIES, FOREX, IPO, POLICY
PRIORITY: 1=MAJOR (rate decision/market crash/>3% move/systemic risk), 2=SIGNIFICANT (major earnings/central bank speech), 3=NOTABLE, 4=FYI

RULES:
- Wire services (Reuters, AP) and official central bank releases take precedence
- Always include specific numbers: percentages, basis points, prices
- Label estimates: [estimate] or [analyst forecast]
- Focus on the LAST 24-48 HOURS only
- whatHappened: 2-4 sentences with specific data points and figures
- whatItCanDo: 3-5 bullets on market/economic implications
- whatsCatch: 2-4 bullets on risks, uncertainty, dissenting views
- keyTakeaway: exactly one sentence — the most important market/economic implication
- howToImprove: what data or policy action would change the picture
- vsPrevious: trend context or "First time covering this topic"
- topSignal: exactly 3 bullets — the 3 most market-moving things today
- quickHits: minor data releases, routine moves""",
    },

    "global-news": {
        "name": "Global News",
        "categories": ["CONFLICT","POLITICS","DIPLOMACY","CLIMATE","HEALTH","SOCIETY","ECONOMY","TECH"],
        "domains": [
            "reuters.com","apnews.com","bbc.com","aljazeera.com",
            "theguardian.com","nytimes.com","afp.com","dw.com",
            "foreignpolicy.com","economist.com","politico.com",
            "scmp.com","euronews.com",
        ],
        "queries": [
            "world news breaking today {date}",
            "geopolitics conflict military {date}",
            "election government political crisis {date}",
            "climate environment disaster {date}",
            "UN NATO G7 G20 international summit {date}",
            "diplomacy sanctions treaty {date}",
            "global health WHO pandemic {date}",
            "humanitarian crisis migration {date}",
        ],
        "system_prompt": """You are the international correspondent behind LIM-AI TERMINAL — a Bloomberg Terminal for global news.

Analyze the search results and produce a structured daily brief using the write_brief tool.

CATEGORIES: CONFLICT, POLITICS, DIPLOMACY, CLIMATE, HEALTH, SOCIETY, ECONOMY, TECH
PRIORITY: 1=MAJOR (armed conflict escalation/government collapse/global emergency), 2=SIGNIFICANT (election result/diplomatic shift), 3=NOTABLE, 4=FYI

RULES:
- Wire services (Reuters, AP, AFP) take precedence for facts
- Always give geographic context (country, region)
- Avoid editorial bias — present multiple perspectives where relevant
- Focus on the LAST 24-48 HOURS only
- whatHappened: 2-4 sentences, factual, with location and key actors
- whatItCanDo: 3-5 bullets on implications and consequences
- whatsCatch: 2-4 bullets on uncertainty, counterpoints, risks
- keyTakeaway: exactly one sentence
- howToImprove: what developments to watch
- vsPrevious: how this fits into ongoing story or "First time covering this topic"
- topSignal: exactly 3 bullets — most globally significant things today
- quickHits: minor international updates""",
    },

    "indo-fin-news": {
        "name": "Indonesia Finance",
        "categories": ["IDX","BANKING","RUPIAH","COMMODITIES","STARTUP","REGULATION","MACRO","SOE"],
        "domains": [
            "kontan.co.id","bisnis.com","cnbcindonesia.com",
            "idx.co.id","bi.go.id","ojk.go.id","kemenkeu.go.id",
            "investordaily.id","katadata.co.id","thejakartapost.com",
            "reuters.com","bloomberg.com","techinasia.com",
        ],
        "queries": [
            "Indonesia IHSG stock market {date}",
            "Bank Indonesia BI rate rupiah IDR {date}",
            "OJK regulation Indonesia finance {date}",
            "Indonesia CPO coal nickel export commodity {date}",
            "Indonesia startup unicorn funding {date}",
            "Indonesia GDP inflation economy {date}",
            "BUMN state-owned enterprise Indonesia {date}",
            "Indonesia IPO IDX listed company {date}",
        ],
        "system_prompt": """You are the financial journalist behind LIM-AI TERMINAL — a Bloomberg Terminal for Indonesia finance news.

Analyze the search results and produce a structured daily brief using the write_brief tool.
All output must be in English.

CATEGORIES: IDX, BANKING, RUPIAH, COMMODITIES, STARTUP, REGULATION, MACRO, SOE
PRIORITY: 1=MAJOR (BI rate decision/IHSG crash/systemic event), 2=SIGNIFICANT (major IPO/OJK ruling/rupiah move), 3=NOTABLE, 4=FYI

RULES:
- Official sources (BI, OJK, IDX, Kemenkeu) take precedence
- Always include specific numbers in IDR or USD, percentages, basis points
- Context: Indonesia is a $1.4T economy, IHSG has ~900 listed companies, BI targets 2.5-4.5% inflation
- Focus on the LAST 24-48 HOURS only
- All output in English
- whatHappened: 2-4 sentences with specific Indonesian market data
- whatItCanDo: 3-5 bullets on implications for investors/economy
- whatsCatch: 2-4 bullets on risks, political economy context
- keyTakeaway: exactly one sentence
- howToImprove: what policy or market development would help
- vsPrevious: trend context or "First time covering this topic"
- topSignal: exactly 3 bullets — most important for Indonesia finance today
- quickHits: minor Indonesian economic updates""",
    },

    "indo-news": {
        "name": "Indonesia News",
        "categories": ["POLITICS","ECONOMY","SOCIAL","REGION","ENVIRONMENT","CULTURE","LAW","HEALTH"],
        "domains": [
            "kompas.com","detik.com","tempo.co","antaranews.com",
            "republika.co.id","kumparan.com","thejakartapost.com",
            "cnnindonesia.com","tirto.id","beritasatu.com",
            "reuters.com",
        ],
        "queries": [
            "Indonesia news today {date}",
            "Indonesia politics government {date}",
            "Indonesia economy investment {date}",
            "Indonesia disaster bencana {date}",
            "Indonesia law court KPK corruption {date}",
            "Indonesia Papua Kalimantan regional {date}",
            "Indonesia social health education {date}",
            "Indonesia environment forest {date}",
        ],
        "system_prompt": """You are the correspondent behind LIM-AI TERMINAL — a Bloomberg Terminal for Indonesia news.

Analyze the search results and produce a structured daily brief using the write_brief tool.
All output must be in English.

CATEGORIES: POLITICS, ECONOMY, SOCIAL, REGION, ENVIRONMENT, CULTURE, LAW, HEALTH
PRIORITY: 1=MAJOR (national crisis/major disaster/government change), 2=SIGNIFICANT (major policy/legal case/regional disaster), 3=NOTABLE, 4=FYI

RULES:
- Kompas, Antara, The Jakarta Post are most authoritative for Indonesian news
- Always give geographic context within Indonesia
- Translate key Indonesian terms in parentheses when necessary
- Focus on the LAST 24-48 HOURS only
- All output in English
- whatHappened: 2-4 sentences, factual
- whatItCanDo: 3-5 bullets on implications for Indonesia
- whatsCatch: 2-4 bullets on context, risks, complications
- keyTakeaway: exactly one sentence
- howToImprove: what to watch next
- vsPrevious: ongoing story context or "First time covering this topic"
- topSignal: exactly 3 bullets — most significant for Indonesia today
- quickHits: minor Indonesian updates""",
    },

    "crypto-news": {
        "name": "Cryptocurrency",
        "categories": ["BTC","ETH","ALTCOIN","DEFI","REGULATION","EXCHANGE","MACRO","HACK"],
        "domains": [
            "coindesk.com","cointelegraph.com","decrypt.co","theblock.co",
            "coingecko.com","coinmarketcap.com","messari.io",
            "bitcoinmagazine.com","cryptoslate.com","blockworks.co",
            "glassnode.com","dlnews.com","unchainedcrypto.com",
        ],
        "queries": [
            "Bitcoin BTC price news {date}",
            "Ethereum ETH upgrade staking {date}",
            "cryptocurrency regulation SEC CFTC {date}",
            "DeFi protocol hack exploit {date}",
            "Binance Coinbase Kraken exchange news {date}",
            "altcoin Solana XRP major move {date}",
            "crypto macro institutional bitcoin ETF {date}",
            "blockchain stablecoin USDT USDC {date}",
        ],
        "system_prompt": """You are the crypto journalist behind LIM-AI TERMINAL — a Bloomberg Terminal for cryptocurrency news.

Analyze the search results and produce a structured daily brief using the write_brief tool.

CATEGORIES: BTC, ETH, ALTCOIN, DEFI, REGULATION, EXCHANGE, MACRO, HACK
PRIORITY: 1=MAJOR (BTC/ETH >10% move/hack >$50M/landmark regulation), 2=SIGNIFICANT (major exchange event/ETF ruling/altcoin >20%), 3=NOTABLE, 4=FYI

RULES:
- CoinDesk, The Block, Messari are most authoritative
- Always include price levels, percentage moves, and TVL figures where relevant
- For hacks: always state exact dollar amount lost and protocol affected
- Focus on the LAST 24-48 HOURS only
- Flag unconfirmed: [unconfirmed] or [on-chain data — verify]
- whatHappened: 2-4 sentences with specific prices/amounts
- whatItCanDo: 3-5 bullets on market/ecosystem implications
- whatsCatch: 2-4 bullets on risks, centralization concerns, regulatory overhang
- keyTakeaway: exactly one sentence
- howToImprove: what would strengthen the thesis or fix the problem
- vsPrevious: trend context or "First time covering this topic"
- topSignal: exactly 3 bullets — most market-moving crypto events today
- quickHits: minor price moves, small protocol updates""",
    },

    "blockchain-news": {
        "name": "Blockchain",
        "categories": ["PROTOCOL","DEFI","NFT","DAO","INFRA","SECURITY","REGULATION","VENTURE"],
        "domains": [
            "theblock.co","messari.io","defillama.com",
            "ethereum.org","solana.com","polkadot.network",
            "a16zcrypto.com","paradigm.xyz","multicoin.capital",
            "banklesshq.com","hackernoon.com","mirror.xyz",
            "alchemy.com","dune.com",
        ],
        "queries": [
            "Ethereum protocol upgrade EIP {date}",
            "blockchain DeFi protocol TVL {date}",
            "DAO governance vote proposal {date}",
            "blockchain security exploit audit {date}",
            "Layer 2 rollup zkEVM {date}",
            "Web3 infrastructure RPC bridge {date}",
            "blockchain venture funding round {date}",
            "NFT market protocol royalty {date}",
        ],
        "system_prompt": """You are the blockchain researcher behind LIM-AI TERMINAL — a Bloomberg Terminal for blockchain and Web3 news.

Analyze the search results and produce a structured daily brief using the write_brief tool.

CATEGORIES: PROTOCOL, DEFI, NFT, DAO, INFRA, SECURITY, REGULATION, VENTURE
PRIORITY: 1=MAJOR (major protocol upgrade/critical exploit >$100M/landmark DAO vote), 2=SIGNIFICANT (protocol milestone/large grant/medium hack), 3=NOTABLE, 4=FYI

RULES:
- Official protocol blogs and Messari/The Block research are most authoritative
- Always include TVL figures, protocol names, chain context
- For security events: state exact amount, protocol, attack vector if known
- Focus on the LAST 24-48 HOURS only
- whatHappened: 2-4 sentences with technical and financial context
- whatItCanDo: 3-5 bullets on ecosystem and developer implications
- whatsCatch: 2-4 bullets on centralization, security, adoption risks
- keyTakeaway: exactly one sentence
- howToImprove: what technical or governance improvement would help
- vsPrevious: trend context or "First time covering this topic"
- topSignal: exactly 3 bullets — most significant blockchain developments today
- quickHits: minor protocol updates, small DAO votes""",
    },
}


# ═══════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════
def search_news(cfg: dict) -> list:
    if not TAVILY_AVAILABLE:
        return []
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    all_results, seen = [], set()
    for query_template in cfg["queries"]:
        query = query_template.format(date=TODAY)
        try:
            resp = tavily.search(
                query,
                max_results=6,
                search_depth="advanced",
                include_domains=cfg["domains"],
            )
            for r in resp.get("results", []):
                if r["url"] not in seen:
                    seen.add(r["url"])
                    all_results.append(r)
        except Exception as e:
            print(f"  Search error [{query[:40]}]: {e}")
    return all_results[:40]


# ═══════════════════════════════════════════════════════════════
#  CLAUDE TOOL SCHEMA  (built per-feature for correct categories)
# ═══════════════════════════════════════════════════════════════
def build_tool(cfg: dict) -> dict:
    return {
        "name": "write_brief",
        "description": f"Write the complete structured daily {cfg['name']} brief.",
        "input_schema": {
            "type": "object",
            "required": ["date","indexHeadline","indexSummary","stats",
                         "topSignal","stories","quickHits"],
            "properties": {
                "date": {"type": "string"},
                "indexHeadline": {"type": "string"},
                "indexSummary": {"type": "string"},
                "stats": {
                    "type": "object",
                    "required": ["total","major","significant","notable"],
                    "properties": {
                        "total":       {"type": "integer"},
                        "major":       {"type": "integer"},
                        "significant": {"type": "integer"},
                        "notable":     {"type": "integer"},
                    },
                },
                "topSignal": {
                    "type": "array", "minItems": 3, "maxItems": 3,
                    "items": {
                        "type": "object",
                        "required": ["headline","detail"],
                        "properties": {
                            "headline": {"type": "string"},
                            "detail":   {"type": "string"},
                        },
                    },
                },
                "stories": {
                    "type": "array", "minItems": 3, "maxItems": 7,
                    "items": {
                        "type": "object",
                        "required": ["id","title","category","tags","priority",
                                     "priorityLevel","sources","eventDate",
                                     "whatHappened","whatItCanDo","whatsCatch",
                                     "keyTakeaway","howToImprove","vsPrevious"],
                        "properties": {
                            "id":            {"type": "integer"},
                            "title":         {"type": "string"},
                            "category":      {"type": "string",
                                              "enum": cfg["categories"]},
                            "tags":          {"type": "array",
                                              "items": {"type": "string"}},
                            "priority":      {"type": "string",
                                              "enum": ["MAJOR","SIGNIFICANT","NOTABLE","FYI"]},
                            "priorityLevel": {"type": "integer", "enum": [1,2,3,4]},
                            "sources": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["name","url"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "url":  {"type": "string"},
                                    },
                                },
                            },
                            "eventDate":    {"type": "string"},
                            "whatHappened": {"type": "string"},
                            "whatItCanDo":  {"type": "array",
                                             "items": {"type": "string"}},
                            "whatsCatch":   {"type": "array",
                                             "items": {"type": "string"}},
                            "keyTakeaway":  {"type": "string"},
                            "howToImprove": {"type": "string"},
                            "vsPrevious":   {"type": "string"},
                        },
                    },
                },
                "quickHits": {
                    "type": "array", "minItems": 2, "maxItems": 8,
                    "items": {
                        "type": "object",
                        "required": ["title","text","url"],
                        "properties": {
                            "title": {"type": "string"},
                            "text":  {"type": "string"},
                            "url":   {"type": "string"},
                        },
                    },
                },
            },
        },
    }


# ═══════════════════════════════════════════════════════════════
#  GENERATE
# ═══════════════════════════════════════════════════════════════
def generate_brief(cfg: dict, search_results: list) -> dict:
    client = anthropic.Anthropic()

    if search_results:
        context = "## SEARCH RESULTS\n\n" + "\n\n".join(
            f"[{i}] **{r.get('title','No title')}**\nURL: {r.get('url','')}\n{r.get('content','')[:700]}"
            for i, r in enumerate(search_results, 1)
        )
    else:
        context = (
            "No search results available. Generate the brief from your training knowledge. "
            "Label every claim: [from training — verify independently]."
        )

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=cfg["system_prompt"],
        tools=[build_tool(cfg)],
        tool_choice={"type": "any"},
        messages=[{
            "role": "user",
            "content": f"Today: {TODAY}\n\n{context}\n\nGenerate today's {cfg['name']} brief.",
        }],
    )

    for block in resp.content:
        if block.type == "tool_use" and block.name == "write_brief":
            return block.input

    raise ValueError("Claude did not call write_brief — check token budget or prompt")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITERS
# ═══════════════════════════════════════════════════════════════
def write_markdown(brief: dict, feature: str) -> Path:
    output_dir = ROOT / "features" / feature / "output"
    p_emoji = {"MAJOR": "🔴", "SIGNIFICANT": "🟠", "NOTABLE": "🟡", "FYI": "⚪"}
    lines = [
        f"# {FEATURES[feature]['name']} Brief — {brief['date']}\n",
        f"> **Stories:** {brief['stats']['total']} &nbsp;|&nbsp; "
        f"**Top signal:** {brief['topSignal'][0]['headline']}\n",
        "\n---\n",
        "## Today's Signal\n",
    ]
    for s in brief["topSignal"]:
        lines.append(f"- **{s['headline']}** — {s['detail']}")
    lines.append("\n---\n")

    for story in brief["stories"]:
        tags = " ".join(f"`#{t}`" for t in story["tags"])
        srcs = " &nbsp;|&nbsp; ".join(
            f"[{s['name']}]({s['url']})" for s in story["sources"]
        )
        emoji = p_emoji.get(story["priority"], "⚪")
        lines += [
            f"\n## {story['id']}. {story['title']}\n",
            f"**[{story['category']}]** {tags} — {emoji} {story['priority']}\n",
            f"**Source:** {srcs} &nbsp;|&nbsp; **Date:** {story['eventDate']}\n",
            "\n---\n",
            f"\n### What happened\n{story['whatHappened']}\n",
            "\n### What it can do",
        ]
        for b in story["whatItCanDo"]:
            lines.append(f"- {b}")
        lines.append("\n### What's the catch")
        for b in story["whatsCatch"]:
            lines.append(f"- {b}")
        lines += [
            f"\n### Key takeaway\n> {story['keyTakeaway']}\n",
            f"\n### How it can improve\n{story['howToImprove']}\n",
            f"\n### vs. Previous coverage\n> *{story['vsPrevious']}*\n",
            "\n---\n",
        ]

    lines.append("\n## Quick Hits\n")
    for q in brief["quickHits"]:
        lines.append(f"- **{q['title']}**: {q['text']} — [Source]({q['url']})")
    lines.append(f"\n\n---\n*Brief compiled by Claude · {feature} · `storage/{brief['date']}.md`*\n")

    path = output_dir / f"{brief['date']}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}")
    return path


def update_index(brief: dict, feature: str):
    path = ROOT / "features" / feature / "output" / "index.md"
    existing = path.read_text(encoding="utf-8")
    entry = (
        f"## {brief['date']} — {brief['indexHeadline']}\n"
        f"{brief['indexSummary']}\n"
        f"[Full brief →]({brief['date']}.md)\n\n---\n\n"
    )
    marker = "*Index starts"
    if marker in existing:
        new_content = existing.replace(marker, entry + marker)
    else:
        new_content = existing + "\n" + entry
    path.write_text(new_content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}")


def archive(brief: dict, feature: str, src: Path):
    dst = ROOT / "features" / feature / "storage" / f"{brief['date']}.md"
    shutil.copy2(src, dst)
    print(f"  ✓ {dst.relative_to(ROOT)}")


def update_data_js(brief: dict, feature: str):
    path = ROOT / "website" / f"data-{feature}.js"
    content = path.read_text(encoding="utf-8")

    entry_json = json.dumps(brief, indent=4, ensure_ascii=False)
    entry_indented = "    " + entry_json.replace("\n", "\n    ")

    # Insert new brief before the closing of briefs array
    marker = "\n  ]\n};"
    if marker not in content:
        # File is empty/placeholder — rebuild from scratch
        new_content = (
            f'window.LIM_DATA = window.LIM_DATA || {{}};\n'
            f'window.LIM_DATA["{feature}"] = {{\n'
            f'  lastUpdated: "{brief["date"]}",\n'
            f'  briefs: [\n'
            f'{entry_indented}\n'
            f'  ]\n'
            f'}};\n'
        )
    else:
        # Append to existing briefs array
        if '"briefs": []' in content or '"briefs": [\n  ]' in content:
            # First entry — replace empty array
            new_content = re.sub(
                r'"briefs":\s*\[\s*\]',
                f'"briefs": [\n{entry_indented}\n  ]',
                content,
            )
        else:
            new_content = content.replace(marker, f",\n{entry_indented}{marker}")
        new_content = re.sub(
            r'lastUpdated:\s*["\']?[^,\n"\']*["\']?',
            f'lastUpdated: "{brief["date"]}"',
            new_content,
        )

    path.write_text(new_content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}")


def git_push(brief: dict, feature: str) -> bool:
    date_str = brief["date"]
    files = [
        f"features/{feature}/output/{date_str}.md",
        f"features/{feature}/output/index.md",
        f"features/{feature}/storage/{date_str}.md",
        f"website/data-{feature}.js",
    ]
    try:
        subprocess.run(["git", "add"] + files, check=True, cwd=ROOT)
        result = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            cwd=ROOT, capture_output=True
        )
        if result.returncode == 0:
            print("  ✓ No changes to commit (brief already exists for today)")
            return True
        s = brief["stats"]
        subprocess.run(
            ["git", "commit", "-m",
             f"[{feature}] Daily brief {date_str} — {s['total']} stories, {s['major']} major [bot]"],
            check=True, cwd=ROOT,
        )
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=ROOT)
        print("  ✓ Pushed — Netlify redeploying in ~30s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Git push failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="LIM-AI Terminal — Daily Brief Generator")
    parser.add_argument(
        "--feature", required=True,
        choices=list(FEATURES.keys()),
        help="Which news category to generate"
    )
    args = parser.parse_args()

    feature = args.feature
    cfg = FEATURES[feature]

    sep = "=" * 56
    print(f"\n{sep}\nLIM-AI TERMINAL — {cfg['name']} Brief\nDate: {TODAY}\n{sep}\n")

    print(f"1/4  Searching {cfg['name']} news...")
    results = search_news(cfg)
    print(f"     Found {len(results)} articles\n")

    print(f"2/4  Generating brief with Claude...")
    brief = generate_brief(cfg, results)
    s = brief["stats"]
    print(f"     {s['total']} stories — {s['major']} major, {s['significant']} significant\n")

    print("3/4  Writing files...")
    md_path = write_markdown(brief, feature)
    update_index(brief, feature)
    archive(brief, feature, md_path)
    update_data_js(brief, feature)

    print("\n4/4  Pushing to GitHub...")
    pushed = git_push(brief, feature)

    print(f"\n{sep}\nSUMMARY\n{sep}")
    print(f"Feature  : {feature}")
    print(f"Date     : {TODAY}")
    print(f"Stories  : {s['total']} total / {s['major']} major / {s['significant']} significant")
    print(f"Git push : {'✓ success' if pushed else '✗ failed (files written locally)'}")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
