# GitHub OAuth Setup Guide

## **WHAT IS GITHUB OAUTH?**

This allows users to log in with their GitHub account instead of creating a new username/password. Your app redirects to GitHub, user approves, and you get their profile info.

---

## **STEP 1: Create GitHub OAuth Application**

### Navigate to GitHub Settings
1. Go to https://github.com/settings/developers
2. Click "OAuth Apps"
3. Click "New OAuth App"

### Fill in Application Details

**Application name**:
```
Raga Rasa Music Therapy
```

**Homepage URL**:
```
https://raga-rasa.vercel.app
```
*(We'll update this when frontend is deployed to Vercel)*

**Application description** (optional):
```
Music therapy application using Indian classical ragas for emotion-based healing
```

**Authorization callback URL**:
```
https://raga-rasa.vercel.app/auth/callback
```
*(This is where GitHub redirects after user approves)*

### Create Application
1. Click "Register application"
2. You'll see your credentials page

---

## **STEP 2: Get Your Credentials**

On the OAuth app page, you'll see:

1. **Client ID** (visible):
   - Starts with a number
   - Example: `123456789abcdef`
   - You can share this publicly

2. **Client Secret** (hidden):
   - Long string
   - Click "Generate a new client secret"
   - **⚠️ KEEP THIS SECRET** - save in password manager
   - Example: `ghp_xxxxxxxxxxxxxxxxxxx`

### Save Credentials

Create file `GITHUB_OAUTH_CREDENTIALS.txt` (don't commit!):
```
# GitHub OAuth Credentials
GITHUB_CLIENT_ID=123456789abcdef
GITHUB_CLIENT_SECRET=ghp_xxxxxxxxxxxxxxxxxxx
```

---

## **STEP 3: Update Environment Variables**

### For Local Development
Update `Backend/.env`:
```ini
GITHUB_CLIENT_ID=123456789abcdef
GITHUB_CLIENT_SECRET=ghp_xxxxxxxxxxxxxxxxxxx
```

Update `raga-rasa-soul-main/.env.development`:
```
VITE_GITHUB_CLIENT_ID=123456789abcdef
VITE_GITHUB_REDIRECT_URI=http://localhost:5173/auth/callback
```

### For Production (Render)
Update Render backend environment:
1. Go to backend service → Environment
2. Add variables:
   ```
   GITHUB_CLIENT_ID=123456789abcdef
   GITHUB_CLIENT_SECRET=ghp_xxxxxxxxxxxxxxxxxxx
   ```

### For Production (Vercel)
In Vercel dashboard:
1. Go to project → Settings → Environment Variables
2. Add:
   ```
   VITE_GITHUB_CLIENT_ID=123456789abcdef
   VITE_GITHUB_REDIRECT_URI=https://raga-rasa.vercel.app/auth/callback
   ```

---

## **STEP 4: Create OAuth Callback Page (Frontend)**

The user needs a page to land on after GitHub approves. Create:

**File**: `raga-rasa-soul-main/src/pages/AuthCallback.tsx`

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function AuthCallback() {
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get authorization code from URL
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');

        if (!code) {
          throw new Error('No authorization code received');
        }

        // Exchange code for token via backend
        const response = await fetch('/api/auth/github/callback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, state }),
        });

        if (!response.ok) {
          throw new Error('GitHub authentication failed');
        }

        const data = await response.json();
        
        // Store token and user info
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Update auth context
        login(data.user, data.access_token);

        // Redirect to home
        navigate('/');
      } catch (error) {
        console.error('Auth error:', error);
        navigate('/login?error=auth_failed');
      }
    };

    handleCallback();
  }, [navigate, login]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2>Authenticating with GitHub...</h2>
        <p>Please wait while we complete your login.</p>
      </div>
    </div>
  );
}
```

---

## **STEP 5: Create Backend OAuth Endpoint**

**File**: `Backend/app/routes/auth.py` - Add this endpoint:

```python
@router.post("/auth/github/callback")
async def github_callback(request: Dict[str, Any]):
    """
    Handle GitHub OAuth callback
    Exchange authorization code for access token
    """
    try:
        code = request.get("code")
        state = request.get("state")
        
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Missing authorization code"
            )
        
        # Exchange code for GitHub access token
        import os
        import httpx
        
        github_client_id = os.getenv("GITHUB_CLIENT_ID")
        github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        
        async with httpx.AsyncClient() as client:
            # Get access token from GitHub
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": github_client_id,
                    "client_secret": github_client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"}
            )
            
            token_data = token_response.json()
            
            if "error" in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"GitHub error: {token_data['error']}"
                )
            
            github_token = token_data.get("access_token")
            
            # Get user profile from GitHub
            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {github_token}"}
            )
            
            github_user = user_response.json()
            
            # Get user email
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"token {github_token}"}
            )
            
            emails = email_response.json()
            email = next(
                (e["email"] for e in emails if e["primary"]),
                github_user.get("email")
            )
            
            # Find or create user in database
            db = get_db()
            user = await db.users.find_one({"email": email})
            
            if not user:
                # Create new user from GitHub profile
                import uuid
                user_id = str(uuid.uuid4())
                user = {
                    "user_id": user_id,
                    "email": email,
                    "name": github_user.get("name", ""),
                    "github_username": github_user.get("login", ""),
                    "role": "user",
                    "provider": "github",
                    "created_at": datetime.utcnow(),
                    "preferences": {
                        "favorite_ragas": [],
                        "preferred_time_of_day": None,
                        "listening_frequency": None
                    },
                    "total_sessions": 0
                }
                await db.users.insert_one(user)
                logger.info(f"New GitHub user created: {user_id}")
            
            # Create JWT token
            access_token = create_access_token(
                user["user_id"],
                user["email"],
                user.get("role", "user")
            )
            
            return TokenSchema(
                access_token=access_token,
                token_type="bearer",
                user={
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "name": user.get("name", ""),
                    "role": user.get("role", "user")
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub callback failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="GitHub authentication failed"
        )
```

---

## **STEP 6: Update Login Page with GitHub Button**

**File**: `raga-rasa-soul-main/src/pages/Login.tsx`

Add GitHub button:

```typescript
function handleGitHubLogin() {
  const client_id = import.meta.env.VITE_GITHUB_CLIENT_ID;
  const redirect_uri = import.meta.env.VITE_GITHUB_REDIRECT_URI || 
    window.location.origin + '/auth/callback';
  
  const github_auth_url = `https://github.com/login/oauth/authorize?client_id=${client_id}&redirect_uri=${redirect_uri}&scope=user:email`;
  
  window.location.href = github_auth_url;
}

export function Login() {
  return (
    <div className="...">
      {/* Existing login form */}
      
      <div className="mt-4 flex gap-2">
        <button
          onClick={handleGitHubLogin}
          className="w-full bg-gray-800 text-white py-2 rounded hover:bg-gray-900"
        >
          Login with GitHub
        </button>
      </div>
    </div>
  );
}
```

---

## **STEP 7: Add Router Entry**

Update your frontend routing to include the callback page:

**File**: `raga-rasa-soul-main/src/main.tsx` or `src/App.tsx`

```typescript
import { AuthCallback } from './pages/AuthCallback';

const routes = [
  // ... existing routes
  {
    path: '/auth/callback',
    element: <AuthCallback />,
  },
];
```

---

## **VERIFICATION CHECKLIST**

- [ ] GitHub OAuth app created
- [ ] Client ID copied and saved
- [ ] Client Secret generated and saved (securely!)
- [ ] Authorization callback URL correct in GitHub settings
- [ ] Environment variables updated (Backend)
- [ ] Environment variables updated (Frontend)
- [ ] `AuthCallback.tsx` page created
- [ ] GitHub callback endpoint created in backend
- [ ] Login page has GitHub button
- [ ] Router includes `/auth/callback` route
- [ ] All environment variables in Render/Vercel dashboards

---

## **TESTING OAUTH LOCALLY**

### Test with Local Frontend

1. Start backend:
   ```bash
   cd Backend
   python -m uvicorn main:app --reload
   ```

2. Start frontend:
   ```bash
   cd raga-rasa-soul-main
   npm run dev
   ```

3. In `src/pages/Login.tsx`, temporarily update redirect URI:
   ```typescript
   const redirect_uri = 'http://localhost:5173/auth/callback';
   ```

4. Click "Login with GitHub"
5. GitHub will ask to authorize
6. You'll be redirected to callback page
7. Token should be stored in localStorage

### Verify Token
```javascript
// In browser console
console.log(localStorage.getItem('access_token'))
```

---

## **TROUBLESHOOTING**

### "Invalid redirect URI"
- GitHub redirect must exactly match your app's redirect URL
- Check for trailing slashes, protocols, ports

### "Invalid client ID"
- Copy-paste exact Client ID from GitHub settings
- No extra spaces

### User not found after GitHub auth
- Check backend logs for database errors
- Verify user collection exists in MongoDB
- Check email extraction from GitHub API

### CORS errors
- Add frontend domain to `ALLOWED_ORIGINS` in Render backend
- Example: `https://raga-rasa.vercel.app`

---

**Status**: GitHub OAuth ready for implementation! Proceed to Day 2d (Dropbox provider) next.
