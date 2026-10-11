/**
 * Client-side Server Prune Interface
 * Adheres to Beautiful UI guidelines and UI context specs.
 */

// State
let allServers = [];
const selectedServerIds = new Set();
let searchQuery = '';
let activeCategory = 'ALL';
let sortAscending = true;

// DOM Elements
const serverListEl = document.getElementById('server-list');
const searchInputEl = document.getElementById('search-input');
const sortToggleBtn = document.getElementById('sort-toggle-btn');
const sortOrderLabel = document.getElementById('sort-order-label');
const categoryChipsContainer = document.getElementById('category-chips');
const selectionCountEl = document.getElementById('selection-count');
const btnSelectAll = document.getElementById('btn-select-all');
const btnDeselectAll = document.getElementById('btn-deselect-all');
const btnPreviewCleanup = document.getElementById('btn-preview-cleanup');
const previewModal = document.getElementById('preview-modal');
const modalCountEl = document.getElementById('modal-count');
const modalBtnClose = document.getElementById('modal-btn-close');

// Fallback initial mock data if bridge is not ready
const INITIAL_FALLBACK_SERVERS = [
  { id: '1001', name: 'Elden Ring Community', icon_url: null, owner: false, category: 'Gaming' },
  { id: '1002', name: 'My Personal Dev Hub', icon_url: null, owner: true, category: 'Development' },
  { id: '1003', name: 'Anime & Manga Lounge', icon_url: null, owner: false, category: 'Anime' },
  { id: '1004', name: 'Solana Alpha Traders', icon_url: null, owner: false, category: 'Crypto / DeFi' },
  { id: '1005', name: 'Pixel Punks NFT Club', icon_url: null, owner: false, category: 'NFT' },
  { id: '1006', name: 'Python Software Engineers', icon_url: null, owner: false, category: 'Development' },
  { id: '1007', name: 'WallStreet Odds & Stocks', icon_url: null, owner: false, category: 'Trading' },
  { id: '1008', name: 'Coffee & Book Chill', icon_url: null, owner: false, category: 'Other' },
];

/**
 * Filter and sort server list according to current controls
 */
function getVisibleServers() {
  return allServers.filter(server => {
    // Category filter
    if (activeCategory !== 'ALL' && server.category !== activeCategory) {
      return false;
    }
    // Search query matching name or ID
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchName = server.name.toLowerCase().includes(q);
      const matchId = server.id.toLowerCase().includes(q);
      if (!matchName && !matchId) {
        return false;
      }
    }
    return true;
  }).sort((a, b) => {
    const cmp = a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
    return sortAscending ? cmp : -cmp;
  });
}

/**
 * Render the server cards list
 */
function renderList() {
  const visible = getVisibleServers();
  serverListEl.innerHTML = '';

  if (visible.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = 'No servers match your search or filter.';
    serverListEl.appendChild(empty);
    updateSelectionToolbar();
    return;
  }

  visible.forEach(server => {
    const isOwner = Boolean(server.owner);
    const isSelected = selectedServerIds.has(server.id);

    const card = document.createElement('article');
    card.className = `server-card ${isSelected ? 'selected' : ''} ${isOwner ? 'owner' : ''}`;
    card.setAttribute('data-id', server.id);

    // Initial avatar / fallback letter
    const initial = server.name ? server.name.charAt(0).toUpperCase() : '?';

    card.innerHTML = `
      <div class="server-row-main" tabindex="0" role="button" aria-expanded="false" aria-label="Toggle details for ${escapeHtml(server.name)}">
        <div class="server-icon" aria-hidden="true">${initial}</div>
        <div class="server-info">
          <div class="server-title-row">
            <span class="server-name" title="${escapeHtml(server.name)}">${escapeHtml(server.name)}</span>
            ${isOwner ? '<span class="badge badge-owner">Owner</span>' : ''}
            <span class="badge badge-category">${escapeHtml(server.category)}</span>
          </div>
          <span class="server-id">ID: ${escapeHtml(server.id)}</span>
        </div>
        <div class="server-checkbox-wrapper">
          <input 
            type="checkbox" 
            class="server-checkbox" 
            data-id="${escapeHtml(server.id)}"
            ${isSelected ? 'checked' : ''}
            ${isOwner ? 'disabled title="Owned servers cannot be left"' : 'aria-label="Select to leave"'}
          >
        </div>
      </div>
      <div class="server-details">
        <p><strong>Status:</strong> ${isOwner ? 'Owned by you (Protected)' : 'Member'}</p>
        <p><strong>Category:</strong> ${escapeHtml(server.category)}</p>
        <p><strong>Identifier:</strong> <code>${escapeHtml(server.id)}</code></p>
      </div>
    `;

    // Row expansion click (must NOT toggle checkbox)
    const rowMain = card.querySelector('.server-row-main');
    rowMain.addEventListener('click', (e) => {
      if (e.target.closest('.server-checkbox-wrapper')) {
        return;
      }
      const isExpanded = card.classList.toggle('expanded');
      rowMain.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
    });

    rowMain.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        if (e.target.closest('.server-checkbox-wrapper')) return;
        e.preventDefault();
        const isExpanded = card.classList.toggle('expanded');
        rowMain.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
      }
    });

    // Checkbox selection
    const checkbox = card.querySelector('.server-checkbox');
    checkbox.addEventListener('change', (e) => {
      e.stopPropagation();
      if (isOwner) {
        checkbox.checked = false;
        return;
      }
      if (checkbox.checked) {
        selectedServerIds.add(server.id);
        card.classList.add('selected');
      } else {
        selectedServerIds.delete(server.id);
        card.classList.remove('selected');
      }
      updateSelectionToolbar();
    });

    serverListEl.appendChild(card);
  });

  updateSelectionToolbar();
}

/**
 * Update selection counts and UI state
 */
function updateSelectionToolbar() {
  const count = selectedServerIds.size;
  selectionCountEl.textContent = count.toString();
  btnPreviewCleanup.disabled = count === 0;
}

/**
 * Escape HTML utility
 */
function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Event Listeners Setup
 */
function setupEvents() {
  // Search input
  searchInputEl.addEventListener('input', (e) => {
    searchQuery = e.target.value.trim();
    renderList();
  });

  // Sort toggle
  sortToggleBtn.addEventListener('click', () => {
    sortAscending = !sortAscending;
    sortOrderLabel.textContent = sortAscending ? 'A-Z' : 'Z-A';
    renderList();
  });

  // Category filter chips
  categoryChipsContainer.addEventListener('click', (e) => {
    const chip = e.target.closest('.filter-chip');
    if (!chip) return;
    
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeCategory = chip.getAttribute('data-category');
    renderList();
  });

  // Bulk Select All (operating only on eligible, non-owner visible servers)
  btnSelectAll.addEventListener('click', async () => {
    // If bridge provides select_all_filtered, validate through backend
    try {
      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.select_all_filtered === 'function') {
        const eligibleIds = await window.pywebview.api.select_all_filtered(searchQuery, activeCategory);
        if (Array.isArray(eligibleIds)) {
          eligibleIds.forEach(id => selectedServerIds.add(id));
          renderList();
          return;
        }
      }
    } catch (err) {
      console.warn('Backend select_all_filtered fallback:', err);
    }

    const visible = getVisibleServers();
    visible.forEach(server => {
      if (!server.owner) {
        selectedServerIds.add(server.id);
      }
    });
    renderList();
  });

  // Bulk Deselect All
  btnDeselectAll.addEventListener('click', () => {
    selectedServerIds.clear();
    renderList();
  });

  // Preview button & modal
  btnPreviewCleanup.addEventListener('click', () => {
    modalCountEl.textContent = selectedServerIds.size.toString();
    previewModal.style.display = 'flex';
  });

  modalBtnClose.addEventListener('click', () => {
    previewModal.style.display = 'none';
  });

  previewModal.addEventListener('click', (e) => {
    if (e.target === previewModal) {
      previewModal.style.display = 'none';
    }
  });
}

/**
 * Load server data from DesktopBridge or fallback
 */
async function loadServers() {
  try {
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.get_servers === 'function') {
      const servers = await window.pywebview.api.get_servers();
      if (Array.isArray(servers) && servers.length > 0) {
        allServers = servers;
        renderList();
        return;
      }
    }
  } catch (err) {
    console.error('Failed to load servers via bridge, using default mock:', err);
  }

  // Fallback
  allServers = [...INITIAL_FALLBACK_SERVERS];
  renderList();
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupEvents();
  loadServers();
});

window.addEventListener('pywebviewready', () => {
  loadServers();
});
