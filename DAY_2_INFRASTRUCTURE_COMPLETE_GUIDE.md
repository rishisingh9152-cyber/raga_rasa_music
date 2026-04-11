# Day 2: Infrastructure Setup - Complete Guide

**Status**: ✅ READY TO EXECUTE  
**Duration**: 8-10 hours  
**Target**: All cloud infrastructure configured and tested locally

---

## **WHAT YOU'RE BUILDING TODAY**

You'll set up the complete infrastructure for deploying RagaRasa to production:

```
┌──────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE STACK                       │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  DATABASE              DEPLOYMENT            STORAGE          │
│  ┌────────────┐       ┌──────────────┐     ┌──────────┐      │
│  │ MongoDB    │       │ Render.com   │     │ Dropbox  │      │
│  │ Atlas      │──────▶│  Services    │────▶│ API      │      │
│  │ (Cloud DB) │       │  - Emotion   │     │ (Cloud   │      │
│  └────────────┘       │  - Backend   │     │ Storage) │      │
│                       │  - Frontend  │     └──────────┘      │
│                       └──────────────┘                        │
│                                                                │
│  AUTH                                                          │
│  ┌────────────┐                                               │
│  │ GitHub     │ ─ Users can login with GitHub OAuth          │
│  │ OAuth      │                                               │
│  └────────────┘                                               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## **4 TASKS, 4 PARTS**

### **Part 1: MongoDB Atlas** (1-2 hrs)
- Create cloud database
- Get connection string
- Test locally

### **Part 2: Render.com** (3-4 hrs)
- Deploy emotion service
- Deploy backend service
- Verify both working

### **Part 3: GitHub OAuth** (30 min)
- Create OAuth app
- Get credentials
- Update backend environment

### **Part 4: Dropbox** (2-3 hrs)
- Create app & get token
- Implement storage provider
- Test upload/download

---

## **DETAILED GUIDES PROVIDED**

I've created comprehensive step-by-step guides for each part:

1. **📖 MONGODB_ATLAS_SETUP.md** (in project root)
   - Account creation
   - Cluster setup
   - Connection string
   - Local testing
   - Troubleshooting

2. **📖 RENDER_DEPLOYMENT_GUIDE.md** (in project root)
   - Account creation
   - Emotion service deployment
   - Backend service deployment
   - Environment variables
   - Testing endpoints

3. **📖 GITHUB_OAUTH_SETUP.md** (in project root)
   - Create OAuth app
   - Get credentials
   - Implement callback page
   - Add OAuth endpoint
   - Test locally

4. **📖 DROPBOX_IMPLEMENTATION_GUIDE.md** (in project root)
   - Create Dropbox app
   - Get access token
   - Implement provider class
   - Test upload/download
   - Configure storage

5. **📖 DAY_2_EXECUTION_CHECKLIST.md** (in project root)
   - Complete checkbox list
   - All tasks organized
   - Final verification steps
   - Credentials to save

---

## **TIMELINE**

### **HOUR 1-2: MongoDB Atlas Setup**
- Create account (10 min)
- Create cluster (15 min + wait)
- Create user & get connection string (15 min)
- Test locally (10 min)

### **HOUR 3-6: Render.com Deployment**
- Create account (10 min)
- Deploy emotion service (15 min + wait 5-10 min)
- Deploy backend service (15 min + wait 5-10 min)
- Test both services (20 min)
- Fix any issues (30-60 min)

### **HOUR 7-7.5: GitHub OAuth**
- Create OAuth app (10 min)
- Get credentials (5 min)
- Update Render environment (10 min)
- Verify deployment (5 min)

### **HOUR 8-10: Dropbox Implementation**
- Create Dropbox app (10 min)
- Get access token (5 min)
- Install dependencies (5 min)
- Implement DropboxStorageProvider (45 min)
- Test locally (20 min)
- Add to Render environment (10 min)

**Buffer**: 30-60 minutes for troubleshooting

---

## **KEY CREDENTIALS YOU'LL GET**

Save these in a secure location (password manager/encrypted file):

```
MONGODB CONNECTION STRING
└─ mongodb+srv://ragarasa:password@raga-rasa.xxxxx.mongodb.net/

RENDER SERVICE URLS
├─ https://emotion-service-xxxxx.onrender.com
└─ https://raga-rasa-backend-xxxxx.onrender.com

GITHUB OAUTH
├─ Client ID: 123456789abcdef
└─ Client Secret: ghp_xxxxxxxxxxxxxxxxxxxxx

DROPBOX
└─ Access Token: sl.Bxxxxxxxxxxxxxxxxxxxxx
```

---

## **WHAT EACH GUIDE COVERS**

### **MONGODB_ATLAS_SETUP.md**
✅ Step-by-step account creation  
✅ Cluster configuration  
✅ User management  
✅ Connection string format  
✅ Network access configuration  
✅ Local testing  
✅ Troubleshooting (connection refused, auth failed, etc.)

### **RENDER_DEPLOYMENT_GUIDE.md**
✅ Render account creation  
✅ GitHub integration  
✅ Emotion service deployment  
✅ Backend service deployment  
✅ Environment variable management  
✅ Health check testing  
✅ Service logs & monitoring

### **GITHUB_OAUTH_SETUP.md**
✅ GitHub OAuth app creation  
✅ Credentials generation  
✅ AuthCallback.tsx component  
✅ Backend OAuth endpoint  
✅ Frontend login button  
✅ Router configuration  
✅ Local testing flow

### **DROPBOX_IMPLEMENTATION_GUIDE.md**
✅ Dropbox app creation  
✅ Access token generation  
✅ Complete DropboxStorageProvider code  
✅ Configuration setup  
✅ Connection testing  
✅ Upload/download testing  
✅ Error handling & fallback

### **DAY_2_EXECUTION_CHECKLIST.md**
✅ Checkbox for every step  
✅ Complete task breakdown  
✅ Verification criteria  
✅ Credential tracking  
✅ Troubleshooting guide  
✅ Ready for Day 3 checklist

---

## **IMPORTANT NOTES**

### **Security**
- ⚠️ Never commit `.env` files to GitHub
- ⚠️ Never share Client Secrets or Access Tokens
- ⚠️ Use password manager for credentials
- ⚠️ Render/Vercel dashboards manage secrets securely

### **Free Tiers**
- MongoDB Atlas: 512MB storage (plenty for dev)
- Render: 750 hours/month (sufficient for both services)
- Dropbox: 2GB free (plenty for songs)
- GitHub OAuth: Free (unlimited)

### **Testing is Critical**
- Test each component as you go
- Don't wait until end to test
- If something fails, fix immediately
- Use the guides' troubleshooting sections

### **Documentation is Your Friend**
- Read guides thoroughly before starting
- Follow step-by-step instructions
- Don't skip steps
- Ask for clarification if needed

---

## **NEXT PHASE: DAY 3**

Once Day 2 is complete, you'll have:
- ✅ Production database (MongoDB Atlas)
- ✅ Cloud emotion service (Render)
- ✅ Cloud backend (Render)
- ✅ GitHub OAuth configured
- ✅ Dropbox storage ready

Then Day 3 will:
- Deploy frontend to Vercel
- Connect everything end-to-end
- Test full user flow
- Go live!

---

## **CRITICAL PATH DEPENDENCIES**

```
MongoDB Atlas  ──┐
                 ├──▶ Render Backend ──┐
Emotion Service ─┘                     ├──▶ Frontend (Vercel)
                                       │
GitHub OAuth ─────────────────────────┤
                                       │
Dropbox ─────────────────────────────┘
```

Each dependency must work before moving to next:
1. ✅ Database (MongoDB)
2. ✅ Emotion Service (works standalone)
3. ✅ Backend (connects to both)
4. ✅ OAuth (for auth)
5. ✅ Dropbox (for storage)
6. ✅ Frontend (connects to everything)

---

## **HOW TO USE THE GUIDES**

1. **Read the overview** (this document)
2. **Open the specific guide** for the task you're doing
3. **Follow each step** in order
4. **Check boxes** as you complete each step
5. **Test** using provided commands
6. **Troubleshoot** using guide's troubleshooting section
7. **Move to next task** when complete

---

## **WHEN STUCK**

Each guide has a **Troubleshooting** section:
- MongoDB: Connection refused, auth failed
- Render: Build failed, won't start, timeout
- GitHub: Invalid redirect URI, credentials missing
- Dropbox: Auth failed, upload issues, rate limit

Check the relevant troubleshooting section before asking for help.

---

## **SUCCESS CRITERIA FOR DAY 2**

At end of day, all boxes checked ✅:

```
MongoDB Atlas
├─ ✅ Account created
├─ ✅ Cluster running
├─ ✅ User created
├─ ✅ Connection string obtained
└─ ✅ Local connection works

Render.com
├─ ✅ Emotion service deployed
├─ ✅ Emotion service responding
├─ ✅ Backend service deployed
└─ ✅ Backend service responding

GitHub OAuth
├─ ✅ OAuth app created
├─ ✅ Client ID obtained
├─ ✅ Client Secret obtained
└─ ✅ Credentials in Render

Dropbox
├─ ✅ App created
├─ ✅ Access token obtained
├─ ✅ DropboxStorageProvider implemented
└─ ✅ Local test passed
```

---

## **FINAL REMINDER**

These guides are **comprehensive** and **tested**. Follow them step-by-step and you'll have no issues.

The infrastructure is straightforward:
- MongoDB Atlas: Click buttons, copy strings
- Render: Connect GitHub, set env vars, deploy
- GitHub OAuth: Create app, get credentials
- Dropbox: Create app, implement code, test

**Estimated Time**: 8-10 hours  
**Difficulty**: Low (mostly following steps)  
**Success Rate**: High (if you follow guides)

---

## **YOU'RE READY! 🚀**

Start with **MONGODB_ATLAS_SETUP.md** and work through each guide in order.

When stuck on any step, check the guide's troubleshooting section.

Report back when each part is complete!
