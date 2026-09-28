# Django Template Preparation

This directory is a migration scaffold only. The current root-level HTML pages remain the working static site; no Django backend or template rendering is required yet.

When Django is introduced:

1. Move the page-specific markup from each root HTML file into `templates/pages/`.
2. Make each page extend `base.html` and place its body inside `{% block content %}`.
3. Use the shared files in `templates/components/` instead of copying the navbar, mobile menu, footer, or Preamble navigation.
4. Replace `.html` links with the URL names documented below.
5. Convert `assets/...` references to `{% static 'assets/...' %}` or move the assets into the final static subdirectories.

## URL names

`home`, `about`, `rights`, `articles`, `cases`, `crimes`, `freedom`, `helpline`, `quiz`, `survey`, `results`, `sovereignty`, `secularism`, `socialism`, `democracy`, `republic`, `justice`, `liberty`, `equality`, `fraternity`, `dignity`, and `unity`.

The component partials intentionally use these names so URL migration is centralized and explicit. No URL configuration is created in this frontend-only phase.