(function () {
  'use strict';

  var MOBILE_NAV_MAX_WIDTH = 1023;

  function initialiseNavigation() {
    var nav = document.getElementById('mainNav');
    var hamburger = document.getElementById('hamburgerBtn');
    var links = document.getElementById('navLinks');

    if (!nav || !hamburger || !links || nav.dataset.navigationReady === 'true') {
      return;
    }

    nav.dataset.navigationReady = 'true';
    hamburger.type = 'button';
    hamburger.setAttribute('aria-controls', 'navLinks');
    hamburger.setAttribute('aria-expanded', 'false');

    function setMenuOpen(isOpen, returnFocus) {
      links.classList.toggle('active', isOpen);
      hamburger.classList.toggle('active', isOpen);
      nav.classList.toggle('menu-open', isOpen);
      hamburger.setAttribute('aria-expanded', String(isOpen));

      if (returnFocus) {
        hamburger.focus();
      }
    }

    function menuIsOpen() {
      return links.classList.contains('active');
    }

    /*
     * Capture the click so this controller safely supersedes older inline
     * hamburger handlers that still exist on some legacy static pages.
     */
    hamburger.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      setMenuOpen(!menuIsOpen(), false);
    }, true);

    links.addEventListener('click', function (event) {
      if (event.target.closest('a')) {
        setMenuOpen(false, false);
      }
    });

    document.addEventListener('click', function (event) {
      if (menuIsOpen() && !nav.contains(event.target)) {
        setMenuOpen(false, false);
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menuIsOpen()) {
        setMenuOpen(false, true);
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > MOBILE_NAV_MAX_WIDTH && menuIsOpen()) {
        setMenuOpen(false, false);
      }
    });

    function updateScrolledState() {
      nav.classList.toggle('scrolled', window.scrollY > 50);
    }

    window.addEventListener('scroll', updateScrolledState, { passive: true });
    updateScrolledState();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialiseNavigation, { once: true });
  } else {
    initialiseNavigation();
  }
})();
