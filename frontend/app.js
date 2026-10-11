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
let isAuthenticated = false;

// DOM Elements - App View
const appView = document.getElementById('app-view');
const loginView = document.getElementById('login-view');
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

// DOM Elements - Login View
const tabBtnEmail = document.getElementById('tab-btn-email');
const tabBtnToken = document.getElementById('tab-btn-token');
const paneEmail = document.getElementById('pane-email');
const paneToken = document.getElementById('pane-token');
const formEmailLogin = document.getElementById('form-email-login');
const formTokenLogin = document.getElementById('form-token-login');
const inputEmail = document.getElementById('input-email');
const inputPassword = document.getElementById('input-password');
const btnTogglePassword = document.getElementById('btn-toggle-password');
const linkForgotPassword = document.getElementById('link-forgot-password');
const btnEmailSubmit = document.getElementById('btn-email-submit');
const emailError = document.getElementById('email-error');
const btnSwitchToToken = document.getElementById('btn-switch-to-token');
const inputTokenMain = document.getElementById('input-token-main');
const btnToggleToken = document.getElementById('btn-toggle-token');
const btnTokenSubmit = document.getElementById('btn-token-submit');
const tokenLoginError = document.getElementById('token-login-error');
const btnBackToEmail = document.getElementById('btn-back-to-email');
const btnSwitchAccount = document.getElementById('btn-switch-account');

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
 * Switch to Token Login tab
 */
function switchToTokenTab() {
  tabBtnToken.classList.add('active');
  tabBtnToken.setAttribute('aria-selected', 'true');
  tabBtnEmail.classList.remove('active');
  tabBtnEmail.setAttribute('aria-selected', 'false');
  paneToken.style.display = 'block';
  paneEmail.style.display = 'none';
  if (tokenLoginError) tokenLoginError.style.display = 'none';
  if (inputTokenMain) inputTokenMain.focus();
}

/**
 * Switch to Email Login tab
 */
function switchToEmailTab() {
  tabBtnEmail.classList.add('active');
  tabBtnEmail.setAttribute('aria-selected', 'true');
  tabBtnToken.classList.remove('active');
  tabBtnToken.setAttribute('aria-selected', 'false');
  paneEmail.style.display = 'block';
  paneToken.style.display = 'none';
  if (emailError) emailError.style.display = 'none';
  if (inputEmail) inputEmail.focus();
}

/**
 * Reveal the main application screen after valid authentication
 */
function enterAppView(username, serverCount) {
  isAuthenticated = true;
  loginView.style.display = 'none';
  appView.style.display = 'flex';

  const statusBadge = document.getElementById('status-badge');
  if (statusBadge) {
    statusBadge.textContent = username ? `Connected (${username})` : 'Connected';
    statusBadge.style.backgroundColor = 'var(--state-success-bg)';
    statusBadge.style.color = 'var(--state-success)';
  }

  loadServers();
}

/**
 * Return to login view (logout / switch account)
 */
function enterLoginView() {
  isAuthenticated = false;
  appView.style.display = 'none';
  loginView.style.display = 'flex';
  if (inputTokenMain) inputTokenMain.value = '';
  if (tokenLoginError) tokenLoginError.style.display = 'none';
  if (emailError) emailError.style.display = 'none';
}

/**
 * Setup Login Screen Handlers
 */
function setupLoginEvents() {
  // Tabs
  if (tabBtnEmail) tabBtnEmail.addEventListener('click', switchToEmailTab);
  if (tabBtnToken) tabBtnToken.addEventListener('click', switchToTokenTab);
  if (btnSwitchToToken) btnSwitchToToken.addEventListener('click', switchToTokenTab);
  if (btnBackToEmail) btnBackToEmail.addEventListener('click', switchToEmailTab);

  // Password visibility toggle
  if (btnTogglePassword && inputPassword) {
    btnTogglePassword.addEventListener('click', () => {
      const isPwd = inputPassword.type === 'password';
      inputPassword.type = isPwd ? 'text' : 'password';
      btnTogglePassword.style.color = isPwd ? '#5865F2' : '#717b94';
    });
  }

  // Token visibility toggle
  if (btnToggleToken && inputTokenMain) {
    btnToggleToken.addEventListener('click', () => {
      const isPwd = inputTokenMain.type === 'password';
      inputTokenMain.type = isPwd ? 'text' : 'password';
      btnToggleToken.style.color = isPwd ? '#5865F2' : '#717b94';
    });
  }

  // Forgot password link
  if (linkForgotPassword) {
    linkForgotPassword.addEventListener('click', (e) => {
      e.preventDefault();
      alert('Password reset must be performed directly on Discord (https://discord.com/login).');
    });
  }

  // Email form submission: Security check
  if (formEmailLogin) {
    formEmailLogin.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = inputEmail.value.trim();
      const pwd = inputPassword.value;

      if (!email || !pwd) {
        emailError.textContent = 'Please enter both email and password.';
        emailError.style.display = 'block';
        return;
      }

      // Security requirement: Never transmit passwords via custom third-party forms
      emailError.innerHTML = '⚠️ <strong>Security Notice:</strong> Discord requires 2FA or User Token for third-party client sessions. Please use the <strong>Token Login</strong> tab for direct authorized access.';
      emailError.style.display = 'block';
    });
  }

  // Token form submission
  if (formTokenLogin) {
    formTokenLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const rawToken = inputTokenMain.value || '';
      // Strip any characters not matching a-zA-Z0-9._-
      const token = rawToken.replace(/[^a-zA-Z0-9._-]/g, '');

      if (!token) {
        tokenLoginError.textContent = 'Please enter a valid Discord authorization token.';
        tokenLoginError.style.display = 'block';
        return;
      }

      tokenLoginError.style.display = 'none';
      btnTokenSubmit.disabled = true;
      const originalText = btnTokenSubmit.querySelector('.btn-text').textContent;
      btnTokenSubmit.querySelector('.btn-text').textContent = 'Connecting...';

      try {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.connect_token === 'function') {
          const res = await window.pywebview.api.connect_token(token);
          if (res && res.success) {
            enterAppView(res.username, res.server_count);
            return;
          } else {
            tokenLoginError.textContent = (res && res.error) ? res.error : 'Invalid token or unable to connect to Discord.';
            tokenLoginError.style.display = 'block';
          }
        } else {
          // If bridge not loaded in browser preview or tests
          enterAppView('Preview User', 8);
          return;
        }
      } catch (err) {
        tokenLoginError.textContent = 'Connection failed: ' + (err.message || 'Network error');
        tokenLoginError.style.display = 'block';
      } finally {
        btnTokenSubmit.disabled = false;
        btnTokenSubmit.querySelector('.btn-text').textContent = originalText;
      }
    });
  }

  // Switch account button in header
  if (btnSwitchAccount) {
    btnSwitchAccount.addEventListener('click', () => {
      enterLoginView();
    });
  }
}

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
  if (!serverListEl) return;
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
    const mainRow = card.querySelector('.server-row-main');
    mainRow.addEventListener('click', (e) => {
      if (e.target.closest('.server-checkbox-wrapper')) return;
      const isExpanded = card.classList.toggle('expanded');
      mainRow.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
    });

    mainRow.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        if (e.target.closest('.server-checkbox-wrapper')) return;
        e.preventDefault();
        const isExpanded = card.classList.toggle('expanded');
        mainRow.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
      }
    });

    // Checkbox toggle logic
    const checkbox = card.querySelector('.server-checkbox');
    checkbox.addEventListener('change', () => {
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
 * Update selection count and preview button state
 */
function updateSelectionToolbar() {
  if (selectionCountEl) selectionCountEl.textContent = selectedServerIds.size.toString();
  if (btnPreviewCleanup) btnPreviewCleanup.disabled = selectedServerIds.size === 0;
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
  setupLoginEvents();

  // Search input
  if (searchInputEl) {
    searchInputEl.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim();
      renderList();
    });
  }

  // Sort toggle
  if (sortToggleBtn) {
    sortToggleBtn.addEventListener('click', () => {
      sortAscending = !sortAscending;
      if (sortOrderLabel) sortOrderLabel.textContent = sortAscending ? 'A-Z' : 'Z-A';
      renderList();
    });
  }

  // Category filter chips
  if (categoryChipsContainer) {
    categoryChipsContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.filter-chip');
      if (!chip) return;
      
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeCategory = chip.getAttribute('data-category');
      renderList();
    });
  }

  // Bulk Select All
  if (btnSelectAll) {
    btnSelectAll.addEventListener('click', async () => {
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
  }

  // Bulk Deselect All
  if (btnDeselectAll) {
    btnDeselectAll.addEventListener('click', () => {
      selectedServerIds.clear();
      renderList();
    });
  }

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
          content = await window.pywebview.api.export_servers_json();
        } else {
          content = JSON.stringify(allServers, null, 2);
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
          content = await window.pywebview.api.export_servers_csv();
        } else {
          const lines = ['id,name,owner,category'];
          allServers.forEach(s => {
            lines.push(`"${s.id}","${s.name.replace(/"/g, '""')}","${s.owner}","${s.category}"`);
          });
          content = lines.join('\n');
        }
        triggerDownload(content, 'discord-servers.csv', 'text/csv');
      } catch (err) {
        console.error('Failed to export CSV:', err);
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

  if (btnPreviewCleanup) {
    btnPreviewCleanup.addEventListener('click', async () => {
      modalPreviewBody.style.display = 'block';
      modalProgress.style.display = 'none';
      modalResult.style.display = 'none';
      modalBtnConfirm.style.display = 'inline-block';
      modalBtnConfirm.disabled = false;
      modalBtnCancel.textContent = 'Cancel';

      const selectedList = Array.from(selectedServerIds);
      if (modalCountEl) modalCountEl.textContent = selectedList.length.toString();
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
  }

  if (modalBtnCancel) {
    modalBtnCancel.addEventListener('click', () => {
      previewModal.style.display = 'none';
    });
  }

  if (modalBtnConfirm) {
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
  }

  if (previewModal) {
    previewModal.addEventListener('click', (e) => {
      if (e.target === previewModal && !modalBtnCancel.disabled) {
        previewModal.style.display = 'none';
      }
    });
  }
}

/**
 * Load server data from DesktopBridge or fallback
 */
async function loadServers() {
  if (!isAuthenticated) return;
  try {
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.get_servers === 'function') {
      const servers = await window.pywebview.api.get_servers();
      if (Array.isArray(servers)) {
        allServers = servers;
        renderList();
        return;
      }
    }
  } catch (err) {
    console.error('Failed to load servers via bridge:', err);
  }

  // Fallback
  allServers = [...INITIAL_FALLBACK_SERVERS];
  renderList();
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupEvents();
  // App starts strictly locked at Login Screen (Demo Mode removed from default entry)
});

window.addEventListener('pywebviewready', () => {
  // If backend was initialized with live token directly, auto-enter
  if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.get_status === 'function') {
    window.pywebview.api.get_status().then(status => {
      if (status && status.mode === 'live') {
        enterAppView('Connected User');
      }
    }).catch(() => {});
  }
});
