document.addEventListener('DOMContentLoaded', () => {

  // Footer year
  document.getElementById('year').textContent = new Date().getFullYear();

  // Mobile nav toggle
  // Drawer open/close is coordinated across three things: the drawer
  // itself (.nav.open, translateX transform in CSS), a backdrop scrim
  // (#navOverlay, .open toggles its opacity/pointer-events in CSS) that
  // closes the drawer when tapped, and a body-scroll lock (.nav-open on
  // <body>, overflow:hidden) so the page behind the drawer can't scroll
  // while it's open.
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  const navOverlay = document.getElementById('navOverlay');

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

  // Shrink site header on scroll
  // site-header is position:fixed (removed from flow), so body needs matching
  // padding-top kept in sync with its real height, including the shrink transition.
  // syncHeaderOffsetFor() is shared with adminhub.js — see static/js/header-offset.js.
  const siteHeader = document.getElementById('siteHeader');
  const header = document.getElementById('header');
  const syncHeaderOffset = syncHeaderOffsetFor(siteHeader);
  siteHeader.addEventListener('transitionend', syncHeaderOffset);

  window.addEventListener('scroll', () => {
    // body.nav-open locks scroll via overflow:hidden, but that doesn't fully
    // block touch-driven rubber-band scrolling on some mobile browsers —
    // stray scroll events were still shrinking the header (topbar collapse +
    // reduced padding) while the drawer was open, visibly shifting the close
    // (X) button upward. Freeze the shrink state while the drawer is open.
    if (document.body.classList.contains('nav-open')) return;
    siteHeader.classList.toggle('is-scrolled', window.scrollY > 10);
    header.style.boxShadow = window.scrollY > 10 ? '0 4px 16px rgba(0,0,0,.08)' : 'none';
  });

  // Back to top button
  const backToTop = document.getElementById('backToTop');
  window.addEventListener('scroll', () => {
    backToTop.classList.toggle('show', window.scrollY > 500);
  });
  backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  // Animated stat counters
  const counters = document.querySelectorAll('.stat__num');
  let countersStarted = false;
  const animateCounters = () => {
    if (countersStarted) return;
    countersStarted = true;
    counters.forEach(el => {
      const target = parseInt(el.dataset.count, 10);
      const duration = 1400;
      const start = performance.now();
      const step = now => {
        const progress = Math.min((now - start) / duration, 1);
        el.textContent = Math.floor(progress * target);
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target;
      };
      requestAnimationFrame(step);
    });
  };

  // Scroll reveal for cards/sections
  const revealTargets = document.querySelectorAll('.card, .process__step, .why, .about__media, .about__text, .logo-card, .cert-card, .phase, .product-card');
  revealTargets.forEach(el => el.classList.add('reveal'));

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealTargets.forEach(el => observer.observe(el));

  const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounters();
        statsObserver.disconnect();
      }
    });
  }, { threshold: 0.4 });
  const statsSection = document.querySelector('.stats');
  if (statsSection) statsObserver.observe(statsSection);

});
