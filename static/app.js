/* AstroEngine PWA - Application Logic */

const API = '';  // Same origin
let currentUserId = null;

// === INIT ===
document.addEventListener('DOMContentLoaded', async () => {
  registerSW();
  setupNav();
  await loadUser();
});

function registerSW() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js').catch(() => {});
  }
}

// === NAVIGATION ===
function setupNav() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
  });
}

function switchView(viewName) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`view-${viewName}`).classList.add('active');
  document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

  if (viewName === 'history' && currentUserId) loadHistory();
  if (viewName === 'settings' && currentUserId) loadSettings();
}

// === USER MANAGEMENT ===
async function loadUser() {
  try {
    const users = await api('GET', '/users/');
    if (users.length > 0) {
      const user = users[0];
      currentUserId = user.id;
      fillProfileForm(user);
      showReadingPanel(user);
      loadNatalChart();
    }
  } catch (e) { /* No users yet */ }
}

function fillProfileForm(user) {
  document.getElementById('inp-name').value = user.name || '';
  document.getElementById('inp-birth-date').value = user.birth_date || '';
  document.getElementById('inp-birth-time').value = user.birth_time || '';
  document.getElementById('inp-birth-city').value = user.birth_city || '';
  document.getElementById('inp-current-city').value = user.current_city || '';
}

function showReadingPanel(user) {
  document.getElementById('no-user-msg').style.display = 'none';
  document.getElementById('reading-actions').style.display = 'block';
  document.getElementById('active-user-name').textContent = user.name;
}

async function saveProfile() {
  const btn = document.getElementById('btn-save-profile');
  const status = document.getElementById('profile-status');
  btn.disabled = true;

  const data = {
    name: document.getElementById('inp-name').value,
    birth_date: document.getElementById('inp-birth-date').value,
    birth_time: document.getElementById('inp-birth-time').value,
    birth_city: document.getElementById('inp-birth-city').value,
    current_city: document.getElementById('inp-current-city').value,
    language: document.getElementById('sel-language')?.value || 'es',
    report_depth: document.getElementById('sel-depth')?.value || 'complete',
    llm_model: document.getElementById('sel-model')?.value || 'gemini-3.1-flash-lite',
  };

  if (!data.name || !data.birth_date || !data.birth_time || !data.birth_city || !data.current_city) {
    status.textContent = 'Completa todos los campos';
    status.style.color = 'var(--danger)';
    btn.disabled = false;
    return;
  }

  try {
    let user;
    if (currentUserId) {
      user = await api('PATCH', `/users/${currentUserId}`, data);
    } else {
      user = await api('POST', '/users/', data);
    }
    currentUserId = user.id;
    showReadingPanel(user);
    status.textContent = 'Perfil guardado correctamente';
    status.style.color = 'var(--success)';
    toast('Perfil guardado');

    // Calcular carta natal automaticamente
    await calcNatal();
  } catch (e) {
    status.textContent = 'Error: ' + e.message;
    status.style.color = 'var(--danger)';
  }
  btn.disabled = false;
}

// === NATAL CHART ===
async function calcNatal() {
  if (!currentUserId) return;
  try {
    const result = await api('POST', '/natal/calculate', { user_id: currentUserId });
    const planets = result.natal_chart.planets;
    renderPlanets('natal-planets', planets);
    renderPlanets('quick-planets', planets.slice(0, 6));
    drawChart('natal-chart-viz', planets);
    document.getElementById('natal-card').style.display = 'block';
  } catch (e) {
    toast('Error calculando carta natal');
  }
}

async function loadNatalChart() {
  try {
    const chart = await api('GET', `/natal/${currentUserId}`);
    if (chart.chart_data_json) {
      const planets = JSON.parse(chart.chart_data_json);
      renderPlanets('natal-planets', planets);
      renderPlanets('quick-planets', planets.slice(0, 6));
      drawChart('natal-chart-viz', planets);
      document.getElementById('natal-card').style.display = 'block';
    }
  } catch (e) {
    // No natal chart yet
  }
}

function renderPlanets(containerId, planets) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = planets.map(p => {
    const retro = p.retrograde ? '<span class="retro">R</span>' : '';
    return `<span class="planet-chip">${p.name} <span class="sign">${p.sign}</span> ${retro}</span>`;
  }).join('');
}

// === READING GENERATION ===
async function generateReading() {
  if (!currentUserId) return;

  const btn = document.getElementById('btn-generate');
  const loading = document.getElementById('reading-loading');
  const result = document.getElementById('reading-result');

  btn.disabled = true;
  loading.style.display = 'flex';
  result.style.display = 'none';

  try {
    const data = await api('POST', '/reading/generate', { user_id: currentUserId });

    document.getElementById('reading-datetime').textContent = formatDate(data.transit_datetime);
    document.getElementById('reading-location').textContent = data.location;
    document.getElementById('reading-text').innerHTML = markdownToHtml(data.interpretation);

    result.style.display = 'block';
    toast('Lectura generada');
  } catch (e) {
    toast('Error: ' + e.message);
  }

  loading.style.display = 'none';
  btn.disabled = false;
}

// === SYNASTRY ===
async function generateSynastry() {
  if (!currentUserId) {
    toast('Configura tu perfil primero');
    return;
  }

  const name = document.getElementById('syn-name').value;
  const date = document.getElementById('syn-birth-date').value;
  const time = document.getElementById('syn-birth-time').value;
  const city = document.getElementById('syn-city').value;

  if (!name || !date || !city) {
    toast('Completa los datos de la otra persona');
    return;
  }

  const btn = document.querySelector('#view-synastry .btn-gold');
  const loading = document.getElementById('syn-loading');
  const result = document.getElementById('syn-result');

  btn.disabled = true;
  loading.style.display = 'flex';
  result.style.display = 'none';

  try {
    const data = await api('POST', '/synastry/calculate', {
      user_id_1: currentUserId,
      guest_name: name,
      guest_birth_date: date,
      guest_birth_time: time,
      guest_birth_city: city
    });

    document.getElementById('syn-partner-name').textContent = `Con ${data.p2_name}`;
    document.getElementById('syn-text').innerHTML = markdownToHtml(data.resolution);

    result.style.display = 'block';
    toast('Resolución generada');
  } catch (e) {
    toast('Error: ' + e.message);
  }

  loading.style.display = 'none';
  btn.disabled = false;
}

// === SETTINGS ===
async function loadSettings() {
  if (!currentUserId) return;
  try {
    const user = await api('GET', `/users/${currentUserId}`);
    document.getElementById('sel-language').value = user.language || 'es';
    document.getElementById('sel-depth').value = user.report_depth || 'complete';
    document.getElementById('sel-model').value = user.llm_model || 'gemini-3.1-flash-lite';
  } catch (e) {}
}

async function saveSettings() {
  if (!currentUserId) return;
  const status = document.getElementById('settings-status');
  try {
    await api('PATCH', `/users/${currentUserId}`, {
      language: document.getElementById('sel-language').value,
      report_depth: document.getElementById('sel-depth').value,
      llm_model: document.getElementById('sel-model').value,
    });
    status.textContent = 'Ajustes guardados';
    status.style.color = 'var(--success)';
    toast('Ajustes guardados');
  } catch (e) {
    status.textContent = 'Error: ' + e.message;
    status.style.color = 'var(--danger)';
  }
}

// === HISTORY ===
async function loadHistory() {
  if (!currentUserId) return;
  const list = document.getElementById('history-list');
  const empty = document.getElementById('history-empty');

  try {
    const data = await api('GET', `/reading/history/${currentUserId}?limit=20`);
    if (data.readings.length === 0) {
      empty.style.display = 'block';
      list.innerHTML = '';
      return;
    }
    empty.style.display = 'none';
    list.innerHTML = data.readings.map(r => `
      <div class="history-item" onclick="showReading('${escapeHtml(r.interpretation)}', '${r.created_at}')">
        <div class="history-date">${formatDate(r.created_at)}</div>
        <div class="history-location">${r.location_used}</div>
      </div>
    `).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:var(--text-muted);text-align:center;">Error cargando historial</p>';
  }
}

function showReading(text, date) {
  document.getElementById('modal-title').textContent = formatDate(date);
  document.getElementById('modal-content').innerHTML = markdownToHtml(text);
  document.getElementById('modal-overlay').classList.add('show');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('show');
}

// === UTILITIES ===
async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const timeout = method === 'POST' && path.includes('reading') ? 120000 : 15000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  opts.signal = controller.signal;

  try {
    const r = await fetch(API + path, opts);
    clearTimeout(timer);
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: 'Error del servidor' }));
      throw new Error(err.detail || `HTTP ${r.status}`);
    }
    return r.json();
  } catch (e) {
    clearTimeout(timer);
    if (e.name === 'AbortError') throw new Error('Tiempo de espera agotado');
    throw e;
  }
}

function markdownToHtml(md) {
  if (!md) return '';
  let html = md
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/---/g, '<hr>')
    .replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>')
    .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

  // Wrap blocks that are not headers or lists in paragraphs
  return html.split('\n\n').map(block => {
    if (block.startsWith('<h') || block.startsWith('<ul') || block.startsWith('<ol') || block.startsWith('<hr')) {
      return block;
    }
    return `<p>${block.replace(/\n/g, '<br>')}</p>`;
  }).join('');
}

function formatDate(dt) {
  if (!dt) return '--';
  try {
    const d = new Date(dt.replace(' ', 'T'));
    return d.toLocaleDateString('es-CL', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  } catch { return dt; }
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/'/g, "\\'").replace(/\n/g, '\\n');
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

function drawChart(containerId, planets) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const size = 300;
  const center = size / 2;
  const radius = size * 0.4;
  
  const signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS'];
  const colors = ['#f87171', '#fbbf24', '#34d399', '#60a5fa', '#f87171', '#fbbf24', '#34d399', '#60a5fa', '#f87171', '#fbbf24', '#34d399', '#60a5fa'];

  let svg = `<svg viewBox="0 0 ${size} ${size}">
    <!-- Círculo exterior -->
    <circle cx="${center}" cy="${center}" r="${radius}" class="chart-circle" />
    <circle cx="${center}" cy="${center}" r="${radius * 0.7}" class="chart-circle" />
    
    <!-- Divisiones de signos -->
    ${signs.map((s, i) => {
      const angle = i * 30 - 90;
      const x1 = center + radius * Math.cos(angle * Math.PI / 180);
      const y1 = center + radius * Math.sin(angle * Math.PI / 180);
      const x2 = center + radius * 0.7 * Math.cos(angle * Math.PI / 180);
      const y2 = center + radius * 0.7 * Math.sin(angle * Math.PI / 180);
      
      const textAngle = angle + 15;
      const tx = center + radius * 0.85 * Math.cos(textAngle * Math.PI / 180);
      const ty = center + radius * 0.85 * Math.sin(textAngle * Math.PI / 180);
      
      return `
        <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="chart-line" />
        <text x="${tx}" y="${ty}" class="chart-text" text-anchor="middle" alignment-baseline="middle" transform="rotate(${textAngle + 90}, ${tx}, ${ty})">${s}</text>
      `;
    }).join('')}
    
    <!-- Planetas -->
    ${planets.map(p => {
      // Calcular ángulo basado en el signo y grado (simplificado)
      const signIdx = signs.indexOf(p.sign.substring(0, 3).toUpperCase());
      const angle = (signIdx * 30 + (p.longitude % 30)) - 90;
      const px = center + radius * 0.55 * Math.cos(angle * Math.PI / 180);
      const py = center + radius * 0.55 * Math.sin(angle * Math.PI / 180);
      
      // Iconos o letras para planetas
      const icons = { 'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂', 'Jupiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Pluton': '♇' };
      const icon = icons[p.name] || p.name[0];
      
      return `
        <text x="${px}" y="${py}" class="chart-planet" fill="${p.retrograde ? 'var(--gold)' : 'var(--accent-soft)'}" text-anchor="middle" alignment-baseline="middle">${icon}</text>
      `;
    }).join('')}
  </svg>`;
  
  container.innerHTML = svg;
}

// Close modal on overlay click
document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});
