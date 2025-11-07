"""
Production settings for Render + Cloudinary deployment
Add this configuration to your settings.py or import it
"""

import os

# Cloudinary configuration for media files (images, videos)
# Sign up at https://cloudinary.com to get free credentials
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# Media files configuration for Cloudinary
# This replaces local file storage with cloud storage
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Optional: Configure image transformations
CLOUDINARY = {
    'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'api_key': os.environ.get('CLOUDINARY_API_KEY', ''),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET', ''),
    'secure': True,  # Use HTTPS
}

# File upload size limits (Cloudinary free tier: 10MB per file)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

