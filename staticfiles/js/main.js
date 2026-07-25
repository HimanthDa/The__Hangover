/**
 * The Hangover - Main JavaScript
 * Handles quantity validation, form enhancements, and cart UX.
 */

(function () {
  'use strict';

  // Ensure quantity inputs are positive integers
  document.querySelectorAll('.quantity-input').forEach(function (input) {
    input.addEventListener('change', function () {
      var val = parseInt(this.value, 10);
      if (isNaN(val) || val < 1) {
        this.value = 1;
      } else {
        this.value = val;
      }
    });
  });

  // Optional: confirm before removing from cart
  document.querySelectorAll('form[action*="/cart/remove/"]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm('Remove this item from your cart?')) {
        e.preventDefault();
      }
    });
  });

  var postalInput = document.getElementById('postal_code');
  var cityInput = document.getElementById('city');
  var stateInput = document.getElementById('state');
  var countryInput = document.getElementById('country');

  if (postalInput && cityInput && stateInput) {
    postalInput.addEventListener('blur', function () {
      var pincode = this.value.trim();
      if (!pincode || countryInput.value.toLowerCase() !== 'india') {
        return;
      }
      if (!/^[0-9]{6}$/.test(pincode)) {
        return;
      }
      fetch('https://api.postalpincode.in/pincode/' + pincode)
        .then(function (response) { return response.json(); })
        .then(function (data) {
          if (!Array.isArray(data) || data.length === 0) {
            return;
          }
          var result = data[0];
          if (result.Status !== 'Success' || !Array.isArray(result.PostOffice) || result.PostOffice.length === 0) {
            return;
          }
          var office = result.PostOffice[0];
          if (office.District) {
            cityInput.value = office.District;
          }
          if (office.State) {
            stateInput.value = office.State;
          }
        })
        .catch(function () {
          // ignore lookup failure
        });
    });
  }
})();
