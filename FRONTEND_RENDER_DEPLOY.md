# Frontend Deployment Guide for Render

## Overview

The RagaRasa Music Therapy Frontend is a React + Vite application that will be deployed on Render using Docker.

**Live Frontend URL:** Will be `https://raga-rasa-frontend.onrender.com` (or similar)
**Live Backend URL:** https://raga-rasa-backend.onrender.com

## Deployment Steps

### 1. Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Select your GitHub repository: `raga_rasa_music`
4. Select branch: `main`

### 2. Configure the Frontend Service

| Setting | Value |
|---------|-------|
| **Name** | `raga-rasa-frontend` |
| **Environment** | Docker |
| **Dockerfile Path** | `./raga-rasa-soul-main/Dockerfile` |
| **Root Directory** | Leave empty (default) |
| **Region** | Oregon (or your preferred region) |
| **Instance Type** | Free (or paid if needed) |

### 3. Set Environment Variables

Add the following environment variable in Render:

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://raga-rasa-backend.onrender.com` |

### 4. Deploy

Click **Create Web Service** and wait for the deployment to complete (5-15 minutes).

## What Gets Deployed

### Build Process
1. Node.js 18 Alpine image pulls dependencies
2. Vite builds the React application to `dist/` folder
3. Nginx Alpine image serves the static files
4. Nginx is configured to proxy `/api/*` requests to the backend

### Production Build
- **Output**: Optimized React bundle in `dist/`
- **Server**: Nginx (lightweight, fast)
- **Port**: 80 (HTTP)
- **Health Check**: `/health` endpoint

## Nginx Configuration

The `nginx.conf` file includes:

- **SPA Routing**: All URLs route to `index.html` (except assets and `/api`)
- **API Proxy**: `/api/*` requests forward to the backend
- **Caching**: Static assets cached for 1 year
- **Gzip Compression**: Reduces file sizes
- **CORS Headers**: Allows cross-origin requests from backend

## Frontend Features

✅ React 18 + TypeScript  
✅ Vite (fast build tool)  
✅ TailwindCSS + Shadcn UI  
✅ React Router (client-side routing)  
✅ Authentication (with JWT tokens)  
✅ Session management  
✅ Audio player  
✅ Emotion detection UI  
✅ Music recommendations  
✅ Admin dashboard  

## Troubleshooting

### Issue: Build Fails
- Check that `raga-rasa-soul-main/package.json` exists
- Ensure `npm ci` completes successfully
- Check `npm run build` output for errors

### Issue: API Calls Return 404
- Verify `VITE_API_BASE_URL` is set to backend URL
- Check that backend service is running
- Verify nginx proxy configuration in `nginx.conf`

### Issue: Frontend Loads But Shows Blank Page
- Check browser console for JavaScript errors
- Verify React version compatibility
- Check that `index.html` exists in `dist/`

## Rollback

To rollback to a previous version:
1. Go to Render Dashboard
2. Select `raga-rasa-frontend` service
3. Click **Deployments**
4. Select a previous deployment
5. Click **Redeploy**

## Monitoring

Check logs in Render:
1. Go to `raga-rasa-frontend` service
2. Click **Logs**
3. View real-time build and runtime logs

## Next Steps

After deployment:
1. Visit the live frontend URL
2. Test user authentication (register/login)
3. Test session creation and music recommendations
4. Verify API calls reach the backend successfully
5. Test emotion detection and psychometric tests

---

**Git Commit**: 07621509 - Docker frontend configuration  
**Date**: April 11, 2026
