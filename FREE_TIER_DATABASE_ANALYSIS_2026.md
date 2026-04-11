# Free Tier Database Analysis 2026
## FastAPI-Compatible SQL Databases for 500 Users

**Analysis Date:** April 10, 2026  
**Requirements:**
- 500 users (not 1000)
- 100 sessions per user = 50K total sessions
- ~5-10MB metadata storage (50K records × 100-200 bytes)
- FastAPI async compatibility
- SQL aggregation support for recommendations

---

## Executive Summary

Only **3 out of 8** evaluated options are genuinely viable for your use case without surprise charges.

| Database | Year 1 Cost | Year 2+ (1K users) | Verdict |
|----------|------------|------------------|---------|
| **Neon** | $0 | ~$45-90/mo | ✅ VIABLE |
| **Supabase** | $0 | ~$25+/mo | ✅ VIABLE |
| **CockroachDB** | $0 | ~$50-200/mo | ✅ VIABLE |
| Firebase | $0 → Hidden costs | Unpredictable | ❌ NOT VIABLE |
| Railway | $0 (expires in 30 days) | $6-120/mo | ❌ NOT VIABLE |
| Render | $0 | $6-120/mo | ⚠️ MARGINAL |
| PlanetScale | Deprecated | N/A | ❌ DEPRECATED |
| MongoDB Atlas | $0 → $57/mo | $200+/mo | ❌ NOT VIABLE |

---

## Detailed Evaluations

### 1. ✅ NEON (VIABLE)

**URL:** https://neon.tech/pricing

#### Pricing Details
- **Free tier:** 100 CU-hours/month, 0.5 GB storage
- **Paid (Launch):** $0.106/CU-hour, $0.35/GB-month
- **Paid (Scale):** $0.222/CU-hour, $0.35/GB-month (production features)

#### 1. Truly Free in 2026?
✅ **YES** - No auto-scaling charges. Free tier is genuinely unlimited in features, just limited in resources.

#### 2. Free Tier Storage Limit
- **0.5 GB per project** (you can create 100 projects on free tier)
- For your 5-10MB, well within limits

#### 3. Can Handle 50K Records?
✅ **YES** - 50K records × 150 bytes avg = ~7.5 MB. Easily fits in 0.5 GB.

#### 4. Connection Limits vs 500 Users
✅ **PERFECT MATCH**
- Free tier: Up to 2 CU autoscaling (8 GB RAM, ~100 connections)
- Launch tier: Up to 16 CU (64 GB RAM, ~500 connections)
- Your 500 users would fit in free tier, but Launch is cheap if you scale

#### 5. Read/Write Operation Limits
✅ **NO OPERATION LIMITS** - You pay for compute time (CU-hours), not operations
- 100 CU-hours free = ~4200 minutes of 1 CU compute/month
- 50K sessions = ~50K DB operations across the month = negligible
- Even with recommendations aggregations, you won't exceed 100 CU-hours

#### 6. Cost If Limits Exceeded
- **Launch:** $0.106/CU-hour beyond 100 CU-hours
- **Example:** 200 CU-hours in a month = $10.60/month
- **Scale plan:** $0.222/CU-hour (for production features like metrics export)
- No surprise auto-scaling charges; you control the bill

#### 7. FastAPI Async Driver
✅ **YES** - `asyncpg` (Python's fastest async Postgres driver)
- Direct Postgres connection support
- Perfect for FastAPI

#### 8. SQL Aggregation Support
✅ **YES** - Full Postgres = full SQL support including CTEs, window functions, GROUP BY, etc.

#### Neon Verdict: **✅ VIABLE**

**Honest Assessment:**
- Best for prototypes to early production
- **Biggest strength:** Generously true free tier with no surprise charges
- **Gotcha:** Free tier compute (100 CU-hours) would last ~18 days if you run 24/7 at 1 CU. Real-world usage (bursty) = easily lasts full month
- **Scale path:** Cheap and predictable ($0.106/CU-hour is competitive)
- **Recommendation:** Use free tier for development. Upgrade to Launch ($50-90/mo) only if you hit limits
- **Risk level:** Low

---

### 2. ✅ SUPABASE (VIABLE)

**URL:** https://supabase.com/pricing

#### Pricing Details
- **Free tier:** Unlimited API requests, 500 MB storage, 2GB bandwidth/month
- **Pro tier:** $25/month, 8 GB storage, 250 GB bandwidth/month
- **Team/Enterprise:** Custom pricing

#### 1. Truly Free in 2026?
✅ **YES** - Free tier is genuinely free. No credit card required. No auto-upgrade.

#### 2. Free Tier Storage Limit
- **500 MB per project** total (database + file storage combined)
- Your 5-10MB is trivial (1-2% of quota)
- **⚠️ GOTCHA:** If you use Supabase Storage for files, that counts toward the 500 MB

#### 3. Can Handle 50K Records?
✅ **YES** - 50K records × 150 bytes = ~7.5 MB ≪ 500 MB

#### 4. Connection Limits vs 500 Users
⚠️ **LIMITED** - Supabase uses connection pooling (PgBouncer)
- Free tier: 10 connections in pool (but multiplexed via pooler)
- Can handle concurrent requests, but not 500 simultaneous connections
- **Real-world:** FastAPI with async pooling (SQLAlchemy async) can handle 500 users with 10 connections
- **Verdict:** Will work, but you're relying on good connection pooling

#### 5. Read/Write Operation Limits
✅ **UNLIMITED** on free tier
- No request quotas
- No operation counts
- Pay-per-operation is a Firebase thing, Supabase doesn't do this
- Aggregation queries = unlimited

#### 6. Cost If Limits Exceeded
- **500 MB to 8 GB storage:** Upgrade to Pro ($25/month)
- **Beyond 8 GB:** $0.024/GB-month on Pro
- **Bandwidth:** 250 GB/month included in Pro; $0.081/GB beyond
- **Example growth scenario:**
  - Free tier: $0 (up to 500 MB)
  - Pro tier: $25/month (8 GB storage + 250 GB bandwidth)
  - Enterprise: Contact sales (but you'd need this at millions of users)
- **No surprise charges** - straightforward tiering

#### 7. FastAPI Async Driver
✅ **YES** - Postgres via async drivers (asyncpg, psycopg async)
- Also offers REST API if you prefer (though less efficient)
- Connection pooling built-in

#### 8. SQL Aggregation Support
✅ **YES** - Full Postgres

#### Supabase Verdict: **✅ VIABLE**

**Honest Assessment:**
- **Best for:** Startups wanting a "batteries included" backend (auth, storage, realtime)
- **Strength:** Free tier has NO storage limit gotchas (unlike Firebase's 1 GB), full SQL
- **Weakness:** 10 connection limit on free tier requires careful pooling
- **Scale path:** Pro tier at $25/month is well-priced for early-stage
- **Recommendation:** Choose Supabase if you want the ecosystem (auth, realtime, storage). Otherwise, Neon is cheaper.
- **Risk level:** Low-Medium (connection pooling is a real limitation if not careful)

---

### 3. ✅ COCKROACHDB (VIABLE)

**URL:** https://www.cockroachlabs.com/pricing/

#### Pricing Details
- **Free tier (Basic):** 50 million Request Units (RUs) free/month, 10 GB storage free, scales to zero
- **Standard:** $0.18/hr (2 vCPUs), on-demand storage after free tier
- **Advanced:** $0.60+/hr (4 vCPUs+), unlimited scaling

#### 1. Truly Free in 2026?
✅ **YES** - Free tier is genuinely free (no credit card required). Scales to zero (no charges when idle).

#### 2. Free Tier Storage Limit
- **10 GB free per month**
- Your 5-10 MB = 0.05-0.1% of quota
- Overage: $0.30/GB-month

#### 3. Can Handle 50K Records?
✅ **YES EASILY** - 50K records ≪ 10 GB capacity

#### 4. Connection Limits vs 500 Users
✅ **EXCELLENT** - CockroachDB is built for distributed systems
- Free tier: "Reasonable" connection limits (documentation unclear, but typically 100+)
- Standard/Advanced: 100+ connections included
- **Verdict:** Much better than Supabase for concurrent connections

#### 5. Read/Write Operation Limits
⚠️ **REQUEST UNITS (RUs) BASED**
- **50 million RUs free per month**
- 1 SQL operation = ~1-10 RUs (depends on complexity)
- 50K session records = ~50K reads/writes = ~50K RUs = ~0.1% of quota
- **Aggregation queries:** More expensive (50-500 RUs depending on join complexity)
- **Verdict:** For your scale, you'll comfortably stay in free tier

#### 6. Cost If Limits Exceeded
- **Standard tier:** $0.18/hr × 730 hrs/month = $131.40/month minimum
- **RU overage:** Generally no per-operation charges beyond tier
- **⚠️ GOTCHA:** Standard tier is expensive for small scale. Better to stay on free "Basic" tier
- **Cost jump:** Free → Standard = $131/month cliff

#### 7. FastAPI Async Driver
✅ **YES** - CockroachDB is Postgres-compatible
- Use asyncpg or SQLAlchemy async
- Drop-in Postgres replacement

#### 8. SQL Aggregation Support
✅ **YES** - Distributed SQL, full support for CTEs, window functions, joins

#### CockroachDB Verdict: **✅ VIABLE**

**Honest Assessment:**
- **Best for:** Scale-first architectures; if you anticipate explosive growth
- **Strength:** Free tier includes 50M RUs (very generous for small workloads)
- **Major weakness:** Pricing cliff between Basic (free) and Standard ($131+/month)
- **Gotcha:** Free tier "scales to zero" in terms of compute, but you're still bound to one-region
- **Scale path:** Only viable if you grow significantly (need Standard tier for multi-region)
- **Recommendation:** Good for prototypes, but Neon/Supabase have better scaling prices
- **Risk level:** Medium (pricing cliff is painful if you outgrow free tier)

---

### 4. ❌ FIREBASE (NOT VIABLE)

**URL:** https://firebase.google.com/pricing

#### Pricing Details
- **Spark plan:** 1 GB storage, 50K reads/day, 20K writes/day
- **Blaze plan (pay-as-you-go):** $0.06/100K reads, $0.18/100K writes, $5/GB storage overage

#### 1. Truly Free in 2026?
⚠️ **TECHNICALLY YES, BUT DECEPTIVE**
- No auto-scaling charges, but...
- Quota limits are harsh
- Easy to hit limits and incur surprise charges

#### 2. Free Tier Storage Limit
- **1 GB for Firestore**
- Your 5-10 MB fits, but margins are thin

#### 3. Can Handle 50K Records?
⚠️ **BARELY** - 50K records might be 50 MB if doc structure is complex
- You'd be at 5-10% of quota with no room to grow
- **Verdict:** Too tight

#### 4. Connection Limits vs 500 Users
✅ **UNLIMITED** - Firestore is serverless
- Concurrent connections = not a bottleneck

#### 5. Read/Write Operation Limits
❌ **KILLER PROBLEM**
- **50K reads/day limit** (Spark plan)
- 500 users × 100 sessions = 50K sessions
- If each session = 1 read (check if user exists), you hit quota on day 1
- If each session = 2 operations (read user + read metadata), you're over by 2x
- Blaze plan charges: $0.06 per 100K reads
  - 50K reads/day × 30 days = 1.5M reads/month = $0.90/month (cheap)
  - But add recommendation aggregations = 2-5M reads/month = $1.20-3.00/month
- **Hidden gotcha:** Read-heavy aggregations cost money

#### 6. Cost If Limits Exceeded
- Spark: Instant quota rejection (app stops working)
- Blaze: Automatic overage charges
  - Reads: $0.06/100K
  - Writes: $0.18/100K
  - Storage: $5/GB after 1 GB
  - **Example:** Heavy aggregation workload = $50-200/month easily

#### 7. FastAPI Async Driver
⚠️ **WEAK**
- Firebase Admin SDK exists for Python
- Async support is limited (not designed for heavy async workloads)
- REST API available but slower

#### 8. SQL Aggregation Support
❌ **NO BUILT-IN SQL**
- Firestore is document-based NoSQL
- Aggregations require client-side code
- No SQL JOINs, GROUP BY, etc.
- **Workaround:** Use Firebase Data Connect (built on Cloud SQL) but that's a different product

#### Firebase Verdict: **❌ NOT VIABLE**

**Honest Assessment:**
- **Why it fails:** 
  1. No native SQL support (kills your aggregation requirement)
  2. Read-heavy operations hit quota quickly
  3. Aggregations require expensive application logic
  4. Data Connect (SQL version) requires billing account
- **Surface-level appeal:** "Free tier" with high quotas
- **Reality:** You'll hit limits within 2-3 weeks of real usage
- **Recommendation:** Skip Firebase entirely. It's great for mobile apps, not backend services with SQL needs.
- **Risk level:** HIGH (will incur charges or function degradation)

---

### 5. ⚠️ RAILWAY (MARGINAL)

**URL:** https://railway.app/pricing

#### Pricing Details
- **Free tier:** $5/month free credit (effectively 1 month free)
- **Free Postgres:** 100 connections, limited storage
- **After credit:** Usage-based ($0.00000231/GB-hour for compute, $0.09/GB-month for storage)

#### 1. Truly Free in 2026?
❌ **NO** - Free tier is a **30-day credit**, not permanent free tier
- After $5 credit expires, you pay per hour
- **Verdict:** Not truly free; designed to push toward paid plans

#### 2. Free Tier Storage Limit
- Free Postgres: ~1-2 GB estimated (not clearly documented)
- Your 5-10 MB easily fits
- Overage: $0.09/GB-month

#### 3. Can Handle 50K Records?
✅ **YES** - 50K records ≪ 2 GB

#### 4. Connection Limits vs 500 Users
✅ **100 connections** on free tier
- Enough for 500 users with proper pooling

#### 5. Read/Write Operation Limits
✅ **UNLIMITED**
- Pay for compute time, not operations
- $0.00000231/GB-hour is essentially free for small workloads

#### 6. Cost If Limits Exceeded
- After $5 credit expires (~30 days):
  - **Free Postgres:** ~$2-5/month (tiny instances)
  - **Upgraded Postgres:** $6-30/month
  - **Example at scale:** 1K users = $20-50/month
- **Gotcha:** Credit-first model is intentionally deceptive

#### 7. FastAPI Async Driver
✅ **YES** - Standard Postgres

#### 8. SQL Aggregation Support
✅ **YES** - Full Postgres

#### Railway Verdict: **⚠️ MARGINAL (NOT RECOMMENDED)**

**Honest Assessment:**
- **Why it's marginal:** Free tier is temporary (30-day credit)
- **Real cost:** $2-10/month after credit expires
- **Compared to alternatives:** Neon's free tier is permanent; Supabase's is permanent
- **When to use:** Only if you're committed to paying; not for true free tier
- **Recommendation:** If you must choose, go Neon or Supabase instead
- **Risk level:** Low (pricing is clear after credit), but not competitive

---

### 6. ❌ RENDER (NOT VIABLE)

**URL:** https://render.com/pricing

#### Pricing Details
- **Free Postgres:** 100 connections, ~1 GB implied storage, 30-day limit
- **Basic:** $6/month (256 MB)
- **Pro:** $55-3000+/month (4 GB to 256 GB+)

#### 1. Truly Free in 2026?
❌ **NO** - Free tier expires after 30 days
- Free instance requirement: Must have activity
- If no activity, instance suspends

#### 2. Free Tier Storage Limit
- Unclear documentation, implied ~1 GB
- Your 5-10 MB easily fits

#### 3. Can Handle 50K Records?
✅ **YES** - Fits in 1 GB

#### 4. Connection Limits vs 500 Users
✅ **100 connections** on free tier
- Adequate with pooling

#### 5. Read/Write Operation Limits
✅ **UNLIMITED**

#### 6. Cost If Limits Exceeded
- **After free tier:** $6/month minimum (Basic tier, 256 MB)
- Professional tier: $19/user/month (unclear if applies to databases)
- **Cost for 500 users:** Unclear pricing model

#### 7. FastAPI Async Driver
✅ **YES** - Postgres

#### 8. SQL Aggregation Support
✅ **YES** - Full Postgres

#### Render Verdict: **❌ NOT VIABLE**

**Honest Assessment:**
- **Why:** Free tier expires after 30 days (not truly free)
- **Cost:** $6/month minimum after free tier
- **Comparison:** Railway and Render both have "free credits" but not permanent free tiers
- **Recommendation:** Pass. Use Neon instead (same features, truly free)
- **Risk level:** Low (but not competitive)

---

## Cost Comparison: Year 1 vs Year 2+ (Scaling to 1000 users)

### Scenario Assumptions:
- **Year 1:** 500 users, 50K sessions/month, 5-10 MB storage
- **Year 2+:** 1000 users, 100K sessions/month, 20-50 MB storage
- Conservative estimates; actual costs depend on your usage patterns

---

### NEON
| Period | Cost | Details |
|--------|------|---------|
| **Year 1 (Free)** | **$0/mo** | 100 CU-hours/month easily covers usage |
| **Year 2 (Launch)** | **$45-90/mo** | Estimated 425-850 CU-hours/month at $0.106/CU-hour |
| **Year 2 (Scale)** | **$90-180/mo** | Higher rate for production features |
| **Storage overage (20-50 MB)** | **$0-0.02/mo** | Negligible |
| **Year 3+ (High traffic)** | **$100-300/mo** | If you add caching, compute-heavy aggregations |

**Total 3-year cost:** $0 + $540-1080 = **$540-1080**

---

### SUPABASE
| Period | Cost | Details |
|--------|------|---------|
| **Year 1 (Free)** | **$0/mo** | 500 MB storage, unlimited operations |
| **Year 2 (Pro)** | **$25/mo** | 8 GB storage, 250 GB bandwidth |
| **Year 2 (Pro with bandwidth)** | **$25-50/mo** | If you exceed 250 GB bandwidth (~rare) |
| **Year 3+ (Team Plan)** | **$100+/mo** | If you add team collaboration |

**Total 3-year cost:** $0 + $300-600 = **$300-600**

---

### COCKROACHDB
| Period | Cost | Details |
|--------|------|---------|
| **Year 1 (Free/Basic)** | **$0/mo** | 50M RUs easily covers usage |
| **Year 2 (Basic → Standard)** | **$131/mo** | 2 vCPUs minimum, pricing cliff |
| **Year 2 (Heavy load)** | **$200-500/mo** | If you need multi-region or larger vCPUs |
| **Year 3+ (Advanced)** | **$500+/mo** | For production-grade SLAs |

**Total 3-year cost:** $0 + ($131-500 × 12) = **$1,572-6,000**

**⚠️ GOTCHA:** Pricing cliff between free and paid tiers makes CockroachDB uncompetitive for your scale.

---

### FIREBASE
| Period | Cost | Details |
|--------|------|---------|
| **Year 1 (Spark)** | **$0-50/mo** | Quota hits + Blaze plan charges for aggregations |
| **Year 2 (Blaze)** | **$50-200/mo** | Heavy read/write operations for recommendations |
| **Year 3+ (Scale)** | **$200+/mo** | Per-operation pricing adds up |

**Total 3-year cost:** $50-600 = **$50-600** (but app may stop working due to quotas)

**⚠️ DEAL BREAKER:** No native SQL = you'll pay more for application logic.

---

### RAILWAY
| Period | Cost | Details |
|--------|------|---------|
| **Year 1 (Free)** | **$5/mo** | $5 credit, then pay-per-hour |
| **Year 1 (Actual)** | **$2-10/mo** | After credit expires |
| **Year 2** | **$20-50/mo** | Small-instance pricing |
| **Year 3+** | **$50-100/mo** | Scale with users |

**Total 3-year cost:** $15-30 + $240-600 = **$255-630**

---

### RENDER
| Period | Cost | Details |
|--------|------|---------|
| **Year 1 (Free)** | **$6/mo** | Free tier expires after 30 days |
| **Year 1 (Actual)** | **$6/mo** | Basic tier minimum |
| **Year 2** | **$6/mo** | Stays on Basic (256 MB) |
| **Year 3+** | **$25-60/mo** | If you scale to Pro tier |

**Total 3-year cost:** $6-12 + $72-180 = **$78-192**

---

## Summary Table: True Cost of Ownership

| Database | Year 1 | Year 2-3 | Total 3yr | Truly Free | SQL Support | Async | Notes |
|----------|--------|----------|----------|-----------|------------|-------|-------|
| **Neon** | **$0** | **$45-90/mo** | **$540-1,080** | ✅ Yes | ✅ Full | ✅ Yes | **BEST CHOICE** |
| **Supabase** | **$0** | **$25/mo** | **$300-600** | ✅ Yes | ✅ Full | ✅ Yes | **BEST VALUE** |
| **CockroachDB** | **$0** | **$131/mo cliff** | **$1,572+** | ✅ Yes | ✅ Full | ✅ Yes | **Pricing cliff breaks it** |
| **Firebase** | **$0-50/mo** | **$50-200/mo** | **$50-600** | ❌ No | ❌ NoSQL | ⚠️ Weak | **Kills your SQL requirement** |
| **Railway** | **$2-10/mo** | **$20-50/mo** | **$255-630** | ❌ No | ✅ Full | ✅ Yes | **Only 30-day free credit** |
| **Render** | **$6/mo** | **$6-60/mo** | **$78-600** | ❌ No | ✅ Full | ✅ Yes | **No permanent free tier** |

---

## Recommendation by Use Case

### 1. **Maximum Cost Savings** → **Supabase**
- Cheapest Year 2+: $25/month
- Most predictable growth
- No surprise charges
- Built-in Auth + Storage if needed later

**3-year cost:** $300-600

---

### 2. **Best Free Tier (Longest Runway)** → **Neon**
- Truly unlimited free tier (stays free until 100 CU-hours)
- Real-world usage = 3-6 months of free tier
- Scales from $45/month when needed
- Best async/FastAPI support

**3-year cost:** $540-1,080

---

### 3. **Most Robust Free Tier (Scalability)** → **CockroachDB**
- 50M RUs free (most generous per-operation quota)
- Scales to zero (no idle charges)
- **BUT:** Pricing cliff ($0 → $131) makes it painful for mid-scale

**3-year cost:** $1,572+ (not competitive)

---

## Final Honest Verdict

### ✅ VIABLE FINALISTS

#### **1. Neon (Recommended for longest free runway)**
- **Why:** Truly free until you hit compute limit (~3-6 months of real usage)
- **Best for:** Developers who want to prototype for free for months
- **FastAPI fit:** Perfect with asyncpg
- **Aggregations:** Full SQL support
- **Gotcha:** Free tier compute limit is per-project; solution = use multiple projects
- **Growth path:** Scales smoothly ($0.106/CU-hour is industry-competitive)

#### **2. Supabase (Recommended for best overall value)**
- **Why:** Cheapest scaling ($25/month), includes auth + storage
- **Best for:** Full-stack startups needing more than just a database
- **FastAPI fit:** Good with connection pooling
- **Aggregations:** Full SQL support
- **Gotcha:** Connection limit requires careful pooling (10 connections)
- **Growth path:** Clear tier structure; Pro at $25 is excellent value

#### **3. CockroachDB (Not recommended for your scale)**
- **Why:** Pricing cliff ($0 → $131/month) makes it uncompetitive
- **Best for:** Only if you anticipate needing multi-region distribution immediately
- **Growth path:** Expensive ($131+ minimum for Standard tier)

### ❌ TO AVOID

- **Firebase:** No native SQL (kills recommendations feature)
- **Railway/Render:** Free tier expires after 30 days (deceptive)
- **PlanetScale:** Officially deprecated (MySQL focus has ended)

---

## Final Recommendation for Your Stack

### **Choose Neon if:**
- You want maximum free tier runway (3-6 months)
- You prioritize cost savings in Year 2+
- You're building a backend service (not full-stack)
- You want the simplest async setup

### **Choose Supabase if:**
- You want an all-in-one platform (auth, DB, storage)
- You're starting a startup (integrated ecosystem matters)
- You prioritize simplicity over maximum free duration
- You want the best Year 2+ pricing

### **Choose CockroachDB if:**
- You already know you'll need multi-region replication soon
- You can afford the $131/month cliff
- You're building a globally distributed system

---

## Technical Setup Notes

### FastAPI + Neon
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:password@neon-host/dbname",
    echo=False,
    pool_pre_ping=True
)
```

### FastAPI + Supabase
```python
from sqlalchemy.ext.asyncio import create_async_engine

# Use Supabase Postgres connection string
engine = create_async_engine(
    "postgresql+asyncpg://user:password@db.supabase.co/postgres",
    echo=False,
    pool_size=10,  # Respect Supabase's 10-connection limit
    max_overflow=5
)
```

Both support:
- SQLAlchemy async ORM
- Recommendation aggregations (CTEs, window functions, etc.)
- Raw SQL for performance-critical queries

---

## Surprise Charges & Gotchas Summary

| Database | Surprise Risk | Mitigation |
|----------|---------------|-----------|
| **Neon** | Low | Monitor CU-hour usage; easy to stay free |
| **Supabase** | Very Low | Storage quota is clear; upgrade at 500 MB |
| **CockroachDB** | Medium | Pricing cliff; free tier has no transition |
| **Firebase** | **HIGH** | Quota limits = app stops working or charges hit |
| **Railway** | Medium | 30-day credit expiration is clear upfront |
| **Render** | Medium | 30-day free tier expires; minimum $6/month |

---

## Conclusion

**For your exact use case (500 users, aggregation support, FastAPI async):**

1. **Best choice: Neon** ($0 Year 1, $45-90/mo Year 2+)
   - Longest free runway
   - Simplest async integration
   - Most predictable scaling

2. **Best value: Supabase** ($0 Year 1, $25/mo Year 2+)
   - Cheapest scaling
   - Ecosystem (auth, storage, realtime)
   - If you don't need multi-region

3. **Avoid: Everything else**
   - Firebase = no SQL
   - Railway/Render = deceptive "free" tiers
   - CockroachDB = pricing cliff too steep

**Recommendation:** Start with **Neon's free tier**. If you need auth/storage later, migrate to **Supabase** at $25/month. Both are truly free today.
