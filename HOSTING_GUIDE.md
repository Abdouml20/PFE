# Free Hosting Guide for Crafty Project

## 🎯 Best Options for Free Hosting

### Option 1: Render + Cloudinary (RECOMMENDED) ⭐

**Why this combination:**
- Render provides free PostgreSQL database
- Cloudinary provides 25GB free storage for images/videos
- Automatic image optimization and CDN
- Easy to set up and maintain

**Setup Steps:**

1. **Deploy to Render:**
   - Push your code to GitHub
   - Connect GitHub to Render
   - Render will auto-detect `render.yaml` and deploy
   - Get your PostgreSQL database URL from Render dashboard

2. **Set up Cloudinary (for media files):**
   - Sign up at https://cloudinary.com (free tier)
   - Get your Cloudinary credentials:
     - Cloud name
     - API Key
     - API Secret
   - Install: `pip install django-cloudinary-storage`
   - Add to `requirements.txt`: `django-cloudinary-storage`

3. **Update settings.py:**
   ```python
   # Add to INSTALLED_APPS
   'cloudinary',
   'cloudinary_storage',
   
   # Media files configuration
   MEDIA_URL = '/media/'
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   
   # Cloudinary settings
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
       'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
   }
   ```

4. **Set environment variables in Render:**
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   - `DATABASE_URL` (auto-set by Render)
   - `SECRET_KEY` (generate one)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.onrender.com`

**Limitations:**
- Free tier spins down after 15 min inactivity (first request may be slow)
- 750 hours/month free (enough for always-on if you upgrade to $7/month)

---

### Option 2: Railway + Cloudinary

**Why:**
- $5 free credit/month (usually enough for small apps)
- Fast deployment
- Good performance

**Setup:**
1. Sign up at https://railway.app
2. Connect GitHub repo
3. Railway auto-detects Django
4. Add PostgreSQL service
5. Follow Cloudinary setup from Option 1
6. Set environment variables in Railway dashboard

**Limitations:**
- Credit-based (may run out)
- Need to monitor usage

---

### Option 3: PythonAnywhere (You Already Have Config!)

**Why:**
- Media files stored on disk (persist)
- You already have configuration files
- Good for learning/testing

**Setup:**
1. Follow your `pythonanywhere_checklist.md`
2. Media files will be stored in `/home/username/crafty/media`
3. Configure static/media file mappings in Web tab

**Limitations:**
- Limited CPU seconds/day on free tier
- No custom domain on free tier
- May need to upgrade for production

---

### Option 4: Fly.io + Cloudinary

**Why:**
- Persistent volumes available
- Good performance
- Global edge network

**Setup:**
1. Install Fly CLI
2. Run `fly launch` in project directory
3. Follow Cloudinary setup
4. Configure persistent volume if needed

**Limitations:**
- More complex setup
- Need to manage volumes

---

## 📦 Cloud Storage Setup (Required for Render/Railway)

### Cloudinary Setup (Recommended)

1. **Install package:**
   ```bash
   pip install django-cloudinary-storage
   ```

2. **Add to requirements.txt:**
   ```
   django-cloudinary-storage
   cloudinary
   ```

3. **Update settings.py:**
   ```python
   INSTALLED_APPS = [
       # ... existing apps ...
       'cloudinary',
       'cloudinary_storage',
   ]
   
   # Media files
   MEDIA_URL = '/media/'
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   
   # Cloudinary configuration
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
       'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
   }
   ```

4. **Get Cloudinary credentials:**
   - Sign up: https://cloudinary.com/users/register_free
   - Go to Dashboard
   - Copy: Cloud name, API Key, API Secret

5. **Set environment variables** in your hosting platform

### Alternative: AWS S3 (More Complex)

If you prefer S3:
- Install: `pip install django-storages boto3`
- Configure in settings.py
- Set up IAM user and bucket
- More setup required but more control

---

## 🚀 Quick Start: Render + Cloudinary

### Step-by-Step:

1. **Prepare your code:**
   ```bash
   # Make sure render.yaml exists (you have it)
   # Update requirements.txt to include:
   django-cloudinary-storage
   cloudinary
   ```

2. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

3. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect Django
   - Add PostgreSQL database
   - Set environment variables

4. **Set up Cloudinary:**
   - Sign up at https://cloudinary.com
   - Get credentials
   - Add to Render environment variables

5. **Update settings.py** (see code above)

6. **Deploy!**

---

## 📊 Comparison Table

| Platform | Database | Media Storage | Free Tier | Best For |
|----------|----------|---------------|-----------|----------|
| **Render** | PostgreSQL | Cloudinary needed | 750 hrs/month | Production-ready |
| **Railway** | PostgreSQL | Cloudinary needed | $5 credit/month | Fast deployment |
| **PythonAnywhere** | MySQL | On-disk (persists) | Limited CPU | Learning/testing |
| **Fly.io** | PostgreSQL | Cloudinary or volumes | Generous | Advanced users |

---

## ⚠️ Important Notes

1. **Media Files:** Never store media files on Render/Railway filesystem - they get wiped on redeploy
2. **Database:** Use PostgreSQL for production (SQLite is for dev only)
3. **Static Files:** Use WhiteNoise (already configured) or CDN
4. **Environment Variables:** Never commit secrets to Git
5. **Backups:** Set up regular database backups
6. **Monitoring:** Monitor your usage to avoid unexpected charges

---

## 🔧 Troubleshooting

### Media files not uploading?
- Check Cloudinary credentials are set correctly
- Verify `DEFAULT_FILE_STORAGE` is set
- Check file size limits (Cloudinary free: 10MB per file)

### Database connection issues?
- Verify `DATABASE_URL` is set correctly
- Check database is running in Render/Railway dashboard
- Run migrations: `python manage.py migrate`

### Static files not loading?
- Run `python manage.py collectstatic`
- Check WhiteNoise is configured
- Verify `STATIC_ROOT` is set

---

## 💡 Recommendation

**For your project, I recommend: Render + Cloudinary**

**Reasons:**
1. ✅ You already have `render.yaml` configured
2. ✅ Free PostgreSQL database
3. ✅ Cloudinary handles images/videos perfectly (25GB free)
4. ✅ Automatic image optimization
5. ✅ CDN for fast delivery
6. ✅ Easy to scale later

**Next Steps:**
1. Sign up for Render and Cloudinary (both free)
2. Update `settings.py` with Cloudinary configuration
3. Push to GitHub and deploy
4. Set environment variables
5. Test user uploads!

---

## 📚 Additional Resources

- Render Docs: https://render.com/docs
- Cloudinary Docs: https://cloudinary.com/documentation/django_integration
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

