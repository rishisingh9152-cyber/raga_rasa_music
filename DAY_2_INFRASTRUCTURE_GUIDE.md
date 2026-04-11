# Day 2: Infrastructure Setup Guide
## PlanetScale + Dropbox + Render.com

### Prerequisites
- Render.com account (will create)
- PlanetScale account (will create)
- Dropbox account (will create)
- GitHub account (already have)

---

## **PART 1: PLANETSCALE DATABASE SETUP** (1-2 hours)

### Step 1: Create PlanetScale Account
1. Go to https://planetscale.com
2. Sign up with GitHub (easiest)
3. Create organization
4. Create new database "raga_rasa"
5. Select region closest to you
6. Keep on free tier

### Step 2: Get Connection String
1. In PlanetScale dashboard, open your database
2. Click "Connect" button
3. Select "MySQL client"
4. Copy connection string:
   ```
   mysql://[username]:[password]@[host]/raga_rasa?sslaccept=strict
   ```
5. Save securely (will add to .env)

### Step 3: Initialize Database Schema
We need to convert MongoDB schemas to MySQL for PlanetScale.

**Note**: This requires updating our database layer. I'll:
1. Create SQL migration files
2. Update database.py to support PlanetScale
3. Add SQLAlchemy models
4. Test connection locally

---

## **PART 2: RENDER.COM SETUP** (2-3 hours)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Create organization
4. Go to Dashboard

### Step 2: Create Environment Variables File
Create `.env.render` to manage all Render environment variables:
```
# Database
DATABASE_URL=mysql://[from planetscale]

# Emotion Service (internal URL)
EMOTION_SERVICE_URL=http://emotion-service:5000

# Storage
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=[will get from Dropbox]

# Auth
JWT_SECRET_KEY=[already have]

# CORS
ALLOWED_ORIGINS=https://[your-vercel-domain].vercel.app

# GitHub OAuth
GITHUB_CLIENT_ID=[will create]
GITHUB_CLIENT_SECRET=[will create]

# Redis (optional, Render provides)
REDIS_URL=redis://[if using Render Redis]
```

### Step 3: Deploy Emotion Service to Render
1. Create new service
   - Name: `emotion-service`
   - Source: Connect GitHub repo
   - Branch: main
   - Build: `pip install -r emotion_service/requirements.txt`
   - Start: `python emotion_service/app.py`
   - Plan: Free tier
   - Environment: Add variables

2. Get public URL (e.g., `https://emotion-service.onrender.com`)

### Step 4: Deploy Backend to Render
1. Create new service
   - Name: `raga-rasa-backend`
   - Source: Connect GitHub repo
   - Branch: main
   - Build: `pip install -r Backend/requirements.txt`
   - Start: `python Backend/main.py` (or `uvicorn Backend/main:app`)
   - Plan: Free tier
   - Environment: Add all variables from `.env.render`
   - Set EMOTION_SERVICE_URL to public Render URL

2. Get public URL (e.g., `https://raga-rasa-backend.onrender.com`)

---

## **PART 3: DROPBOX STORAGE SETUP** (45 minutes)

### Step 1: Create Dropbox App
1. Go to https://www.dropbox.com/developers/apps
2. Click "Create app"
3. Choose:
   - API: Dropbox API
   - Type: App folder
   - Name: raga-rasa-songs
4. Click Create

### Step 2: Get Dropbox Access Token
1. Go to Settings tab
2. Generate access token
3. Copy token (long string like `sl.Bxxx...`)
4. Save securely

### Step 3: Create App Folder Structure
In your Dropbox app folder, create:
```
/Songs/
  /shaant/
  /shringar/
  /veer/
  /shok/
```

### Step 4: Get Folder ID (if needed)
1. Open Dropbox app folder
2. Right-click folder
3. Copy Dropbox link
4. Extract folder ID from URL

---

## **PART 4: GITHUB OAUTH SETUP** (30 minutes)

### Step 1: Create GitHub OAuth App
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - App name: `Raga Rasa Music Therapy`
   - Homepage URL: `https://raga-rasa.vercel.app` (temp, update later)
   - Authorization callback URL: `https://raga-rasa.vercel.app/auth/callback`
4. Click Create

### Step 2: Get Credentials
1. Copy Client ID
2. Click "Generate new client secret"
3. Copy Client Secret
4. Save both securely

---

## **FILES TO MODIFY**

### 1. Create `Backend/.env.production`
```ini
# Database (PlanetScale)
DATABASE_URL=mysql://[from planetscale]
DATABASE_PROVIDER=planetscale

# Emotion Service
EMOTION_SERVICE_URL=https://emotion-service.onrender.com

# Storage (Dropbox)
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=sl.Bxxx...

# Auth
JWT_SECRET_KEY=[use same from dev]
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=https://raga-rasa.vercel.app

# GitHub OAuth
GITHUB_CLIENT_ID=[from GitHub]
GITHUB_CLIENT_SECRET=[from GitHub]

# API
API_HOST=0.0.0.0
API_PORT=8000

# Debug
DEBUG=False
```

### 2. Create `raga-rasa-soul-main/.env.production`
```ini
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com
VITE_GITHUB_CLIENT_ID=[from GitHub]
VITE_GITHUB_REDIRECT_URI=https://raga-rasa.vercel.app/auth/callback
```

### 3. Update `Backend/app/database.py`
- Add PlanetScale MySQL support
- Create SQLAlchemy ORM models
- Keep MongoDB imports but make optional

### 4. Update `Backend/app/services/cloud_storage.py`
- Implement DropboxStorageProvider
- Add Dropbox client initialization
- Implement upload/download/delete/list

---

## **IMPLEMENTATION PRIORITY**

Day 2a (2-4 hours):
- [ ] Create PlanetScale account & database
- [ ] Get connection string
- [ ] Create SQL migration files
- [ ] Update database.py to support PlanetScale

Day 2b (3-4 hours):
- [ ] Create Render account
- [ ] Deploy emotion service
- [ ] Deploy backend
- [ ] Get public URLs

Day 2c (30 min):
- [ ] Create GitHub OAuth app
- [ ] Save credentials

Day 2d (2-3 hours):
- [ ] Create Dropbox app
- [ ] Implement DropboxStorageProvider
- [ ] Test locally
- [ ] Deploy updated backend

---

## **TESTING CHECKLIST**

After each step:
- [ ] PlanetScale: Can connect from local machine
- [ ] PlanetScale: Can read/write data
- [ ] Render: Emotion service running (check health endpoint)
- [ ] Render: Backend running (check health endpoint)
- [ ] Render: Emotion service URL working
- [ ] GitHub: OAuth app credentials saved
- [ ] Dropbox: Can authenticate with token
- [ ] Dropbox: Can upload/download files
- [ ] Backend: Uses Dropbox for storage
- [ ] Backend: Falls back to local if Dropbox unavailable

---

## **CRITICAL NOTES**

1. **Free Tiers**:
   - PlanetScale: Free tier is generous (1 million row reads/month)
   - Render: Free tier has limited hours but sufficient
   - Dropbox: 2GB free (plenty for songs)

2. **Connection Security**:
   - Never commit `.env.production` to git
   - Use Render's secret management
   - Rotate tokens regularly

3. **Emotion Service Timeout**:
   - Render free tier may have 30-second timeout
   - If emotion service slow, may need paid tier

4. **Database Scalability**:
   - PlanetScale offers painless MySQL scaling
   - Can upgrade to paid tier if needed
   - No schema lock during migrations (PlanetScale advantage)

---

**Ready to start? I'll guide you through each step with exact commands and confirmations.**
