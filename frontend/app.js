/**
 * Client-side CleanCord / Discord Server Cleanup Interface
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
        <span class="expand-chevron" aria-hidden="true">▶</span>
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

  // Export buttons
  const btnExportJson = document.getElementById('btn-export-json');
  const btnExportCsv = document.getElementById('btn-export-csv');

  function triggerDownload(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  if (btnExportJson) {
    btnExportJson.addEventListener('click', async () => {
      try {
        let content = '';
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.export_servers_json === 'function') {
          content = await window.pywebview.api.export_servers_json(searchQuery, activeCategory, sortAscending);
        } else {
          const visible = getVisibleServers();
          content = JSON.stringify(visible, null, 2);
        }
        triggerDownload(content, 'discord-servers.json', 'application/json');
      } catch (err) {
        console.error('Failed to export JSON:', err);
      }
    });
  }

  if (btnExportCsv) {
    btnExportCsv.addEventListener('click', async () => {
      try {
        let content = '';
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.export_servers_csv === 'function') {
          content = await window.pywebview.api.export_servers_csv(searchQuery, activeCategory, sortAscending);
        } else {
          const visible = getVisibleServers();
          const headers = ['id', 'name', 'owner', 'category', 'icon_url'];
          const lines = [headers.join(',')];
          visible.forEach(s => {
            const row = [s.id, `"${s.name.replace(/"/g, '""')}"`, s.owner, `"${s.category}"`, `"${s.icon_url || ''}"`];
            lines.push(row.join(','));
          });
          content = lines.join('\n');
        }
        triggerDownload(content, 'discord-servers.csv', 'text/csv');
      } catch (err) {
        console.error('Failed to export CSV:', err);
      }
    });
  }

  // Token connection modal
  const btnOpenTokenModal = document.getElementById('btn-open-token-modal');
  const tokenModal = document.getElementById('token-modal');
  const tokenInput = document.getElementById('token-input');
  const tokenError = document.getElementById('token-error');
  const tokenModalCancel = document.getElementById('token-modal-cancel');
  const tokenModalSubmit = document.getElementById('token-modal-submit');

  if (btnOpenTokenModal && tokenModal) {
    btnOpenTokenModal.addEventListener('click', () => {
      tokenInput.value = '';
      tokenError.style.display = 'none';
      tokenModal.style.display = 'flex';
    });

    tokenModalCancel.addEventListener('click', () => {
      tokenModal.style.display = 'none';
    });

    tokenModalSubmit.addEventListener('click', async () => {
      const val = tokenInput.value.trim();
      if (!val) {
        tokenError.textContent = 'Please enter a token';
        tokenError.style.display = 'block';
        return;
      }

      tokenModalSubmit.disabled = true;
      tokenModalSubmit.textContent = 'Connecting...';
      tokenError.style.display = 'none';

      try {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.connect_token === 'function') {
          const res = await window.pywebview.api.connect_token(val);
          if (res && res.success) {
            tokenModal.style.display = 'none';
            const statusBadge = document.getElementById('status-badge');
            if (statusBadge) {
              statusBadge.textContent = `Connected (${res.username})`;
              statusBadge.style.backgroundColor = 'var(--state-success-bg)';
              statusBadge.style.color = 'var(--state-success)';
            }
            await loadServers();
          } else {
            tokenError.textContent = res.error || 'Connection failed';
            tokenError.style.display = 'block';
          }
        }
      } catch (err) {
        tokenError.textContent = 'Error connecting to bridge';
        tokenError.style.display = 'block';
      } finally {
        tokenModalSubmit.disabled = false;
        tokenModalSubmit.textContent = 'Connect';
      }
    });
  }

  // Preview button & modal elements
  const previewServerListEl = document.getElementById('preview-server-list');
  const modalPreviewBody = document.getElementById('modal-preview-body');
  const modalProgress = document.getElementById('modal-progress');
  const modalProgressText = document.getElementById('modal-progress-text');
  const modalResult = document.getElementById('modal-result');
  const modalResultText = document.getElementById('modal-result-text');
  const modalBtnCancel = document.getElementById('modal-btn-cancel');
  const modalBtnConfirm = document.getElementById('modal-btn-confirm');

  btnPreviewCleanup.addEventListener('click', async () => {
    modalPreviewBody.style.display = 'block';
    modalProgress.style.display = 'none';
    modalResult.style.display = 'none';
    modalBtnConfirm.style.display = 'inline-block';
    modalBtnConfirm.disabled = false;
    modalBtnCancel.textContent = 'Cancel';

    const selectedList = Array.from(selectedServerIds);
    modalCountEl.textContent = selectedList.length.toString();
    previewServerListEl.innerHTML = '';

    try {
      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.preview_cleanup === 'function') {
        const preview = await window.pywebview.api.preview_cleanup(selectedList);
        if (preview && preview.servers_to_leave) {
          modalCountEl.textContent = preview.eligible_count.toString();
          preview.servers_to_leave.forEach(s => {
            const li = document.createElement('li');
            li.innerHTML = `❌ <strong>${escapeHtml(s.name)}</strong> <span style="color: var(--text-muted);">(${escapeHtml(s.category)})</span>`;
            previewServerListEl.appendChild(li);
          });
          if (preview.protected_owner_count > 0) {
            const li = document.createElement('li');
            li.style.color = 'var(--state-warning)';
            li.innerHTML = `🛡️ <em>${preview.protected_owner_count} owned server(s) protected</em>`;
            previewServerListEl.appendChild(li);
          }
        }
      } else {
        selectedList.forEach(id => {
          const s = allServers.find(x => x.id === id);
          if (s) {
            const li = document.createElement('li');
            li.innerHTML = `❌ <strong>${escapeHtml(s.name)}</strong>`;
            previewServerListEl.appendChild(li);
          }
        });
      }
    } catch (err) {
      console.error('Error generating preview:', err);
    }

    previewModal.style.display = 'flex';
  });

  modalBtnCancel.addEventListener('click', () => {
    previewModal.style.display = 'none';
  });

  modalBtnConfirm.addEventListener('click', async () => {
    modalBtnConfirm.disabled = true;
    modalBtnCancel.disabled = true;
    modalProgress.style.display = 'block';
    modalPreviewBody.style.display = 'none';

    const selectedList = Array.from(selectedServerIds);

    try {
      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.execute_cleanup === 'function') {
        const result = await window.pywebview.api.execute_cleanup(selectedList);
        modalProgress.style.display = 'none';
        modalResult.style.display = 'block';
        modalResultText.textContent = `Cleanup completed: ${result.success_count} server(s) left successfully (${result.failed_count} failed).`;
        
        // Clear selection and refresh list
        selectedServerIds.clear();
        await loadServers();
      } else {
        // Fallback simulation
        modalProgress.style.display = 'none';
        modalResult.style.display = 'block';
        modalResultText.textContent = `Simulation: Left ${selectedList.length} servers.`;
        selectedServerIds.clear();
        renderList();
      }
    } catch (err) {
      modalProgress.style.display = 'none';
      modalResult.style.display = 'block';
      modalResultText.style.color = 'var(--state-error)';
      modalResultText.textContent = 'Cleanup operation failed. Please check your network or token.';
    } finally {
      modalBtnConfirm.style.display = 'none';
      modalBtnCancel.disabled = false;
      modalBtnCancel.textContent = 'Close';
    }
  });

  previewModal.addEventListener('click', (e) => {
    if (e.target === previewModal && !modalBtnCancel.disabled) {
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
