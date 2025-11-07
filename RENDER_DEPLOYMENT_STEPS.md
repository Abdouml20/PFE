# 🚀 Step-by-Step: Deploy to Render

## ⚠️ Why Cloudinary is Required

**Important:** Render (and most free hosting platforms) **do NOT persist files** on the server filesystem. This means:
- ❌ Any images/videos uploaded by users will be **DELETED** when the app redeploys
- ❌ Files stored in `media/` folder get wiped on every deployment
- ❌ Your project has user uploads (product images, profile pics, videos, community posts)

**Solution:** Use **Cloudinary** (free cloud storage) to store all user-uploaded media files:
- ✅ Files persist permanently
- ✅ 25GB free storage
- ✅ Automatic image optimization
- ✅ CDN for fast delivery
- ✅ Works with your existing code (no code changes needed)

**Alternative:** You can skip Cloudinary if you don't need user uploads, but your project clearly uses images/videos.

---

## Prerequisites Checklist
- [ ] GitHub account
- [ ] Code pushed to GitHub repository
- [ ] Cloudinary account (free) - https://cloudinary.com/users/register_free

---

## Step 1: Prepare Your Code

### 1.1 Update requirements.txt
Add Cloudinary packages for media file storage:
```txt
django-cloudinary-storage==0.3.0
cloudinary==1.36.0
```

### 1.2 Update settings.py
Add Cloudinary configuration. See Step 2 below for exact code.

### 1.3 Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## Step 2: Configure Cloudinary in settings.py

### 2.1 Add to INSTALLED_APPS
Find `INSTALLED_APPS` in `crafty/settings.py` and add:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps ...
    'cloudinary',           # Add this
    'cloudinary_storage',   # Add this
]
```

### 2.2 Add Cloudinary Configuration
Find this line in settings.py:
```python
MEDIA_ROOT = BASE_DIR / 'media'
```

Add this code **right after** it:
```python
# Cloudinary configuration for production (media files)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# Use Cloudinary for media storage in production
if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### 2.3 Update ALLOWED_HOSTS
In `render.yaml`, your app name is `crafty-django`, so your URL will be:
`crafty-django.onrender.com`

Make sure `ALLOWED_HOSTS` in settings.py can handle this:
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
```

The `render.yaml` already sets this, but verify it works.

---

## Step 3: Get Cloudinary Credentials

1. Go to https://cloudinary.com/users/register_free
2. Sign up (free tier: 25GB storage, 25GB bandwidth/month)
3. After login, go to **Dashboard**
4. Copy these 3 values (you'll need them in Step 5):
   - **Cloud name** (e.g., `dxyz1234`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz`)

---

## Step 4: Deploy on Render

### 4.1 Create Blueprint Instance
1. In Render dashboard, you're on the **Blueprints** page
2. Click **"+ New Blueprint Instance"** button
3. Connect your GitHub account (if not already connected)
4. Select your repository containing the `render.yaml` file
5. Click **"Apply"**

### 4.2 Render Will Auto-Detect Configuration
- Render will read your `render.yaml` file
- It will automatically:
  - Create the PostgreSQL database (`crafty-db`)
  - Create the web service (`crafty-django`)
  - Set up environment variables from `render.yaml`

### 4.3 Wait for Initial Deployment
- First deployment takes 5-10 minutes
- You can watch the build logs in real-time
- The database will be created automatically

---

## Step 5: Add Cloudinary Environment Variables

After the initial deployment:

1. Go to your **Web Service** (not the Blueprint)
   - Click on **"crafty-django"** in the dashboard
   
2. Go to **Environment** tab

3. Add these 3 environment variables:
   ```
   CLOUDINARY_CLOUD_NAME = <your-cloud-name>
   CLOUDINARY_API_KEY = <your-api-key>
   CLOUDINARY_API_SECRET = <your-api-secret>
   ```
   (Use the values from Step 3)

4. Click **"Save Changes"**

5. Render will automatically redeploy with the new variables

---

## Step 6: Run Database Migrations

After deployment completes:

1. Go to your **Web Service** → **Shell** tab
2. Run these commands:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Follow prompts to create admin user

---

## Step 7: Verify Deployment

1. **Check your app URL:**
   - Go to your Web Service dashboard
   - Your URL will be: `https://crafty-django.onrender.com`
   - Click the URL to open your site

2. **Test functionality:**
   - Visit admin panel: `https://crafty-django.onrender.com/admin`
   - Test user registration
   - Test image upload (should go to Cloudinary)
   - Check that static files load correctly

---

## Step 8: (Optional) Update render.yaml

If you want to add Cloudinary env vars directly in `render.yaml`:

```yaml
services:
  - type: web
    name: crafty-django
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput --clear
    startCommand: gunicorn crafty.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: DEBUG
        value: False
      - key: SECRET_KEY
        generateValue: true
      - key: ALLOWED_HOSTS
        value: crafty-django.onrender.com
      - key: DATABASE_URL
        fromDatabase:
          name: crafty-db
          property: connectionString
      # Add these (but keep secrets secure - better to add in dashboard)
      - key: CLOUDINARY_CLOUD_NAME
        sync: false  # You'll set this manually
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false

databases:
  - name: crafty-db
    databaseName: crafty
    user: crafty_user
```

**Note:** It's safer to add secrets in the dashboard rather than in the YAML file.

---

## ✅ Deployment Complete!

Your Django app is now live with:
- ✅ PostgreSQL database (auto-created)
- ✅ Cloud storage for images/videos (Cloudinary)
- ✅ User accounts working
- ✅ File uploads working
- ✅ Static files served via WhiteNoise

---

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify all packages in `requirements.txt` are correct
- Make sure Python version is compatible (Django 5.2.7 needs Python 3.10+)

### Database Connection Errors
- Verify `DATABASE_URL` is set (should be automatic from `render.yaml`)
- Check database is running in Render dashboard
- Run migrations: `python manage.py migrate`

### Media Files Not Uploading
- Verify Cloudinary env vars are set correctly
- Check `DEFAULT_FILE_STORAGE` is set in settings.py
- Check Cloudinary dashboard for uploaded files

### Static Files Not Loading
- Render runs `collectstatic` automatically
- Verify WhiteNoise is in `MIDDLEWARE`
- Check build logs for collectstatic errors

### App Spins Down
- Free tier spins down after 15 min inactivity
- First request after spin-down may take 30-60 seconds
- Upgrade to $7/month for always-on

---

## 📊 Free Tier Limits

**Render Free Tier:**
- 750 hours/month (enough for ~31 days of always-on)
- Spins down after 15 min inactivity
- 512MB RAM
- PostgreSQL database included

**Cloudinary Free Tier:**
- 25GB storage
- 25GB bandwidth/month
- 10MB max file size per upload
- Image optimization included
- CDN included

---

## 🎯 Next Steps

1. **Set up custom domain** (optional):
   - Go to Web Service → Settings → Custom Domains
   - Add your domain
   - Update DNS records

2. **Enable automatic backups**:
   - Go to Database → Backups
   - Enable automatic daily backups

3. **Monitor usage**:
   - Check Render dashboard for resource usage
   - Check Cloudinary dashboard for storage/bandwidth

4. **Set up email** (for user verification):
   - Configure SMTP settings in settings.py
   - Or use SendGrid/Mailgun free tier

---

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- Cloudinary Docs: https://cloudinary.com/documentation/django_integration
- Render Support: Available in dashboard

