# Netlify Deployment Guide

This Hospital Management System is configured for deployment on Netlify using serverless functions.

## Prerequisites

- GitHub repository: https://github.com/future-genius/hospital_management_system_app
- Netlify account (free tier available at netlify.com)

## Setup Steps

### 1. Connect Repository to Netlify

1. Go to [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Choose GitHub and authorize Netlify
4. Select the `hospital_management_system_app` repository
5. Connect to the repository

### 2. Configure Environment Variables

In Netlify Dashboard → Site Settings → Build & Deploy → Environment:

#### Required Variables:
```
SECRET_KEY=<generate-a-secure-random-key>
DATABASE_URL=<your-database-url>
FLASK_ENV=production
PYTHON_VERSION=3.11
```

#### To generate a secure SECRET_KEY:
```python
import secrets
print(secrets.token_hex(32))
```

#### Database Options:

**Option A: Use PostgreSQL Add-on (Recommended)**
- Go to Integrations → Add-on → PostgreSQL
- Netlify automatically sets DATABASE_URL

**Option B: Use SQLite**
- Leave DATABASE_URL empty
- App uses SQLite in instance/app.db

**Option C: External PostgreSQL Database**
- Get connection string from your provider
- Set DATABASE_URL environment variable

### 3. Build Configuration

The `netlify.toml` file already contains:
- Build command to install dependencies
- Python functions configuration
- URL redirects to Flask app
- Environment variables per deployment context

### 4. Deploy

Simply push to GitHub:
```bash
git push origin main
```

Netlify will automatically:
1. Build the project
2. Install dependencies from requirements.txt
3. Deploy as serverless functions
4. Set up URL routing

## Project Structure

```
hospital_app_23f2005421/
├── netlify/
│   └── functions/
│       └── app.py          # Serverless function handler
├── routes/                 # Flask blueprints
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── models.py              # Database models
├── app.py                 # Flask application (updated for serverless)
├── wsgi.py                # WSGI entry point
├── requirements.txt       # Python dependencies
├── netlify.toml          # Netlify configuration
├── runtime.txt           # Python version specification
└── .gitignore            # Git ignore patterns
```

## Features

- **Serverless Deployment**: Runs on Netlify Functions (no server management)
- **Environment-aware Configuration**: Detects and uses environment variables
- **Database Flexibility**: Supports SQLite (local), PostgreSQL (cloud)
- **Multi-tier Access**: Admin, Provider, Patient roles
- **Responsive Templates**: Bootstrap-based UI
- **User Authentication**: Flask-Login integration

## Important Notes

1. **Database Persistence**:
   - SQLite: Limited in serverless (no persistence between deploys)
   - PostgreSQL: Recommended for production

2. **Session Management**:
   - Ensure SECRET_KEY is set in environment variables
   - Configure secure session cookies

3. **Static Files**:
   - CSS and JS are served from the `static/` directory
   - Ensure these are included in the deployment

4. **Initial Setup**:
   - Default admin account: `admin@facilities.local` / `admin123`
   - Change these credentials immediately in production
   - Roles and departments are created automatically on first run

## Troubleshooting

### Build Failures
- Check build logs in Netlify Dashboard
- Verify all dependencies are in requirements.txt
- Ensure Python version is compatible

### Database Connection Issues
- Verify DATABASE_URL format is correct
- Check database credentials
- Ensure firewall allows connections from Netlify

### Function Timeout
- Default timeout is 10 seconds
- For long operations, consider optimizing or increasing timeout in netlify.toml

## Post-Deployment

1. Update default admin credentials
2. Configure email service (if needed)
3. Set up proper logging
4. Configure CDN and caching policies
5. Set up monitoring and alerts

## Support & Documentation

- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Deployment Monitoring

Monitor your site:
1. Netlify Dashboard → Deploys
2. View build logs and deployment history
3. Check function performance metrics
4. Set up email notifications for deployment failures

---

**Last Updated**: December 2, 2025
