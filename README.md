# Solar Energy Prediction Web App

A full-stack web application for predicting solar panel energy output based on weather forecasts and solar panel condition data. This project supports SDG 7 (Affordable & Clean Energy) by enabling better planning and maintenance of solar infrastructure.

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
         │ HTTP/REST
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

- **Backend**: Django 4.x + Django REST Framework
- **Frontend**: React 18.x + React Router
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (via Supabase)
- **ML**: scikit-learn, TensorFlow/Keras (optional for CNN)
- **File Storage**: Local filesystem (media/uploads)

## 📁 Project Structure

```
Finito/
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

- Python 3.9+
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

## 📝 License

See LICENSE file for details.

