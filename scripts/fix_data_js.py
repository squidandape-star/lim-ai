#!/usr/bin/env python3
"""Fix: rewrite the 6 non-ai-news data JS files that ended up with briefs: []"""

import sys, json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# Import brief data from init_briefs
from init_briefs import BRIEFS

SKIP = {"ai-news"}   # already correct

for feature, brief in BRIEFS.items():
    if feature in SKIP:
        print(f"  skip {feature} (already ok)")
        continue

    entry  = json.dumps(brief, ensure_ascii=False, indent=4)
    indented = "    " + entry.replace("\n", "\n    ")
    content = (
        f'window.LIM_DATA = window.LIM_DATA || {{}};\n'
        f'window.LIM_DATA["{feature}"] = {{\n'
        f'  lastUpdated: "{brief["date"]}",\n'
        f'  briefs: [\n'
        f'{indented}\n'
        f'  ]\n'
        f'}};\n'
    )

    path = ROOT / "website" / f"data-{feature}.js"
    path.write_text(content, encoding="utf-8")
    print(f"  OK  website/data-{feature}.js  ({len(content)} bytes)")

print("\nDone.")
