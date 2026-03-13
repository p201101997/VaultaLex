"""
LegacyVault — Synthetic Data Generator
Digital Estate Planning Platform: consolidating assets, documents, beneficiaries
and legal instructions in one secure place.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_all(seed=42):
    np.random.seed(seed)
    random.seed(seed)

    N     = 2000
    START = datetime(2022, 1, 1)
    END   = datetime(2026, 3, 1)

    TIERS   = ['Free', 'Basic', 'Premium', 'Family']
    PRICES  = {'Free': 0, 'Basic': 9, 'Premium': 24, 'Family': 49}
    T_W     = [0.35, 0.28, 0.25, 0.12]

    CHANNELS = ['Organic Search','Paid Ads','Referral','Social Media','Email Campaign','Partner']
    C_W      = [0.30, 0.22, 0.18, 0.15, 0.10, 0.05]
    C_CAC    = {'Organic Search':18,'Paid Ads':72,'Referral':12,'Social Media':45,'Email Campaign':28,'Partner':35}

    REASONS  = ['Price Sensitivity','Low Engagement','Missing Features','Security Concern','Competitor Switch','Life Event','Technical Issues']
    R_W      = [0.25,0.22,0.18,0.12,0.10,0.08,0.05]

    STATES   = ['CA','TX','NY','FL','IL','PA','OH','GA','NC','MI','NJ','VA','WA','AZ','MA']

    ASSET_TYPES = ['Cryptocurrency','Real Property','Bank Account','Investment Portfolio','Insurance Policy','Business Ownership','Retirement Account','Intellectual Property']
    DOC_TYPES   = ['Last Will & Testament','Power of Attorney','Property Deed','Insurance Policy','Tax Return','Trust Document','Digital Will','Beneficiary Form','Investment Statement','Healthcare Directive']

    def rdate(s, e):
        delta = (e - s).days
        if delta <= 0: return s
        return s + timedelta(days=random.randint(0, delta))

    # ── CUSTOMERS ─────────────────────────────────────────────────────────────
    rows = []
    for i in range(1, N+1):
        signup = rdate(START, END - timedelta(days=60))
        tier   = np.random.choice(TIERS, p=T_W)
        ch     = np.random.choice(CHANNELS, p=C_W)
        cac    = C_CAC[ch] * np.random.uniform(0.7, 1.5)
        age    = random.randint(30, 74)

        cp = {'Free':0.42,'Basic':0.28,'Premium':0.18,'Family':0.12}[tier]
        churned = np.random.random() < cp
        cd, cr  = None, None
        if churned:
            days = random.randint(30, min(365, (END-signup).days))
            cd   = (signup+timedelta(days=days)).strftime('%Y-%m-%d')
            cr   = np.random.choice(REASONS, p=R_W)

        upgraded = tier != 'Free' and np.random.random() < 0.35
        prev = TIERS[TIERS.index(tier)-1] if upgraded and TIERS.index(tier)>0 else None
        twofa = np.random.random() < {'Free':0.30,'Basic':0.55,'Premium':0.75,'Family':0.85}[tier]
        nps   = np.random.choice(range(11), p=[0.02,0.02,0.03,0.03,0.05,0.07,0.10,0.15,0.20,0.18,0.15])

        # Estate completeness — higher tiers = more complete
        base_comp = {'Free':0.18,'Basic':0.40,'Premium':0.68,'Family':0.82}[tier]
        tenure_days = (END - signup).days
        tenure_boost = min(0.20, tenure_days / 730 * 0.20)
        estate_comp = min(0.99, base_comp + tenure_boost + np.random.uniform(-0.10, 0.10))

        # Beneficiaries assigned
        max_bene = {'Free':1,'Basic':3,'Premium':6,'Family':10}[tier]
        bene_count = random.randint(0, max_bene) if not churned else random.randint(0, max(1,max_bene//2))

        # Platforms previously used (consolidation metric)
        platforms_replaced = {'Free':1,'Basic':2,'Premium':4,'Family':6}[tier] + random.randint(-1,2)
        platforms_replaced = max(0, platforms_replaced)

        # Digital / crypto
        has_crypto = np.random.random() < {'Free':0.15,'Basic':0.28,'Premium':0.45,'Family':0.52}[tier]

        # Testamentary readiness
        test_ready = estate_comp * (0.7 + 0.3*(bene_count > 0)) * np.random.uniform(0.85,1.15)
        test_ready = min(1.0, test_ready)

        # Legal advisory
        legal_ready = np.random.beta(2,6) if tier in ['Free','Basic'] else np.random.beta(4,3)

        # CLV
        avg_tenure_mo = {'Free':8,'Basic':18,'Premium':28,'Family':36}[tier]
        clv = PRICES[tier] * avg_tenure_mo * np.random.uniform(0.8,1.3)

        churn_score   = np.random.beta(2,5) if not churned else np.random.beta(5,2)
        upgrade_prop  = np.random.beta(3,4) if tier in ['Free','Basic'] else np.random.beta(1,5)
        uplift        = np.random.uniform(0.02, 0.45)

        rows.append(dict(
            customer_id=f'CUST{i:04d}',
            signup_date=signup.strftime('%Y-%m-%d'),
            age=age, state=random.choice(STATES),
            acquisition_channel=ch, cac_usd=round(cac,2),
            subscription_tier=tier, previous_tier=prev,
            tier_price_monthly=PRICES[tier],
            is_churned=int(churned), churn_date=cd, churn_reason=cr,
            two_fa_enabled=int(twofa), nps_score=nps,
            estate_completeness_score=round(estate_comp,4),
            beneficiaries_assigned=bene_count,
            platforms_consolidated=platforms_replaced,
            has_crypto_assets=int(has_crypto),
            testamentary_readiness_score=round(test_ready,4),
            legal_advisory_readiness_score=round(legal_ready,4),
            clv_predicted_usd=round(clv,2),
            churn_probability_score=round(churn_score,4),
            upgrade_propensity_score=round(upgrade_prop,4),
            uplift_score=round(uplift,4),
        ))
    customers = pd.DataFrame(rows)

    # ── MONTHLY REVENUE ────────────────────────────────────────────────────────
    months = pd.date_range('2022-01-01','2026-03-01',freq='MS')
    mrr_rows = []
    for m in months:
        active = customers[
            (pd.to_datetime(customers['signup_date']) <= m) &
            ((customers['churn_date'].isna()) |
             (pd.to_datetime(customers['churn_date'].fillna('2099-01-01')) > m))
        ]
        for t in TIERS:
            ts  = active[active['subscription_tier']==t]
            new = customers[
                (pd.to_datetime(customers['signup_date']).dt.to_period('M')==m.to_period('M')) &
                (customers['subscription_tier']==t)
            ]
            chu = customers[
                (pd.to_datetime(customers['churn_date'].fillna('2099-01-01')).dt.to_period('M')==m.to_period('M')) &
                (customers['subscription_tier']==t)
            ]
            mrr_rows.append(dict(
                month=m.strftime('%Y-%m'), tier=t,
                active_subscribers=len(ts),
                mrr_usd=len(ts)*PRICES[t],
                new_subscribers=len(new),
                churned_subscribers=len(chu),
                arr_usd=len(ts)*PRICES[t]*12,
            ))
    monthly_revenue = pd.DataFrame(mrr_rows)

    # ── ASSETS (what users are storing) ───────────────────────────────────────
    asset_rows = []
    asset_value_range = {
        'Cryptocurrency':      (500,   85000),
        'Real Property':       (80000, 900000),
        'Bank Account':        (1000,  120000),
        'Investment Portfolio':(5000,  400000),
        'Insurance Policy':    (10000, 500000),
        'Business Ownership':  (20000, 2000000),
        'Retirement Account':  (10000, 600000),
        'Intellectual Property':(500,  50000),
    }
    adoption_by_tier = {
        'Cryptocurrency':       {'Free':0.15,'Basic':0.28,'Premium':0.45,'Family':0.52},
        'Real Property':        {'Free':0.12,'Basic':0.35,'Premium':0.62,'Family':0.80},
        'Bank Account':         {'Free':0.60,'Basic':0.78,'Premium':0.90,'Family':0.95},
        'Investment Portfolio': {'Free':0.10,'Basic':0.30,'Premium':0.58,'Family':0.72},
        'Insurance Policy':     {'Free':0.20,'Basic':0.42,'Premium':0.68,'Family':0.82},
        'Business Ownership':   {'Free':0.04,'Basic':0.10,'Premium':0.22,'Family':0.30},
        'Retirement Account':   {'Free':0.18,'Basic':0.40,'Premium':0.65,'Family':0.78},
        'Intellectual Property':{'Free':0.03,'Basic':0.08,'Premium':0.15,'Family':0.20},
    }
    for _, c in customers.iterrows():
        for atype in ASSET_TYPES:
            if np.random.random() < adoption_by_tier[atype][c['subscription_tier']]:
                lo, hi = asset_value_range[atype]
                val = np.random.lognormal(mean=np.log((lo+hi)/2), sigma=0.6)
                val = max(lo, min(hi*2, val))
                asset_rows.append(dict(
                    customer_id=c['customer_id'],
                    tier=c['subscription_tier'],
                    asset_type=atype,
                    estimated_value_usd=round(val,2),
                    registered_date=rdate(
                        datetime.strptime(c['signup_date'],'%Y-%m-%d'), END
                    ).strftime('%Y-%m-%d'),
                    is_crypto=int(atype=='Cryptocurrency'),
                ))
    assets = pd.DataFrame(asset_rows)

    # ── DOCUMENTS (what users are uploading) ──────────────────────────────────
    doc_rows = []
    doc_adoption = {
        'Last Will & Testament': {'Free':0.08,'Basic':0.28,'Premium':0.58,'Family':0.72},
        'Power of Attorney':     {'Free':0.06,'Basic':0.22,'Premium':0.48,'Family':0.65},
        'Property Deed':         {'Free':0.05,'Basic':0.18,'Premium':0.40,'Family':0.55},
        'Insurance Policy':      {'Free':0.22,'Basic':0.45,'Premium':0.68,'Family':0.80},
        'Tax Return':            {'Free':0.30,'Basic':0.52,'Premium':0.72,'Family':0.85},
        'Trust Document':        {'Free':0.02,'Basic':0.08,'Premium':0.28,'Family':0.50},
        'Digital Will':          {'Free':0.04,'Basic':0.12,'Premium':0.35,'Family':0.55},
        'Beneficiary Form':      {'Free':0.15,'Basic':0.38,'Premium':0.65,'Family':0.80},
        'Investment Statement':  {'Free':0.12,'Basic':0.35,'Premium':0.60,'Family':0.75},
        'Healthcare Directive':  {'Free':0.05,'Basic':0.18,'Premium':0.40,'Family':0.60},
    }
    for _, c in customers.iterrows():
        for dtype in DOC_TYPES:
            if np.random.random() < doc_adoption[dtype][c['subscription_tier']]:
                doc_rows.append(dict(
                    customer_id=c['customer_id'],
                    tier=c['subscription_tier'],
                    doc_type=dtype,
                    upload_date=rdate(
                        datetime.strptime(c['signup_date'],'%Y-%m-%d'), END
                    ).strftime('%Y-%m-%d'),
                    verified=int(np.random.random()<0.72),
                    size_kb=random.randint(50,4500),
                ))
    documents = pd.DataFrame(doc_rows)

    # ── ESTATE COMPLETENESS BREAKDOWN (per user, per section) ─────────────────
    estate_sections = ['Personal Info','Asset Registry','Document Vault',
                       'Beneficiary Setup','Password Vault','Legal Instructions']
    section_comp_rows = []
    for _, c in customers.iterrows():
        base = {'Free':0.2,'Basic':0.45,'Premium':0.70,'Family':0.85}[c['subscription_tier']]
        for sec in estate_sections:
            weight = {'Personal Info':0.95,'Asset Registry':0.55,'Document Vault':0.50,
                      'Beneficiary Setup':0.45,'Password Vault':0.60,'Legal Instructions':0.30}
            tier_w = weight[sec]
            comp = min(1.0, max(0.0, base * tier_w + np.random.uniform(-0.15,0.15)))
            section_comp_rows.append(dict(
                customer_id=c['customer_id'],
                tier=c['subscription_tier'],
                section=sec,
                completion=round(comp,4),
            ))
    estate_sections_df = pd.DataFrame(section_comp_rows)

    # ── SESSIONS ──────────────────────────────────────────────────────────────
    sess_rows, sid = [], 1
    for _, c in customers[customers['is_churned']==0].sample(600,random_state=42).iterrows():
        sd = datetime.strptime(c['signup_date'],'%Y-%m-%d')
        hi_map = {'Free':6,'Basic':15,'Premium':27,'Family':42}
        lo_map = {'Free':2,'Basic':5,'Premium':9,'Family':14}
        n = random.randint(lo_map[c['subscription_tier']], hi_map[c['subscription_tier']])
        for _ in range(n):
            d = rdate(sd, END)
            sess_rows.append(dict(
                session_id=f'SES{sid:06d}',
                customer_id=c['customer_id'],
                session_date=d.strftime('%Y-%m-%d'),
                duration_minutes=round(np.random.gamma(3,4),1),
                tier=c['subscription_tier'],
                pages_visited=random.randint(2,15),
                features_accessed=random.randint(1,6),
            ))
            sid += 1
    sessions = pd.DataFrame(sess_rows)

    # ── FEATURE USAGE ─────────────────────────────────────────────────────────
    FEATURES = ['Document Upload','Password Vault','Asset Registry','Beneficiary Designation','Legal Advisory']
    f_adopt = {
        'Document Upload':        {'Free':0.50,'Basic':0.70,'Premium':0.88,'Family':0.92},
        'Password Vault':         {'Free':0.35,'Basic':0.60,'Premium':0.82,'Family':0.88},
        'Asset Registry':         {'Free':0.20,'Basic':0.45,'Premium':0.75,'Family':0.80},
        'Beneficiary Designation':{'Free':0.15,'Basic':0.40,'Premium':0.72,'Family':0.85},
        'Legal Advisory':         {'Free':0.05,'Basic':0.12,'Premium':0.40,'Family':0.55},
    }
    feat_rows = []
    for _, c in customers.iterrows():
        for feat in FEATURES:
            if np.random.random() < f_adopt[feat][c['subscription_tier']]:
                lam = {'Free':2,'Basic':5,'Premium':10,'Family':14}[c['subscription_tier']]
                feat_rows.append(dict(
                    customer_id=c['customer_id'], feature=feat, adopted=1,
                    usage_count=max(1,int(np.random.poisson(lam))),
                    last_used_date=rdate(
                        datetime.strptime(c['signup_date'],'%Y-%m-%d'), END
                    ).strftime('%Y-%m-%d'),
                    tier=c['subscription_tier'],
                ))
    feature_usage = pd.DataFrame(feat_rows)

    # ── SECURITY EVENTS ────────────────────────────────────────────────────────
    etypes = ['Failed Login Attempt','2FA Enabled','2FA Disabled','Vault Access',
              'Password Reset','Suspicious IP Flagged','Document Encrypted','Beneficiary Updated']
    erisk  = {'Failed Login Attempt':'High','2FA Enabled':'Low','2FA Disabled':'High',
              'Vault Access':'Low','Password Reset':'Medium','Suspicious IP Flagged':'High',
              'Document Encrypted':'Low','Beneficiary Updated':'Medium'}
    e_rows, eid = [], 1
    for _, c in customers.sample(1200,random_state=7).iterrows():
        sd = datetime.strptime(c['signup_date'],'%Y-%m-%d')
        for _ in range(random.randint(1,10)):
            et  = np.random.choice(etypes, p=[0.20,0.18,0.05,0.25,0.12,0.05,0.10,0.05])
            res = 1 if erisk[et]!='High' else int(np.random.random()<0.75)
            e_rows.append(dict(
                event_id=f'SEC{eid:06d}', customer_id=c['customer_id'],
                event_date=rdate(sd,END).strftime('%Y-%m-%d'),
                event_type=et, risk_level=erisk[et], resolved=res,
                tier=c['subscription_tier'],
            ))
            eid += 1
    security_events = pd.DataFrame(e_rows)

    # ── RFM SEGMENTATION ──────────────────────────────────────────────────────
    rfm_rows = []
    for _, c in customers.iterrows():
        sd  = datetime.strptime(c['signup_date'],'%Y-%m-%d')
        dss = (END-sd).days
        rec  = random.randint(1, min(365,max(1,dss)))
        freq = max(1,int(np.random.poisson({'Free':2,'Basic':6,'Premium':12,'Family':18}[c['subscription_tier']])))
        mon  = PRICES[c['subscription_tier']] * random.randint(1,24)
        rs = 5 if rec<=30 else 4 if rec<=90 else 3 if rec<=180 else 2 if rec<=270 else 1
        fs = 5 if freq>=15 else 4 if freq>=10 else 3 if freq>=5 else 2 if freq>=2 else 1
        ms = 5 if mon>=400 else 4 if mon>=200 else 3 if mon>=100 else 2 if mon>=50 else 1
        tot = rs+fs+ms
        seg = 'Champions' if tot>=13 else 'Loyal Customers' if tot>=10 else 'Potential Loyalists' if tot>=8 else 'At Risk' if tot>=6 else 'Hibernating'
        rfm_rows.append(dict(
            customer_id=c['customer_id'], tier=c['subscription_tier'],
            recency_days=rec, frequency_logins=freq, monetary_value_usd=mon,
            r_score=rs, f_score=fs, m_score=ms, rfm_total=tot, rfm_segment=seg,
        ))
    rfm = pd.DataFrame(rfm_rows)

    # ── COHORT RETENTION ──────────────────────────────────────────────────────
    cohort_rows = []
    for cm in pd.date_range('2022-01-01','2025-06-01',freq='MS'):
        cohort = customers[pd.to_datetime(customers['signup_date']).dt.to_period('M')==cm.to_period('M')]
        if len(cohort)==0: continue
        cs = len(cohort)
        for p in range(13):
            ck = cm + pd.DateOffset(months=p)
            if ck > pd.Timestamp(END): break
            ret = cohort[(pd.to_datetime(cohort['churn_date'].fillna('2099-01-01')) > ck) | cohort['churn_date'].isna()]
            cohort_rows.append(dict(
                cohort_month=cm.strftime('%Y-%m'), period_month=p,
                cohort_size=cs, retained_customers=len(ret),
                retention_rate=round(len(ret)/cs,4),
            ))
    cohort = pd.DataFrame(cohort_rows)

    # ── A/B TESTS ─────────────────────────────────────────────────────────────
    tests = [
        ('ABT001','Onboarding: Estate Wizard vs DIY',       'Onboarding',       '2023-03-01','2023-04-01'),
        ('ABT002','Pricing Page: Value-Led vs Feature-Led', 'Conversion',       '2023-06-01','2023-07-01'),
        ('ABT003','Re-engagement: Estate Gap Nudge',        'Retention',        '2023-09-01','2023-10-01'),
        ('ABT004','Legal Advisory Upsell Banner',           'Upsell',           '2024-01-01','2024-02-01'),
        ('ABT005','Security Trust Badge Placement',         'Trust',            '2024-03-01','2024-04-01'),
        ('ABT006','Family Plan: Legacy Story Messaging',    'Upsell',           '2024-06-01','2024-07-01'),
        ('ABT007','Crypto Asset Setup Prompt',              'Feature Adoption', '2024-09-01','2024-10-01'),
        ('ABT008','Digital Will: Guided vs Blank Template', 'Feature Adoption', '2025-01-01','2025-02-01'),
        ('ABT009','Beneficiary Setup Wizard v2',            'Feature Adoption', '2025-04-01','2025-05-01'),
        ('ABT010','Churn Winback: Estate Reminder',         'Retention',        '2025-07-01','2025-08-01'),
    ]
    ab_rows = []
    for tid,tname,cat,ts,te in tests:
        bc = random.uniform(0.05,0.20)
        for var in ['Control','Treatment']:
            n    = random.randint(300,800)
            lift = random.uniform(-0.02,0.12) if var=='Treatment' else 0
            cr   = min(0.99, bc+lift)
            conv = int(n*cr)
            ab_rows.append(dict(
                test_id=tid, test_name=tname, category=cat,
                start_date=ts, end_date=te, variant=var, sample_size=n,
                conversions=conv, conversion_rate=round(cr,4),
                revenue_impact_usd=round(conv*PRICES['Basic']*random.uniform(1.5,4.0),2),
                statistical_significance=round(random.uniform(0.70,0.99),3),
            ))
    ab_tests = pd.DataFrame(ab_rows)

    # ── TIER TRANSITIONS ──────────────────────────────────────────────────────
    transitions = [('Free','Basic'),('Basic','Premium'),('Premium','Family'),
                   ('Free','Premium'),('Basic','Family'),
                   ('Premium','Basic'),('Family','Premium'),('Basic','Free')]
    t_rows = []
    for f,t in transitions:
        base = customers[customers['subscription_tier']==f]
        n    = int(len(base)*random.uniform(0.05,0.22))
        t_rows.append(dict(
            from_tier=f, to_tier=t,
            direction='Upgrade' if PRICES[t]>PRICES[f] else 'Downgrade',
            customers_transitioned=n,
            revenue_impact_monthly_usd=n*(PRICES[t]-PRICES[f]),
            avg_days_before_transition=random.randint(30,365),
        ))
    tier_transitions = pd.DataFrame(t_rows)

    # ── MRR FORECAST ──────────────────────────────────────────────────────────
    last_mrr = monthly_revenue[monthly_revenue['month']=='2026-03'].groupby('tier')['mrr_usd'].sum().to_dict()
    fc_rows = []
    for i,m in enumerate(pd.date_range('2026-04-01','2026-12-01',freq='MS'),1):
        for t in TIERS:
            g = {'Free':0.01,'Basic':0.025,'Premium':0.035,'Family':0.04}[t]
            p = last_mrr.get(t,0)*((1+g)**i)
            fc_rows.append(dict(
                forecast_month=m.strftime('%Y-%m'), tier=t,
                projected_mrr_usd=round(p,2),
                lower_bound_usd=round(p*0.88,2),
                upper_bound_usd=round(p*1.12,2),
                forecast_horizon_months=i,
            ))
    mrr_forecast = pd.DataFrame(fc_rows)

    return dict(
        customers=customers,
        monthly_revenue=monthly_revenue,
        assets=assets,
        documents=documents,
        estate_sections=estate_sections_df,
        sessions=sessions,
        feature_usage=feature_usage,
        security_events=security_events,
        rfm=rfm,
        cohort=cohort,
        ab_tests=ab_tests,
        tier_transitions=tier_transitions,
        mrr_forecast=mrr_forecast,
    )
