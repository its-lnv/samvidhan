(function () {
  'use strict';
  const toggle = document.querySelector('[data-menu-toggle], #hamburger');
  const menu = document.querySelector('[data-mobile-menu], #mobileMenu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      const isOpen = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });
  }
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav a[href]').forEach(function (link) {
    const target = link.getAttribute('href').split('#')[0].split('?')[0];
    if (target === currentPage) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    }
  });
}());