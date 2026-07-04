const CURRENCIES = [
  'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR',
  'BRL', 'KRW', 'MXN', 'SGD', 'NZD', 'SEK', 'NOK', 'TRY',
];

const form = document.getElementById('search-form');
const cityInput = document.getElementById('city-input');
const currencySelect = document.getElementById('currency-select');
const searchBtn = document.getElementById('search-btn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');

const cityName = document.getElementById('city-name');
const recText = document.getElementById('rec-text');
const scoreValue = document.getElementById('score-value');
const scoreCircle = document.getElementById('score-circle');
const weatherTemp = document.getElementById('weather-temp');
const weatherCond = document.getElementById('weather-cond');
const weatherDetails = document.getElementById('weather-details');
const exchangeBase = document.getElementById('exchange-base');
const exchangeRate = document.getElementById('exchange-rate');
const recContent = document.getElementById('rec-content');

// Settings modal
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const modalClose = document.getElementById('modal-close');
const modalSave = document.getElementById('modal-save');
const modalClear = document.getElementById('modal-clear');
const weatherKeyInput = document.getElementById('weather-key');
const exchangeKeyInput = document.getElementById('exchange-key');

const RING_RADIUS = 38;
const CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;
let isSearching = false;

// --- Currencies ---
function populateCurrencies() {
  CURRENCIES.forEach((c) => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    currencySelect.appendChild(opt);
  });
}

// --- Settings ---
function loadKeys() {
  weatherKeyInput.value = localStorage.getItem('weather_api_key') || '';
  exchangeKeyInput.value = localStorage.getItem('exchange_api_key') || '';
}

function saveKeys() {
  const w = weatherKeyInput.value.trim();
  const e = exchangeKeyInput.value.trim();
  if (w) localStorage.setItem('weather_api_key', w);
  else localStorage.removeItem('weather_api_key');
  if (e) localStorage.setItem('exchange_api_key', e);
  else localStorage.removeItem('exchange_api_key');
}

function clearKeys() {
  weatherKeyInput.value = '';
  exchangeKeyInput.value = '';
  localStorage.removeItem('weather_api_key');
  localStorage.removeItem('exchange_api_key');
}

function openModal() {
  loadKeys();
  settingsModal.classList.add('open');
}

function closeModal() {
  settingsModal.classList.remove('open');
}

settingsBtn.addEventListener('click', openModal);
modalClose.addEventListener('click', closeModal);
settingsModal.addEventListener('click', (e) => {
  if (e.target === settingsModal) closeModal();
});

modalSave.addEventListener('click', () => {
  saveKeys();
  closeModal();
});

modalClear.addEventListener('click', () => {
  clearKeys();
  closeModal();
});

// --- Score helpers ---
function getScoreColor(score) {
  if (score >= 75) return '#22c55e';
  if (score >= 50) return '#eab308';
  return '#ef4444';
}

function getScoreLabel(score) {
  if (score >= 75) return 'Excellent';
  if (score >= 50) return 'Moderate';
  return 'Poor';
}

function updateScoreRing(score) {
  const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
  scoreCircle.style.strokeDasharray = `${CIRCUMFERENCE}`;
  scoreCircle.style.strokeDashoffset = `${offset}`;
  scoreCircle.style.stroke = getScoreColor(score);
  scoreValue.textContent = score;
}

// --- UI state ---
function showError(msg) {
  error.textContent = msg;
  error.classList.add('show');
  results.classList.remove('show');
}

function hideError() {
  error.classList.remove('show');
}

function showLoading() {
  loading.classList.add('show');
  results.classList.remove('show');
  hideError();
  searchBtn.disabled = true;
}

function hideLoading() {
  loading.classList.remove('show');
  searchBtn.disabled = false;
}

// --- Render ---
function renderWeather(data) {
  weatherDetails.innerHTML = '';
  const rows = [
    { label: 'Condition', value: data.condition },
    { label: 'Humidity', value: `${data.humidity}%` },
    { label: 'Wind Speed', value: `${data.wind_kph} km/h` },
    { label: 'Daylight', value: data.is_day ? 'Daytime' : 'Nighttime' },
  ];

  rows.forEach((r) => {
    const div = document.createElement('div');
    div.className = 'detail-item';
    div.innerHTML = `<span class="label">${r.label}</span><span class="val">${r.value}</span>`;
    weatherDetails.appendChild(div);
  });
}

function getRecBadgeClass(score, temp) {
  if (temp > 35 || temp < 5) return 'bad';
  if (score > 75) return 'great';
  return 'okay';
}

function renderResults(data) {
  cityName.textContent = data.city;
  recText.textContent = getScoreLabel(data.travel_score);
  updateScoreRing(data.travel_score);

  weatherTemp.textContent = `${data.weather.temp_c}°C`;
  weatherCond.textContent = data.weather.condition;
  renderWeather(data.weather);

  exchangeBase.textContent = `${data.exchange.base} → ${data.exchange.target}`;
  exchangeRate.textContent = `${data.exchange.rate}`;

  const badgeClass = getRecBadgeClass(data.travel_score, data.weather.temp_c);
  recContent.innerHTML = `<span class="rec-badge ${badgeClass}">💬 ${data.recommendation}</span>`;

  results.classList.add('show');
}

// --- Search ---
async function handleSearch(e) {
  if (e) e.preventDefault();

  const city = cityInput.value.trim();
  if (!city || city.length < 2) {
    showError('Please enter a city name (at least 2 characters).');
    return;
  }

  if (isSearching) return;
  isSearching = true;

  const currency = currencySelect.value;
  showLoading();

  const headers = {};
  const wk = localStorage.getItem('weather_api_key');
  const ek = localStorage.getItem('exchange_api_key');
  if (wk) headers['X-Weather-Api-Key'] = wk;
  if (ek) headers['X-Exchange-Api-Key'] = ek;

  try {
    const resp = await fetch(
      `/api/v1/search?city=${encodeURIComponent(city)}&currency=${currency}`,
      { headers },
    );
    const data = await resp.json();

    if (!resp.ok) {
      showError(data.error || 'Something went wrong.');
      return;
    }

    hideError();
    renderResults(data);
  } catch (err) {
    showError('Network error — could not reach the API.');
  } finally {
    hideLoading();
    isSearching = false;
  }
}

populateCurrencies();
form.addEventListener('submit', handleSearch);
cityInput.focus();
