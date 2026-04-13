# VERCEL FRONTEND DEPLOYMENT GUIDE - RAGA RASA SOUL

## Overview

This guide walks through deploying the React frontend to Vercel with automatic CI/CD from GitHub.

**Estimated Deployment Time**: 15 minutes
**Cost Estimate**: Free tier (unlimited deployments, 100GB bandwidth/month)

---

## Prerequisites

Before starting:

1. **Vercel Account**
   - Sign up at https://vercel.com
   - Free tier includes automatic deployments

2. **GitHub Account**
   - Forked/cloned RagaRasa repo
   - Admin access to manage deploy tokens

3. **Backend Ready**
   - Backend deployed to Google Cloud Run
   - Know the backend URL: `https://raga-rasa-backend-xxxxx.run.app`

---

## Step 1: Prepare Frontend Code

### 1.1 Verify Project Structure
```bash
# In raga-rasa-soul-main directory
ls -la
# Should contain:
# - src/
# - public/
# - package.json
# - vite.config.ts
# - tailwind.config.js
# - tsconfig.json
```

### 1.2 Update vite.config.ts
```typescript
// raga-rasa-soul-main/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable for production
    minify: 'terser',
    target: 'es2020',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
```

### 1.3 Create Vercel Config
```json
// raga-rasa-soul-main/vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "@raga_rasa_api_url"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, must-revalidate"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    },
    {
      "source": "/index.html",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/",
      "destination": "/dashboard",
      "permanent": false
    }
  ]
}
```

### 1.4 Update Environment Variables

```bash
# raga-rasa-soul-main/.env.local (for local development)
VITE_API_URL=http://localhost:8000/api
VITE_EMOTION_SERVICE_URL=http://localhost:7860
VITE_DEBUG=true

# raga-rasa-soul-main/.env.production (for Vercel)
VITE_API_URL=https://raga-rasa-backend-xxxxx.run.app/api
VITE_EMOTION_SERVICE_URL=https://raga-rasa-emotion.hf.space
VITE_DEBUG=false
```

---

## Step 2: Connect GitHub Repository

### 2.1 Push Code to GitHub
```bash
cd raga-rasa-soul-main

# Initialize git if not already done
git init
git add .
git commit -m "Frontend: Production-ready React application"

# Push to GitHub
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/raga-rasa-soul.git
git push -u origin main
```

### 2.2 Create GitHub Personal Access Token
```bash
# Go to GitHub Settings → Developer settings → Personal access tokens
# Generate new token with scopes:
# - repo (full control of repositories)
# - read:user
# - user:email

# Save token as: GITHUB_TOKEN=ghp_xxxxx
```

---

## Step 3: Deploy to Vercel

### 3.1 Import Project
```bash
# Option 1: Using Vercel CLI
npm i -g vercel
cd raga-rasa-soul-main
vercel

# Follow prompts:
# 1. Link to existing project? No
# 2. What's your project name? raga-rasa-soul
# 3. In which directory? ./raga-rasa-soul-main
# 4. Want to modify vercel.json? No
```

**Option 2: Using Vercel Dashboard**
```
1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Click "Import Git Repository"
4. Paste: https://github.com/YOUR_USERNAME/raga-rasa-soul
5. Select root directory: raga-rasa-soul-main
6. Click "Import"
```

### 3.2 Configure Build Settings
In Vercel Dashboard:

```
Framework: Vite
Build Command: npm run build
Output Directory: dist
Node.js Version: 18.x (or later)
```

---

## Step 4: Set Up Environment Variables

### 4.1 Add to Vercel Project
In Vercel Dashboard → Settings → Environment Variables:

```
VITE_API_URL = https://raga-rasa-backend-xxxxx.run.app/api
VITE_EMOTION_SERVICE_URL = https://raga-rasa-emotion.hf.space
VITE_DEBUG = false
```

### 4.2 Apply to Environments
Set variables for:
- Production
- Preview
- Development

---

## Step 5: Configure Deployment Rules

### 5.1 Deployment Branches
In Vercel Dashboard → Settings → Git:

```
Production Branch: main
Preview Branches: develop, staging
```

### 5.2 Auto-Deploy Settings
```
✓ Automatically redeploy on push
✓ Require approval for production deployments (optional)
✓ Auto-cancel redundant builds
```

---

## Step 6: Verify Deployment

### 6.1 Check Deployment Status
```bash
# In Vercel Dashboard
# Deployments tab shows:
# - Build status
# - Deployment URL
# - Environment variables
# - Git commit info
```

### 6.2 Test Frontend
```bash
# Get deployment URL from dashboard
export FRONTEND_URL="https://raga-rasa-soul-xxxxx.vercel.app"

# Test page loads
curl -I $FRONTEND_URL

# Expected: 200 OK

# Test API connection
curl -I $FRONTEND_URL/api/health

# Test with browser
open $FRONTEND_URL
```

### 6.3 Check Console Logs
```bash
# In browser DevTools Console
# Should see:
# - No CORS errors
# - API calls to backend successful
# - No 404s for assets
```

---

## Step 7: Set Up Custom Domain (Optional)

### 7.1 Add Domain
In Vercel Dashboard → Settings → Domains:

```
1. Enter domain: app.yourdomain.com
2. Choose DNS configuration:
   - Vercel Nameservers (recommended)
   - CNAME (if using external DNS)
3. Add DNS records:
   - CNAME: cname.vercel-dns.com
4. Verify domain
```

### 7.2 SSL Certificate
```
Vercel automatically provisions:
- Free SSL certificate
- Auto-renewal
- HSTS headers
```

---

## Step 8: Configure Security

### 8.1 Add Security Headers
```bash
# Already in vercel.json, includes:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: SAMEORIGIN
# - X-XSS-Protection: 1; mode=block
# - Content-Security-Policy (optional)
```

### 8.2 Set Up CORS (in Backend)
```bash
# Backend should have frontend URL in CORS origins
CORS_ORIGINS="https://raga-rasa-soul-xxxxx.vercel.app,https://app.yourdomain.com"
```

### 8.3 Enable Rate Limiting
```bash
# Use Vercel Functions for rate limiting
# Or use Backend rate limiter (SlowAPI)
```

---

## Step 9: Set Up CI/CD

### 9.1 Create GitHub Actions (Optional)
```yaml
# .github/workflows/vercel-deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: raga-rasa-soul-main
```

### 9.2 Set GitHub Secrets
```bash
# In GitHub Repository → Settings → Secrets

VERCEL_TOKEN: [from Vercel → Settings → Tokens]
VERCEL_ORG_ID: [from Vercel dashboard]
VERCEL_PROJECT_ID: [from Vercel project]
```

---

## Step 10: Monitoring and Analytics

### 10.1 Enable Analytics
In Vercel Dashboard → Settings → Analytics:

```
✓ Web Vitals
✓ Performance Monitoring
✓ Error Tracking
```

### 10.2 Set Up Alerts
```bash
# Monitor:
- Build failures
- Deployment errors
- Web Vitals degradation
- Traffic spikes
```

---

## Step 11: Production Checklist

Before going live:

- [ ] Frontend builds successfully
- [ ] Environment variables configured
- [ ] API endpoints responding
- [ ] CORS errors resolved
- [ ] Mobile responsiveness tested
- [ ] All pages loading
- [ ] Authentication flows working
- [ ] Error handling in place
- [ ] Performance acceptable
- [ ] Security headers present
- [ ] Analytics tracking working
- [ ] Custom domain configured (if applicable)

---

## Common Issues and Solutions

### Issue: CORS Error from Frontend
```
Error: Access to XMLHttpRequest blocked by CORS
```

**Solution**:
1. Check backend CORS configuration
2. Update CORS_ORIGINS to include Vercel URL
3. Restart backend
```bash
gcloud run services update raga-rasa-backend \
  --set-env-vars=CORS_ORIGINS="https://raga-rasa-soul-xxxxx.vercel.app"
```

### Issue: Build Fails with Module Not Found
```
Error: Cannot find module '@/components/...'
```

**Solution**:
1. Verify `vite.config.ts` has correct alias
2. Check that all imports use correct paths
3. Verify `tsconfig.json` has compilerOptions.paths configured

### Issue: Environment Variables Not Loading
```
VITE_API_URL is undefined
```

**Solution**:
1. Variables must start with `VITE_` in Vite
2. Restart build after changing variables
3. Check Vercel Environment Variables section
4. Verify correct environment selected (Production/Preview/Development)

### Issue: Slow Build Time
**Solution**:
1. Optimize dependencies in package.json
2. Use dynamic imports for large components
3. Enable code splitting
4. Check for unused dependencies: `npm prune`

### Issue: 404 on Client-Side Routes
**Solution**: Add rewrite rule in `vercel.json`
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## Cost Optimization

1. **Free Tier Includes**:
   - Unlimited deployments
   - 100GB bandwidth/month
   - Unlimited projects
   - SSL certificates
   - Git integration

2. **Paid Features** (if needed):
   - Pro: $20/month (priority support, team features)
   - Enterprise: Custom pricing

3. **Cost Estimate**: $0/month (free tier sufficient)

---

## Next Steps

1. Set up backend on Google Cloud Run (see GOOGLE_CLOUD_RUN_DEPLOYMENT.md)
2. Deploy emotion service to HF Spaces (see HF_SPACES_EMOTION_DEPLOYMENT.md)
3. Configure monitoring and alerting
4. Set up automated backups
5. Plan for scaling and CDN optimization

---

## Useful Links

- Vercel Docs: https://vercel.com/docs
- Vite Docs: https://vitejs.dev/guide/ssr.html
- React Docs: https://react.dev
- Vercel Deployment Guide: https://vercel.com/docs/concepts/deployments/overview

**Last Updated**: April 2026
**Version**: 1.0
