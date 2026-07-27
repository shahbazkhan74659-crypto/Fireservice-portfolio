document.addEventListener('DOMContentLoaded', () => {

  // .adminhub-header is position:fixed (removed from flow), so body needs
  // matching padding-top so <main> doesn't render underneath it. Measured
  // via JS since the header's real height changes: below 1150px its nav
  // goes off-canvas into a drawer (see style.css), leaving just a single
  // brand+toggle row in the header itself.
  // syncHeaderOffsetFor() is shared with site.js — see static/js/header-offset.js.
  const header = document.querySelector('.adminhub-header');
  syncHeaderOffsetFor(header);

  // Mobile nav drawer — same open/close/scroll-lock pattern as the public
  // site's static/js/site.js (Admin Hub doesn't load that file, so it needs
  // its own copy here, wired to its own ids: adminNavToggle/adminNav/
  // adminNavOverlay instead of navToggle/nav/navOverlay).
  const navToggle = document.getElementById('adminNavToggle');
  const nav = document.getElementById('adminNav');
  const navOverlay = document.getElementById('adminNavOverlay');

  const openNav = () => {
    nav.classList.add('open');
    navOverlay.classList.add('open');
    navToggle.classList.add('open');
    navToggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('nav-open');
  };
  const closeNav = () => {
    nav.classList.remove('open');
    navOverlay.classList.remove('open');
    navToggle.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('nav-open');
  };

  navToggle.addEventListener('click', () => {
    if (nav.classList.contains('open')) closeNav();
    else openNav();
  });
  navOverlay.addEventListener('click', closeNav);
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeNav);
  });

});
