"""
Character generation logic for WW2 aviation game
Ported from frontend/src/lib/assetData.js
"""
import random
import uuid

# Body shape options
BODY_SHAPES = [
    {'index': 3, 'name': 'Thin'},
    {'index': 2, 'name': 'Average'},
    {'index': 1, 'name': 'Bulky'},
    {'index': 0, 'name': 'Fat'}
]

# Color palettes - Matches game's color system exactly
COLOR_PALETTES = {
    'Skin': [
        {'index': 0, 'name': 'Skin 0', 'hex': '#F5CCBA'},
        {'index': 1, 'name': 'Skin 1', 'hex': '#E0BAB4'},
        {'index': 2, 'name': 'Skin 2', 'hex': '#ECA696'},
        {'index': 3, 'name': 'Skin 3', 'hex': '#CF9895'},
        {'index': 4, 'name': 'Skin 4', 'hex': '#CA7E5B'},
        {'index': 5, 'name': 'Skin 5', 'hex': '#9C7162'},
        {'index': 6, 'name': 'Skin 6', 'hex': '#A65C3F'},
        {'index': 7, 'name': 'Skin 7', 'hex': '#765543'},
        {'index': 8, 'name': 'Skin 8', 'hex': '#603121'},
        {'index': 9, 'name': 'Skin 9', 'hex': '#4B342E'}
    ],
    'Hair': [
        {'index': 0, 'name': 'Hair 0', 'hex': '#73361F'},
        {'index': 1, 'name': 'Hair 1', 'hex': '#994E2A'},
        {'index': 2, 'name': 'Hair 2', 'hex': '#673719'},
        {'index': 3, 'name': 'Hair 3', 'hex': '#7B511F'},
        {'index': 4, 'name': 'Hair 4', 'hex': '#6F3B17'},
        {'index': 5, 'name': 'Hair 5', 'hex': '#09090A'},
        {'index': 6, 'name': 'Hair 6', 'hex': '#29150C'},
        {'index': 7, 'name': 'Hair 7', 'hex': '#482518'},
        {'index': 8, 'name': 'Hair 8', 'hex': '#684834'},
        {'index': 9, 'name': 'Hair 9', 'hex': '#442B28'},
        {'index': 10, 'name': 'Hair 10', 'hex': '#AE9D88'},
        {'index': 11, 'name': 'Hair 11', 'hex': '#AC8C7A'},
        {'index': 12, 'name': 'Hair 12', 'hex': '#8E6E51'},
        {'index': 13, 'name': 'Hair 13', 'hex': '#C2A370'},
        {'index': 14, 'name': 'Hair 14', 'hex': '#735145'},
        {'index': 15, 'name': 'Hair 15', 'hex': '#685F5F'},
        {'index': 16, 'name': 'Hair 16', 'hex': '#383434'},
        {'index': 17, 'name': 'Hair 17', 'hex': '#817778'}
    ],
    'Eye': [
        {'index': 0, 'name': 'Eye 0', 'hex': '#333C82'},
        {'index': 1, 'name': 'Eye 1', 'hex': '#2B3041'},
        {'index': 2, 'name': 'Eye 2', 'hex': '#2E2E2E'},
        {'index': 3, 'name': 'Eye 3', 'hex': '#2E5224'},
        {'index': 4, 'name': 'Eye 4', 'hex': '#4E5224'},
        {'index': 5, 'name': 'Eye 5', 'hex': '#5B4708'},
        {'index': 6, 'name': 'Eye 6', 'hex': '#5E351B'},
        {'index': 7, 'name': 'Eye 7', 'hex': '#76442D'},
        {'index': 8, 'name': 'Eye 8', 'hex': '#3F2417'},
        {'index': 9, 'name': 'Eye 9', 'hex': '#29180F'},
        {'index': 10, 'name': 'Eye 10', 'hex': '#1D0E06'},
        {'index': 11, 'name': 'Eye 11', 'hex': '#261F1B'}
    ],
    'Accessory': [
        {'index': 0, 'name': 'Black', 'hex': '#000000'},
        {'index': 1, 'name': 'Brown', 'hex': '#6F4429'},
        {'index': 2, 'name': 'Gold', 'hex': '#9F7F44'}
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


def get_clothes_for_class_job_gender(character_class, job, gender):
    """
    Get clothes sprites based on Class, Job, and Gender

    Args:
        character_class: 'AirCrew' or 'BaseCrew'
        job: Job for BaseCrew: 'None', 'AAFCook', 'FieldMechanic', 'FieldEngineer', 'RAFMedic', 'AAFLabour'
        gender: 'Male' or 'Female'

    Returns:
        dict: {'clothes': {'index': int, 'variant': int}, 'clothesBack': {'index': int, 'variant': int}}
    """
    # AirCrew always gets clothes_01_00.png and clothesback_14_00.png
    if character_class == 'AirCrew':
        return {
            'clothes': {'index': 1, 'variant': 0},
            'clothesBack': {'index': 14, 'variant': 0}
        }

    # BaseCrew clothing depends on Job and Gender
    clothes_map = {
        'Male': {
            'None': {'index': 0, 'variant': 0},          # clothes_00_00.png
            'AAFCook': {'index': 2, 'variant': 0},       # clothes_02_00.png
            'FieldMechanic': {'index': 3, 'variant': 0}, # clothes_03_00.png
            'FieldEngineer': {'index': 4, 'variant': 0}, # clothes_04_00.png
            'RAFMedic': {'index': 5, 'variant': 0},      # clothes_05_00.png
            'AAFLabour': {'index': 6, 'variant': 0}      # clothes_06_00.png
        },
        'Female': {
            'AAFCook': {'index': 7, 'variant': 0},       # clothes_07_00_F.png
            'FieldEngineer': {'index': 8, 'variant': 0}, # clothes_08_00_F.png
            'AAFLabour': {'index': 9, 'variant': 0},     # clothes_09_00_F.png
            'FieldMechanic': {'index': 10, 'variant': 0},# clothes_10_00_F.png
            'RAFMedic': {'index': 11, 'variant': 0},     # clothes_11_00_F.png
            'None': {'index': 12, 'variant': 0}          # clothes_12_00_F.png
        }
    }

    clothes = clothes_map.get(gender, {}).get(job) or clothes_map.get(gender, {}).get('None') or {'index': 0, 'variant': 0}

    # ClothesBack: Only Male BaseCrew with Job=None gets clothesback_00_00.png
    # All other BaseCrew get no ClothesBack (index: -1)
    if gender == 'Male' and job == 'None':
        clothes_back = {'index': 0, 'variant': 0}  # clothesback_00_00.png
    else:
        clothes_back = {'index': -1, 'variant': -1}  # No ClothesBack

    return {'clothes': clothes, 'clothesBack': clothes_back}


def generate_random_character(gender='Male', skin_color_range=None):
    """
    Generate random character data

    Args:
        gender: 'Male' or 'Female'
        skin_color_range: Tuple of (min, max) skin color indices, default (0, 9)

    Returns:
        dict: Character data with gender, bodyShapeIndex, colorIndices, and parts
    """
    if skin_color_range is None:
        skin_color_range = (0, len(COLOR_PALETTES['Skin']) - 1)

    # Pick random skin color with weighted distribution
    # 90% chance for lighter tones (0-4), 10% chance for darker tones (5-9)
    min_skin = max(0, skin_color_range[0])
    max_skin = min(len(COLOR_PALETTES['Skin']) - 1, skin_color_range[1])

    if max_skin <= 4:
        # If range doesn't include darker tones, pick uniformly
        skin_color_index = random.randint(min_skin, max_skin)
    elif min_skin >= 5:
        # If range only includes darker tones, pick uniformly
        skin_color_index = random.randint(min_skin, max_skin)
    else:
        # Range includes both lighter and darker tones, use weighted distribution
        if random.random() < 0.9:
            # 90% chance: pick from lighter tones (0-4)
            lighter_max = min(4, max_skin)
            skin_color_index = random.randint(min_skin, lighter_max)
        else:
            # 10% chance: pick from darker tones (5-9)
            darker_min = max(5, min_skin)
            skin_color_index = random.randint(darker_min, max_skin)

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

    # Probability weights for optional features (matching in-game generator)
    FEATURE_PROBABILITIES = {
        'Moustache': 0.50,      # 50% - Matches in-game generator
        'Beard': 0.10,          # 10% - Matches in-game generator
        'AccessoryFace': 0.50,  # 50% - Glasses/monocle (matches in-game accessories)
        'AccessoryFront': 0.50, # 50% - Pipe (matches in-game accessories)
        'AccessoryHead': 0.50,  # 50% - Hats, etc. (matches in-game accessories)
        'Blemish': 0.15,        # 15% - Scars, marks
        'DetailUpper': 0.20,    # 20% - Wrinkles, etc.
        'DetailLower': 0.20,    # 20% - Chin details
        'Background': 0.80      # 80% - Usually want background
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
        # Optional layers use specific probabilities
        if not layer.get('canBeNone'):
            should_add = True
        else:
            probability = FEATURE_PROBABILITIES.get(layer_name, 0.3)
            should_add = random.random() < probability

        if should_add:
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
