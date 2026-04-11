# MongoDB Atlas Setup Guide - Complete Walkthrough

## **STEP 1: Create MongoDB Atlas Account**

### Option A: Sign Up with GitHub (Recommended)
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Start Free"
3. Click "Sign up with GitHub"
4. Authorize MongoDB to access your GitHub account
5. Fill in your details:
   - First name: [Your name]
   - Last name: [Your name]
   - Email: [Your email - can be different from GitHub]
6. Create strong password (yes, you need one even with GitHub auth)
7. Click "Create your account"

### Option B: Email Sign Up
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Start Free"
3. Enter email and password
4. Click "Create account"
5. Verify email (check inbox)

---

## **STEP 2: Create Your First Cluster**

### Page 1: Choose Cluster Tier
1. After login, you'll see "Create a Deployment" screen
2. Select "Shared" tier (FREE - $0/month)
3. Click "Create Shared Cluster"

### Page 2: Configure Cluster
1. Choose Cloud Provider & Region:
   - Provider: AWS (or your preference)
   - Region: Pick closest to your location (e.g., us-east-1 for USA)
2. Cluster Name: `raga-rasa` (or your choice)
3. Click "Create Deployment"

**⏱️ Wait 3-5 minutes** for cluster to be created

---

## **STEP 3: Create Database User & Get Connection String**

### Create Database User
1. After cluster created, go to "Security" → "Database Access"
2. Click "+ ADD NEW DATABASE USER"
3. Fill in:
   - Username: `ragarasa` (or your choice)
   - Password: Generate secure password (save it!)
   - Database User Privileges: "Built-in Role" → "Atlas admin"
4. Click "Add User"

### Get Connection String
1. Go to "Deployment" → "Databases"
2. Click "Connect" button next to your cluster
3. Choose "Drivers"
4. Select "Python" and version "3.11" (or your Python version)
5. Copy the connection string:

```
mongodb+srv://[username]:[password]@[cluster-name].mongodb.net/?retryWrites=true&w=majority
```

**Replace**:
- `[username]`: Username you created
- `[password]`: Password you created
- `[cluster-name]`: Auto-filled

**Example**:
```
mongodb+srv://ragarasa:MySecurePassword123@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

## **STEP 4: Add IP Whitelist (Network Access)**

This allows your backend to connect from Render.com later.

1. Go to "Security" → "Network Access"
2. Click "+ ADD IP ADDRESS"
3. Click "Allow Access from Anywhere" (for dev/testing)
   - This adds `0.0.0.0/0` (all IPs)
4. Click "Confirm"

**⚠️ Production Security**: Later, replace with specific Render.com IPs

---

## **STEP 5: Update Your Backend Configuration**

### Update `.env` File

Open `Backend/.env` and update:

```ini
# Replace existing line:
MONGODB_URL=mongodb+srv://ragarasa:MySecurePassword123@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority

# Keep everything else the same
DATABASE_NAME=raga_rasa
```

### Create `.env.production` File

This is for Render.com deployment (don't commit to git):

```ini
# Database
MONGODB_URL=mongodb+srv://ragarasa:MySecurePassword123@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=raga_rasa

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Emotion Service (will use Render URL later)
USE_EXTERNAL_EMOTION_SERVICE=True
EMOTION_SERVICE_URL=https://emotion-service.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
EMOTION_CONFIDENCE_THRESHOLD=0.3

# Rasa Model
RASA_MODEL_PATH=./models/rasa_classification/
USE_RASA_MODEL=True

# Storage (Dropbox)
STORAGE_PROVIDER=local
STORAGE_BASE_PATH=./Songs/
DROPBOX_ACCESS_TOKEN=

# JWT & Auth
JWT_SECRET_KEY=dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=https://raga-rasa.vercel.app,http://localhost:5173

# GitHub OAuth (get from GitHub later)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Logging
DEBUG=False
```

---

## **STEP 6: Test Connection Locally**

### Test 1: Test from Python
```python
# Run this in Python terminal
from pymongo import MongoClient

url = "mongodb+srv://ragarasa:MySecurePassword123@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(url)

# Test connection
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Test 2: Test from Backend
```bash
cd Backend
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

Expected output:
```
Database initialized successfully
✅ Connected to MongoDB!
```

---

## **STEP 7: Seed Initial Data (Optional)**

If you want to pre-populate the database:

```bash
cd Backend
python seed_all_data.py
```

This will create:
- Admin user
- Sample songs
- Sample sessions
- Sample ratings

---

## **STEP 8: Create Collections Manually (If Needed)**

If seeds don't work, create collections via Atlas UI:

1. Go to "Databases"
2. Click your cluster
3. Click "+ Create Database"
4. Database name: `raga_rasa`
5. Create these collections:
   - `users`
   - `songs`
   - `sessions`
   - `ratings`
   - `emotions`
   - `psychometric_tests`
   - `admin_config`
   - `storage_config`
   - `storage_migrations`

---

## **VERIFICATION CHECKLIST**

- [ ] MongoDB Atlas account created
- [ ] Cluster "raga-rasa" created
- [ ] Database user "ragarasa" created
- [ ] Connection string copied
- [ ] IP whitelist allows all IPs (0.0.0.0/0)
- [ ] `.env` updated with connection string
- [ ] `.env.production` created
- [ ] Local connection test passed (Python)
- [ ] Backend connection test passed
- [ ] Collections created or seeded
- [ ] Can query data from MongoDB Atlas UI

---

## **NEXT STEPS**

Once MongoDB is verified:
1. Move to Render.com account creation
2. Deploy emotion service
3. Deploy backend to Render
4. Update connection strings in Render

---

## **TROUBLESHOOTING**

### "Connection refused"
- Check IP whitelist includes your IP (or 0.0.0.0/0)
- Wait for cluster to fully initialize

### "Authentication failed"
- Double-check username/password
- Ensure special characters in password are URL-encoded

### "Cannot resolve host"
- Check internet connection
- Verify cluster name in connection string
- Wait a few minutes if cluster just created

---

**Status**: Ready to provide detailed Render.com setup once MongoDB is confirmed working!
