document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.querySelector('.password-toggle');
  if (toggle) {
    const passwordField = document.querySelector('.password-input');
    if (passwordField) {
      toggle.addEventListener('click', function () {
        const isPassword = passwordField.type === 'password';
        passwordField.type = isPassword ? 'text' : 'password';
        toggle.classList.toggle('visible', isPassword);
        toggle.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
      });
    }
  }

  const overlay = document.getElementById('auth-overlay');
  const overlayTitle = document.getElementById('overlay-title');
  const overlaySubtitle = document.getElementById('overlay-subtitle');

  function showOverlay(mode, subtitle = 'Please wait...') {
    if (!overlay || !overlayTitle || !overlaySubtitle) return;

    const modeMap = {
      'login': ['Logging in...', 'Please wait...'],
      'logout': ['Logging out...', 'Please wait a moment.'],
      'loading': ['Loading...', 'Please wait...'],
      'success': ['Login successful', 'Redirecting...']
    };

    const content = modeMap[mode] || modeMap.login;
    overlayTitle.textContent = content[0];
    overlaySubtitle.textContent = subtitle || content[1];

    overlay.className = 'auth-overlay is-visible';
    if (mode === 'success') {
      overlay.classList.add('success');
    } else {
      overlay.classList.remove('success');
    }
    overlay.setAttribute('aria-hidden', 'false');
  }

  function hideOverlay() {
    if (!overlay) return;
    overlay.className = 'auth-overlay';
    overlay.setAttribute('aria-hidden', 'true');
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function () {
      const submitButton = loginForm.querySelector('input[type="submit"]') || loginForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.value = 'Signing in...';
        submitButton.dataset.originalValue = submitButton.value;
      }

      const usernameField = document.getElementById('username');
      const passwordField = document.getElementById('password');

      if (usernameField && usernameField.value.trim().length === 0) {
        usernameField.classList.add('error');
      }
      if (passwordField && passwordField.value.trim().length === 0) {
        passwordField.classList.add('error');
      }

      showOverlay('login');
    });
  }

  const logoutLinks = document.querySelectorAll('a[href*="/logout"]');
  logoutLinks.forEach((link) => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      const targetHref = link.getAttribute('href');
      showOverlay('logout', 'Please wait a moment.');
      link.setAttribute('aria-disabled', 'true');
      window.location.assign(targetHref);
    });
  });

  const url = window.location.pathname;
  const shouldNotUseLoginCache = url === '/login' && document.body.classList.contains('login-page');
  if (shouldNotUseLoginCache) {
    window.history.replaceState(null, '', '/login');
  }

  if (window.performance && window.performance.getEntriesByType) {
    const navigationEntries = performance.getEntriesByType('navigation');
    if (navigationEntries && navigationEntries.length > 0) {
      const type = navigationEntries[0].type;
      if (type === 'back_forward') {
        window.location.reload();
      }
    }
  }

  const loginUsername = document.getElementById('username');
  const password = document.getElementById('password');
  if (loginUsername && loginUsername.classList.contains('error')) {
    loginUsername.closest('.form-group').querySelector('input').classList.add('element-shake');
  }

  if (password && password.classList.contains('error')) {
    password.closest('.form-group').querySelector('input').classList.add('element-shake');
  }

  window.hideAuthOverlay = hideOverlay;
});
