# Fix Permission Denied Error - Use Personal Access Token

## Problem
Your system has cached credentials for a different GitHub account (`rishisingh9152-cyber`), preventing push to `rishi17205-ops`.

## Solution: Personal Access Token (5 minutes)

### Step 1: Generate a GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens/new
2. **Token name:** `opencode-push`
3. **Select scopes:**
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (if you want to manage workflows)
4. **Click "Generate token"**
5. **COPY the token** (shows only once!)

Example token looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Update Git Remote URL with Token

Replace YOUR_TOKEN with the actual token:

```bash
git remote set-url origin https://rishi17205-ops:YOUR_TOKEN@github.com/rishi17205-ops/raga_rasa_music_therapy.git
```

For example:
```bash
git remote set-url origin https://rishi17205-ops:ghp_1234567890abcdefghijklmnopqrstuv@github.com/rishi17205-ops/raga_rasa_music_therapy.git
```

### Step 3: Push to GitHub

```bash
git push -u origin main
```

No password prompt - should push immediately!

### Step 4: Verify

Check your repository at:
https://github.com/rishi17205-ops/raga_rasa_music_therapy

---

## Alternative: Use Windows Credential Manager

If you prefer NOT to embed token in URL:

1. Go to: Control Panel → Credential Manager → Windows Credentials
2. Find: `git:https://github.com`
3. Edit it, change password to your GitHub Personal Access Token
4. Then run: `git push -u origin main`

---

## ⚠️ Security Note

**NEVER commit your token to git!** If you embed it in the URL:
- Don't push the `.git/config` file anywhere
- Use environment variables for sensitive data
- Consider removing token from URL after first push

Safe method:
```bash
# After first push, remove token from URL
git remote set-url origin https://github.com/rishi17205-ops/raga_rasa_music_therapy.git

# Authenticate with token only when needed using credential manager
```

---

## Steps Summary

1. Go to https://github.com/settings/tokens/new
2. Generate token with `repo` scope
3. Copy token
4. Run: `git remote set-url origin https://rishi17205-ops:YOUR_TOKEN@github.com/rishi17205-ops/raga_rasa_music_therapy.git`
5. Run: `git push -u origin main`
6. Verify at GitHub repository page
7. (Optional) Remove token from URL afterward

Done! Your code will be on GitHub.
