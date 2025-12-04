"""
Server-side postcard generation using Pillow (PIL)
Renders character portraits onto postcard templates
"""
import os
from PIL import Image, ImageDraw
from io import BytesIO
import base64

# VERSION IDENTIFIER - increment to verify module is loaded
MODULE_VERSION = "1.0.5"
print(f"postcard_generator.py MODULE_VERSION {MODULE_VERSION} loaded")

# Postcard dimensions
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 614

# Character canvas size (for rendering individual portraits)
CHARACTER_SIZE = 256

# Color palettes - MUST match frontend assetData.js exactly! Matches game's color system.
COLOR_PALETTES = {
    'Skin': [
        '#F5CCBA',  # 0
        '#E0BAB4',  # 1
        '#ECA696',  # 2
        '#CF9895',  # 3
        '#CA7E5B',  # 4
        '#9C7162',  # 5
        '#A65C3F',  # 6
        '#765543',  # 7
        '#603121',  # 8
        '#4B342E'   # 9
    ],
    'Hair': [
        '#73361F',  # 0
        '#994E2A',  # 1
        '#673719',  # 2
        '#7B511F',  # 3
        '#6F3B17',  # 4
        '#09090A',  # 5
        '#29150C',  # 6
        '#482518',  # 7
        '#684834',  # 8
        '#442B28',  # 9
        '#AE9D88',  # 10
        '#AC8C7A',  # 11
        '#8E6E51',  # 12
        '#C2A370',  # 13
        '#735145',  # 14
        '#685F5F',  # 15
        '#383434',  # 16
        '#817778'   # 17
    ],
    'Eye': [
        '#333C82',  # 0
        '#2B3041',  # 1
        '#2E2E2E',  # 2
        '#2E5224',  # 3
        '#4E5224',  # 4
        '#5B4708',  # 5
        '#5E351B',  # 6
        '#76442D',  # 7
        '#3F2417',  # 8
        '#29180F',  # 9
        '#1D0E06',  # 10
        '#261F1B'   # 11
    ],
    'Accessory': [
        '#000000',  # 0: Black
        '#6F4429',  # 1: Brown
        '#9F7F44'   # 2: Gold
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

    # Try gender-specific filename first for female characters
    if gender == 'Female':
        # For clothes layers, try _F suffix (e.g., clothes_07_00_F.png)
        if layer_name in ['Clothes', 'ClothesBack']:
            female_filename = f"{prefix}_{index:02d}_{variant:02d}_F.png"
            female_path = os.path.join(base_path, 'PortraitSprites', folder, female_filename)
            if os.path.exists(female_path):
                return female_path

        # For hair layers, try _female suffix (e.g., hair_07_00_female.png)
        if layer_name in ['Hair', 'HairBack']:
            female_filename = f"{prefix}_{index:02d}_{variant:02d}_female.png"
            female_path = os.path.join(base_path, 'PortraitSprites', folder, female_filename)
            if os.path.exists(female_path):
                return female_path

    # Fall back to base filename (for male or unisex sprites)
    filename = f"{prefix}_{index:02d}_{variant:02d}.png"
    full_path = os.path.join(base_path, 'PortraitSprites', folder, filename)

    return full_path if os.path.exists(full_path) else None


def render_character(character, base_path, size=None):
    """
    Render a single character portrait to a PIL Image
    Returns a CHARACTER_SIZE x CHARACTER_SIZE RGBA image (or custom size if specified)

    Args:
        character: Character data dict
        base_path: Base path to static files
        size: Optional custom size (defaults to CHARACTER_SIZE)
    """
    if size is None:
        size = CHARACTER_SIZE

    print(f'\n=== RENDERING CHARACTER ===')
    print(f'Base path: {base_path}')
    print(f'Character keys: {character.keys()}')
    print(f'Gender: {character.get("gender")}')
    print(f'Color indices: {character.get("colorIndices")}')
    print(f'Parts count: {len(character.get("parts", {}))}')
    if character.get('parts'):
        print(f'First few parts: {list(character.get("parts", {}).keys())[:5]}')

    # Create transparent canvas
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))

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

        # Resize to target size if needed
        if img.size != (size, size):
            img = img.resize((size, size), Image.Resampling.LANCZOS)

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
    # If single character, use larger centered slot (different positioning for blue vs orange)
    if len(characters) == 1:
        if color == 'blue':
            slots = [
                {'x': 4.8, 'y': 8.8, 'width': 25.4, 'height': 41.5},  # Blue template box: centered in upper-left tan box
            ]
        else:  # orange
            slots = [
                {'x': 18.0, 'y': 32.0, 'width': 30.0, 'height': 30.0},  # Orange template box: centered in white box on left
            ]
    else:
        # Multiple characters - 3 per row layout with much larger portraits
        # Taking up more of the left side of the postcard
        slots = [
            {'x': 2.0, 'y': 5.0, 'width': 28.0, 'height': 28.0},   # Slot 1 - Top row
            {'x': 32.0, 'y': 5.0, 'width': 28.0, 'height': 28.0},  # Slot 2 - Top row
            {'x': 2.0, 'y': 36.0, 'width': 28.0, 'height': 28.0},  # Slot 3 - Middle row
            {'x': 32.0, 'y': 36.0, 'width': 28.0, 'height': 28.0}, # Slot 4 - Middle row
            {'x': 2.0, 'y': 67.0, 'width': 28.0, 'height': 28.0},  # Slot 5 - Bottom row
            {'x': 32.0, 'y': 67.0, 'width': 28.0, 'height': 28.0}, # Slot 6 - Bottom row
            {'x': 17.0, 'y': 5.0, 'width': 28.0, 'height': 28.0},  # Slot 7 - Extra
            {'x': 17.0, 'y': 36.0, 'width': 28.0, 'height': 28.0}, # Slot 8 - Extra
            {'x': 17.0, 'y': 67.0, 'width': 28.0, 'height': 28.0}, # Slot 9 - Extra
            {'x': 47.0, 'y': 36.0, 'width': 28.0, 'height': 28.0}  # Slot 10 - Extra
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

        # For single character templates (both blue and orange), don't draw background/border
        # For multiple characters, use square slots with background/border
        is_single_char = len(characters) == 1
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
