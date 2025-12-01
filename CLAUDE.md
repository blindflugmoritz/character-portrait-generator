# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL DEPLOYMENT RULES ⚠️

**NEVER DEPLOY TO PYTHONANYWHERE WITHOUT EXPLICIT USER PERMISSION**

- DO NOT upload files to the server using rsync, scp, or MCP tools
- DO NOT install packages on the server
- DO NOT reload the webapp
- DO NOT make ANY changes to the production environment
- Development happens LOCALLY only
- Only deploy when the user explicitly says "deploy to production" or "upload to server"

If the user asks to implement a server-side feature:
1. Create the code locally in the `/backend` directory
2. Test it locally
3. Ask the user if they want to deploy it
4. Wait for explicit confirmation before any server operations

## 🧪 MANDATORY PRE-DEPLOYMENT TESTING

**BEFORE EVERY DEPLOYMENT, YOU MUST:**

1. **Run Pre-Deployment Tests:**
   ```bash
   cd backend && source venv/bin/activate
   python3 tests/test_pre_deploy.py
   ```
   - If tests FAIL: Stop, fix issues, don't deploy
   - If tests PASS: Proceed with deployment

2. **After Deployment, Run Production Tests:**
   ```bash
   python3 tests/test_production.py
   ```
   - Verifies health endpoint, postcard generation, portrait visibility

**Why:** These tests would have caught the missing `photo_matcher.py` and `sprite-metadata.json` files immediately, saving hours of debugging.

**Test files location:**
- `backend/tests/test_pre_deploy.py` - Checks files exist, imports work, signatures correct
- `backend/tests/test_production.py` - Verifies production is working
- `backend/deploy.py` - Automated deployment with built-in testing

## Project Overview
A web-based character portrait generator for creating customizable character portraits using layered transparent PNG assets. Features include:
- **Character Generator**: Create crew members with customizable portraits (21-layer sprite system)
- **Crew Management**: Save multiple crew members with metadata (names, roles, skills, biography)
- **Postcard Generator**: Create postcards featuring your crew (server-side generation with PIL)
- **Export**: Download individual portraits or postcards as PNG files

## Current Architecture
- **Frontend**: SvelteKit with Svelte 5 (runes), shadcn-svelte UI components, Tailwind CSS
- **Backend**: Django REST API with PIL/Pillow for image processing
- **Deployment**: PythonAnywhere (blindflugstudios.pythonanywhere.com)
- **Remote Server**: Accessible via MCP (use mcp__pythonanywhere__* tools for deployment operations)
- **Assets**: 21-layer portrait system with 193+ PNG sprites in `frontend/static/PortraitSprites/`
- **Local Storage**: Crew data persisted in browser localStorage

## Deployment
- **Django Backend**: `/home/blindflugstudios/CharacterEditor`
- **Frontend Build**: `/home/blindflugstudios/build/` (THIS is where the live site serves from)
- **Domain**: blindflugstudios.pythonanywhere.com
- **Python**: 3.10 with virtualenv at `/home/blindflugstudios/crew-generator-backend/venv`
- **Control**: Use MCP tools (mcp__pythonanywhere__*) to read/write files, reload webapp, etc.
- **Password**: `HFY.ecy5mem1gcd-nhx`

### Deploying Frontend to Production

**IMPORTANT**: The live site serves from `/home/blindflugstudios/build/`, NOT from `CharacterEditor/static/`

1. **Build for production** (from `frontend/` directory):
   ```bash
   npm run build:prod
   ```
   This uses `.env.production` which sets `VITE_STATIC_BASE_PATH=/static` for Django static serving.

2. **Upload complete build** (includes HTML, JS, CSS, and images):
   ```bash
   cd "/Users/momo/Downloads/charactergenerator-prototype copy/frontend"
   sshpass -p 'HFY.ecy5mem1gcd-nhx' rsync -avz --progress --delete --force \
     build/ \
     blindflugstudios@ssh.pythonanywhere.com:/home/blindflugstudios/build/
   ```

3. **Reload webapp**:
   ```bash
   # Use MCP: mcp__pythonanywhere__reload_webapp with domain: blindflugstudios.pythonanywhere.com
   ```

### Uploading Only Assets (PortraitSprites)
If you only need to update sprite images without rebuilding:
```bash
cd "/Users/momo/Downloads/charactergenerator-prototype copy/frontend/static"
sshpass -p 'HFY.ecy5mem1gcd-nhx' rsync -avz --progress \
  PortraitSprites/ \
  blindflugstudios@ssh.pythonanywhere.com:/home/blindflugstudios/build/PortraitSprites/
```

**Note**: Requires `sshpass` installed (`brew install hudochenkov/sshpass/sshpass`)

## Development Commands
All commands must be run from the `frontend/` directory:
- Install dependencies: `npm install`
- Development server: `npm run dev`
- Build for production: `npm run build`
- Preview production build: `npm run preview`
- Type checking: `npm run check`

## Key Components

### Frontend Components

#### Asset Management (`src/lib/assetData.js`)
- `LAYERS`: Object defining all 21 portrait layers with metadata and color tinting flags
- `COLOR_PALETTES`: Color definitions for Skin, Hair, Eye, Accessory
- `getAssetPath(layerName, index, variant, gender)`: Constructs full asset path with gender support
- Gender-specific asset handling for certain layers (Hair, Headshape, Eyes, etc.)

#### Portrait Rendering (`src/lib/PortraitCanvas.svelte`)
- Canvas-based rendering with image caching and color tinting (multiply blend mode)
- Layers rendered back-to-front using HTML5 Canvas API
- Automatic image scaling to fit canvas while maintaining aspect ratio
- `exportPortrait()`: Exports canvas as PNG data URL
- Reactive rendering with Svelte 5 `$effect` runes

#### Character Controls (`src/lib/CharacterControls.svelte`)
- Dropdown selectors for each body part organized by category
- Color pickers for Skin, Hair, Eye, Accessory colors
- `randomizeCharacter()`: Generates random portraits with validation
- Gender-aware asset selection

#### Crew Management (`src/lib/CrewList.svelte`)
- Grid display of crew member thumbnails with canvas rendering
- Select/delete crew members
- Navigate to postcard generator
- Real-time thumbnail updates using `$effect` reactivity

#### Character Metadata (`src/lib/CharacterMetadata.svelte`)
- Edit character information (name, role, class, biography, skills)
- UUID generation for unique character IDs
- AirCrew vs BaseCrew class handling
- Skill ranks (0-6) for AirCrew members

#### Main Page (`src/routes/+page.svelte`)
- Tab-based interface: Appearance, Character Info, Crew Generator
- Save/load crew from localStorage
- Export individual portraits as PNG
- Navigate to postcard generator

#### Postcard Generator (`src/lib/PostcardGenerator.svelte` & `/postcard` route)
- Select postcard style (Blue/Orange)
- Server-side generation via Django API
- Preview and high-quality export
- Handles 1-10 crew members

### Backend Components

#### Postcard Generator API (`backend/api/postcard_generator.py`)
- Server-side postcard generation with PIL/Pillow
- Character rendering with 21-layer sprite composition
- Color tinting using multiply blend mode
- Two layout modes:
  - **Single-character**: Large centered portrait (260×260px) using special template
  - **Multi-character**: 6+4 grid layout for 2-10 characters
- Template selection based on character count and color
- Returns base64 preview or PNG download

#### API Endpoints (`backend/api/urls.py`)
- `/api/generate-crew`: AI crew generation (placeholder)
- `/api/analyze-photo`: Photo analysis (placeholder)
- `/api/generate-postcard`: Postcard generation endpoint

## Asset Structure
Portrait sprites in `frontend/static/PortraitSprites/` with 21 layer directories:
- Naming pattern: `{LayerNumber}_{FeatureName}_{ColorCategory}/`
- File naming: `{feature}_{variant}_{color}.png`
- Render order: Layer 20 (background) rendered first, Layer 0 (front accessories) rendered last
- All assets are transparent PNGs optimized for web

## Data Structures

### Character Object Format
```javascript
{
  gender: "Male" | "Female",
  parts: {
    Body: { index: 0, variant: 0 },
    Head: { index: 1, variant: 0 },
    Ears: { index: 0, variant: 0 },
    Eyes: { index: 3, variant: 4 },
    Nose: { index: 6, variant: 0 },
    Mouth: { index: 2, variant: 0 },
    Eyebrows: { index: 5, variant: 1 },
    Hair: { index: 7, variant: 0 },
    Headshape: { index: 7, variant: 0 },
    // Optional layers (can have index: -1)
    Moustache: { index: -1, variant: 0 },
    Beard: { index: -1, variant: 0 },
    Accessory: { index: -1, variant: 0 },
    Clothes: { index: -1, variant: 0 },
    Headgear: { index: -1, variant: 0 },
    Backpack: { index: -1, variant: 0 },
    Background: { index: 0, variant: 0 },
    // ... other layers
  },
  colorIndices: {
    Skin: 2,      // Index into COLOR_PALETTES.Skin
    Hair: 3,      // Index into COLOR_PALETTES.Hair
    Eye: 2,       // Index into COLOR_PALETTES.Eye
    Accessory: 1  // Index into COLOR_PALETTES.Accessory
  }
}
```

### Crew Member Format
```javascript
{
  character: { /* Character object as above */ },
  metadata: {
    Id: "uuid-string",
    CreatorName: "Your Name",
    FirstName: "John",
    LastName: "Doe",
    Nickname: "Ace",           // AirCrew only
    BirthDate: "1920-01-01",
    Gender: "Male",
    Class: "AirCrew" | "BaseCrew",
    Job: "None" | "AAFCook" | "FieldMechanic" | ...,  // BaseCrew only
    Role: "Pilot" | "Gunner" | "Navigator" | ...,     // AirCrew only
    Biography: { en: "Character background..." },
    SkillRanks: {              // AirCrew only
      Flying: 0-6,
      Shooting: 0-6,
      Bombing: 0-6,
      Endurance: 0-6,
      Engineering: 0-6,
      Navigating: 0-6
    }
  }
}
```

## Current Features
✅ Character portrait generator with 21-layer sprite system
✅ Gender-specific assets and rendering
✅ Color tinting for skin, hair, eyes, accessories
✅ Crew management with save/load (localStorage)
✅ Character metadata editor (names, roles, skills, biography)
✅ Postcard generator (1-10 crew members)
✅ Server-side postcard rendering with PIL
✅ Export portraits and postcards as PNG
✅ Responsive UI with shadcn-svelte components

## Future Development
1. Database persistence for crew data
2. User accounts and authentication
3. Share links with query parameters
4. AI crew generation via OpenAI API
5. Photo analysis for character creation
6. Additional postcard templates
7. Batch export functionality
8. Character import/export (JSON)

Refer to `crew_portrait_generator_system_design.md` for comprehensive technical specifications and user requirements.