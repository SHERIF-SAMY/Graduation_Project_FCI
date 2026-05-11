const API_BASE = 'http://127.0.0.1:8000';

// ─── Generate unique session ID per browser session ───
const SESSION_ID = sessionStorage.getItem('nexon_session_id') || (() => {
  const id = 'sess_' + Math.random().toString(36).slice(2, 11) + Date.now().toString(36);
  sessionStorage.setItem('nexon_session_id', id);
  return id;
})();

console.log('[Nexon] Session ID:', SESSION_ID);
const CATEGORY_ICONS = {
  electronics: '📱', computers: '💻', sports: '🚴', gaming: '🎮',
  audio: '🎧', cameras: '📷', photography: '📸', projectors: '📽️',
  tools: '🔧', furniture: '🪑', default: '📦'
};

function getCategoryIcon(name) {
  const lower = (name || '').toLowerCase();
  for (const [key, icon] of Object.entries(CATEGORY_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return CATEGORY_ICONS.default;
}

function getProductIcon(category, name) {
  return getCategoryIcon(category || name || '');
}

// ─── State ───
let isLoading = false;
let currentCategory = null;

// ─── Init ───
document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  loadCategories();
  document.getElementById('chat-input').focus();
  fetchRecommendations(); // Fetch initially for Discover view
});

// ─── Tab Switching ───
function switchTab(tabId) {
  // Update buttons
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');
  
  // Update views
  document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
  document.getElementById(`${tabId}-view`).classList.add('active');
  
  if (tabId === 'chat') {
    document.getElementById('chat-input').focus();
  } else if (tabId === 'discover') {
    fetchRecommendations();
  }
}

// ─── Recommendations ───
async function fetchRecommendations() {
  const grid = document.getElementById('recommendations-grid');
  const metadata = document.getElementById('rec-metadata');
  const explanation = document.getElementById('rec-explanation');
  
  grid.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text3);">Loading recommendations...</div>';
  
  try {
    const res = await fetch(`${API_BASE}/recommendations?session_id=${SESSION_ID}&limit=6`);
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    const data = await res.json();
    
    // Update Metadata Badge
    const isCold = data.recommendation_type === 'cold_start';
    const confScore = Math.round(data.user_profile.profile_confidence * 100);
    metadata.innerHTML = `
      <span class="rec-badge ${isCold ? 'cold' : ''}">
        ${isCold ? 'Trending & Newest' : 'Personalized'}
      </span>
      <span style="font-size: 11px; color: var(--text3);">Confidence: ${confScore}%</span>
      <span style="font-size: 11px; color: var(--text3); margin-left: auto;">${data.latency_ms}ms</span>
    `;
    
    // Update Explanation
    if (data.explanation) {
      explanation.style.display = 'block';
      explanation.innerHTML = escapeHtml(data.explanation);
    } else {
      explanation.style.display = 'none';
    }
    
    // Render Products
    if (data.products && data.products.length > 0) {
      grid.innerHTML = data.products.map((p, i) => {
        // Find matching debug info if available
        const debugInfo = data.debug ? data.debug.find(d => d.id === p.id) : null;
        return productCard(p, debugInfo);
      }).join('');
    } else {
      grid.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text3);">No recommendations available yet.</div>';
    }
    
  } catch (err) {
    console.error(err);
    grid.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--red);">Failed to load recommendations. Make sure backend is running.</div>';
  }
}

// ─── Health check ───
async function checkHealth() {
  const dot = document.getElementById('health-dot');
  const text = document.getElementById('health-text');
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    if (data.db === 'ok') {
      dot.className = 'health-dot ok';
      text.textContent = 'All systems online';
    } else {
      dot.className = 'health-dot error';
      text.textContent = `DB: ${data.db}`;
    }
  } catch {
    dot.className = 'health-dot error';
    text.textContent = 'Service offline';
  }
  // Re-check every 30 seconds
  setTimeout(checkHealth, 30000);
}

// ─── Load Categories ───
async function loadCategories() {
  const list = document.getElementById('categories-list');
  try {
    const res = await fetch(`${API_BASE}/categories`);
    const data = await res.json();
    const cats = data.categories || [];

    if (!cats.length) {
      list.innerHTML = '<p style="color:var(--text3);font-size:12px;">No categories found</p>';
      return;
    }

    list.innerHTML = cats.map(c => `
      <div class="category-item" id="cat-${c.CategoryId}" onclick="filterByCategory('${c.CategoryName}', ${c.CategoryId})">
        <span class="category-dot"></span>
        ${getCategoryIcon(c.CategoryName)} ${c.CategoryName}
      </div>
    `).join('');
  } catch {
    list.innerHTML = '<p style="color:var(--text3);font-size:12px;">Failed to load</p>';
  }
}

// ─── Filter by category (sends as chat query) ───
function filterByCategory(name, id) {
  document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
  const el = document.getElementById(`cat-${id}`);
  if (el) el.classList.add('active');
  currentCategory = name;
  sendSuggestion(`Show me available ${name} products`);
}

// ─── Keyboard handler ───
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ─── Auto-resize textarea ───
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

// ─── Send suggestion chip ───
function sendSuggestion(text) {
  document.getElementById('chat-input').value = text;
  sendMessage();
}

// ─── Main send message ───
async function sendMessage() {
  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query || isLoading) return;

  // Hide welcome screen
  document.getElementById('welcome-screen').style.display = 'none';

  // Add user message
  appendMessage('user', query);
  input.value = '';
  input.style.height = 'auto';

  // Show typing
  const typingId = showTyping();
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: SESSION_ID })   // ← send session_id
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    removeTyping(typingId);
    appendAIMessage(data);
  } catch (err) {
    removeTyping(typingId);
    appendMessage('ai', `⚠️ Error: ${err.message}. Please check if the server is running.`);
  } finally {
    setLoading(false);
  }
}

// ─── Append user message ───
function appendMessage(role, text) {
  const list = document.getElementById('messages-list');
  const isAI = role === 'ai';
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="message-avatar">${isAI ? '🤖' : '👤'}</div>
    <div class="message-content">
      <div class="message-bubble">${escapeHtml(text)}</div>
    </div>`;
  list.appendChild(div);
  scrollToBottom();
}

// ─── Append full AI response with products ───
function appendAIMessage(data) {
  const list = document.getElementById('messages-list');
  const div = document.createElement('div');
  div.className = 'message ai';

  const products = (data.products || []).slice(0, 6);
  const productCards = products.length ? `
    <div class="products-grid">
      ${products.map(p => productCard(p)).join('')}
    </div>` : '';

  const metaHtml = `
    <div class="message-meta">
      <span>${data.latency_ms}ms</span>
      ${data.intent ? `<span class="intent-tag">${data.intent}</span>` : ''}
      ${data.cached ? `<span class="cached-tag">⚡ cached</span>` : ''}
      ${data.total_found ? `<span>${data.total_found} found</span>` : ''}
    </div>`;

  div.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-bubble">${escapeHtml(data.answer || '')}</div>
      ${productCards}
      ${metaHtml}
    </div>`;

  list.appendChild(div);
  scrollToBottom();
}

// ─── Product card HTML ───
function productCard(p, debugInfo = null) {
  const icon = getProductIcon(p.category, p.name);
  const condTag = p.condition === 'New'
    ? '<span class="product-tag tag-new">✨ New</span>'
    : '<span class="product-tag tag-used">♻️ Used</span>';
  const locTag = p.location ? `<span class="product-tag tag-loc">📍 ${p.location}</span>` : '';
  const gTagHtml = p.rental_guarantee ? '<span class="product-tag tag-guarantee">🛡️ Guaranteed</span>' : '';

  const imgHtml = p.image_url
    ? `<img class="product-img" src="${API_BASE}${p.image_url}" alt="${escapeHtml(p.name)}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" />
       <span class="product-icon product-icon-fallback" style="display:none">${icon}</span>`
    : `<span class="product-icon product-icon-fallback">${icon}</span>`;

  let debugHtml = '';
  if (debugInfo) {
    debugHtml = `
      <div class="debug-overlay">
        <div>Score: <span>${debugInfo.score.toFixed(1)}</span></div>
        <div>Src: <span>${debugInfo.source}</span></div>
      </div>
    `;
  }

  return `
    <div class="product-card" onclick="viewProduct(${p.id})">
      <div class="product-img-wrap">
        ${imgHtml}
        ${debugHtml}
      </div>
      <div class="product-name" title="${p.name}">${p.name}</div>
      <div class="product-brand">${p.brand || p.category || ''}</div>
      <div class="product-price">${parseFloat(p.price_per_day).toFixed(0)} EGP <span>/ day</span></div>
      <div class="product-tags">
        ${condTag}${locTag}${gTagHtml}
      </div>
    </div>`;
}

// ─── View single product ───
async function viewProduct(id) {
  try {
    const res = await fetch(`${API_BASE}/products/${id}`);
    if (!res.ok) throw new Error('Product not found');
    const p = await res.json();
    const icon = getProductIcon(p.category, p.name);
    const modal = document.getElementById('search-modal');

    const heroHtml = p.image_url
      ? `<img src="${API_BASE}${p.image_url}" alt="${escapeHtml(p.name)}"
              style="width:100%;max-height:220px;object-fit:cover;border-radius:12px;margin-bottom:16px;"
              onerror="this.style.display='none';this.nextElementSibling.style.display='block'" />
         <div style="display:none;font-size:56px;margin-bottom:16px;text-align:center;">${icon}</div>`
      : `<div style="font-size:56px;margin-bottom:16px;text-align:center;">${icon}</div>`;

    document.getElementById('search-results').innerHTML = `
      <div style="padding:20px 0 28px;">
        ${heroHtml}
        <div style="text-align:center;">
          <h2 style="font-size:20px;font-weight:700;margin-bottom:6px;">${escapeHtml(p.name)}</h2>
          <p style="color:var(--text3);margin-bottom:20px;">${escapeHtml(p.brand || '')} · ${escapeHtml(p.category)}</p>
          <div style="font-size:28px;font-weight:700;color:var(--accent2);margin-bottom:20px;">
            ${parseFloat(p.price_per_day).toFixed(0)} EGP <span style="font-size:14px;font-weight:400;color:var(--text3)"> / day</span>
          </div>
          <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:20px;">
            ${p.condition === 'New' ? '<span class="product-tag tag-new">✨ New</span>' : '<span class="product-tag tag-used">♻️ Used</span>'}
            ${p.location ? `<span class="product-tag tag-loc">📍 ${escapeHtml(p.location)}</span>` : ''}
            ${p.rental_guarantee ? '<span class="product-tag tag-guarantee">🛡️ Guaranteed</span>' : ''}
            <span class="product-tag" style="background:var(--surface2);color:var(--text2);">${p.status}</span>
          </div>
        </div>
      </div>`;
    modal.classList.add('active');
  } catch (err) {
    console.error(err);
  }
}


// ─── Live Search (sidebar) ───
let _liveSearchTimer = null;

function onLiveSearch(val) {
  const clear = document.getElementById('live-search-clear');
  clear.classList.toggle('visible', val.length > 0);

  clearTimeout(_liveSearchTimer);
  _liveSearchTimer = setTimeout(() => fetchLiveSearch(val), 200);
}

function onLiveSearchFocus() {
  const val = document.getElementById('live-search-input').value;
  fetchLiveSearch(val); // show dropdown immediately on focus
}

async function fetchLiveSearch(val) {
  const dd = document.getElementById('live-search-dropdown');
  dd.innerHTML = `<div class="live-search-loading">
    <div class="lsl-dot"></div><div class="lsl-dot"></div><div class="lsl-dot"></div>
  </div>`;
  dd.classList.add('open');

  try {
    const res = await fetch(`${API_BASE}/search/live?q=${encodeURIComponent(val.trim())}`);
    const data = await res.json();
    renderLiveDropdown(data.products || []);
  } catch {
    dd.innerHTML = `<div class="live-search-empty">⚠️ Could not load results</div>`;
  }
}

function renderLiveDropdown(products) {
  const dd = document.getElementById('live-search-dropdown');
  if (!products.length) {
    dd.innerHTML = `<div class="live-search-empty">🔍 No products found</div>`;
    return;
  }
  dd.innerHTML = products.map(p => {
    const icon = getProductIcon(p.category, p.name);
    const price = parseFloat(p.price_per_day || 0).toFixed(0);
    const meta = [p.category, p.location].filter(Boolean).join(' · ');
    return `
      <div class="live-search-item" onclick="selectLiveProduct(${p.id}, '${escapeAttr(p.name)}')">
        <span class="lsi-icon">${icon}</span>
        <div class="lsi-info">
          <div class="lsi-name">${escapeHtml(p.name)}</div>
          <div class="lsi-meta">${escapeHtml(meta)}</div>
        </div>
        <span class="lsi-price">${price} EGP</span>
      </div>`;
  }).join('');
}

function selectLiveProduct(id, name) {
  closeLiveDropdown();
  document.getElementById('live-search-input').value = name;
  document.getElementById('live-search-clear').classList.add('visible');
  viewProduct(id);   // open product detail modal
}

function clearLiveSearch() {
  document.getElementById('live-search-input').value = '';
  document.getElementById('live-search-clear').classList.remove('visible');
  closeLiveDropdown();
}

function closeLiveDropdown() {
  document.getElementById('live-search-dropdown').classList.remove('open');
}

function escapeAttr(s) { return (s || '').replace(/'/g, "\\'"); }

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  if (!document.getElementById('live-search-wrapper')?.contains(e.target)) {
    closeLiveDropdown();
  }
});

// ─── Quick Search (sidebar filters form) ───
async function quickSearch() {
  const keyword = document.getElementById('qs-keyword').value.trim();
  const location = document.getElementById('qs-location').value.trim();
  const maxPrice = document.getElementById('qs-price').value;
  const condition = document.getElementById('qs-condition').value;

  const btn = document.getElementById('qs-btn');
  btn.disabled = true;
  btn.innerHTML = 'Searching...';

  const body = {};
  if (keyword) body.name_keyword = keyword;
  if (location) body.location = location;
  if (maxPrice) body.max_price = parseFloat(maxPrice);
  if (condition) body.condition = condition;

  try {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    const products = data.products || [];

    document.getElementById('search-results').innerHTML = products.length
      ? `<p style="color:var(--text3);font-size:12px;margin-bottom:14px;">
           Found ${data.total_found} products · ${data.latency_ms}ms
         </p>
         <div class="products-grid" style="max-width:100%;">
           ${products.map(p => productCard(p)).join('')}
         </div>`
      : `<div style="text-align:center;padding:40px;color:var(--text3);">
           <div style="font-size:40px;margin-bottom:12px;">🔍</div>
           <p>No products found matching your filters.</p>
         </div>`;

    document.getElementById('search-modal').classList.add('active');
  } catch (err) {
    alert('Search failed: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> Search`;
  }
}

// ─── Helpers ───
function showTyping() {
  const list = document.getElementById('messages-list');
  const id = 'typing-' + Date.now();
  list.insertAdjacentHTML('beforeend', `
    <div class="message ai" id="${id}">
      <div class="message-avatar">🤖</div>
      <div class="message-content">
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>`);
  scrollToBottom();
  return id;
}

function removeTyping(id) {
  document.getElementById(id)?.remove();
}

function setLoading(val) {
  isLoading = val;
  document.getElementById('send-btn').disabled = val;
}

function scrollToBottom() {
  const area = document.getElementById('chat-area');
  area.scrollTop = area.scrollHeight;
}

function escapeHtml(text) {
  return (text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
}

function clearChat() {
  document.getElementById('messages-list').innerHTML = '';
  document.getElementById('welcome-screen').style.display = '';
  document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
  currentCategory = null;
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

function closeModal(e) {
  if (e.target.id === 'search-modal') {
    e.target.classList.remove('active');
  }
}
