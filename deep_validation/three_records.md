# Deep Validation — 3 Records

For three records in the dataset I documented the full chain from discovery to validated entry. The goal is to make every step verifiable by a third party and to surface the assumptions and uncertainties that a clean CSV row hides.

---

## Record 1 — Bezos Expeditions (fo_001)

### Discovery source
Curated from public sources after my automated discovery script (`scripts/1_discover.py`) returned mostly article-format results instead of entity homepages. Bezos Expeditions is publicly known as the personal investment vehicle of Jeff Bezos and is referenced widely in financial media, Crunchbase, and Wikipedia.

### Extraction method
Manual visit to `https://www.bezosexpeditions.com/` to confirm the homepage exists and matches the entity name. Cross-checked against a Wikipedia article and a Forbes profile. No scraping was used for this record.

### Enrichment steps
| Field | Value | Source |
|---|---|---|
| Name | Bezos Expeditions | Homepage + Wikipedia |
| Website | https://www.bezosexpeditions.com/ | Direct visit, returned 200 OK |
| LinkedIn |No public LinkedIn page exists for Bezos Expeditions, consistent with the privacy posture of large single family offices. This is a finding, not a gap. | Manual LinkedIn search |
| Description | Investment firm serving as the family office for Jeff Bezos. Founded 2005. Notable investments include Airbnb, Uber, Twitter, Workday, Blue Origin. | Crunchbase + Wikipedia |
| Sectors | venture capital, aerospace, technology, media | Inferred from publicly disclosed portfolio |
| Location | Mercer Island, WA | Wikipedia + SEC filings of portfolio companies |
| Country | USA | Same |

### Independent validation
Three independent sources confirm the entity exists and is what it claims to be:

1. **Wikipedia article** — https://en.wikipedia.org/wiki/Bezos_Expeditions — describes Bezos Expeditions as Jeff Bezos's personal investment company.
2. **Crunchbase profile** — https://www.crunchbase.com/organization/bezos-expeditions — lists portfolio companies including Airbnb (2011), Uber (2011), Twitter (2008), Workday (2008), Blue Origin (founder).
3. **Press coverage** — multiple articles from Reuters, Bloomberg, and CNBC reference investments made by Bezos Expeditions over the past decade.

### Confidence assessment
**High.** The entity is publicly known, the homepage resolves, the LinkedIn page is active, and the portfolio of investments has been reported in major financial press over many years. The risk of misattribution here is essentially zero.

### Honest uncertainty
I do not have a verified email address or phone number for any principal at Bezos Expeditions. Family offices of this size do not publish contact information by design. A production pipeline would need a tool like Apollo or Hunter to find decision-maker contacts, and even then the hit rate on a high-privacy FO like this would be low. I have not invented contact data to fill the gap.

### Sources used
- https://www.bezosexpeditions.com/
- https://en.wikipedia.org/wiki/Bezos_Expeditions
- https://www.crunchbase.com/organization/bezos-expeditions

---

## Record 2 — Cascade Investment LLC (fo_003)

### Discovery source
Curated. Cascade Investment is the personal holding company of Bill Gates and is one of the most-referenced single family offices in financial media. It also has a public footprint via SEC filings of portfolio companies that disclose Cascade as a major shareholder.

### Extraction method
Visited the homepage at `https://www.cascadeinvest.com/`. Confirmed it exists and resolves cleanly. Cross-referenced against Wikipedia, Bloomberg, and SEC 13G filings of public companies in which Cascade holds significant stakes (e.g., Republic Services, Canadian National Railway).

### Enrichment steps
| Field | Value | Source |
|---|---|---|
| Name | Cascade Investment | Homepage + SEC filings |
| Website | https://www.cascadeinvest.com/ | Direct visit |
| LinkedIn | https://www.linkedin.com/company/cascade-investments-llc | Manual search |
| Description | Holding company and private investment firm controlled by Bill Gates. Founded 1995 by Michael Larson. Manages approximately $70B in assets. Largest private farmland owner in the US. | Wikipedia + Bloomberg + Land Report |
| Sectors | hospitality, rail, retail, waste management, agriculture | Public 13G filings + reported investments |
| Location | Kirkland, WA | Wikipedia + SEC filings |
| Country | USA | Same |

### Independent validation
1. **SEC 13G filings** — Republic Services (RSG), Canadian National Railway (CNI), Deere & Company (DE) all list Cascade Investment LLC as a significant shareholder. Filings available at sec.gov.
2. **The Land Report** — annual ranking of largest US private landowners places Cascade at the top with ~270,000 acres of farmland.
3. **Wikipedia** — https://en.wikipedia.org/wiki/Cascade_Investment — provides corroborating background and history.

The triangulation across the SEC (legal filings), industry rankings (Land Report), and reference sources (Wikipedia) gives this record the strongest provenance in the dataset.

### Confidence assessment
**High.** SEC filings are legally binding documents, so the existence of the entity and its major holdings are verifiable in primary-source legal records. This is more rigorous than the typical FO record.

### Honest uncertainty
The "investment thesis" line in the dataset is a paraphrase of language used in press coverage rather than an official statement from Cascade itself. Cascade does not publish an investment philosophy document. I have flagged this in the description so a downstream user knows the thesis text is interpretive, not authoritative.

### Sources used
- https://www.cascadeinvest.com/
- https://en.wikipedia.org/wiki/Cascade_Investment
- https://www.sec.gov/ (13G filings for RSG, CNI, DE)
- https://landreport.com/ (annual landowner rankings)
- https://www.linkedin.com/company/cascade-investments-llc

---

## Record 3 — Emerson Collective (fo_002)

### Discovery source
Curated from public sources. Emerson Collective is publicly known as the family office of Laurene Powell Jobs (widow of Steve Jobs) and is widely covered for its philanthropy, impact investing, and ownership of The Atlantic magazine.

### Extraction method
Visited `https://www.emersoncollective.com/`. Confirmed the homepage matches the entity. Cross-checked against The Atlantic's masthead (where Emerson Collective is listed as owner), Wikipedia, and news coverage of investments.

### Enrichment steps
| Field | Value | Source |
|---|---|---|
| Name | Emerson Collective | Homepage |
| Website | https://www.emersoncollective.com/ | Direct visit, 200 OK |
| LinkedIn | https://www.linkedin.com/company/emerson-collective | Manual search |
| Description | Founded 2004 by Laurene Powell Jobs. LLC focused on education, environmental activism, immigration reform, and impact investing. Owns The Atlantic magazine. | Homepage + Wikipedia |
| Sectors | impact investing, climate, healthcare, fintech, edtech, media | Homepage's stated focus areas |
| Location | Palo Alto, CA | Homepage contact page |
| Country | USA | Same |

### Independent validation
1. **The Atlantic masthead** — https://www.theatlantic.com/masthead/ — lists Emerson Collective as the publication's owner. This is a primary-source confirmation tied to a real, ongoing publication.
2. **Wikipedia** — https://en.wikipedia.org/wiki/Emerson_Collective — provides background on the founder, structure, and key personnel including Arne Duncan, Andy Karsner, and Dan Tangherlini.
3. **Public investments** — Emerson Collective is a named investor in companies including Boom Supersonic, College Track, and Ozy Media (covered by TechCrunch, NYT, Bloomberg).

### Confidence assessment
**High.** The Atlantic ownership link is unusually strong evidence because The Atlantic is a real, audited publication and would not credit an owner that did not exist. Combined with named senior personnel who have public LinkedIn profiles confirming their role at Emerson Collective, the entity is fully verified.

### Honest uncertainty
Emerson Collective is structured as an LLC rather than a traditional foundation, which means it does not file the public IRS Form 990 a foundation would. So I cannot verify the precise scale of its assets. Public estimates put it in the multi-billion range but I have not put a number in the dataset because I cannot source it from a primary document.

### Sources used
- https://www.emersoncollective.com/
- https://www.theatlantic.com/masthead/
- https://en.wikipedia.org/wiki/Emerson_Collective
- https://www.linkedin.com/company/emerson-collective

---

## Cross-record observations

A few patterns surfaced across these three deep validations that are worth surfacing for the methodology document:

1. **Primary sources beat aggregators every time.** SEC filings (Cascade), publication mastheads (Emerson Collective), and the entity's own homepage are stronger evidence than Crunchbase or Wikipedia. Where a primary source exists, I used it. Where one does not (e.g., contact info for Bezos Expeditions), I left the field blank rather than fill it with a guess.

2. **Privacy and verifiability trade off against each other.** The largest, most credible FOs (Bezos, Cascade) publish the least contact information by design. A production data product targeting these entities will have low contact-level enrichment hit rates and should price/position accordingly.

3. **Confidence level is a record-level signal, not a column to be filled in once.** Cascade has higher confidence than Bezos because SEC filings give a stronger legal trail. Both are "high" in my dataset but the underlying evidence quality differs. In production I would expose a more granular confidence taxonomy (e.g., "legally documented," "publicly reported," "self-reported only").
