import os
import re

new_terms = [
    ("Permanent Disability Rate", "Turkish: Maluliyet Oranı", "The officially determined percentage of permanent loss of bodily or mental functions resulting from a medical error, used to calculate future loss of earnings."),
    ("Temporary Incapacity", "Turkish: Geçici İş Göremezlik", "The period during which a patient is unable to work or perform daily activities while recovering from a medically induced injury before reaching maximum medical improvement."),
    ("Iatrogenic Injury", "Turkish: İyatrojenik Zarar", "Any harm, injury, or complication unintentionally caused to a patient by a physician, medical treatment, or diagnostic procedure."),
    ("Nosocomial Infection", "Turkish: Hastane Enfeksiyonu", "An infection acquired by a patient during a hospital stay that was not present or incubating at the time of admission, often raising questions about facility hygiene standards."),
    ("Wrong-Site Surgery", "Turkish: Yanlış Taraf Ameliyatı", "A severe never event in which a surgical procedure is performed on the wrong patient, wrong body part, or the wrong side of the body."),
    ("Surgical Negligence", "Turkish: Cerrahi İhmal", "A failure by a surgeon to exercise the required standard of care during an operation, encompassing technical errors, leaving foreign objects inside patients, or poor surgical planning."),
    ("Post-Operative Care", "Turkish: Ameliyat Sonrası Bakım Yükümlülüğü", "The legal and ethical obligation of a healthcare provider to monitor, treat, and manage a patient's recovery and any complications immediately following surgery."),
    ("Off-Label Drug Use", "Turkish: Endikasyon Dışı İlaç Kullanımı", "The practice of prescribing a medication for an unapproved indication, age group, dose, or form of administration, which carries specific informed consent requirements."),
    ("Medical Device Liability", "Turkish: Tıbbi Cihaz Sorumluluğu", "The legal responsibility borne by manufacturers, distributors, or medical facilities when a defective medical implant or device causes patient injury."),
    ("Cosmetic Surgery Regulation", "Turkish: Estetik Cerrahi Mevzuatı", "The specific body of laws and ethical guidelines governing elective aesthetic procedures, which heavily emphasizes guaranteed outcomes and stringent informed consent."),
    ("Loss of Earnings", "Turkish: Kazanç Kaybı", "Pecuniary damages awarded to compensate a patient for the income they have lost, and will predictably lose in the future, due to a malpractice-induced disability."),
    ("Future Medical Expenses", "Turkish: Gelecekteki Tedavi Giderleri", "Compensation intended to cover all anticipated costs for necessary ongoing care, revision surgeries, medications, and rehabilitation resulting from a medical error."),
    ("Loss of Consortium", "Turkish: Aile Bütünlüğünün Bozulması Zararı", "Damages claimed by the close family members or spouse of a malpractice victim for the deprivation of companionship, affection, and marital relations due to severe injury or death."),
    ("Wrongful Death", "Turkish: Haksız Ölüm", "A legal claim brought by surviving dependents or close relatives against a healthcare provider whose negligence directly caused the death of the patient."),
    ("Bereavement Damages", "Turkish: Ölüm Nedeniyle Manevi Tazminat", "Non-pecuniary (moral) compensation awarded to the family members of a deceased patient to alleviate their profound grief and emotional suffering."),
    ("Damage Mitigation Obligation", "Turkish: Zararı Azaltma Yükümlülüğü", "The legal duty of an injured patient to take reasonable steps to prevent their health condition and financial losses from worsening following a medical error."),
    ("Interest on Damages", "Turkish: Tazminata İşleyen Faiz", "The statutory or commercial interest applied to a compensation award, calculated from the date the malpractice occurred or the lawsuit was filed, to preserve the value of the money."),
    ("Lump Sum vs. Periodic Payment", "Turkish: Toplu / Dönemsel Ödeme", "The methods by which courts can order compensation to be paid; while lump-sum is standard in Türkiye, periodic payments (annuities) can be requested for long-term care needs."),
    ("Malpractice Insurance", "Turkish: Mesleki Sorumluluk Sigortası", "Mandatory professional liability insurance for physicians in Türkiye that covers the defense costs and compensation claims arising from medical negligence."),
    ("Social Security Recourse", "Turkish: SGK Rücu Hakkı", "The legal right of the Turkish Social Security Institution (SGK) to reclaim the costs of medical treatments it provided to the victim from the negligent doctor or hospital."),
    ("Contractual Liability", "Turkish: Sözleşmeden Doğan Sorumluluk", "The legal responsibility arising when a healthcare provider or private clinic breaches the explicit or implied terms of the treatment contract with the patient."),
    ("Tortious Liability", "Turkish: Haksız Fiilden Doğan Sorumluluk", "Liability that arises from a wrongful act or infringement of a right (other than under contract) leading to civil legal liability, often applicable in emergency interventions."),
    ("Vicarious Liability", "Turkish: Üstün Sorumluluğu / Adam Çalıştıranın Sorumluluğu", "The legal doctrine holding a hospital or clinic owner strictly liable for the negligent actions committed by their employed doctors or nurses during their duties."),
    ("Joint and Several Liability", "Turkish: Müteselsil Sorumluluk", "A legal rule allowing a patient to pursue a claim for the full amount of damages against any one or all of multiple negligent parties (e.g., both the surgeon and the hospital)."),
    ("Strict Liability", "Turkish: Kusursuz Sorumluluk", "Liability that does not depend on actual negligence or intent to harm; in Turkish medical law, this is exceptionally applied to hospitals regarding facility safety and organizational flaws."),
    ("Contributory Negligence", "Turkish: Müterafik Kusur", "A legal defense arguing that the patient's own actions (such as failing to follow post-operative instructions) contributed to their injury, which may reduce the compensation amount."),
    ("Force Majeure", "Turkish: Mücbir Sebep", "An unforeseeable and unavoidable external event (like an earthquake during surgery) that totally prevents a doctor from fulfilling their obligations, exempting them from liability."),
    ("Assumption of Risk", "Turkish: Riski Kabul", "The legal principle that a patient, having been fully and properly informed of the unavoidable natural risks of a procedure, cannot claim malpractice if one of those specific risks occurs."),
    ("Breach of Contract", "Turkish: Sözleşmenin İhlali", "A failure by a medical provider to perform any term of a contract, such as a cosmetic surgeon failing to achieve an explicitly promised aesthetic outcome."),
    ("Medical Service Contract", "Turkish: Vekalet / Eser Sözleşmesi", "The legal classification of the doctor-patient relationship; generally a mandate contract (vekalet) for healing, but a contract of work (eser) for elective cosmetic results."),
    ("Patient Rights Regulation", "Turkish: Hasta Hakları Yönetmeliği", "The comprehensive administrative legislation in Türkiye detailing the fundamental rights of patients, including the right to information, privacy, and respectful care."),
    ("Right to Refuse Treatment", "Turkish: Tedaviyi Reddetme Hakkı", "The fundamental right of a mentally competent patient to decline or halt medical interventions, even if doing so may result in severe health consequences or death."),
    ("Right to Second Opinion", "Turkish: İkinci Görüş Hakkı", "The legal right of a patient to consult with another physician regarding their diagnosis and treatment plan without facing prejudice from their primary healthcare provider."),
    ("Privacy of Medical Data", "Turkish: Tıbbi Veri Gizliliği", "The strict legal protection of patient health records and personal information, protected under both medical ethics and the Turkish Personal Data Protection Law (KVKK)."),
    ("Right to Access Medical Records", "Turkish: Tıbbi Kayıtlara Erişim Hakkı", "A patient's absolute right to obtain copies of all documents, test results, and notes in their medical file, which is crucial for building a malpractice case."),
    ("Patient Advocate", "Turkish: Hasta Hakları Birimi", "A dedicated unit within Turkish hospitals designed to address patient grievances, facilitate communication, and mediate minor disputes before they escalate to legal action."),
    ("Vulnerable Patient", "Turkish: Savunmasız Hasta", "Patients who are minors, elderly, mentally incapacitated, or language-barrier-restricted (like tourists), requiring heightened standards of care and specialized consent procedures."),
    ("Minor Patient Consent", "Turkish: Küçük Hastada Onam", "The legal requirement that valid consent for treating a patient under the age of 18 must be obtained from their parents or legal guardians, except in immediate life-saving emergencies."),
    ("Capacity to Consent", "Turkish: Rıza Ehliyeti", "The mental and legal ability of a patient to understand the nature, risks, and consequences of a medical procedure and make an informed decision regarding it."),
    ("Emergency Exception to Consent", "Turkish: Acil Durumda Onam İstisnası", "The legal provision allowing doctors to perform life-saving medical interventions on an unconscious or incapacitated patient without obtaining prior consent.")
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\-]+', '-', text)
    return text.strip('-')

header_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Microsoft Clarity -->
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        })(window, document, "clarity", "script", "w3ub3di1um");
    </script>
  <!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-L2R09RPPTV"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-L2R09RPPTV');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__TERM__ — Glossary | Medical Law Türkiye</title>
  <meta name="description" content="Detailed guide on __TERM__ (__TR_TERM__) in Turkish medical law. Learn what it means, the legal framework, processes, and FAQs.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://medicallawturkey.com/glossary-__SLUG__.html">
  <meta property="og:title" content="__TERM__ — Glossary | Medical Law Türkiye">
  <meta property="og:description" content="Detailed guide on __TERM__ (__TR_TERM__) in Turkish medical law.">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://medicallawturkey.com/glossary-__SLUG__.html">
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v=20260901-nav">
  <link rel="icon" href="favicon.ico" type="image/x-icon">
  <link rel="apple-touch-icon" href="images/logo.png">
</head>
<body>
  <nav id="mainNav" class="scrolled">
    <div class="nav-inner">
      <a href="index.html" class="logo" aria-label="Medical Law Türkiye Home">
        <div class="logo-cross">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <line x1="14" y1="2" x2="14" y2="26" stroke="#0E7490" stroke-width="4" stroke-linecap="square" />
            <line x1="2" y1="14" x2="26" y2="14" stroke="#0E7490" stroke-width="4" stroke-linecap="square" />
          </svg>
        </div>
        <div class="logo-text">
          <span class="logo-main">Medical<br>Law</span>
          <span class="logo-sub">Turkey</span>
        </div>
      </a>
      <ul class="nav-links" id="navLinks">
        <li><a href="index.html#about">About Us</a></li>
        <li><a href="specializations.html">Our Specializations</a></li>
        <li><a href="casestudies.html">Case Studies</a></li>
        <li><a href="articles.html">Articles</a></li>
        <li><a href="glossary.html" class="active">Glossary</a></li>
        <li><a href="index.html#contact">Contact</a></li>
      </ul>
      <a href="index.html#contact" class="nav-cta" id="navCtaBtn">Case Review</a>
      <button class="hamburger" id="hamburgerBtn" type="button" aria-label="Toggle navigation menu" aria-controls="navLinks" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>

  <section class="spec-page-hero">
    <div class="section-inner spec-hero-inner">
      <div class="spec-hero-copy">
        <div class="section-eyebrow">Legal Glossary</div>
        <h1 class="section-title">__TERM__</h1>
        <p class="section-desc">__TR_TERM__</p>
      </div>
    </div>
  </section>

  <section id="article-content" style="padding-top: 4rem; padding-bottom: 4rem; background: #fff;">
    <div class="section-inner" style="max-width: 800px; margin: auto; font-size: 1.1rem; line-height: 1.8; color: #334155;">
"""

footer_template = """
    </div>
  </section>

  <footer>
    <div class="footer-inner">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="footer-logo-wrap">
            <div class="footer-cross">
              <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
                <line x1="14" y1="2" x2="14" y2="26" stroke="#0891B2" stroke-width="4" stroke-linecap="square" />
                <line x1="2" y1="14" x2="26" y2="14" stroke="#0891B2" stroke-width="4" stroke-linecap="square" />
              </svg>
            </div>
            <div class="footer-logo-text">
              <span class="footer-logo-main">Medical Law</span>
              <span class="footer-logo-sub">Turkey</span>
            </div>
          </div>
          <p>Expert legal representation for international patients experiencing complications after cosmetic surgery in Türkiye.</p>
        </div>
        <div class="footer-nav">
          <h4>Our Specializations</h4>
          <a href="arm-lift-malpractice.html">Arm Lift</a>
          <a href="bbl-malpractice.html">BBL</a>
          <a href="rhinoplasty-malpractice.html">Rhinoplasty</a>
          <a href="dental-treatments-malpractice.html">Dental Care</a>
          <a href="specializations.html">All Practice Areas</a>
        </div>
        <div class="footer-nav">
          <h4>Resources</h4>
          <a href="articles.html">Articles</a>
          <a href="casestudies.html">Case Studies</a>
          <a href="glossary.html">Legal Glossary</a>
        </div>
        <div class="footer-legal">
          <h4>Legal</h4>
          <a href="privacy-policy.html">Privacy Policy</a>
          <a href="kvkk-gdpr-notice.html">KVKK/GDPR</a>
          <a href="terms-of-use.html">Terms of Use</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>Att. Başak Çavuşoğulları &amp; Att. Büşra Ocak</p>
        <p class="footer-disclaimer">This website provides general legal information only. No attorney-client relationship is created until a formal engagement agreement is signed.</p>
        <p>&copy; 2026 Medical Law Türkiye. All rights reserved.</p>
      </div>
    </div>
  </footer>

  <script src="navigation.js?v=20260901-nav"></script>

  <!-- ── FLOATING WHATSAPP ── -->
  <a href="https://wa.me/905319336316" class="floating-whatsapp" id="floatingWhatsapp" target="_blank" rel="noopener"
    aria-label="Contact us on WhatsApp">
    <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
      <path
        d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z" />
      <path
        d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492l4.625-1.478A11.932 11.932 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75c-2.16 0-4.16-.69-5.795-1.86l-.415-.276-2.744.878.853-2.668-.3-.434A9.713 9.713 0 012.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75z" />
    </svg>
  </a>
</body>
</html>
"""

def generate_body(term, tr_term, short_def):
    body = f"<h2 style='color: #0F172A; margin-bottom: 1.5rem; font-size: 2rem;'>Introduction to {term}</h2>\n"
    body += f"<p style='margin-bottom: 1.5rem;'><strong>{term}</strong> ({tr_term}) is a critical concept in the Turkish health and legal system. {short_def}</p>\n"
    
    body += f"""
<p style='margin-bottom: 1.5rem;'>Understanding the nuances of <strong>{term}</strong> is absolutely essential for both medical professionals and patients, especially international patients coming to Türkiye for medical, dental, or cosmetic procedures. The Turkish legal framework treats health as a fundamental human right, heavily protected under the Constitution. Thus, any matter concerning {term.lower()} is approached with a rigorous, detail-oriented legal perspective.</p>
<p style='margin-bottom: 1.5rem;'>Navigating medical law without a firm grasp of what {term.lower()} means can lead to significant procedural disadvantages. In Turkish courts, terminology is not merely pedantic; it shapes the burden of proof, the jurisdiction of the court, and the types of damages that can be claimed. This comprehensive guide serves to illuminate the profound implications of {term.lower()} in the context of Turkish medical malpractice litigation.</p>
"""

    body += f"<h2 style='color: #0F172A; margin-top: 2.5rem; margin-bottom: 1.5rem; font-size: 1.8rem;'>Legal Framework and Evolution in Turkish Law</h2>\n"
    body += f"""
<p style='margin-bottom: 1.5rem;'>The legal basis for <strong>{term}</strong> traces its origins back to the foundational principles of the Turkish Civil Code and the Turkish Code of Obligations. Over the decades, as modern medicine has evolved and Türkiye has positioned itself as a leading destination for health tourism, the legal system has had to adapt. The Turkish Ministry of Health, alongside judicial bodies like the Court of Cassation, have continually refined the legal precedents surrounding {term.lower()}.</p>
<p style='margin-bottom: 1.5rem;'>Historically, medical disputes were often settled outside the formal judiciary. Today, the approach is highly structured. Cases involving {term.lower()} might fall under the jurisdiction of Consumer Courts (if the relationship is deemed a contractual one based on a specific result, like in cosmetic surgery), Civil Courts of General Jurisdiction, or even Administrative Courts if the incident occurred in a state-run hospital. Recognizing how <strong>{term}</strong> interplays with these different jurisdictions is what separates a successful legal strategy from an unsuccessful one.</p>
<p style='margin-bottom: 1.5rem;'>Furthermore, the integration of European Union legal standards into the Turkish legal framework has bolstered the protection of patient rights. Elements such as the stringent requirements for informed consent and detailed medical record-keeping have directly influenced how <strong>{term}</strong> is interpreted by judges and medical expert panels today.</p>
"""

    body += f"<h2 style='color: #0F172A; margin-top: 2.5rem; margin-bottom: 1.5rem; font-size: 1.8rem;'>Key Principles and Application in Practice</h2>\n"
    body += f"""
<p style='margin-bottom: 1.5rem;'>In practical terms, whenever a medical dispute arises, one of the first elements scrutinized by the attorneys and the presiding judge is how <strong>{term}</strong> factors into the timeline of events. Let us break down the core principles:</p>
<ul style='margin-bottom: 1.5rem; padding-left: 20px;'>
  <li style='margin-bottom: 0.8rem;'><strong>Rigid Adherence to Standards:</strong> In Turkish law, any deviation from established protocols must be justified. The concept of {term.lower()} often serves as the benchmark against which the actions of the healthcare provider are measured.</li>
  <li style='margin-bottom: 0.8rem;'><strong>Expert Evaluation:</strong> Judges in Türkiye are legal experts, not medical doctors. Therefore, cases hinging on <strong>{term}</strong> invariably require reports from independent medical experts or the Forensic Medicine Institute (Adli Tıp Kurumu). These experts will dissect the case file to determine if the criteria for {term.lower()} have been met.</li>
  <li style='margin-bottom: 0.8rem;'><strong>Patient's Burden vs. Doctor's Duty:</strong> The dynamic between what the patient must prove and what the doctor must defend is complex. <strong>{term}</strong> plays a pivotal role in shifting this balance. For instance, if a complication arises, the defense will heavily rely on proving that the standard of care was met and the patient was adequately informed.</li>
</ul>
<p style='margin-bottom: 1.5rem;'>It is also important to note that the application of <strong>{term}</strong> is not static. It varies significantly between elective procedures (like aesthetic surgeries, which are evaluated under a strict contract of work) and therapeutic procedures (which are evaluated under a mandate contract, requiring only the highest degree of diligence, not a guaranteed outcome).</p>
"""

    body += f"<h2 style='color: #0F172A; margin-top: 2.5rem; margin-bottom: 1.5rem; font-size: 1.8rem;'>Implications for International Health Tourists</h2>\n"
    body += f"""
<p style='margin-bottom: 1.5rem;'>Türkiye is a global hub for health tourism, attracting hundreds of thousands of patients annually for procedures ranging from dental implants to complex neurosurgery. For these international patients, understanding <strong>{term}</strong> is particularly challenging due to language barriers and differences in legal cultures.</p>
<p style='margin-bottom: 1.5rem;'>When an international patient encounters a negative medical outcome, they often assume the legal process will mirror that of their home country. However, Turkish law operates on civil law principles, not common law. The interpretation of <strong>{term}</strong> might lack the punitive damages seen in US courts but offers other distinct advantages, such as comprehensive non-pecuniary damage assessments and the ability to litigate via Power of Attorney without needing to travel back to Türkiye frequently.</p>
<p style='margin-bottom: 1.5rem;'>Furthermore, health tourism regulations introduced by the Turkish Ministry of Health impose additional obligations on clinics and agencies catering to foreigners. These regulations intersect with the concept of <strong>{term}</strong>, meaning that a breach of these specific health tourism rules can inherently constitute a breach of the standard of care or contractual obligations.</p>
"""

    body += f"<h2 style='color: #0F172A; margin-top: 2.5rem; margin-bottom: 1.5rem; font-size: 1.8rem;'>Court of Cassation Precedents Involving {term}</h2>\n"
    body += f"""
<p style='margin-bottom: 1.5rem;'>To truly understand the weight of <strong>{term}</strong>, one must look at the decisions rendered by the Court of Cassation (Yargıtay), Türkiye's highest appellate court for civil matters. Over the years, the Court of Cassation has established a robust body of jurisprudence.</p>
<p style='margin-bottom: 1.5rem;'>In numerous landmark rulings, the Court has emphasized that generic, pre-printed consent forms do not absolve a physician of liability if <strong>{term}</strong> is improperly handled. The Court consistently demands that patients be enlightened in a manner they can understand—meaning plain language, not complex medical jargon. If the defense cannot prove this targeted enlightenment, the Court often rules in favor of the patient, regardless of whether a technical medical error occurred.</p>
<p style='margin-bottom: 1.5rem;'>Similarly, when assessing damages, the Court's interpretation of <strong>{term}</strong> ensures that patients are compensated not just for physical corrective surgeries, but for the profound psychological trauma and loss of life enjoyment caused by the incident. This holistic approach to compensation underscores the profound respect Turkish jurisprudence holds for bodily integrity.</p>
"""

    body += f"<h2 style='color: #0F172A; margin-top: 2.5rem; margin-bottom: 1.5rem; font-size: 1.8rem;'>What to Do If You Encounter Issues Related to {term}</h2>\n"
    body += f"""
<p style='margin-bottom: 1.5rem;'>If you believe your rights have been violated in relation to <strong>{term}</strong>, taking immediate and calculated steps is vital:</p>
<ol style='margin-bottom: 1.5rem; padding-left: 20px;'>
  <li style='margin-bottom: 0.8rem;'><strong>Secure Your Medical Records:</strong> Under Turkish patient rights regulations, you have an absolute right to access your entire medical file, including surgical notes, consent forms, and imaging. Do this before making any formal accusations.</li>
  <li style='margin-bottom: 0.8rem;'><strong>Seek Independent Medical Advice:</strong> Before proceeding legally, have your condition assessed by another doctor, preferably in your home country, to establish the extent of the damage.</li>
  <li style='margin-bottom: 0.8rem;'><strong>Consult Specialized Legal Counsel:</strong> Do not rely on general practitioners. Find attorneys who specialize strictly in Turkish medical malpractice law. They will evaluate your case against the legal parameters of {term.lower()}.</li>
  <li style='margin-bottom: 0.8rem;'><strong>Understand the Time Limits:</strong> Statute of limitations in Türkiye can be complex, ranging from 1 to 5 to 10 years depending on the classification of the procedure and the facility. Prompt action is necessary.</li>
</ol>
"""

    body += f"<h2 style='color: #0F172A; margin-top: 3.5rem; margin-bottom: 1.5rem; font-size: 2rem;'>Frequently Asked Questions (FAQs)</h2>\n"
    
    faq1 = f"What exactly does {term} mean in the context of a Turkish medical lawsuit?"
    faq1_ans = f"In a Turkish medical lawsuit, {term} ({tr_term}) refers specifically to {short_def.lower()} It is a core element that courts examine when determining liability and assessing the validity of a malpractice claim. Without establishing the parameters of {term.lower()}, advancing a claim is incredibly difficult."
    
    faq2 = f"How does {term} affect international patients differently than Turkish citizens?"
    faq2_ans = f"Legally, the core definition of {term} applies equally to both citizens and foreigners. However, international patients often face practical challenges—such as translated documents that fail to convey the true legal meaning of {term.lower()}, or logistical hurdles in providing testimony. Specialized legal representation bridges this gap."
    
    faq3 = f"Can I claim compensation solely based on issues related to {term}?"
    faq3_ans = f"Yes, depending on the severity of the breach. In Turkish law, if a violation related to {term.lower()} directly results in physical, financial, or severe emotional harm, it forms a valid basis for both pecuniary (material) and non-pecuniary (moral) damage claims."
    
    faq4 = f"Is the concept of {term} judged by the standards of my home country or Türkiye?"
    faq4_ans = f"It is strictly judged according to Turkish legal standards and the Turkish medical community's accepted practices. The court will apply Turkish law (specifically the Code of Obligations and Consumer Protection Law) to interpret {term.lower()}, supported by local expert testimony."
    
    faq5 = f"How long does a court case revolving around {term} typically take in Türkiye?"
    faq5_ans = f"Medical malpractice cases are notoriously complex and require detailed expert evaluations. A case heavily reliant on determining the nuances of {term.lower()} can take anywhere from 2 to 4 years to reach a verdict in the first instance court, followed by potential appeals."

    faqs = [
        (faq1, faq1_ans),
        (faq2, faq2_ans),
        (faq3, faq3_ans),
        (faq4, faq4_ans),
        (faq5, faq5_ans),
    ]

    for q, a in faqs:
        body += f"""
<div class="faq-item" style="margin-bottom: 1.5rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 1rem;">
  <h3 style="color: #0891B2; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 600;">{q}</h3>
  <p style="margin: 0;">{a}</p>
</div>
"""

    return body

for term, tr_term, short_def in new_terms:
    slug = slugify(term)
    filename = f"glossary-{slug}.html"
    
    header = header_template.replace("__TERM__", term).replace("__TR_TERM__", tr_term).replace("__SLUG__", slug)
    content = header + generate_body(term, tr_term, short_def) + footer_template
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Generated {len(new_terms)} new glossary pages successfully.")
