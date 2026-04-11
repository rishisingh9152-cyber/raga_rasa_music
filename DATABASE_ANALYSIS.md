# Free-Tier Database Analysis for MongoDB Replacement
## Requirements Analysis
- **1000+ users** minimum
- **500K total sessions** (500 per user average)
- **Flexible schema** (optional cognitive test data, sessions, ratings)
- **FastAPI async compatibility** required
- **Analytics/aggregation** for recommendation engine
- **Estimated data volume**: ~500K sessions × 2-5KB metadata = 1-2.5GB base data
- **Date**: April 2026

---

## 1. POSTGRESQL (via Neon, Railway, or Render)

### PostgreSQL + Neon (Recommended for SQL)
**Free Tier Specifications:**
- **Storage**: 3GB free project (256MB per branch)
- **Compute**: Shared auto-scaling (0.25 - 2 CPU equivalent)
- **Concurrent connections**: ~20-30 for free tier (pooling recommended)
- **Bandwidth**: 5GB/month free
- **API support**: Yes (via PostgREST)

**Data Sizing for 500K sessions:**
```
Sessions table (500K rows):
- id: 8 bytes
- user_id: 8 bytes  
- session_data: ~2KB (JSON)
- metadata: 500 bytes
Total: ~500K × 2.5KB = 1.25GB

Indexes + overhead: ~400MB
Estimated total: ~1.65GB ✓ (fits free tier 3GB)
```

**Concurrent Connections:** 20-30 → Requires pgBouncer connection pooling for FastAPI
- **FastAPI Library**: asyncpg (excellent async support, battle-tested)
- **Pooling Support**: Yes (asyncpg.create_pool)

**Analytics/Aggregation:**
- ✅ **Excellent** - Window functions, CTEs, JSON aggregation
- Recommendation engine: `GROUP BY user_id, HAVING COUNT(*) > threshold`
- Complex queries: Native support for subqueries, materialized views

**Dropbox/Google Drive:**
- ❌ No direct integration
- **Workaround**: Use Python `dropbox` SDK + asyncio to trigger uploads on schedule

**Cost After Free Tier:**
| Tier | Compute | Storage | Monthly Cost |
|------|---------|---------|--------------|
| Pro | 0.5 CPU | 10GB | $15 |
| Scale | Auto | 100GB | $35+ |
| Custom | Custom | Custom | Custom |

**Migration from MongoDB:**
| Aspect | Effort | Details |
|--------|--------|---------|
| Schema design | 🟠 Medium | Need to normalize collections → tables |
| Data migration | 🟡 Easy | mongodump → JSON → psql bulk insert |
| Application code | 🟠 Medium | Update query syntax (aggregation → GROUP BY) |
| Indexes | 🟢 Easy | Similar index strategies |
| Transactions | 🟢 Easy | Better ACID support |

**FastAPI Integration:**
```python
# Async connection pooling (ready for 500K sessions)
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=10,
    max_size=20,  # Adjust based on concurrent requests
    timeout=10.0
)

# Example aggregation for recommendation engine
async def get_user_rating_stats(user_id):
    return await pool.fetch("""
        SELECT 
            raga_id,
            COUNT(*) as listen_count,
            AVG(rating) as avg_rating,
            MAX(updated_at) as last_listen
        FROM sessions
        WHERE user_id = $1
        GROUP BY raga_id
        ORDER BY listen_count DESC
        LIMIT 10
    """, user_id)
```

**⭐ Recommendation Score: 9/10** (Best SQL option)
- Mature ecosystem
- Excellent async support
- Strong analytics
- Affordable scaling

---

## 2. FIREBASE FIRESTORE + REALTIME DATABASE

**Free Tier Specifications:**
- **Storage**: 1GB total (Firestore)
- **Read ops**: 50K/day free
- **Write ops**: 20K/day free
- **Delete ops**: 20K/day free
- **Concurrent connections**: Unlimited (managed by Firebase)
- **Bandwidth**: Google Cloud networking

**Data Sizing for 500K sessions:**
```
1GB limit ÷ 1.25GB needed = 80% usage
❌ FAILS - Storage insufficient for free tier

Workaround: Archive old sessions monthly
- Keep last 30 days: ~50K sessions = 125MB ✓
- Archive to Cloud Storage (1GB free/month transfer)
```

**Concurrent Connections:**
- ✅ **Unlimited** - Firebase handles auto-scaling
- Real-time sync included

**Analytics/Aggregation:**
| Capability | Available | Notes |
|------------|-----------|-------|
| GROUP BY | ❌ No | Firestore has no native aggregation |
| Window functions | ❌ No | Limited query operations |
| Complex filtering | 🟡 Limited | Basic WHERE + ORDER BY only |
| Aggregation pipeline | ❌ No | No equivalent to MongoDB aggregation |

**Recommendation Engine:**
```javascript
// Limited aggregation - requires client-side processing
const snapshot = await db.collection('sessions')
    .where('userId', '==', userId)
    .orderBy('timestamp', 'desc')
    .limit(500)
    .get();

// Must process in application (inefficient for 500K)
const ragaStats = {};
snapshot.forEach(doc => {
    // Group manually in code ❌ Performance hit
});
```

**FastAPI Integration:**
```python
# Using firebase-admin SDK
from firebase_admin import firestore
import asyncio

db = firestore.client()

# ⚠️ SDK is not fully async - blocks event loop
async def get_sessions(user_id):
    # Runs in thread pool
    result = await asyncio.to_thread(
        lambda: db.collection('sessions')
            .where('user_id', '==', user_id)
            .stream()
    )
    return result
```

**Dropbox/Google Drive:**
- ✅ **Native integration** - Firebase Cloud Functions
- **Google Drive**: Direct export via Firestore Data Export
- **Dropbox**: Custom Cloud Function

**Cost After Free Tier:**
| Volume | Storage | Operations | Monthly |
|--------|---------|-----------|---------|
| 100K reads/day | 2GB | 100K reads | ~$15 |
| 500K reads/day | 2GB | 500K reads | ~$50 |
| 1M+ reads/day | 5GB | 1M+ reads | ~$100+ |

**Migration from MongoDB:**
| Aspect | Effort | Details |
|--------|--------|---------|
| Schema design | 🟡 Easy | Firebase prefers denormalized docs |
| Data migration | 🔴 Hard | Complex aggregation transforms |
| Application code | 🔴 Hard | Query syntax completely different |
| Indexes | 🔴 Hard | Firestore composite indexes different |
| Transactions | 🟡 Easy | Similar to MongoDB |

**❌ Recommendation Score: 4/10** (Poor for this use case)
- **Major con**: 1GB storage insufficient for 500K sessions
- **Major con**: No server-side aggregation (killer for recommendation engine)
- **Major con**: Async integration awkward with FastAPI
- **Pro**: Unlimited real-time connections
- **Use case**: Better for mobile apps with smaller datasets

---

## 3. SUPABASE (PostgreSQL + Auth)

**Free Tier Specifications:**
- **Storage**: 500MB (database) + 1GB file storage
- **Bandwidth**: 2GB/month
- **Realtime connections**: 200 concurrent
- **Database**: PostgreSQL (same as #1, but with extras)
- **Concurrent connections**: 20 (via pgBouncer)

**Data Sizing for 500K sessions:**
```
500M + 1GB file = 1.5GB available
Sessions data: ~1.25GB needed
Additional overhead: 250MB
Total: 1.5GB = 100% usage
⚠️ TIGHT - Borderline viable, minimal headroom
```

**Concurrent Connections:** 20 (connection pooling required)

**Analytics/Aggregation:**
- ✅ **Same as PostgreSQL** (it IS PostgreSQL)
- Full support for complex aggregations
- Real-time subscriptions built-in

**Recommendation Engine:**
```python
# Supabase Python SDK
from supabase import create_client, Client
import asyncio

supabase: Client = create_client(url, key)

async def get_raga_recommendations(user_id: int, limit: int = 10):
    response = supabase.table('sessions') \
        .select('raga_id, COUNT(*), AVG(rating)') \
        .eq('user_id', user_id) \
        .group_by('raga_id') \
        .order('COUNT(*)', ascending=False) \
        .limit(limit) \
        .execute()
    return response.data

# ⚠️ Note: Supabase Python SDK doesn't support group_by natively
# Use raw SQL instead:
result = await supabase.rpc('get_user_recommendations', 
    {'user_id': user_id}
).execute()
```

**FastAPI Integration:**
```python
# Create PL/pgSQL function for aggregation
create_function_sql = """
CREATE OR REPLACE FUNCTION get_user_recommendations(p_user_id INT, p_limit INT = 10)
RETURNS TABLE (raga_id INT, listen_count BIGINT, avg_rating FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT s.raga_id, COUNT(*)::BIGINT, AVG(s.rating)::FLOAT
    FROM sessions s
    WHERE s.user_id = p_user_id
    GROUP BY s.raga_id
    ORDER BY COUNT(*) DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
"""

# In FastAPI
@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int):
    result = await supabase.rpc('get_user_recommendations', 
        {'user_id': user_id, 'p_limit': 10}
    ).execute()
    return result.data
```

**Dropbox/Google Drive:**
- ✅ **File storage integration** - Use Supabase Storage (1GB free)
- **Dropbox**: Use `supabase-py` + schedule exports
- **Recommendation**: Store exports in Supabase Storage, sync to Dropbox via Edge Functions

**Cost After Free Tier:**
| Tier | Database | Storage | Monthly |
|------|----------|---------|---------|
| Pro | 8GB | 100GB | $25 |
| Team | Unlimited | 500GB | $599 |
| Enterprise | Custom | Custom | Custom |

**Migration from MongoDB:**
| Aspect | Effort | Details |
|--------|--------|---------|
| Schema design | 🟠 Medium | Same as PostgreSQL (normalize) |
| Data migration | 🟡 Easy | Supabase provides migration guides |
| Application code | 🟠 Medium | Supabase SDK different from psycopg2 |
| Indexes | 🟢 Easy | PostgreSQL indexes |
| Transactions | 🟢 Easy | ACID guaranteed |

**⭐ Recommendation Score: 7/10** (Good middle ground)
- **Pro**: All PostgreSQL power + auth included
- **Pro**: Realtime subscriptions for live updates
- **Con**: Storage tight (500MB) for 500K sessions
- **Con**: Still need connection pooling
- **Best for**: Authentication-heavy apps needing real-time features

---

## 4. PLANETSCALE (MySQL-compatible, Vitess)

**Free Tier Specifications:**
- **Storage**: 5GB
- **Read operations**: 1 million/month free
- **Write operations**: 1 million/month free
- **Concurrent connections**: 1000 (built-in scaling)
- **Branches**: 10 free branches

**Data Sizing for 500K sessions:**
```
5GB available vs 1.25GB needed = Excellent fit ✓✓
Plenty of headroom for indexes and growth
```

**Concurrent Connections:**
- ✅ **1000+** - Vitess handles unlimited connections via connection pooling
- Automatically scales reads/writes

**Analytics/Aggregation:**
| Capability | Available | Performance |
|------------|-----------|-------------|
| GROUP BY | ✅ Yes | Excellent on Vitess |
| JOIN operations | ✅ Yes | Fast (horizontal shard aware) |
| Window functions | 🟡 Limited | MySQL 8.0+ support |
| Complex aggregation | ✅ Yes | Optimized for this |

**Recommendation Engine:**
```python
# Using aiomysql for async
import aiomysql

async def get_recommendations(pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT 
                    raga_id,
                    COUNT(*) as listen_count,
                    AVG(rating) as avg_rating,
                    MAX(updated_at) as last_listen
                FROM sessions
                WHERE user_id = %s
                GROUP BY raga_id
                HAVING listen_count > 2
                ORDER BY listen_count DESC
                LIMIT 10
            """, (user_id,))
            return await cursor.fetchall()
```

**FastAPI Integration:**
```python
from contextlib import asynccontextmanager

async def init_pool():
    global pool
    pool = await aiomysql.create_pool(
        host='host.planetscale.com',
        port=3306,
        user='username',
        password='password',
        db='database_name',
        minsize=5,
        maxsize=100,  # Can handle much more than MongoDB
        loop=asyncio.get_event_loop()
    )

@app.get("/sessions/{user_id}")
async def get_sessions(user_id: int, skip: int = 0, limit: int = 100):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT id, user_id, session_data, created_at
                FROM sessions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, skip))
            return await cursor.fetchall()
```

**Dropbox/Google Drive:**
- ❌ No native integration
- **Workaround**: Use PlanetScale API + Python SDK to export backups
- Cloud Function approach: Trigger on schedule to export → upload

**Cost After Free Tier:**
| Plan | Storage | Monthly Cost | Ops/month |
|------|---------|--------------|-----------|
| Hobby | 10GB | Free (1M ops/mo) | 1M |
| Scaler | 100GB | $29 | 10M |
| Scaler Pro | 200GB | $99 | 100M |

**Migration from MongoDB:**
| Aspect | Effort | Details |
|--------|--------|---------|
| Schema design | 🟠 Medium | RDBMS normalization required |
| Data migration | 🟡 Easy | MongoDB → JSON → MySQL import |
| Application code | 🟠 Medium | Different query syntax |
| Indexes | 🟢 Easy | Similar strategy to MongoDB |
| Transactions | 🟢 Easy | Better ACID support |

**⭐ Recommendation Score: 8/10** (Excellent choice)
- **Pro**: 5GB free storage (plenty of headroom)
- **Pro**: 1000+ concurrent connections built-in
- **Pro**: Vitess horizontal scaling included
- **Pro**: Excellent async MySQL driver (aiomysql)
- **Con**: Limited window functions in older versions
- **Best for**: High-concurrency apps with large data volumes

---

## 5. RAILWAY (Managed Databases)

**Free Tier Specifications:**
- **Storage**: $5 credit/month (~10GB PostgreSQL equivalent)
- **Includes**: PostgreSQL, MySQL, MongoDB, Redis
- **Concurrent connections**: Depends on database choice
- **Bandwidth**: Included in credit
- **After credit**: Usage-based billing ($0.20/GB-month storage)

**Data Sizing for 500K sessions:**
```
$5/month credit for 10GB PostgreSQL
Sessions data: 1.25GB
Plenty of room within free tier
```

**Concurrent Connections:**
- PostgreSQL: ~20-30 (requires pooling)
- MySQL: ~20-30 (requires pooling)
- MongoDB: Unlimited

**FastAPI Integration:**
```python
# Railway automatically provides DATABASE_URL environment variable
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_delete=False
)

@app.get("/sessions/{user_id}")
async def get_sessions(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Session).where(Session.user_id == user_id)
        )
        return result.scalars().all()
```

**Analytics/Aggregation:**
- **PostgreSQL**: ✅ Excellent
- **MySQL**: ✅ Good
- **MongoDB**: ✅ Good (kept same as original)

**Dropbox/Google Drive:**
- ✅ Easy - Use Railway's cron jobs
- Schedule exports via Edge Functions
- Push to Dropbox/Google Drive directly

**Cost After Free Tier:**
| Usage | Database | Storage | Monthly |
|-------|----------|---------|---------|
| 2GB data | PostgreSQL | 2GB | $4 |
| 10GB data | PostgreSQL | 10GB | $20 |
| 50GB data | PostgreSQL | 50GB | $100 |

**Migration from MongoDB:**
- **Same as PostgreSQL** (if using pg)
- Can keep MongoDB on Railway → no migration needed ✓

**⭐ Recommendation Score: 8.5/10** (Very flexible)
- **Pro**: Start free, then pay for what you use
- **Pro**: Can trial different databases
- **Pro**: Keep MongoDB if preferred
- **Pro**: Simple deployment for FastAPI
- **Con**: Credit expires if not used
- **Best for**: Flexible requirements, trying different databases

---

## 6. NEON (PostgreSQL Serverless)

**Free Tier Specifications:**
- **Storage**: 3GB
- **Compute**: Shared auto-scaling
- **Concurrent connections**: Limited (via pooling)
- **Connection pooling**: Built-in (PgBouncer)
- **Branches**: 10 free (great for dev/test)

**Data Sizing for 500K sessions:**
```
3GB available vs 1.25GB needed = Excellent fit ✓
Best storage ratio among SQL options
```

**Concurrent Connections:**
- Built-in connection pooling handles high concurrency
- Auto-scales compute from 0 to needed resources
- Better than traditional PostgreSQL for serverless

**Analytics/Aggregation:**
- ✅ **Full PostgreSQL** - Same as #1

**FastAPI Integration:**
```python
# Neon uses standard PostgreSQL async drivers
import asyncpg

dsn = os.getenv("DATABASE_URL_ASYNC")  # Neon provides
pool = await asyncpg.create_pool(dsn)

# Identical to Neon example above
```

**Dropbox/Google Drive:**
- ❌ No native integration
- **Workaround**: Use Neon serverless functions + Python SDK

**Cost After Free Tier:**
| Tier | Storage | Compute | Monthly |
|------|---------|---------|---------|
| Pro | 10GB | Always-on | $15 |
| Business | 100GB | Custom | $50+ |

**Migration from MongoDB:**
- Same as PostgreSQL
- 🟠 Medium effort

**⭐ Recommendation Score: 8.5/10** (Serverless PostgreSQL)
- **Pro**: Best PostgreSQL for serverless
- **Pro**: Built-in connection pooling
- **Pro**: 3GB storage perfect for data size
- **Pro**: Auto-scaling compute (pay for what you use)
- **Con**: Compute pause after inactivity (cold starts)
- **Best for**: FastAPI apps with variable load

---

## 7. COCKROACHDB (Distributed SQL)

**Free Tier Specifications:**
- **Storage**: 5GB total
- **Request units**: 250M/month free
- **Concurrent connections**: 100 (limited)
- **Regions**: 3-node cluster (us-east)
- **Availability**: 99.99% SLA

**Data Sizing for 500K sessions:**
```
5GB available vs 1.25GB needed = Excellent fit ✓
Distributed resilience included
```

**Concurrent Connections:**
- ❌ **Limited to 100** on free tier
- Not ideal for high-concurrency applications
- Connection pooling helps but still limiting

**Analytics/Aggregation:**
- ✅ **Excellent** - SQL superset, advanced features
- Better window function support than MySQL
- Complex CTEs and partitioning

**FastAPI Integration:**
```python
import asyncpg

# CockroachDB wire protocol compatible with PostgreSQL
dsn = "postgresql://user:password@cluster.crdb.io:26257/database?sslmode=require"
pool = await asyncpg.create_pool(dsn)

async def get_recommendations(pool, user_id: int):
    return await pool.fetch("""
        SELECT 
            raga_id,
            COUNT(*) OVER (PARTITION BY raga_id) as listen_count,
            AVG(rating) OVER (PARTITION BY raga_id) as avg_rating
        FROM sessions
        WHERE user_id = $1
        ORDER BY listen_count DESC
        LIMIT 10
    """, user_id)
```

**Dropbox/Google Drive:**
- ❌ No native integration
- Similar Python SDK workaround

**Cost After Free Tier:**
| Usage | Requests/month | Storage | Monthly |
|-------|-----------------|---------|---------|
| Small | 250M | 5GB | Free |
| Medium | 1B | 50GB | ~$150 |
| Large | 10B | 500GB | ~$1500+ |

**Migration from MongoDB:**
- 🟠 Medium effort
- PostgreSQL-compatible syntax

**❌ Recommendation Score: 5/10** (Limited concurrency)
- **Pro**: Distributed, highly available
- **Pro**: Excellent SQL features
- **Con**: Only 100 concurrent connections
- **Con**: Expensive after free tier
- **Not ideal for**: Your 500K session concurrent load

---

## 8. MONGODB ALTERNATIVES (NoSQL)

### Alternatives to reconsider:

#### A. **MongoDB Atlas (Official)**
| Aspect | Detail |
|--------|--------|
| Free tier | 512MB storage |
| Concurrent connections | Unlimited |
| Sessions fit? | ❌ 512MB << 1.25GB needed |
| Recommendation score | 3/10 |

#### B. **FaunaDB (Serverless NoSQL)**
| Aspect | Detail |
|--------|--------|
| Free tier | 100K read/write ops/day, 25GB storage |
| Serverless | ✅ Yes, full async |
| Query language | FQL (unique, not MongoDB) |
| Recommendation score | 6/10 - Good but learning curve |

#### C. **Dgraph (GraphQL Database)**
| Aspect | Detail |
|--------|--------|
| Free tier | Self-hosted, Dgraph Cloud: 1GB |
| Graph queries | ✅ Excellent for relationships |
| FastAPI compat | ✅ GraphQL async |
| Recommendation score | 5/10 - Overkill for your use case |

#### D. **Turso (SQLite in Cloud)**
| Aspect | Detail |
|--------|--------|
| Free tier | 500M read requests, 50K write requests/month |
| Storage | 8GB per database |
| Edge locations | ✅ Global replication |
| Analytics | ❌ Limited for complex aggregations |
| Recommendation score | 6/10 - Not for 500K session volume |

---

## SUMMARY COMPARISON TABLE

| Database | Storage | Connections | Analytics | Migration | FastAPI | Cost | Score |
|----------|---------|-------------|-----------|-----------|---------|------|-------|
| **PostgreSQL (Neon)** | 3GB | 20-30* | ⭐⭐⭐⭐⭐ | 🟠🟠 | ✅ | $15 | **8.5** |
| **PostgreSQL (Railway)** | $5 credit | 20-30* | ⭐⭐⭐⭐⭐ | 🟠🟠 | ✅ | Free then $0.20/GB | **8.5** |
| **PlanetScale (MySQL)** | 5GB | 1000+ | ⭐⭐⭐⭐ | 🟠🟠 | ✅ | Free then $29 | **8** |
| **Supabase** | 500MB* | 20-30* | ⭐⭐⭐⭐⭐ | 🟠🟠 | ✅ | $25 | **7** |
| **Firebase/Firestore** | 1GB* | Unlimited | ⭐⭐ | 🔴 | 🟡 | $15+ | **4** |
| **CockroachDB** | 5GB | 100* | ⭐⭐⭐⭐⭐ | 🟠🟠 | ✅ | $150+ | **5** |
| **MongoDB Atlas** | 512MB* | Unlimited | ⭐⭐⭐ | ✅ | ✅ | Free then $57 | **3** |

*requires connection pooling, too small, or too limited

---

## FINAL RECOMMENDATIONS BY PRIORITY

### 🥇 TIER 1: BEST OVERALL

#### **1. PlanetScale (MySQL via Vitess)**
**Why**: 
- 5GB storage (enough headroom)
- 1000+ concurrent connections (no pooling tricks needed)
- Free tier actually free for reasonable volume
- Excellent async MySQL driver (aiomysql)
- Vitess scaling transparent to app

**For your 500K sessions:**
```
✅ Handles 1000+ concurrent users
✅ 500K sessions = 1.25GB (fits in 5GB free)
✅ Aggregation/analytics via GROUP BY, window functions
✅ Easy async FastAPI integration
✅ Scales to $29/month when needed
```

---

### 🥈 TIER 2: EXCELLENT ALTERNATIVES

#### **2. Neon (PostgreSQL Serverless)**
**Why**:
- 3GB storage (perfect for data size)
- Built-in connection pooling
- Auto-scaling compute (pay per use)
- Full PostgreSQL power
- Better than Supabase for read-heavy workloads

**Best if**: You prefer serverless, need auto-scaling

#### **3. Railway (Pay-as-you-go)**
**Why**:
- Start free ($5 credit)
- Choose your own database (PostgreSQL, MySQL, MongoDB)
- Usage-based pricing (transparent)
- Easiest deployment for FastAPI

**Best if**: Want flexibility, plan to scale gradually

---

### 🥉 TIER 3: CONDITIONAL RECOMMENDATIONS

#### **4. Supabase (PostgreSQL + Auth)**
**Why**: If you need user authentication built-in
- Realtime subscriptions
- Row-level security
- Built-in auth (save backend work)

**Con**: Tight storage (500MB) for 500K sessions
**Workaround**: Archive sessions monthly to separate storage

---

## RECOMMENDATION ENGINE COMPATIBILITY ANALYSIS

```python
# Use PlanetScale with this pattern for best results:

import aiomysql
from typing import List, Dict

async def get_user_recommendations(
    pool: aiomysql.Pool, 
    user_id: int,
    limit: int = 10
) -> List[Dict]:
    """Get personalized recommendations based on listening history."""
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 1. Get user's listening patterns
            await cursor.execute("""
                SELECT 
                    s.raga_id,
                    COUNT(*) as listen_count,
                    AVG(s.rating) as avg_rating,
                    MAX(s.listen_date) as last_listen
                FROM sessions s
                WHERE s.user_id = %s
                AND s.listen_date > DATE_SUB(NOW(), INTERVAL 90 DAY)
                GROUP BY s.raga_id
                HAVING listen_count >= 2
                ORDER BY listen_count DESC, avg_rating DESC
            """, (user_id,))
            user_preferences = await cursor.fetchall()
            
            if not user_preferences:
                return []  # Cold start user
            
            # 2. Find similar users (collaborative filtering)
            raga_ids = [p['raga_id'] for p in user_preferences]
            placeholders = ','.join(['%s'] * len(raga_ids))
            
            await cursor.execute(f"""
                SELECT 
                    DISTINCT s2.user_id as similar_user_id
                FROM sessions s1
                JOIN sessions s2 ON s1.raga_id = s2.raga_id
                WHERE s1.user_id = %s
                AND s1.raga_id IN ({placeholders})
                AND s2.user_id != %s
                LIMIT 50
            """, [user_id] + raga_ids + [user_id])
            similar_users = await cursor.fetchall()
            
            if not similar_users:
                # Fallback to popular ragas
                await cursor.execute("""
                    SELECT 
                        raga_id,
                        COUNT(*) as popularity
                    FROM sessions
                    WHERE raga_id NOT IN (
                        SELECT raga_id FROM sessions WHERE user_id = %s
                    )
                    GROUP BY raga_id
                    ORDER BY popularity DESC
                    LIMIT %s
                """, (user_id, limit))
                return await cursor.fetchall()
            
            # 3. Get recommendations from similar users
            similar_user_ids = [u['similar_user_id'] for u in similar_users]
            placeholders = ','.join(['%s'] * len(similar_user_ids))
            
            await cursor.execute(f"""
                SELECT 
                    s.raga_id,
                    COUNT(*) as recommendation_score,
                    AVG(s.rating) as avg_rating
                FROM sessions s
                WHERE s.user_id IN ({placeholders})
                AND s.raga_id NOT IN (
                    SELECT raga_id FROM sessions WHERE user_id = %s
                )
                GROUP BY s.raga_id
                ORDER BY recommendation_score DESC, avg_rating DESC
                LIMIT %s
            """, similar_user_ids + [user_id, limit])
            
            return await cursor.fetchall()
```

---

## DROPBOX/GOOGLE DRIVE INTEGRATION

### Recommended Approach for PlanetScale:

```python
# utils/database_exports.py
import asyncio
from datetime import datetime
import dropbox
import aiomysql
import io

async def export_sessions_to_dropbox(
    pool: aiomysql.Pool,
    dropbox_token: str,
    user_id: int
):
    """Export user sessions to Dropbox."""
    # 1. Query sessions from PlanetScale
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT id, raga_id, rating, listen_date, session_data
                FROM sessions
                WHERE user_id = %s
                ORDER BY listen_date DESC
            """, (user_id,))
            rows = await cursor.fetchall()
    
    # 2. Convert to CSV
    csv_buffer = io.StringIO()
    csv_buffer.write("session_id,raga_id,rating,listen_date,metadata\n")
    for row in rows:
        csv_buffer.write(f"{row[0]},{row[1]},{row[2]},{row[3]},\"{row[4]}\"\n")
    
    # 3. Upload to Dropbox
    dbx = dropbox.Dropbox(dropbox_token)
    filename = f"sessions_backup_{user_id}_{datetime.now().isoformat()}.csv"
    
    dbx.files_upload(
        csv_buffer.getvalue().encode(),
        f"/raga_rasa_exports/{filename}",
        autorename=True
    )
    
    return filename
```

---

## MIGRATION CHECKLIST (MongoDB → PlanetScale)

```bash
# 1. Export MongoDB data
mongodump --db raga_rasa --out ./mongo_dump

# 2. Convert to SQL format
python scripts/mongo_to_mysql.py ./mongo_dump

# 3. Create PlanetScale schema
mysql -h host.planetscale.com -u user -p database < schema.sql

# 4. Import data
mysql -h host.planetscale.com -u user -p database < data.sql

# 5. Update FastAPI requirements.txt
# Replace pymongo with aiomysql and sqlalchemy

# 6. Update connection string
DATABASE_URL=mysql+aiomysql://user:password@host.planetscale.com:3306/database

# 7. Test aggregations work identically
```

---

## CONCLUSION

**Choose PlanetScale if:**
- ✅ You need simple, transparent pricing
- ✅ Want best free tier (5GB)
- ✅ Need unlimited concurrent connections
- ✅ Prefer managed MySQL (less complex than PostgreSQL)
- ✅ Don't want vendor lock-in with Supabase auth

**Choose Neon if:**
- ✅ You like serverless auto-scaling
- ✅ Want PostgreSQL advanced features
- ✅ Prefer pay-per-use model
- ✅ Need built-in connection pooling

**Choose Railway if:**
- ✅ Want maximum flexibility
- ✅ Like experimenting with different databases
- ✅ Want simplest FastAPI deployment
- ✅ Need transparent usage billing

**Avoid Firebase/Firestore for this use case** - storage too small, aggregation too weak

---

## Implementation Timeline

```
Week 1: Set up PlanetScale + basic FastAPI integration
Week 2: Migrate MongoDB data (if needed)
Week 3: Implement recommendation engine with aggregations
Week 4: Add Dropbox export functionality
Week 5: Performance testing at 500K sessions scale
```

**Last updated**: April 10, 2026
