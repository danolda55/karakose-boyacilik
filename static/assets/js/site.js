/* Karaköse Boyacılık — site davranışları. İçerik HTML'de durur; bu dosya sadece etkileşim ekler. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  var cfg = window.KB_CONFIG || {};

  function track(name, params) {
    window.dataLayer = window.dataLayer || [];
    var ev = { event: name };
    for (var k in params || {}) ev[k] = params[k];
    window.dataLayer.push(ev);
  }

  /* Başlık gölgesi */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Mobil menü */
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    };
    btn.addEventListener("click", function () { setOpen(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setOpen(false); });
  }

  /* Kaydırınca beliren bölümler */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* Telefon / WhatsApp tıklama takibi (Google Tag Manager) */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (href.indexOf("tel:") === 0) track("phone_click", { link_url: href });
    else if (href.indexOf("wa.me") !== -1) track("whatsapp_click", { link_url: href });
    else if (href.indexOf("google.") !== -1 && a.dataset.review !== undefined) track("review_click", {});
  });

  /* İşçilik hesaplama */
  var form = document.getElementById("calc-form");
  if (form && cfg.prices) {
    var out = document.getElementById("calc-result");
    var err = document.getElementById("calc-error");
    var priceEl = document.getElementById("calc-price");
    var waEl = document.getElementById("calc-wa");
    var fmt = function (n) { return n.toLocaleString("tr-TR") + " TL"; };
    var roundTo = function (n, step) { return Math.round(n / step) * step; };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      err.textContent = "";
      var data = new FormData(form);
      var area = parseFloat(String(data.get("area") || "").replace(",", "."));
      var status = data.get("status");
      var color = data.get("color");

      if (!isFinite(area) || area < 10 || area > 1000) {
        err.textContent = "Lütfen 10 ile 1000 m² arasında bir alan girin.";
        out.hidden = true;
        form.querySelector("#area").focus();
        return;
      }
      var rate = cfg.prices.rates[status];
      var mult = cfg.prices.colorMultipliers[color];
      if (!rate || !mult) {
        err.textContent = "Lütfen evin durumunu ve renk değişimini seçin.";
        out.hidden = true;
        return;
      }
      var base = area * rate * mult;
      var low = roundTo(base * (1 - cfg.prices.spread), 500);
      var high = roundTo(base * (1 + cfg.prices.spread), 500);
      priceEl.textContent = fmt(low) + " – " + fmt(high);

      var statusText = status === "furnished" ? "eşyalı" : "boş";
      var colorText = { light_to_light: "açıktan açığa", light_to_dark: "açıktan koyuya", dark_to_light: "koyudan açığa", dark_to_dark: "koyudan koyuya" }[color];
      var msg = "Merhaba Birol Usta, siteden hesapladım: " + area + " m² " + statusText + " ev, renk " + colorText +
        ". Tahmini işçilik " + fmt(low) + " – " + fmt(high) + " çıktı. Keşif için uygun olduğunuz bir gün var mı?";
      waEl.href = "https://wa.me/" + cfg.phoneIntl + "?text=" + encodeURIComponent(msg);

      out.hidden = false;
      out.scrollIntoView({ behavior: "smooth", block: "nearest" });
      track("calculator_submit", { area: area, status: status, color: color, low: low, high: high });
    });
  }
})();
