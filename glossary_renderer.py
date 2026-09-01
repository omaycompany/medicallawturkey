"""Render source-backed, buyer-facing Medical Law Türkiye glossary pages."""

from __future__ import annotations

import html
import hashlib
import json
import re
from pathlib import Path

SITE = "https://www.medicallawturkey.com"
UPDATED_ISO = "2026-09-01"
UPDATED_LABEL = "1 September 2026"

SOURCES = {
    "tbk": {
        "title": "Turkish Code of Obligations, Law No. 6098",
        "publisher": "Grand National Assembly of Türkiye",
        "url": "https://www.tbmm.gov.tr/Yasama/Kanun/f72877bd-e416-037b-e050-007f01005610",
    },
    "civil": {
        "title": "Turkish Civil Code, Law No. 4721",
        "publisher": "Grand National Assembly of Türkiye",
        "url": "https://www.tbmm.gov.tr/Yasama/Kanun/f72877bd-78c3-037b-e050-007f01005610",
    },
    "penal": {
        "title": "Turkish Penal Code, Law No. 5237",
        "publisher": "Grand National Assembly of Türkiye",
        "url": "https://www.tbmm.gov.tr/Yasama/Kanun/F72877BD-AA54-037B-E050-007F01005610",
    },
    "patient_rights": {
        "title": "Patient Rights Regulation",
        "publisher": "Republic of Türkiye Ministry of Health",
        "url": "https://www.saglik.gov.tr/TR-10461/hasta-haklari-yonetmeligi.html",
    },
    "consumer": {
        "title": "Consumer Protection Law No. 6502 and secondary legislation",
        "publisher": "Republic of Türkiye Ministry of Trade",
        "url": "https://ticaret.gov.tr/tuketici/mevzuat/6502-sayili-tuketicinin-korunmasi-mevzuati",
    },
    "mediation": {
        "title": "Mediation legislation and regulations",
        "publisher": "Republic of Türkiye Ministry of Justice",
        "url": "https://higm.adalet.gov.tr/Home/SayfaDetay/kanun",
    },
    "yargitay": {
        "title": "Official Court of Cassation decision search",
        "publisher": "Court of Cassation of Türkiye",
        "url": "https://karararama.yargitay.gov.tr/",
    },
    "atk": {
        "title": "Adli Tıp Kurumu official information",
        "publisher": "Forensic Medicine Institute",
        "url": "https://www.atk.gov.tr/",
    },
    "tourism": {
        "title": "International Health Tourism Regulation",
        "publisher": "Republic of Türkiye Ministry of Health",
        "url": "https://turkogludh.saglik.gov.tr/TR-461253/uluslararasi-saglik-turizmi-yonetmeligi.html",
    },
    "kvkk": {
        "title": "Personal Data Protection Law No. 6698",
        "publisher": "Personal Data Protection Authority",
        "url": "https://www.kvkk.gov.tr/Icerik/6649/Personal-Data-Protection-Law",
    },
    "ethics": {
        "title": "Rules of Medical Professional Ethics",
        "publisher": "Turkish Medical Association",
        "url": "https://www.ttb.org.tr/kutuphane/h_etikkural.pdf",
    },
    "device": {
        "title": "Medical device regulatory information",
        "publisher": "Turkish Medicines and Medical Devices Agency",
        "url": "https://www.titck.gov.tr/faaliyetalanlari/tibbicihaz",
    },
    "medicine": {
        "title": "Rational use of medicines",
        "publisher": "Turkish Medicines and Medical Devices Agency",
        "url": "https://akilciilac.titck.gov.tr/home/nedenakilcilackullanimi/",
    },
    "insurance": {
        "title": "Compulsory medical malpractice liability insurance general conditions",
        "publisher": "Insurance and Private Pension Regulation and Supervision Agency",
        "url": "https://www.seddk.gov.tr/tr/mevzuat/sigortacilik/genel-sartlar",
    },
    "sgk": {
        "title": "General Health Insurance official information",
        "publisher": "Social Security Institution",
        "url": "https://www.sgk.gov.tr/Content/Post/742c02df-68e1-422c-a387-fa2e4326b015/Genel-Saglik-Sigortasi-nedir-2023-01-25-11-25-46",
    },
}

CATEGORY_SOURCES = {
    "framework": ["patient_rights", "tbk", "consumer"],
    "liability": ["tbk", "yargitay", "patient_rights"],
    "consent": ["patient_rights", "ethics", "yargitay"],
    "procedure": ["mediation", "yargitay", "patient_rights"],
    "damages": ["tbk", "yargitay", "civil"],
    "clinical": ["patient_rights", "ethics", "yargitay"],
    "tourism": ["tourism", "consumer", "patient_rights"],
    "evidence": ["atk", "yargitay", "patient_rights"],
    "consumer": ["consumer", "mediation", "tbk"],
    "criminal": ["penal", "atk", "yargitay"],
    "product": ["device", "consumer", "tbk"],
    "insurance": ["insurance", "sgk", "tbk"],
    "contract": ["tbk", "consumer", "yargitay"],
    "rights": ["patient_rights", "kvkk", "ethics"],
    "data": ["kvkk", "patient_rights", "tourism"],
}

CATEGORY_CONTEXT = {
    "framework": "Because {term} crosses institutional and legal boundaries, the first reliable step is classification. Provider status, facility type and the patient's route into treatment determine which official rules should be read together. This prevents a broad health-law label from hiding the specific right, duty or remedy that actually needs attention.",
    "liability": "For {term}, breach, responsibility, causation and loss should be kept as separate propositions. A persuasive review explains which person or organisation owed which duty, identifies the conduct in question, and then connects that conduct to the particular harm through records and appropriate expertise.",
    "consent": "A consent analysis concerning {term} is a process review. It examines understandable information, capacity, voluntariness, timing and documentation. The patient's language, urgency and individual circumstances may be important, so a signature should never be used as a substitute for the underlying conversation.",
    "procedure": "Procedure can determine whether a legally sound point about {term} is heard at all. Parties, forum, authority, deadline and pre-action requirements must be identified from current official rules. Early chronology work also protects evidence and prevents inconsistent accounts later.",
    "damages": "A damages review involving {term} begins with proof and causation, not a promised figure. Past and future losses are separated, supporting assumptions are stated, and payments from employers, insurers or public bodies are recorded so that the calculation can be tested.",
    "clinical": "Clinical review of {term} should be anchored to the information available at the time. The relevant specialty, procedure, patient risk and response to changing symptoms matter. A later bad outcome can prompt investigation, but it does not replace an evidence-based comparison with the professional standard.",
    "tourism": "Cross-border treatment adds actors and documents to {term}: the healthcare provider, any intermediary, travel arrangements, translations, advertising and international payment flows. Mapping each promise and payment to the correct legal entity is essential before choosing a remedy.",
    "evidence": "A report associated with {term} is only as useful as its mandate, inputs and reasoning. The issuing body's authority, the specialties involved, the questions asked and the complete record supplied should all be visible. Conclusions should then be compared with the issue the court or decision-maker must resolve.",
    "consumer": "Whether {term} engages consumer procedure depends on the parties and transaction. The provider's commercial identity, payment recipient, service promise and public or private status should be confirmed before selecting a forum or treating mediation as mandatory.",
    "criminal": "Criminal assessment of {term} uses offence elements and criminal procedure, not the civil standard for compensation. Original evidence must be preserved and factual language used carefully because investigation, expert review and charging decisions belong to the competent authorities.",
    "product": "Product analysis of {term} separates the device itself from selection, storage, implantation, instructions and follow-up. Traceability is critical: without the exact model, lot or serial information, it may be difficult to test a recall, warning, defect or supply-chain theory.",
    "insurance": "Insurance questions around {term} require the policy and governing rules, not assumptions about available funds. Coverage, insured status, notification, defence and liability are distinct. Public-benefit or recourse questions may also sit outside the patient's own damages claim.",
    "contract": "Contract analysis of {term} starts with the actual undertaking. Written terms, advertisements, professional duties and mandatory protections are read together, then compared with performance. The label attached to an aesthetic or therapeutic service cannot decide the legal classification by itself.",
    "rights": "Patient-rights review of {term} connects the event to a current official provision, the responsible institution and an available complaint or legal route. Respect for autonomy, dignity and accessible communication should remain visible throughout the evidence rather than appearing only as general slogans.",
    "data": "Data review of {term} maps the controller, health-information categories, purpose, legal basis, recipients, retention and any international transfer. The privacy route should be kept distinct from clinical negligence while preserving evidence relevant to both.",
}


def slugify(value: str) -> str:
    value = value.lower().replace("ı", "i")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def pick(slug: str, section: str, options: list[str]) -> str:
    """Choose stable copy variants without relying on Python's randomised hash."""
    digest = hashlib.sha256(f"{slug}:{section}".encode("utf-8")).digest()
    return options[int.from_bytes(digest[:4], "big") % len(options)]


def page_specific_copy(item: dict, slug: str, related_titles: list[str]) -> dict[str, str]:
    term = item["term"]
    lower = term.lower()
    evidence = item["evidence"]

    bridge = pick(slug, "bridge", [
        "A useful first review therefore asks who did what, when it happened and which part of the record can verify it.",
        "The practical task is to convert that definition into a dated account of the treatment, the responsible actors and the outcome under review.",
        "That distinction matters because a label alone cannot identify the provider, prove the disputed conduct or connect it to a loss.",
        "In practice, the term becomes legally meaningful only after the treatment pathway and the documents supporting each step have been identified.",
        "A careful assessment keeps the legal concept separate from the patient's understandable concern, then tests both against the same chronology.",
        "The starting point is not an assumption about liability but a structured comparison between the allegation, the contemporaneous record and the applicable rule.",
        "For an international patient, this also means confirming the legal identity of every clinic, practitioner and intermediary involved in the treatment journey.",
        "The definition should guide evidence collection, not predetermine the result; disputed facts still need records, context and appropriate expertise.",
        "Its role is to frame the right question for review while leaving room for the medical evidence and current Turkish rules to determine the answer.",
        "A reliable analysis narrows the concept to the particular procedure, promise, decision or omission shown by the patient's own documents.",
    ])

    official_bridge = pick(slug, "official", [
        "The three official references cited below provide the verification path for this page. They must be read in their current form and then matched to the provider and facts.",
        "Primary materials, rather than summaries by commercial publishers, should anchor the legal analysis. Their relevance still depends on the treatment setting and remedy pursued.",
        "The applicable source may change with the facility, party or legal route. The cited authorities are therefore a starting set for fact-specific research, not a substitute for it.",
        "Current legislation and official institutional material should be checked before relying on a procedural or substantive proposition. The links below permit that direct check.",
        "Official text is especially important where translations or online summaries compress legal qualifications. Each cited rule must still be applied to the evidence in the individual matter.",
        "A sound opinion traces each legal proposition back to an authority responsible for the rule or procedure. This page uses only that kind of primary or institutional source.",
        "The legal framework is not selected by keyword alone. Provider status, contractual chain and requested remedy decide how the cited official materials interact.",
        "Direct consultation of official publications reduces the risk of relying on outdated commentary. Dates, amendments and the scope of each rule remain part of the review.",
        "The sources below come directly from public authorities or the recognised professional body relevant to the issue, allowing the current wording to be checked at source.",
        "Verification should move from the patient's chronology to the current official rule and back to the supporting record. The cited links are provided for that purpose.",
    ])

    evidence_intro = pick(slug, "evidence", [
        "The checklist below targets the records most likely to clarify this issue. Collecting them does not mean that a viable claim has already been established.",
        "An efficient first review begins with the material capable of confirming dates, decisions and responsible parties. The following items deserve early attention.",
        "Evidence should answer the legal question, not merely increase the volume of the file. These four items create a focused starting bundle.",
        "Where accounts differ, contemporaneous records can narrow the dispute. Preserve the following material in its original form wherever possible.",
        "A structured file allows the medical and legal questions to be tested separately. Start with these records before reconstructing events from memory.",
        "The value of a document depends on its date, source and completeness. The following evidence categories usually help establish those features.",
        "Before drawing conclusions, build a small auditable record of the event. These items are selected for their connection to this particular concept.",
        "The first evidence pass should reveal both what is known and what remains missing. Use the following list to organise that pass.",
        "Original files, full message threads and identifiable issuers are preferable to cropped screenshots or later summaries. Prioritise the material below.",
        "A lawyer or independent expert can review the matter more accurately when the key propositions are paired with the following dated evidence.",
    ])

    international_one = pick(slug, "international-one", [
        "If the patient has returned home, begin by preserving {e0} and {e1}. Keep the original-language versions, original digital files and any later translation as separate items so their source remains clear.",
        "Cross-border review is easier when {e0} is collected alongside {e1}. Record the clinic's full legal name, the payment recipient and every intermediary instead of relying only on a brand shown in advertising.",
        "Before messages or portals disappear, export {e0} and secure {e1}. A translation can assist the review, but it should not replace the original Turkish or other source document.",
        "Distance does not prevent an initial assessment, but missing identifiers do. Preserve {e0}, link it to {e1}, and note which person or entity created each record.",
        "An overseas patient should organise {e0} first, then compare it with {e1}. File names, dates and metadata should remain intact because they may later help authenticate the chronology.",
        "For a remote instruction, a concise timeline supported by {e0} and {e1} is more useful than a long undated narrative. Identify the treating facility and payment chain at the same time.",
        "International treatment files often split across email, messaging apps and patient portals. Consolidate {e0} with {e1} without editing or overwriting the originals.",
        "After travel home, request missing records in writing and retain {e0} together with {e1}. Note whether a clinic, doctor or facilitator answered each request.",
        "Remote evidence collection should preserve provenance. Keep {e0} in its native format, attach {e1} to the relevant event, and store translations as clearly labelled working copies.",
        "The first cross-border bundle should make provider identity and timing visible. {e0} and {e1} are practical anchors for that bundle, subject to the facts of the case.",
    ]).format(e0=evidence[0], e1=evidence[1])

    international_two = pick(slug, "international-two", [
        "Urgent medical needs should be addressed independently of any legal strategy. Before signing a refund, waiver or settlement, obtain advice about its effect on {term} and preserve {e2} plus {e3}.",
        "Do not delay appropriate follow-up care while assembling a legal file. Once safe, add {e2} and {e3}, then ask counsel to confirm the forum, parties and any time-sensitive step.",
        "A complaint sent too early can omit a party or fix an inaccurate chronology. Secure {e2} and {e3} first, while obtaining independent treatment whenever health requires it.",
        "Any proposed refund document should be read before acceptance because its scope may extend beyond payment. The review should also include {e2} and {e3} in connection with {term}.",
        "Separate recovery decisions from compensation decisions: seek suitable care, retain {e2}, preserve {e3}, and then obtain advice about the correct Turkish route.",
        "Avoid promising a deadline or outcome in correspondence with the provider. A lawyer can use {e2} and {e3} to evaluate {term} while keeping medical priorities first.",
        "Where continuing symptoms exist, independent clinical care comes before document strategy. The later legal review should incorporate {e2} and {e3} without assuming that either proves liability.",
        "A remote review can identify gaps, but it cannot safely replace missing medical evidence. Preserve {e2} and {e3} before negotiating or accepting language that may affect rights.",
        "The appropriate remedy may depend on facts not visible in advertising or a single report. Add {e2} and {e3}, protect immediate health needs and obtain individual Turkish advice.",
        "Communications should remain factual while the evidence is incomplete. Keep {e2} and {e3}, and have any release or settlement proposal checked before it is signed.",
    ]).format(e2=evidence[2], e3=evidence[3], term=term)

    source_note = pick(slug, "source-note", [
        "These links let readers verify the governing material at its source. Publication dates, amendments and case-specific scope should be checked again when advice is given.",
        "The citations are supplied for direct verification. Official wording and procedure can change, so the current version remains controlling for a later assessment.",
        "Each reference comes from a Turkish public authority or recognised professional body. Its current text and factual relevance should be confirmed before use.",
        "Use the linked publications to test the statements above against the source itself. An official link does not remove the need for fact-specific interpretation.",
        "The list is deliberately limited to primary and official institutional material. Current amendments and the competence of the issuing body remain important.",
        "Readers can follow these citations without passing through a commercial summary. Check the live publication and the date relevant to the treatment.",
        "Official materials support verification, but they do not decide disputed facts. The record and the legal route must still be analysed together.",
        "These authorities form a focused research trail for this concept. They should be supplemented only where the facts or procedural route require another official source.",
        "The source list is limited to direct official and institutional publications. Confirm the latest wording before relying on any rule described on this page.",
        "Direct citations improve transparency for patients and reviewing professionals. They remain general references until applied to a specific provider, event and remedy.",
    ])

    review_intro = pick(slug, "review", [
        "A disciplined review should connect {term} to {e0}, then test that account against {e1} before addressing responsibility or loss.",
        "The analysis becomes easier to audit when {e0} establishes the timeline and {e1} is used to check the disputed proposition about {term}.",
        "Begin with the event shown by {e0}; use {e1} to identify gaps, competing explanations and the expert question that actually needs an answer.",
        "For {term}, the sequence below keeps medical safety, document provenance, party identity and the choice of legal route in the correct order.",
        "A reliable opinion is built in stages. {e0} and {e1} should be linked to the relevant actor before a breach, causation or remedy is proposed.",
        "Reviewing {term} requires more than a conclusion in a report. The underlying {e0} and {e1} should support the reasoning step by step.",
        "Use {e0} to anchor what happened and {e1} to test how it was recorded. Only then should the possible legal consequences of {term} be classified.",
        "The following order reduces avoidable errors: protect the patient, preserve {e0}, verify {e1}, identify the actors and select the competent route.",
        "A complete file should show how {e0} relates to {e1}. That relationship helps separate a clinical concern from a legally supportable point about {term}.",
        "The legal route should be the result of the evidence review, not its starting assumption. {e0} and {e1} provide two concrete checks on that discipline.",
    ]).format(term=term, e0=evidence[0], e1=evidence[1])

    faq_remote = pick(slug, "faq-remote", [
        "An initial remote review is often possible using organised digital records. Representation, evidence collection, deadlines and any physical examination remain fact-dependent.",
        "Leaving Türkiye does not by itself prevent preliminary review. The completeness of the records, the parties involved and the chosen procedure determine what can happen remotely.",
        "Many first assessments can begin after the patient travels home. Missing source files, identity details or necessary examinations may still require additional steps.",
        "Counsel can often identify issues and document gaps remotely. No conclusion about procedure or timing should be made until the individual treatment file is checked.",
        "Remote instruction may be practical where original records and communications are available. Later medical or procedural requirements depend on the specific dispute.",
        "A patient can usually send a first evidence bundle from abroad. The next step depends on health needs, provider identity, forum and the quality of the preserved record.",
        "Distance changes logistics, not the need for reliable evidence. A preliminary review can start remotely, while formal steps are assessed separately.",
        "Digital records can support an initial consultation from another country. Whether further examination, notarisation or representation is needed must be decided case by case.",
        "The file can often be triaged remotely after travel. Current deadlines and evidence requirements must still be confirmed under the route relevant to the patient.",
        "A remote review may clarify the legal and evidential questions. It cannot guarantee that every later procedural or medical step can also be completed remotely.",
    ])

    return {
        "bridge": bridge,
        "official_bridge": official_bridge,
        "evidence_intro": evidence_intro,
        "international_one": international_one,
        "international_two": international_two,
        "source_note": source_note,
        "review_intro": review_intro,
        "faq_remote": faq_remote,
        "related_one": related_titles[0],
        "related_two": related_titles[1],
        "related_three": related_titles[2],
    }


def related_title(slug: str, terms_by_slug: dict[str, dict]) -> str:
    return terms_by_slug.get(slug, {}).get("term", slug.replace("-", " ").title())


def source_markup(source_keys: list[str]) -> str:
    items = []
    for key in source_keys:
        source = SOURCES[key]
        items.append(
            f'<li><a href="{esc(source["url"])}" target="_blank" rel="noopener">'
            f'{esc(source["title"])}</a><span>{esc(source["publisher"])}</span></li>'
        )
    return "\n".join(items)


def evidence_markup(term: str, evidence: list[str]) -> str:
    lead_ins = [
        "Establish the contemporaneous record with",
        "Test the factual sequence against",
        "Support the medical or financial proposition using",
        "Preserve the communication and responsibility trail through",
    ]
    return "\n".join(
        f"<li><strong>{esc(item.capitalize())}:</strong> {esc(lead_ins[index])} {esc(item)} so the {esc(term.lower())} issue can be assessed from dated evidence rather than recollection alone.</li>"
        for index, item in enumerate(evidence)
    )


def build_form(term: str) -> str:
    return f"""
        <aside class="glossary-hero-form" aria-labelledby="heroFormTitle">
          <h2 id="heroFormTitle">Request a confidential case review</h2>
          <p>Tell us briefly what happened. Submitting this form does not create an attorney-client relationship.</p>
          <form class="custom-contact-form glossary-request-form" data-type="contact">
            <input type="hidden" name="procedure" value="Glossary enquiry: {esc(term)}">
            <div class="glossary-form-row">
              <div class="form-group"><label for="firstName">First name *</label><input id="firstName" type="text" name="firstname" autocomplete="given-name" required></div>
              <div class="form-group"><label for="lastName">Last name</label><input id="lastName" type="text" name="lastname" autocomplete="family-name"></div>
            </div>
            <div class="form-group"><label for="email">Email *</label><input id="email" type="email" name="email" autocomplete="email" required></div>
            <div class="glossary-form-row glossary-phone-row">
              <div class="form-group glossary-code"><label for="phoneCode">Code</label><select id="phoneCode" name="phonecode" aria-label="Phone country code"><option value="+90">+90</option><option value="+44">+44</option><option value="+1">+1</option><option value="+49">+49</option><option value="+33">+33</option><option value="+31">+31</option><option value="+61">+61</option></select></div>
              <div class="form-group"><label for="phone">Phone *</label><input id="phone" type="tel" name="phone" autocomplete="tel" required></div>
            </div>
            <div class="form-group"><label for="message">What happened? *</label><textarea id="message" name="message" rows="3" required></textarea></div>
            <label class="glossary-privacy-check"><input type="checkbox" name="privacy_acknowledgement" value="yes" required><span>I have read the <a href="privacy-policy.html" target="_blank" rel="noopener">Privacy Policy</a> and understand how my information will be used to respond to this enquiry.</span></label>
            <button type="submit" class="btn-submit specialization-submit-btn">Request case review</button>
            <div class="form-msg" role="status" aria-live="polite"></div>
          </form>
        </aside>"""


def build_schema(item: dict, slug: str, description: str, source_keys: list[str]) -> str:
    canonical = f"{SITE}/glossary-{slug}.html"
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": f"{canonical}#article",
                "headline": f"{item['term']} in Turkish Medical Law",
                "description": description,
                "dateModified": UPDATED_ISO,
                "mainEntityOfPage": canonical,
                "inLanguage": "en",
                "author": {
                    "@type": "Person",
                    "name": "Başak Çavuşoğulları",
                    "jobTitle": "Attorney at Law",
                    "url": f"{SITE}/#att-basak-cavusogullari",
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Medical Law Türkiye",
                    "url": SITE,
                    "logo": {"@type": "ImageObject", "url": f"{SITE}/images/logo.png"},
                },
                "image": [f"{SITE}/images/glossary/{slug}-{number}.webp" for number in range(1, 4)],
                "citation": [SOURCES[key]["url"] for key in source_keys],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Glossary", "item": f"{SITE}/glossary.html"},
                    {"@type": "ListItem", "position": 3, "name": item["term"], "item": canonical},
                ],
            },
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2).replace("</", "<\\/")


def render_page(item: dict, terms_by_slug: dict[str, dict]) -> str:
    term = item["term"]
    tr = item["tr"]
    slug = slugify(term)
    canonical = f"{SITE}/glossary-{slug}.html"
    description = f"Understand {term} ({tr}) in Turkish medical law: what it means, evidence to preserve, official sources and practical review steps."
    source_keys = list(CATEGORY_SOURCES[item["category"]])
    if term == "Off-Label Drug Use":
        source_keys[1] = "medicine"
    context = CATEGORY_CONTEXT[item["category"]].format(term=term)
    related_titles = [related_title(related_slug, terms_by_slug) for related_slug in item["related"]]
    related = "\n".join(
        f'<a href="glossary-{esc(related_slug)}.html">{esc(related_title(related_slug, terms_by_slug))}</a>'
        for related_slug in item["related"]
    )
    copy = page_specific_copy(item, slug, related_titles)
    evidence = evidence_markup(term, item["evidence"])
    sources = source_markup(source_keys)
    schema = build_schema(item, slug, description, source_keys)
    form = build_form(term)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","w3ub3di1um");</script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-L2R09RPPTV"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-L2R09RPPTV');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(term)} in Turkish Medical Law | Medical Law Türkiye</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="Başak Çavuşoğulları">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <link rel="canonical" href="{canonical}">
  <meta property="og:locale" content="en_US">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(term)} in Turkish Medical Law">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Medical Law Türkiye">
  <meta property="og:image" content="{SITE}/images/glossary/{slug}-1.webp">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(term)} in Turkish Medical Law">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SITE}/images/glossary/{slug}-1.webp">
  <script type="application/ld+json">{schema}</script>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v=20260901-seo2">
  <link rel="icon" href="favicon.ico" type="image/x-icon">
  <link rel="apple-touch-icon" href="images/logo.png">
</head>
<body>
  <nav id="mainNav" class="scrolled">
    <div class="nav-inner">
      <a href="/" class="logo" aria-label="Medical Law Türkiye Home"><div class="logo-cross"><svg width="28" height="28" viewBox="0 0 28 28" fill="none"><line x1="14" y1="2" x2="14" y2="26" stroke="#0E7490" stroke-width="4"/><line x1="2" y1="14" x2="26" y2="14" stroke="#0E7490" stroke-width="4"/></svg></div><div class="logo-text"><span class="logo-main">Medical<br>Law</span><span class="logo-sub">Turkey</span></div></a>
      <ul class="nav-links" id="navLinks"><li><a href="/#about">About Us</a></li><li><a href="specializations.html">Our Specializations</a></li><li><a href="casestudies.html">Case Studies</a></li><li><a href="articles.html">Articles</a></li><li><a href="glossary.html" class="active">Glossary</a></li><li><a href="/#contact">Contact</a></li></ul>
      <a href="/#contact" class="nav-cta" id="navCtaBtn">Case Review</a>
      <button class="hamburger" id="hamburgerBtn" type="button" aria-label="Toggle navigation menu" aria-controls="navLinks" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </nav>

  <main>
    <section class="glossary-page-hero">
      <div class="section-inner glossary-hero-grid">
        <div class="glossary-hero-copy">
          <nav class="glossary-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="glossary.html">Glossary</a><span>/</span><span aria-current="page">{esc(term)}</span></nav>
          <div class="section-eyebrow">Turkish Medical Law Glossary</div>
          <h1>{esc(term)}</h1>
          <p class="glossary-turkish-term">Turkish: {esc(tr)}</p>
          <p class="glossary-hero-definition">{esc(item['definition'])}</p>
          <div class="glossary-author-line"><span>Written by <a href="/#att-basak-cavusogullari">Att. Başak Çavuşoğulları</a></span><span>Reviewed {UPDATED_LABEL}</span></div>
        </div>
{form}
      </div>
    </section>

    <article class="glossary-article" id="article-content">
      <div class="section-inner glossary-article-inner">
        <section>
          <h2>What {esc(term)} means in a Turkish medical case</h2>
          <p>{esc(item['definition'])} {esc(copy['bridge'])}</p>
          <p>{esc(item['question'])}</p>
          <p>{esc(item['nuance'])}</p>
        </section>

        <figure class="glossary-figure glossary-figure-wide">
          <img src="images/glossary/{slug}-1.webp" alt="Professional case review illustrating {esc(term.lower())} in Turkish medical law" width="1200" height="675" loading="eager" fetchpriority="high">
          <figcaption>A document-led review keeps {esc(term.lower())} tied to the patient's real chronology.</figcaption>
        </figure>

        <section>
          <h2>The legal framework to check</h2>
          <p>{esc(context)}</p>
          <p>{esc(copy['official_bridge'])}</p>
        </section>

        <section class="glossary-evidence-section">
          <div>
            <h2>Evidence that usually deserves early attention</h2>
            <p>{esc(copy['evidence_intro'])}</p>
            <ul class="glossary-evidence-list">{evidence}</ul>
          </div>
          <figure class="glossary-figure">
            <img src="images/glossary/{slug}-2.webp" alt="Records and evidence relevant to {esc(term.lower())}" width="1200" height="675" loading="lazy">
            <figcaption>Original, dated records are more reliable than reconstructed summaries.</figcaption>
          </figure>
        </section>

        <section>
          <h2>How an international patient can prepare</h2>
          <p>{esc(copy['international_one'])}</p>
          <p>{esc(copy['international_two'])}</p>
        </section>

        <section class="glossary-review-panel">
          <figure class="glossary-figure">
            <img src="images/glossary/{slug}-3.webp" alt="Independent legal review concerning {esc(term.lower())}" width="1200" height="675" loading="lazy">
            <figcaption>Legal review should separate clinical facts, official rules, causation and loss.</figcaption>
          </figure>
          <div>
            <h2>A careful review sequence</h2>
            <p>{esc(copy['review_intro'])}</p>
            <ol>
              <li><strong>Protect health first.</strong> Seek appropriate independent treatment when symptoms or complications require attention.</li>
              <li><strong>Preserve the source record.</strong> Keep original files, metadata, invoices and messages relevant to {esc(term.lower())}.</li>
              <li><strong>Identify every actor.</strong> Separate the surgeon, facility, intermediary, insurer and payment recipient.</li>
              <li><strong>Apply the current official rule.</strong> Match each factual proposition to a primary source and appropriate expert evidence.</li>
              <li><strong>Choose the correct route.</strong> Confirm forum, parties, pre-action steps and deadlines before filing or settling.</li>
            </ol>
          </div>
        </section>

        <section class="official-sources" aria-labelledby="officialSourcesTitle">
          <h2 id="officialSourcesTitle">Official primary sources</h2>
          <p>{esc(copy['source_note'])}</p>
          <ul>{sources}</ul>
        </section>

        <section>
          <h2>Related glossary concepts</h2>
          <div class="glossary-related-links">{related}</div>
        </section>

        <section class="glossary-faq">
          <h2>Questions patients often ask</h2>
          <details><summary>Does {esc(term)} automatically prove medical malpractice?</summary><p>No. {esc(item['nuance'])} The complete record and applicable Turkish rule must be reviewed before any conclusion.</p></details>
          <details><summary>Which documents are useful for a first {esc(term.lower())} review?</summary><p>Start with {esc(', '.join(item['evidence'][:-1]))}, and {esc(item['evidence'][-1])}. Keep original files and dates wherever possible.</p></details>
          <details><summary>Can the issue be reviewed after I leave Türkiye?</summary><p>{esc(copy['faq_remote'])}</p></details>
        </section>

        <aside class="glossary-legal-note"><strong>Legal information, not a case outcome:</strong> This page provides general information. It does not diagnose malpractice, guarantee compensation or create an attorney-client relationship.</aside>
      </div>
    </article>
  </main>

  <footer><div class="footer-inner"><div class="footer-top"><div class="footer-brand"><div class="footer-logo-wrap"><div class="footer-cross"><svg width="24" height="24" viewBox="0 0 28 28" fill="none"><line x1="14" y1="2" x2="14" y2="26" stroke="#0891B2" stroke-width="4"/><line x1="2" y1="14" x2="26" y2="14" stroke="#0891B2" stroke-width="4"/></svg></div><div class="footer-logo-text"><span class="footer-logo-main">Medical Law</span><span class="footer-logo-sub">Turkey</span></div></div><p>Legal representation for international patients experiencing complications after treatment in Türkiye.</p></div><div class="footer-nav"><h4>Our Specializations</h4><a href="rhinoplasty-malpractice.html">Rhinoplasty</a><a href="hair-transplant-malpractice.html">Hair Transplant</a><a href="dental-treatments-malpractice.html">Dental Care</a><a href="specializations.html">All Practice Areas</a></div><div class="footer-nav"><h4>Resources</h4><a href="articles.html">Articles</a><a href="casestudies.html">Case Studies</a><a href="glossary.html">Legal Glossary</a></div><div class="footer-legal"><h4>Legal</h4><a href="privacy-policy.html">Privacy Policy</a><a href="kvkk-gdpr-notice.html">KVKK/GDPR</a><a href="terms-of-use.html">Terms of Use</a></div></div><div class="footer-bottom"><p>Att. Başak Çavuşoğulları &amp; Att. Büşra Ocak</p><p class="footer-disclaimer">This website provides general legal information only. No attorney-client relationship is created until a formal engagement agreement is signed.</p><p>&copy; 2026 Medical Law Türkiye. All rights reserved.</p></div></div></footer>

  <script src="navigation.js?v=20260901-nav"></script>
  <script src="specialization-form.js?v=20260901-glossary"></script>
  <!-- ── FLOATING WHATSAPP ── -->
  <a href="https://wa.me/905319336316" class="floating-whatsapp" id="floatingWhatsapp" target="_blank" rel="noopener" aria-label="Contact us on WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492l4.625-1.478A11.932 11.932 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75c-2.16 0-4.16-.69-5.795-1.86l-.415-.276-2.744.878.853-2.668-.3-.434A9.713 9.713 0 012.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75z"/></svg></a>
</body>
</html>
"""


def render_pages(terms: list[dict], output_dir: str | Path = ".") -> list[Path]:
    output_root = Path(output_dir)
    terms_by_slug = {slugify(item["term"]): item for item in terms}
    rendered: list[Path] = []
    for item in terms:
        slug = slugify(item["term"])
        markup = render_page(item, terms_by_slug)
        article_match = re.search(
            r'<article class="glossary-article" id="article-content">(.*?)</article>',
            markup,
            flags=re.DOTALL,
        )
        article_text = html.unescape(re.sub(r"<[^>]+>", " ", article_match.group(1))) if article_match else ""
        word_count = len(re.findall(r"\b[\w’'-]+\b", article_text))
        if word_count < 500:
            raise ValueError(f"glossary-{slug}.html has only {word_count} article words")
        if markup.count('class="floating-whatsapp"') != 1:
            raise ValueError(f"glossary-{slug}.html must contain exactly one floating WhatsApp button")
        path = output_root / f"glossary-{slug}.html"
        path.write_text(markup, encoding="utf-8")
        rendered.append(path)
    return rendered
