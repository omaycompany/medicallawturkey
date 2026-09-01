"""Add maintained, contextual resource links to legacy editorial pages."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).parent

PAGES = {
    "arm-lift-malpractice.html": ("Arm lift legal resources", "glossary-medical-malpractice.html", "glossary-informed-consent.html", "cosmetic-surgery-complications-turkey-legal-rights.html"),
    "breast-reduction-malpractice.html": ("Breast reduction legal resources", "glossary-medical-malpractice.html", "glossary-causation.html", "breast-reduction-necrosis-case-study.html"),
    "dental-treatments-malpractice.html": ("Dental treatment legal resources", "glossary-medical-malpractice.html", "glossary-informed-consent.html", "clinic-blocked-me-after-surgery-legal-case-turkey.html"),
    "ear-lift-malpractice.html": ("Ear surgery legal resources", "glossary-medical-malpractice.html", "glossary-complication.html", "cosmetic-surgery-complications-turkey-legal-rights.html"),
    "eye-treatments.html": ("Eye treatment legal resources", "glossary-standard-of-care.html", "glossary-informed-consent.html", "patient-rights-and-informed-consent-in-turkey.html"),
    "eyelid-lift-malpractice.html": ("Eyelid surgery legal resources", "glossary-medical-malpractice.html", "glossary-post-operative-care.html", "cosmetic-surgery-complications-turkey-legal-rights.html"),
    "french-sling-malpractice.html": ("French sling legal resources", "glossary-medical-malpractice.html", "glossary-cosmetic-surgery-regulation.html", "patient-rights-and-informed-consent-in-turkey.html"),
    "gynecomastia-malpractice.html": ("Gynecomastia surgery legal resources", "glossary-medical-malpractice.html", "glossary-causation.html", "cosmetic-surgery-complications-turkey-legal-rights.html"),
    "hair-transplant-malpractice.html": ("Hair transplant legal resources", "glossary-medical-malpractice.html", "glossary-health-tourism.html", "hair-transplant-case-study.html"),
    "hollywood-smile-malpractice.html": ("Smile treatment legal resources", "glossary-consumer-law.html", "glossary-informed-consent.html", "dental-treatments-malpractice.html"),
    "in-vitro-fertilization-malpractice.html": ("IVF legal resources", "glossary-medical-malpractice.html", "glossary-privacy-of-medical-data.html", "patient-rights-and-informed-consent-in-turkey.html"),
    "leg-lift-malpractice.html": ("Leg lift legal resources", "glossary-medical-malpractice.html", "glossary-post-operative-care.html", "cosmetic-surgery-complications-turkey-legal-rights.html"),
    "liposuction-malpractice.html": ("Liposuction legal resources", "glossary-medical-malpractice.html", "glossary-complication.html", "liposuction-body-contouring-complications-turkey-legal-rights.html"),
    "non-surgical-malpractice.html": ("Non-surgical treatment legal resources", "glossary-standard-of-care.html", "glossary-off-label-drug-use.html", "patient-rights-and-informed-consent-in-turkey.html"),
    "breast-insurance-case-study.html": ("Related insurance and liability concepts", "breast-augmentation-malpractice.html", "glossary-malpractice-insurance.html", "glossary-causation.html"),
    "breast-reconstruction-asymmetry-case-study.html": ("Related reconstruction concepts", "breast-augmentation-malpractice.html", "glossary-causation.html", "glossary-non-pecuniary-damages.html"),
    "breast-reduction-necrosis-case-study.html": ("Related breast surgery concepts", "breast-reduction-malpractice.html", "glossary-post-operative-care.html", "glossary-causation.html"),
    "breast-reduction-revision-case-study.html": ("Related revision surgery concepts", "breast-reduction-malpractice.html", "glossary-medical-malpractice.html", "glossary-future-medical-expenses.html"),
    "cervical-disc-hernia-case-study.html": ("Related clinical and evidence concepts", "glossary-standard-of-care.html", "glossary-medical-board-report.html", "glossary-causation.html"),
    "face-neck-lift-case-study.html": ("Related face and neck surgery concepts", "glossary-cosmetic-surgery-regulation.html", "glossary-post-operative-care.html", "glossary-non-pecuniary-damages.html"),
    "face-scar-revision-case-study.html": ("Related scar revision concepts", "glossary-medical-malpractice.html", "glossary-future-medical-expenses.html", "glossary-causation.html"),
    "facelift-abdominal-liposuction-case-study.html": ("Related combined-procedure concepts", "liposuction-malpractice.html", "glossary-informed-consent.html", "glossary-causation.html"),
    "hair-dye-consumer-jurisdiction-case-study.html": ("Related consumer-law concepts", "glossary-consumer-law.html", "glossary-mediation.html", "glossary-pecuniary-damages.html"),
    "hair-transplant-case-study.html": ("Related hair transplant concepts", "hair-transplant-malpractice.html", "glossary-health-tourism.html", "glossary-causation.html"),
    "liposuction-arm-lift-case-study.html": ("Related body-contouring concepts", "liposuction-malpractice.html", "arm-lift-malpractice.html", "glossary-informed-consent.html"),
    "rhinoplasty-case-study.html": ("Related rhinoplasty concepts", "rhinoplasty-malpractice.html", "glossary-informed-consent.html", "glossary-causation.html"),
    "rhinoplasty-multiple-revision-conflict-case-study.html": ("Related revision rhinoplasty concepts", "rhinoplasty-malpractice.html", "glossary-future-medical-expenses.html", "glossary-post-operative-care.html"),
    "septorhinoplasty-infraorbital-fracture-case-study.html": ("Related septorhinoplasty concepts", "rhinoplasty-malpractice.html", "glossary-medical-board-report.html", "glossary-causation.html"),
    "medical-malpractice-and-compensation-liability-in-turkey.html": ("Continue with key liability concepts", "glossary-medical-malpractice.html", "glossary-pecuniary-damages.html", "glossary-non-pecuniary-damages.html"),
    "rhinoplasty-in-turkey-went-wrong-medical-malpractice.html": ("Continue with rhinoplasty guidance", "rhinoplasty-malpractice.html", "glossary-causation.html", "glossary-informed-consent.html"),
}


def label_for(target: str) -> str:
    return target.removesuffix(".html").removeprefix("glossary-").replace("-", " ").title()


def block(title: str, targets: tuple[str, str, str]) -> str:
    links = "".join(
        f'<a href="{html.escape(target, quote=True)}">{html.escape(label_for(target))}<span aria-hidden="true">→</span></a>'
        for target in targets
    )
    return f'''\n  <!-- SEO RELATED RESOURCES -->
  <section class="seo-related-resources" aria-label="Related legal resources">
    <div class="section-inner">
      <div class="section-eyebrow">Continue your research</div>
      <h2>{html.escape(title)}</h2>
      <p>Explore the connected legal concepts and practical guidance most relevant to this page.</p>
      <div class="seo-related-links">{links}</div>
    </div>
  </section>\n\n'''


def update() -> int:
    changed = 0
    for filename, (title, *targets) in PAGES.items():
        path = ROOT / filename
        content = path.read_text(encoding="utf-8")
        if "<!-- SEO RELATED RESOURCES -->" in content:
            continue
        revised, replacements = re.subn(
            r"(?=<footer\b)", block(title, tuple(targets)), content, count=1, flags=re.IGNORECASE
        )
        if replacements != 1:
            raise ValueError(f"Could not locate footer in {filename}")
        path.write_text(revised, encoding="utf-8")
        changed += 1
    return changed


if __name__ == "__main__":
    print(f"Added contextual resources to {update()} pages.")
