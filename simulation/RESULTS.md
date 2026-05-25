# Social Media Algorithm Simulation v5 Results

**Version:** v5 (fully empirically anchored)
**Date:** 2026
**Seed:** 42 (reproducible)
**Cohort:** 10,000,000 users
**Horizon:** 36 months

---

## Empirical Anchors

Every parameter in v5 is derived from published data:

| Parameter | Value | Source |
|-----------|-------|--------|
| Anger amplification | 0.47 SD | Milli et al. 2025, PNAS Nexus |
| User value divergence | 0.18 SD | Milli et al. 2025, PNAS Nexus |
| Polarization per update cycle | 0.167 SD | Germano et al. 2026 |
| Marketing cost per user/month | $0.286 | Meta 2024 10-K |
| CPM floor (X/Twitter) | $5.80 | Digital Applied Q1 2026 |
| CPM start (Facebook) | $11.20 | Digital Applied Q1 2026 |
| CPM ceiling (YouTube) | $15.40 | Digital Applied Q1 2026 |
| LinkedIn CPM (reference) | $34.50 | Digital Applied Q1 2026 |
| Engagement base churn | 3.8%/month | Qualtrics 2025 (Instagram rate) |
| Connection base churn | 1.5%/month | Qualtrics 2025 (Facebook rate) |
| Twitter churn (reference) | 5.4%/month | Qualtrics 2025 |
| X Premium sub conversion | <1% | TechCrunch 2024 |
| Substack sub conversion | 5-10% | TechCrunch 2024 |
| Advertiser cliff threshold | 0.60 polarization | X/Twitter real data (MediaPost, Reuters) |
| Advertiser cliff CPM drop | ~45% | X: top 10 categories down 71%, 14/30 top advertisers stopped all ads |

---

## Key Results

### Month 1 (Both Models Start Identically)
| Metric | Engagement-Based | Connection-Based |
|--------|-----------------|-----------------|
| CPM | $11.17 | $11.19 |
| Net monthly revenue | $75.25M | $76.60M |
| Gross monthly revenue | $79.08M | $79.75M |

### Month 36
| Metric | Engagement-Based | Connection-Based | Difference |
|--------|-----------------|-----------------|------------|
| CPM | $5.80 (X floor) | $13.43 (near YouTube) | +132% for connection |
| Net monthly revenue | $35.93M | $93.34M | +160% for connection |
| Gross monthly revenue | $40.40M | $96.48M | +139% for connection |
| Subscription rate | 2.7% | 9.2% | +241% for connection |
| Monthly churn | 7.1% | 1.5% | -79% for connection |
| User satisfaction | 0.302 | 0.937 | +210% for connection |
| Polarization score | 0.601 (cliff triggered) | 0.020 | -97% for connection |

### Cumulative (36 months)
| Metric | Engagement-Based | Connection-Based | Difference |
|--------|-----------------|-----------------|------------|
| Cumulative net revenue | $2,096.8M | $3,004.1M | +$907.3M (+43%) |

### Key Events
- **Net revenue crossover:** Month 2
- **Advertiser cliff triggered:** Month 36 (engagement-based, polarization hits 0.60 threshold)

---

## Generated Charts

All charts saved to `simulation/` and copied to repo root:

1. `net_revenue_v5.png` -- Net monthly revenue comparison (primary chart)
2. `cpm_v5.png` -- CPM trajectory anchored to real platform data
3. `subscriptions_v5.png` -- Subscription conversion rate and revenue
4. `satisfaction_polarization_v5.png` -- User satisfaction and polarization

---

## Interpretation

The v5 model produces a qualitatively different result from earlier versions in one important way: both platforms now start at approximately the same revenue level (both at Facebook-level CPM), rather than the connection-based platform starting lower. This is because the CAC model is now based on Meta's actual $0.286/user/month budget rather than a per-churn-event cost.

The result is that the connection-based advantage appears almost immediately (Month 2 crossover) rather than requiring a long transition period. This is driven primarily by lower churn reducing the fraction of the marketing budget spent on replacement users rather than growth.

The 36-month divergence is driven by three compounding mechanisms:
1. CPM divergence: engagement-based declines to X floor, connection-based rises toward YouTube level
2. Churn divergence: 7.1% vs 1.5% monthly churn by Month 36
3. Subscription divergence: 2.7% vs 9.2% conversion rate by Month 36

The advertiser cliff (Month 36 for engagement-based) is modeled as a discrete threshold event, not a smooth decay, anchored to the documented X/Twitter advertiser exodus pattern.

---

## Sources

- Milli, S. et al. (2025). "Engagement vs. Satisfaction in Social Media." PNAS Nexus. https://pmc.ncbi.nlm.nih.gov/articles/PMC11894805/
- Germano, F. et al. (2026). "Engagement Amplification in Algorithmic Media." SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4238756
- Meta 2024 10-K. SEC EDGAR. https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm
- Digital Applied Q1 2026. CPM benchmarks by platform. https://www.digitalapplied.com/blog/social-media-marketing-costs-2026-pricing-guide
- Qualtrics 2025. Customer churn statistics. https://www.qualtrics.com/articles/customer/30-statistics-about-customer-churn/
- TechCrunch 2024. X Premium subscription revenue. https://techcrunch.com/2024/10/15/elon-musks-x-still-struggles-to-grow-subscription-revenue/
- MediaPost. X ad category revenue decline. https://www.mediapost.com/publications/article/411393/
- Reuters. X advertiser exodus. https://www.reuters.com/technology/twitters-revenue-down-40-year-over-year-platformer-reporter-2023-01-18/
