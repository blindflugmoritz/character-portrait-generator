# Complete Implementation Plan: Photo-to-Character Generation Feature

**Status:** Ready to implement (after Django backend is complete)
**Created:** 2025-11-28
**Estimated Implementation Time:** 5 days
**Cost per Generation:** ~$0.015

---

## Project Overview
Add photo upload functionality to the character portrait generator that analyzes uploaded photos using Anthropic Claude Vision API and automatically generates matching character portraits by mapping detected facial features to the existing 193 sprite assets.

---

## 1. Technical Architecture

### 1.1 System Flow
```
User uploads photo (max 2MB, JPEG/PNG/HEIC/WebP)
    ↓
Frontend validates & encodes to base64
    ↓
POST to /api/analyze-photo with image data
    ↓
SvelteKit API route receives image
    ↓
Send to Anthropic Claude Vision API with structured prompt
    ↓
Claude returns JSON with detected features
    ↓
Backend matching algorithm compares with sprite-metadata.json
    ↓
Generate character config (indices/variants per layer)
    ↓
Return character JSON to frontend
    ↓
Frontend loads character in existing editor (user can tweak)
```

### 1.2 Technology Stack
- **Frontend**: SvelteKit (existing)
- **Backend**: SvelteKit API routes (existing pattern)
- **Vision AI**: Anthropic Claude Vision API (existing integration)
- **Sprite Metadata**: sprite-metadata.json (existing, 2608 lines)
- **No database**: Stateless generation, results returned as JSON

---

## 2. File Structure & New Files

### 2.1 New Files to Create

```
frontend/
├── src/
│   ├── routes/
│   │   ├── api/
│   │   │   └── analyze-photo/
│   │   │       └── +server.js          [NEW] Photo analysis endpoint
│   ├── lib/
│   │   ├── photoMatcher.js             [NEW] Feature matching logic
│   │   ├── PhotoUpload.svelte          [NEW] Upload UI component
│   │   └── components/
│   │       └── PhotoAnalysisResult.svelte [NEW] Show confidence/results
└── sprite-metadata.json                [EXISTS] Already perfect!
```

### 2.2 Files to Modify

```
frontend/
├── src/
│   ├── routes/
│   │   └── +page.svelte                [MODIFY] Add photo upload UI
│   ├── lib/
│   │   └── assetData.js                [MODIFY] Add helper for metadata lookup
```

---

## 3. API Endpoint Design

### 3.1 POST `/api/analyze-photo/+server.js`

**Request:**
```javascript
{
  "image": "base64_encoded_image_data",
  "mimeType": "image/jpeg"
}
```

**Response (Success):**
```javascript
{
  "character": {
    "gender": "Male",
    "bodyShapeIndex": 1,
    "colorIndices": {
      "Skin": 2,
      "Hair": 3,
      "Eye": 1,
      "Accessory": 0
    },
    "parts": {
      "Body": { "index": 0, "variant": 0 },
      "Headshape": { "index": 2, "variant": 0 },
      // ... all 21 layers
    }
  },
  "analysis": {
    "detectedFeatures": {
      "face_shape": "square angular",
      "skin_tone": "light medium",
      "hair_length": "short",
      "hair_style": "spiky",
      // ... all detected features
    },
    "matchConfidence": {
      "Headshape": 0.85,
      "Hair": 0.92,
      "Nose": 0.78,
      // ... per-layer confidence
    }
  }
}
```

**Response (Error):**
```javascript
{
  "error": "No face detected in photo",
  "details": "..."
}
```

---

## 4. Claude Vision API Integration

### 4.1 Prompt Design

```javascript
const prompt = `Analyze this portrait photo and extract facial features in structured JSON format.

REQUIREMENTS:
- Detect ONE person's face (if multiple, analyze the most prominent)
- Return detailed, descriptive terms (not measurements)
- Use terms like: angular, soft, rounded, square, oval, delicate, prominent, etc.

Return JSON with this EXACT structure:
{
  "face_detected": true,
  "gender_presentation": "Male|Female|Ambiguous",
  "face_shape": "oval|round|square|heart|diamond|rectangular|angular",
  "face_characteristics": ["angular jaw", "defined chin", "soft curves"],

  "skin_tone": "very light|light|light medium|medium|olive|brown|dark brown",

  "hair": {
    "present": true,
    "length": "bald|very short|short|medium|long",
    "style": "spiky|wavy|straight|curly|swept|slicked|messy|ponytail|bob",
    "color": "black|dark brown|brown|light brown|blonde|red|auburn|gray|white",
    "characteristics": ["messy", "styled", "natural"]
  },

  "facial_hair": {
    "beard": "none|stubble|goatee|full",
    "mustache": "none|thin|handlebar|chevron|walrus"
  },

  "nose": {
    "size": "small|medium|large",
    "shape": "rounded|angular|curved|straight|button|hook|upturned",
    "bridge": "low|medium|high",
    "characteristics": ["delicate", "prominent", "feminine", "masculine"]
  },

  "eyes": {
    "shape": "almond|round|narrow|wide",
    "size": "small|medium|large",
    "color": "blue|green|brown|hazel|gray|amber"
  },

  "mouth": {
    "size": "small|medium|large",
    "shape": "full|thin|neutral",
    "expression": "neutral|smiling|frowning"
  },

  "accessories": {
    "glasses": "none|round|rectangular|monocle",
    "other": ["beauty mark", "scar", "etc"]
  },

  "age_markers": {
    "apparent_age": "young|middle|mature|elderly",
    "wrinkles": "none|minimal|moderate|prominent",
    "details": ["crow's feet", "smile lines", "forehead lines"]
  },

  "overall_characteristics": ["youthful", "strong", "delicate", "angular", "soft"]
}

Analyze the photo now and return ONLY the JSON, no markdown, no explanations.`;
```

### 4.2 API Call Implementation

```javascript
const message = await anthropic.messages.create({
  model: 'claude-sonnet-4-5',
  max_tokens: 2048,
  messages: [
    {
      role: 'user',
      content: [
        {
          type: 'image',
          source: {
            type: 'base64',
            media_type: mimeType,
            data: imageBase64
          }
        },
        {
          type: 'text',
          text: prompt
        }
      ]
    }
  ]
});
```

---

## 5. Feature Matching Algorithm

### 5.1 Matching Strategy (`photoMatcher.js`)

```javascript
/**
 * Match detected features to sprite metadata
 * Priority: Face Shape > Hair > Skin Tone > Other features
 */

export function matchFeaturesToSprites(detectedFeatures, spriteMetadata) {
  const character = {
    gender: mapGender(detectedFeatures.gender_presentation),
    bodyShapeIndex: 1, // Default to average
    colorIndices: {
      Skin: matchSkinTone(detectedFeatures.skin_tone),
      Hair: matchHairColor(detectedFeatures.hair.color),
      Eye: matchEyeColor(detectedFeatures.eyes.color),
      Accessory: 0 // Default
    },
    parts: {}
  };

  // Priority 1: Face Shape (most important)
  character.parts.Headshape = matchHeadshape(
    detectedFeatures.face_shape,
    detectedFeatures.face_characteristics,
    detectedFeatures.gender_presentation,
    spriteMetadata
  );

  // Priority 2: Hair
  if (detectedFeatures.hair.present && detectedFeatures.hair.length !== 'bald') {
    character.parts.Hair = matchHair(
      detectedFeatures.hair,
      detectedFeatures.gender_presentation,
      spriteMetadata
    );

    // Match HairBack if Hair exists
    const hairIndex = character.parts.Hair.index;
    const matchingHairBack = getMatchingHairBackIndices(hairIndex, character.gender);
    if (matchingHairBack.length > 0) {
      character.parts.HairBack = { index: matchingHairBack[0], variant: 0 };
    }
  } else {
    character.parts.Hair = { index: 4, variant: 0 }; // Bald
    character.parts.HairBack = { index: 4, variant: 0 };
  }

  // Priority 3: Nose
  character.parts.Nose = matchNose(
    detectedFeatures.nose,
    detectedFeatures.gender_presentation,
    spriteMetadata
  );

  // Remaining features
  character.parts.Body = { index: 0, variant: 0 };
  character.parts.Ears = { index: 0, variant: 0 };
  character.parts.Eyes = matchEyes(detectedFeatures.eyes, character.gender);
  character.parts.Eyebrows = { index: 0, variant: 0 }; // Default
  character.parts.Mouth = matchMouth(detectedFeatures.mouth);

  // Facial hair (only for males)
  if (character.gender === 'Male') {
    character.parts.Beard = matchBeard(detectedFeatures.facial_hair.beard);
    character.parts.Moustache = matchMoustache(detectedFeatures.facial_hair.mustache);

    // Clear mouth if mustache present
    if (character.parts.Moustache.index !== -1) {
      character.parts.Mouth = { index: -1, variant: -1 };
    }
  } else {
    character.parts.Beard = { index: -1, variant: -1 };
    character.parts.Moustache = { index: -1, variant: -1 };
  }

  // Accessories
  character.parts.AccessoryFace = matchAccessories(detectedFeatures.accessories);
  character.parts.AccessoryHead = { index: -1, variant: -1 };
  character.parts.AccessoryFront = { index: -1, variant: -1 };

  // Details (age markers)
  character.parts.DetailUpper = matchAgeMarkers(detectedFeatures.age_markers, 'upper');
  character.parts.DetailLower = matchAgeMarkers(detectedFeatures.age_markers, 'lower');
  character.parts.Blemish = matchBlemishes(detectedFeatures.accessories.other);

  // Clothes (default)
  character.parts.Clothes = { index: 0, variant: 0 };
  character.parts.ClothesBack = { index: 0, variant: 0 };

  // Background
  character.parts.Background = { index: -1, variant: -1 };

  return character;
}
```

### 5.2 Tag-Based Matching Logic

```javascript
/**
 * Match a layer by comparing detected features with sprite tags
 * Returns best matching sprite index/variant
 */
function matchLayerByTags(layerName, detectedTerms, gender, spriteMetadata) {
  const layerKey = LAYERS[layerName].folder;
  const layerSprites = spriteMetadata.categories[layerKey];

  let bestMatch = { filename: null, score: 0, index: -1, variant: -1 };

  for (const [filename, metadata] of Object.entries(layerSprites)) {
    // Skip gender-mismatched sprites
    if (metadata.gender_fit !== 'both' && metadata.gender_fit !== gender.toLowerCase()) {
      continue;
    }

    // Calculate match score based on tag overlap
    let score = 0;
    const spriteTags = metadata.tags || [];
    const spriteCharacteristics = metadata.characteristics?.split(',').map(s => s.trim()) || [];
    const allSpriteTerms = [...spriteTags, ...spriteCharacteristics, metadata.style, metadata.shape];

    for (const term of detectedTerms) {
      for (const spriteTerm of allSpriteTerms) {
        if (spriteTerm && spriteTerm.toLowerCase().includes(term.toLowerCase())) {
          score += 1;
        }
        if (term && term.toLowerCase().includes(spriteTerm.toLowerCase())) {
          score += 0.5;
        }
      }
    }

    if (score > bestMatch.score) {
      // Extract index and variant from filename
      const match = filename.match(/(\w+)_(\d+)_(\d+)/);
      if (match) {
        bestMatch = {
          filename,
          score,
          index: parseInt(match[2]),
          variant: parseInt(match[3])
        };
      }
    }
  }

  // If no good match found (score < 1), use defaults
  if (bestMatch.score < 1) {
    const availableIndices = getAvailableIndices(layerName, gender);
    bestMatch.index = availableIndices[0] || 0;
    bestMatch.variant = 0;
    bestMatch.score = 0; // Low confidence
  }

  return {
    index: bestMatch.index,
    variant: bestMatch.variant,
    confidence: Math.min(bestMatch.score / 3, 1.0) // Normalize to 0-1
  };
}
```

### 5.3 Color Mapping

```javascript
function matchSkinTone(detectedTone) {
  const toneMap = {
    'very light': 0,
    'light': 1,
    'light medium': 2,
    'medium': 3,
    'olive': 4,
    'brown': 5,
    'dark brown': 6
  };
  return toneMap[detectedTone.toLowerCase()] ?? 2;
}

function matchHairColor(detectedColor) {
  const colorMap = {
    'platinum blonde': 0,
    'blonde': 1,
    'light brown': 2,
    'brown': 3,
    'dark brown': 4,
    'black': 5,
    'auburn': 6,
    'red': 7,
    'gray': 4,
    'white': 0
  };
  return colorMap[detectedColor.toLowerCase()] ?? 3;
}

function matchEyeColor(detectedColor) {
  const colorMap = {
    'blue': 0,
    'green': 1,
    'brown': 2,
    'hazel': 3,
    'gray': 4,
    'amber': 5
  };
  return colorMap[detectedColor.toLowerCase()] ?? 2;
}
```

---

## 6. Frontend UI Components

### 6.1 PhotoUpload.svelte Component

```svelte
<script>
  export let onPhotoAnalyzed = (character) => {};

  let uploading = false;
  let analyzing = false;
  let error = null;
  let dragActive = false;

  async function handleFileSelect(event) {
    const file = event.target.files?.[0] || event.dataTransfer?.files?.[0];
    if (!file) return;

    // Validate
    const validTypes = ['image/jpeg', 'image/png', 'image/heic', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      error = 'Invalid file type. Please upload JPEG, PNG, HEIC, or WebP';
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      error = 'File too large. Maximum size is 2MB';
      return;
    }

    await analyzePhoto(file);
  }

  async function analyzePhoto(file) {
    analyzing = true;
    error = null;

    try {
      // Convert to base64
      const reader = new FileReader();
      const base64 = await new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      // Call API
      const response = await fetch('/api/analyze-photo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: base64,
          mimeType: file.type
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Analysis failed');
      }

      const result = await response.json();
      onPhotoAnalyzed(result.character);

    } catch (err) {
      error = err.message;
    } finally {
      analyzing = false;
    }
  }
</script>

<div class="upload-container">
  <h3>📸 Generate from Photo</h3>

  {#if analyzing}
    <div class="analyzing">
      <div class="spinner"></div>
      <p>Analyzing photo...</p>
    </div>
  {:else}
    <div
      class="drop-zone"
      class:drag-active={dragActive}
      on:drop|preventDefault={handleFileSelect}
      on:dragover|preventDefault={() => dragActive = true}
      on:dragleave={() => dragActive = false}
    >
      <input
        type="file"
        accept="image/jpeg,image/png,image/heic,image/webp"
        on:change={handleFileSelect}
        id="photo-upload"
      />
      <label for="photo-upload">
        <div class="upload-icon">📷</div>
        <p>Click to upload or drag & drop</p>
        <small>JPEG, PNG, HEIC, WebP (max 2MB)</small>
      </label>
    </div>
  {/if}

  {#if error}
    <div class="error">{error}</div>
  {/if}
</div>

<style>
  .drop-zone {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
  }

  .drop-zone:hover, .drop-zone.drag-active {
    border-color: #4caf50;
    background: #f0f9f0;
  }

  .analyzing {
    text-align: center;
    padding: 40px;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #4caf50;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error {
    color: #f44336;
    padding: 10px;
    background: #ffebee;
    border-radius: 4px;
    margin-top: 10px;
  }
</style>
```

### 6.2 Modified +page.svelte

```svelte
<script>
  import PortraitCanvas from '$lib/PortraitCanvas.svelte';
  import CharacterControls from '$lib/CharacterControls.svelte';
  import PhotoUpload from '$lib/PhotoUpload.svelte';

  let character = {};

  function handlePhotoAnalyzed(generatedCharacter) {
    character = generatedCharacter;
    // Optional: show success message
  }
</script>

<div class="container">
  <h1>Character Portrait Generator</h1>

  <!-- Add Photo Upload Section -->
  <div class="generation-options">
    <PhotoUpload onPhotoAnalyzed={handlePhotoAnalyzed} />
  </div>

  <div class="main-content">
    <div class="canvas-section">
      <PortraitCanvas {character} />
      <!-- Export/Share buttons -->
    </div>

    <div class="controls-section">
      <CharacterControls bind:character />
    </div>
  </div>
</div>
```

---

## 7. Error Handling & Edge Cases

### 7.1 Error Scenarios

| Error | Handling Strategy |
|-------|------------------|
| **No face detected** | Return error: "No face detected in photo. Please upload a clear portrait photo." |
| **Multiple faces** | Analyze most prominent face, add warning |
| **Poor quality/lighting** | Attempt analysis, return low confidence scores |
| **File too large** | Frontend validation, reject before upload |
| **Invalid format** | Frontend validation |
| **API timeout** | 30s timeout, return error with retry option |
| **API rate limit** | Return error with wait time |
| **Feature outside sprite range** | Use closest match + low confidence score |

### 7.2 Edge Case Handling

```javascript
// No face detected
if (!analysis.face_detected) {
  return json({
    error: 'No face detected in photo',
    details: 'Please upload a clear portrait photo showing one person\'s face'
  }, { status: 400 });
}

// Ambiguous gender
if (analysis.gender_presentation === 'Ambiguous') {
  // Default to Male sprites (more variety available)
  character.gender = 'Male';
}

// Very unusual features
if (analysis.hair.color === 'blue' || analysis.hair.color === 'green') {
  // Map to closest natural color
  character.colorIndices.Hair = 5; // Black
}

// Age detection for children
if (analysis.age_markers.apparent_age === 'young' || analysis.age_markers.apparent_age === 'child') {
  // Round face, no wrinkles
  character.parts.DetailUpper = { index: -1, variant: -1 };
  character.parts.DetailLower = { index: -1, variant: -1 };
}
```

---

## 8. Implementation Steps (Ordered)

### Phase 1: Backend Foundation (Day 1)
1. ✅ Create `/src/routes/api/analyze-photo/+server.js`
2. ✅ Implement Claude Vision API call with prompt
3. ✅ Test with sample images, verify JSON response structure
4. ✅ Add error handling for API failures

### Phase 2: Matching Algorithm (Day 2)
5. ✅ Create `/src/lib/photoMatcher.js`
6. ✅ Implement `matchFeaturesToSprites()` main function
7. ✅ Implement color mapping functions (skin, hair, eyes)
8. ✅ Implement tag-based matching for each layer:
   - Face shape (headshape)
   - Hair
   - Nose
   - Eyes
   - Mouth
   - Facial hair
   - Accessories
   - Age markers
9. ✅ Test matching algorithm with mock detected features

### Phase 3: Frontend UI (Day 3)
10. ✅ Create `/src/lib/PhotoUpload.svelte` component
11. ✅ Add file validation (size, type)
12. ✅ Implement drag & drop functionality
13. ✅ Add loading/analyzing state
14. ✅ Add error display
15. ✅ Integrate into `+page.svelte`

### Phase 4: Integration & Testing (Day 4)
16. ✅ Wire up PhotoUpload → API → CharacterControls flow
17. ✅ Test full flow with real photos
18. ✅ Test edge cases (no face, multiple faces, poor quality)
19. ✅ Adjust matching algorithm based on results
20. ✅ Fine-tune confidence thresholds

### Phase 5: Polish & Optimization (Day 5)
21. ✅ Add confidence indicators (optional visual feedback)
22. ✅ Optimize image compression before upload
23. ✅ Add loading progress indicators
24. ✅ Document API usage and costs
25. ✅ User testing & refinement

---

## 9. Testing Strategy

### 9.1 Test Cases

| Test Category | Test Cases |
|--------------|------------|
| **Basic Functionality** | - Upload JPEG → generates character<br>- Upload PNG → generates character<br>- Upload HEIC → generates character |
| **Face Detection** | - Clear front-facing portrait<br>- Side profile (should work)<br>- Multiple people (picks main face)<br>- No face (error) |
| **Feature Matching** | - Bald person → hair_04_00<br>- Beard → appropriate beard sprite<br>- Glasses → accessory match<br>- Female → only female sprites |
| **Edge Cases** | - File > 2MB (reject)<br>- Invalid format (reject)<br>- Corrupted image (error)<br>- Very dark/bright photo (best effort) |
| **Gender Matching** | - Male photo → male sprites<br>- Female photo → female sprites<br>- Ambiguous → defaults properly |
| **Ethnicity/Skin** | - Light skin → indices 0-2<br>- Dark skin → indices 5-6<br>- Medium/olive → indices 3-4 |

### 9.2 Test Data
Prepare 10-15 test photos:
- 3 male, clear lighting, various ages
- 3 female, clear lighting, various ages
- 2 with facial hair (beard, mustache)
- 2 with glasses
- 1 bald
- 1 with unusual angle/lighting
- 1 with multiple people
- 1 with no face

---

## 10. Cost Analysis

### 10.1 Per-Request Costs

| Operation | Cost |
|-----------|------|
| Claude Vision API call | ~$0.015 per image |
| Data transfer | negligible |
| Processing time | ~2-5 seconds |

**Total cost per generation: ~$0.015**

### 10.2 Budget Estimates

| Monthly Usage | Cost |
|---------------|------|
| 100 generations | $1.50 |
| 1,000 generations | $15.00 |
| 10,000 generations | $150.00 |

Well under the $0.05 per generation budget! ✅

---

## 11. Future Enhancements (Post-MVP)

### Phase 2 Features (Later)
1. **User Feedback Loop**
   - Track which features users manually adjust after generation
   - Add thumbs up/down rating on results
   - Store adjustment patterns in database
   - Use data to improve matching over time

2. **Multiple Photo Support**
   - Allow 2-3 photos per character
   - Merge analysis from multiple angles
   - Better accuracy from additional data

3. **Advanced Matching**
   - Machine learning model for better sprite matching
   - Custom-trained model on sprite dataset
   - Confidence visualization per feature

4. **Batch Processing**
   - Upload multiple photos → generate multiple characters
   - Useful for creating teams/squads

---

## 12. Security & Privacy

### 12.1 Security Measures
- ✅ File size validation (2MB max)
- ✅ File type validation (whitelist only)
- ✅ No file storage (process & delete immediately)
- ✅ API rate limiting (prevent abuse)
- ✅ Input sanitization for filenames

### 12.2 Privacy Policy
- Photos are NOT stored on server
- Photos sent to Anthropic API (see their privacy policy)
- Anthropic does not train on API data
- No PII collected
- Generated character data only returned to client

---

## 13. Documentation Requirements

### 13.1 Code Documentation
- JSDoc comments for all public functions
- Inline comments for complex matching logic
- README section for photo upload feature

### 13.2 User Documentation
- Help text in UI explaining feature
- Example photos that work well
- Troubleshooting common issues

---

## 14. Success Metrics

| Metric | Target |
|--------|--------|
| **Generation Success Rate** | >90% |
| **User Satisfaction** | >80% don't manually adjust major features |
| **Processing Time** | <5 seconds average |
| **Cost per Generation** | <$0.02 |
| **Error Rate** | <5% |

---

## 15. Configuration Requirements

### 15.1 Environment Variables Needed
```env
# Already exists in project:
ANTHROPIC_API_KEY=sk-ant-...

# No new environment variables needed
```

### 15.2 Dependencies
```json
{
  "@anthropic-ai/sdk": "^0.71.0"  // Already installed
}
```

No new npm packages required! ✅

---

## 16. Decision Log

### Key Decisions Made
1. **Vision AI Provider:** Anthropic Claude (already integrated, cost-effective)
2. **Single Photo Only:** Simplified MVP, can add multi-photo later
3. **No Photo Storage:** Privacy-first, process and discard immediately
4. **No Database:** Stateless generation, results returned to client
5. **SvelteKit API Routes:** Matches existing backend pattern
6. **Tag-Based Matching:** Uses existing sprite-metadata.json structure
7. **File Size Limit:** 2MB (balance between quality and upload speed)
8. **Allowed Formats:** JPEG, PNG, HEIC, WebP (covers all common formats)
9. **Priority Matching:** Face shape > Hair > Skin tone (most distinctive features first)
10. **User Feedback:** Planned for Phase 2 (after Django backend)

---

## 17. Questions Answered During Planning

| Question | Answer | Rationale |
|----------|--------|-----------|
| Which AI service? | Anthropic Claude | Already integrated, cost-effective |
| Where to process? | Backend (SvelteKit routes) | Better control, can cache results later |
| Cost tolerance? | Under $0.05 per generation | ~$0.015 actual cost ✅ |
| User flow? | Instant auto-generate | Best UX, user can refine after |
| Multiple photos? | No (single photo only) | Simplified MVP |
| Photo quality issues? | Show error, ask for new photo | Clear user feedback |
| Editable results? | Yes, in normal editor | Leverages existing UI |
| Sprite metadata? | Use existing (AI-generated) | Already perfect, 2608 lines |
| No perfect match? | Pick closest automatically | Better UX than showing options |
| Priority features? | Face, Hair, Skin tone | Most distinctive |
| Backend tech? | SvelteKit API routes | Matches existing pattern |
| Photo storage? | Don't store (immediate delete) | Privacy-first |
| Save characters? | No database (return JSON) | Stateless for now |
| Max file size? | 2MB | Balance quality/speed |
| Max photos? | 1 per character | Simplified for MVP |
| Allowed formats? | All common formats | Maximum compatibility |
| Metadata generation? | Already done (use existing) | sprite-metadata.json ✅ |
| Prompt strategy? | Single structured prompt | Cost-effective, simpler |
| User improvements? | Plan for Phase 2 | After Django backend |

---

## 18. Ready for Implementation

This plan is **complete and ready to implement** after Django backend is finished.

**What's already prepared:**
- ✅ sprite-metadata.json (2608 lines, AI-generated)
- ✅ Anthropic API integration
- ✅ SvelteKit project structure
- ✅ Existing character generation system

**What needs to be built:**
- 1 API endpoint (~200 lines)
- 1 Matching algorithm (~400 lines)
- 1 Upload component (~150 lines)
- Minor modifications to existing files

**Estimated timeline:** 5 days
**Estimated cost:** $0.015 per generation
**Next step:** Implement Django backend first, then return to this plan
