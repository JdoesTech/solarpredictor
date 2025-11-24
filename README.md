# Solar Energy Prediction Web App

A full-stack web application for predicting solar panel energy output based on weather forecasts and solar panel condition data. This project supports SDG 7 (Affordable & Clean Energy) by enabling better planning and maintenance of solar infrastructure.

The motivation for the development of this application is to enable users of solar energy to preempt solar patterns, plan for cloudy/rainy days and maximize on high solar radiation to either bank the excess energy or set it up for commercial supply. 
In the long run, the combined efforts of this and ther like-minded initiatives is to facilitate the wider adoption of solar energy, which is clean and renewable, leading to the achievement of Sustainable Development Goal 7: Affordable & Clean Energy.

Access the web app through this link : https://solarpredictor-1.onrender.com

## 🎯 Project Overview

**Goal**: Forecast energy production from solar panels based on weather forecasts and condition of solar arrays.

**AI/ML Approach**:
- **Technique**: Supervised learning (regression models, CNNs)
- **Input Data**: Weather data, historical energy production, solar panel images
- **Output**: Estimated daily/hourly energy output from solar systems

**Impact**:
- Better planning for solar grid contribution
- Proactive solar panel maintenance
- Improved ROI for solar infrastructure

## 🏗️ System Architecture

```
┌─────────────────┐
│   React Frontend │
│   (Port 3000)    │
└────────┬─────────┘
         │ HTTP/RESt
         │
┌────────▼─────────┐
│  Django Backend  │
│  (Port 8000)     │
│  - REST API      │
│  - ML Models     │
│  - File Upload   │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Supabase│ │  Local │
│  Auth  │ │  Files │
│  + DB  │ │ Storage│
└────────┘ └────────┘
```

## 🛠️ Tech Stack

- **Backend**: Django 4 + Django REST Framework
- **Frontend**: React 18 + React Router
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (via Supabase)
- **ML**: scikit-learn, TensorFlow/Keras (optional for CNN)
- **File Storage**: Local filesystem (media/uploads)

## 📁 Project Structure

```
solarpredictor/
├── backend/                 # Django backend
│   ├── solar_app/          # Main Django app
│   ├── ml_models/          # ML training and prediction
│   ├── api/                # REST API endpoints
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── App.js
│   └── package.json
├── ml_pipeline/            # ML training scripts
│   ├── notebooks/         # Jupyter notebooks
│   └── models/            # Trained models
├── docs/                  # Documentation
│   ├── architecture.md
│   ├── erd.md
│   └── api_docs.md
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10
- Node.js 16+
- Supabase account (free tier)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Get your project URL and anon key
3. Update `backend/solar_app/settings.py` with your Supabase credentials
4. Run the SQL schema from `docs/supabase_schema.sql`

## 📊 Features

- ✅ Admin authentication (JWT-based via Supabase)
- ✅ Dashboard with predicted vs actual output
- ✅ Data upload (weather CSV, production CSV, panel images)
- ✅ Model training interface
- ✅ Prediction/report page (hourly & daily forecast)
- ✅ System health panel (panel condition classifier)

## 📚 Open Datasets

For training the ML models, you can use these free datasets:

1. **Solar Power Generation Data**: [Kaggle - Solar Power Generation Data](https://www.kaggle.com/datasets/anikannal/solar-power-generation-data)
2. **Weather Data**: [OpenWeatherMap Historical Data](https://openweathermap.org/history)
3. **Solar Panel Images**: [Solar Panel Defect Detection Dataset](https://www.kaggle.com/datasets/dataclusterlabs/solar-panel-defect-detection)

## 📖 Documentation

- [System Architecture](docs/architecture.md)
- [Database Schema (ERD)](docs/erd.md)
- [API Documentation](docs/api_docs.md)

## 🔐 Environment Variables

Create `.env` files in both `backend/` and `frontend/`:

**backend/.env**:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_django_secret_key
DEBUG=True
```

**frontend/.env**:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🚢 Production Configuration

When moving from local development to production, adjust the following settings:

1. **Django (`backend/solar_app/settings.py`)**
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS` with your domain(s), i.e. `['api.yourdomain.com']`
   - Enable security middleware settings:
     ```python
     SECURE_SSL_REDIRECT = True
     SESSION_COOKIE_SECURE = True
     CSRF_COOKIE_SECURE = True
     SECURE_HSTS_SECONDS = 31536000  # this is equvalent to 1 year
     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
     SECURE_HSTS_PRELOAD = True
     SECURE_BROWSER_XSS_FILTER = True
     SECURE_CONTENT_TYPE_NOSNIFF = True
     ```
   - Configure static files:
     ```python
     STATIC_ROOT = BASE_DIR / 'staticfiles'
     ```
   - Generate a new strong `SECRET_KEY` and store it via environment variables.
   You can do so by running : python -c "import secrets; print(secrets.token_urlsafe())" 

2. **Environment Variables**
   - Provide production Supabase credentials, database host, and any storage keys in your hosting provider’s secrets manager.
   - Update `REACT_APP_API_URL` so the frontend calls the deployed backend HTTPS endpoint i.e. your backend url

3. **Frontend Build**
   - Add `.env.production` (or hosting equivalent) with production API URLs.
   - Run `npm run build` before deploying to static hosts (Vercel, Netlify, etc.).

4. **Supabase**
   - Add your deployed frontend domain under **Authentication → URL Configuration** and **API → CORS**.
   - Review Row Level Security policies before going live.

5. **Process Manager**
   - Install `gunicorn` (already listed in `backend/requirements.txt`) and start the Django app with `gunicorn solar_app.wsgi:application --bind 0.0.0.0:$PORT`.

## 📝 License

As of this moment, this projected is released under the MIT License.
More information to be found in the License file.

This project is hosted on Render, with the backend as a Web service and the frontend as a Static service

