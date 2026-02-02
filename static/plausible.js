(function () {
  // Stub plausible before loading the script (queue-based, same as snippet)
  window.plausible =
    window.plausible ||
    function () {
      (window.plausible.q = window.plausible.q || []).push(arguments);
    };

  window.plausible.init =
    window.plausible.init ||
    function (opts) {
      window.plausible.o = opts || {};
    };

  // Load Plausible script
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://plausible.io/js/pa-C4b1d4tXm7xemtcbC7WZk.js";
  document.head.appendChild(s);

  // Call init (no options in your snippet)
  window.plausible.init();
})();
