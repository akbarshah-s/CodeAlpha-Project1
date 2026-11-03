/**
 * IndianShopEase - Modern E-Commerce Platform
 * Frontend Micro-Interactions & Cart Management
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Toast Notification Auto-Dismissal
  initToasts();

  // 2. Quantity Stepper Controls
  initQuantitySteppers();

  // 3. AJAX Add to Cart
  initAjaxAddToCart();

  // 4. Sort Dropdown Auto-submit
  initSortDropdown();

  // 5. Search Bar Shortcut (press '/' to focus)
  initSearchShortcut();
});

function initToasts() {
  const toasts = document.querySelectorAll('.toast-custom');
  toasts.forEach((toast) => {
    // Auto-dismiss after 4.5 seconds
    const timer = setTimeout(() => {
      dismissToast(toast);
    }, 4500);

    const closeBtn = toast.querySelector('.toast-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(timer);
        dismissToast(toast);
      });
    }
  });
}

function dismissToast(toast) {
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(100%)';
  setTimeout(() => {
    toast.remove();
  }, 300);
}

function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container-custom');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container-custom';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-custom toast-${type}`;

  const iconClass = type === 'success' ? 'bi-check-circle-fill text-success' :
                    type === 'danger' ? 'bi-exclamation-triangle-fill text-danger' :
                    type === 'warning' ? 'bi-exclamation-circle-fill text-warning' : 'bi-info-circle-fill text-info';

  toast.innerHTML = `
    <i class="bi ${iconClass} fs-5"></i>
    <div class="flex-grow-1">
      <div class="small fw-medium">${message}</div>
    </div>
    <button type="button" class="btn-close ms-2 toast-close-btn" aria-label="Close" style="font-size: 0.75rem;"></button>
  `;

  container.appendChild(toast);
  initToasts();
}

function initQuantitySteppers() {
  document.querySelectorAll('.quantity-stepper').forEach((stepper) => {
    const minusBtn = stepper.querySelector('.btn-qty-minus');
    const plusBtn = stepper.querySelector('.btn-qty-plus');
    const input = stepper.querySelector('input');

    if (!input) return;

    const maxStock = parseInt(input.getAttribute('data-max-stock') || '9999', 10);
    const minQty = parseInt(input.getAttribute('min') || '1', 10);

    function updateButtonStates() {
      const val = parseInt(input.value || '1', 10);
      if (minusBtn) minusBtn.disabled = val <= minQty;
      if (plusBtn) plusBtn.disabled = val >= maxStock;
    }

    if (minusBtn) {
      minusBtn.addEventListener('click', (e) => {
        e.preventDefault();
        let val = parseInt(input.value || '1', 10);
        if (val > minQty) {
          input.value = val - 1;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }
        updateButtonStates();
      });
    }

    if (plusBtn) {
      plusBtn.addEventListener('click', (e) => {
        e.preventDefault();
        let val = parseInt(input.value || '1', 10);
        if (val < maxStock) {
          input.value = val + 1;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
          showToast(`Maximum available stock is ${maxStock}.`, 'warning');
        }
        updateButtonStates();
      });
    }

    input.addEventListener('change', () => {
      let val = parseInt(input.value, 10);
      if (isNaN(val) || val < minQty) val = minQty;
      if (val > maxStock) {
        val = maxStock;
        showToast(`Capped to maximum available stock (${maxStock}).`, 'warning');
      }
      input.value = val;
      updateButtonStates();
    });

    updateButtonStates();
  });
}

function initAjaxAddToCart() {
  document.querySelectorAll('.ajax-add-to-cart-form').forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalHtml = submitBtn ? submitBtn.innerHTML : '';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Adding...';
      }

      try {
        const formData = new FormData(form);
        const actionUrl = form.getAttribute('action');

        const response = await fetch(actionUrl, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          // Update cart badge counter in header
          const badges = document.querySelectorAll('.cart-counter');
          badges.forEach((b) => {
            b.textContent = data.cart_count;
            b.classList.remove('d-none');
          });

          showToast(data.message, data.success ? 'success' : 'warning');
        } else {
          // Fallback to standard submit
          form.submit();
        }
      } catch (err) {
        console.error('Add to cart error:', err);
        // Fallback
        form.submit();
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalHtml;
        }
      }
    });
  });
}

function initSortDropdown() {
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', function () {
      const url = new URL(window.location.href);
      if (this.value) {
        url.searchParams.set('sort', this.value);
      } else {
        url.searchParams.delete('sort');
      }
      window.location.href = url.toString();
    });
  }
}

function initSearchShortcut() {
  window.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const searchInput = document.querySelector('.nav-search-input');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });
}
