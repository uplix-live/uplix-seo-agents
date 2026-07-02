"""
advertools_utils.py — Utilitaires SEO via advertools
Wrapper pour les fonctions advertools les plus utiles en audit SEO.

Usage:
    python scripts/advertools_utils.py sitemap https://example.fr/sitemap.xml
    python scripts/advertools_utils.py robots https://example.fr/robots.txt
    python scripts/advertools_utils.py crawl https://example.fr --max-pages 500
    python scripts/advertools_utils.py logs server.log
    python scripts/advertools_utils.py kw "assurance auto,assurance moto" --modifier "pas cher,devis"
"""

import argparse
import sys
from pathlib import Path

# Fix Windows cp1252 encoding issues
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import advertools as adv
    import pandas as pd
except ImportError as e:
    print(f"ERROR: {e}\nInstaller: pip install advertools pandas")
    sys.exit(1)


# ── Sitemap ───────────────────────────────────────────────────────────────────

def cmd_sitemap(url: str, output: str = None):
    """Parse un sitemap XML (y compris sitemap index) en DataFrame."""
    print(f"Analyse sitemap : {url}")
    try:
        df = adv.sitemap_to_df(url)
        print(f"  {len(df)} URLs trouvées")
        print(f"\nColonnes disponibles : {list(df.columns)}")
        print(f"\nAperçu :\n{df.head(10).to_string()}")

        if output:
            df.to_csv(output, index=False, encoding="utf-8-sig")
            print(f"\nExporté -> {output}")
        return df
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return None


# ── Robots.txt ────────────────────────────────────────────────────────────────

def cmd_robots(url: str, output: str = None):
    """Parse un robots.txt en DataFrame structuré."""
    if not url.endswith("robots.txt"):
        url = url.rstrip("/") + "/robots.txt"
    print(f"Analyse robots.txt : {url}")
    try:
        df = adv.robotstxt_to_df(url)
        print(f"\n{df.to_string()}")

        # Résumé utile
        print("\n--- RÉSUMÉ ---")
        user_agents = df["user_agent"].unique()
        print(f"User-agents : {list(user_agents)}")
        disallowed = df[df["directive"] == "Disallow"]["content"].tolist()
        print(f"Disallow ({len(disallowed)}) : {disallowed[:10]}")
        sitemaps = df[df["directive"] == "Sitemap"]["content"].tolist()
        print(f"Sitemaps ({len(sitemaps)}) : {sitemaps}")

        if output:
            df.to_csv(output, index=False, encoding="utf-8-sig")
            print(f"\nExporté -> {output}")
        return df
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return None


# ── Crawl Scrapy ──────────────────────────────────────────────────────────────

def cmd_crawl(url: str, max_pages: int = 500, output: str = None):
    """
    Crawl léger via advertools (Scrapy).
    Extrait : status, title, meta_desc, h1, canonical, links, etc.
    """
    out_path = output or f"crawl_{url.replace('https://','').replace('http://','').replace('/','_')[:30]}.jl"
    print(f"Crawl : {url} (max {max_pages} pages)")
    print(f"Sortie : {out_path}")
    try:
        adv.crawl(
            url,
            out_path,
            follow_links=True,
            custom_settings={
                "CLOSESPIDER_PAGECOUNT": max_pages,
                "CONCURRENT_REQUESTS": 5,
                "DOWNLOAD_DELAY": 0.5,
            }
        )
        # Lire et afficher résumé
        df = pd.read_json(out_path, lines=True)
        print(f"\n  {len(df)} pages crawlées")
        if "status" in df.columns:
            print(f"  Statuts HTTP : {df['status'].value_counts().to_dict()}")
        return df
    except Exception as e:
        print(f"Erreur crawl : {e}", file=sys.stderr)
        return None


# ── Analyse logs serveur ──────────────────────────────────────────────────────

def cmd_logs(log_file: str, output: str = None, log_format: str = "common"):
    """
    Parse des logs serveur Apache/Nginx.
    Formats supportés : 'common', 'combined', 'nginx'
    Utile pour détecter les crawls Googlebot, erreurs fréquentes, etc.
    """
    print(f"Analyse logs : {log_file} (format: {log_format})")
    try:
        df = adv.logs_to_df(log_file, output or log_file + ".jl", log_format)
        print(f"\n  {len(df)} requêtes analysées")
        if "status" in df.columns:
            print(f"  Statuts : {df['status'].value_counts().head(5).to_dict()}")
        if "crawlers" in df.columns or "user_agent" in df.columns:
            ua_col = "crawlers" if "crawlers" in df.columns else "user_agent"
            bots = df[df[ua_col].str.contains("Googlebot|Bingbot|bot|spider", case=False, na=False)]
            print(f"  Requêtes bots : {len(bots)} ({len(bots)/len(df)*100:.1f}%)")
        return df
    except Exception as e:
        print(f"Erreur logs : {e}", file=sys.stderr)
        return None


# ── Génération de mots-clés ───────────────────────────────────────────────────

def cmd_kw(seeds: str, modifiers: str = None, output: str = None):
    """
    Génère des combinaisons de mots-clés (seeds × modifiers).
    Utile pour construire des listes longue traîne.
    """
    seed_list = [s.strip() for s in seeds.split(",")]
    modifier_list = [m.strip() for m in modifiers.split(",")] if modifiers else []

    print(f"Génération KW : {len(seed_list)} seeds × {len(modifier_list)} modifiers")
    try:
        df = adv.kw_generate(seed_list, modifier_list or [""])
        print(f"  {len(df)} combinaisons générées")
        print(f"\nAperçu :\n{df.head(20).to_string()}")

        if output:
            df.to_csv(output, index=False, encoding="utf-8-sig")
            print(f"\nExporté -> {output}")
        return df
    except Exception as e:
        print(f"Erreur kw_generate : {e}", file=sys.stderr)
        return None


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Utilitaires SEO via advertools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commandes:
  sitemap URL      Parse sitemap XML -> DataFrame
  robots URL       Parse robots.txt -> analyse Disallow/Sitemap
  crawl URL        Crawl léger Scrapy (title, meta, h1, links, status)
  logs FILE        Analyse logs serveur (Googlebot, erreurs, fréquences)
  kw "seeds"       Génère combinaisons de mots-clés

Exemples:
  python scripts/advertools_utils.py sitemap https://maaf.fr/sitemap.xml -o sitemap.csv
  python scripts/advertools_utils.py robots https://maaf.fr
  python scripts/advertools_utils.py crawl https://maaf.fr --max-pages 200
  python scripts/advertools_utils.py kw "assurance auto,assurance moto" --modifier "pas cher,devis,en ligne"
        """
    )

    sub = parser.add_subparsers(dest="cmd")

    # sitemap
    p = sub.add_parser("sitemap")
    p.add_argument("url")
    p.add_argument("-o", "--output")

    # robots
    p = sub.add_parser("robots")
    p.add_argument("url")
    p.add_argument("-o", "--output")

    # crawl
    p = sub.add_parser("crawl")
    p.add_argument("url")
    p.add_argument("--max-pages", type=int, default=500)
    p.add_argument("-o", "--output")

    # logs
    p = sub.add_parser("logs")
    p.add_argument("file")
    p.add_argument("--format", default="common", choices=["common", "combined", "nginx"])
    p.add_argument("-o", "--output")

    # kw
    p = sub.add_parser("kw")
    p.add_argument("seeds", help="Seeds séparés par virgule")
    p.add_argument("--modifier", help="Modificateurs séparés par virgule")
    p.add_argument("-o", "--output")

    args, _ = parser.parse_known_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    if args.cmd == "sitemap":
        cmd_sitemap(args.url, args.output)
    elif args.cmd == "robots":
        cmd_robots(args.url, args.output)
    elif args.cmd == "crawl":
        cmd_crawl(args.url, args.max_pages, args.output)
    elif args.cmd == "logs":
        cmd_logs(args.file, args.output, args.format)
    elif args.cmd == "kw":
        cmd_kw(args.seeds, args.modifier, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
