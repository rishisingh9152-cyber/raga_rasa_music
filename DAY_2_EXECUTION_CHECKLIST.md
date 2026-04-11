# Day 2 Execution Checklist - Infrastructure Setup

## **DAY 2 OVERVIEW**

**Goal**: Set up all cloud infrastructure and get credentials ready for deployment  
**Duration**: 8-10 hours  
**Outcome**: Ready for Day 3 (deployment to Render/Vercel)

---

## **DAY 2a: MongoDB ATLAS (1-2 hours)**

### Account Creation
- [ ] Go to https://www.mongodb.com/cloud/atlas
- [ ] Sign up with GitHub (easiest)
- [ ] Verify email
- [ ] Create organization

### Cluster Setup
- [ ] Create cluster named "raga-rasa"
- [ ] Select "Shared" tier (FREE)
- [ ] Choose region closest to you
- [ ] Wait for cluster to initialize (3-5 min)

### Database User
- [ ] Go to "Security" → "Database Access"
- [ ] Create user "ragarasa"
- [ ] Generate secure password (save it!)
- [ ] Set role to "Atlas admin"

### Get Connection String
- [ ] Go to "Deployment" → "Databases"
- [ ] Click "Connect"
- [ ] Select "Drivers" → "Python"
- [ ] Copy connection string
- [ ] **Save to file**: `MONGODB_CREDENTIALS.txt`

### Network Access
- [ ] Go to "Security" → "Network Access"
- [ ] Add IP: "Allow Access from Anywhere" (0.0.0.0/0)
- [ ] Click Confirm

### Update Backend Configuration
- [ ] Open `Backend/.env`
- [ ] Update `MONGODB_URL` with your connection string
- [ ] Save file

### Test Locally
```bash
cd Backend
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```
- [ ] Test passes (✅ Connected to MongoDB!)

### Create `.env.production`
```bash
cd Backend
cp .env .env.production
# Update values in .env.production
```
- [ ] Update `MONGODB_URL` in `.env.production`
- [ ] Update other production values
- [ ] Save file (don't commit!)

---

## **DAY 2b: RENDER.COM SETUP (3-4 hours)**

### Account Creation
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize Render access to repos
- [ ] Confirm email

### Prepare Repository
- [ ] Verify `Backend/main.py` exists
- [ ] Verify `Backend/requirements.txt` exists
- [ ] Verify `emotion_service/` folder exists
- [ ] Verify `.gitignore` excludes `*.env`
- [ ] Push any uncommitted changes to GitHub

### Deploy Emotion Service
- [ ] In Render dashboard, click "+ New"
- [ ] Select "Web Service"
- [ ] Connect to your GitHub repo
- [ ] Configure:
  - **Name**: `emotion-service`
  - **Build**: `cd emotion_service && pip install -r requirements.txt`
  - **Start**: `cd emotion_service && python app.py`
  - **Plan**: Free
- [ ] Add environment variables:
  - `FLASK_ENV=production`
  - `PORT=5000`
  - `DEBUG=False`
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 min)
- [ ] **Save URL**: `https://emotion-service-xxxxx.onrender.com`

### Test Emotion Service
```bash
curl https://emotion-service-xxxxx.onrender.com/health
```
- [ ] Returns `{"status": "healthy"}`

### Deploy Backend
- [ ] In Render dashboard, click "+ New"
- [ ] Select "Web Service"
- [ ] Connect to your GitHub repo
- [ ] Configure:
  - **Name**: `raga-rasa-backend`
  - **Build**: `pip install -r Backend/requirements.txt`
  - **Start**: `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
  - **Plan**: Free
- [ ] Add environment variables from `.env.production`:

```
MONGODB_URL=mongodb+srv://ragarasa:password@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=raga_rasa
USE_EXTERNAL_EMOTION_SERVICE=True
EMOTION_SERVICE_URL=https://emotion-service-xxxxx.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
EMOTION_CONFIDENCE_THRESHOLD=0.3
API_HOST=0.0.0.0
API_PORT=8000
STORAGE_PROVIDER=local
STORAGE_BASE_PATH=./Songs/
JWT_SECRET_KEY=dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
DEBUG=False
```

- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 min)
- [ ] **Save URL**: `https://raga-rasa-backend-xxxxx.onrender.com`

### Test Backend
```bash
curl https://raga-rasa-backend-xxxxx.onrender.com/health
```
- [ ] Returns healthy status

### Verify Emotion Service URL in Backend
- [ ] In Render backend settings, verify `EMOTION_SERVICE_URL`
- [ ] Should point to emotion service public URL
- [ ] Service will redeploy (1-2 min)

### Test Backend-Emotion Integration
```bash
curl https://raga-rasa-backend-xxxxx.onrender.com/api/emotion/detect
```
- [ ] Should work or give proper error (not timeout)

---

## **DAY 2c: GITHUB OAUTH SETUP (30 minutes)**

### Create GitHub OAuth App
- [ ] Go to https://github.com/settings/developers
- [ ] Click "OAuth Apps"
- [ ] Click "New OAuth App"
- [ ] Fill in:
  - **App name**: `Raga Rasa Music Therapy`
  - **Homepage URL**: `https://raga-rasa.vercel.app` (temp)
  - **Authorization callback**: `https://raga-rasa.vercel.app/auth/callback`
- [ ] Click "Register application"

### Get Credentials
- [ ] Copy **Client ID** to `GITHUB_OAUTH_CREDENTIALS.txt`
- [ ] Click "Generate new client secret"
- [ ] Copy **Client Secret** to `GITHUB_OAUTH_CREDENTIALS.txt`
- [ ] **KEEP THESE SECRET!**

### Update Backend Environment
- [ ] In Render backend settings → Environment
- [ ] Add `GITHUB_CLIENT_ID=xxxxx`
- [ ] Add `GITHUB_CLIENT_SECRET=xxxxx`
- [ ] Click Save (backend redeploys)
- [ ] Verify in logs it redeployed successfully

### Save Credentials Locally
Create `GITHUB_OAUTH_CREDENTIALS.txt`:
```
GITHUB_CLIENT_ID=123456789abcdef
GITHUB_CLIENT_SECRET=ghp_xxxxxxxxxxxxxxxxxxxxx
```
- [ ] File created and saved securely

---

## **DAY 2d: DROPBOX IMPLEMENTATION (2-3 hours)**

### Create Dropbox App
- [ ] Go to https://www.dropbox.com/developers/apps
- [ ] Click "Create app"
- [ ] Select:
  - **API**: Scoped API
  - **Type**: App folder
  - **Name**: `raga-rasa-songs`
- [ ] Click "Create app"

### Get Access Token
- [ ] In app settings, find "OAuth 2.0"
- [ ] Click "Generate" access token
- [ ] Copy token (`sl.Bxxxxx...`)
- [ ] Save to `DROPBOX_CREDENTIALS.txt`
- [ ] **KEEP THIS SECRET!**

### Create Folder Structure in Dropbox
- [ ] In your Dropbox app folder create:
  - `/shaant/`
  - `/shringar/`
  - `/veer/`
  - `/shok/`

### Update Code

**Add to `Backend/requirements.txt`**:
```
dropbox==11.36.2
```
- [ ] Added

**Replace DropboxStorageProvider in `Backend/app/services/cloud_storage.py`**:
- [ ] Full implementation added from guide
- [ ] Handles upload, download, delete, list, URL generation
- [ ] Error handling and fallback included

**Update `Backend/app/config.py`**:
- [ ] Add `DROPBOX_ACCESS_TOKEN` field

**Update `Backend/.env`**:
```ini
STORAGE_PROVIDER=local
DROPBOX_ACCESS_TOKEN=
```
- [ ] Added

**Update `Backend/.env.production`**:
```ini
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=sl.Bxxxxxxxxxxxxx
```
- [ ] Added

### Test Locally
```bash
cd Backend
pip install dropbox==11.36.2
python test_dropbox.py
```
- [ ] ✅ Dropbox connection successful!
- [ ] ✅ Files in Dropbox: 0

### Full Test
Create test file with upload/download/delete:
```bash
python test_dropbox_full.py
```
- [ ] ✅ All operations successful

### Verify Dropbox in Backend
- [ ] Change `STORAGE_PROVIDER=dropbox` in `.env`
- [ ] Restart backend: `python -m uvicorn main:app --reload`
- [ ] Test song upload via API
- [ ] Verify file appears in Dropbox web UI

### Update Render Backend
- [ ] Add `DROPBOX_ACCESS_TOKEN=sl.Bxxxxx` to Render environment
- [ ] Update `STORAGE_PROVIDER=dropbox` in Render
- [ ] Backend redeploys
- [ ] Verify in Render logs (no errors)

---

## **FINAL VERIFICATION CHECKLIST**

### MongoDB Atlas
- [ ] ✅ Account created
- [ ] ✅ Cluster "raga-rasa" running
- [ ] ✅ User "ragarasa" created
- [ ] ✅ Connection string saved
- [ ] ✅ IP whitelist includes 0.0.0.0/0
- [ ] ✅ Local backend connects successfully
- [ ] ✅ Can read/write data

### Render.com
- [ ] ✅ Account created
- [ ] ✅ Emotion service deployed and running
- [ ] ✅ Backend service deployed and running
- [ ] ✅ Both services have public URLs
- [ ] ✅ Health endpoints responding
- [ ] ✅ Environment variables all set
- [ ] ✅ Emotion service URL correct in backend

### GitHub OAuth
- [ ] ✅ OAuth app created
- [ ] ✅ Client ID copied and saved
- [ ] ✅ Client secret generated and saved
- [ ] ✅ Credentials added to Render backend
- [ ] ✅ Backend redeployed with new credentials

### Dropbox
- [ ] ✅ Dropbox app created
- [ ] ✅ Access token generated and saved
- [ ] ✅ Folder structure created
- [ ] ✅ `dropbox==11.36.2` installed locally
- [ ] ✅ DropboxStorageProvider implemented
- [ ] ✅ Local connection test passed
- [ ] ✅ Upload/download test passed
- [ ] ✅ Credentials added to Render backend
- [ ] ✅ Backend configured for Dropbox

---

## **CREDENTIALS TO SAVE** (Keep Secure!)

Create secure file `DEPLOYMENT_SECRETS.txt`:

```
=== MONGODB ATLAS ===
Connection URL: mongodb+srv://ragarasa:password@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority

=== RENDER.COM ===
Emotion Service URL: https://emotion-service-xxxxx.onrender.com
Backend Service URL: https://raga-rasa-backend-xxxxx.onrender.com

=== GITHUB OAUTH ===
Client ID: 123456789abcdef
Client Secret: ghp_xxxxxxxxxxxxxxxxxxxxx

=== DROPBOX ===
Access Token: sl.Bxxxxxxxxxxxxxxxxxxxx

=== JWT SECRET ===
JWT Secret: dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY

=== NEXT STEPS ===
1. Update GitHub OAuth settings with actual Vercel domain (once deployed)
2. Update CORS origins in Render backend (add Vercel domain)
3. Deploy frontend to Vercel (Day 3)
4. Test end-to-end
```

- [ ] Created and saved securely

---

## **READY FOR DAY 3?**

When all checkboxes are ✅, proceed to:

### **Day 3: Deployment to Vercel**
- Deploy frontend to Vercel
- Add Vercel domain to CORS origins
- Update GitHub OAuth callback URL
- Test end-to-end

---

**ESTIMATED COMPLETION**: 8-10 hours  
**Current Status**: Ready to start Day 2a
