"""
API views for crew generation and photo analysis
"""
import os
import json
import re
import uuid
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import anthropic
from dotenv import load_dotenv
from .character_generator import generate_random_character
from .photo_matcher import match_features_to_sprites
from . import postcard_generator

# Load environment variables
load_dotenv()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Ethnicity to skin color range mapping
ETHNICITY_TO_SKIN_RANGE = {
    'European': (0, 2),      # Very Light to Light Medium
    'African': (5, 6),       # Brown to Dark Brown
    'Asian': (1, 3),         # Light to Medium
    'MiddleEastern': (3, 4), # Medium to Olive
    'Hispanic': (2, 4),      # Light Medium to Olive
    'Mixed': (0, 6)          # Any skin tone
}


@csrf_exempt
@require_http_methods(["POST"])
def generate_crew(request):
    """
    Generate crew members using AI based on description
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        description = body.get('description', '').strip()
        replace_existing = body.get('replaceExisting', False)

        # Validate description
        if not description:
            return JsonResponse(
                {'error': 'Description is required'},
                status=400
            )

        print(f'Starting crew generation for description: {description}')
        print(f'API Key exists: {bool(ANTHROPIC_API_KEY)}')

        # AI prompt for crew generation
        prompt = f"""You are a crew generator for a WW2 aviation game. Generate a crew based on this description: "{description}"

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks, no explanations.

Requirements:
- Generate an appropriate number of crew members (if not specified, generate 5-10)
- MAXIMUM 10 crew members total - never generate more than 10
- All birth dates must be before 1922 (valid format: YYYY-MM-DD)
- Use authentic names appropriate for the nationality/squadron mentioned
- Class must be either "AirCrew" or "BaseCrew"
- For AirCrew: Role must be one of: Pilot, Gunner, Navigator, BombAimer, FlightEngineer, RadioOperator
- For BaseCrew: Job must be one of: AAFCook, FieldMechanic, FieldEngineer, RAFMedic, AAFLabour
- Skill ranks must be 0-6 (only for AirCrew)
- Gender must be "Male" or "Female"
- Create brief but authentic biographies (2-3 sentences)
- Add "Ethnicity" field: Based on the nationality/description, specify the ethnicity/appearance
  Valid values: "European", "African", "Asian", "MiddleEastern", "Hispanic", "Mixed"
  Examples: Polish → European, Tuskegee Airmen → African, Japanese → Asian

Return a JSON array with this EXACT structure:
[
  {{
    "FirstName": "Jan",
    "LastName": "Kowalski",
    "Nickname": "Eagle",
    "BirthDate": "1918-05-15",
    "Gender": "Male",
    "Ethnicity": "European",
    "Class": "AirCrew",
    "Role": "Pilot",
    "Job": "None",
    "Biography": {{
      "en": "Brief biography here..."
    }},
    "SkillRanks": {{
      "Flying": 4,
      "Shooting": 3,
      "Bombing": 2,
      "Endurance": 5,
      "Engineering": 2,
      "Navigating": 3
    }}
  }}
]

Generate the crew now:"""

        # Call Anthropic API
        print('Calling Claude API...')
        message = client.messages.create(
            model='claude-sonnet-4-5',
            max_tokens=4096,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            timeout=60.0  # 60 second timeout
        )

        print('Claude API response received')

        # Extract text from response
        response_text = message.content[0].text
        print(f'Response text length: {len(response_text)}')

        # Parse JSON from response
        crew_data = None
        try:
            # Try direct JSON parse first
            crew_data = json.loads(response_text)
            print('Successfully parsed JSON directly')
        except json.JSONDecodeError as e:
            print(f'Direct JSON parse failed: {e}')
            # Try to extract from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', response_text)
            if json_match:
                crew_data = json.loads(json_match.group(1))
                print('Extracted JSON from markdown code block')
            else:
                # Try to find any JSON array
                array_match = re.search(r'\[[\s\S]*\]', response_text)
                if array_match:
                    crew_data = json.loads(array_match.group(0))
                    print('Extracted JSON array from response')
                else:
                    print(f'Could not extract JSON. Response text: {response_text[:500]}')
                    raise ValueError('Could not extract valid JSON from response')

        # Validate it's an array
        if not isinstance(crew_data, list):
            print(f'Response is not an array: {type(crew_data)}')
            raise ValueError('Response is not an array')

        # Limit to maximum 10 crew members
        if len(crew_data) > 10:
            print(f'Limiting crew from {len(crew_data)} to 10 members')
            crew_data = crew_data[:10]

        print(f'Successfully parsed crew data, count: {len(crew_data)}')

        # Enrich crew data with random character appearance
        enriched_crew = []
        for member in crew_data:
            # Get gender and ethnicity
            gender = member.get('Gender', 'Male')
            ethnicity = member.get('Ethnicity', 'European')

            # Get appropriate skin color range based on ethnicity
            skin_color_range = ETHNICITY_TO_SKIN_RANGE.get(ethnicity, (0, 6))

            print(f'Generating {ethnicity} character with skin range: {skin_color_range}')

            # Generate random character appearance
            random_character = generate_random_character(gender, skin_color_range)

            # Create metadata structure
            metadata = {
                'Id': str(uuid.uuid4()),
                'CreatorName': member.get('CreatorName', ''),
                'FirstName': member.get('FirstName', 'Unknown'),
                'LastName': member.get('LastName', ''),
                'Nickname': member.get('Nickname', ''),
                'BirthDate': member.get('BirthDate', '1920-01-01'),
                'Gender': gender,
                'Class': member.get('Class', 'AirCrew'),
                'Job': member.get('Job', 'None'),
                'Role': member.get('Role', 'Pilot'),
                'Biography': member.get('Biography', {'en': ''}),
                'SkillRanks': member.get('SkillRanks', {
                    'Flying': 0,
                    'Shooting': 0,
                    'Bombing': 0,
                    'Endurance': 0,
                    'Engineering': 0,
                    'Navigating': 0
                })
            }

            enriched_crew.append({
                'character': random_character,
                'metadata': metadata
            })

        print(f'Returning enriched crew, count: {len(enriched_crew)}')

        return JsonResponse({
            'crew': enriched_crew,
            'count': len(enriched_crew),
            'replaceExisting': replace_existing
        })

    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        return JsonResponse(
            {
                'error': 'Invalid JSON in request',
                'details': str(e)
            },
            status=400
        )

    except anthropic.APIError as e:
        print(f'Anthropic API error: {e}')
        return JsonResponse(
            {
                'error': 'Failed to generate crew',
                'details': str(e),
                'type': 'APIError'
            },
            status=500
        )

    except Exception as e:
        print(f'Crew generation error: {e}')
        import traceback
        traceback.print_exc()

        return JsonResponse(
            {
                'error': 'Failed to generate crew',
                'details': str(e),
                'type': type(e).__name__
            },
            status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def version_check(request):
    """
    Check which version of postcard_generator module is loaded
    """
    try:
        version = getattr(postcard_generator, 'MODULE_VERSION', 'UNKNOWN')
        return JsonResponse({
            'module': 'postcard_generator',
            'version': version,
            'status': 'loaded'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Comprehensive health check for production debugging
    Returns status of all critical files, modules, and dependencies
    """
    import sys
    from django.conf import settings

    health = {
        'status': 'healthy',
        'issues': [],
        'checks': {}
    }

    # Check Python files
    api_dir = os.path.dirname(__file__)
    required_files = [
        'views.py',
        'views_postcard.py',
        'postcard_generator.py',
        'character_generator.py',
        'photo_matcher.py',
        'sprite-metadata.json',
        'urls.py'
    ]

    health['checks']['files'] = {}
    for filename in required_files:
        filepath = os.path.join(api_dir, filename)
        exists = os.path.exists(filepath)
        health['checks']['files'][filename] = {
            'exists': exists,
            'path': filepath
        }
        if not exists:
            health['issues'].append(f'Missing file: {filename}')
            health['status'] = 'unhealthy'

    # Check module imports
    health['checks']['imports'] = {}
    modules_to_check = [
        ('anthropic', 'Anthropic API client'),
        ('PIL', 'Pillow (image processing)'),
        ('dotenv', 'Environment variables'),
    ]

    for module_name, description in modules_to_check:
        try:
            __import__(module_name)
            health['checks']['imports'][module_name] = {
                'status': 'ok',
                'description': description
            }
        except ImportError as e:
            health['checks']['imports'][module_name] = {
                'status': 'missing',
                'error': str(e),
                'description': description
            }
            health['issues'].append(f'Missing module: {module_name} ({description})')
            health['status'] = 'unhealthy'

    # Check environment variables
    health['checks']['environment'] = {
        'ANTHROPIC_API_KEY': 'set' if ANTHROPIC_API_KEY else 'missing',
        'STATIC_ROOT': getattr(settings, 'STATIC_ROOT', 'not configured')
    }

    if not ANTHROPIC_API_KEY:
        health['issues'].append('ANTHROPIC_API_KEY not set')
        health['status'] = 'unhealthy'

    # Check static files directory
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root:
        health['checks']['static_files'] = {
            'STATIC_ROOT': static_root,
            'exists': os.path.exists(static_root),
            'PortraitSprites_exists': os.path.exists(os.path.join(static_root, 'PortraitSprites')),
            'PostcardTemplates_exists': os.path.exists(os.path.join(static_root, 'PostcardTemplates'))
        }

        if not os.path.exists(static_root):
            health['issues'].append(f'STATIC_ROOT directory does not exist: {static_root}')
            health['status'] = 'unhealthy'

    # Check module versions
    health['checks']['versions'] = {
        'postcard_generator': getattr(postcard_generator, 'MODULE_VERSION', 'UNKNOWN'),
        'python_version': sys.version,
        'django_settings_module': os.getenv('DJANGO_SETTINGS_MODULE', 'not set')
    }

    # Check current working directory and Python path
    health['checks']['system'] = {
        'cwd': os.getcwd(),
        'api_dir': api_dir,
        'sys_path': sys.path[:3]  # First 3 paths only
    }

    return JsonResponse(health, status=200 if health['status'] == 'healthy' else 500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_photo(request):
    """
    Analyze photo and generate matching character
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        image_base64 = body.get('image', '').strip()
        mime_type = body.get('mimeType', 'image/jpeg')

        # Validate inputs
        if not image_base64 or not mime_type:
            return JsonResponse(
                {'error': 'Image data and mimeType are required'},
                status=400
            )

        # Validate MIME type
        valid_types = ['image/jpeg', 'image/png', 'image/heic', 'image/webp']
        if mime_type not in valid_types:
            return JsonResponse(
                {'error': 'Invalid image format. Allowed: JPEG, PNG, HEIC, WebP'},
                status=400
            )

        print('Starting photo analysis...')
        print(f'Image size: {len(image_base64)} bytes (base64)')
        print(f'MIME type: {mime_type}')

        # Create Claude Vision API prompt
        prompt = """Analyze this portrait photo and extract facial features in structured JSON format.

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

Analyze the photo now and return ONLY the JSON, no markdown, no explanations."""

        # Call Claude Vision API
        print('Calling Claude Vision API...')
        message = client.messages.create(
            model='claude-sonnet-4-5',
            max_tokens=2048,
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': mime_type,
                                'data': image_base64
                            }
                        },
                        {
                            'type': 'text',
                            'text': prompt
                        }
                    ]
                }
            ],
            timeout=30.0  # 30 second timeout
        )

        print('Claude API response received')

        # Extract and parse JSON response
        response_text = message.content[0].text
        print(f'Response text length: {len(response_text)}')

        detected_features = None
        try:
            # Try direct parse first
            detected_features = json.loads(response_text)
            print('Successfully parsed JSON directly')
        except json.JSONDecodeError as e:
            print(f'Direct JSON parse failed: {e}')
            # Try to extract from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
            if json_match:
                detected_features = json.loads(json_match.group(1))
                print('Extracted JSON from markdown code block')
            else:
                # Try to find any JSON object
                object_match = re.search(r'\{[\s\S]*\}', response_text)
                if object_match:
                    detected_features = json.loads(object_match.group(0))
                    print('Extracted JSON object from response')
                else:
                    print(f'Could not extract JSON. Response text: {response_text[:500]}')
                    raise ValueError('Could not extract valid JSON from response')

        # Validate face detection
        if not detected_features.get('face_detected'):
            return JsonResponse(
                {
                    'error': 'No face detected in photo',
                    'details': 'Please upload a clear portrait photo showing one person\'s face'
                },
                status=400
            )

        print('Face detected successfully')
        print(f'Gender: {detected_features.get("gender_presentation")}')
        print(f'Face shape: {detected_features.get("face_shape")}')
        print(f'Skin tone: {detected_features.get("skin_tone")}')

        # Match features to sprites
        print('Matching features to sprites...')
        character = match_features_to_sprites(detected_features)

        print('Character generated successfully')
        print(f'Gender: {character["gender"]}')
        print(f'Parts count: {len(character["parts"])}')

        return JsonResponse({
            'character': character,
            'analysis': {
                'detectedFeatures': detected_features,
                'matchConfidence': character.get('matchConfidence', {})
            }
        })

    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        return JsonResponse(
            {
                'error': 'Invalid JSON in request',
                'details': str(e)
            },
            status=400
        )

    except anthropic.APIError as e:
        print(f'Anthropic API error: {e}')
        return JsonResponse(
            {
                'error': 'Failed to analyze photo',
                'details': str(e),
                'type': 'APIError'
            },
            status=500
        )

    except Exception as e:
        print(f'Photo analysis error: {e}')
        import traceback
        traceback.print_exc()

        return JsonResponse(
            {
                'error': 'Failed to analyze photo',
                'details': str(e),
                'type': type(e).__name__
            },
            status=500
        )
