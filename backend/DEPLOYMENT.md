# PythonAnywhere Deployment Guide

## Prerequisites
1. PythonAnywhere account (free or paid)
2. PythonAnywhere API token (from Account page)
3. ANTHROPIC_API_KEY environment variable

## Option 1: Manual Deployment (Recommended for First Time)

### Step 1: Create PythonAnywhere Web App
1. Log into https://www.pythonanywhere.com
2. Go to "Web" tab
3. Click "Add a new web app"
4. Choose "Manual configuration"
5. Select Python 3.10 or higher

### Step 2: Upload Code
1. Go to "Files" tab
2. Create directory: `/home/YOUR_USERNAME/crew-generator-backend/`
3. Upload all files from `backend/` directory:
   - `manage.py`
   - `requirements.txt`
   - `api/` folder (all contents)
   - `crew_generator_backend/` folder (all contents)
   - `.env.example`

### Step 3: Set Up Virtual Environment
Open a Bash console from "Consoles" tab:

```bash
cd ~/crew-generator-backend
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cd ~/crew-generator-backend
cp .env.example .env
nano .env
```

Add your ANTHROPIC_API_KEY:
```
ANTHROPIC_API_KEY=your_actual_key_here
```

Save with Ctrl+X, Y, Enter.

### Step 5: Configure WSGI File
Go to "Web" tab, click on WSGI configuration file link. Replace contents with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/YOUR_USERNAME/crew-generator-backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'crew_generator_backend.settings'

# Load .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/crew-generator-backend/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `YOUR_USERNAME` with your actual PythonAnywhere username.

### Step 6: Configure Django Settings
Edit `crew_generator_backend/settings.py`:

```bash
cd ~/crew-generator-backend
nano crew_generator_backend/settings.py
```

Update these settings:
```python
# Add your PythonAnywhere domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com', 'localhost']

# Update CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'https://YOUR_FRONTEND_DOMAIN.com',  # Add your frontend domain
]

# Set DEBUG=False for production (after testing)
DEBUG = True  # Keep True initially for debugging
```

### Step 7: Run Migrations
```bash
cd ~/crew-generator-backend
source venv/bin/activate
python manage.py migrate
```

### Step 8: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 9: Configure Static Files in Web Tab
In PythonAnywhere "Web" tab:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/crew-generator-backend/static/`

### Step 10: Reload Web App
Click the big green "Reload" button in the Web tab.

### Step 11: Test Deployment
Visit: `https://YOUR_USERNAME.pythonanywhere.com/api/`

You should see Django REST framework page or a simple response.

Test photo analysis endpoint:
```bash
curl -X POST https://YOUR_USERNAME.pythonanywhere.com/api/analyze-photo \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_data_here", "mimeType": "image/jpeg"}'
```

### Step 12: Update Frontend
Edit `frontend/src/lib/PhotoUpload.svelte`:

Change:
```javascript
const response = await fetch('http://localhost:8000/api/analyze-photo', {
```

To:
```javascript
const response = await fetch('https://YOUR_USERNAME.pythonanywhere.com/api/analyze-photo', {
```

## Option 2: Using Claude MCP (Automated)

### Requirements
- Claude Code with MCP support
- PythonAnywhere API token

### Setup MCP Server
```bash
claude mcp add pythonanywhere
```

When prompted, provide:
- **Username**: Your PythonAnywhere username
- **API Token**: From https://www.pythonanywhere.com/account/#api_token

### Deploy with MCP
After MCP is configured, you can use Claude Code to automate deployment tasks.

## Troubleshooting

### Issue: Import Errors
**Solution**: Check that virtual environment is activated in WSGI file and all dependencies are installed.

### Issue: 500 Internal Server Error
**Solution**:
1. Check error log in "Web" tab → "Error log"
2. Enable DEBUG=True temporarily to see detailed errors
3. Verify ANTHROPIC_API_KEY is set correctly

### Issue: CORS Errors from Frontend
**Solution**: Add your frontend domain to CORS_ALLOWED_ORIGINS in settings.py

### Issue: Static Files Not Loading
**Solution**: Run `python manage.py collectstatic` and configure static files path in Web tab

## Environment Variables Required
- `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude Vision

## Cost Considerations
- Free PythonAnywhere tier limitations:
  - Limited CPU time per day
  - Only HTTPS requests to whitelist domains
  - Add anthropic.com to whitelist if needed
- Paid tier recommended for production use

## Security Checklist
- [ ] Set DEBUG=False in production
- [ ] Use environment variables for sensitive data
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Enable HTTPS only (PythonAnywhere default)
- [ ] Keep API keys secure in .env file
- [ ] Add .env to .gitignore
- [ ] Review CORS settings
- [ ] Set up proper authentication if needed

## Monitoring
Check logs regularly:
- Error log: Shows Python errors and Django issues
- Server log: Shows requests and responses
- Access log: Shows all HTTP requests

Location: PythonAnywhere Web tab → Log files section
