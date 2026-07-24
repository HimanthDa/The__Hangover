/**
 * Age verification for the Wines section on the home page.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'hangover_age_verified';
  var modal = document.getElementById('age-gate-modal');
  var lockedView = document.getElementById('wines-locked');
  var contentView = document.getElementById('wines-content');
  var confirmButton = modal ? modal.querySelector('[data-age-gate-confirm]') : null;

  if (!modal || !lockedView || !contentView) {
    return;
  }

  function isVerified() {
    try {
      return sessionStorage.getItem(STORAGE_KEY) === 'true';
    } catch (error) {
      return false;
    }
  }

  function unlockWinesSection() {
    lockedView.hidden = true;
    contentView.hidden = false;
  }

  function showModal() {
    modal.hidden = false;
    document.body.classList.add('age-gate-open');
    if (confirmButton) {
      confirmButton.focus();
    }
  }

  function hideModal() {
    modal.hidden = true;
    document.body.classList.remove('age-gate-open');
  }

  function confirmAge() {
    try {
      sessionStorage.setItem(STORAGE_KEY, 'true');
    } catch (error) {
      // If sessionStorage is unavailable, unlock for the current page view.
    }
    hideModal();
    unlockWinesSection();
    contentView.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function handleTrigger(event) {
    if (isVerified()) {
      return;
    }

    event.preventDefault();
    showModal();
  }

  document.querySelectorAll('[data-adult-trigger]').forEach(function (trigger) {
    trigger.addEventListener('click', handleTrigger);
  });

  document.querySelectorAll('[data-age-gate-close]').forEach(function (button) {
    button.addEventListener('click', hideModal);
  });

  if (confirmButton) {
    confirmButton.addEventListener('click', confirmAge);
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !modal.hidden) {
      hideModal();
    }
  });

  if (isVerified()) {
    unlockWinesSection();
  } else if (window.location.hash === '#wines') {
    showModal();
    history.replaceState(null, '', window.location.pathname + window.location.search);
  }
})();
