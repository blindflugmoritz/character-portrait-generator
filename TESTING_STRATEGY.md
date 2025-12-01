# Testing Strategy to Prevent Deployment Bugs

## Problem Analysis

**What went wrong:**
1. Missing files on production (photo_matcher.py, sprite-metadata.json)
2. Wrong WSGI configuration pointing to old directory
3. Function signature mismatch between modules
4. No automated verification before/after deployment
5. Debugging was painful - no logs, no diagnostics

## 3-Layer Testing Strategy

### Layer 1: Pre-Deployment Tests (Local)
**Goal**: Catch bugs BEFORE uploading to server

#### 1.1 File Manifest Check
- Verify all required files exist locally
- Check file sizes (detect empty/corrupted files)
- Verify JSON files are valid JSON

#### 1.2 Import Tests
- Try importing all modules
- Catch syntax errors, missing dependencies

#### 1.3 Function Contract Tests
- Verify function signatures match between modules
- Check that postcard_generator.generate_postcard() is called correctly

#### 1.4 Integration Test
- Generate a test postcard locally
- Verify portrait renders correctly
- Compare with expected output

**Implementation**: `backend/tests/test_pre_deploy.py`

---

### Layer 2: Deployment Validation
**Goal**: Ensure files are uploaded correctly

#### 2.1 Upload Verification
- After rsync, verify files exist on server
- Check file sizes match local files
- Verify permissions are correct

#### 2.2 WSGI Configuration Check
- Verify WSGI file points to correct directory
- Check Python path is correct

**Implementation**: Enhanced `deploy_check.sh` with pre-upload checks

---

### Layer 3: Post-Deployment Tests (Production)
**Goal**: Verify production is working correctly

#### 3.1 Health Check
- `/api/health` endpoint (already implemented)
- Returns 200 if all systems operational

#### 3.2 Smoke Tests
- Test each API endpoint with real request
- Generate crew, analyze photo, generate postcard
- Verify responses are valid

#### 3.3 Visual Regression Test
- Generate test postcard
- Verify portrait is visible (not empty boxes)
- Compare with reference image

**Implementation**: `backend/tests/test_production.py`

---

## Testing Workflow

### Manual Deployment (Current)
```
1. Make code changes
2. Test locally (optional)
3. Upload files
4. Reload webapp
5. Hope it works
6. Debug when it breaks ❌
```

### New Workflow (Automated)
```
1. Make code changes
2. Run pre-deploy tests ✅
   - If fail: Fix locally, repeat
3. Run deployment script ✅
   - Uploads files
   - Verifies upload
   - Reloads webapp
4. Run post-deploy tests ✅
   - Health check
   - Smoke tests
   - Visual regression
5. Get clear PASS/FAIL report ✅
```

---

## Implementation Priority

### Phase 1: Quick Wins (1 hour) 🟢
- [x] Health check endpoint
- [ ] Pre-deploy file manifest check
- [ ] Enhanced deploy_check.sh
- [ ] Simple smoke tests

### Phase 2: Automated Testing (2-3 hours) 🟡
- [ ] Unit tests for critical functions
- [ ] Integration tests
- [ ] Automated deployment script
- [ ] Visual regression tests

### Phase 3: CI/CD Pipeline (4+ hours) 🔴
- [ ] GitHub Actions workflow
- [ ] Automatic deployment on push
- [ ] Slack/email notifications
- [ ] Rollback on failure

---

## Test Files Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_pre_deploy.py      # Run before upload
│   ├── test_production.py      # Run after upload
│   ├── test_postcard.py        # Integration tests
│   └── fixtures/
│       ├── test_character.json
│       └── expected_postcard.png
├── deploy.py                    # Automated deployment script
└── deploy_check.sh             # Quick manual check
```

---

## Specific Tests Needed

### Test 1: File Manifest
```python
def test_all_files_exist():
    required_files = [
        'api/views.py',
        'api/views_postcard.py',
        'api/postcard_generator.py',
        'api/character_generator.py',
        'api/photo_matcher.py',
        'api/sprite-metadata.json',
        'api/urls.py'
    ]
    for filepath in required_files:
        assert os.path.exists(filepath), f"Missing: {filepath}"
```

### Test 2: Function Signatures
```python
def test_postcard_generator_signature():
    import inspect
    from api.postcard_generator import generate_postcard

    sig = inspect.signature(generate_postcard)
    params = list(sig.parameters.keys())

    # Verify correct order
    assert params[0] == 'color', "First param should be 'color'"
    assert params[1] == 'characters', "Second param should be 'characters'"
    assert params[2] == 'base_path', "Third param should be 'base_path'"
```

### Test 3: Postcard Generation
```python
def test_generate_postcard_integration():
    character = load_fixture('test_character.json')

    postcard = generate_postcard('blue', [character], BASE_PATH)

    # Verify image size
    assert postcard.size == (1024, 614)

    # Verify portrait area is not blank (has pixels with color)
    portrait_area = postcard.crop((50, 50, 250, 250))
    colors = portrait_area.getcolors()
    assert len(colors) > 10, "Portrait should have multiple colors"
```

### Test 4: Production Health
```python
def test_production_health():
    response = requests.get('https://blindflugstudios.pythonanywhere.com/api/health')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert len(data['issues']) == 0
```

### Test 5: Production Postcard
```python
def test_production_postcard_generation():
    character = load_fixture('test_character.json')

    response = requests.post(
        'https://blindflugstudios.pythonanywhere.com/api/generate-postcard',
        json={'color': 'blue', 'characters': [character]}
    )

    assert response.status_code == 200
    assert len(response.content) > 1_000_000  # ~1MB

    # Verify it's a valid PNG
    img = Image.open(BytesIO(response.content))
    assert img.format == 'PNG'
    assert img.size == (1024, 614)
```

---

## Key Benefits

1. **Catch bugs locally** before they reach production
2. **Automated verification** - no manual testing needed
3. **Clear error messages** - know exactly what's wrong
4. **Fast debugging** - tests pinpoint the issue
5. **Confidence** - deploy without fear
6. **Documentation** - tests show how things should work

---

## Next Steps

1. Implement Phase 1 tests (quick wins)
2. Create automated deployment script
3. Add to git pre-commit hook
4. Document testing workflow
5. Train team on new process
