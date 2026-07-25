(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FADE_MS = reduceMotion ? 0 : 250;

  // The topbar/header/footer stay on screen through a navigation — only
  // <main> (the page content in between) fades. Every page shell (public
  // base.html, adminhub/base.html, adminhub/login.html) wraps its content
  // in a <main>, so this is never null in practice.
  var content = document.querySelector('main') || document.body;

  function showContent() {
    content.classList.remove('content-leaving');
    content.classList.add('content-visible');
  }

  // Script tag sits at the end of <body> (same convention as site.js), so
  // the DOM is already parsed by the time this runs — reveal immediately,
  // no need to wait for DOMContentLoaded.
  showContent();

  // Fires when a page is restored from the back/forward cache, where the
  // script above does not re-run — without this, a page that was mid-fade-out
  // when the user navigated away could come back showing as invisible.
  window.addEventListener('pageshow', showContent);

  function isEligibleLink(link) {
    if (!link) return false;
    if (link.target && link.target !== '_self') return false;
    if (link.hasAttribute('download')) return false;
    if (link.origin !== window.location.origin) return false;
    var href = link.getAttribute('href') || '';
    if (!href || href.charAt(0) === '#') return false;
    if (href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) return false;
    return true;
  }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

    var link = e.target.closest('a[href]');
    if (!isEligibleLink(link)) return;

    // Same page (only the hash differs, or an exact re-click) — let the
    // browser handle it natively, nothing to fade between.
    if (link.pathname === window.location.pathname && link.search === window.location.search) return;

    e.preventDefault();
    content.classList.remove('content-visible');
    content.classList.add('content-leaving');
    window.setTimeout(function () {
      window.location.href = link.href;
    }, FADE_MS);
  });
})();
