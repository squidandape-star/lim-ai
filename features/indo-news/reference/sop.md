# AI News Terminal — Standard Operating Procedure

> Mission: Track, summarize, and compound AI knowledge daily. Think Bloomberg Terminal for AI — fast, structured, signal over noise.

---

## 1. Purpose

Every day, Claude pulls AI news from a curated list of sources (see `creator.md`), synthesizes the key developments, and saves a structured daily brief. Over time, this compounds into a personal knowledge base that helps you adapt faster than the market.

---

## 2. Daily Run — Step by Step

### Step 1: Source Collection
- Pull latest from all sources in `creator.md`
- Priority order: Official company announcements → Top researchers → Curated aggregators → General tech press
- Time window: Last 24 hours (or since last run)

### Step 2: Filter & Triage
- Apply categories from `categorization.md`
- Drop duplicates (same story covered by multiple outlets — keep the primary source)
- Flag anything marked `BREAKING` or `MAJOR RELEASE` for top placement

### Step 3: Write Daily Brief
- File: `output/YYYY-MM-DD.md`
- Follow the template in `example-output.md` exactly
- One section per distinct news item
- Always end with a "Today's Signal" summary (3 bullets max — the 3 things that matter most)

### Step 4: Update Index
- Add one-liner entry to `output/index.md` (30–50 words max)
- Format: `## YYYY-MM-DD — [headline theme]`

### Step 5: Archive to Storage
- Copy the completed `output/YYYY-MM-DD.md` into `storage/YYYY-MM-DD.md`
- Never delete from storage — this is the compounding knowledge base

### Step 6: Update Website
- Open `website/data.js`
- **Prepend** the new brief object into the `briefs: [...]` array (newest first at the end, since `init()` loads `briefs[briefs.length - 1]` as the default)
- Match the existing JSON structure exactly — date, indexHeadline, indexSummary, stats, topSignal, stories[], quickHits[]
- Each story needs: id, title, category, tags, priority, priorityLevel (1=MAJOR 2=SIG 3=NOTABLE), sources[], eventDate, whatHappened, whatItCanDo[], whatsCatch[], keyTakeaway, howToImprove, vsPrevious

### Step 7: Distribute
- Send to Telegram (daily digest channel)
- Website auto-refreshes from `website/data.js` — no deploy needed if self-hosted

---

## 3. Quality Rules

| Rule | Why |
|------|-----|
| Primary sources over secondary | Avoid telephone game distortion |
| Date-stamp every claim | AI moves fast — last week's news is stale |
| Compare to previous entries | The delta matters more than the absolute state |
| No hype, only facts + implications | You're adapting, not cheerleading |
| Flag uncertainty explicitly | "unconfirmed" / "leaked" must be labeled |

---

## 4. File Structure

```
lim-ai/
├── reference/
│   ├── ai-news-sop.md         ← this file
│   ├── creator.md             ← source list
│   ├── categorization.md      ← how to tag/sort news
│   └── example-output.md      ← output template
├── output/
│   ├── index.md               ← running one-liner log
│   └── YYYY-MM-DD.md          ← daily briefs
└── storage/
    └── YYYY-MM-DD.md          ← permanent archive (never delete)
```

---

## 5. Telegram & Website Integration

- **Telegram**: Send a condensed version — headline + 3 key takeaways + link to full brief
- **Website**: Post the full `YYYY-MM-DD.md` content, rendered as a page on the Bloomberg-style dashboard
- Both should go out by **9:00 AM local time** each day

---

## 6. How to Start a Daily Run

Tell Claude:
> "Run today's AI news brief."

Claude will follow this SOP, pull from `creator.md`, apply `categorization.md`, write to `output/YYYY-MM-DD.md`, update `output/index.md`, and copy to `storage/`.
