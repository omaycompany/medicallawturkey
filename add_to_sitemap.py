"""Rebuild sitemap.xml from canonical root-level HTML URLs."""

from pathlib import Path
from xml.etree import ElementTree as ET

from add_contextual_links import PAGES as CONTEXTUAL_PAGES


SITE = "https://www.medicallawturkey.com"
UPDATED = "2026-09-01"
ROOT = Path(__file__).parent
SITEMAP = ROOT / "sitemap.xml"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def existing_lastmods() -> dict[str, str]:
    if not SITEMAP.exists():
        return {}
    tree = ET.parse(SITEMAP)
    return {
        node.findtext(f"{{{NS}}}loc", ""): node.findtext(f"{{{NS}}}lastmod", "")
        for node in tree.findall(f"{{{NS}}}url")
    }


def canonical_for(page: Path) -> str:
    return f"{SITE}/" if page.name == "index.html" else f"{SITE}/{page.name}"


def rebuild() -> int:
    prior = existing_lastmods()
    pages = sorted(ROOT.glob("*.html"), key=lambda path: (path.name != "index.html", path.name))
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}urlset")
    for page in pages:
        canonical = canonical_for(page)
        url = ET.SubElement(root, f"{{{NS}}}url")
        ET.SubElement(url, f"{{{NS}}}loc").text = canonical
        changed_content = page.name.startswith("glossary-") or page.name in CONTEXTUAL_PAGES or page.name in {
            "index.html",
            "cookie-policy.html", "kvkk-gdpr-notice.html", "privacy-policy.html", "terms-of-use.html"
        }
        lastmod = UPDATED if changed_content else prior.get(canonical, UPDATED)
        ET.SubElement(url, f"{{{NS}}}lastmod").text = lastmod
    ET.indent(root, space="  ")
    SITEMAP.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(root, encoding="unicode")
        + "\n",
        encoding="utf-8",
    )
    return len(pages)


if __name__ == "__main__":
    print(f"Sitemap rebuilt with {rebuild()} canonical URLs.")
