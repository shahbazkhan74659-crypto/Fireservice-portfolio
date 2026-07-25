document.addEventListener('DOMContentLoaded', () => {

  // .adminhub-header is position:fixed (removed from flow), so body needs
  // matching padding-top so <main> doesn't render underneath it. Measured
  // via JS rather than a fixed CSS value since the nav can wrap onto a
  // second line at narrower widths (see the 860px breakpoint override that
  // keeps .adminhub-header .nav inline instead of going off-canvas).
  const header = document.querySelector('.adminhub-header');
  if (!header) return;

  const syncHeaderOffset = () => {
    document.body.style.paddingTop = header.offsetHeight + 'px';
  };
  syncHeaderOffset();
  window.addEventListener('resize', syncHeaderOffset);

});
