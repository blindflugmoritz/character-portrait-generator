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

## Project Overview
A web-based character portrait generator for creating customizable character portraits using layered transparent PNG assets. The frontend SvelteKit application is functional with HTML5 Canvas rendering, asset management, and export capabilities. Backend integration is planned but not yet implemented.

## Current Architecture
- **Frontend**: SvelteKit with HTML5 Canvas rendering (functional)
- **Backend**: Django REST API deployed on PythonAnywhere (blindflugstudios.pythonanywhere.com)
- **Remote Server**: Accessible via MCP (use mcp__pythonanywhere__* tools for deployment operations)
- **Assets**: 21-layer portrait system with 193+ PNG sprites in `frontend/static/PortraitSprites/`

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

### Asset Management (`src/lib/assetData.js`)
- `ASSET_LAYERS`: Array defining all 21 portrait layers with metadata
- `ASSET_FILES`: Object mapping layer folders to available PNG filenames
- `getRandomAsset(layerId)`: Returns random asset filename for a layer
- `getAssetPath(layerId, filename)`: Constructs full asset path

### Portrait Rendering (`src/lib/PortraitCanvas.svelte`)
- Canvas-based rendering with image caching via `loadedImages` Map
- Layers rendered back-to-front (ID 20 → 0) using HTML5 Canvas API
- Automatic image scaling to fit 512×512 canvas while maintaining aspect ratio
- `exportPortrait()`: Exports canvas as PNG data URL
- Reactive rendering triggered on character object changes

### Character Controls (`src/lib/CharacterControls.svelte`)
- Layer selection organized by category (Skin, Hair, Eye, Lip, Accessory, Clothes, Background)
- `randomizeCharacter()`: Generates random portrait with 80% probability for optional layers
- Required layers (Body, Head, Ears, Eyes, Nose, Mouth) always included in random generation
- Per-layer dropdowns for manual asset selection

### Main Page (`src/routes/+page.svelte`)
- Integrates PortraitCanvas and CharacterControls components
- Export functionality: downloads portrait as PNG file
- Share functionality: uses Web Share API or clipboard fallback
- Responsive grid layout with gradient background

## Asset Structure
Portrait sprites in `frontend/static/PortraitSprites/` with 21 layer directories:
- Naming pattern: `{LayerNumber}_{FeatureName}_{ColorCategory}/`
- File naming: `{feature}_{variant}_{color}.png`
- Render order: Layer 20 (background) rendered first, Layer 0 (front accessories) rendered last
- All assets are transparent PNGs optimized for web

## Character State Format
Character objects use layer IDs as keys and filenames as values:
```javascript
{
  17: "body_00_00.png",    // Body layer
  13: "headshape_01_00.png", // Head shape
  10: "hair_07_02.png",    // Hair
  5: "eyes_03_01.png",     // Eyes
  // ... other layers
}
```

## Future Development
1. Django backend API for portrait persistence
2. Database model for storing character configurations
3. Share links with query parameters
4. Optional email collection for updates

Refer to `crew_portrait_generator_system_design.md` for comprehensive technical specifications and user requirements.