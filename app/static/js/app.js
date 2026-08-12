const socket = io();

const sidebar = document.querySelector('.app-sidebar');
const sidebarBackdrop = document.querySelector('.app-sidebar-backdrop');
const hamburger = document.querySelector('.icon-button');
const profileButton = document.querySelector('.profile-button');
const profileMenu = document.querySelector('.profile-menu');
const notifButton = document.getElementById('notification-button');
const notifDropdown = document.getElementById('notification-dropdown');
const notifBadge = document.getElementById('notification-badge');
const notifList = document.getElementById('notification-list');
const markReadBtn = document.getElementById('mark-read');

if (sidebar && sidebarBackdrop && hamburger) {
  hamburger.addEventListener('click', () => {
    const isOpen = sidebar.classList.toggle('sidebar-open');
    // show backdrop only on narrow screens (drawer behavior)
    sidebarBackdrop.classList.toggle('is-visible', isOpen && window.innerWidth <= 900);
    hamburger.classList.toggle('is-active', isOpen);
    // on desktop toggle a body class to collapse sidebar and expand content
    if (window.innerWidth > 900) {
      document.body.classList.toggle('sidebar-collapsed', !isOpen);
    }
    hamburger.textContent = isOpen ? '✕' : '☰';
  });

  sidebarBackdrop.addEventListener('click', () => {
    sidebar.classList.remove('sidebar-open');
    sidebarBackdrop.classList.remove('is-visible');
    hamburger.classList.remove('is-active');
    hamburger.textContent = '☰';
    document.body.classList.remove('sidebar-collapsed');
  });

  // profile menu toggle + accessibility
  if (profileButton && profileMenu) {
    profileButton.addEventListener('click', (e) => {
      const isOpen = profileMenu.classList.toggle('is-visible');
      profileButton.setAttribute('aria-expanded', String(isOpen));
      profileMenu.setAttribute('aria-hidden', String(!isOpen));
    });

    document.addEventListener('click', (ev) => {
      if (!profileMenu.contains(ev.target) && !profileButton.contains(ev.target)) {
        profileMenu.classList.remove('is-visible');
        profileButton.setAttribute('aria-expanded', 'false');
        profileMenu.setAttribute('aria-hidden', 'true');
      }
    });

    document.addEventListener('keydown', (ev) => {
      if (ev.key === 'Escape') {
        profileMenu.classList.remove('is-visible');
        profileButton.setAttribute('aria-expanded', 'false');
        profileMenu.setAttribute('aria-hidden', 'true');
      }
    });
  }

  // notifications dropdown behavior
  if (notifButton && notifDropdown) {
    function updateBadge(count) {
      if (!notifBadge) return;
      if (count <= 0) { notifBadge.classList.add('hidden'); notifBadge.textContent = '0'; }
      else { notifBadge.classList.remove('hidden'); notifBadge.textContent = count > 99 ? '99+' : String(count); }
    }

    let unreadCount = 0;
    notifButton.addEventListener('click', (e) => {
      const open = notifDropdown.classList.toggle('is-visible');
      notifButton.setAttribute('aria-expanded', String(open));
      notifDropdown.setAttribute('aria-hidden', String(!open));
      if (open) {
        // mark visible items as read in UI (does not notify server)
        unreadCount = 0; updateBadge(unreadCount);
      }
    });

    markReadBtn && markReadBtn.addEventListener('click', () => {
      unreadCount = 0; updateBadge(unreadCount);
      // mark all visually as read
      Array.from(notifList.querySelectorAll('.notification-item')).forEach(it => it.classList.remove('unread'));
    });

    document.addEventListener('click', (ev) => {
      if (!notifDropdown.contains(ev.target) && !notifButton.contains(ev.target)) {
        notifDropdown.classList.remove('is-visible');
        notifButton.setAttribute('aria-expanded', 'false');
        notifDropdown.setAttribute('aria-hidden', 'true');
      }
    });

    document.addEventListener('keydown', (ev) => {
      if (ev.key === 'Escape') {
        notifDropdown.classList.remove('is-visible');
        notifButton.setAttribute('aria-expanded', 'false');
        notifDropdown.setAttribute('aria-hidden', 'true');
      }
    });

    function pushNotification(title, text, time) {
      const item = document.createElement('div');
      item.className = 'notification-item unread';
      item.innerHTML = `<div><strong>${title}</strong><p>${text}</p><div class="time">${time || ''}</div></div>`;
      // insert at top
      if (notifList) {
        // remove empty state if present
        const empty = document.getElementById('empty-notifs'); if (empty) empty.classList.add('hidden');
        notifList.insertBefore(item, notifList.firstChild);
      }
      unreadCount += 1; updateBadge(unreadCount);
    }

    // expose small API for socket events
    window.__pushNotification = pushNotification;
  }

    document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) {
        sidebar.classList.remove('sidebar-open');
        sidebarBackdrop.classList.remove('is-visible');
      }
      // ensure collapsed state is removed when navigating on any screen
      document.body.classList.remove('sidebar-collapsed');
    });
  });
}

// close sidebar on Escape
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') {
    if (sidebar.classList.contains('sidebar-open')) {
      sidebar.classList.remove('sidebar-open');
      sidebarBackdrop.classList.remove('is-visible');
      if (hamburger) { hamburger.classList.remove('is-active'); hamburger.textContent = '☰'; }
    }
  }
});

// Password visibility toggles (small eye icon)
document.addEventListener('DOMContentLoaded', () => {
  const pwFields = Array.from(document.querySelectorAll('input[type="password"]'));
  pwFields.forEach((input) => {
    if (input.closest('.password-field') || input.parentNode.querySelector('.password-toggle')) {
      return;
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'input-with-icon';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'password-toggle';
    btn.setAttribute('aria-label', 'Toggle password visibility');
    btn.innerText = '👁';
    wrapper.appendChild(btn);

    btn.addEventListener('click', () => {
      const isPwd = input.type === 'password';
      input.type = isPwd ? 'text' : 'password';
      btn.innerText = isPwd ? '🙈' : '👁';
    });
  });
});

function updateMetrics(metrics) {
  document.getElementById('metric-total').textContent = metrics.total_people;
  document.getElementById('metric-registered').textContent = metrics.registered;
  document.getElementById('metric-not-registered').textContent = metrics.not_registered;
  document.getElementById('metric-ladies').textContent = metrics.ladies;
  document.getElementById('metric-men').textContent = metrics.men;
  document.getElementById('metric-young-people').textContent = metrics.young_people;
  document.getElementById('metric-members').textContent = metrics.members;
  document.getElementById('metric-visitors').textContent = metrics.visitors;
  document.getElementById('progress-count').textContent = `${metrics.registered} / ${metrics.total_people}`;
  document.getElementById('progress-fill').style.width = `${metrics.progress_pct}%`;
}

function addActivity(item) {
  const list = document.getElementById('activity-list');
  if (!list) return;

  const li = document.createElement('li');
  li.className = 'activity-item';
  const timeDisplay = item.time ? `${item.time}` : item.timestamp;
  li.innerHTML = `<strong>${timeDisplay}</strong><span>${item.description}</span>`;
  list.insertBefore(li, list.firstChild);
}

function showRegistration(payload) {
  const container = document.getElementById('live-registration');
  if (!container) return;
  const timeStr = payload.time || payload.timestamp || '';
  const dateStr = payload.date ? `<div class="registration-date">${payload.date}</div>` : '';
  const nameHtml = payload.id ? `<a class="person-name-link" href="/people/${payload.id}" aria-label="View profile for ${payload.name}">${payload.name}</a>` : `<strong>${payload.name}</strong>`;
  container.innerHTML = `
    <div class="registration-card">
      <div class="registration-head">
        ${nameHtml}
        <span>${payload.category} • ${payload.person_type}</span>
      </div>
      <div class="registration-meta">
        <span class="registration-time">${timeStr}</span>
        ${dateStr}
      </div>
    </div>
  `;
}

socket.on('connect', () => {
  console.log('Socket connected');
});

socket.on('metrics_update', (metrics) => {
  updateMetrics(metrics);
});

socket.on('new_activity', (payload) => {
  addActivity(payload);
});

socket.on('new_registration', (payload) => {
  showRegistration(payload);
  addActivity({
    timestamp: payload.timestamp,
    description: `${payload.name} was registered`,
  });
  // also push a notification for new registration
  try {
    window.__pushNotification && window.__pushNotification('New registration', `${payload.name} was registered`, payload.time || payload.timestamp);
    // play sound only when user's setting enabled
    try{
      if (window._hb_settings && window._hb_settings.notification_sound) {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = 'sine'; o.frequency.setValueAtTime(880, ctx.currentTime);
        g.gain.setValueAtTime(0.02, ctx.currentTime);
        o.connect(g); g.connect(ctx.destination);
        o.start();
        setTimeout(()=>{ o.stop(); ctx.close(); }, 150);
      }
    }catch(err){ /* ignore sound errors */ }
  } catch(e){}
});

// fetch current user's settings for runtime behavior
fetch('/settings/json').then(r => r.json()).then(data => { window._hb_settings = data; }).catch(()=>{ window._hb_settings = { notification_sound: false }; });

// Notification system
function ensureNotificationContainer() {
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  }
  return container;
}

function showNotification(message, type = 'info') {
  const container = ensureNotificationContainer();
  const notif = document.createElement('div');
  notif.className = `notification notification-${type}`;
  notif.setAttribute('role', 'status');
  notif.innerHTML = `<div class="notification-body"><span class="notification-icon" aria-hidden="true"></span><div class="notification-text">${message}</div></div>`;
  container.appendChild(notif);

  // enter animation
  requestAnimationFrame(() => {
    notif.classList.add('show');
  });

  const duration = 3000;
  const exitMs = 250;
  const timeoutId = setTimeout(() => {
    notif.classList.remove('show');
    notif.classList.add('hide');
    setTimeout(() => {
      if (notif && notif.parentNode) notif.parentNode.removeChild(notif);
    }, exitMs);
  }, duration);

  // allow manual dismissal on click
  notif.addEventListener('click', () => {
    clearTimeout(timeoutId);
    notif.classList.remove('show');
    notif.classList.add('hide');
    setTimeout(() => {
      if (notif && notif.parentNode) notif.parentNode.removeChild(notif);
    }, exitMs);
  });
  return notif;
}

// Convert any existing server-rendered flash messages into the notification system
document.addEventListener('DOMContentLoaded', () => {
  const flashWrap = document.querySelector('.flash-messages');
  if (!flashWrap) return;
  const flashes = Array.from(flashWrap.querySelectorAll('.flash'));
  flashes.forEach((el) => {
    const message = el.textContent.trim();
    const classes = el.className || '';
    let type = 'info';
    if (classes.includes('success')) type = 'success';
    else if (classes.includes('danger') || classes.includes('error')) type = 'error';
    else if (classes.includes('warning')) type = 'warning';
    showNotification(message, type);
  });
  // remove original flashes from DOM to avoid duplication
  if (flashWrap.parentNode) flashWrap.parentNode.removeChild(flashWrap);
});

// Logout overlay flow: intercept logout links and POST to /logout while showing overlay
document.addEventListener('click', (ev) => {
  const target = ev.target.closest && ev.target.closest('a.logout-link');
  if (!target) return;
  ev.preventDefault();
  const overlay = document.getElementById('auth-overlay');
  const title = document.getElementById('overlay-title');
  const subtitle = document.getElementById('overlay-subtitle');
  if (overlay && title && subtitle) {
    overlay.classList.add('is-visible');
    overlay.setAttribute('aria-hidden', 'false');
    title.textContent = 'Logging out...';
    subtitle.textContent = 'Please wait.';
  }

  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

  fetch(target.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'same-origin',
    body: JSON.stringify({})
  }).then((resp) => {
    // on success redirect to login
    window.setTimeout(() => { window.location = '/login'; }, 400);
  }).catch(() => {
    // fallback: navigate to login
    window.location = '/login';
  });
});

const clearHistoryModal = document.getElementById('clear-history-modal');
const openClearButton = document.getElementById('open-clear-history-modal');
const closeClearButton = document.getElementById('close-clear-history-modal');
const cancelClearButton = document.getElementById('cancel-clear-history');
const confirmClearButton = document.getElementById('confirm-clear-history');

function showClearHistoryModal() {
  if (!clearHistoryModal) return;
  clearHistoryModal.classList.add('is-visible');
  clearHistoryModal.setAttribute('aria-hidden', 'false');
}

function hideClearHistoryModal() {
  if (!clearHistoryModal) return;
  clearHistoryModal.classList.remove('is-visible');
  clearHistoryModal.setAttribute('aria-hidden', 'true');
}

if (openClearButton && clearHistoryModal) {
  openClearButton.addEventListener('click', showClearHistoryModal);
}

if (closeClearButton && clearHistoryModal) {
  closeClearButton.addEventListener('click', hideClearHistoryModal);
}

if (cancelClearButton && clearHistoryModal) {
  cancelClearButton.addEventListener('click', hideClearHistoryModal);
}

if (confirmClearButton && clearHistoryModal) {
  confirmClearButton.addEventListener('click', () => {
    confirmClearButton.disabled = true;
    confirmClearButton.textContent = 'Clearing...';

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

    fetch('/admin/activity/clear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({})
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Unable to clear history');
        }
        return response.json();
      })
      .then((data) => {
        hideClearHistoryModal();
        const list = document.getElementById('activity-list');
        const empty = document.getElementById('empty-activity-log');
        if (list) list.innerHTML = '';
        if (empty) empty.classList.remove('hidden');
        showNotification(data.message || 'Activity history cleared successfully.', 'success');
      })
      .catch(() => {
        showNotification('Unable to clear activity history.', 'error');
      })
      .finally(() => {
        confirmClearButton.disabled = false;
        confirmClearButton.textContent = 'Clear History';
      });
  });
}
