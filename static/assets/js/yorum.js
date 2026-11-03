/* Google yorum isteme aracı — Birol Usta numarayı girip Gönder'e basar; mesaj sunucu üzerinden (InfiniReach) babanın 0505 hattından WhatsApp ve SMS olarak kendiliğinden gider. */
(function () {
  "use strict";
  var cfg = window.KB_CONFIG || {};
  var KEY = "kb-yorum-gecmis", PINKEY = "kb-yorum-pin";
  var API = "send.php", STATUS = "status.php";

  var phoneIn = document.getElementById("musteri-tel");
  var nameIn = document.getElementById("musteri-ad");
  var preview = document.getElementById("mesaj");
  var err = document.getElementById("tel-hata");
  var sendBtn = document.getElementById("gonder");
  var box = document.getElementById("sonuc");
  var pinBtn = document.getElementById("pin-degis");
  var list = document.getElementById("gecmis");
  var clearBtn = document.getElementById("gecmis-sil");

  function normalize(raw) {
    var d = String(raw || "").replace(/\D/g, "");
    if (d.indexOf("0090") === 0) d = d.slice(2);
    if (d.length === 11 && d[0] === "0") d = "9" + d;
    if (d.length === 10 && d[0] === "5") d = "90" + d;
    return /^905\d{9}$/.test(d) ? d : null;
  }
  function pretty(d) { return "0" + d.slice(2, 5) + " " + d.slice(5, 8) + " " + d.slice(8, 10) + " " + d.slice(10); }
  function buildMessage() {
    var name = (nameIn.value || "").trim();
    return cfg.reviewMessage.replace("{selam}", name ? "Merhaba " + name + "," : "Merhaba,").replace("{link}", cfg.reviewUrl);
  }
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save(arr) { try { localStorage.setItem(KEY, JSON.stringify(arr.slice(0, 50))); } catch (e) {} }
  function getPin() { try { return localStorage.getItem(PINKEY) || ""; } catch (e) { return ""; } }
  function setPin(p) { try { p ? localStorage.setItem(PINKEY, p) : localStorage.removeItem(PINKEY); } catch (e) {} }

  function render() {
    var arr = load();
    list.innerHTML = "";
    if (!arr.length) { list.innerHTML = '<li class="small">Henüz gönderim yok.</li>'; return; }
    arr.forEach(function (it) {
      var li = document.createElement("li");
      var left = document.createElement("span");
      left.textContent = (it.name ? it.name + " · " : "") + pretty(it.phone);
      var right = document.createElement("span");
      right.className = "small";
      right.textContent = it.via + " · " + new Date(it.at).toLocaleDateString("tr-TR");
      li.appendChild(left); li.appendChild(right);
      list.appendChild(li);
    });
  }
  function refresh() { preview.value = buildMessage(); }
  function show(html) { box.innerHTML = html; box.hidden = false; }
  function esc(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }

  function call(url, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ "Content-Type": "application/json", "X-Pin": getPin() }, opts.headers || {});
    return fetch(url, opts).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j._status = r.status; return j; }); });
  }

  function askPin() {
    var p = prompt("Gönderim PIN'ini girin (bir kez sorulur):", "");
    if (p === null) return Promise.resolve(false);
    setPin(p.trim());
    return call(API, { method: "POST", body: JSON.stringify({ check: 1 }) }).then(function (j) {
      if (j.ok) return true;
      setPin("");
      alert(j.error || "PIN hatalı");
      return false;
    });
  }
  function ensurePin() { return getPin() ? Promise.resolve(true) : askPin(); }

  var LABEL = { whatsapp: "WhatsApp", sms: "SMS" };
  var STATE = { queued: "sırada", pending: "sırada", sending: "gidiyor", sent: "gönderildi ✓", delivered: "iletildi ✓✓", read: "okundu ✓✓", failed: "gitmedi ✗", undelivered: "gitmedi ✗" };

  function poll(ids, phone, n) {
    var keys = Object.keys(ids);
    Promise.all(keys.map(function (c) {
      return fetch(STATUS + "?id=" + encodeURIComponent(ids[c]), { headers: { "X-Pin": getPin() } })
        .then(function (r) { return r.json(); }).catch(function () { return {}; });
    })).then(function (rs) {
      var done = true, rows = keys.map(function (c, i) {
        var s = (rs[i] && rs[i].status) || "queued";
        if (!/sent|delivered|read|failed|undelivered/.test(s)) done = false;
        return "<li>" + LABEL[c] + ": <strong>" + esc(STATE[s] || s) + "</strong></li>";
      });
      show("<p style='margin:0 0 8px'><strong>" + pretty(phone) + "</strong></p><ul style='margin:0;padding-left:18px'>" + rows.join("") + "</ul>");
      if (!done && n < 12) setTimeout(function () { poll(ids, phone, n + 1); }, 5000);
    });
  }

  function send(force) {
    var phone = normalize(phoneIn.value);
    err.textContent = "";
    if (!phone) { err.textContent = "Numara hatalı görünüyor. Örnek: 0532 123 45 67"; phoneIn.focus(); return; }
    ensurePin().then(function (ok) {
      if (!ok) return;
      var text = preview.value || buildMessage();
      var name = (nameIn.value || "").trim();
      sendBtn.disabled = true; sendBtn.textContent = "Gönderiliyor…";
      call(API, { method: "POST", body: JSON.stringify({ phone: phone, text: text, force: force ? 1 : 0 }) }).then(function (j) {
        sendBtn.disabled = false; sendBtn.textContent = "Gönder";
        if (j._status === 401) { setPin(""); err.textContent = "PIN hatalı, tekrar deneyin."; return; }
        if (j.dup) {
          if (confirm("Bu numaraya " + new Date(j.at * 1000).toLocaleDateString("tr-TR") + " tarihinde zaten gönderilmiş. Yine de gönderilsin mi?")) send(true);
          return;
        }
        if (!j.ok) { err.textContent = j.error || "Gönderilemedi. İnterneti kontrol edip tekrar deneyin."; return; }
        var ids = {}, via = [];
        Object.keys(j.results || {}).forEach(function (c) { if (j.results[c].ok) { ids[c] = j.results[c].id; via.push(LABEL[c]); } });
        var arr = load();
        arr.unshift({ phone: phone, name: name, via: via.join(" + "), at: Date.now() });
        save(arr); render();
        phoneIn.value = ""; nameIn.value = ""; refresh();
        show("<p style='margin:0'><strong>" + pretty(phone) + "</strong>: gönderiliyor…</p>");
        poll(ids, phone, 0);
      }).catch(function () {
        sendBtn.disabled = false; sendBtn.textContent = "Gönder";
        err.textContent = "Bağlantı yok. İnterneti kontrol edip tekrar deneyin.";
      });
    });
  }

  nameIn.addEventListener("input", refresh);
  sendBtn.addEventListener("click", function () { send(false); });
  pinBtn.addEventListener("click", function () { setPin(""); askPin(); });
  clearBtn.addEventListener("click", function () {
    if (confirm("Gönderim geçmişi bu telefondan silinsin mi?")) { save([]); render(); }
  });
  refresh();
  render();
})();
