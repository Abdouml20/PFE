"""
Quick setup script to add Cloudinary configuration to settings.py
Run this to automatically update your settings.py with Cloudinary support
"""

import os
import re
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / 'crafty' / 'settings.py'

def add_cloudinary_to_settings():
    """Add Cloudinary configuration to settings.py"""
    
    if not SETTINGS_FILE.exists():
        print(f"Error: {SETTINGS_FILE} not found!")
        return False
    
    with open(SETTINGS_FILE, 'r') as f:
        content = f.read()
    
    # Check if Cloudinary is already configured
    if 'cloudinary_storage' in content:
        print("Cloudinary is already configured in settings.py")
        return True
    
    # Add cloudinary to INSTALLED_APPS
    installed_apps_pattern = r"(INSTALLED_APPS\s*=\s*\[)"
    installed_apps_match = re.search(installed_apps_pattern, content)
    
    if installed_apps_match:
        # Find the end of INSTALLED_APPS list
        start_pos = installed_apps_match.end()
        # Look for the closing bracket
        bracket_count = 1
        pos = start_pos
        while pos < len(content) and bracket_count > 0:
            if content[pos] == '[':
                bracket_count += 1
            elif content[pos] == ']':
                bracket_count -= 1
            pos += 1
        
        # Insert cloudinary apps before the closing bracket
        insert_pos = pos - 1
        cloudinary_apps = "\n    'cloudinary',\n    'cloudinary_storage',"
        content = content[:insert_pos] + cloudinary_apps + content[insert_pos:]
    
    # Add Cloudinary configuration after MEDIA_ROOT
    media_root_pattern = r"(MEDIA_ROOT\s*=\s*BASE_DIR\s*/\s*'media')"
    media_config = """
# Cloudinary configuration for production (media files)
# Set these environment variables: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# Use Cloudinary for media storage in production
if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
"""
    
    if re.search(media_root_pattern, content):
        content = re.sub(
            media_root_pattern,
            r"\1" + media_config,
            content
        )
    
    # Write back to file
    with open(SETTINGS_FILE, 'w') as f:
        f.write(content)
    
    print("✅ Cloudinary configuration added to settings.py")
    print("\nNext steps:")
    print("1. Add to requirements.txt: django-cloudinary-storage cloudinary")
    print("2. Set environment variables:")
    print("   - CLOUDINARY_CLOUD_NAME")
    print("   - CLOUDINARY_API_KEY")
    print("   - CLOUDINARY_API_SECRET")
    print("3. Sign up at https://cloudinary.com to get free credentials")
    
    return True

if __name__ == '__main__':
    add_cloudinary_to_settings()

