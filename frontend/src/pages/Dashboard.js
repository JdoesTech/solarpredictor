import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, Marker, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { useAuth } from '../services/auth';
import { fetchSolarForecast, getDashboardStats, searchLocation } from '../services/api';
import './Dashboard.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend);

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const DEFAULT_CENTER = [0, 0];
const DEFAULT_ZOOM = 3;

function MapInteractions({ onSelect }) {
  useMapEvents({
    click: (event) => onSelect(event.latlng),
  });
  return null;
}

function MapCenterUpdater({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, map.getZoom(), { duration: 0.6 });
    }
  }, [center, map]);
  return null;
}

const formatNumber = (value, digits = 1) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  return Number(value).toFixed(digits);
};

function Dashboard() {
  const { token } = useAuth();
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState('');

  const [mapCenter, setMapCenter] = useState(DEFAULT_CENTER);
  const [selectedCoords, setSelectedCoords] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastError, setForecastError] = useState('');

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);

  const mapRef = useRef(null);
  const getIsMobile = () => (typeof window !== 'undefined' ? window.matchMedia('(max-width: 900px)').matches : false);
  const [isMobile, setIsMobile] = useState(getIsMobile);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }
    const media = window.matchMedia('(max-width: 900px)');
    const update = () => setIsMobile(media.matches);
    update();
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await getDashboardStats();
        setStats(data);
      } catch (err) {
        setStatsError('Failed to load dashboard metrics.');
      } finally {
        setStatsLoading(false);
      }
    };
    loadStats();
  }, []);

  const handleForecastFetch = async (lat, lon) => {
    setForecastLoading(true);
    setForecastError('');
    setSelectedCoords({ lat, lon });

    try {
      const data = await fetchSolarForecast({ lat, lon });
      console.log('Forecast data received:', data);
      console.log('Current conditions:', data.current_conditions);
      console.log('Hourly forecast count:', data.hourly_forecast?.length);
      console.log('Daily summary count:', data.daily_summary?.length);
      setForecast(data);
      setSheetOpen(true);
      if (mapRef.current) {
        mapRef.current.flyTo([lat, lon], Math.max(mapRef.current.getZoom(), 5), { duration: 0.6 });
      }
    } catch (err) {
      console.error('Forecast fetch error:', err);
      console.error('Error response:', err.response?.data);
      const message = err.response?.data?.error || err.response?.data?.details || 'Unable to fetch Solcast data. Try another point.';
      setForecastError(message);
    } finally {
      setForecastLoading(false);
    }
  };

  const handleMapSelect = (latlng) => {
    setMapCenter([latlng.lat, latlng.lng]);
    handleForecastFetch(latlng.lat, latlng.lng);
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    setForecastError('');
    try {
      const results = await searchLocation(searchQuery.trim());
      setSearchResults(results);
      if (results.length) {
        const top = results[0];
        setMapCenter([top.lat, top.lon]);
        handleForecastFetch(top.lat, top.lon);
      }
    } catch {
      setForecastError('Location search failed. Please try again.');
    } finally {
      setSearching(false);
    }
  };

  const handleResultSelect = (result) => {
    setSearchQuery(result.display_name || '');
    setSearchResults([]);
    handleForecastFetch(result.lat, result.lon);
  };

  const chartColors = {
    pv: '#f59e0b',
    ghi: '#6366f1',
  };

  const hourlyChartData = {
    labels: (forecast?.hourly_forecast || []).map((point) =>
      new Date(point.time).toLocaleString(undefined, {
        weekday: 'short',
        hour: 'numeric',
      })
    ),
    datasets: [
      {
        label: 'Estimated PV Output (kW/kWp)',
        data: (forecast?.hourly_forecast || []).map((point) => point.pv_kw || 0),
        borderColor: chartColors.pv,
        backgroundColor: 'rgba(245, 158, 11, 0.15)',
        tension: 0.4,
        fill: true,
        pointRadius: 0,
      },
    ],
  };

  const dailyChartData = {
    labels: (forecast?.daily_summary || []).map((day) => day.date),
    datasets: [
      {
        label: 'Daily Solar Gain (kWh/m²)',
        backgroundColor: 'rgba(14, 165, 233, 0.7)',
        borderRadius: 8,
        data: (forecast?.daily_summary || []).map((day) => day.kwh_per_m2),
      },
    ],
  };

  const hourlyChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${formatNumber(context.raw, 2)} kW`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'kW per 1 kWp system' },
      },
    },
  };

  const dailyChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'kWh/m²' },
      },
    },
  };

  const trainingWindow = {
    start: stats?.active_model?.training_data_start?.split('T')[0] || 'N/A',
    end: stats?.active_model?.training_data_end?.split('T')[0] || 'N/A',
  };

  const panelContent = (
    <div className="forecast-panel__body">
      <div className="panel-header">
        <div>
          <p className="panel-label">Location</p>
          <h2>
            {forecast?.location?.city || 'Tap the map'}{' '}
            {forecast?.location?.country ? `• ${forecast.location.country}` : ''}
          </h2>
          {selectedCoords && (
            <p className="panel-subtitle">
              {formatNumber(selectedCoords.lat, 3)}°, {formatNumber(selectedCoords.lon, 3)}°
            </p>
          )}
        </div>
        {forecast?.cache?.source && (
          <span className={`badge badge--${forecast.cache.source === 'cache' ? 'cached' : 'live'}`}>
            {forecast.cache.source === 'cache' ? 'Cached (15 min)' : 'Fresh'}
          </span>
        )}
      </div>

      {forecast ? (
        <>
          <div className="metrics-grid">
            <div className="metric-card">
              <p className="metric-label">Current GHI</p>
              <p className="metric-value">{formatNumber(forecast.current_conditions?.ghi, 0)} W/m²</p>
              {forecast.current_conditions?.ghi !== null && forecast.current_conditions?.ghi !== undefined && (
                <p className="metric-subtitle">Global Horizontal Irradiance</p>
              )}
            </div>
            <div className="metric-card">
              <p className="metric-label">Air Temp</p>
              <p className="metric-value">{formatNumber(forecast.current_conditions?.air_temp, 1)}°C</p>
              {forecast.current_conditions?.air_temp !== null && forecast.current_conditions?.air_temp !== undefined && (
                <p className="metric-subtitle">Ambient Temperature</p>
              )}
            </div>
            <div className="metric-card">
              <p className="metric-label">Cloud Opacity</p>
              <p className="metric-value">{formatNumber(forecast.current_conditions?.cloud_opacity, 0)}%</p>
              {forecast.current_conditions?.cloud_opacity !== null && forecast.current_conditions?.cloud_opacity !== undefined && (
                <p className="metric-subtitle">Sky Cover</p>
              )}
            </div>
            {forecast.forecast_length && (
              <div className="metric-card">
                <p className="metric-label">Forecast Hours</p>
                <p className="metric-value">{forecast.forecast_length}</p>
                <p className="metric-subtitle">Available data points</p>
              </div>
            )}
          </div>
          
          {/* Debug info - shows API response details */}
          {process.env.NODE_ENV === 'development' && (
            <details className="debug-section" style={{ marginTop: '1rem', padding: '1rem', background: 'var(--surface-muted)', borderRadius: '8px', fontSize: '0.85rem' }}>
              <summary style={{ cursor: 'pointer', fontWeight: '600', marginBottom: '0.5rem' }}>API Response Details (Debug)</summary>
              <pre style={{ 
                overflow: 'auto', 
                maxHeight: '300px', 
                background: 'var(--surface-color)', 
                padding: '1rem', 
                borderRadius: '4px',
                fontSize: '0.75rem',
                lineHeight: '1.4'
              }}>
                {JSON.stringify(forecast, null, 2)}
              </pre>
            </details>
          )}

          <div className="chart-card">
            <div className="chart-card__header">
              <h3>Next 48 Hours</h3>
              <p>Estimated PV output per 1 kWp system</p>
            </div>
            <div className="chart">
              <Line data={hourlyChartData} options={hourlyChartOptions} />
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-card__header">
              <h3>7-Day Solar Gain</h3>
              <p>Daily kWh/m² summary</p>
            </div>
            <div className="chart">
              <Bar data={dailyChartData} options={dailyChartOptions} />
            </div>
          </div>
        </>
      ) : (
        <div className="panel-placeholder">
          <p>Select any point on the map or search for a city to load a forecast.</p>
        </div>
      )}

      <div className="my-model card">
        <div className="my-model__header">
          <h3>My Trained Model</h3>
          <span className="badge badge--muted">Coming soon</span>
        </div>
        {stats?.active_model ? (
          <p>
            Active model <strong>{stats.active_model.version_name}</strong> trained on{' '}
            {trainingWindow.start} → {trainingWindow.end}. Personalized outputs for nearby
            coordinates will appear here as soon as they are available.
          </p>
        ) : (
          <p>
            Once you train a site-specific model, this space will highlight insights for locations
            near your assets.
          </p>
        )}
      </div>
    </div>
  );

  return (
    <div className="dashboard-page container">
      <div className="dashboard-heading">
        <div>
          <p className="eyebrow">Global Solar Intelligence</p>
          <h1>Interactive Solar Forecasting</h1>
          <p className="subhead">
            Tap anywhere on earth to stream live Solcast irradiance, PV estimates, and weather-layered insights.
          </p>
        </div>
      </div>

      {statsError && <div className="error">{statsError}</div>}
      {forecastError && <div className="error">{forecastError}</div>}

      <div className="stats-grid">
        <div className="card stats-card">
          <p className="stat-label">Total Predictions</p>
          <p className="stat-value">{stats?.total_predictions ?? '—'}</p>
        </div>
        <div className="card stats-card">
          <p className="stat-label">Total Production</p>
          <p className="stat-value">
            {stats?.total_production_kwh ? stats.total_production_kwh.toFixed(2) : '—'} kWh
          </p>
        </div>
        <div className="card stats-card">
          <p className="stat-label">Active Model</p>
          <p className="stat-value small">{stats?.active_model?.version_name || 'No active model'}</p>
          {stats?.active_model && (
            <p className="stat-meta">
              Window: {trainingWindow.start} → {trainingWindow.end}
            </p>
          )}
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="map-column card">
          <div className="map-header">
            <h2>Map Explorer</h2>
            <p>Click or search to fetch a 14-day Solcast irradiance forecast.</p>
          </div>

          <form className="map-search" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Search city, address, or coordinates"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="btn btn-secondary" disabled={searching}>
              {searching ? 'Finding...' : 'Search'}
            </button>
          </form>

          {!!searchResults.length && (
            <div className="search-results">
              {searchResults.map((result, idx) => (
                <button key={`${result.lat}-${result.lon}-${idx}`} onClick={() => handleResultSelect(result)}>
                  {result.display_name}
                </button>
              ))}
            </div>
          )}

          <div className="map-wrapper">
            <MapContainer
              center={mapCenter}
              zoom={DEFAULT_ZOOM}
              scrollWheelZoom
              whenCreated={(mapInstance) => {
                mapRef.current = mapInstance;
              }}
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors &copy; CARTO"
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              />
              <MapInteractions onSelect={handleMapSelect} />
              <MapCenterUpdater center={mapCenter} />
              {selectedCoords && (
                <Marker position={[selectedCoords.lat, selectedCoords.lon]}>
                  <Popup>
                    {forecast?.location?.display_name || 'Selected point'}
                    <br />
                    {formatNumber(selectedCoords.lat, 3)}°, {formatNumber(selectedCoords.lon, 3)}°
                  </Popup>
                </Marker>
              )}
            </MapContainer>
            {forecastLoading && <div className="map-loading">Loading Solcast data…</div>}
          </div>
        </div>

        {!isMobile && <aside className="forecast-panel card">{panelContent}</aside>}
      </div>

      {isMobile && forecast && (
        <div className="forecast-sheet" data-open={sheetOpen ? 'true' : 'false'}>
          <button className="sheet-handle" onClick={() => setSheetOpen((prev) => !prev)}>
            {sheetOpen ? 'Close details' : 'Open details'}
          </button>
          <div className="forecast-panel">{panelContent}</div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
