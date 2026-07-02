import json
from collections import defaultdict

filepath = "C:/Users/evaux/.claude/projects/c--Users-evaux-E-vauxmoret-Dropbox-Emmanuel-de-Vauxmoret-Developement-IA-Claude-Code-Consultant-SEO-IA/2fba088b-6125-4555-a910-99fb437c3e62/tool-results/mcp-haloscan-get_keywords_site_structure-1772442085162.txt"
outpath = "C:/Users/evaux/E.vauxmoret Dropbox/Emmanuel de Vauxmoret/Developement IA/Claude-Code/Consultant SEO IA/haloscan_volumes.txt"

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

try:
    inner = json.loads(data[1]["text"])
except (IndexError, KeyError, TypeError):
    inner = json.loads(data[0]["text"])

table = inner.get("table", [])

lines = []

# Volume summary by V1 silo
v1_data = defaultdict(lambda: {"kws": 0, "total_vol": 0, "total_cpc": 0.0, "keywords": []})

for row in table:
    v1 = row.get("V1", "NA")
    vol = row.get("volume", 0) or 0
    cpc = row.get("cpc", 0) or 0
    kw = row.get("keyword", "")

    v1_data[v1]["kws"] += 1
    v1_data[v1]["total_vol"] += vol
    v1_data[v1]["total_cpc"] += cpc
    v1_data[v1]["keywords"].append({
        "keyword": kw,
        "volume": vol,
        "cpc": cpc,
        "competition": row.get("competition", 0) or 0,
        "kvi": row.get("kvi", ""),
        "article": row.get("article", ""),
        "V2": row.get("V2", ""),
        "V3": row.get("V3", ""),
    })

lines.append("VOLUMES PAR SILO V1 (tries par volume decroissant)")
lines.append("=" * 100)

for v1_name, data_v1 in sorted(v1_data.items(), key=lambda x: -x[1]["total_vol"]):
    avg_cpc = data_v1["total_cpc"] / data_v1["kws"] if data_v1["kws"] > 0 else 0
    lines.append(f"\n### {v1_name} ###")
    lines.append(f"  KWs: {data_v1['kws']} | Volume total: {data_v1['total_vol']} | CPC moyen: {avg_cpc:.2f} EUR")

    # Sort keywords by volume
    sorted_kws = sorted(data_v1["keywords"], key=lambda x: -x["volume"])
    for kw_data in sorted_kws[:20]:
        lines.append(f"    {kw_data['keyword']:<50} vol={kw_data['volume']:>6} | cpc={kw_data['cpc']:.2f} | comp={kw_data['competition']:.2f} | kvi={kw_data['kvi']}")
    if len(sorted_kws) > 20:
        lines.append(f"    ... et {len(sorted_kws)-20} autres")

# Top 30 keywords overall by volume
lines.append("\n\n" + "=" * 100)
lines.append("TOP 30 KEYWORDS PAR VOLUME (tous silos confondus)")
lines.append("=" * 100)

all_kws = []
for row in table:
    all_kws.append(row)
all_kws.sort(key=lambda x: -(x.get("volume", 0) or 0))

for i, row in enumerate(all_kws[:30], 1):
    kw = row.get("keyword", "")
    vol = row.get("volume", 0) or 0
    cpc = row.get("cpc", 0) or 0
    comp = row.get("competition", 0) or 0
    v1 = row.get("V1", "")
    lines.append(f"  {i:>2}. {kw:<50} vol={vol:>6} | cpc={cpc:.2f} | silo={v1}")

with open(outpath, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"Written to {outpath}")
