# PythonAnywhere Deployment Checklist

## Pre-Deployment Setup
- [ ] Create PythonAnywhere account
- [ ] Choose appropriate plan (Hacker recommended)
- [ ] Create new web app (Manual configuration, Python 3.12)

## Code Upload
- [ ] Upload project files via Files tab OR clone via Git
- [ ] Install dependencies: `pip3.12 install --user -r requirements_pythonanywhere.txt`

## Database Setup
- [ ] Create MySQL database in Databases tab
- [ ] Set database password
- [ ] Update settings.py with correct database credentials
- [ ] Run migrations: `python3.12 manage.py migrate`
- [ ] Create superuser: `python3.12 manage.py createsuperuser`

## Static Files Configuration
- [ ] Update STATIC_ROOT in settings.py for PythonAnywhere
- [ ] Run collectstatic: `python3.12 manage.py collectstatic --noinput`
- [ ] Configure static files mapping in Web tab (/static/ -> /home/username/crafty/staticfiles)
- [ ] Configure media files mapping in Web tab (/media/ -> /home/username/crafty/media)

## Web App Configuration
- [ ] Set source code path: `/home/username/crafty`
- [ ] Set working directory: `/home/username/crafty`
- [ ] Set WSGI file: `/home/username/crafty/crafty/wsgi.py`
- [ ] Edit WSGI file with correct path configuration
- [ ] Set environment variables (MYSQL_PASSWORD, SECRET_KEY, DEBUG=False)

## Final Steps
- [ ] Reload web app
- [ ] Test your website
- [ ] Check static files are loading correctly
- [ ] Test database functionality
- [ ] Test admin panel

## Troubleshooting
- [ ] Check error logs in Web tab
- [ ] Verify all file paths are correct
- [ ] Ensure database credentials are correct
- [ ] Check static files are collected properly
- [ ] Verify WSGI configuration

## Important Notes
- Replace 'abdouml20' with your actual PythonAnywhere username
- Free accounts have limited CPU seconds per day
- Free accounts can't use custom domains
- Consider upgrading to Hacker plan for production use
