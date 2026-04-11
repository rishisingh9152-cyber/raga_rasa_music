# Quick Reference: Database Costs at Your Scale

## Scenario: 500 Users → 1000 Users Growth

### Monthly Cost Projection

```
NEON
├─ Year 1 (500 users):        $0/mo   [100 CU-hours free]
├─ Year 2 (750 users):        $50/mo  [~470 CU-hours @ $0.106/hr]
└─ Year 3 (1000 users):       $85/mo  [~800 CU-hours @ $0.106/hr]
   3-Year Total:              $540 + storage ($0-2)

SUPABASE
├─ Year 1 (500 users):        $0/mo   [500 MB free storage]
├─ Year 2 (750 users):        $25/mo  [Pro: 8 GB storage, 250 GB BW]
└─ Year 3 (1000 users):       $25/mo  [Same, if within quota]
   3-Year Total:              $300 + bandwidth overages

COCKROACHDB
├─ Year 1 (500 users):        $0/mo   [50M RUs free]
├─ Year 2 (750 users):        $131/mo [PRICING CLIFF: Standard 2vCPU min]
└─ Year 3 (1000 users):       $200/mo [Likely need 4vCPU Standard]
   3-Year Total:              $1,572+ (uncompetitive)

FIREBASE
├─ Year 1 (500 users):        $0-50/mo [Quota hits + Blaze charges]
├─ Year 2 (750 users):        $100/mo  [Heavy aggregation costs]
└─ Year 3 (1000 users):       $150/mo  [Per-operation fees add up]
   3-Year Total:              $600+ [PLUS: No native SQL]

RAILWAY
├─ Year 1 (500 users):        $2-10/mo [After $5 credit expires]
├─ Year 2 (750 users):        $30/mo   [Small instance]
└─ Year 3 (1000 users):       $50/mo   [Medium instance]
   3-Year Total:              $300+ [NOT truly free]

RENDER
├─ Year 1 (500 users):        $6/mo    [After 30-day free expires]
├─ Year 2 (750 users):        $25/mo   [Standard tier]
└─ Year 3 (1000 users):       $60/mo   [Pro tier]
   3-Year Total:              $372 [NOT truly free]
```

---

## Which Database Wins on Each Criterion?

| Criterion | Winner | Details |
|-----------|--------|---------|
| **Longest Free Tier** | Neon | ~3-6 months (100 CU-hours) |
| **Cheapest Year 2+** | Supabase | $25/month vs Neon's $45-90 |
| **Most Storage Free** | CockroachDB | 10 GB vs Neon 0.5 GB per project |
| **No Pricing Cliff** | Neon | Scales smoothly; CockroachDB has $0→$131 cliff |
| **Best SQL Support** | All equal (Neon, Supabase, CockroachDB) | Firebase excluded |
| **Best Async Support** | Neon | asyncpg is best-in-class |
| **Most Aggregation Friendly** | Neon | Window functions, CTEs, subqueries |
| **Truly Free (No Expiry)** | Neon, Supabase | Others have 30-day credits or paid minimums |
| **Easiest Connection Pooling** | Neon | Auto-managed; Supabase requires careful tuning |
| **Best Ecosystem** | Supabase | Auth, Storage, Realtime included |

---

## One-Page Decision Matrix

### Your Requirements:
- 500 users (not 1K initially)
- 50K sessions/month
- 5-10 MB metadata
- FastAPI async
- SQL aggregations

### Must-Have:
- ✅ Truly free tier (no auto-upgrade)
- ✅ SQL support
- ✅ Async Python driver
- ✅ Aggregation support (GROUP BY, CTEs, etc.)
- ✅ No surprise charges

### Scoring (✅ = Yes, ⚠️ = Weak, ❌ = No)

| | Neon | Supabase | CockroachDB | Firebase | Railway | Render |
|---|------|----------|-----------|----------|---------|--------|
| Truly Free | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| Free Duration | ✅✅ (6mo) | ✅ (forever) | ✅ (forever) | ❌ (quota limits) | ❌ (30-day) | ❌ (30-day) |
| SQL Support | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Aggregations | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Async Support | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| No Surprises | ✅ | ✅ | ⚠️ (cliff) | ❌ (quota) | ✅ | ✅ |
| Competitive Year 2+ | ✅ | ✅✅ (cheaper) | ❌ (cliff) | ❌ (heavy) | ✅ | ✅ |

### **VERDICT**
- ✅ **Neon** - Best free tier runway
- ✅ **Supabase** - Best value long-term
- ❌ **CockroachDB** - Pricing cliff kills it
- ❌ **Firebase** - No SQL
- ❌ **Railway** - No permanent free tier
- ❌ **Render** - No permanent free tier

---

## What Each Database Loses At

### NEON
- **Loses at:** Beyond 6 months of heavy usage (if >800 CU-hours/month)
- **Solution:** Upgrade to Launch plan ($0.106/CU-hour) - still competitive

### SUPABASE
- **Loses at:** Beyond 8 GB storage or 250 GB bandwidth/month on Pro
- **Solution:** Pro+ at $100+/month, but still cheaper than competitors

### COCKROACHDB
- **Loses immediately:** When you outgrow free tier (50M RUs)
- **Cliff:** Standard tier = $131/month minimum (5x jump)
- **Better option:** Use Neon or Supabase at lower cost

### FIREBASE
- **Loses at:** Day 1 with write-heavy operations
- **Additional loss:** No native SQL = complexity tax
- **Cost:** $50-200/month for small scale (vs $0-25 elsewhere)

### RAILWAY
- **Loses at:** Day 31 (free credit expires)
- **Cost:** $2-50/month after that
- **Not competitive:** Neon and Supabase have permanent free tiers

### RENDER
- **Loses at:** Day 31 (free tier expires)
- **Cost:** $6/month minimum
- **Not competitive:** Neon and Supabase have permanent free tiers

---

## The $1 Test: What $1/month Gets You

| Database | For $1/month in Year 2+ |
|----------|--------|
| **Neon** | ~9 CU-hours (enough for 500-1000 users at low traffic) |
| **Supabase** | Partial Pro tier ($25/month = $0.83 per week) - doesn't apply |
| **CockroachDB** | Can't buy < 1 hour of Standard ($0.18/hr) |
| **Firebase** | ~17,000 reads in Blaze plan |
| **Railway** | ~24 hours of small compute |
| **Render** | Can't buy < Basic tier ($6/month) |

**Winner:** Firebase on pure $/operation, but loses on "no SQL" requirement.

---

## Setup Complexity: Which is Easiest?

### 🥇 NEON
```python
# 1. Copy connection string from console
# 2. One line of code
engine = create_async_engine("postgresql+asyncpg://...")
# Done. No pooling config needed.
```

### 🥈 SUPABASE
```python
# 1. Copy connection string
# 2. Configure pool size carefully (max 10 connections)
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=10,
    max_overflow=0
)
# Need to understand connection pooling
```

### 🥉 COCKROACHDB
```python
# 1. Copy connection string (Postgres-compatible)
# 2. One line of code (same as Neon)
engine = create_async_engine("postgresql+asyncpg://...")
# Same as Neon, but pricing model is confusing
```

---

## Migration Risk If You Choose Wrong

| Database | Cost to Migrate Later | Difficulty | Data Loss Risk |
|----------|-----|-----------|-----|
| Neon → Supabase | Low | Easy (Postgres → Postgres) | None |
| Neon → Firebase | High | Hard (SQL → NoSQL) | Moderate (refactor aggregations) |
| Supabase → Neon | Low | Easy (Postgres → Postgres) | None |
| Firebase → Neon | High | Hard (NoSQL → SQL) | High (rebuild queries) |

**Lesson:** Start with Neon or Supabase (both Postgres). Avoid Firebase unless you're certain about NoSQL.

---

## Final Cheat Sheet: Pick Your Database in 30 Seconds

1. **Do you need auth + storage too?** 
   - YES → Supabase ($0 Year 1, $25 Year 2+)
   - NO → Neon ($0 Year 1, $45-90 Year 2+)

2. **Is multi-region a hard requirement in Year 1?**
   - YES → CockroachDB (but accept $131/month cliff)
   - NO → Neon or Supabase

3. **Are you certain about SQL aggregations?**
   - NO (might use NoSQL) → Firebase (but you'll regret it)
   - YES → Neon or Supabase

4. **Do you have a hard budget cap?**
   - $0-10/month → Neon (longest free runway)
   - $25/month → Supabase (best long-term value)
   - $100+/month → CockroachDB (if you really need it)

---

## The Honest Truth

**None of these databases will hurt you if you choose Neon or Supabase.**

Both are:
- ✅ Truly free at your scale
- ✅ Full SQL support
- ✅ Async-first
- ✅ Aggregation-friendly
- ✅ No hidden charges

**The difference:**
- **Neon:** Free for longer (6 months), costs more in Year 2+ ($45-90/mo)
- **Supabase:** Free forever until 500 MB, cheaper in Year 2+ ($25/mo) if you stay under limits

**The risk:**
- Choose wrong (Firebase, Railway, Render) = you'll overspend or rebuild later

**Pick Neon for:**
- Maximum free time to build
- Pure backend service
- Async-first team

**Pick Supabase for:**
- Building a startup (auth + DB + storage)
- Lowest Year 2+ cost
- All-in-one platform preference

You cannot go wrong with either. Get started today.
