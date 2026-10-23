// All poster content is rendered in HTML. JavaScript only adds a print action.
document.querySelectorAll('[data-print]').forEach((button) => {
  button.hidden = false;
  button.addEventListener('click', () => window.print());
});
