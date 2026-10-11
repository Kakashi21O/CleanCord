/**
 * Desktop Window Client Script
 */

window.addEventListener('pywebviewready', async () => {
  const statusBadge = document.getElementById('status-badge');
  try {
    if (window.pywebview && window.pywebview.api) {
      const status = await window.pywebview.api.get_status();
      if (status && status.status === 'online') {
        statusBadge.textContent = 'Ready (Mock Mode)';
      } else {
        statusBadge.textContent = 'Connected';
      }
    }
  } catch (err) {
    console.error('Error communicating with bridge:', err);
    statusBadge.textContent = 'Bridge Error';
  }
});
