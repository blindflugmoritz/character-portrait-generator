"""
Photo matching logic - maps detected facial features to sprite assets
"""
import json
import os
from .character_generator import (
    LAYERS, COLOR_PALETTES,
    get_available_indices, get_available_variants,
    get_matching_hairback_indices
)


def load_sprite_metadata():
    """Load sprite metadata from JSON file"""
    metadata_path = os.path.join(os.path.dirname(__file__), 'sprite-metadata.json')
    with open(metadata_path, 'r') as f:
        return json.load(f)


def match_features_to_sprites(detected_features):
    """
    Match detected features from photo to sprite metadata
    Priority: Face Shape > Hair > Skin Tone > Other features

    Args:
        detected_features: Features detected by Claude Vision API

    Returns:
        dict: Character configuration
    """
    sprite_metadata = load_sprite_metadata()

    gender = map_gender(detected_features.get('gender_presentation', 'Male'))

    character = {
        'gender': gender,
        'bodyShapeIndex': 1,  # Default to average
        'colorIndices': {
            'Skin': match_skin_tone(detected_features.get('skin_tone')),
            'Hair': match_hair_color(detected_features.get('hair', {}).get('color', 'black')),
            'Eye': match_eye_color(detected_features.get('eyes', {}).get('color', 'brown')),
            'Accessory': 0  # Default to black
        },
        'parts': {},
        'matchConfidence': {}
    }

    # Priority 1: Face Shape (most important)
    headshape_match = match_headshape(
        detected_features.get('face_shape'),
        detected_features.get('face_characteristics', []),
        gender,
        sprite_metadata
    )
    character['parts']['Headshape'] = {'index': headshape_match['index'], 'variant': headshape_match['variant']}
    character['matchConfidence']['Headshape'] = headshape_match['confidence']

    # Priority 2: Hair
    hair_data = detected_features.get('hair', {})
    if hair_data.get('present') and hair_data.get('length') != 'bald':
        hair_match = match_hair(hair_data, gender, sprite_metadata)
        character['parts']['Hair'] = {'index': hair_match['index'], 'variant': hair_match['variant']}
        character['matchConfidence']['Hair'] = hair_match['confidence']

        # Match HairBack if Hair exists
        matching_hairback = get_matching_hairback_indices(hair_match['index'], gender)
        if matching_hairback:
            character['parts']['HairBack'] = {'index': matching_hairback[0], 'variant': 0}
        else:
            character['parts']['HairBack'] = {'index': -1, 'variant': -1}
    else:
        # Bald
        character['parts']['Hair'] = {'index': 4, 'variant': 0}
        character['parts']['HairBack'] = {'index': 4, 'variant': 0}
        character['matchConfidence']['Hair'] = 1.0

    # Priority 3: Nose
    nose_match = match_nose(detected_features.get('nose', {}), gender, sprite_metadata)
    character['parts']['Nose'] = {'index': nose_match['index'], 'variant': nose_match['variant']}
    character['matchConfidence']['Nose'] = nose_match['confidence']

    # Eyes
    eyes_match = match_eyes(detected_features.get('eyes', {}), gender, sprite_metadata)
    character['parts']['Eyes'] = {'index': eyes_match['index'], 'variant': eyes_match['variant']}
    character['matchConfidence']['Eyes'] = eyes_match['confidence']

    # Mouth
    mouth_match = match_mouth(detected_features.get('mouth', {}), sprite_metadata)
    character['parts']['Mouth'] = {'index': mouth_match['index'], 'variant': mouth_match['variant']}
    character['matchConfidence']['Mouth'] = mouth_match['confidence']

    # Eyebrows (default for now)
    character['parts']['Eyebrows'] = {'index': 0, 'variant': 0}

    # Facial hair (only for males)
    if gender == 'Male':
        facial_hair = detected_features.get('facial_hair', {})
        beard_match = match_beard(facial_hair.get('beard', 'none'), sprite_metadata)
        character['parts']['Beard'] = {'index': beard_match['index'], 'variant': beard_match['variant']}

        mustache_match = match_mustache(facial_hair.get('mustache', 'none'), sprite_metadata)
        character['parts']['Moustache'] = {'index': mustache_match['index'], 'variant': mustache_match['variant']}

        # Clear mouth if mustache present
        if character['parts']['Moustache']['index'] != -1:
            character['parts']['Mouth'] = {'index': -1, 'variant': -1}
    else:
        character['parts']['Beard'] = {'index': -1, 'variant': -1}
        character['parts']['Moustache'] = {'index': -1, 'variant': -1}

    # Accessories
    accessory_match = match_accessories(detected_features.get('accessories', {}), gender, sprite_metadata)
    character['parts']['AccessoryFace'] = {'index': accessory_match['index'], 'variant': accessory_match['variant']}
    character['parts']['AccessoryHead'] = {'index': -1, 'variant': -1}
    character['parts']['AccessoryFront'] = {'index': -1, 'variant': -1}

    # Age markers / Details
    age_markers = detected_features.get('age_markers', {})
    detail_upper_match = match_age_markers(age_markers, 'upper', sprite_metadata)
    detail_lower_match = match_age_markers(age_markers, 'lower', sprite_metadata)
    character['parts']['DetailUpper'] = {'index': detail_upper_match['index'], 'variant': detail_upper_match['variant']}
    character['parts']['DetailLower'] = {'index': detail_lower_match['index'], 'variant': detail_lower_match['variant']}

    # Blemishes
    blemish_match = match_blemishes(detected_features.get('accessories', {}).get('other', []), sprite_metadata)
    character['parts']['Blemish'] = {'index': blemish_match['index'], 'variant': blemish_match['variant']}

    # Required body parts
    character['parts']['Body'] = {'index': 0, 'variant': 0}
    character['parts']['Ears'] = {'index': 0, 'variant': 0}

    # Clothes (default)
    character['parts']['Clothes'] = {'index': 0, 'variant': 0}
    character['parts']['ClothesBack'] = {'index': 0, 'variant': 0}

    # Background (none)
    character['parts']['Background'] = {'index': -1, 'variant': -1}

    return character


def map_gender(gender_presentation):
    """Map gender presentation to Male/Female"""
    if gender_presentation == 'Female':
        return 'Female'
    return 'Male'


def match_skin_tone(detected_tone):
    """Match skin tone to color index"""
    tone_map = {
        'very light': 0,
        'light': 1,
        'light medium': 2,
        'medium': 3,
        'olive': 4,
        'brown': 5,
        'dark brown': 6
    }
    return tone_map.get(detected_tone.lower() if detected_tone else '', 2)


def match_hair_color(detected_color):
    """Match hair color to color index"""
    color_map = {
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
    }
    return color_map.get(detected_color.lower() if detected_color else '', 3)


def match_eye_color(detected_color):
    """Match eye color to color index"""
    color_map = {
        'blue': 0,
        'green': 1,
        'brown': 2,
        'hazel': 3,
        'gray': 4,
        'amber': 5
    }
    return color_map.get(detected_color.lower() if detected_color else '', 2)


def match_headshape(face_shape, characteristics, gender, sprite_metadata):
    """Match headshape using tag-based matching"""
    detected_terms = [face_shape] + (characteristics or [])
    return match_layer_by_tags('Headshape', detected_terms, gender, sprite_metadata)


def match_hair(hair_data, gender, sprite_metadata):
    """Match hair using tag-based matching"""
    detected_terms = [
        hair_data.get('length'),
        hair_data.get('style'),
    ] + (hair_data.get('characteristics') or [])
    detected_terms = [t for t in detected_terms if t]
    return match_layer_by_tags('Hair', detected_terms, gender, sprite_metadata)


def match_nose(nose_data, gender, sprite_metadata):
    """Match nose using tag-based matching"""
    detected_terms = [
        nose_data.get('size'),
        nose_data.get('shape'),
        nose_data.get('bridge'),
    ] + (nose_data.get('characteristics') or [])
    detected_terms = [t for t in detected_terms if t]
    return match_layer_by_tags('Nose', detected_terms, gender, sprite_metadata)


def match_eyes(eyes_data, gender, sprite_metadata):
    """Match eyes using tag-based matching"""
    detected_terms = [eyes_data.get('shape'), eyes_data.get('size')]
    detected_terms = [t for t in detected_terms if t]
    return match_layer_by_tags('Eyes', detected_terms, gender, sprite_metadata)


def match_mouth(mouth_data, sprite_metadata):
    """Match mouth using tag-based matching"""
    detected_terms = [mouth_data.get('shape'), mouth_data.get('expression')]
    detected_terms = [t for t in detected_terms if t]
    return match_layer_by_tags('Mouth', detected_terms, None, sprite_metadata)


def match_beard(beard_type, sprite_metadata):
    """Match beard"""
    if beard_type == 'none':
        return {'index': -1, 'variant': -1, 'confidence': 1.0}

    beard_map = {
        'stubble': {'index': -1, 'variant': -1},
        'goatee': {'index': 20, 'variant': 0},
        'full': {'index': 0, 'variant': 0}
    }

    match = beard_map.get(beard_type, {'index': -1, 'variant': -1})
    return {**match, 'confidence': 0.8}


def match_mustache(mustache_type, sprite_metadata):
    """Match mustache"""
    if mustache_type == 'none':
        return {'index': -1, 'variant': -1, 'confidence': 1.0}

    mustache_map = {
        'thin': {'index': 0, 'variant': 1},
        'handlebar': {'index': 1, 'variant': 0},
        'chevron': {'index': 2, 'variant': 0},
        'walrus': {'index': 3, 'variant': 0}
    }

    match = mustache_map.get(mustache_type, {'index': 0, 'variant': 0})
    return {**match, 'confidence': 0.8}


def match_accessories(accessories_data, gender, sprite_metadata):
    """Match accessories (glasses, etc.)"""
    glasses_type = accessories_data.get('glasses')

    if not glasses_type or glasses_type == 'none':
        return {'index': -1, 'variant': -1, 'confidence': 1.0}

    glasses_map = {
        'monocle': {'index': 1, 'variant': 0},
        'round': {'index': 2, 'variant': 0},
        'rectangular': {'index': 2, 'variant': 3}
    }

    match = glasses_map.get(glasses_type, {'index': 2, 'variant': 0})
    return {**match, 'confidence': 0.9}


def match_age_markers(age_markers, position, sprite_metadata):
    """Match age markers (wrinkles, details)"""
    wrinkle_level = age_markers.get('wrinkles', 'none')

    if wrinkle_level == 'none' or age_markers.get('apparent_age') == 'young':
        return {'index': -1, 'variant': -1, 'confidence': 1.0}

    if position == 'upper':
        if wrinkle_level == 'prominent':
            return {'index': 0, 'variant': 0, 'confidence': 0.7}
        elif wrinkle_level == 'moderate':
            return {'index': 1, 'variant': 0, 'confidence': 0.6}
    else:
        if wrinkle_level == 'prominent':
            return {'index': 14, 'variant': 0, 'confidence': 0.7}
        elif wrinkle_level == 'moderate':
            return {'index': 10, 'variant': 0, 'confidence': 0.6}

    return {'index': -1, 'variant': -1, 'confidence': 1.0}


def match_blemishes(other_accessories, sprite_metadata):
    """Match blemishes (scars, beauty marks)"""
    if not other_accessories:
        return {'index': -1, 'variant': -1, 'confidence': 1.0}

    has_scar = any('scar' in item.lower() for item in other_accessories)

    if has_scar:
        return {'index': 0, 'variant': 0, 'confidence': 0.8}

    return {'index': -1, 'variant': -1, 'confidence': 1.0}


def match_layer_by_tags(layer_name, detected_terms, gender, sprite_metadata):
    """
    Generic tag-based matching for any layer
    Compares detected terms with sprite metadata tags
    """
    layer = LAYERS.get(layer_name)
    if not layer:
        print(f'Layer {layer_name} not found')
        return {'index': 0, 'variant': 0, 'confidence': 0}

    layer_key = layer['folder']
    layer_sprites = sprite_metadata.get('categories', {}).get(layer_key)

    if not layer_sprites:
        print(f'Sprite metadata for {layer_key} not found')
        # Return default
        available_indices = get_available_indices(layer_name, gender)
        return {
            'index': available_indices[0] if available_indices else 0,
            'variant': 0,
            'confidence': 0
        }

    best_match = {'filename': None, 'score': 0, 'index': -1, 'variant': -1}

    for filename, metadata in layer_sprites.items():
        # Skip gender-mismatched sprites
        if gender and metadata.get('gender_fit') != 'both' and metadata.get('gender_fit') != gender.lower():
            continue

        # Calculate match score based on tag overlap
        score = 0
        sprite_tags = metadata.get('tags', [])
        characteristics = metadata.get('characteristics', '')
        sprite_characteristics = [s.strip() for s in characteristics.split(',')] if characteristics else []
        all_sprite_terms = sprite_tags + sprite_characteristics + [
            metadata.get('style'),
            metadata.get('shape'),
            metadata.get('description')
        ]
        all_sprite_terms = [t for t in all_sprite_terms if t]

        for term in detected_terms:
            if not term:
                continue
            term_lower = term.lower()

            for sprite_term in all_sprite_terms:
                if not sprite_term:
                    continue
                sprite_term_lower = sprite_term.lower()

                # Exact match
                if term_lower == sprite_term_lower:
                    score += 2
                # Sprite term contains detected term
                elif term_lower in sprite_term_lower:
                    score += 1
                # Detected term contains sprite term
                elif sprite_term_lower in term_lower:
                    score += 0.5

        if score > best_match['score']:
            # Extract index and variant from filename
            import re
            match = re.search(r'(\w+)_(\d+)_(\d+)', filename)
            if match:
                best_match = {
                    'filename': filename,
                    'score': score,
                    'index': int(match.group(2)),
                    'variant': int(match.group(3))
                }

    # If no good match found (score < 1), use defaults
    if best_match['score'] < 1:
        available_indices = get_available_indices(layer_name, gender)
        best_match['index'] = available_indices[0] if available_indices else 0
        best_match['variant'] = 0
        best_match['score'] = 0

    return {
        'index': best_match['index'],
        'variant': best_match['variant'],
        'confidence': min(best_match['score'] / 3, 1.0)  # Normalize to 0-1
    }
