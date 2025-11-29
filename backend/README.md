# WW2 Character Generator - Django Backend

Django REST API backend for the WW2 aviation game character portrait generator.

## Features

- AI-powered crew generation using Anthropic Claude API
- Character appearance generation with ethnicity-based skin tones
- RESTful API endpoints
- CORS enabled for frontend integration

## Requirements

- Python 3.13+
- Django 5.2.8
- Anthropic API key

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### POST /api/generate-crew

Generate crew members based on description.

**Request:**
```json
{
  "description": "Create a crew of 10 Polish pilots from 303 Squadron",
  "replaceExisting": false
}
```

**Response:**
```json
{
  "crew": [
    {
      "character": {
        "gender": "Male",
        "bodyShapeIndex": 1,
        "colorIndices": { ... },
        "parts": { ... }
      },
      "metadata": {
        "Id": "uuid",
        "FirstName": "Jan",
        "LastName": "Kowalski",
        ...
      }
    }
  ],
  "count": 10,
  "replaceExisting": false
}
```

## Project Structure

```
backend/
├── api/                          # API application
│   ├── character_generator.py    # Character generation logic
│   ├── views.py                  # API views
│   └── urls.py                   # API URL routing
├── crew_generator_backend/       # Django project settings
│   ├── settings.py               # Main settings
│   └── urls.py                   # Main URL routing
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── .env                          # Environment variables (not in git)
```

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` with your domain
3. Use a production WSGI server (gunicorn, uWSGI)
4. Set up proper database (PostgreSQL recommended)
5. Configure static file serving
6. Use environment variables for secrets

### Recommended: Deploy to PythonAnywhere

1. Upload code to PythonAnywhere
2. Create virtual environment
3. Install dependencies from requirements.txt
4. Configure WSGI file
5. Set environment variables in PythonAnywhere dashboard
6. Reload web app

## License

Proprietary - WW2 Aviation Game Character Generator
