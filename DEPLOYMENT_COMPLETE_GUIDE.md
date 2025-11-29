# Complete Deployment Guide - Backend + Frontend

## ✅ What's Done

### Backend (/home/blindflugstudios/crew-generator-backend/)
- ✓ All Python files uploaded
- ✓ requirements.txt with dependencies
- ✓ .env with ANTHROPIC_API_KEY configured
- ✓ sprite-metadata.json uploaded
- ✓ setup.sh script ready

### Frontend (built locally in /frontend/build/)
- ✓ Built as static files with @sveltejs/adapter-static
- ✓ Configured to call production API: https://blindflugstudios.pythonanywhere.com
- ✓ All assets included (PortraitSprites, CSS, JS)

## 🚀 Deployment Steps (15 minutes)

### STEP 1: Upload Frontend Build (via Web UI)

Since the build has ~1000+ files, use PythonAnywhere's Files tab with zip upload:

1. **Create zip of build:**
   ```bash
   cd /Users/momo/Downloads/charactergenerator-prototype\ copy/frontend
   zip -r build.zip build/
   ```

2. **Upload via Files tab:**
   - Go to https://www.pythonanywhere.com/files/
   - Navigate to `/home/blindflugstudios/`
   - Click "Upload a file" and select `build.zip`
   - Open Bash console and run:
     ```bash
     cd /home/blindflugstudios
     unzip build.zip
     rm build.zip
     ```

### STEP 2: Run Backend Setup

Open Bash console at https://www.pythonanywhere.com/consoles/:

```bash
cd /home/blindflugstudios/crew-generator-backend
bash setup.sh
```

This will:
- Create Python 3.10 virtual environment
- Install all dependencies (Django, Anthropic, CORS, etc.)
- Run database migrations
- Collect static files

### STEP 3: Create Web App

Go to https://www.pythonanywhere.com/#/webapps/:

1. Click **"Add a new web app"**
2. Choose **"Manual configuration"**
3. Select **"Python 3.10"**
4. Domain: `blindflugstudios.pythonanywhere.com`

### STEP 4: Configure WSGI

Click on the **WSGI configuration file** link and replace ALL contents with:

```python
import os
import sys

# Backend path
backend_path = '/home/blindflugstudios/crew-generator-backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'crew_generator_backend.settings'

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_path, '.env'))

# Get Django WSGI app
from django.core.wsgi import get_wsgi_application
django_app = get_wsgi_application()

# Serve frontend static files for root/non-API paths
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings
from django.views.static import serve
import os

frontend_path = '/home/blindflugstudios/build'

def application(environ, start_response):
    path = environ.get('PATH_INFO', '')

    # API requests go to Django
    if path.startswith('/api/') or path.startswith('/admin/'):
        return django_app(environ, start_response)

    # Frontend static files
    if path == '/':
        path = '/index.html'

    file_path = os.path.join(frontend_path, path.lstrip('/'))

    # Serve file if it exists
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()

        # Determine content type
        if path.endswith('.html'):
            content_type = 'text/html'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.json'):
            content_type = 'application/json'
        elif path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif path.endswith('.svg'):
            content_type = 'image/svg+xml'
        else:
            content_type = 'application/octet-stream'

        start_response('200 OK', [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content)))
        ])
        return [content]

    # Fallback to index.html for SPA routes
    index_path = os.path.join(frontend_path, 'index.html')
    if os.path.isfile(index_path):
        with open(index_path, 'rb') as f:
            content = f.read()
        start_response('200 OK', [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(content)))
        ])
        return [content]

    # 404
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return [b'Not Found']
```

### STEP 5: Set Virtual Environment

In the Web tab, under **"Virtualenv"** section:

```
/home/blindflugstudios/crew-generator-backend/venv
```

### STEP 6: Update Django Settings

Edit `/home/blindflugstudios/crew-generator-backend/crew_generator_backend/settings.py`:

Change these lines:

```python
ALLOWED_HOSTS = ['blindflugstudios.pythonanywhere.com', 'localhost', '127.0.0.1']

# Add at the end of file:
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Update CORS to allow your frontend domain
CORS_ALLOWED_ORIGINS = [
    'https://blindflugstudios.pythonanywhere.com',
    'http://localhost:5173',
]
```

Add `import os` at the top if not present.

### STEP 7: Reload Web App

Click the big green **"Reload blindflugstudios.pythonanywhere.com"** button.

## 🎉 Testing

### Frontend (Full App)
```
https://blindflugstudios.pythonanywhere.com/
```

### Backend API Endpoints
```
https://blindflugstudios.pythonanywhere.com/api/generate-crew
https://blindflugstudios.pythonanywhere.com/api/analyze-photo
```

### Test Photo Upload
1. Go to https://blindflugstudios.pythonanywhere.com/
2. Upload a photo in the "Generate from Photo" section
3. Character should be generated and displayed

### Test Crew Generator
1. Enter a description like "Tuskegee Airmen squadron"
2. Click "Generate Crew"
3. Crew members should appear with portraits

## 📊 Architecture

```
blindflugstudios.pythonanywhere.com/
│
├── /                          → Frontend (SvelteKit static build)
├── /_app/*                    → Frontend assets (JS, CSS)
├── /PortraitSprites/*         → Character sprites
│
├── /api/generate-crew         → Django REST endpoint
├── /api/analyze-photo         → Django REST endpoint (with Claude Vision)
└── /admin/                    → Django admin (optional)
```

## 🔒 Security Checklist

- ✓ ANTHROPIC_API_KEY in .env (not committed to git)
- ✓ Django SECRET_KEY secured
- ✓ CORS configured for production domain
- ✓ ALLOWED_HOSTS restricted
- ⚠ For production: Set DEBUG=False in settings.py

## 🐛 Troubleshooting

### 500 Internal Server Error
- Check error log: Web tab → "Error log" link
- Verify virtual environment path is correct
- Check WSGI file has no syntax errors

### API CORS Errors
- Verify CORS_ALLOWED_ORIGINS includes your domain
- Check django-cors-headers is installed

### Frontend Not Loading
- Verify /home/blindflugstudios/build/ directory exists
- Check WSGI file frontend_path is correct
- Try accessing https://blindflugstudios.pythonanywhere.com/index.html directly

### Photo Upload Not Working
- Check ANTHROPIC_API_KEY is set in .env
- Verify backend logs for API errors
- Test API directly: curl -X POST https://blindflugstudios.pythonanywhere.com/api/analyze-photo

## 💰 Cost Estimate

- PythonAnywhere Free Tier: $0/month (limited CPU, one web app)
- Anthropic API: ~$0.015 per photo analysis
- Recommended: Paid PythonAnywhere tier ($5/month) for production

## 📝 Next Steps

1. Test all features thoroughly
2. Set DEBUG=False for production
3. Monitor API usage on Anthropic console
4. Set up custom domain (optional, requires paid tier)
5. Add analytics/monitoring (optional)

---

## Quick Command Reference

**Bash console shortcuts:**
```bash
# Navigate to backend
cd /home/blindflugstudios/crew-generator-backend

# Activate venv
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (for /admin)
python manage.py createsuperuser

# Check logs
tail -f /var/log/blindflugstudios.pythonanywhere.com.error.log
```

**Reload after changes:**
- Go to Web tab
- Click green "Reload" button
- OR: Use API: `curl -X POST https://www.pythonanywhere.com/api/v0/user/blindflugstudios/webapps/blindflugstudios.pythonanywhere.com/reload/ -H "Authorization: Token YOUR_API_TOKEN"`

## Support

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Docs: https://docs.djangoproject.com/
- Anthropic API: https://docs.anthropic.com/
