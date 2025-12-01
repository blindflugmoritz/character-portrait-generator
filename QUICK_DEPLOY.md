# Quick Deployment Guide

## ⚡ Fast Deploy (With Tests)

```bash
cd backend
source venv/bin/activate
python3 deploy.py
```

That's it! The script will:
1. ✅ Run pre-deployment tests
2. 📤 Upload files
3. 🔄 Reload webapp
4. ✅ Run post-deployment tests

---

## 🧪 Manual Testing

### Before Deploy (Local)
```bash
cd backend
source venv/bin/activate
python3 tests/test_pre_deploy.py
```

**Checks:**
- All required files exist
- JSON files are valid
- All modules can import
- Function signatures are correct

### After Deploy (Production)
```bash
cd backend
source venv/bin/activate
python3 tests/test_production.py
```

**Checks:**
- Health endpoint returns healthy
- Postcard generation works
- Portraits are visible (not blank)

---

## 🩺 Health Check

**Quick check:**
```bash
curl https://blindflugstudios.pythonanywhere.com/api/health | python3 -m json.tool
```

**What it checks:**
- ✅ All 7 Python files exist
- ✅ Dependencies can be imported
- ✅ Static directories exist
- ✅ Environment variables set

**Status:**
- `"status": "healthy"` = ✅ Everything OK
- `"status": "unhealthy"` = ❌ Check `"issues"` array

---

## 🐛 Common Issues

### "Missing file: X"
**Fix:** Upload the missing file
```bash
sshpass -p 'HFY.ecy5mem1gcd-nhx' scp FILE blindflugstudios@ssh.pythonanywhere.com:/home/blindflugstudios/CharacterEditor/api/
```

### "Portraits not visible"
**Check:**
```bash
python3 tests/test_production.py
```
Look for "Portrait area colors" - should be > 100

### "Tests fail locally"
**Fix:**
```bash
pip install -r requirements.txt
```

---

## 📋 What Would Have Caught Today's Bug?

**Missing photo_matcher.py would have been caught by:**

1. ✅ `test_pre_deploy.py` - "Missing file: photo_matcher.py"
2. ✅ `/api/health` endpoint - Shows missing file immediately
3. ✅ `test_production.py` - Health check fails

**Instead of:** Hours of debugging 500 errors! 😤

---

## 🎯 Best Practice Workflow

```
1. Make code changes locally
2. Test locally: python3 tests/test_pre_deploy.py
3. Deploy: python3 deploy.py (handles everything)
4. Done! ✅
```

**Time saved per deployment:** 15-30 minutes
**Frustration saved:** Priceless 😊
