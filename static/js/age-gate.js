/**
 * Global Age Verification Handler for "The Hangover"
 * Manages full-screen modal, session state, and backend AJAX verification.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'hangover_age_verified';
  var VERIFY_URL = '/products/verify-age/';
  var WINES_URL = '/products/category/wines/';

  var modal = document.getElementById('age-gate-modal');
  if (!modal) return;

  var over18Btn = modal.querySelector('[data-age-gate-confirm="over18"]');
  var closeBtn = modal.querySelector('[data-age-gate-confirm="close"], [data-age-gate-confirm="under18"]');

  var pendingTargetUrl = null;

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function isVerifiedLocally() {
    try {
      if (localStorage.getItem(STORAGE_KEY)) {
        localStorage.removeItem(STORAGE_KEY);
      }
      if (sessionStorage.getItem(STORAGE_KEY) === 'true') return true;
      if (getCookie('age_verified') === 'true') return true;
    } catch (e) {}
    return false;
  }

  function markVerifiedLocally(verified) {
    try {
      var strVal = verified ? 'true' : 'false';
      sessionStorage.setItem(STORAGE_KEY, strVal);
      localStorage.removeItem(STORAGE_KEY);
      document.cookie = 'age_verified=' + strVal + '; path=/; SameSite=Lax';
    } catch (e) {}
  }

  function showModal(targetUrl) {
    pendingTargetUrl = targetUrl || WINES_URL;
    modal.hidden = false;
    modal.classList.add('is-active');
    document.body.classList.add('age-gate-open');
    if (over18Btn) over18Btn.focus();
  }

  function hideModal() {
    modal.hidden = true;
    modal.classList.remove('is-active');
    document.body.classList.remove('age-gate-open');
  }

  function handleAgeChoice(choice) {
    var csrfToken = getCookie('csrftoken') || '';

    fetch(VERIFY_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ choice: choice })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (choice === 'over18' || (data && data.verified)) {
        markVerifiedLocally(true);
        hideModal();
        var destination = pendingTargetUrl || WINES_URL;
        window.location.href = destination;
      } else {
        markVerifiedLocally(false);
        hideModal();
        if (window.location.pathname.indexOf('/wines') !== -1 || window.location.pathname.indexOf('/category/wine') !== -1) {
          window.location.href = '/';
        }
      }
    })
    .catch(function() {
      if (choice === 'over18') {
        markVerifiedLocally(true);
        hideModal();
        window.location.href = pendingTargetUrl || WINES_URL;
      } else {
        markVerifiedLocally(false);
        hideModal();
        if (window.location.pathname.indexOf('/wines') !== -1) {
          window.location.href = '/';
        }
      }
    });
  }

  // Event Listeners
  if (over18Btn) {
    over18Btn.addEventListener('click', function () {
      handleAgeChoice('over18');
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      handleAgeChoice('under18');
    });
  }

  // Intercept all wine links
  document.body.addEventListener('click', function(e) {
    var target = e.target.closest('a[data-adult-trigger], a[href*="/category/wines"], a[href*="/category/wine"], a[href*="/wines"]');
    if (target) {
      if (!isVerifiedLocally()) {
        e.preventDefault();
        e.stopPropagation();
        var targetUrl = target.getAttribute('href');
        showModal(targetUrl);
      }
    }
  });

  // Check URL query parameters if server redirected due to age check
  var urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('age_gate') === 'wines' || urlParams.get('age_gate') === 'required') {
    var nextParam = urlParams.get('next');
    if (!isVerifiedLocally()) {
      showModal(nextParam || WINES_URL);
    }
  }

  window.HangoverAgeGate = {
    show: showModal,
    hide: hideModal,
    isVerified: isVerifiedLocally
  };
})();
