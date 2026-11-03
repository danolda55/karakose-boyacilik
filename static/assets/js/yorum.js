/* Google yorum isteme aracı — Birol Usta iş bitince müşterinin numarasını girer, hazır mesaj WhatsApp veya SMS ile gider. Ücretsizdir; mesaj ustanın kendi telefonundan gönderilir. */
(function () {
  "use strict";
  var cfg = window.KB_CONFIG || {};
  var KEY = "kb-yorum-gecmis";

  var phoneIn = document.getElementById("musteri-tel");
  var nameIn = document.getElementById("musteri-ad");
  var preview = document.getElementById("mesaj");
  var err = document.getElementById("tel-hata");
  var sendBtn = document.getElementById("gonder");
  var smsBox = document.getElementById("sms-adim");
  var smsWho = document.getElementById("sms-kime");
  var smsOpen = document.getElementById("sms-ac");
  var smsSkip = document.getElementById("sms-atla");
  var PEND = "kb-yorum-sms-bekleyen";
  var list = document.getElementById("gecmis");
  var clearBtn = document.getElementById("gecmis-sil");

  /* 0532 123 45 67, 532..., +90 532... → 905321234567 */
  function normalize(raw) {
    var d = String(raw || "").replace(/\D/g, "");
    if (d.indexOf("0090") === 0) d = d.slice(2);
    if (d.length === 11 && d[0] === "0") d = "9" + d;
    if (d.length === 10 && d[0] === "5") d = "90" + d;
    return /^905\d{9}$/.test(d) ? d : null;
  }

  function pretty(d) {
    return "0" + d.slice(2, 5) + " " + d.slice(5, 8) + " " + d.slice(8, 10) + " " + d.slice(10);
  }

  function buildMessage() {
    var name = (nameIn.value || "").trim();
    var hello = name ? "Merhaba " + name + "," : "Merhaba,";
    return cfg.reviewMessage.replace("{selam}", hello).replace("{link}", cfg.reviewUrl);
  }

  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save(arr) { try { localStorage.setItem(KEY, JSON.stringify(arr.slice(0, 50))); } catch (e) {} }

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

  function waUrl(phone, text) { return "https://wa.me/" + phone + "?text=" + encodeURIComponent(text); }
  function smsUrl(phone, text) {
    return "sms:+" + phone + (/iPhone|iPad|iPod|Macintosh/i.test(navigator.userAgent) ? "&" : "?") + "body=" + encodeURIComponent(text);
  }
  function pending() { try { return JSON.parse(sessionStorage.getItem(PEND)); } catch (e) { return null; } }
  function setPending(p) { try { p ? sessionStorage.setItem(PEND, JSON.stringify(p)) : sessionStorage.removeItem(PEND); } catch (e) {} }

  function showSmsStep() {
    var p = pending();
    if (!p) { smsBox.hidden = true; return; }
    smsWho.textContent = pretty(p.phone);
    smsBox.hidden = false;
  }
  function openSms() {
    var p = pending();
    if (!p) return;
    setPending(null);
    smsBox.hidden = true;
    window.location.href = smsUrl(p.phone, p.text);
  }

  function send() {
    var phone = normalize(phoneIn.value);
    err.textContent = "";
    if (!phone) {
      err.textContent = "Numara hatalı görünüyor. Örnek: 0532 123 45 67";
      phoneIn.focus();
      return;
    }
    var already = load().filter(function (x) { return x.phone === phone; })[0];
    if (already && !confirm("Bu numaraya " + new Date(already.at).toLocaleDateString("tr-TR") + " tarihinde zaten mesaj gönderilmiş. Yine de gönderilsin mi?")) return;

    var text = preview.value || buildMessage();
    var arr = load();
    arr.unshift({ phone: phone, name: (nameIn.value || "").trim(), via: "WhatsApp + SMS", at: Date.now() });
    save(arr);
    render();
    phoneIn.value = ""; nameIn.value = ""; refresh();
    setPending({ phone: phone, text: text, at: Date.now() });
    showSmsStep();
    window.location.href = waUrl(phone, text);
  }

  /* WhatsApp'tan geri dönünce SMS'i kendiliğinden aç; telefon izin vermezse "SMS'i aç" düğmesi görünür kalır */
  function onReturn() {
    if (document.visibilityState !== "visible") return;
    var p = pending();
    if (!p) return;
    showSmsStep();
    if (Date.now() - p.at > 1500) setTimeout(openSms, 400);
  }
  document.addEventListener("visibilitychange", onReturn);
  window.addEventListener("pageshow", onReturn);
  window.addEventListener("focus", onReturn);
  smsOpen.addEventListener("click", openSms);
  smsSkip.addEventListener("click", function () { setPending(null); showSmsStep(); });

  nameIn.addEventListener("input", refresh);
  sendBtn.addEventListener("click", send);
  clearBtn.addEventListener("click", function () {
    if (confirm("Gönderim geçmişi bu telefondan silinsin mi?")) { save([]); render(); }
  });
  refresh();
  render();
  showSmsStep();
})();
