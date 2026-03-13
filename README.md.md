# ⚖️ VaultaLex — Analytics Command Center

> **Digital Estate Planning & Legal Documentation Platform**  
> *Secure Your Legacy — one platform for assets, documents, beneficiaries & testamentary instructions.*

## Platform Overview

VaultaLex addresses the market gap where critical documents, passwords, investments and property records are scattered across multiple platforms. Users consolidate everything into one secure vault:

- **Asset Registry** — Crypto, real property, investments, retirement, insurance, business ownership
- **Document Vault** — Wills, digital wills, POAs, trust documents, healthcare directives, deeds
- **Beneficiary Management** — Assign and track beneficiaries per asset
- **Testamentary Instructions** — Guided legal documentation and digital will creation
- **Legal Advisory** — Premium tier: query resolution & guided legal documentation

---

## Repository Structure

```
vaultalex-dashboard/
├── app.py                        ← Main Streamlit app (4 analytics layers)
├── requirements.txt              ← Dependencies
├── README.md
├── .gitignore
├── assets/
│   └── vaultalex_logo.png        ← Brand logo (required for header & sidebar)
├── .streamlit/
│   └── config.toml               ← Dark navy/silver theme
├── data/
│   └── generate.py               ← Synthetic data generator (13 datasets, seed=42)
└── reports/
    └── pdf_generator.py          ← ReportLab PDF engine (4 branded reports)
```

---

## Deploy to Streamlit Cloud

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "VaultaLex Analytics Command Center — initial deploy"
git remote add origin https://github.com/YOUR_USERNAME/vaultalex-dashboard.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your repo: `YOUR_USERNAME/vaultalex-dashboard`
4. Main file path: `app.py`
5. Click **Deploy**

> No CSV uploads needed — all data generated on first load via `data/generate.py` (seed=42, fully deterministic).

---

## Analytics Layers

| Layer | Purpose | Key Charts |
|-------|---------|-----------|
| 📊 **Descriptive** | What is happening | Estate completeness, asset portfolio, document vault, MRR, CAC, platform consolidation |
| 🔍 **Diagnostic** | Why it's happening | RFM segmentation, cohort retention heatmap, churn root cause, feature-retention, tier funnels |
| 🔮 **Predictive** | What will happen | Churn risk scoring, CLV by tier, MRR 9-month forecast, legal advisory pipeline |
| 🧭 **Prescriptive** | What to do | A/B test results, estate gap map, at-risk intervention table, LTV:CAC, uplift scores |

---

## Synthetic Datasets (seed=42)

| Dataset | Rows | Description |
|---------|------|-------------|
| `customers` | 2,000 | Subscribers with estate scores, crypto flags, platform consolidation count |
| `monthly_revenue` | 204 | MRR / ARR by tier and month |
| `assets` | ~5,800 | 8 asset types registered per user |
| `documents` | ~6,500 | 10 document types in the vault |
| `estate_sections` | 12,000 | Completion % per estate section per user |
| `sessions` | ~8,300 | Session activity and engagement |
| `feature_usage` | ~4,800 | Feature adoption by subscriber |
| `security_events` | ~6,700 | Vault security events |
| `rfm` | 2,000 | RFM segmentation scores |
| `cohort` | 540 | Monthly cohort retention curves |
| `ab_tests` | 20 | 10 estate-planning A/B experiments |
| `tier_transitions` | 8 | Upgrade / downgrade flow |
| `mrr_forecast` | 36 | 9-month MRR projection with confidence bands |

---

## Subscription Tiers

| Tier | Price | Key Features |
|------|-------|-------------|
| Free | $0/mo | Basic vault, 1 beneficiary |
| Basic | $9/mo | Full vault, 3 beneficiaries, document uploads |
| Premium | $24/mo | All features, 6 beneficiaries, legal advisory access |
| Family | $49/mo | Everything, 10 beneficiaries, family estate management |

---

## PDF Export

Each analytics layer has a branded **PDF Report** button. Reports are generated on-demand using ReportLab (no Kaleido / screenshot dependency) and reflect current sidebar filters.

Reports include: branded cover page, KPI summaries, charts, data tables and strategic insight callouts — all in the VaultaLex dark navy/silver executive theme.

---

*VaultaLex — Digital Estate Security*
