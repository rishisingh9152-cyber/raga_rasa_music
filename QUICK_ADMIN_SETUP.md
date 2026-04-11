# 🚀 QUICK SETUP GUIDE - GET YOU ADMIN ACCESS

## Step 1: Start the Backend Server

Open a terminal/PowerShell and run:

```bash
cd Backend
python main.py
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**Wait for the message**: `[Database] Database initialization complete`

---

## Step 2: Setup Your Admin Account

Once backend is running, open a **NEW** terminal/PowerShell and run:

```bash
cd "C:\Major Project"
python setup_admin.py
```

This will:
✅ Connect to your running backend
✅ Create admin account with your email
✅ Return your JWT token
✅ Show "🎉 YOU ARE NOW AN ADMIN!"

---

## Step 3: Start the Frontend

Open another terminal/PowerShell and run:

```bash
cd "C:\Major Project\raga-rasa-soul-main"
npm run dev
```

You should see:
```
Local: http://localhost:5173/
```

---

## Step 4: Login to Your Admin Account

1. Open browser: **http://localhost:5173**
2. Click "Login" button
3. Enter your credentials:
   - **Email**: `rishisingh9152@gmail.com`
   - **Password**: `Ripra@2622`
4. You'll be redirected to Admin Dashboard

---

## 📊 What You Can Do as Admin

Once logged in, go to: **http://localhost:5173/admin**

You have access to:

### 📈 Overview Tab
- Total users count
- Total songs count
- Session statistics
- Average rating

### 👥 Users Tab
- See all registered users
- Promote users to admin
- Demote admins to users
- View user join dates

### 🎵 Songs Tab
- See all songs in catalog
- Delete songs
- View Rasa classifications
- See artist information

---

## 🆘 Troubleshooting

### "Cannot connect to backend"
**Solution**: Make sure backend is running in first terminal
```bash
cd Backend && python main.py
```

### "Admin already exists"
**Solution**: You're already admin! Just login at:
```
http://localhost:5173/login
```

### "Port already in use"
**Solution**: Change port (example for 8081):
```bash
cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port 8081
```

### Dependencies missing
**Solution**: Install them:
```bash
pip install -r Backend/requirements.txt
npm install
```

---

## ✅ Verification Checklist

Before you start, verify:

- [ ] MongoDB running on `localhost:27017`
- [ ] Node.js installed (`node --version`)
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Project files exist in `C:\Major Project`

---

## 📝 Your Credentials

**Email**: `rishisingh9152@gmail.com`
**Password**: `Ripra@2622`
**Role**: `admin`

Keep these safe! You can change password later (when that feature is added).

---

## 🎯 Next Steps

1. ✅ Run `setup_admin.py` to create admin
2. ✅ Start frontend with `npm run dev`
3. ✅ Login at http://localhost:5173/login
4. ✅ Go to admin dashboard
5. ✅ Invite other users to register

---

## 💡 Pro Tips

**Create Test Users:**
- Register as regular user on `/register`
- Promote to admin via `/admin` dashboard

**Test Workflows:**
- Try therapy session as regular user
- Manage users/songs as admin
- Rate songs and see statistics

**Check Logs:**
Backend logs show all operations:
```
INFO: User registered: uuid
INFO: Admin accessed dashboard
INFO: Song deleted: song_id
```

---

## 🔐 Security Reminder

- Keep your password safe
- Don't share credentials
- Change JWT_SECRET_KEY in production
- Use HTTPS in production (not HTTP)

---

## 📞 Need Help?

If you encounter issues:
1. Check backend logs for error messages
2. Verify all services are running
3. Check browser console for frontend errors
4. Ensure port 8080 and 5173 are available

---

**You're all set! Go create an amazing experience.** 🎉
