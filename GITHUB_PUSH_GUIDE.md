# GitHub Push Guide - Step by Step

## Current Status

✅ **Committed to local git:**
- Song streaming fix (ce79ebb)
- Emotion-to-rasa mapping update (f8b3c12)
- Authentication & auth state management (3fbaaad)
- API fixes and integration (multiple commits)

⏳ **Uncommitted changes:**
- Frontend modifications: LiveSession.tsx, MusicPlayer.tsx
- Many test scripts and documentation files

---

## Option A: Push to GitHub (EASIEST)

### Step 1: Create a GitHub Repository
1. Go to https://github.com/new
2. Name it: `raga-rasa-music-therapy` (or your preferred name)
3. Choose: **Public** (for open source) or **Private** (for private)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

### Step 2: Add Remote to Your Local Repository
Copy the HTTPS URL from GitHub (should look like):
```
https://github.com/YOUR_USERNAME/raga-rasa-music-therapy.git
```

Then run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/raga-rasa-music-therapy.git
```

### Step 3: Commit Uncommitted Changes (Optional)
If you want to keep the frontend changes:
```bash
git add raga-rasa-soul-main/src/components/session/LiveSession.tsx
git add raga-rasa-soul-main/src/pages/MusicPlayer.tsx
git commit -m "feat: enhance music player and live session UI"
```

Or discard them if not needed:
```bash
git restore raga-rasa-soul-main/src/components/session/LiveSession.tsx
git restore raga-rasa-soul-main/src/pages/MusicPlayer.tsx
```

### Step 4: Push to GitHub
```bash
git branch -M main
git push -u origin main
```

You'll be prompted to authenticate:
- **Username:** Your GitHub username
- **Password:** Your GitHub Personal Access Token (NOT your password)
  - Generate token at: https://github.com/settings/tokens
  - Scopes needed: `repo` (full control of private repositories)

---

## Option B: Include Documentation & Tests

If you want to push everything (including docs and test files):

### Step 1: Create .gitignore (clean up unnecessary files)

Create file: `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Node/Frontend
node_modules/
dist/
.vite

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Keep test scripts, exclude only generated outputs
# test_*.py files are kept to show testing effort
```

### Step 2: Clean up test/debug scripts (optional)
```bash
# Remove only debug/setup scripts we don't need
rm Backend/debug_*.py Backend/check_*.py Backend/setup_*.py

# Keep test_*.py scripts as they show testing
```

### Step 3: Organize documentation

Create a `docs/` folder:
```bash
mkdir docs
mv RECOMMENDATION_ENGINE_EXPLAINED.md docs/
mv RECOMMENDATION_VISUAL_FLOW.md docs/
mv RECOMMENDATION_QUICK_REFERENCE.md docs/
mv *.md docs/  # (keep important ones)
```

### Step 4: Create main README.md

Create: `README.md`
```markdown
# RagaRasa Music Therapy Platform

An AI-powered emotion-based music therapy system using Indian classical music ragas.

## Features

- **Emotion Detection:** Real-time emotion detection using psychometric tests
- **Smart Recommendations:** Hybrid recommendation engine combining:
  - Content-based filtering (user's cognitive state)
  - Collaborative filtering (community ratings)
  - Emotion-to-rasa mapping (therapeutic music selection)
- **Music Streaming:** Audio streaming of 68+ Indian classical music tracks
- **Session Management:** Track therapy sessions and user progress
- **Authentication:** JWT-based auth with role-based access control

## Quick Start

See [docs/QUICK_START.md](docs/QUICK_START.md) for setup instructions.

## Architecture

- **Backend:** FastAPI + MongoDB
- **Frontend:** React + Vite
- **Emotion Service:** Flask (external)

## Documentation

- [API Documentation](docs/API_ERROR_FIXES.md)
- [Recommendation Engine](docs/RECOMMENDATION_ENGINE_EXPLAINED.md)
- [Audio Player Guide](docs/HOW_TO_SEE_AUDIO_PLAYER.md)

## License

MIT License - See LICENSE file
```

### Step 5: Push everything
```bash
git add .
git commit -m "docs: add comprehensive documentation and test scripts"
git push -u origin main
```

---

## What Gets Pushed

### Will be pushed:
- ✅ All source code (Backend & Frontend)
- ✅ All commits (history preserved)
- ✅ Documentation files
- ✅ Test scripts
- ✅ Configuration files

### Won't be pushed (recommended):
- ❌ `.env` files (environment variables with secrets)
- ❌ `node_modules/` (install via npm install)
- ❌ `__pycache__/` (Python cache)
- ❌ `venv/` (virtual environment)

---

## After Pushing

### Make it visible:
1. Add a description to your GitHub repo
2. Add topics: `music-therapy`, `ai`, `emotion-detection`, `indian-classical`
3. Add a GitHub Actions workflow for CI/CD (optional)

### For others to use:
1. Create a CONTRIBUTING.md guide
2. Add issue templates
3. Create a LICENSE file (MIT recommended)

---

## Troubleshooting

### Authentication Failed
**Problem:** "fatal: could not read Username"

**Solution:**
1. Go to https://github.com/settings/tokens
2. Generate a new Personal Access Token
3. Copy the token
4. When prompted for password, paste the token instead

### Permission Denied (SSH)
**Problem:** "Permission denied (publickey)"

**Solution:** Use HTTPS instead:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/raga-rasa-music-therapy.git
```

### Branch Name Mismatch
**Problem:** "refs/heads/master does not match any existing ref"

**Solution:**
```bash
git branch -M main
git push -u origin main
```

---

## Complete Command Sequence

```bash
# 1. Add remote (replace URL)
git remote add origin https://github.com/YOUR_USERNAME/raga-rasa-music-therapy.git

# 2. Commit any pending changes
git add .
git commit -m "feat: latest updates and documentation"

# 3. Rename branch to main
git branch -M main

# 4. Push to GitHub
git push -u origin main

# 5. Verify
git remote -v
```

---

## Next Steps

After pushing to GitHub:

1. **Invite collaborators:** Settings → Collaborators
2. **Enable Issues:** Settings → Enable issues for tracking
3. **Set up branch protection:** Settings → Branches → Add rule
4. **Create releases:** Go to Releases → Create a new release

---

Would you like me to help you execute these steps?
