#!/bin/bash
# Deployment verification script
# Run this after deploying to catch missing files quickly

set -e

echo "🔍 Deployment Health Check"
echo "=========================="

# Check health endpoint
echo ""
echo "1️⃣ Checking production health endpoint..."
HEALTH_RESPONSE=$(curl -s https://blindflugstudios.pythonanywhere.com/api/health)

if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
    echo "✅ Health check PASSED"
else
    echo "❌ Health check FAILED"
    echo ""
    echo "Issues found:"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool
    exit 1
fi

# Test postcard generation
echo ""
echo "2️⃣ Testing postcard generation..."
POSTCARD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://blindflugstudios.pythonanywhere.com/api/generate-postcard \
  -H "Content-Type: application/json" \
  -d '{
    "color": "blue",
    "characters": [{
      "gender": "Male",
      "bodyShapeIndex": 1,
      "colorIndices": {"Skin": 2, "Hair": 3, "Eye": 2, "Accessory": 0},
      "parts": {
        "Body": {"index": 0, "variant": 0},
        "Headshape": {"index": 1, "variant": 0},
        "Ears": {"index": 0, "variant": 0},
        "Hair": {"index": 7, "variant": 0},
        "HairBack": {"index": 7, "variant": 0},
        "Eyes": {"index": 12, "variant": 0},
        "Eyebrows": {"index": 0, "variant": 0},
        "Nose": {"index": 2, "variant": 0},
        "Mouth": {"index": 2, "variant": 0},
        "Beard": {"index": -1, "variant": -1},
        "Moustache": {"index": -1, "variant": -1},
        "AccessoryFace": {"index": -1, "variant": -1},
        "AccessoryHead": {"index": -1, "variant": -1},
        "AccessoryFront": {"index": -1, "variant": -1},
        "DetailUpper": {"index": -1, "variant": -1},
        "DetailLower": {"index": -1, "variant": -1},
        "Blemish": {"index": -1, "variant": -1},
        "Clothes": {"index": 0, "variant": 0},
        "ClothesBack": {"index": 0, "variant": 0},
        "Background": {"index": -1, "variant": -1}
      }
    }]
  }')

HTTP_CODE=$(echo "$POSTCARD_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Postcard generation PASSED (HTTP 200)"
else
    echo "❌ Postcard generation FAILED (HTTP $HTTP_CODE)"
    echo "$POSTCARD_RESPONSE" | head -n -1
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🎉 Deployment is healthy!"
