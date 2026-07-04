const CURRENCIES = [
  'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR',
  'BRL', 'KRW', 'MXN', 'SGD', 'NZD', 'SEK', 'NOK', 'TRY',
];
const WEATHER_EMOJI = {
  'sunny': '☀️', 'clear': '🌙', 'cloudy': '☁️', 'partly cloudy': '⛅',
  'overcast': '☁️', 'rain': '🌧️', 'light rain': '🌦️', 'moderate rain': '🌧️',
  'heavy rain': '🌧️', 'thunder': '⛈️', 'snow': '❄️', 'light snow': '🌨️',
  'fog': '🌫️', 'mist': '🌫️', 'drizzle': '🌦️',
};
const RING_RADIUS = 38;
const CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;
let currentMap = null;
let isSearching = false;
let authToken = localStorage.getItem('auth_token') || null;

const $ = id => document.getElementById(id);
const views = {};
document.querySelectorAll('.view').forEach(v => { views[v.id.replace('view-', '')] = v; });

function navigate(view) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const target = views[view];
  if (target) target.classList.add('active');
  const link = document.querySelector(`.nav-link[data-view="${view}"]`);
  if (link) link.classList.add('active');
  updateAuthUI();
  if (view === 'favorites') loadFavorites();
  if (view === 'history') loadHistory();
}

window.addEventListener('hashchange', () => {
  const view = location.hash.slice(1) || 'dashboard';
  navigate(view);
});

function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  document.getElementById('theme-toggle').textContent = saved === 'dark' ? '🌙 Dark' : '☀️ Light';
}
document.getElementById('theme-toggle').addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  document.getElementById('theme-toggle').textContent = next === 'dark' ? '🌙 Dark' : '☀️ Light';
});

document.getElementById('sidebar-toggle').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('open');
});
document.querySelectorAll('.nav-link').forEach(l => {
  l.addEventListener('click', () => document.getElementById('sidebar').classList.remove('open'));
});

(function populateCurrencies() {
  const sel = document.getElementById('currency-select');
  CURRENCIES.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; sel.appendChild(o); });
})();

function updateAuthUI() {
  const link = document.getElementById('auth-link');
  link.textContent = authToken ? '👤 Account' : '👤 Sign In';
}

document.getElementById('show-register').addEventListener('click', e => {
  e.preventDefault();
  document.getElementById('login-form-card').style.display = 'none';
  document.getElementById('register-form-card').style.display = 'block';
});
document.getElementById('show-login').addEventListener('click', e => {
  e.preventDefault();
  document.getElementById('login-form-card').style.display = 'block';
  document.getElementById('register-form-card').style.display = 'none';
});

async function authFetch(path, body) {
  const resp = await fetch(`/api/v1${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return resp;
}

document.getElementById('login-form').addEventListener('submit', async e => {
  e.preventDefault();
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;
  const err = document.getElementById('auth-error');
  try {
    const resp = await authFetch('/auth/login', { username, password });
    const data = await resp.json();
    if (!resp.ok) { err.textContent = data.detail || 'Login failed'; err.classList.add('show'); return; }
    err.classList.remove('show');
    authToken = data.access_token;
    localStorage.setItem('auth_token', authToken);
    document.getElementById('auth-success-msg').textContent = `Welcome back, ${data.user.username}!`;
    document.getElementById('login-form-card').style.display = 'none';
    document.getElementById('register-form-card').style.display = 'none';
    document.getElementById('auth-success').style.display = 'block';
    updateAuthUI();
    setTimeout(() => navigate('dashboard'), 1500);
  } catch { err.textContent = 'Network error'; err.classList.add('show'); }
});

document.getElementById('register-form').addEventListener('submit', async e => {
  e.preventDefault();
  const username = document.getElementById('reg-username').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const err = document.getElementById('auth-error');
  if (password.length < 6) { err.textContent = 'Password must be at least 6 characters'; err.classList.add('show'); return; }
  try {
    const resp = await authFetch('/auth/register', { username, email, password });
    const data = await resp.json();
    if (!resp.ok) { err.textContent = data.detail || 'Registration failed'; err.classList.add('show'); return; }
    err.classList.remove('show');
    authToken = data.access_token;
    localStorage.setItem('auth_token', authToken);
    document.getElementById('auth-success-msg').textContent = `Welcome, ${data.user.username}!`;
    document.getElementById('login-form-card').style.display = 'none';
    document.getElementById('register-form-card').style.display = 'none';
    document.getElementById('auth-success').style.display = 'block';
    updateAuthUI();
    setTimeout(() => navigate('dashboard'), 1500);
  } catch { err.textContent = 'Network error'; err.classList.add('show'); }
});

document.getElementById('settings-save').addEventListener('click', () => {
  const w = document.getElementById('weather-key').value.trim();
  const e = document.getElementById('exchange-key').value.trim();
  if (w) localStorage.setItem('weather_api_key', w); else localStorage.removeItem('weather_api_key');
  if (e) localStorage.setItem('exchange_api_key', e); else localStorage.removeItem('exchange_api_key');
  alert('API keys saved!');
});
document.getElementById('settings-clear').addEventListener('click', () => {
  document.getElementById('weather-key').value = '';
  document.getElementById('exchange-key').value = '';
  localStorage.removeItem('weather_api_key');
  localStorage.removeItem('exchange_api_key');
});
function loadSettingsKeys() {
  document.getElementById('weather-key').value = localStorage.getItem('weather_api_key') || '';
  document.getElementById('exchange-key').value = localStorage.getItem('exchange_api_key') || '';
}
document.querySelector('.nav-link[data-view="settings"]').addEventListener('click', loadSettingsKeys);

function getScoreColor(s) { return s >= 75 ? '#22c55e' : s >= 50 ? '#eab308' : '#ef4444'; }
function getScoreLabel(s) { return s >= 75 ? 'Excellent' : s >= 50 ? 'Moderate' : 'Poor'; }
function getWeatherEmoji(c) {
  const cl = c.toLowerCase();
  for (const [k, v] of Object.entries(WEATHER_EMOJI)) { if (cl.includes(k)) return v; }
  return '🌡️';
}
function showError(el, msg) { el.textContent = msg; el.classList.add('show'); }
function hideError(el) { el.classList.remove('show'); }

function updateScoreRing(score) {
  const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
  const circle = document.getElementById('score-circle');
  circle.style.strokeDasharray = `${CIRCUMFERENCE}`;
  circle.style.strokeDashoffset = `${offset}`;
  circle.style.stroke = getScoreColor(score);
  document.getElementById('score-value').textContent = score;
}

function getApiHeaders() {
  const h = {};
  const wk = localStorage.getItem('weather_api_key');
  const ek = localStorage.getItem('exchange_api_key');
  if (wk) h['X-Weather-Api-Key'] = wk;
  if (ek) h['X-Exchange-Api-Key'] = ek;
  return h;
}

function renderForecast(forecast) {
  if (!forecast || !forecast.length) return;
  const card = document.getElementById('forecast-card');
  card.style.display = 'block';
  const grid = document.getElementById('forecast-grid');
  grid.innerHTML = '';
  forecast.forEach(d => {
    const date = new Date(d.date + 'T12:00:00');
    const dayName = date.toLocaleDateString('en', { weekday: 'short' });
    const emoji = getWeatherEmoji(d.condition);
    const div = document.createElement('div');
    div.className = 'forecast-day';
    div.innerHTML = `
      <div class="day-name">${dayName}</div>
      <div class="day-icon">${emoji}</div>
      <div class="day-temp">${Math.round(d.max_temp_c)}° <span class="low">${Math.round(d.min_temp_c)}°</span></div>
      ${d.chance_of_rain > 0 ? `<div class="day-rain">🌧️ ${d.chance_of_rain}%</div>` : ''}
    `;
    grid.appendChild(div);
  });
}

function renderAttractions(attractions) {
  if (!attractions || !attractions.length) return;
  const card = document.getElementById('attractions-card');
  card.style.display = 'block';
  const list = document.getElementById('attractions-list');
  list.innerHTML = '';
  const kinds = { 'cultural': '🎨', 'natural': '🌿', 'architecture': '🏛️', 'historical': '📜', 'amusements': '🎡', 'religious': '⛪', 'sport': '⚽', 'food': '🍽️' };
  attractions.forEach(a => {
    let icon = '📍';
    for (const [k, v] of Object.entries(kinds)) { if (a.kinds.includes(k)) { icon = v; break; } }
    const div = document.createElement('div');
    div.className = 'attraction-item';
    div.innerHTML = `<span class="attr-icon">${icon}</span><span class="attr-name">${a.name}</span><span class="attr-kind">${a.kinds.split(',')[0] || ''}</span>`;
    list.appendChild(div);
  });
}

function renderCountryInfo(info) {
  if (!info) return;
  const meta = document.getElementById('city-meta');
  const items = [
    info.flag ? `<span class="meta-tag">${info.flag} ${info.name}</span>` : '',
    info.capital ? `<span class="meta-tag">🏛️ ${info.capital}</span>` : '',
    info.region ? `<span class="meta-tag">🌍 ${info.region}</span>` : '',
    info.population ? `<span class="meta-tag">👥 ${(info.population / 1e6).toFixed(1)}M</span>` : '',
    info.currencies?.length ? `<span class="meta-tag">💱 ${info.currencies.join(', ')}</span>` : '',
  ].filter(Boolean);
  meta.innerHTML = items.join('');
}

function renderBreakdown(breakdown) {
  const bars = document.getElementById('breakdown-bars');
  bars.innerHTML = '';
  const items = [
    { label: 'Temperature', value: breakdown.temperature_score, weight: breakdown.temperature_weight, color: getScoreColor(breakdown.temperature_score) },
    { label: 'Humidity', value: breakdown.humidity_score, weight: breakdown.humidity_weight, color: getScoreColor(breakdown.humidity_score) },
    { label: 'Total Score', value: breakdown.total, weight: 1, color: getScoreColor(breakdown.total), bold: true },
  ];
  items.forEach((item, i) => {
    const row = document.createElement('div');
    row.className = 'breakdown-row';
    row.innerHTML = `
      <span class="label">${item.label}${item.weight < 1 ? ` (${Math.round(item.weight * 100)}%)` : ''}</span>
      <div class="bar-track"><div class="bar-fill" style="width:0%;background:${item.color};${item.bold ? 'height:10px;' : ''}"></div></div>
      <span class="bar-val" style="${item.bold ? 'font-size:0.9rem;' : ''}">${item.value}</span>
    `;
    bars.appendChild(row);
    setTimeout(() => row.querySelector('.bar-fill').style.width = `${item.value}%`, 100 + i * 100);
  });
}

function renderWeatherDetails(w) {
  const container = document.getElementById('weather-details');
  container.innerHTML = '';
  const rows = [
    { label: 'Condition', value: `${getWeatherEmoji(w.condition)} ${w.condition}` },
    { label: 'Humidity', value: `${w.humidity}%` },
    { label: 'Wind Speed', value: `${w.wind_kph} km/h` },
    { label: 'Daylight', value: w.is_day ? '☀️ Daytime' : '🌙 Nighttime' },
  ];
  rows.forEach(r => {
    const div = document.createElement('div'); div.className = 'detail-item';
    div.innerHTML = `<span class="label">${r.label}</span><span class="val">${r.value}</span>`;
    container.appendChild(div);
  });
}

function initMap(lat, lon, label) {
  const card = document.getElementById('map-card');
  card.style.display = 'block';
  if (currentMap) { currentMap.remove(); currentMap = null; }
  currentMap = L.map('map').setView([lat, lon], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18, attribution: '© OpenStreetMap',
  }).addTo(currentMap);
  L.marker([lat, lon]).addTo(currentMap).bindPopup(label);
  setTimeout(() => currentMap.invalidateSize(), 300);
}

async function handleSearch(e) {
  if (e) e.preventDefault();
  const city = document.getElementById('city-input').value.trim();
  if (!city || city.length < 2) { showError(document.getElementById('error'), 'Enter a city name'); return; }
  if (isSearching) return;
  isSearching = true;

  const currency = document.getElementById('currency-select').value;
  const include = [];
  if (document.getElementById('inc-forecast').checked) include.push('forecast');
  if (document.getElementById('inc-attractions').checked) include.push('attractions');
  if (document.getElementById('inc-country').checked) include.push('country');

  document.getElementById('loading').classList.add('show');
  document.getElementById('results').style.display = 'none';
  hideError(document.getElementById('error'));
  document.getElementById('search-btn').disabled = true;

  try {
    const params = new URLSearchParams({ city, currency });
    if (include.length) params.set('include', include.join(','));
    const resp = await fetch(`/api/v1/search?${params}`, { headers: getApiHeaders() });
    const data = await resp.json();
    if (!resp.ok) { showError(document.getElementById('error'), data.error || 'Search failed'); return; }

    document.getElementById('results').style.display = 'block';
    document.getElementById('city-name').textContent = data.city;
    document.getElementById('rec-text').textContent = getScoreLabel(data.travel_score);
    updateScoreRing(data.travel_score);
    document.getElementById('weather-temp').textContent = `${data.weather.temp_c}°C`;
    document.getElementById('weather-cond').textContent = `${getWeatherEmoji(data.weather.condition)} ${data.weather.condition}`;
    document.getElementById('exchange-base').textContent = `${data.exchange.base} → ${data.exchange.target}`;
    document.getElementById('exchange-rate').textContent = `${data.exchange.rate}`;
    renderWeatherDetails(data.weather);
    renderBreakdown(data.score_breakdown);
    document.getElementById('rec-content').innerHTML = `<span class="rec-badge ${data.travel_score >= 75 ? 'great' : data.travel_score >= 50 ? 'okay' : 'bad'}">💬 ${data.recommendation}</span>`;
    document.getElementById('city-country').textContent = data.country_info?.name || '';
    renderCountryInfo(data.country_info);
    renderForecast(data.forecast);
    renderAttractions(data.attractions);

    const lat = data.weather?.lat || data.attractions?.[0]?.lat || null;
    const lon = data.weather?.lon || data.attractions?.[0]?.lon || null;
    if (lat && lon) initMap(lat, lon, data.city);

    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch { showError(document.getElementById('error'), 'Network error — could not reach the API.'); }
  finally {
    document.getElementById('loading').classList.remove('show');
    document.getElementById('search-btn').disabled = false;
    isSearching = false;
  }
}

document.getElementById('search-form').addEventListener('submit', handleSearch);
document.getElementById('city-input').addEventListener('keydown', e => { if (e.key === 'Enter') handleSearch(e); });

async function handleCompare(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('compare-input').value.trim();
  if (!input) { showError(document.getElementById('compare-error'), 'Enter at least one city'); return; }
  document.getElementById('compare-loading').style.display = 'block';
  document.getElementById('compare-results').style.display = 'none';
  hideError(document.getElementById('compare-error'));
  try {
    const resp = await fetch(`/api/v1/compare?cities=${encodeURIComponent(input)}&currency=EUR`, { headers: getApiHeaders() });
    const data = await resp.json();
    if (!resp.ok) { showError(document.getElementById('compare-error'), data.error || 'Compare failed'); return; }
    const tbody = document.getElementById('compare-body');
    tbody.innerHTML = '';
    data.results.forEach((r, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="rank">${i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i + 1}`}</td>
        <td><strong>${r.city}</strong></td>
        <td class="score-cell" style="color:${getScoreColor(r.travel_score)}">${r.travel_score}</td>
        <td>${r.weather.temp_c}°C</td>
        <td>${getWeatherEmoji(r.weather.condition)} ${r.weather.condition}</td>
        <td>${r.exchange.rate}</td>
      `;
      tbody.appendChild(tr);
    });
    document.getElementById('compare-results').style.display = 'block';
  } catch { showError(document.getElementById('compare-error'), 'Network error'); }
  finally { document.getElementById('compare-loading').style.display = 'none'; }
}
document.getElementById('compare-form').addEventListener('submit', handleCompare);

async function loadFavorites() {
  const container = document.getElementById('favorites-list');
  if (!authToken) { container.innerHTML = '<div class="empty-state">🔒 Sign in to save and sync your favorite cities.</div>'; return; }
  try {
    const resp = await fetch('/api/v1/me/favorites', { headers: { ...getApiHeaders(), Authorization: `Bearer ${authToken}` } });
    if (!resp.ok) { container.innerHTML = '<div class="empty-state">Could not load favorites.</div>'; return; }
    const data = await resp.json();
    if (!data.length) { container.innerHTML = '<div class="empty-state">No favorites yet. Search a city and add it!</div>'; return; }
    container.innerHTML = '<div class="fav-grid"></div>';
    const grid = container.querySelector('.fav-grid');
    data.forEach(f => {
      const div = document.createElement('div'); div.className = 'fav-card';
      div.innerHTML = `<div class="fav-city">📍 ${f.city_name}</div><div class="fav-score" style="color:${getScoreColor(f.travel_score || 50)}">${f.travel_score || '—'}</div>${f.country ? `<div style="font-size:0.75rem;color:var(--text-secondary)">${f.country}</div>` : ''}<button class="fav-remove" data-city="${f.city_name}">✕ Remove</button>`;
      div.querySelector('.fav-remove').addEventListener('click', async e => {
        e.stopPropagation();
        await fetch(`/api/v1/me/favorites/${f.city_name}`, { method: 'DELETE', headers: { Authorization: `Bearer ${authToken}` } });
        loadFavorites();
      });
      div.addEventListener('click', () => {
        document.getElementById('city-input').value = f.city_name;
        navigate('dashboard');
        handleSearch(new Event('submit'));
      });
      grid.appendChild(div);
    });
  } catch { container.innerHTML = '<div class="empty-state">Could not load favorites.</div>'; }
}

async function addCurrentToFavorites() {
  if (!authToken) { showError(document.getElementById('error'), 'Sign in to save favorites'); return; }
  const city = document.getElementById('city-name').textContent;
  if (!city || city === '—') return;
  await fetch('/api/v1/me/favorites', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authToken}` },
    body: JSON.stringify({ city_name: city }),
  });
}

const favBtn = document.createElement('button');
favBtn.className = 'btn secondary';
favBtn.style.cssText = 'font-size:0.75rem;padding:0.3rem 0.6rem;margin-left:0.5rem';
favBtn.textContent = '❤️ Save';
favBtn.addEventListener('click', addCurrentToFavorites);
const cityInfo = document.querySelector('#hero-card .city-info h2');
if (cityInfo) cityInfo.after(favBtn);

async function loadHistory() {
  const container = document.getElementById('history-list');
  if (!authToken) { container.innerHTML = '<div class="empty-state">🔒 Sign in to see your search history.</div>'; return; }
  try {
    const resp = await fetch('/api/v1/me/history', { headers: { Authorization: `Bearer ${authToken}` } });
    if (!resp.ok) { container.innerHTML = '<div class="empty-state">Could not load history.</div>'; return; }
    const data = await resp.json();
    if (!data.length) { container.innerHTML = '<div class="empty-state">No search history yet.</div>'; return; }
    container.innerHTML = '<div class="fav-grid"></div>';
    const grid = container.querySelector('.fav-grid');
    data.forEach(h => {
      const div = document.createElement('div'); div.className = 'fav-card';
      const date = new Date(h.timestamp).toLocaleDateString();
      div.innerHTML = `<div class="fav-city">📍 ${h.city_name}</div><div class="fav-score" style="color:${getScoreColor(h.travel_score || 0)}">${h.travel_score || '—'}</div><div style="font-size:0.7rem;color:var(--text-tertiary)">${date}</div>`;
      div.addEventListener('click', () => {
        document.getElementById('city-input').value = h.city_name;
        navigate('dashboard');
        handleSearch(new Event('submit'));
      });
      grid.appendChild(div);
    });
  } catch { container.innerHTML = '<div class="empty-state">Could not load history.</div>'; }
}

initTheme();
const initialView = location.hash.slice(1) || 'dashboard';
navigate(initialView);
document.getElementById('city-input').focus();
