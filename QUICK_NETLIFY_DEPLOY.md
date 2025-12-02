# Quick Deploy to Netlify

## 3-Minute Deployment

### 1️⃣ Push Code (1 min)
```bash
cd hospital_app_23f2005421
git add .
git commit -m "Netlify deployment configuration"
git push origin main
```

### 2️⃣ Connect to Netlify (1 min)
- Go to: https://netlify.com
- Click: "New site from Git"
- Select: `hospital_management_system_app` repo
- Click: Deploy

### 3️⃣ Set Environment Variables (1 min)
In Netlify Dashboard → Site Settings → Build & Deploy → Environment:

```
SECRET_KEY=your-secure-key-here
DATABASE_URL=postgresql://user:pass@host/db
FLASK_ENV=production
```

**OR** use SQLite (leave DATABASE_URL empty)

---

## What's New

✅ `netlify.toml` - Build & function configuration  
✅ `netlify/functions/app.py` - Serverless handler  
✅ `runtime.txt` - Python 3.11  
✅ `.env.example` - Environment template  
✅ `.gitignore` - Git patterns  
✅ Updated `app.py` - Environment variable support  

## Key Files to Review

📖 `NETLIFY_READY.md` - Complete overview  
📖 `NETLIFY_DEPLOYMENT.md` - Detailed setup guide  
📖 `DEPLOYMENT_CHECKLIST.md` - Pre/post checks  

## First Login

Email: `admin@facilities.local`  
Password: `admin123`  
⚠️ Change after first login!

## Test Deployment

✓ Can you access the site?  
✓ Can you log in?  
✓ Can you see the dashboard?  
✓ No database errors in logs?  

## Database Options

| Option | Setup Time | Cost | Notes |
|--------|-----------|------|-------|
| SQLite | 0 min | Free | Good for testing |
| PostgreSQL | 5 min | Free tier | Recommended |

**To use PostgreSQL:**
- Netlify Marketplace → Add PostgreSQL
- Or use external provider (AWS RDS, Railway, etc.)

## Need Help?

```
Build fails → Check Netlify build logs
Database error → Verify DATABASE_URL
Page doesn't load → Clear cache and redeploy
```

---

**Your app is ready! 🚀**

Next: Push to GitHub and Netlify will handle the rest.
