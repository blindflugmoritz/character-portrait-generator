# Deployment Guide

## Quick Deploy Checklist

### 1. Upload Backend Files
```bash
cd "/Users/momo/Downloads/charactergenerator-prototype copy/backend"

# Upload all Python files at once
sshpass -p 'HFY.ecy5mem1gcd-nhx' rsync -avz --progress \
  --include='*.py' \
  --include='*.json' \
  --include='*/' \
  --exclude='*' \
  api/ \
  blindflugstudios@ssh.pythonanywhere.com:/home/blindflugstudios/CharacterEditor/api/
```

### 2. Reload Webapp
Use MCP tool: `mcp__pythonanywhere__reload_webapp` with domain `blindflugstudios.pythonanywhere.com`

### 3. Run Health Check
```bash
./deploy_check.sh
```

Or manually check: https://blindflugstudios.pythonanywhere.com/api/health

## Health Check Endpoint

**URL**: `/api/health`

**What it checks**:
- ✅ All required Python files exist
- ✅ All Python dependencies can be imported (anthropic, PIL, etc.)
- ✅ Environment variables are set (ANTHROPIC_API_KEY)
- ✅ Static file directories exist
- ✅ Module versions

**Response** (when healthy):
```json
{
  "status": "healthy",
  "issues": [],
  "checks": {
    "files": {...},
    "imports": {...},
    "environment": {...},
    "static_files": {...}
  }
}
```

**Response** (when unhealthy):
```json
{
  "status": "unhealthy",
  "issues": ["Missing file: photo_matcher.py", ...],
  "checks": {...}
}
```

## Common Issues & Fixes

### Issue: Missing Python modules
**Symptoms**: 500 errors, Django won't start
**Fix**: Check `/api/health` endpoint to see which files are missing
```bash
curl https://blindflugstudios.pythonanywhere.com/api/health | python3 -m json.tool
```

### Issue: Portraits not rendering
**Symptoms**: Postcard shows empty boxes
**Check**:
1. `/api/health` - verify all files present
2. Download test postcard: `curl -X POST https://blindflugstudios.pythonanywhere.com/api/generate-postcard -d '...' > test.png`
3. Check sprite files exist on server

### Issue: Wrong WSGI directory
**Symptoms**: Old code running, changes not taking effect
**Fix**: Check `/var/www/blindflugstudios_pythonanywhere_com_wsgi.py` has correct path:
```python
backend_path = '/home/blindflugstudios/CharacterEditor'  # NOT crew-generator-backend
```

## Required Files Checklist

Backend (`/home/blindflugstudios/CharacterEditor/api/`):
- [ ] `views.py`
- [ ] `views_postcard.py`
- [ ] `postcard_generator.py`
- [ ] `character_generator.py`
- [ ] `photo_matcher.py`
- [ ] `sprite-metadata.json`
- [ ] `urls.py`

Frontend (`/home/blindflugstudios/build/`):
- [ ] `index.html`
- [ ] `_app/` directory
- [ ] `PortraitSprites/` directory (21 subdirectories)
- [ ] `PostcardTemplates/` (blue.png, orange.png)
