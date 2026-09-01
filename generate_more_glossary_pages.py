"""Compatibility entry point for the unified glossary generator."""

from glossary_renderer import render_pages
from glossary_terms import TERMS


if __name__ == "__main__":
    pages = render_pages(TERMS)
    print(f"Generated {len(pages)} source-backed glossary pages.")
