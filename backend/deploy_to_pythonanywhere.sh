#!/bin/bash

# PythonAnywhere Deployment Script
# This script helps you prepare files for deployment to PythonAnywhere

echo "======================================"
echo "PythonAnywhere Deployment Helper"
echo "======================================"
echo ""

# Check if username is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy_to_pythonanywhere.sh YOUR_USERNAME"
    echo ""
    echo "Example: ./deploy_to_pythonanywhere.sh myusername"
    echo ""
    exit 1
fi

USERNAME=$1

echo "Preparing deployment files for user: $USERNAME"
echo ""

# Update WSGI file with username
echo "1. Updating WSGI configuration..."
sed "s/YOUR_PYTHONANYWHERE_USERNAME/$USERNAME/g" pythonanywhere_wsgi.py > pythonanywhere_wsgi_configured.py
echo "   ✓ Created: pythonanywhere_wsgi_configured.py"

# Update production settings with username
echo "2. Updating production settings..."
sed "s/YOUR_USERNAME/$USERNAME/g" crew_generator_backend/settings_production.py > crew_generator_backend/settings_production_configured.py
echo "   ✓ Created: crew_generator_backend/settings_production_configured.py"

# Create a deployment checklist
echo "3. Creating deployment checklist..."
cat > DEPLOYMENT_CHECKLIST.txt << EOF
PythonAnywhere Deployment Checklist for: $USERNAME
================================================

PRE-DEPLOYMENT:
□ Have PythonAnywhere account created
□ Have ANTHROPIC_API_KEY ready
□ Have reviewed DEPLOYMENT.md

PYTHONANYWHERE SETUP:
□ Created new web app (Manual configuration, Python 3.10+)
□ Created directory: /home/$USERNAME/crew-generator-backend/
□ Uploaded all backend files to the directory

VIRTUAL ENVIRONMENT:
□ Created venv: python3.10 -m venv venv
□ Activated venv: source venv/bin/activate
□ Installed packages: pip install -r requirements.txt

ENVIRONMENT VARIABLES:
□ Created .env file from .env.example
□ Added ANTHROPIC_API_KEY to .env
□ Verified .env is not in git (check .gitignore)

WSGI CONFIGURATION:
□ Opened WSGI file from Web tab
□ Replaced contents with pythonanywhere_wsgi_configured.py
□ Verified username is correct in WSGI file

DJANGO CONFIGURATION:
□ Updated settings.py ALLOWED_HOSTS with $USERNAME.pythonanywhere.com
□ Updated CORS_ALLOWED_ORIGINS with frontend URL
□ Ran migrations: python manage.py migrate
□ Collected static files: python manage.py collectstatic

STATIC FILES (Web tab):
□ Set Static URL: /static/
□ Set Static Directory: /home/$USERNAME/crew-generator-backend/static/

RELOAD & TEST:
□ Clicked Reload button in Web tab
□ Tested base URL: https://$USERNAME.pythonanywhere.com/
□ Tested API endpoint: https://$USERNAME.pythonanywhere.com/api/analyze-photo
□ Checked error logs if any issues

FRONTEND UPDATE:
□ Updated PhotoUpload.svelte with production URL
□ Changed http://localhost:8000 to https://$USERNAME.pythonanywhere.com

PRODUCTION CHECKLIST:
□ Set DEBUG=False in settings
□ Generated new SECRET_KEY for production
□ Reviewed security settings
□ Set up monitoring/logging
□ Documented API endpoint for team

NOTES:
------
- Error log location: Web tab → Log files
- Free tier has API whitelist - add anthropic.com if needed
- Consider paid tier for production use

URLS:
-----
Backend: https://$USERNAME.pythonanywhere.com
API Docs: https://$USERNAME.pythonanywhere.com/api/
Photo Analysis: https://$USERNAME.pythonanywhere.com/api/analyze-photo
Crew Generator: https://$USERNAME.pythonanywhere.com/api/generate-crew
EOF

echo "   ✓ Created: DEPLOYMENT_CHECKLIST.txt"

echo ""
echo "======================================"
echo "Preparation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review DEPLOYMENT.md for detailed instructions"
echo "2. Use DEPLOYMENT_CHECKLIST.txt to track progress"
echo "3. Copy pythonanywhere_wsgi_configured.py contents to PythonAnywhere WSGI file"
echo "4. Follow the manual deployment steps in DEPLOYMENT.md"
echo ""
echo "Your production URL will be: https://$USERNAME.pythonanywhere.com"
echo ""
