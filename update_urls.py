"""Normalise production and homepage URLs in generated static files."""

from pathlib import Path


def replace_urls(directory: str | Path = ".") -> list[Path]:
    root = Path(directory)
    updated: list[Path] = []
    source_script = Path(__file__).resolve()
    non_www_site = "https://" + "medicallawturkey.com"
    production_site = "https://www." + "medicallawturkey.com"
    for filepath in sorted(root.rglob("*")):
        if filepath.suffix.lower() not in {".html", ".xml", ".json", ".py"}:
            continue
        if filepath.resolve() == source_script:
            continue
        content = filepath.read_text(encoding="utf-8")
        normalised = content.replace(non_www_site, production_site)
        if filepath.suffix.lower() in {".html", ".py"}:
            normalised = normalised.replace('href="index.html#', 'href="/#')
            normalised = normalised.replace('href="index.html"', 'href="/"')
        if normalised != content:
            filepath.write_text(normalised, encoding="utf-8")
            updated.append(filepath)
    return updated


if __name__ == "__main__":
    changed = replace_urls()
    print(f"Normalised URLs in {len(changed)} files.")
