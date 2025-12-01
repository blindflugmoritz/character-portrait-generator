"""
Server-side postcard generation using Pillow (PIL)
Renders character portraits onto postcard templates
"""
import os
from PIL import Image, ImageDraw
from io import BytesIO
import base64

# VERSION IDENTIFIER - increment to verify module is loaded
MODULE_VERSION = "1.0.1"
print(f"postcard_generator.py MODULE_VERSION {MODULE_VERSION} loaded")

# Postcard dimensions
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 614

# Character canvas size (for rendering individual portraits)
CHARACTER_SIZE = 256

# Color palettes - MUST match frontend assetData.js exactly!
COLOR_PALETTES = {
    'Skin': [
        '#FFE0BD',  # 0: Very Light
        '#FFCD94',  # 1: Light
        '#EAC086',  # 2: Light Medium
        '#C68642',  # 3: Medium
        '#A67C52',  # 4: Olive
        '#8D5524',  # 5: Brown
        '#664229'   # 6: Dark Brown
    ],
    'Hair': [
        '#F5F5DC',  # 0: Platinum Blonde
        '#E5C18A',  # 1: Blonde
        '#A67C52',  # 2: Light Brown
        '#6E4A2D',  # 3: Brown
        '#4A2C1C',  # 4: Dark Brown
        '#1C1C1C',  # 5: Black
        '#8B4513',  # 6: Auburn
        '#C85A32'   # 7: Red
    ],
    'Eye': [
        '#5A9BCF',  # 0: Blue
        '#5FA777',  # 1: Green
        '#6E4A2D',  # 2: Brown
        '#8D6E49',  # 3: Hazel
        '#8FA8B0',  # 4: Gray
        '#D4A650'   # 5: Amber
    ],
    'Accessory': [
        '#1C1C1C',  # 0: Black
        '#6E4A2D',  # 1: Brown
        '#808080',  # 2: Gray
        '#C0C0C0',  # 3: Silver
        '#FFD700'   # 4: Gold
    ]
}

# Layer definitions (from assetData.js) - MUST match frontend exactly!
LAYERS = {
    'Background': {'id': 20, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'ClothesBack': {'id': 19, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'HairBack': {'id': 18, 'useSkinColor': False, 'useHairColor': True, 'useEyeColor': False, 'useAccessoryColor': False},
    'Body': {'id': 17, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'Clothes': {'id': 16, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'Ears': {'id': 15, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'AccessoryHead': {'id': 14, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': True},
    'Headshape': {'id': 13, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'DetailUpper': {'id': 12, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'DetailLower': {'id': 11, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'Hair': {'id': 10, 'useSkinColor': False, 'useHairColor': True, 'useEyeColor': False, 'useAccessoryColor': False},
    'Mouth': {'id': 9, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'Beard': {'id': 8, 'useSkinColor': False, 'useHairColor': True, 'useEyeColor': False, 'useAccessoryColor': False},
    'Moustache': {'id': 7, 'useSkinColor': False, 'useHairColor': True, 'useEyeColor': False, 'useAccessoryColor': False},
    'Eyes': {'id': 5, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': True, 'useAccessoryColor': False},
    'Eyebrows': {'id': 4, 'useSkinColor': False, 'useHairColor': True, 'useEyeColor': False, 'useAccessoryColor': False},
    'AccessoryFace': {'id': 3, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': True},
    'Nose': {'id': 2, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'Blemish': {'id': 1, 'useSkinColor': True, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': False},
    'AccessoryFront': {'id': 0, 'useSkinColor': False, 'useHairColor': False, 'useEyeColor': False, 'useAccessoryColor': True},
}


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def apply_color_tint(img, hex_color):
    """
    Apply color tint to an image using multiply blend mode
    Same method as the client-side Canvas rendering
    """
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Create a color overlay
    color_overlay = Image.new('RGBA', img.size, hex_to_rgb(hex_color) + (255,))

    # Apply multiply blend
    # Multiply blend: result = (base * blend) / 255
    base = img.split()
    overlay = color_overlay.split()

    r = Image.eval(base[0], lambda a: int((a * overlay[0].getpixel((0, 0))) / 255))
    g = Image.eval(base[1], lambda a: int((a * overlay[1].getpixel((0, 0))) / 255))
    b = Image.eval(base[2], lambda a: int((a * overlay[2].getpixel((0, 0))) / 255))

    # Keep original alpha
    result = Image.merge('RGBA', (r, g, b, base[3]))

    return result


def get_asset_path(layer_name, index, variant, gender, base_path):
    """
    Construct the full path to a sprite asset
    """
    layer_info = LAYERS.get(layer_name)
    if not layer_info:
        return None

    layer_id = layer_info['id']

    # Sprite folders - MUST match frontend assetData.js exactly!
    sprite_folders = {
        'Background': '20_Background_Background',
        'ClothesBack': '19_ClothesBack_Clothes',
        'HairBack': '18_HairBack_Hair',
        'Body': '17_Body_Skin',
        'Clothes': '16_Clothes_Clothes',
        'Ears': '15_Ears_Skin',
        'AccessoryHead': '14_Accessory_Accessory',
        'Headshape': '13_Headshape_Skin',
        'DetailUpper': '12_Detail_Skin',
        'DetailLower': '11_Detail_Skin',
        'Hair': '10_Hair_Hair',
        'Mouth': '9_Mouth_Lip',
        'Beard': '8_Beard_Hair',
        'Moustache': '7_Moustache_Hair',
        'Eyes': '5_Eyes_Eye',
        'Eyebrows': '4_Eyebrows_Hair',
        'AccessoryFace': '3_Accessory_Accessory',
        'Nose': '2_Nose_Skin',
        'Blemish': '1_Blemish_Skin',
        'AccessoryFront': '3_Accessory_Accessory',  # Same folder as AccessoryFace - all accessories in one folder
    }

    folder = sprite_folders.get(layer_name)
    if not folder:
        return None

    # Map layer names to their sprite filename prefixes
    filename_prefixes = {
        'Background': 'bg',
        'ClothesBack': 'clothesback',
        'HairBack': 'hairback',
        'Body': 'body',
        'Clothes': 'clothes',
        'Ears': 'ears',
        'AccessoryHead': 'accessory',
        'Headshape': 'headshape',
        'DetailUpper': 'detail',  # Both detail folders use 'detail' prefix
        'DetailLower': 'detail',  # Both detail folders use 'detail' prefix
        'Hair': 'hair',
        'Mouth': 'mouth',
        'Beard': 'beard',
        'Moustache': 'moustache',
        'Eyes': 'eyes',
        'Eyebrows': 'eyebrows',
        'AccessoryFace': 'accessory',
        'Nose': 'nose',
        'Blemish': 'blemish',
        'AccessoryFront': 'accessory',
    }

    prefix = filename_prefixes.get(layer_name, layer_name.lower())
    filename = f"{prefix}_{index:02d}_{variant:02d}.png"

    full_path = os.path.join(base_path, 'PortraitSprites', folder, filename)

    return full_path if os.path.exists(full_path) else None


def render_character(character, base_path):
    """
    Render a single character portrait to a PIL Image
    Returns a CHARACTER_SIZE x CHARACTER_SIZE RGBA image
    """
    print(f'\n=== RENDERING CHARACTER ===')
    print(f'Base path: {base_path}')
    print(f'Character keys: {character.keys()}')
    print(f'Gender: {character.get("gender")}')
    print(f'Color indices: {character.get("colorIndices")}')
    print(f'Parts count: {len(character.get("parts", {}))}')
    if character.get('parts'):
        print(f'First few parts: {list(character.get("parts", {}).keys())[:5]}')

    # Create transparent canvas
    canvas = Image.new('RGBA', (CHARACTER_SIZE, CHARACTER_SIZE), (0, 0, 0, 0))

    # Get color values
    skin_color = COLOR_PALETTES['Skin'][character.get('colorIndices', {}).get('Skin', 2)]
    hair_color = COLOR_PALETTES['Hair'][character.get('colorIndices', {}).get('Hair', 3)]
    eye_color = COLOR_PALETTES['Eye'][character.get('colorIndices', {}).get('Eye', 2)]
    accessory_color = COLOR_PALETTES['Accessory'][character.get('colorIndices', {}).get('Accessory', 1)]

    gender = character.get('gender', 'Male')
    print(f'Using colors - Skin: {skin_color}, Hair: {hair_color}, Eye: {eye_color}')

    # Sort layers by ID (back to front: 20 to 0)
    sorted_layers = sorted(LAYERS.items(), key=lambda x: x[1]['id'], reverse=True)

    layers_rendered = 0
    for layer_name, layer_info in sorted_layers:
        part_data = character.get('parts', {}).get(layer_name)

        if not part_data or part_data.get('index') == -1 or part_data.get('variant') == -1:
            continue

        # Skip mouth if moustache is present
        if layer_name == 'Mouth':
            moustache = character.get('parts', {}).get('Moustache', {})
            if moustache.get('index', -1) != -1:
                continue

        # Get asset path
        asset_path = get_asset_path(
            layer_name,
            part_data.get('index', 0),
            part_data.get('variant', 0),
            gender,
            base_path
        )

        if not asset_path:
            print(f'  ERROR: No path generated for {layer_name} - index={part_data.get("index")}, variant={part_data.get("variant")}')
            continue

        if not os.path.exists(asset_path):
            print(f'  MISSING: {layer_name} - index={part_data.get("index")}, variant={part_data.get("variant")}')
            print(f'    Expected path: {asset_path}')
            continue

        # Load image
        print(f'  ✓ Loading: {layer_name} from {os.path.basename(asset_path)}')
        img = Image.open(asset_path).convert('RGBA')
        layers_rendered += 1

        # Resize to CHARACTER_SIZE if needed
        if img.size != (CHARACTER_SIZE, CHARACTER_SIZE):
            img = img.resize((CHARACTER_SIZE, CHARACTER_SIZE), Image.Resampling.LANCZOS)

        # Apply color tinting
        if layer_info['useSkinColor']:
            img = apply_color_tint(img, skin_color)
        elif layer_info['useHairColor']:
            img = apply_color_tint(img, hair_color)
        elif layer_info['useEyeColor']:
            img = apply_color_tint(img, eye_color)
        elif layer_info['useAccessoryColor']:
            img = apply_color_tint(img, accessory_color)

        # Composite onto canvas
        canvas = Image.alpha_composite(canvas, img)

    print(f'Character rendered successfully with {layers_rendered} layers')
    return canvas


def generate_postcard(color, characters, base_path):
    """
    Generate a complete postcard with multiple characters

    Args:
        color: 'blue' or 'orange'
        characters: List of character objects (max 10)
        base_path: Base path to static files

    Returns:
        PIL Image of the postcard
    """
    # Load template - use single-box template if only 1 character
    if len(characters) == 1 and color == 'blue':
        template_paths = {
            'blue': 'PostcardTemplates/goa_postcard_greetingsfromlichfield.png',
            'orange': 'PostcardTemplates/goa_postcard_greetingsfromlichfieldcrew_noboxes.png'
        }
    else:
        template_paths = {
            'blue': 'PostcardTemplates/goa_postcard_greetingsfromlichfield_noboxes_720.png',
            'orange': 'PostcardTemplates/goa_postcard_greetingsfromlichfieldcrew_noboxes.png'
        }

    template_path = os.path.join(base_path, template_paths.get(color, template_paths['blue']))

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Load and resize template to canvas size
    template = Image.open(template_path).convert('RGBA')
    if template.size != (CANVAS_WIDTH, CANVAS_HEIGHT):
        template = template.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)

    # Create postcard canvas
    postcard = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (255, 255, 255, 255))
    postcard = Image.alpha_composite(postcard, template)

    # Character slot positions
    # If single character with blue template, use larger centered slot
    if len(characters) == 1 and color == 'blue':
        slots = [
            {'x': 5.37, 'y': 8.23, 'width': 24.88, 'height': 39.44},  # Adjusted: 55,53 with size 255×254 to fit inside border
        ]
    else:
        # Multiple characters - 6 on top row, 4 on bottom row
        # Top row ends at ~80% to avoid overlapping the right edge and logo text
        slots = [
            {'x': 5.5, 'y': 5.5, 'width': 13.0, 'height': 26.0},   # Slot 1 - Top row
            {'x': 19.5, 'y': 5.5, 'width': 13.0, 'height': 26.0},  # Slot 2 - Top row
            {'x': 33.5, 'y': 5.5, 'width': 13.0, 'height': 26.0},  # Slot 3 - Top row
            {'x': 47.5, 'y': 5.5, 'width': 13.0, 'height': 26.0},  # Slot 4 - Top row
            {'x': 61.5, 'y': 5.5, 'width': 13.0, 'height': 26.0},  # Slot 5 - Top row
            {'x': 75.5, 'y': 5.5, 'width': 13.0, 'height': 26.0},  # Slot 6 - Top row (last to fit)
            {'x': 5.5, 'y': 33.0, 'width': 13.0, 'height': 26.0},  # Slot 7 - Bottom row
            {'x': 19.5, 'y': 33.0, 'width': 13.0, 'height': 26.0}, # Slot 8 - Bottom row
            {'x': 33.5, 'y': 33.0, 'width': 13.0, 'height': 26.0}, # Slot 9 - Bottom row
            {'x': 47.5, 'y': 33.0, 'width': 13.0, 'height': 26.0}  # Slot 10 - Bottom row
        ]

    # Render each character
    draw = ImageDraw.Draw(postcard)

    for i, character in enumerate(characters[:10]):  # Max 10 characters
        if i >= len(slots):
            break

        slot = slots[i]

        # Calculate slot position in pixels
        slot_x = int((slot['x'] / 100) * CANVAS_WIDTH)
        slot_y = int((slot['y'] / 100) * CANVAS_HEIGHT)
        slot_width = int((slot['width'] / 100) * CANVAS_WIDTH)
        slot_height = int((slot['height'] / 100) * CANVAS_HEIGHT)

        # For single character blue template, use full rectangular slot
        # For multiple characters, use square slots with background/border
        is_single_char = len(characters) == 1 and color == 'blue'
        print(f"\n=== CHARACTER {i} RENDERING ===")
        print(f"Characters count: {len(characters)}, Color: {color}")
        print(f"Is single character mode: {is_single_char}")

        if is_single_char:
            # Don't draw background/border - template already has it
            # Use full rectangular dimensions
            render_width = slot_width
            render_height = slot_height
            padding = 0  # No padding - fit exactly to template box
            print(f"Single character mode: NO background/border, NO padding")
        else:
            # Make slot square (use width as dimension)
            square_size = slot_width

            # Draw background box
            bg_color = (237, 231, 221, 255)  # #EDE7DD
            draw.rectangle(
                [slot_x, slot_y, slot_x + square_size, slot_y + square_size],
                fill=bg_color
            )

            # Draw border
            border_color = (200, 191, 176, 255)  # #C8BFB0
            draw.rectangle(
                [slot_x, slot_y, slot_x + square_size, slot_y + square_size],
                outline=border_color,
                width=3
            )

            render_width = square_size
            render_height = square_size
            padding = 4

        # Render character
        character_img = render_character(character, base_path)

        # Resize character to fit slot with padding
        character_img = character_img.resize(
            (render_width - padding * 2, render_height - padding * 2),
            Image.Resampling.LANCZOS
        )

        # Paste character onto postcard
        postcard.paste(
            character_img,
            (slot_x + padding, slot_y + padding),
            character_img  # Use as alpha mask
        )

    return postcard


def postcard_to_base64(postcard_image):
    """Convert PIL Image to base64 PNG string"""
    buffer = BytesIO()
    postcard_image.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')
