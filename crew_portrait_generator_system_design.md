
# 📘 System Design Document  
**Title**: Online Crew Portrait Generator  
**Project**: [Upcoming Base Builder Game — Crew Customizer Tool]  
**Date**: 2025-05-31  
**Author**: Moritz Zumbühl  

---

## 1. 🎯 Purpose

To create a web-based character portrait generator where players can pre-build their in-game crew by layering transparent PNG assets representing different facial/body elements. The final image is rendered dynamically in the browser and optionally saved to a backend.

---

## 2. 👤 Target Users

- Fans of the game pre-release  
- Streamers/community sharing their “crew”  
- TikTok and mobile users accessing via in-app browsers  

---

## 3. ⚙️ Core Features

- Randomly or manually generate character portraits using 20 transparent PNG layers
- Preview character in real-time via HTML5 Canvas or stacked `<img>` tags
- Customize individual traits (e.g. hair, mouth, eyes)
- Save and share unique portraits via a Django backend
- Export image as PNG and optionally store user email for launch updates

---

## 4. 🧱 System Architecture

```plaintext
[SvelteKit Frontend] ←→ [Django REST Backend]  
        ↑                      ↑  
[Layer Rendering in Canvas]   [PNG Layers via /static/]  
        ↓                      ↓  
  Export / Share / Save    JSON Config + Email (optional)
```

---

## 5. 🧩 Data Structure

### 5.1 Portrait Configuration JSON

```json
{
  "background": "20_Background_Background/bg03.png",
  "body": "17_Body_Skin/body01.png",
  "clothes": "16_Clothes_Clothes/top05.png",
  "hair": "10_Hair_Hair/hair07.png",
  "mouth": "9_Mouth_Lip/mouth02.png",
  "eyes": "5_Eyes_Eye/eyes01.png"
}
```

### 5.2 Django Model

```python
class Portrait(models.Model):
    slug = models.SlugField(unique=True)
    config = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
```

---

## 6. 📂 Layer Categories & Render Order

This is the render order (back to front):

1. `20_Background_Background`  
2. `19_ClothesBack_Clothes`  
3. `18_HairBack_Hair`  
4. `17_Body_Skin`  
5. `16_Clothes_Clothes`  
6. `15_Ears_Skin`  
7. `14_Accessory_Accessory`  
8. `13_Headshape_Skin`  
9. `12_Detail_Skin`  
10. `11_Detail_Skin`  
11. `10_Hair_Hair`  
12. `9_Mouth_Lip`  
13. `8_Beard_Hair`  
14. `7_Moustache_Hair`  
15. `6_HeadshapeAuxiliary_Skin`  
16. `5_Eyes_Eye`  
17. `4_Eyebrows_Hair`  
18. `3_Accessory_Accessory`  
19. `2_Nose_Skin`  
20. `1_Blemish_Skin`  
21. `0_Accessory_Accessory`  

---

## 7. 🖼️ Frontend UI Components (SvelteKit)

- `<PortraitPreview>` — renders stacked layers using canvas or `<img>`
- `<LayerSelector>` — dropdown or thumbnails to pick a layer
- `<RandomizeButton>` — assigns a random file from each folder
- `<SaveButton>` — sends JSON config to Django API
- `<ShareLink>` — generates URL with query params (e.g., `?hair=10_03&eyes=5_01`)

---

## 8. 🔁 API Routes (Django REST Framework)

| Method | URL                      | Purpose                       |
|--------|--------------------------|-------------------------------|
| GET    | `/api/portraits/<slug>` | Load portrait by slug         |
| POST   | `/api/portraits/`        | Save new portrait config      |
| POST   | `/api/email/`            | Save user email (optional)    |

---

## 9. 🚀 Deployment Plan

- **Frontend**: SvelteKit hosted on Vercel or Netlify  
- **Backend**: Django REST Framework hosted on Render, Railway, or DigitalOcean  
- **Assets**: PNG layers stored in Django's `/static/` directory  

---

## 10. 🔐 Security & Performance

- Rate-limit `POST` endpoints to prevent abuse  
- Add CORS middleware for cross-origin frontend/backend  
- Avoid storing large image data—just store layer config  
- Optional: Email confirmation for GDPR compliance  

---

## 11. ✅ Milestones

| Milestone                        | Owner   | Due Date  |
|----------------------------------|---------|-----------|
| Asset folder review & naming     | Moritz  | Done      |
| Frontend UI draft                | Claude  | TBA       |
| Django API skeleton              | Claude  | TBA       |
| Static asset serving             | Claude  | TBA       |
| End-to-end MVP (generate → share)| Claude  | TBA       |

---
