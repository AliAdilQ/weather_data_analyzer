document.querySelectorAll('[data-city]').forEach(button => {
  button.addEventListener('click', () => {
    const input = document.querySelector('input[name="city"]');
    input.value = button.dataset.city;
    input.focus();
  });
});
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) {
      event.preventDefault();
      return;
    }
    if (form.method.toLowerCase() === 'post') {
      const button = form.querySelector('[type="submit"], button:not([type])');
      if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Please wait…';
      }
    }
  });
});
