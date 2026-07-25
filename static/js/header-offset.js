// Shared helper for keeping `<body>`'s padding-top in sync with a
// position:fixed header's real (possibly shrinking/wrapping) height, so
// page content never renders underneath it. Used by both static/js/site.js
// (public site, #siteHeader) and static/js/adminhub.js (Admin Hub,
// .adminhub-header) — each stays otherwise independent/standalone (Admin
// Hub deliberately never loads site.js), this is just the one bit of logic
// they both need.
//
// A fixed CSS value doesn't work here: the public header shrinks on scroll
// (topbar collapses, padding/logo size reduce) and the Admin Hub header's
// nav can wrap onto a second line at narrower widths — both change the
// header's real height at runtime, so it has to be measured via JS.
function syncHeaderOffsetFor(headerEl) {
  if (!headerEl) return null;

  const sync = () => {
    document.body.style.paddingTop = headerEl.offsetHeight + 'px';
  };
  sync();
  window.addEventListener('resize', sync);

  return sync;
}
