# Production Deployment Guide

## Overview

This guide covers deploying the Solar Energy Prediction app to production using free/affordable hosting services.

## Architecture

```
┌─────────────────┐
│  React Frontend │  → Vercel / Netlify (Free)
│  (Static Host)  │
└─────────────────┘
         │
         │ API Calls
         │
┌────────▼─────────┐
│  Django Backend   │  → Railway / Render / Heroku (Free tier)
│  (API Server)     │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Supabase│ │  Cloud │
│  (DB)  │ │ Storage│
└────────┘ └────────┘
```

## Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) - Recommended

**Frontend on Vercel (Free)**
- Automatic deployments from Git
- Built-in SSL
- Global CDN
- Free tier: Unlimited

**Backend on Railway (Free tier)**
- $5/month free credit
- Easy PostgreSQL connection
- Automatic deployments
- Environment variables management

### Option 2: Netlify (Frontend) + Render (Backend) - Free

**Frontend on Netlify (Free)**
- Continuous deployment
- Free SSL
- CDN included

**Backend on Render (Free tier)**
- Free tier available (with limitations)
- Automatic SSL
- PostgreSQL support

## Step-by-Step Deployment

### 1. Prepare for Production

#### Backend Settings

Update `backend/solar_app/settings.py`:

```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['your-backend-domain.com', 'api.yourdomain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files (if using Django static files)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

#### Frontend Build

The React app will be built automatically, but ensure `.env.production`:

```env
REACT_APP_API_URL=https://your-backend-domain.com/api
REACT_APP_SUPABASE_URL=your-supabase-url
REACT_APP_SUPABASE_ANON_KEY=your-supabase-key
```

### 2. Deploy Backend (Railway)

1. **Create Railway account**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Select your repository**
4. **Add PostgreSQL** (or use Supabase connection string)
5. **Set Environment Variables**:
   ```
   SECRET_KEY=generate-strong-secret-key
   DEBUG=False
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=your-db-host
   DB_PORT=5432
   ```
6. **Configure Build**:
   - Build command: `cd backend && pip install -r requirements.txt`
   - Start command: `cd backend && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn solar_app.wsgi:application --bind 0.0.0.0:$PORT`
7. **Add gunicorn** to `backend/requirements.txt`:
   ```
   gunicorn==21.2.0
   ```

### 3. Deploy Frontend (Vercel)

1. **Create Vercel account**: https://vercel.com
2. **Import Project** from GitHub
3. **Configure**:
   - Framework Preset: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
4. **Environment Variables**:
   ```
   REACT_APP_API_URL=https://your-backend.railway.app/api
   REACT_APP_SUPABASE_URL=your-supabase-url
   REACT_APP_SUPABASE_ANON_KEY=your-supabase-key
   ```
5. **Deploy**

### 4. Configure Supabase

1. **Update CORS** in Supabase Dashboard:
   - Settings → API → CORS
   - Add your frontend domain: `https://your-frontend.vercel.app`

2. **Update RLS Policies** (if needed):
   - Ensure production users can access data
   - Test authentication flow

### 5. File Storage (Optional)

For production image uploads, consider:

**Option A: Supabase Storage** (Recommended)
- Free tier: 1GB
- Update `data_processing/file_handler.py` to use Supabase Storage

**Option B: Cloudinary** (Free tier: 25GB)
- Free image hosting
- CDN included

**Option C: AWS S3** (Pay-as-you-go)
- More control
- Requires AWS account

## Production Checklist

### Security
- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (use: `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- [ ] HTTPS enabled everywhere
- [ ] CORS configured correctly
- [ ] Environment variables secured (not in Git)
- [ ] Supabase RLS policies reviewed

### Performance
- [ ] Static files collected (`collectstatic`)
- [ ] Database indexes created
- [ ] ML models optimized/cached
- [ ] Frontend assets minified
- [ ] CDN configured (if using)

### Monitoring
- [ ] Error logging set up (Sentry, etc.)
- [ ] Health check endpoint working
- [ ] Database backups configured
- [ ] Uptime monitoring (UptimeRobot - free)

### Testing
- [ ] All API endpoints tested
- [ ] Authentication flow tested
- [ ] File uploads working
- [ ] Predictions generating correctly
- [ ] Mobile responsiveness checked

## Environment Variables Summary

### Backend (.env or Railway variables)
```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-backend-domain.com
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=your-db-host.supabase.co
DB_PORT=5432
```

### Frontend (Vercel/Netlify variables)
```
REACT_APP_API_URL=https://your-backend-domain.com/api
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Cost Estimate (Free Tier)

- **Vercel**: Free (unlimited)
- **Railway**: $5/month free credit (usually enough)
- **Supabase**: Free (500MB database, 1GB storage)
- **Total**: $0-5/month

## Alternative: All-in-One Deployment

### Render (Full Stack)

1. **Create Render account**: https://render.com
2. **Deploy Backend**:
   - New Web Service
   - Connect GitHub repo
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn solar_app.wsgi:application`
3. **Deploy Frontend**:
   - New Static Site
   - Root Directory: `frontend`
   - Build: `npm install && npm run build`
   - Publish: `build`

**Note**: Render free tier spins down after inactivity (15 min cold start)

## Post-Deployment

1. **Test all features**:
   - Login/authentication
   - Data uploads
   - Model training
   - Predictions
   - Health checks

2. **Set up monitoring**:
   - Error tracking (Sentry free tier)
   - Uptime monitoring (UptimeRobot)
   - Performance monitoring

3. **Configure backups**:
   - Supabase automatic backups (Pro plan)
   - Or manual database exports

4. **Update documentation**:
   - Update API URLs in docs
   - Share production URLs

## Troubleshooting

**Backend won't start:**
- Check environment variables
- Verify database connection
- Check logs in Railway/Render dashboard

**Frontend can't connect to API:**
- Verify CORS settings
- Check API URL in environment variables
- Verify backend is running

**Database connection issues:**
- Check Supabase connection string
- Verify network access
- Check firewall settings

**Static files not loading:**
- Run `collectstatic` command
- Check `STATIC_ROOT` setting
- Verify file permissions

## Scaling Considerations

When you outgrow free tiers:

1. **Database**: Upgrade Supabase plan ($25/month for 8GB)
2. **Backend**: Upgrade Railway plan or use AWS/GCP
3. **Storage**: Move to S3 or Cloudinary
4. **CDN**: Use Cloudflare (free) for better performance
5. **Caching**: Add Redis for session caching
6. **Load Balancing**: Use multiple backend instances

## Security Best Practices

1. **Never commit** `.env` files
2. **Rotate secrets** regularly
3. **Use HTTPS** everywhere
4. **Enable rate limiting** on API
5. **Regular security updates** for dependencies
6. **Monitor** for suspicious activity
7. **Backup** database regularly

## Support Resources

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs
- Supabase Docs: https://supabase.com/docs

