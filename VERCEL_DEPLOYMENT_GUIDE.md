# Vercel Deployment Guide - Frontend

## Quick Start

Deploy your RagaRasa Music Therapy Frontend to Vercel in 3 minutes.

### Step 1: Connect GitHub to Vercel

1. Go to https://vercel.com/new
2. Click **Continue with GitHub**
3. Authorize Vercel to access your GitHub account
4. Select repository: `raga_rasa_music`

### Step 2: Import Project

1. Vercel will auto-detect it's a Vite project
2. **Framework Preset**: Vite (should be auto-selected)
3. **Root Directory**: `raga-rasa-soul-main`

### Step 3: Environment Variables

Add this environment variable:

| Name | Value |
|------|-------|
| `VITE_API_BASE_URL` | `https://raga-rasa-backend.onrender.com` |

**Important**: This tells the frontend where to find the backend API.

### Step 4: Deploy

Click **Deploy** and wait for the build to complete (2-3 minutes).

## What Vercel Does

✅ **Clones your repo** from GitHub  
✅ **Installs dependencies** with `npm ci`  
✅ **Builds with Vite** using `npm run build`  
✅ **Optimizes** CSS, JavaScript, and images  
✅ **Deploys to CDN** globally for fast loading  
✅ **Provides free HTTPS** with auto-renewal  
✅ **Sets up automatic deployments** on every push to main  

## Your Frontend URLs

After deployment, you'll get:
- **Production URL**: `https://raga-rasa-soul-main.vercel.app` (or custom domain)
- **Preview URLs**: For each pull request

## Environment Variables Explained

### VITE_API_BASE_URL
- **Purpose**: Tells the frontend where the backend API is located
- **Development**: `http://localhost:8000` (local)
- **Production**: `https://raga-rasa-backend.onrender.com` (live)
- **Usage**: All API calls use this base URL

## Testing After Deployment

Once deployed:

1. **Open the frontend URL** in your browser
2. **Test authentication**:
   - Click Register or Login
   - Try creating a new account
   - Verify JWT token works

3. **Test API connection**:
   - Open browser DevTools (F12)
   - Go to Network tab
   - Try logging in
   - Verify `/api/auth/login` requests go to backend

4. **Test session features**:
   - Create a new session
   - Check emotion detection
   - Verify music recommendations load

## Deployments & Rollback

### View Deployments
1. Go to https://vercel.com/dashboard
2. Select `raga_rasa_music` (your project)
3. Click **Deployments** tab
4. See all deployment history

### Rollback to Previous Version
1. Find the deployment you want
2. Click the three dots menu
3. Select **Promote to Production**

### Manual Redeploy
1. Go to Deployments tab
2. Click a deployment
3. Click **Redeploy**

## Automatic Deployments

Every time you push to the `main` branch:
1. Vercel detects the change
2. Automatically builds the project
3. Deploys to production when build succeeds
4. Updates the live URL

**To disable**: Go to Project Settings → Deployments → uncheck "Auto build"

## Performance Tips

### Optimize Images
- Vercel automatically optimizes images
- Use `.webp` format where possible
- Compress before uploading

### Code Splitting
- Vite automatically code-splits your routes
- Each route loads only what it needs
- Faster initial page load

### Caching
- Static assets cached for 1 year
- JavaScript/CSS cached intelligently
- Users get latest version automatically

## Troubleshooting

### Issue: Build Fails
**Error**: "npm run build failed"
**Solution**: 
- Check `raga-rasa-soul-main/package.json` exists
- Verify `build` script is defined
- Run locally: `npm run build` to debug

### Issue: API Calls Return 404
**Error**: "Cannot POST /api/auth/login"
**Solution**:
- Verify `VITE_API_BASE_URL` is set in Vercel
- Ensure backend URL is correct: `https://raga-rasa-backend.onrender.com`
- Check backend service is running

### Issue: Blank Page / JavaScript Error
**Error**: "Cannot read property 'x' of undefined"
**Solution**:
- Check browser console (F12)
- Verify React version compatibility
- Clear browser cache and reload
- Check that `dist/index.html` was built

### Issue: Environment Variable Not Working
**Error**: API requests go to undefined/localhost
**Solution**:
1. Go to Vercel Dashboard
2. Select your project
3. Settings → Environment Variables
4. Verify `VITE_API_BASE_URL` is set
5. Redeploy after adding variables

## Custom Domain (Optional)

To use a custom domain like `raga-rasa.com`:

1. Go to Project Settings → Domains
2. Click **Add Domain**
3. Enter your domain
4. Follow DNS setup instructions
5. Wait for DNS propagation (5-15 minutes)

## Monitoring

### View Logs
1. Go to Deployments
2. Click latest deployment
3. Click **Logs** tab
4. See build logs and errors

### View Errors
- **Runtime Errors**: Check browser console (F12)
- **Build Errors**: Check Vercel build logs
- **API Errors**: Check network tab in DevTools

## Git Workflow

```bash
# Make changes locally
git add .
git commit -m "feature: add new feature"

# Push to GitHub
git push origin main

# Vercel automatically deploys!
# Check progress at https://vercel.com/dashboard
```

## Team Collaboration

Share access to your Vercel project:
1. Go to Project Settings → Git
2. Click **Invite**
3. Enter team member email
4. They can now view deployments and logs

---

## Summary

| Aspect | Details |
|--------|---------|
| **Build Tool** | Vite |
| **Framework** | React 18 |
| **Platform** | Vercel |
| **Build Time** | 2-3 minutes |
| **CDN** | Global (300+ locations) |
| **SSL** | Free HTTPS |
| **Auto-Deploy** | On every git push |
| **Rollback** | One-click restore |

---

**Configuration File**: `raga-rasa-soul-main/vercel.json`  
**Environment Variable**: `VITE_API_BASE_URL`  
**Backend URL**: `https://raga-rasa-backend.onrender.com`  
**Git Commit**: f79d3895  
**Date**: April 11, 2026
