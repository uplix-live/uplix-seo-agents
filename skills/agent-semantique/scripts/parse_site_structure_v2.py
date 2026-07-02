import json
from collections import defaultdict

filepath = "C:/Users/evaux/.claude/projects/c--Users-evaux-E-vauxmoret-Dropbox-Emmanuel-de-Vauxmoret-Developement-IA-Claude-Code-Consultant-SEO-IA/2fba088b-6125-4555-a910-99fb437c3e62/tool-results/mcp-haloscan-get_keywords_site_structure-1772442085162.txt"
outpath = "C:/Users/evaux/E.vauxmoret Dropbox/Emmanuel de Vauxmoret/Developement IA/Claude-Code/Consultant SEO IA/haloscan_structure_full.txt"

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Parse inner JSON
try:
    inner = json.loads(data[1]["text"])
except (IndexError, KeyError, TypeError):
    inner = json.loads(data[0]["text"])

table = inner.get("table", [])
outliers = inner.get("outliers", [])
cannibalisation = inner.get("cannibalisation", [])
seed = inner.get("seed", "")

lines = []
lines.append(f"SEED KEYWORD: {seed}")
lines.append(f"TOTAL KEYWORDS IN TABLE: {len(table)}")
lines.append(f"TOTAL OUTLIERS: {len(outliers)}")
lines.append(f"TOTAL CANNIBALIZATION ENTRIES: {len(cannibalisation)}")
lines.append("")

# Analyze table: group by V1 (top silo), then V2, then V3
v1_groups = defaultdict(list)
for row in table:
    v1 = row.get("V1", "")
    v1_groups[v1].append(row)

lines.append(f"NUMBER OF V1 SILOS: {len(v1_groups)}")
lines.append("=" * 80)
lines.append("")

# Print first 5 rows to understand structure
lines.append("SAMPLE TABLE ROW (first entry):")
if table:
    for k, v in table[0].items():
        lines.append(f"  {k}: {v}")
lines.append("")

# Group by V1 silo
for v1_name, rows in sorted(v1_groups.items(), key=lambda x: -len(x[1])):
    # Sub-group by V2
    v2_groups = defaultdict(list)
    for row in rows:
        v2 = row.get("V2", "")
        v2_groups[v2].append(row)

    kw_list = [r.get("keyword", "") for r in rows]

    lines.append(f"### SILO V1: {v1_name} ###")
    lines.append(f"  Total keywords: {len(rows)}")
    lines.append(f"  Sous-clusters V2: {len(v2_groups)}")

    for v2_name, v2_rows in sorted(v2_groups.items(), key=lambda x: -len(x[1])):
        # Sub-group by V3
        v3_groups = defaultdict(list)
        for row in v2_rows:
            v3 = row.get("V3", "")
            v3_groups[v3].append(row)

        lines.append(f"  -- V2: {v2_name} ({len(v2_rows)} KWs)")

        for v3_name, v3_rows in sorted(v3_groups.items(), key=lambda x: -len(x[1])):
            if v3_name != v2_name:  # Only show V3 if different from V2
                lines.append(f"     -- V3: {v3_name} ({len(v3_rows)} KWs)")
            for row in v3_rows[:10]:
                kw = row.get("keyword", "")
                article = row.get("article", "")
                allintitle = row.get("allintitle", "")
                lines.append(f"        - {kw} | article: {article} | allintitle: {allintitle}")
            if len(v3_rows) > 10:
                lines.append(f"        ... et {len(v3_rows)-10} autres")

    lines.append("")

# Outliers
lines.append("=" * 80)
lines.append("OUTLIERS (mots-cles hors structure)")
lines.append("=" * 80)
for o in outliers:
    lines.append(f"  - {o.get('keyword', '')}")
lines.append("")

# Cannibalization
lines.append("=" * 80)
lines.append("CANNIBALISATION DETECTEE")
lines.append("=" * 80)
canni_groups = defaultdict(list)
for c in cannibalisation:
    grp = c.get("groupe", "")
    canni_groups[grp].append(c.get("keyword", ""))

for grp, kws in sorted(canni_groups.items(), key=lambda x: -len(x[1])):
    lines.append(f"  Groupe: {grp} ({len(kws)} KWs)")
    for kw in kws:
        lines.append(f"    - {kw}")
lines.append("")

with open(outpath, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"Written {len(lines)} lines to {outpath}")
