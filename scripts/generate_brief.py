#!/usr/bin/env python3
"""
LIM-AI Terminal — Daily Brief Generator
Runs via GitHub Actions at 9 AM every day (no desktop required).

Required environment variables:
  ANTHROPIC_API_KEY  — from console.anthropic.com
  TAVILY_API_KEY     — from app.tavily.com (free tier works)
"""

import anthropic
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

# ── Paths ───────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent
OUTPUT_DIR  = ROOT / "output"
STORAGE_DIR = ROOT / "storage"
WEBSITE_DIR = ROOT / "website"

TODAY = date.today().isoformat()

# ── Web search ──────────────────────────────────────────────────────
PRIORITY_DOMAINS = [
    "anthropic.com", "openai.com", "deepmind.google", "ai.meta.com",
    "x.ai", "mistral.ai", "ssi.inc", "thinkingmachines.ai",
    "huggingface.co", "llm-stats.com", "aireleasetracker.com",
    "buildfastwithai.com", "techcrunch.com", "theverge.com",
    "bloomberg.com", "therundown.ai", "venturebeat.com",
]

SEARCH_QUERIES = [
    f"AI model release announcement today {TODAY}",
    f"OpenAI Anthropic Google DeepMind Meta xAI news {TODAY}",
    f"AI safety policy regulation export control {TODAY}",
    f"AI startup funding acquisition {TODAY}",
    f"AI developer tools agents framework release {TODAY}",
    f"AI researcher scientist hire departure {TODAY}",
    f"Hugging Face papers trending {TODAY}",
    f"llm-stats buildfastwithai AI updates {TODAY}",
]

def search_news() -> list:
    if not TAVILY_AVAILABLE:
        return []
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    all_results, seen = [], set()
    for query in SEARCH_QUERIES:
        try:
            resp = tavily.search(
                query,
                max_results=6,
                search_depth="advanced",
                include_domains=PRIORITY_DOMAINS,
            )
            for r in resp.get("results", []):
                if r["url"] not in seen:
                    seen.add(r["url"])
                    all_results.append(r)
        except Exception as e:
            print(f"  Search error [{query[:40]}]: {e}")
    return all_results[:40]

# ── Tool schema for structured output ───────────────────────────────
WRITE_BRIEF_TOOL = {
    "name": "write_brief",
    "description": "Write the complete structured daily AI news brief.",
    "input_schema": {
        "type": "object",
        "required": ["date", "indexHeadline", "indexSummary", "stats",
                     "topSignal", "stories", "quickHits"],
        "properties": {
            "date": {"type": "string"},
            "indexHeadline": {"type": "string"},
            "indexSummary": {"type": "string"},
            "stats": {
                "type": "object",
                "required": ["total", "major", "significant", "notable"],
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
                    "required": ["headline", "detail"],
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
                    "required": ["id", "title", "category", "tags", "priority",
                                 "priorityLevel", "sources", "eventDate",
                                 "whatHappened", "whatItCanDo", "whatsCatch",
                                 "keyTakeaway", "howToImprove", "vsPrevious"],
                    "properties": {
                        "id":            {"type": "integer"},
                        "title":         {"type": "string"},
                        "category":      {"type": "string",
                                          "enum": ["MODEL","TOOL","RESEARCH","PRODUCT",
                                                   "BUSINESS","POLICY","PEOPLE","SAFETY"]},
                        "tags":          {"type": "array", "items": {"type": "string"}},
                        "priority":      {"type": "string",
                                          "enum": ["MAJOR","SIGNIFICANT","NOTABLE","FYI"]},
                        "priorityLevel": {"type": "integer", "enum": [1, 2, 3, 4]},
                        "sources": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["name", "url"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "url":  {"type": "string"},
                                },
                            },
                        },
                        "eventDate":    {"type": "string"},
                        "whatHappened": {"type": "string"},
                        "whatItCanDo":  {"type": "array", "items": {"type": "string"}},
                        "whatsCatch":   {"type": "array", "items": {"type": "string"}},
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
                    "required": ["title", "text", "url"],
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

SYSTEM_PROMPT = """You are the AI journalist behind LIM-AI TERMINAL — a personal Bloomberg Terminal for AI news.

Analyze the provided search results and produce a structured daily brief using the write_brief tool.

CATEGORIES: MODEL, TOOL, RESEARCH, PRODUCT, BUSINESS, POLICY, PEOPLE, SAFETY
PRIORITY: 1=MAJOR (frontier model / paradigm shift), 2=SIGNIFICANT (major tool/funding/person move), 3=NOTABLE (useful update), 4=FYI (minor)

RULES:
- Official company blogs always beat press reports for facts
- Label unverified: [press report — unconfirmed] or [unverified — social post]
- Focus on the LAST 24-48 HOURS only
- No hype — facts and implications only
- whatHappened: 2-4 sentences, pure facts
- whatItCanDo: 3-5 bullets on capabilities/implications (use ✓ framing)
- whatsCatch: 2-4 bullets on limits/risks/concerns
- keyTakeaway: exactly one sentence — the single most important thing
- howToImprove: 1-2 sentences of editorial (what's missing, what should come next)
- vsPrevious: compare to prior coverage if the topic recurred, else "First time covering this topic"
- topSignal: exactly 3 bullets — the 3 things that matter most today
- quickHits: one-liners for minor updates not worth a full story"""


def generate_brief(search_results: list) -> dict:
    client = anthropic.Anthropic()

    if search_results:
        context = "## SEARCH RESULTS\n\n" + "\n\n".join(
            f"[{i}] **{r.get('title','No title')}**\nURL: {r.get('url','')}\n{r.get('content','')[:700]}"
            for i, r in enumerate(search_results, 1)
        )
    else:
        context = ("No search results available. Generate the brief from your training knowledge "
                   "of recent AI events. Label every claim: [from training — verify independently].")

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[WRITE_BRIEF_TOOL],
        tool_choice={"type": "any"},
        messages=[{
            "role": "user",
            "content": f"Today: {TODAY}\n\n{context}\n\nGenerate today's AI news brief.",
        }],
    )

    for block in resp.content:
        if block.type == "tool_use" and block.name == "write_brief":
            return block.input

    raise ValueError("Claude did not call write_brief tool — check token budget or prompt")


# ── File writers ─────────────────────────────────────────────────────
def write_markdown(brief: dict) -> Path:
    p_emoji = {"MAJOR": "🔴", "SIGNIFICANT": "🟠", "NOTABLE": "🟡", "FYI": "⚪"}
    lines = [
        f"# AI News Brief — {brief['date']}\n",
        f"> **Today's count:** {brief['stats']['total']} items &nbsp;|&nbsp; "
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
    lines.append(f"\n\n---\n*Brief compiled by Claude · Archived at `storage/{brief['date']}.md`*\n")

    path = OUTPUT_DIR / f"{brief['date']}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}")
    return path


def update_index(brief: dict):
    path = OUTPUT_DIR / "index.md"
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


def archive(brief: dict, src: Path):
    dst = STORAGE_DIR / f"{brief['date']}.md"
    shutil.copy2(src, dst)
    print(f"  ✓ {dst.relative_to(ROOT)}")


def update_data_js(brief: dict):
    path = WEBSITE_DIR / "data.js"
    content = path.read_text(encoding="utf-8")

    # Serialize new entry and indent it
    entry_json = json.dumps(brief, indent=4, ensure_ascii=False)
    entry_indented = "    " + entry_json.replace("\n", "\n    ")

    # Find the closing of briefs array and insert before it
    marker = "\n  ]\n};"
    if marker not in content:
        raise ValueError("Insertion marker not found in data.js — check file structure")

    new_content = content.replace(marker, f",\n{entry_indented}{marker}")
    new_content = re.sub(r'lastUpdated: "[^"]*"', f'lastUpdated: "{brief["date"]}"', new_content)

    path.write_text(new_content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(ROOT)}")


def git_push(brief: dict) -> bool:
    date_str  = brief["date"]
    n_total   = brief["stats"]["total"]
    n_major   = brief["stats"]["major"]
    files = [
        f"output/{date_str}.md",
        "output/index.md",
        f"storage/{date_str}.md",
        "website/data.js",
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
        subprocess.run(
            ["git", "commit", "-m",
             f"Daily brief {date_str} — {n_total} stories, {n_major} major"],
            check=True, cwd=ROOT,
        )
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=ROOT)
        print("  ✓ Pushed — Netlify will redeploy in ~30s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Git push failed: {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────────
def main():
    sep = "=" * 52
    print(f"\n{sep}\nLIM-AI TERMINAL — Daily Brief\nDate: {TODAY}\n{sep}\n")

    print("1/5  Searching for today's AI news...")
    results = search_news()
    print(f"     Found {len(results)} articles\n")

    print("2/5  Generating brief with Claude...")
    brief = generate_brief(results)
    s = brief["stats"]
    print(f"     {s['total']} stories — {s['major']} major, {s['significant']} significant\n")

    print("3/5  Writing files...")
    md_path = write_markdown(brief)
    update_index(brief)
    archive(brief, md_path)
    update_data_js(brief)

    print("\n4/5  Pushing to GitHub...")
    pushed = git_push(brief)

    print(f"\n{sep}\nSUMMARY\n{sep}")
    print(f"Date     : {TODAY}")
    print(f"Stories  : {s['total']} total / {s['major']} major / {s['significant']} significant")
    print(f"Files    : output/{TODAY}.md, index.md, storage/{TODAY}.md, website/data.js")
    print(f"Git push : {'✓ success — Netlify redeploying' if pushed else '✗ failed (files written locally)'}")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
