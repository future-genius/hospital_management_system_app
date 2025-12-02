# Netlify Deployment Checklist

## Pre-Deployment Tasks

- [ ] **Review Configuration Files**
  - [x] `netlify.toml` - Build settings and redirects
  - [x] `.env.example` - Environment variable template
  - [x] `runtime.txt` - Python version specification
  - [x] `requirements.txt` - All dependencies listed

- [ ] **Code Quality**
  - [ ] All routes are tested locally
  - [ ] No hardcoded secrets or credentials
  - [ ] Error handling is in place
  - [ ] Logging is configured

- [ ] **Database**
  - [ ] Choose PostgreSQL for production (recommended)
  - [ ] Or configure SQLite with persistence
  - [ ] Backup strategy in place

## Deployment Steps

### 1. Connect to Netlify
```bash
# Push changes to GitHub
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

### 2. Netlify Dashboard Setup
1. Go to https://netlify.com
2. Log in with GitHub
3. Click "New site from Git"
4. Select `hospital_management_system_app` repository
5. Verify build settings:
   - Build command: `pip install -r requirements.txt`
   - Functions directory: `netlify/functions`
   - Python version: 3.11

### 3. Configure Environment Variables
In Netlify Site Settings → Build & Deploy → Environment:

```
SECRET_KEY=<generate-secure-key>
DATABASE_URL=<postgres-connection-string>
FLASK_ENV=production
PYTHON_VERSION=3.11
```

**To generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 4. Deploy
Push to GitHub, Netlify will automatically:
- Build your project
- Install dependencies
- Deploy serverless functions
- Set up routing

## Post-Deployment Verification

- [ ] **Site is Live**
  - [ ] Can access site at https://your-site.netlify.app
  - [ ] Landing page loads
  - [ ] CSS/JS are loading correctly

- [ ] **Authentication Works**
  - [ ] Can navigate to login page
  - [ ] Can sign up as new user
  - [ ] Can log in with default admin credentials
  - [ ] Session persists across pages

- [ ] **Database Operations**
  - [ ] Can create/read/update clinic departments
  - [ ] Can manage providers
  - [ ] Can manage patients
  - [ ] No database errors in logs

- [ ] **Error Handling**
  - [ ] 404 pages display correctly
  - [ ] Error pages have proper messages
  - [ ] No console errors

- [ ] **Performance**
  - [ ] Page load times are acceptable
  - [ ] API responses are fast
  - [ ] No function timeouts

## Security Tasks

- [ ] **Credentials**
  - [ ] Change default admin password immediately
  - [ ] Use strong SECRET_KEY (not dev-secret)
  - [ ] No credentials in GitHub

- [ ] **HTTPS**
  - [ ] Site uses HTTPS (Netlify default)
  - [ ] SSL certificate is valid

- [ ] **Headers**
  - [ ] Security headers are set (X-Frame-Options, etc.)
  - [ ] No sensitive data in headers

## Optimization Tasks

- [ ] **Database**
  - [ ] PostgreSQL indexes are created
  - [ ] Query performance is acceptable
  - [ ] Connection pooling is configured

- [ ] **Caching**
  - [ ] Static files have cache headers
  - [ ] HTML is not cached
  - [ ] API responses have appropriate TTL

- [ ] **Monitoring**
  - [ ] Netlify analytics enabled
  - [ ] Function logs are accessible
  - [ ] Error tracking is set up

## Troubleshooting

### Build Fails
- Check build logs in Netlify Dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python 3.11 is being used
- Check for import errors

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check PostgreSQL credentials
- Ensure firewall allows Netlify IP ranges
- Test connection string locally

### Static Files Not Loading
- Check `static/` directory is included
- Verify file paths in templates
- Check cache headers

### Function Timeouts
- Optimize database queries
- Reduce payload size
- Increase timeout in netlify.toml (max 30s)
- Use caching where possible

## Support Resources

- [Netlify Functions Docs](https://docs.netlify.com/functions/overview/)
- [Netlify Build Plugins](https://docs.netlify.com/configure-builds/build-plugins/)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [SQLAlchemy with PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

## Additional Notes

### Default Admin Credentials
- **Email**: admin@facilities.local
- **Password**: admin123
- **Action**: Change immediately after first login!

### Initial Data
- Roles (Admin, Provider, Patient) - Auto-created
- Departments - Auto-created on first deployment
- Can be modified through admin dashboard

### Backup Strategy
- Set up PostgreSQL automated backups
- Or use SQLite backup solutions
- Configure disaster recovery plan

---

**Last Updated**: December 2, 2025
**Status**: Ready for Deployment
