"""
API view for server-side postcard generation
"""
import os
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .postcard_generator import postcard_to_base64
from .postcard_generator_v2 import generate_postcard_v2


@csrf_exempt
@require_http_methods(["POST"])
def generate_postcard_api(request):
    """
    Generate a postcard on the server side using Pillow

    Request body:
    {
        "color": "blue" | "orange",
        "characters": [<character objects>]
    }

    Returns: PNG image or base64 encoded PNG
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        color = body.get('color', 'blue')
        characters = body.get('characters', [])
        return_format = body.get('format', 'image')  # 'image' or 'base64'

        # Validate inputs
        if color not in ['blue', 'orange']:
            return JsonResponse(
                {'error': 'Color must be "blue" or "orange"'},
                status=400
            )

        if not characters or not isinstance(characters, list):
            return JsonResponse(
                {'error': 'Characters array is required'},
                status=400
            )

        if len(characters) > 10:
            return JsonResponse(
                {'error': 'Maximum 10 characters allowed'},
                status=400
            )

        print(f'Generating postcard: color={color}, characters={len(characters)}')
        print(f'Character data: {characters[0] if characters else "none"}')

        # Get base path for static files
        base_path = settings.STATIC_ROOT

        # Generate postcard using V2 generator
        postcard_image = generate_postcard_v2(color, characters, base_path)

        print('Postcard generated successfully')

        # Return based on format
        if return_format == 'base64':
            # Return as JSON with base64 encoded image
            base64_str = postcard_to_base64(postcard_image)
            return JsonResponse({
                'success': True,
                'image': base64_str,
                'format': 'png'
            })
        else:
            # Return as direct PNG image
            from io import BytesIO
            buffer = BytesIO()
            postcard_image.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)

            response = HttpResponse(buffer.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="postcard_{color}_{len(characters)}crew.png"'
            return response

    except FileNotFoundError as e:
        print(f'File not found: {e}')
        return JsonResponse(
            {
                'error': 'Template or sprite file not found',
                'details': str(e)
            },
            status=404
        )

    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        return JsonResponse(
            {
                'error': 'Invalid JSON in request',
                'details': str(e)
            },
            status=400
        )

    except Exception as e:
        print(f'Postcard generation error: {e}')
        import traceback
        traceback.print_exc()

        return JsonResponse(
            {
                'error': 'Failed to generate postcard',
                'details': str(e),
                'type': type(e).__name__
            },
            status=500
        )
