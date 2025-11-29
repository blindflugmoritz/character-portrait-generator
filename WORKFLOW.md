# Development Workflow Cheat Sheet

## The Process (3 Stages)

```
Local Development → GitHub → Production Server
(your computer)      (backup)   (live site)
```

---

## Step-by-Step: Adding a New Feature

### 1. Start Feature
```
Tell Claude: "Create feature branch for [feature name]"
```

### 2. Develop Locally
```bash
cd frontend
npm run dev
# Make your changes, test at http://localhost:5173
```

### 3. Save Work
```
Tell Claude: "Commit changes: [what you did]"
```

### 4. Merge to Testing
```
Tell Claude: "Merge to develop"
```

### 5. Test Again
```bash
# Switch to develop branch
npm run dev
# Test everything works together
```

### 6. Release Version
```
Tell Claude: "Release version v[X.Y.Z]"
```

### 7. Deploy to Server
```
Tell Claude: "Deploy to PythonAnywhere"
```

---

## Version Numbers

- **v1.0.1** - Bug fix (patch)
- **v1.1.0** - New feature (minor)
- **v2.0.0** - Major rewrite (major)

---

## Branches

- **main** - Production (live site)
- **develop** - Testing area
- **feature/xyz** - Your work in progress

---

## Common Commands

| What You Want | Tell Claude |
|--------------|-------------|
| Start feature | "Create feature branch for [name]" |
| Save work | "Commit changes: [description]" |
| Test feature | "Merge to develop" |
| Release | "Release version v[X.Y.Z]" |
| Deploy | "Deploy to PythonAnywhere" |
| See history | "Show changelog" |
| Undo changes | "Revert to v[X.Y.Z]" |

---

## Quick Reference for Claude

**Setup (one time):**
1. Initialize git repo
2. Create GitHub repo
3. Connect local to GitHub
4. Initial commit to main

**Regular workflow:**
1. Create feature branch from develop
2. User develops locally
3. Commit & push feature branch
4. Merge feature → develop
5. Test on develop
6. Merge develop → main with version tag
7. Build & deploy to PythonAnywhere

**Commands:**
- Build: `npm run build:prod` (in frontend/)
- Deploy frontend: rsync to `/home/blindflugstudios/build/`
- Deploy backend: rsync to `/home/blindflugstudios/crew-generator-backend/`
- Reload: `mcp__pythonanywhere__reload_webapp`
