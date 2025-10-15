# PythonAnywhere Database Configuration
# Add this to your settings.py or create a separate settings file

import os

# PythonAnywhere Database Configuration
if 'pythonanywhere.com' in os.environ.get('HTTP_HOST', ''):
    # Production database (MySQL on PythonAnywhere)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'yourusername$crafty_db',  # Replace 'yourusername' with your PA username
            'USER': 'yourusername',  # Replace with your PA username
            'PASSWORD': 'your_mysql_password',  # Set this in PA database tab
            'HOST': 'yourusername.mysql.pythonanywhere-services.com',  # Replace with your PA username
            'PORT': '3306',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
