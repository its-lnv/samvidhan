(function () {
  'use strict';
  const targets = document.querySelectorAll('.fade-in, .fade-up, .timeline-item');
  if (!('IntersectionObserver' in window)) {
    targets.forEach(function (element) { element.classList.add('visible', 'vis'); });
    return;
  }
  const observer = new IntersectionObserver(function (entries, currentObserver) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible', 'vis');
      currentObserver.unobserve(entry.target);
    });
  }, { threshold: .1 });
  targets.forEach(function (element) { observer.observe(element); });
}());