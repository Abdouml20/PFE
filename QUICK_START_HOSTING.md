# 🚀 Quick Start: Deploy to Free Hosting

## Recommended: Render + Cloudinary (5 minutes setup)

### Step 1: Get Cloudinary Account (Free)
1. Go to https://cloudinary.com/users/register_free
2. Sign up (free tier: 25GB storage, 25GB bandwidth/month)
3. Go to Dashboard → Copy these 3 values:
   - **Cloud name**
   - **API Key**
   - **API Secret**

### Step 2: Update Your Code

**A. Update requirements.txt:**
```bash
# Add these two lines to requirements.txt:
django-cloudinary-storage==0.3.0
cloudinary==1.36.0
```

**B. Update settings.py:**

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'cloudinary',
    'cloudinary_storage',
]
```

Add after `MEDIA_ROOT = BASE_DIR / 'media'`:
```python
# Cloudinary configuration for production
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# Use Cloudinary for media storage in production
if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Step 3: Deploy to Render

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Cloudinary support"
   git push
   ```

2. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render auto-detects Django from `render.yaml`
   - Click "Create Web Service"

3. **Add PostgreSQL Database:**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Name it (e.g., "crafty-db")
   - Click "Create"
   - Copy the "Internal Database URL"

4. **Set Environment Variables in Render:**
   Go to your Web Service → Environment tab, add:
   ```
   DEBUG=False
   SECRET_KEY=<generate-a-random-secret-key>
   ALLOWED_HOSTS=your-app-name.onrender.com
   DATABASE_URL=<from-postgres-service>
   CLOUDINARY_CLOUD_NAME=<from-cloudinary-dashboard>
   CLOUDINARY_API_KEY=<from-cloudinary-dashboard>
   CLOUDINARY_API_SECRET=<from-cloudinary-dashboard>
   ```

5. **Deploy!**
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait 5-10 minutes
   - Your app will be live!

### Step 4: Run Migrations

After first deployment, in Render dashboard:
- Go to your Web Service → Shell
- Run: `python manage.py migrate`
- Run: `python manage.py createsuperuser`

---

## ✅ That's It!

Your Django app is now live with:
- ✅ Free PostgreSQL database
- ✅ Free cloud storage for images/videos (25GB)
- ✅ Automatic image optimization
- ✅ CDN for fast delivery
- ✅ User accounts working
- ✅ File uploads working

**Your app URL:** `https://your-app-name.onrender.com`

---

## 🔧 Troubleshooting

**Media files not uploading?**
- Check Cloudinary env vars are set correctly
- Verify `DEFAULT_FILE_STORAGE` is set in settings.py

**Database errors?**
- Check `DATABASE_URL` is set correctly
- Run migrations: `python manage.py migrate`

**Static files not loading?**
- Render runs `collectstatic` automatically
- Check WhiteNoise is in MIDDLEWARE

---

## 📊 Free Tier Limits

**Render:**
- 750 hours/month (enough for always-on if you upgrade to $7/mo)
- Spins down after 15 min inactivity (first request may be slow)

**Cloudinary:**
- 25GB storage
- 25GB bandwidth/month
- 10MB max file size
- Image optimization included

---

## 💡 Pro Tips

1. **Always-on:** Upgrade Render to $7/month to prevent spin-down
2. **Custom Domain:** Add your domain in Render dashboard
3. **Backups:** Set up automatic database backups
4. **Monitoring:** Monitor usage in both Render and Cloudinary dashboards

---

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- Cloudinary Docs: https://cloudinary.com/documentation/django_integration
- See `HOSTING_GUIDE.md` for detailed information

