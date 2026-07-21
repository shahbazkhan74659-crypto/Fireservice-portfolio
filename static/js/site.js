document.addEventListener('DOMContentLoaded', () => {

  // Footer year
  document.getElementById('year').textContent = new Date().getFullYear();

  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  navToggle.addEventListener('click', () => {
    nav.classList.toggle('open');
  });
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => nav.classList.remove('open'));
  });

  // Shrink site header on scroll
  // site-header is position:fixed (removed from flow), so body needs matching
  // padding-top kept in sync with its real height, including the shrink transition.
  const siteHeader = document.getElementById('siteHeader');
  const header = document.getElementById('header');
  const syncHeaderOffset = () => {
    document.body.style.paddingTop = siteHeader.offsetHeight + 'px';
  };
  syncHeaderOffset();
  window.addEventListener('resize', syncHeaderOffset);
  siteHeader.addEventListener('transitionend', syncHeaderOffset);

  window.addEventListener('scroll', () => {
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
  const revealTargets = document.querySelectorAll('.card, .process__step, .why, .about__media, .about__text, .logo-card, .cert-card, .phase');
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
