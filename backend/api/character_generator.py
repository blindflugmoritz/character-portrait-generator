"""
Character generation logic for WW2 aviation game
Ported from frontend/src/lib/assetData.js
"""
import random
import uuid

# Body shape options
BODY_SHAPES = [
    {'index': 0, 'name': 'Thin'},
    {'index': 1, 'name': 'Average'},
    {'index': 2, 'name': 'Bulky'},
    {'index': 3, 'name': 'Fat'}
]

# Color palettes
COLOR_PALETTES = {
    'Skin': [
        {'index': 0, 'name': 'Very Light', 'hex': '#FFE0BD'},
        {'index': 1, 'name': 'Light', 'hex': '#FFCD94'},
        {'index': 2, 'name': 'Light Medium', 'hex': '#EAC086'},
        {'index': 3, 'name': 'Medium', 'hex': '#C68642'},
        {'index': 4, 'name': 'Olive', 'hex': '#A67C52'},
        {'index': 5, 'name': 'Brown', 'hex': '#8D5524'},
        {'index': 6, 'name': 'Dark Brown', 'hex': '#664229'}
    ],
    'Hair': [
        {'index': 0, 'name': 'Platinum Blonde', 'hex': '#F5F5DC'},
        {'index': 1, 'name': 'Blonde', 'hex': '#E5C18A'},
        {'index': 2, 'name': 'Light Brown', 'hex': '#A67C52'},
        {'index': 3, 'name': 'Brown', 'hex': '#6E4A2D'},
        {'index': 4, 'name': 'Dark Brown', 'hex': '#4A2C1C'},
        {'index': 5, 'name': 'Black', 'hex': '#1C1C1C'},
        {'index': 6, 'name': 'Auburn', 'hex': '#8B4513'},
        {'index': 7, 'name': 'Red', 'hex': '#C85A32'}
    ],
    'Eye': [
        {'index': 0, 'name': 'Blue', 'hex': '#5A9BCF'},
        {'index': 1, 'name': 'Green', 'hex': '#5FA777'},
        {'index': 2, 'name': 'Brown', 'hex': '#6E4A2D'},
        {'index': 3, 'name': 'Hazel', 'hex': '#8D6E49'},
        {'index': 4, 'name': 'Gray', 'hex': '#8FA8B0'},
        {'index': 5, 'name': 'Amber', 'hex': '#D4A650'}
    ],
    'Accessory': [
        {'index': 0, 'name': 'Black', 'hex': '#1C1C1C'},
        {'index': 1, 'name': 'Brown', 'hex': '#6E4A2D'},
        {'index': 2, 'name': 'Gray', 'hex': '#808080'},
        {'index': 3, 'name': 'Silver', 'hex': '#C0C0C0'},
        {'index': 4, 'name': 'Gold', 'hex': '#FFD700'}
    ]
}

# Layer definitions
LAYERS = {
    'Background': {'id': 20, 'folder': '20_Background_Background', 'category': 'Background', 'canBeNone': True},
    'ClothesBack': {'id': 19, 'folder': '19_ClothesBack_Clothes', 'category': 'Clothes', 'canBeNone': False},
    'HairBack': {'id': 18, 'folder': '18_HairBack_Hair', 'category': 'Hair', 'canBeNone': True, 'useHairColor': True},
    'Body': {'id': 17, 'folder': '17_Body_Skin', 'category': 'Skin', 'canBeNone': False, 'useSkinColor': True},
    'Clothes': {'id': 16, 'folder': '16_Clothes_Clothes', 'category': 'Clothes', 'canBeNone': False},
    'Ears': {'id': 15, 'folder': '15_Ears_Skin', 'category': 'Skin', 'canBeNone': False, 'useSkinColor': True},
    'AccessoryHead': {'id': 14, 'folder': '14_Accessory_Accessory', 'category': 'Accessory', 'canBeNone': True, 'useAccessoryColor': True},
    'Headshape': {'id': 13, 'folder': '13_Headshape_Skin', 'category': 'Skin', 'canBeNone': False, 'useSkinColor': True},
    'DetailUpper': {'id': 12, 'folder': '12_Detail_Skin', 'category': 'Skin', 'canBeNone': True, 'useSkinColor': True},
    'DetailLower': {'id': 11, 'folder': '11_Detail_Skin', 'category': 'Skin', 'canBeNone': True, 'useSkinColor': True},
    'Hair': {'id': 10, 'folder': '10_Hair_Hair', 'category': 'Hair', 'canBeNone': False, 'useHairColor': True},
    'Mouth': {'id': 9, 'folder': '9_Mouth_Lip', 'category': 'Lip', 'canBeNone': True},
    'Beard': {'id': 8, 'folder': '8_Beard_Hair', 'category': 'Hair', 'canBeNone': True, 'useHairColor': True},
    'Moustache': {'id': 7, 'folder': '7_Moustache_Hair', 'category': 'Hair', 'canBeNone': True, 'useHairColor': True},
    'Eyes': {'id': 5, 'folder': '5_Eyes_Eye', 'category': 'Eye', 'canBeNone': False, 'useEyeColor': True},
    'Eyebrows': {'id': 4, 'folder': '4_Eyebrows_Hair', 'category': 'Hair', 'canBeNone': False, 'useHairColor': True},
    'AccessoryFace': {'id': 3, 'folder': '3_Accessory_Accessory', 'category': 'Accessory', 'canBeNone': True, 'useAccessoryColor': True},
    'Nose': {'id': 2, 'folder': '2_Nose_Skin', 'category': 'Skin', 'canBeNone': False, 'useSkinColor': True},
    'Blemish': {'id': 1, 'folder': '1_Blemish_Skin', 'category': 'Skin', 'canBeNone': True, 'useSkinColor': True},
    'AccessoryFront': {'id': 0, 'folder': '0_Accessory_Accessory', 'category': 'Accessory', 'canBeNone': True, 'useAccessoryColor': True}
}

# Asset variants (simplified - includes commonly available indices)
ASSET_VARIANTS = {
    'Accessory': {'variants': {0: 4, 1: 1, 2: 4, 3: 1}},
    'Beard': {'variants': {0: 3, 20: 1}},
    'Blemish': {'variants': {0: 1, 1: 1, 2: 1}},
    'Body': {'variants': {0: 1, 1: 1}},
    'Clothes': {
        'variants': {0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1},
        'femaleOnlyIndices': [7, 8, 9, 10, 11, 12]
    },
    'ClothesBack': {'variants': {0: 1, 14: 1}},
    'Detail': {'variants': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 10: 1, 11: 1}},
    'Ears': {'variants': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}},
    'Eyebrows': {'variants': {0: 1, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2}},
    'Eyes': {'variants': {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2}},
    'Hair': {
        'variants': {0: 2, 1: 2, 2: 2, 3: 3, 4: 2, 5: 3, 6: 3, 7: 4, 8: 3, 9: 2, 10: 3, 11: 3},
        'genderSpecific': {0: True, 1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True, 10: True, 11: True}
    },
    'HairBack': {
        'variants': {0: 1, 5: 1, 7: 4},
        'femaleOnlyIndices': [7]
    },
    'Headshape': {'variants': {0: 2, 1: 2, 2: 2, 3: 2, 4: 2}},
    'Mouth': {'variants': {0: 2, 1: 2, 2: 2, 3: 2, 4: 2}},
    'Moustache': {'variants': {0: 1, 1: 1, 2: 1}},
    'Nose': {'variants': {0: 2, 1: 2, 2: 2, 3: 2}},
    'Background': {'variants': {0: 1, 1: 1, 2: 1, 3: 1}}
}

# Clothes to ClothesBack mapping
CLOTHES_BACK_MAPPING = {
    0: 0,
    1: 14
}

# Layer to variant key mapping
LAYER_TO_VARIANT_KEY = {
    'AccessoryFront': 'Accessory',
    'AccessoryFace': 'Accessory',
    'AccessoryHead': 'Accessory',
    'Beard': 'Beard',
    'Blemish': 'Blemish',
    'Body': 'Body',
    'Clothes': 'Clothes',
    'ClothesBack': 'ClothesBack',
    'DetailLower': 'Detail',
    'DetailUpper': 'Detail',
    'Ears': 'Ears',
    'Eyebrows': 'Eyebrows',
    'Eyes': 'Eyes',
    'Hair': 'Hair',
    'HairBack': 'HairBack',
    'Headshape': 'Headshape',
    'Mouth': 'Mouth',
    'Moustache': 'Moustache',
    'Nose': 'Nose',
    'Background': 'Background'
}


def get_available_indices(layer_name, gender=None):
    """Get available indices for a layer"""
    variant_key = LAYER_TO_VARIANT_KEY.get(layer_name)
    asset_data = ASSET_VARIANTS.get(variant_key)

    if not asset_data or 'variants' not in asset_data:
        return []

    indices = sorted(list(asset_data['variants'].keys()))

    # Filter out female-only indices for Male characters
    if gender == 'Male' and 'femaleOnlyIndices' in asset_data:
        indices = [idx for idx in indices if idx not in asset_data['femaleOnlyIndices']]

    return indices


def get_available_variants(layer_name, index, gender=None):
    """Get available variants for a specific index"""
    variant_key = LAYER_TO_VARIANT_KEY.get(layer_name)
    asset_data = ASSET_VARIANTS.get(variant_key)

    if not asset_data or 'variants' not in asset_data or index not in asset_data['variants']:
        return []

    variant_data = asset_data['variants'][index]

    # Handle both array format and number format
    if isinstance(variant_data, list):
        variants = list(variant_data)
    else:
        variants = list(range(variant_data))

    return variants


def get_matching_hairback_indices(hair_index, gender=None):
    """Get matching HairBack indices for a given Hair index"""
    hairback_indices = get_available_indices('HairBack', gender)
    return [idx for idx in hairback_indices if idx == hair_index]


def generate_random_character(gender='Male', skin_color_range=None):
    """
    Generate random character data

    Args:
        gender: 'Male' or 'Female'
        skin_color_range: Tuple of (min, max) skin color indices, default (0, 6)

    Returns:
        dict: Character data with gender, bodyShapeIndex, colorIndices, and parts
    """
    if skin_color_range is None:
        skin_color_range = (0, len(COLOR_PALETTES['Skin']) - 1)

    # Pick random skin color within allowed range
    min_skin = max(0, skin_color_range[0])
    max_skin = min(len(COLOR_PALETTES['Skin']) - 1, skin_color_range[1])
    skin_color_index = random.randint(min_skin, max_skin)

    character = {
        'gender': gender,
        'bodyShapeIndex': random.randint(0, len(BODY_SHAPES) - 1),
        'colorIndices': {
            'Skin': skin_color_index,
            'Hair': random.randint(0, len(COLOR_PALETTES['Hair']) - 1),
            'Eye': random.randint(0, len(COLOR_PALETTES['Eye']) - 1),
            'Accessory': random.randint(0, len(COLOR_PALETTES['Accessory']) - 1)
        },
        'parts': {}
    }

    # First pass: Add each layer (except Mouth, ClothesBack, and HairBack which have dependencies)
    for layer_name, layer in LAYERS.items():
        if layer_name in ['Mouth', 'ClothesBack', 'HairBack']:
            continue

        # Skip facial hair for females
        if gender == 'Female' and layer_name in ['Beard', 'Moustache']:
            character['parts'][layer_name] = {'index': -1, 'variant': -1}
            continue

        # Required layers always get a value
        if not layer.get('canBeNone') or random.random() > 0.3:
            indices = get_available_indices(layer_name, gender)
            if indices:
                random_index = random.choice(indices)
                variants = get_available_variants(layer_name, random_index, gender)
                if variants:
                    random_variant = random.choice(variants)
                    character['parts'][layer_name] = {'index': random_index, 'variant': random_variant}
                else:
                    character['parts'][layer_name] = {'index': -1, 'variant': -1}
            else:
                character['parts'][layer_name] = {'index': -1, 'variant': -1}
        else:
            character['parts'][layer_name] = {'index': -1, 'variant': -1}

    # Handle ClothesBack: Set based on Clothes selection
    clothes_index = character['parts'].get('Clothes', {}).get('index')
    if clothes_index is not None and clothes_index != -1:
        clothes_back_index = CLOTHES_BACK_MAPPING.get(clothes_index)
        if clothes_back_index is not None:
            character['parts']['ClothesBack'] = {'index': clothes_back_index, 'variant': 0}
        else:
            # If no mapping exists, set a random ClothesBack
            indices = get_available_indices('ClothesBack', gender)
            if indices:
                character['parts']['ClothesBack'] = {'index': random.choice(indices), 'variant': 0}
            else:
                character['parts']['ClothesBack'] = {'index': -1, 'variant': -1}
    else:
        character['parts']['ClothesBack'] = {'index': -1, 'variant': -1}

    # Handle Mouth: Only add if Moustache is -1
    has_moustache = character['parts'].get('Moustache', {}).get('index', -1) != -1
    if not has_moustache:
        # Mouth can be present (70% chance) when no moustache
        if random.random() > 0.3:
            indices = get_available_indices('Mouth', gender)
            if indices:
                random_index = random.choice(indices)
                variants = get_available_variants('Mouth', random_index, gender)
                if variants:
                    character['parts']['Mouth'] = {'index': random_index, 'variant': random.choice(variants)}
                else:
                    character['parts']['Mouth'] = {'index': -1, 'variant': -1}
            else:
                character['parts']['Mouth'] = {'index': -1, 'variant': -1}
        else:
            character['parts']['Mouth'] = {'index': -1, 'variant': -1}
    else:
        character['parts']['Mouth'] = {'index': -1, 'variant': -1}

    # Handle HairBack: Set based on Hair selection (matching identification numbers)
    hair_index = character['parts'].get('Hair', {}).get('index')
    if hair_index is not None and hair_index != -1:
        matching_hairback_indices = get_matching_hairback_indices(hair_index, gender)
        if matching_hairback_indices and random.random() > 0.3:
            # 70% chance to add matching HairBack if available
            random_index = random.choice(matching_hairback_indices)
            variants = get_available_variants('HairBack', random_index, gender)
            if variants:
                character['parts']['HairBack'] = {'index': random_index, 'variant': random.choice(variants)}
            else:
                character['parts']['HairBack'] = {'index': -1, 'variant': -1}
        else:
            character['parts']['HairBack'] = {'index': -1, 'variant': -1}
    else:
        character['parts']['HairBack'] = {'index': -1, 'variant': -1}

    return character
