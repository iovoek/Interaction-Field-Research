# Research Notes: Profiles, Datasets, and Citations

## Researcher Profiles

### Smitha Milli
- **Website:** http://smithamilli.com/
- **Twitter/X:** https://x.com/SmithaMilli
- **Google Scholar:** https://scholar.google.com/citations?user=tsXh_hwAAAAJ&hl=en
- **Affiliation:** Research Scientist at Meta FAIR; PhD from UC Berkeley (EECS)
- **Key paper:** Milli, S. et al. (2025). "Engagement, user satisfaction, and the amplification of divisive content on social media." PNAS Nexus, 4(3), pgaf062. https://pmc.ncbi.nlm.nih.gov/articles/PMC11894805/
- **Paper data/code:** https://github.com/smilli/twitter | https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/1QMLOV
- **Key finding:** Twitter's engagement-based algorithm amplifies emotionally charged, out-group hostile content. Users do NOT prefer the algorithm-selected political tweets over a reverse-chronological baseline. Stated preferences diverge from revealed preferences.

### W. Brian Arthur
- **SFI Profile:** https://www.santafe.edu/people/profile/w-brian-arthur
- **Google Scholar:** https://scholar.google.com/citations?user=eczJRhQAAAAJ&hl=en
- **LinkedIn:** https://www.linkedin.com/in/w-brian-arthur-71b9065
- **YouTube talks:** https://www.youtube.com/watch?v=noAn60dlk04 | https://www.youtube.com/watch?v=ldAFHNpDbjY | https://www.youtube.com/watch?v=kyXZtp-Htu8
- **Affiliation:** External Faculty, Santa Fe Institute; IBM Faculty Fellow; Visiting Researcher at PARC

### Leroy Hood MD PhD
- **ISB Profile:** https://isbscience.org/people/leroy-hood-md-phd/
- **Google Scholar:** https://scholar.google.com/citations?user=TQ8RcVgAAAAJ&hl=en
- **Twitter/X:** https://x.com/ISBLeeHood
- **LinkedIn:** https://www.linkedin.com/in/leehood111
- **YouTube:** https://www.youtube.com/watch?v=wHd-BHAw6QM | https://www.youtube.com/watch?v=KRm_b5XcRpQ

### Dami Lee (Nollistudio)
- **YouTube:** https://www.youtube.com/@DamiLeeArch (2.35M subscribers)
- **Instagram:** https://www.instagram.com/damileearch/ (760K followers)
- **Website:** https://damilee.com/
- **LinkedIn:** https://ca.linkedin.com/in/damilee

### Huni Choi
- **Instagram:** https://www.instagram.com/hunichoipyramid/
- **YouTube video:** https://www.youtube.com/watch?v=h5kWDOuY2Uo
- **Note:** Primarily known for pyramid theory/pyramidology content

### History for GRANITE
- **YouTube:** https://www.youtube.com/@HistoryforGRANITE (331K subscribers, 174 videos)
- **Facebook:** https://www.facebook.com/profile.php?id=100087258871624
- **Merch:** https://history-for-granite.creator-spring.com

### Germano, Gómez, Sobbrio
- **Paper:** "Ranking for engagement: How social media algorithms fuel misinformation and polarization"
- **SSRN:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4238756
- **DOI:** https://doi.org/10.1016/j.jpubeco.2026.105589
- **Germano Google Scholar:** https://scholar.google.com/citations?user=BETtBGEAAAAJ&hl=en
- **Gómez Twitter/X:** https://x.com/vicen__gomez
- **Key finding:** Facebook's 2018 "Meaningful Social Interactions" update increased ideological extremism and affective polarization. Increasing weight on social interactions (likes, shares) increases engagement BUT also misinformation and polarization.

### Peter N. Robinson
- **Institutional Profile:** https://www.bihealth.org/en/research/research-group/medical-computer-science-and-artificial-intelligence
- **Google Scholar:** https://scholar.google.com/citations?user=TPOD_XUAAAAJ&hl=en
- **Twitter/X:** https://twitter.com/pnrobins
- **LinkedIn:** https://www.linkedin.com/in/peter-n-robinson-b7833811
- **HPO Website:** http://www.human-phenotype-ontology.org
- **GitHub:** https://robinsongroup.github.io/

---

## Key Datasets

### Social Media
- **Milli et al. paper data:** https://github.com/smilli/twitter (code for Twitter algorithmic audit)
- **Harvard Dataverse (Eady 2024):** https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/1QMLOV (News sharing ideology mapping)
- **Reddit engagement dataset (Kaggle):** https://www.kaggle.com/datasets/datancoffee/predicting-reddit-community-engagement-dataset
- **Stanford SNAP:** https://snap.stanford.edu/data/ (50+ large social network datasets)
- **Pew Research 2025 Social Media Fact Sheet:** https://www.pewresearch.org/internet/fact-sheet/social-media/

### Pharmaceutical
- **BIO Clinical Development Success Rates 2011-2020:** https://www.bio.org/clinical-development-success-rates-and-contributing-factors-2011-2020
- **BIO PDF Report:** https://go.bio.org/rs/490-EHZ-999/images/ClinicalDevelopmentSuccessRates2011_2020.pdf
- **ClinicalTrials.gov trends:** https://clinicaltrials.gov/about-site/trends-charts
- **FDA Drug Approvals Data:** https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files
- **Key stat from BIO report:** Overall likelihood of approval from Phase I = 7.9% (not 10% as commonly cited). Phase II success rate = 28.9%.

---

## Key Statistics for Simulation Calibration

### Social Media (from Milli et al. 2025 and Germano et al.)
- Twitter's engagement algorithm amplifies out-group hostile content vs. reverse-chronological baseline
- Users do NOT prefer algorithm-selected political tweets (stated vs. revealed preference divergence)
- Facebook's 2018 MSI update increased polarization (Germano et al.)
- These are qualitative directional findings, not exact percentages for calibration

### Pharmaceutical (from BIO 2011-2020 report)
- Phase I to approval: 7.9% (not 10%)
- Phase I success rate: ~63%
- Phase II success rate: 28.9% (this is the biggest bottleneck)
- Phase III success rate: ~57%
- NDA/BLA to approval: 90.6%
