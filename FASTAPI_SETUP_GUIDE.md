# FastAPI Setup Guide: Neon vs Supabase

## Quick Setup Comparison

### NEON Setup (5 minutes)

#### 1. Create Free Account
```bash
# Go to https://console.neon.tech
# Sign up with GitHub
# Create a new project (defaults to Postgres 15)
```

#### 2. Get Connection String
```
postgresql://[user]:[password]@[neon-host]/[dbname]
```

#### 3. Convert to Async Connection String
```
postgresql+asyncpg://[user]:[password]@[neon-host]/[dbname]
```

#### 4. FastAPI Code
```python
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends

# Create engine (NO pool config needed - Neon handles it)
engine = create_async_engine(
    "postgresql+asyncpg://user:password@neon-host/dbname",
    echo=False,
    pool_pre_ping=True,  # Keep connections alive
)

# Create session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

app = FastAPI()

# Dependency
async def get_db():
    async with async_session() as session:
        yield session

# Example: Aggregation query (recommendation system)
@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    # Complex aggregation example
    query = select(
        UserActivity.activity_type,
        func.count(UserActivity.id).label("count"),
        func.avg(UserActivity.score).label("avg_score")
    ).where(
        UserActivity.user_id == user_id
    ).group_by(
        UserActivity.activity_type
    ).order_by(
        func.count(UserActivity.id).desc()
    )
    
    result = await db.execute(query)
    return result.all()
```

---

### SUPABASE Setup (8 minutes)

#### 1. Create Free Account
```bash
# Go to https://supabase.com/dashboard
# Sign up with GitHub
# Create a new project
```

#### 2. Get Connection String
```
postgresql://[user]:[password]@db.[project-ref].supabase.co/postgres
```

#### 3. Convert to Async Connection String
```
postgresql+asyncpg://[user]:[password]@db.[project-ref].supabase.co/postgres
```

#### 4. FastAPI Code (WITH Connection Pooling)
```python
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends

# Create engine with CAREFUL pooling (Supabase has 10-connection limit)
engine = create_async_engine(
    "postgresql+asyncpg://user:password@db.supabase.co/postgres",
    echo=False,
    pool_size=10,        # Match Supabase's connection limit
    max_overflow=0,      # Don't create temporary connections
    pool_pre_ping=True,  # Keep connections alive
    pool_recycle=3600,   # Recycle connections every hour
)

# Create session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

app = FastAPI()

# Dependency with context manager
async def get_db():
    async with async_session() as session:
        yield session

# Example: Same aggregation query
@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(
        UserActivity.activity_type,
        func.count(UserActivity.id).label("count"),
        func.avg(UserActivity.score).label("avg_score")
    ).where(
        UserActivity.user_id == user_id
    ).group_by(
        UserActivity.activity_type
    ).order_by(
        func.count(UserActivity.id).desc()
    )
    
    result = await db.execute(query)
    return result.all()
```

---

## Key Differences in Practice

### Connection Pool Configuration

**NEON**
- ✅ Automatic connection pooling
- ✅ No configuration needed
- ✅ Default pool_size=5 works fine
- ✅ Scales automatically

**SUPABASE**
- ⚠️ **MUST** set pool_size=10 (hard limit)
- ⚠️ **MUST** set max_overflow=0 (no temporary connections)
- ⚠️ **MUST** understand pooling or you'll hit connection limits
- ✅ Connection pooling via PgBouncer is excellent when configured

### Production Settings Comparison

| Setting | NEON | SUPABASE |
|---------|------|----------|
| `pool_size` | 5 (default ok) | **10 (must match limit)** |
| `max_overflow` | 0 (ok) | **0 (required)** |
| `pool_pre_ping` | True (recommended) | True (recommended) |
| `pool_recycle` | 3600 (ok) | 3600 (important) |
| `echo` | False (default) | False (default) |

### Query Performance

**Both are identical for:**
- Window functions (`ROW_NUMBER() OVER ...`)
- Common Table Expressions (CTEs)
- Complex JOINs
- Aggregations with GROUP BY
- Subqueries

**Example recommendation query (identical on both):**
```python
# Get top 5 activities by user engagement
query = select(
    UserActivity.activity_type,
    func.count(UserActivity.id).label("engagement"),
    func.row_number().over(
        order_by=func.count(UserActivity.id).desc()
    ).label("rank")
).where(
    UserActivity.user_id == user_id
).group_by(
    UserActivity.activity_type
).having(
    func.count(UserActivity.id) > 5
).limit(5)

result = await db.execute(query)
return result.all()
```

---

## Model Definition (Identical for Both)

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(50))
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Database Initialization

### NEON
```python
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run once on startup
if __name__ == "__main__":
    asyncio.run(init_db())
```

### SUPABASE
```python
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run once on startup (identical to Neon)
if __name__ == "__main__":
    asyncio.run(init_db())
```

**No difference between them.**

---

## Performance Tuning

### NEON Tuning Checklist
- [ ] Use `pool_pre_ping=True` to keep connections alive
- [ ] Set `echo=False` in production
- [ ] Enable read replicas if you have >1K concurrent reads/min
- [ ] Use connection pooling via PgBouncer (optional, Neon manages)
- [ ] Monitor CU-hour usage in console

### SUPABASE Tuning Checklist
- [ ] **CRITICAL:** pool_size=10, max_overflow=0
- [ ] Set `pool_pre_ping=True`
- [ ] Set `pool_recycle=3600` (recycle connections hourly)
- [ ] Set `echo=False` in production
- [ ] Monitor connection usage (Dashboard → Database → Connections)
- [ ] If hitting connection limit: add connection pooling config above

---

## Troubleshooting

### NEON Issues

**Issue:** "too many connections"
- **Unlikely:** Neon auto-scales connections
- **Fix:** Check if you're creating new engines instead of reusing one

**Issue:** Connection times out after idle
- **Fix:** Add `pool_pre_ping=True`

**Issue:** CU-hours running out
- **Check:** Console → Usage → Compute
- **Fix:** Reduce background query frequency or optimize queries

---

### SUPABASE Issues

**Issue:** "FATAL: remaining connection slots are reserved for non-replication superuser connections"
- **Cause:** You exceeded 10 connections
- **Fix:** Set `max_overflow=0` and `pool_size=10`
- **Long-term:** Reduce concurrent connections or upgrade to Pro tier

**Issue:** Connection pooling not working
- **Check:** Settings → Database → Connection Pooling
- **Fix:** Enable PgBouncer mode (Session mode or Transaction mode)

**Issue:** Intermittent connection drops
- **Fix:** Add `pool_recycle=3600` to recycle stale connections

---

## Minimal Reproducible Setup

### NEON (.env file)
```
DATABASE_URL=postgresql+asyncpg://user:password@neon-host/dbname
```

### SUPABASE (.env file)
```
DATABASE_URL=postgresql+asyncpg://user:password@db.project-ref.supabase.co/postgres
```

### FastAPI app (works for both)
```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10 if "supabase" in DATABASE_URL else 5,
    max_overflow=0 if "supabase" in DATABASE_URL else -1,
    pool_pre_ping=True,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

async def get_db():
    async with async_session() as session:
        yield session

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    # Test database connection
    result = await db.execute(text("SELECT 1"))
    return {"status": "ok"}
```

---

## When to Choose Which

### Choose NEON if:
- You want the simplest setup
- Pool configuration is not your concern
- You're building a pure backend service
- You don't need auth/storage

### Choose SUPABASE if:
- You need integrated auth
- You need file storage
- You want realtime subscriptions
- You're willing to manage connection pooling

---

## Migration from One to Another

If you start with Neon and want to switch to Supabase later:

1. **Export data from Neon**
   ```bash
   pg_dump postgresql://user:password@neon-host/dbname > backup.sql
   ```

2. **Import into Supabase**
   ```bash
   psql postgresql://user:password@db.supabase.co/postgres < backup.sql
   ```

3. **Update DATABASE_URL in .env**
   ```
   # Change from Neon
   DATABASE_URL=postgresql+asyncpg://...@neon-host/...
   # To Supabase
   DATABASE_URL=postgresql+asyncpg://...@db.supabase.co/...
   ```

4. **Update pool configuration**
   ```python
   pool_size=10,  # For Supabase
   max_overflow=0
   ```

5. **Done.** No code changes beyond that.

---

## Recommendation Aggregation Example

This example works identically on both Neon and Supabase:

```python
@app.get("/user/{user_id}/recommendations")
async def get_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get personalized recommendations based on user's activity patterns.
    
    This demonstrates:
    - CTEs (WITH clause)
    - Window functions (ROW_NUMBER)
    - Complex aggregations (COUNT, AVG, MAX)
    - GROUP BY with HAVING
    """
    
    query = select(
        Activity.type,
        func.count(UserActivity.id).label("frequency"),
        func.avg(UserActivity.rating).label("avg_rating"),
        func.max(UserActivity.created_at).label("last_activity"),
        func.row_number().over(
            order_by=func.count(UserActivity.id).desc()
        ).label("rank")
    ).join(
        Activity, UserActivity.activity_id == Activity.id
    ).where(
        UserActivity.user_id == user_id
    ).group_by(
        Activity.type
    ).having(
        func.count(UserActivity.id) >= 3  # At least 3 of same type
    ).order_by(
        func.count(UserActivity.id).desc()
    ).limit(10)
    
    result = await db.execute(query)
    recommendations = result.all()
    
    return {
        "user_id": user_id,
        "recommendations": [
            {
                "type": rec[0],
                "frequency": rec[1],
                "avg_rating": rec[2],
                "last_activity": rec[3].isoformat(),
                "rank": rec[4],
            }
            for rec in recommendations
        ]
    }
```

---

## Summary: It's the Same Code

**The key insight:** Choose Neon or Supabase, and 95% of your code is identical.

The only differences are:
1. Connection string (host changes)
2. Pool configuration (Supabase requires careful pooling)
3. Additional features (Supabase adds auth/storage/realtime)

**Your FastAPI code remains the same.**

This means:
- ✅ Easy to switch later
- ✅ No vendor lock-in
- ✅ Both support full SQL features
- ✅ Both support async/await
- ✅ Both are Postgres under the hood

Start with **Neon** for simplicity, **Supabase** for ecosystem.
